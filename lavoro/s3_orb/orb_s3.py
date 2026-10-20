# -*- coding: utf-8 -*-
"""S3 (PROTOCOLLO_S3.md, versione definitiva): l'ORB di Manu (build 10-09-R, filtro di allineamento spento) con regole
congelate su barre M1, alle aperture di Francoforte, Londra e Tokyo (+ USA-ALTRI come secondario).
Uso:  python3 -I orb_s3.py equivalenza   -> confronto con la lista del tester (US100 FTMO, date < 2024)
      python3 -I orb_s3.py test          -> test S3 sui dati di scoperta (< 2024)"""
import os, sys, json
import numpy as np
import pandas as pd
import holidays
from zoneinfo import ZoneInfo
from scipy import stats

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "s1_s2"))
import s12_comune as C

OUT = os.path.join(QUI, "risultati")
CACHE = "/tmp/claude-0/-home-user-Strategy-20-10-UK100/3f32bb43-76e4-56e7-9055-9f1cda27903e/scratchpad/cache_s3"
FINE = pd.Timestamp("2023-12-31")
NY = ZoneInfo("America/New_York")
STOP_ATR, TP_R, BODY_MIN, RANGE_MIN, ATR_N = 0.10, 8.0, 0.05, 0.12, 14
SLIP_MIN_BPS, SLIP_FRAZ_SPREAD, SLIP_ORDINE_STRESS_BPS = 0.32, 0.55, 0.3
FATTORE_SPREAD = 0.638 / 0.561          # spread reale M1BA / campo SPREAD su US100 (strumenti senza M1BA)
PEP_NY8 = (pd.Timestamp("2017-10-30"), pd.Timestamp("2018-03-16"))   # feed Pepperstone in NY+8: sedute escluse

FEED = {("US100", "FTMO"): ("/home/user/dati_scoperta_tutti", "US100 m1 - FTMO", "2021-09-14"),
        ("US500", "PEP"): ("/home/user/dati_scoperta_tutti", "US500 m1 - Pepperstone", "2020-07-13"),
        ("US500", "FTMO"): ("/home/user/dati_scoperta_tutti", "US500 m1 - FTMO", "2021-09-14"),
        ("US30", "PEP"): ("/home/user/dati_s12/scoperta", "US30 Pepperstone m1", "2018-01-02"),
        ("GER40", "PEP"): ("/home/user/dati_scoperta_tutti", "GER40 Pepperstone m1", "2020-06-11"),
        ("GER40", "FTMO"): ("/home/user/dati_scoperta_tutti", "GER40 FTMO m1", "2021-12-28"),
        ("UK100", "PEP"): ("/home/user/dati_scoperta_tutti", "UK100 Pepperstone m1", "2017-06-06"),
        ("UK100", "FTMO"): ("/home/user/dati_scoperta_tutti", "UK100 FTMO m1", "2021-09-14"),
        ("JP225", "FTMO"): ("/home/user/dati_s3/scoperta", "JP225 m1 FTMO", "2021-09-13")}
BORSA = {"US100": ("NYSE", "America/New_York", "09:30", "16:00"), "US500": ("NYSE", "America/New_York", "09:30", "16:00"),
         "US30": ("NYSE", "America/New_York", "09:30", "16:00"),
         "GER40": ("XETRA", "Europe/Berlin", "09:00", "17:30"), "UK100": ("LSE", "Europe/London", "08:00", "16:30"),
         "JP225": ("TOKYO", "Asia/Tokyo", "09:00", "15:00")}
PRIMARI = {"EUROPA": [("GER40", "PEP", "FTMO"), ("UK100", "PEP", "FTMO")], "ASIA": [("JP225", "FTMO", None)]}
SECONDARI = {"USA-ALTRI": [("US500", "PEP", "FTMO"), ("US30", "PEP", None)]}
VALUTE = {"GER40": {"EUR", "USD"}, "UK100": {"GBP", "USD"}, "JP225": {"JPY", "USD"}, "US500": {"USD"}, "US30": {"USD"}, "US100": {"USD"}}
MEZZE_NYSE = C.NYSE_ANTICIPATE | {pd.Timestamp(x) for x in ["2025-07-03", "2025-11-28", "2025-12-24", "2026-11-27", "2026-12-24"]}
_c = pd.read_csv(os.path.join(OUT, "COSTI_S3.csv"), sep=";", decimal=",")
COSTI = {(r.strumento, r.contesto): r.base_bps * (1.0 if r.strumento == "US100" else FATTORE_SPREAD) for r in _c.itertuples()}


def carica(s, f):
    os.makedirs(CACHE, exist_ok=True)
    d, nome, inizio = FEED[(s, f)]
    pk = os.path.join(CACHE, f"{s}_{f}_{inizio}.pkl")
    if os.path.exists(pk): return pd.read_pickle(pk)
    raw = pd.read_csv(os.path.join(d, nome + ".csv"), sep="\t", dtype=str, usecols=[0, 1, 2, 3, 4, 5, 8])
    raw.columns = ["d", "t", "o", "h", "l", "c", "sp"]
    dig = int(raw.c.head(20000).str.split(".").str[1].str.len().fillna(0).max())
    raw = raw[raw.d >= (pd.Timestamp(inizio) - pd.Timedelta(days=40)).strftime("%Y.%m.%d")]   # riscaldamento ATR
    df = pd.DataFrame({"ts": pd.to_datetime(raw.d + " " + raw.t, format="%Y.%m.%d %H:%M:%S").values,
                       **{k: raw[k].astype(float).values for k in "ohlc"},
                       "sp": raw.sp.astype(float).values * 10.0 ** (-dig)})   # spread storico (minimo del minuto)
    df = df.drop_duplicates("ts", keep="last").sort_values("ts").reset_index(drop=True)
    assert df.ts.max() < pd.Timestamp("2024-01-01")
    g = df.ts.dt.normalize()
    passo = df.ts.diff().dt.total_seconds().div(60)
    moda = passo.groupby(g).agg(lambda x: x.mode().iloc[0] if x.notna().any() else np.nan)
    df["m1_ok"] = (g.map(moda) == 1).values
    df.to_pickle(pk)
    return df

def atr_d1(df):
    """ATR(14) come iATR di MT5 (media semplice di 14 true range) sulle barre D1 del giorno server."""
    g = df.groupby(df.ts.dt.normalize())
    d = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()})
    pc = d.c.shift()
    tr = np.maximum(d.h, pc) - np.minimum(d.l, pc)
    tr.iloc[0] = d.h.iloc[0] - d.l.iloc[0]
    return tr.rolling(ATR_N, min_periods=ATR_N).mean()

def giorni_sessione(borsa, da, a):
    anni = range(pd.Timestamp(da).year - 1, pd.Timestamp(a).year + 2)
    g = pd.date_range(da, a, freq="B")
    mezze = set()
    if borsa == "NYSE":
        chiusi = {pd.Timestamp(x) for x in holidays.NYSE(years=anni).keys()}
        mezze = MEZZE_NYSE
        g = pd.DatetimeIndex([x for x in g if x not in chiusi])
    elif borsa == "TOKYO":
        chiusi = {pd.Timestamp(x) for x in holidays.Japan(years=anni).keys()}
        for y in anni:
            for mm, gg in ((12, 31), (1, 1), (1, 2), (1, 3)): chiusi.add(pd.Timestamp(y, mm, gg))
        g = pd.DatetimeIndex([x for x in g if x not in chiusi])
    else:   # XETRA, LSE: come S2 (mezze sedute escluse; Xetra aperta il lunedi' di Pentecoste)
        g = C.giorni_borsa(borsa, da, a)
    return g, mezze

def orb_strumento(s, f, spread="oggi", mult=1.0, fine=FINE):
    """Un trade ORB per giorno di sessione (o nessuno), su barre M1 bid con il lato ask = bid + spread: long all'ask e
    uscite al bid; short al bid e uscite all'ask (stop e target sull'ask). spread = "storico" (campo SPREAD del minuto,
    per l'equivalenza col tester) o "oggi" (tabella congelata x fattore, in bps del prezzo, x mult per lo stress)."""
    df = carica(s, f); borsa, tz, apre, chiude = BORSA[s]
    inizio = pd.Timestamp(FEED[(s, f)][2])
    giorni, mezze = giorni_sessione(borsa, inizio, fine)
    atr = atr_d1(df)
    t = df.ts.values; o, h, l, c, ok, spv = df.o.values, df.h.values, df.l.values, df.c.values, df.m1_ok.values, df.sp.values
    srv = lambda x: C.a_server(pd.DatetimeIndex([x]), tz, "NY7")[0]
    righe = []
    for d in giorni:
        rec = dict(giorno=d, strumento=s, feed=f, esito="")
        if f == "PEP" and PEP_NY8[0] <= d <= PEP_NY8[1]:
            rec["esito"] = "skip: fuso NY+8 (Pepperstone)"; righe.append(rec); continue
        ah, am = map(int, apre.split(":")); ch, cm = map(int, chiude.split(":"))
        if borsa == "NYSE" and d in mezze: ch, cm = 13, 0
        if s == "JP225" and d >= pd.Timestamp("2024-11-05"): ch, cm = 15, 30
        T0 = srv(d + pd.Timedelta(hours=ah, minutes=am))
        Tfine = srv(d + pd.Timedelta(hours=ch, minutes=cm) - pd.Timedelta(minutes=5))
        if pd.isna(T0) or pd.isna(Tfine): continue
        i0 = np.searchsorted(t, np.datetime64(T0), "left"); i5 = np.searchsorted(t, np.datetime64(T0 + pd.Timedelta(minutes=5)), "left")
        if i5 <= i0 or not ok[i0:i5].all():
            rec["esito"] = "skip: candela 1 assente"; righe.append(rec); continue
        o1, c1, h1, l1 = o[i0], c[i5 - 1], h[i0:i5].max(), l[i0:i5].min()
        rng = h1 - l1
        gsrv = pd.Timestamp(T0).normalize()
        a_prev = atr[atr.index < gsrv]
        a = a_prev.iloc[-1] if len(a_prev) and np.isfinite(a_prev.iloc[-1]) else np.nan
        rec.update(o1=o1, c1=c1, h1=h1, l1=l1, atr=a)
        if rng <= 0: rec["esito"] = "skip: range nullo"; righe.append(rec); continue
        if abs(c1 - o1) < BODY_MIN * rng: rec["esito"] = "skip: doji"; righe.append(rec); continue
        if not np.isfinite(a) or a <= 0: rec["esito"] = "skip: ATR n/d"; righe.append(rec); continue
        if rng < RANGE_MIN * a: rec["esito"] = "skip: ampiezza"; righe.append(rec); continue
        verso = 1 if c1 > o1 else -1
        Te = T0 + pd.Timedelta(minutes=5)
        ie = np.searchsorted(t, np.datetime64(Te), "left")         # finestra d'ingresso dell'EA: [apertura+5', apertura+10')
        if ie >= len(t) or (t[ie] - np.datetime64(Te)) >= np.timedelta64(5, "m") or not ok[ie]:
            rec["esito"] = "skip: barra d'ingresso assente"; righe.append(rec); continue
        bid_in = o[ie]; dist = STOP_ATR * a
        if spread == "storico":
            spk = lambda k: spv[k]
            sp_fine = None
        else:
            sp_in_bps = COSTI[(s, "ingresso")] * mult; sp_fine_bps = COSTI[(s, "uscita_fine_sessione")] * mult
            spk = lambda k, _p=bid_in, _b=sp_in_bps: _b * 1e-4 * _p
            sp_fine = sp_fine_bps
        fill = bid_in + spk(ie) if verso > 0 else bid_in
        sl, tp = fill - verso * dist, fill + verso * TP_R * dist
        uscita, px, tu = "fine sessione", np.nan, None
        for k in range(ie, len(t)):
            if t[k] >= np.datetime64(Tfine):
                if (t[k] - np.datetime64(Tfine)) <= np.timedelta64(5, "m"): kk, pb = k, o[k]
                elif k > ie and (np.datetime64(Tfine) - t[k - 1]) <= np.timedelta64(5, "m"): kk, pb = k - 1, c[k - 1]
                else: kk = None
                if kk is not None:
                    esp = (sp_fine * 1e-4 * pb) if sp_fine is not None else spk(kk)
                    px, tu = (pb if verso > 0 else pb + esp), t[kk]
                break
            if verso > 0:
                if o[k] <= sl: px, uscita, tu = o[k], "stop", t[k]; break
                if o[k] >= tp: px, uscita, tu = o[k], "target", t[k]; break
                if l[k] <= sl: px, uscita, tu = sl, "stop", t[k]; break
                if h[k] >= tp: px, uscita, tu = tp, "target", t[k]; break
            else:
                sk = spk(k); ao, ah_, al_ = o[k] + sk, h[k] + sk, l[k] + sk
                if ao >= sl: px, uscita, tu = ao, "stop", t[k]; break
                if ao <= tp: px, uscita, tu = ao, "target", t[k]; break
                if ah_ >= sl: px, uscita, tu = sl, "stop", t[k]; break
                if al_ <= tp: px, uscita, tu = tp, "target", t[k]; break
        if not np.isfinite(px): rec["esito"] = "skip: dati mancanti a fine sessione"; righe.append(rec); continue
        R = verso * (px - fill) / dist
        rec.update(esito="trade", verso=verso, ingresso_srv=pd.Timestamp(t[ie]), prezzo_in=fill, dist=dist, sl=sl, tp=tp,
                   uscita=uscita, uscita_srv=pd.Timestamp(tu), prezzo_out=px, R_dopo_spread=R,
                   spread_R=(spk(ie) / dist), dist_bps=dist / fill * 1e4)
        righe.append(rec)
    return pd.DataFrame(righe)

def simula(s, f):
    """trade con costi base e stress (stress = simulazione rifatta con spread x 1,5)."""
    b = orb_strumento(s, f, "oggi", 1.0); st = orb_strumento(s, f, "oggi", 1.5)
    tr = b[b.esito == "trade"].copy()
    trs = st[st.esito == "trade"].set_index("giorno")
    sp_bps = COSTI[(s, "ingresso")]
    s_liv = max(SLIP_MIN_BPS, SLIP_FRAZ_SPREAD * sp_bps)
    livello = tr.uscita.isin(["stop", "target"])
    tr["slip_R"] = np.where(livello, s_liv * 1e-4 * tr.prezzo_in / tr.dist, 0.0)
    tr["R_netto"] = tr.R_dopo_spread - tr.slip_R
    Rs = trs.reindex(tr.giorno).R_dopo_spread.to_numpy()
    liv_s = trs.reindex(tr.giorno).uscita.isin(["stop", "target"]).to_numpy()
    extra = (np.where(liv_s, 2.5 * s_liv, SLIP_ORDINE_STRESS_BPS) + SLIP_ORDINE_STRESS_BPS) * 1e-4 * tr.prezzo_in.to_numpy() / tr.dist.to_numpy()
    tr["R_stress"] = Rs - extra
    return b, tr


def equivalenza():
    E = orb_strumento("US100", "FTMO", spread="storico")
    E.to_csv(os.path.join(OUT, "EQUIV_US100_python.csv"), sep=";", decimal=",", index=False)
    T = pd.read_csv(os.path.join(QUI, "..", "portafoglio_esistente", "ORB_P1_trade.csv"), sep=";", decimal=",")
    T["ingresso_srv"] = pd.to_datetime(T.ingresso_srv, format="%Y.%m.%d %H:%M:%S")
    T = T[T.ingresso_srv < pd.Timestamp("2024-01-01")].copy()
    T["giorno_srv"] = T.ingresso_srv.dt.normalize(); T["verso_t"] = np.where(T.verso == "long", 1, -1)
    E["giorno_srv"] = pd.to_datetime(E.giorno)
    giorni = E[E.giorno >= T.giorno_srv.min()].copy()
    m = giorni.merge(T[["giorno_srv", "verso_t", "R", "prezzo_in", "uscita"]], on="giorno_srv", how="outer", indicator=True)
    trade_py = m.esito == "trade"; trade_t = m._merge.isin(["both", "right_only"])
    stessa = (trade_py == trade_t) & (~(trade_py & trade_t) | (m.verso == m.verso_t))
    both = m[trade_py & trade_t]
    out = dict(giorni=int(len(m)), trade_python=int(trade_py.sum()), trade_tester=int(trade_t.sum()),
               quota_stessa_decisione=float(stessa.mean()), trade_in_comune=int(len(both)),
               stesso_verso_in_comune=float((both.verso == both.verso_t).mean()),
               corr_R=float(np.corrcoef(both.R_dopo_spread, both.R)[0, 1]),
               R_medio_python=float(both.R_dopo_spread.mean()), R_medio_tester=float(both.R.mean()),
               diff_prezzo_in_mediana=float((both.prezzo_in_x - both.prezzo_in_y).abs().median()),
               uscite_python=both.uscita_x.value_counts().to_dict())
    soglie = dict(decisione=out["quota_stessa_decisione"] >= 0.95, corr=out["corr_R"] >= 0.90,
                  diff_R=abs(out["R_medio_python"] - out["R_medio_tester"]) <= 0.05)
    out["soglie"] = soglie; out["SUPERATO"] = all(soglie.values())
    m[~stessa][["giorno_srv", "esito", "verso", "verso_t", "R_dopo_spread", "R"]].to_csv(
        os.path.join(OUT, "EQUIV_US100_discordanze.csv"), sep=";", decimal=",", index=False)
    json.dump(out, open(os.path.join(OUT, "EQUIV_US100.json"), "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


def stat_paniere(a):
    x = a.R_netto.to_numpy(); g = pd.DatetimeIndex(a.giorno).to_numpy(); n = len(x)
    if n < 30: return dict(n=n, p=1.0)
    m, t, G = C.cr1(x, g); p = float(stats.t.sf(t, G - 1))
    d = pd.DatetimeIndex(a.giorno); med = d.sort_values()[n // 2]
    anni = pd.Series(x).groupby(d.year).agg(["mean", "size"]); anni = anni[anni["size"] >= 10]
    contr = pd.Series(x).groupby(d.normalize()).sum() / n
    via = set(contr.abs().sort_values(ascending=False).index[:int(np.ceil(0.01 * len(contr)))])
    return dict(n=n, giorni_anno=n / max(1e-9, (d.max() - d.min()).days / 365.25), netto_R=m, t=t, p=p,
                p_boot=C.bootstrap_giorni(x, g), stress_R=float(a.R_stress.mean()), dopo_spread_R=float(a.R_dopo_spread.mean()),
                meta1=float(x[d < med].mean()), meta2=float(x[d >= med].mean()), taglio=str(med.date()),
                anni_validi=int(len(anni)), quota_anni_pos=float((anni["mean"] > 0).mean()) if len(anni) else np.nan,
                senza_influenti=float(x[~d.normalize().isin(via)].mean()), primo=str(d.min().date()), ultimo=str(d.max().date()))

def carica_esistenti():
    """liste del tester ORB P1 e IM G (date < 2024): trade con orari server e verso, R per giorno."""
    out = {}
    for nome, f in (("ORB", "ORB_P1_trade.csv"), ("IM", "IM_G_trade.csv")):
        T = pd.read_csv(os.path.join(QUI, "..", "portafoglio_esistente", f), sep=";", decimal=",")
        T["in"] = pd.to_datetime(T.ingresso_srv, format="%Y.%m.%d %H:%M:%S"); T["out"] = pd.to_datetime(T.uscita_srv, format="%Y.%m.%d %H:%M:%S")
        T = T[T["in"] < pd.Timestamp("2024-01-01")].copy(); T["v"] = np.where(T.verso == "long", 1, -1)
        T["giorno"] = T["in"].dt.normalize()
        out[nome] = T
    return out

def g6(tr_paniere, giornaliero, esistenti):
    res = {}
    for nome, T in esistenti.items():
        e = T.groupby("giorno").R.sum()
        u = pd.concat([giornaliero.rename("p"), e.rename("e")], axis=1).fillna(0.0)
        u = u[(u.index >= max(giornaliero.index.min(), e.index.min())) & (u.index <= min(giornaliero.index.max(), e.index.max()))]
        res[f"corr_{nome}"] = float(u.corr().iloc[0, 1]) if len(u) > 30 else np.nan
        # quota di trade del paniere aperti insieme a un trade esistente nello stesso verso
        ins = 0
        for r in tr_paniere.itertuples():
            sov = T[(T["in"] < r.uscita_srv) & (T["out"] > r.ingresso_srv) & (T.v == r.verso)]
            ins += int(len(sov) > 0)
        res[f"quota_insieme_stesso_verso_{nome}"] = ins / max(1, len(tr_paniere))
    res["G6_verde"] = all((np.isnan(res[f"corr_{n}"]) or res[f"corr_{n}"] <= 0.3) and res[f"quota_insieme_stesso_verso_{n}"] <= 0.5
                          for n in esistenti)
    return res

def notizie_livello(tr):
    """quota delle uscite a livello entro +-2 minuti da eventi ad alto impatto (valuta dell'indice + USD)."""
    sys.path.insert(0, os.path.join(QUI, "..", "s1_s2")); import s12_test as S
    cal = S.calendario(); cal = cal[cal.importanza == 3]
    out = {}
    for s, y in tr.groupby("strumento"):
        V = pd.DatetimeIndex(sorted(cal[cal.valuta.isin(VALUTE[s])].T_ny.unique())).values
        liv = y[y.uscita.isin(["stop", "target"])]
        tny = (pd.DatetimeIndex(liv.uscita_srv) - pd.Timedelta(hours=7)).values     # NY+7 -> New York
        k = np.searchsorted(V, tny)
        dmin = np.minimum(np.abs(tny - V[np.clip(k, 0, len(V) - 1)]), np.abs(tny - V[np.clip(k - 1, 0, len(V) - 1)]))
        out[s] = dict(uscite_livello=int(len(liv)), entro_2_minuti=int((dmin <= np.timedelta64(2, "m")).sum()),
                      quota=float((dmin <= np.timedelta64(2, "m")).mean()) if len(liv) else np.nan)
    return out

def test():
    esistenti = carica_esistenti()
    tutti, righe, sec, desc = [], [], [], {}
    for famiglia, panieri in (("primario", PRIMARI), ("secondario", SECONDARI)):
        for paniere, membri in panieri.items():
            trs, trc = [], []
            for s, fi, fc in membri:
                b, tr = simula(s, fi); tr["paniere"] = paniere; trs.append(tr); b["paniere"] = paniere; tutti.append(b)
                if fc:
                    _, tc = simula(s, fc); tc["paniere"] = paniere; trc.append(tc)
                print(paniere, s, "fatto", flush=True)
            x = pd.concat(trs, ignore_index=True)
            assert pd.DatetimeIndex(x.giorno).max() < pd.Timestamp("2024-01-01")
            a = x.groupby("giorno").agg(R_netto=("R_netto", "mean"), R_stress=("R_stress", "mean"), R_dopo_spread=("R_dopo_spread", "mean")).reset_index()
            st = stat_paniere(a); st.update(paniere=paniere, famiglia=famiglia)
            per = x.groupby("strumento").R_netto.mean()
            st["strumenti_pos"], st["strumenti"] = int((per > 0).sum()), int(len(per))
            if trc:
                xc = pd.concat(trc, ignore_index=True)
                ac = xc.groupby("giorno").R_dopo_spread.mean()
                ap = x[x.strumento.isin(xc.strumento.unique())].groupby("giorno").R_dopo_spread.mean()
                com = ap.index.intersection(ac.index)
                st.update(conc_n=int(len(com)), conc_ftmo=float(ac.loc[com].mean()) if len(com) else np.nan,
                          conc_inferenza=float(ap.loc[com].mean()) if len(com) else np.nan)
            else:
                st.update(conc_n=0, conc_ftmo=np.nan, conc_inferenza=np.nan)
            st.update(g6(x, a.set_index("giorno").R_netto, esistenti))
            desc[f"notizie|{paniere}"] = notizie_livello(x)
            righe.append(st)
            for sname, y in x.groupby("strumento"):
                m, t, G = C.cr1(y.R_netto.to_numpy(), pd.DatetimeIndex(y.giorno).to_numpy())
                sec.append(dict(paniere=paniere, strumento=sname, n=len(y), netto_R=m, t=t, dopo_spread_R=y.R_dopo_spread.mean(),
                                stress_R=y.R_stress.mean(), spread_R=y.spread_R.mean(), slip_R=y.slip_R.mean(),
                                costo_R=(y.spread_R + y.slip_R).mean(), operabile_G1=bool((y.spread_R + y.slip_R).mean() <= 0.125),
                                quota_stop=(y.uscita == "stop").mean(), quota_target=(y.uscita == "target").mean(),
                                quota_fine=(y.uscita == "fine sessione").mean(), dist_bps_mediana=y.dist_bps.median(),
                                per_anno=json.dumps(y.groupby(pd.DatetimeIndex(y.giorno).year).R_netto.mean().round(3).to_dict())))
    R = pd.DataFrame(righe)
    R["bh"] = False
    prim = R.famiglia == "primario"
    R.loc[prim, "bh"], soglia = C.bh(R.loc[prim, "p"].fillna(1.0).to_numpy(), 0.10)
    conc_ok = (R.conc_n < 100) | (np.sign(R.conc_ftmo) == np.sign(R.conc_inferenza))
    R["promosso"] = (prim & R.bh & (R.stress_R > 0) & (R.meta1 > 0) & (R.meta2 > 0) & (R.anni_validi >= 3) & (R.quota_anni_pos >= 0.6)
                     & (R.strumenti_pos >= np.ceil(R.strumenti / 2)) & (R.senza_influenti > 0) & conc_ok)
    R["classe"] = np.where(R.promosso, "PROMOSSO", np.where((R.p < 0.05) & (R.netto_R > 0), "INDIZIO", "NULLO"))
    R["valido_S3"] = R.promosso & R.G6_verde
    R.to_csv(os.path.join(OUT, "S3_PRIMARI.csv"), sep=";", decimal=",", index=False)
    pd.DataFrame(sec).to_csv(os.path.join(OUT, "S3_SECONDARI.csv"), sep=";", decimal=",", index=False)
    pd.concat(tutti, ignore_index=True).to_csv(os.path.join(OUT, "S3_trade.csv"), sep=";", decimal=",", index=False)
    json.dump(desc, open(os.path.join(OUT, "S3_DESCRITTIVI.json"), "w"), indent=1, default=float)
    pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
    print(R.round(4).to_string(index=False)); print(pd.DataFrame(sec).round(4).to_string(index=False)); print(json.dumps(desc, indent=1, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "equivalenza": equivalenza()
    elif sys.argv[1] == "test": test()
