# -*- coding: utf-8 -*-
"""S3 (PROTOCOLLO_S3.md): l'ORB di Manu (build 10-09-R, filtro di allineamento spento) con regole congelate su barre M1.
Uso:  python3 -I orb_s3.py equivalenza   -> confronto con la lista del tester (US100 FTMO, date < 2024)
      python3 -I orb_s3.py test          -> test primari S3 sui dati di scoperta (< 2024)"""
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
SLIP_LIVELLO_BPS, SLIP_ORDINE_STRESS_BPS = 0.32, 0.3

FEED = {("US100", "FTMO"): ("/home/user/dati_scoperta_tutti", "US100 m1 - FTMO", "2021-09-14"),
        ("US500", "PEP"): ("/home/user/dati_scoperta_tutti", "US500 m1 - Pepperstone", "2020-07-13"),
        ("US500", "FTMO"): ("/home/user/dati_scoperta_tutti", "US500 m1 - FTMO", "2021-09-14"),
        ("US30", "PEP"): ("/home/user/dati_s12/scoperta", "US30 Pepperstone m1", "2018-01-02"),
        ("US2000", "PEP"): ("/home/user/dati_s12/scoperta", "US2000 m1 Pepperstone", "2017-06-05"),
        ("US2000", "FTMO"): ("/home/user/dati_s12/scoperta", "US2000 m1 FTMO", "2018-04-09"),
        ("GER40", "PEP"): ("/home/user/dati_scoperta_tutti", "GER40 Pepperstone m1", "2020-06-11"),
        ("GER40", "FTMO"): ("/home/user/dati_scoperta_tutti", "GER40 FTMO m1", "2021-12-28"),
        ("UK100", "PEP"): ("/home/user/dati_scoperta_tutti", "UK100 Pepperstone m1", "2017-06-06"),
        ("UK100", "FTMO"): ("/home/user/dati_scoperta_tutti", "UK100 FTMO m1", "2021-09-14"),
        ("FRA40", "FTMO"): ("/home/user/dati_s12/scoperta", "FRA40 m1 FTMO", "2021-09-14"),
        ("JP225", "FTMO"): ("/home/user/dati_s3/scoperta", "JP225 m1 FTMO", "2021-09-13")}
BORSA = {"US100": ("NYSE", "America/New_York", "09:30", "16:00"), "US500": ("NYSE", "America/New_York", "09:30", "16:00"),
         "US30": ("NYSE", "America/New_York", "09:30", "16:00"), "US2000": ("NYSE", "America/New_York", "09:30", "16:00"),
         "GER40": ("XETRA", "Europe/Berlin", "09:00", "17:30"), "UK100": ("LSE", "Europe/London", "08:00", "16:30"),
         "FRA40": ("EURONEXT", "Europe/Paris", "09:00", "17:30"), "JP225": ("TOKYO", "Asia/Tokyo", "09:00", "15:00")}
PANIERI = {"EUROPA": [("GER40", "PEP", "FTMO"), ("UK100", "PEP", "FTMO"), ("FRA40", "FTMO", None)],
           "ASIA": [("JP225", "FTMO", None)],
           "USA-ALTRI": [("US500", "PEP", "FTMO"), ("US30", "PEP", None), ("US2000", "PEP", "FTMO")]}
_c = pd.read_csv(os.path.join(OUT, "COSTI_S3.csv"), sep=";", decimal=",")
COSTI = {(r.strumento, r.contesto): (r.base_bps, r.stress_bps) for r in _c.itertuples()}


def carica(s, f):
    os.makedirs(CACHE, exist_ok=True)
    pk = os.path.join(CACHE, f"{s}_{f}.pkl")
    if os.path.exists(pk): return pd.read_pickle(pk)
    d, nome, inizio = FEED[(s, f)]
    raw = pd.read_csv(os.path.join(d, nome + ".csv"), sep="\t", dtype=str, usecols=[0, 1, 2, 3, 4, 5, 8])
    raw.columns = ["d", "t", "o", "h", "l", "c", "sp"]
    dig = int(raw.c.head(20000).str.split(".").str[1].str.len().fillna(0).max())
    # 40 giorni prima dell'inizio per l'ATR(14) delle barre D1
    raw = raw[raw.d >= (pd.Timestamp(inizio) - pd.Timedelta(days=40)).strftime("%Y.%m.%d")]
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
    """ATR(14) come iATR di MT5 (media semplice di 14 true range) sulle barre D1 del giorno server, indicizzato per giorno server."""
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
        mezze = C.NYSE_ANTICIPATE
        g = pd.DatetimeIndex([x for x in g if x not in chiusi])
    elif borsa == "TOKYO":
        chiusi = {pd.Timestamp(x) for x in holidays.Japan(years=anni).keys()}
        for y in anni:
            for mm, gg in ((12, 31), (1, 1), (1, 2), (1, 3)): chiusi.add(pd.Timestamp(y, mm, gg))
        g = pd.DatetimeIndex([x for x in g if x not in chiusi])
    else:   # XETRA, EURONEXT, LSE: come S2 (mezze sedute escluse)
        g = C.giorni_borsa(borsa, da, a)
    return g, mezze

def orb_strumento(s, f, spread="oggi"):
    """un trade ORB per giorno di sessione (o nessuno), su barre M1 bid con il lato ask ricostruito (ask = bid + spread):
    i long entrano all'ask ed escono al bid; gli short entrano al bid ed escono all'ask, e i loro stop e target scattano
    sull'ask (come in MT5). spread = "storico" (campo SPREAD del minuto, per l'equivalenza col tester) oppure "oggi"
    (spread FTMO 2025-26 della tabella congelata, in bps del prezzo)."""
    df = carica(s, f); borsa, tz, apre, chiude = BORSA[s]
    inizio = pd.Timestamp(FEED[(s, f)][2])
    giorni, mezze = giorni_sessione(borsa, inizio, FINE)
    atr = atr_d1(df)
    t = df.ts.values; o, h, l, c, ok, spv = df.o.values, df.h.values, df.l.values, df.c.values, df.m1_ok.values, df.sp.values
    srv = lambda x: C.a_server(pd.DatetimeIndex([x]), tz, "NY7")[0]
    righe = []
    for d in giorni:
        ah, am = map(int, apre.split(":")); ch, cm = map(int, chiude.split(":"))
        if d in mezze: ch, cm = 13, 0
        T0 = srv(d + pd.Timedelta(hours=ah, minutes=am))
        Tfine = srv(d + pd.Timedelta(hours=ch, minutes=cm) - pd.Timedelta(minutes=5))
        if pd.isna(T0) or pd.isna(Tfine): continue
        i0 = np.searchsorted(t, np.datetime64(T0), "left"); i5 = np.searchsorted(t, np.datetime64(T0 + pd.Timedelta(minutes=5)), "left")
        rec = dict(giorno=d, strumento=s, feed=f, esito="")
        if i5 <= i0 or not ok[i0:i5].all():
            rec["esito"] = "skip: candela 1 assente"; righe.append(rec); continue
        o1, c1, h1, l1 = o[i0], c[i5 - 1], h[i0:i5].max(), l[i0:i5].min()
        rng = h1 - l1
        # ATR dell'ultima barra D1 completa (giorno server precedente a quello dell'ingresso)
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
        ie = np.searchsorted(t, np.datetime64(Te), "left")
        if ie >= len(t) or (t[ie] - np.datetime64(Te)) > np.timedelta64(2, "m") or not ok[ie]:
            rec["esito"] = "skip: barra d'ingresso assente"; righe.append(rec); continue
        bid_in = o[ie]; dist = STOP_ATR * a
        if spread == "storico":
            spk = lambda k: spv[k]
        else:
            sp_in_bps, sp_fine_bps = COSTI[(s, "ingresso")][0], COSTI[(s, "uscita_fine_sessione")][0]
            spk = lambda k, _p=bid_in, _b=sp_in_bps: _b * 1e-4 * _p
        fill = bid_in + spk(ie) if verso > 0 else bid_in        # long all'ask, short al bid
        sl, tp = fill - verso * dist, fill + verso * TP_R * dist  # stop e target riancorati al fill (come l'EA)
        uscita, px, tu = "fine sessione", np.nan, None
        for k in range(ie, len(t)):
            if t[k] >= np.datetime64(Tfine):
                kk = k if (t[k] - np.datetime64(Tfine)) <= np.timedelta64(5, "m") else k - 1
                pb = o[k] if kk == k else c[k - 1]
                if spread == "oggi": esp = sp_fine_bps * 1e-4 * pb
                else: esp = spk(kk)
                px, tu = (pb if verso > 0 else pb + esp), t[kk]
                break
            if verso > 0:                                    # uscite sul bid
                if o[k] <= sl: px, uscita, tu = o[k], "stop", t[k]; break
                if o[k] >= tp: px, uscita, tu = o[k], "target", t[k]; break
                if l[k] <= sl: px, uscita, tu = sl, "stop", t[k]; break
                if h[k] >= tp: px, uscita, tu = tp, "target", t[k]; break
            else:                                            # uscite sull'ask = bid + spread
                sk = spk(k); ao, ah, al = o[k] + sk, h[k] + sk, l[k] + sk
                if ao >= sl: px, uscita, tu = ao, "stop", t[k]; break
                if ao <= tp: px, uscita, tu = ao, "target", t[k]; break
                if ah >= sl: px, uscita, tu = sl, "stop", t[k]; break
                if al <= tp: px, uscita, tu = tp, "target", t[k]; break
        if not np.isfinite(px): rec["esito"] = "skip: uscita assente"; righe.append(rec); continue
        R = verso * (px - fill) / dist                       # spread gia' dentro (lato ask)
        livello = uscita in ("stop", "target")
        slip_b = (SLIP_LIVELLO_BPS if livello else 0.0) * 1e-4 * fill / dist
        sp_extra = 0.5 * COSTI[(s, "ingresso")][0] * 1e-4 * fill / dist          # stress: spread x 1,5
        slip_s = ((2.5 * SLIP_LIVELLO_BPS if livello else SLIP_ORDINE_STRESS_BPS) + SLIP_ORDINE_STRESS_BPS) * 1e-4 * fill / dist
        rec.update(esito="trade", verso=verso, ingresso_srv=pd.Timestamp(t[ie]), prezzo_in=fill, dist=dist, sl=sl, tp=tp,
                   uscita=uscita, uscita_srv=pd.Timestamp(tu), prezzo_out=px, R_lordo=R + verso * 0.0,
                   R_netto=R - slip_b, R_stress=R - sp_extra - slip_s, spread_R=(spk(ie) / dist))
        righe.append(rec)
    return pd.DataFrame(righe)


def equivalenza():
    E = orb_strumento("US100", "FTMO", spread="storico")
    E.to_csv(os.path.join(OUT, "EQUIV_US100_python.csv"), sep=";", decimal=",", index=False)
    T = pd.read_csv(os.path.join(QUI, "..", "portafoglio_esistente", "ORB_P1_trade.csv"), sep=";", decimal=",")
    T["ingresso_srv"] = pd.to_datetime(T.ingresso_srv, format="%Y.%m.%d %H:%M:%S")
    T = T[T.ingresso_srv < pd.Timestamp("2024-01-01")].copy()
    T["giorno_srv"] = T.ingresso_srv.dt.normalize(); T["verso_t"] = np.where(T.verso == "long", 1, -1)
    E["giorno_srv"] = pd.to_datetime(E.giorno)  # US: giorno di New York = giorno server all'apertura (16:30 server)
    giorni = E[E.giorno >= T.giorno_srv.min()].copy()
    m = giorni.merge(T[["giorno_srv", "verso_t", "R", "prezzo_in", "uscita"]], on="giorno_srv", how="outer", indicator=True)
    trade_py = m.esito == "trade"; trade_t = m._merge.isin(["both", "right_only"])
    stessa_decisione = (trade_py == trade_t) & (~(trade_py & trade_t) | (m.verso == m.verso_t))
    both = m[trade_py & trade_t]
    out = dict(giorni=int(len(m)), trade_python=int(trade_py.sum()), trade_tester=int(trade_t.sum()),
               quota_stessa_decisione=float(stessa_decisione.mean()), trade_in_comune=int(len(both)),
               stesso_verso_in_comune=float((both.verso == both.verso_t).mean()),
               corr_R=float(np.corrcoef(both.R_lordo, both.R)[0, 1]),
               R_medio_python_lordo=float(both.R_lordo.mean()), R_medio_tester=float(both.R.mean()),
               diff_prezzo_in_mediana=float((both.prezzo_in_x - both.prezzo_in_y).abs().median()) if "prezzo_in_x" in both else None,
               uscite_python=both.uscita_x.value_counts().to_dict() if "uscita_x" in both else None)
    soglie = dict(decisione=out["quota_stessa_decisione"] >= 0.95, corr=out["corr_R"] >= 0.90,
                  diff_R=abs(out["R_medio_python_lordo"] - out["R_medio_tester"]) <= 0.05)
    out["soglie"] = soglie; out["SUPERATO"] = all(soglie.values())
    disc = m[~stessa_decisione][["giorno_srv", "esito", "verso", "verso_t", "R_lordo", "R"]]
    disc.to_csv(os.path.join(OUT, "EQUIV_US100_discordanze.csv"), sep=";", decimal=",", index=False)
    json.dump(out, open(os.path.join(OUT, "EQUIV_US100.json"), "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


def stat_paniere(a):
    """a: DataFrame (giorno, R_netto, R_stress, R_lordo) gia' aggregato per giorno."""
    x = a.R_netto.to_numpy(); g = pd.DatetimeIndex(a.giorno).to_numpy(); n = len(x)
    if n < 30: return dict(n=n, p=1.0)
    m, t, G = C.cr1(x, g); p = float(stats.t.sf(t, G - 1))
    d = pd.DatetimeIndex(a.giorno); med = d.sort_values()[n // 2]
    anni = pd.Series(x).groupby(d.year).agg(["mean", "size"]); anni = anni[anni["size"] >= 10]
    contr = pd.Series(x).groupby(d.normalize()).sum() / n
    via = set(contr.abs().sort_values(ascending=False).index[:int(np.ceil(0.01 * len(contr)))])
    return dict(n=n, giorni_anno=n / max(1e-9, (d.max() - d.min()).days / 365.25), netto_R=m, t=t, p=p,
                p_boot=C.bootstrap_giorni(x, g), stress_R=float(a.R_stress.mean()), lordo_R=float(a.R_lordo.mean()),
                meta1=float(x[d < med].mean()), meta2=float(x[d >= med].mean()), taglio=str(med.date()),
                anni_validi=int(len(anni)), quota_anni_pos=float((anni["mean"] > 0).mean()) if len(anni) else np.nan,
                senza_influenti=float(x[~d.normalize().isin(via)].mean()), primo=str(d.min().date()), ultimo=str(d.max().date()))

def test():
    T, Tc = [], []
    for paniere, membri in PANIERI.items():
        for s, fi, fc in membri:
            x = orb_strumento(s, fi, spread="oggi"); x["paniere"] = paniere; T.append(x)
            if fc:
                y = orb_strumento(s, fc, spread="oggi"); y["paniere"] = paniere; Tc.append(y)
            print(paniere, s, "fatto", flush=True)
    T = pd.concat(T, ignore_index=True); Tc = pd.concat(Tc, ignore_index=True)
    tr = T[T.esito == "trade"].copy(); trc = Tc[Tc.esito == "trade"].copy()
    assert pd.DatetimeIndex(tr.giorno).max() < pd.Timestamp("2024-01-01")
    T.to_csv(os.path.join(OUT, "S3_trade.csv"), sep=";", decimal=",", index=False)
    # ORB US100 esistente (lista del tester, solo date < 2024) per l'indipendenza
    O = pd.read_csv(os.path.join(QUI, "..", "portafoglio_esistente", "ORB_P1_trade.csv"), sep=";", decimal=",")
    O["giorno"] = pd.to_datetime(O.ingresso_srv, format="%Y.%m.%d %H:%M:%S").dt.normalize()
    O = O[O.giorno < pd.Timestamp("2024-01-01")].groupby("giorno").R.sum()
    righe, sec = [], []
    for paniere in PANIERI:
        x = tr[tr.paniere == paniere]
        a = x.groupby("giorno").agg(R_netto=("R_netto", "mean"), R_stress=("R_stress", "mean"), R_lordo=("R_lordo", "mean")).reset_index()
        st = stat_paniere(a); st["paniere"] = paniere
        per = x.groupby("strumento").R_netto.mean()
        st["strumenti_pos"], st["strumenti"] = int((per > 0).sum()), int(len(per))
        xc = trc[trc.paniere == paniere]
        ac = xc.groupby("giorno").R_lordo.mean(); ap = x[x.strumento.isin(xc.strumento.unique())].groupby("giorno").R_lordo.mean()
        com = ap.index.intersection(ac.index)
        st["conc_n"], st["conc_lordo_ftmo"] = int(len(com)), float(ac.loc[com].mean()) if len(com) else np.nan
        j = a.set_index("giorno").R_netto.to_frame().join(O.rename("orb"), how="inner")
        st["corr_ORB_US100"], st["giorni_comuni_ORB"] = (float(j.corr().iloc[0, 1]) if len(j) > 30 else np.nan), int(len(j))
        righe.append(st)
        for sname, y in x.groupby("strumento"):
            m, t, G = C.cr1(y.R_netto.to_numpy(), pd.DatetimeIndex(y.giorno).to_numpy())
            sec.append(dict(paniere=paniere, strumento=sname, n=len(y), netto_R=m, t=t, lordo_R=y.R_lordo.mean(), stress_R=y.R_stress.mean(),
                            quota_stop=(y.uscita == "stop").mean(), quota_target=(y.uscita == "target").mean(),
                            quota_fine=(y.uscita == "fine sessione").mean(), costo_spread_R=y.spread_R.mean(),
                            per_anno=y.groupby(pd.DatetimeIndex(y.giorno).year).R_netto.mean().round(3).to_dict()))
    R = pd.DataFrame(righe)
    R["bh"], soglia = C.bh(R.p.fillna(1.0).to_numpy(), 0.10)
    conc_ok = (R.conc_n < 100) | (np.sign(R.conc_lordo_ftmo) == np.sign(R.lordo_R))
    R["promosso"] = (R.bh & (R.stress_R > 0) & (R.meta1 > 0) & (R.meta2 > 0) & (R.anni_validi >= 3) & (R.quota_anni_pos >= 0.6)
                     & (R.strumenti_pos >= np.ceil(R.strumenti / 2)) & (R.senza_influenti > 0) & conc_ok)
    R["classe"] = np.where(R.promosso, "PROMOSSO", np.where((R.p < 0.05) & (R.netto_R > 0), "INDIZIO", "NULLO"))
    R["strategia_nuova_G6"] = R.corr_ORB_US100.isna() | (R.corr_ORB_US100 <= 0.3)
    R.to_csv(os.path.join(OUT, "S3_PRIMARI.csv"), sep=";", decimal=",", index=False)
    pd.DataFrame(sec).to_csv(os.path.join(OUT, "S3_SECONDARI.csv"), sep=";", decimal=",", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(R.round(4).to_string(index=False)); print(pd.DataFrame(sec).round(4).to_string(index=False))


if __name__ == "__main__":
    if sys.argv[1] == "equivalenza": equivalenza()
    elif sys.argv[1] == "test": test()
