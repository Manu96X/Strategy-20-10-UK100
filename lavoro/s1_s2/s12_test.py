# -*- coding: utf-8 -*-
"""Event study pre-registrato di S1 (prosecuzione dopo i dati macro USA) e S2 (reversione dopo le aste di chiusura),
PROTOCOLLO_S1_S2.md (versione definitiva). Solo dati di scoperta sigillati (< 01/01/2024).
Uso: python3 -I s12_test.py
Uscite in risultati/: S12_PRIMARI.csv (14 test aggregati e cancelli), S12_SECONDARI.csv (per strumento),
S12_DESCRITTIVI.json, S1_trade.csv, S2_trade.csv, S1_aggregato.csv, S2_aggregato.csv, S12_MANCANTI.csv."""
import os, sys, json
import numpy as np
import pandas as pd
import holidays
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s12_comune as C

OUT = os.path.join(C.QUI, "risultati")
FINE = pd.Timestamp("2023-12-31 23:59")
NY = "America/New_York"
SLIP_STRESS = 0.3e-4                      # per ordine, tutti gli strumenti (§5)
PIP = {"EURUSD": 1e-4, "GBPUSD": 1e-4, "USDJPY": 1e-2}
SWAP_X2 = {"US500": (-0.000227, 0.000011), "US100": (-0.000227, 0.000011), "US30": (-0.000227, 0.000011),
           "US2000": (-0.000227, 0.000011), "GER40": (-0.000178, -0.000002), "UK100": (-0.000236, 0.000011)}
FASCE_EVENTO = [("08:00", "08:59"), ("09:00", "09:59"), ("10:00", "11:59"), ("12:00", "16:59")]
VALUTE = {"EURUSD": {"USD", "EUR"}, "GBPUSD": {"USD", "GBP"}, "USDJPY": {"USD", "JPY"}, "XAU": {"USD"},
          "US100": {"USD"}, "US500": {"USD"}, "US30": {"USD"}, "US2000": {"USD"},
          "GER40": {"EUR", "USD"}, "FRA40": {"EUR", "USD"}, "UK100": {"GBP", "USD"}}
FOMC_IMP2 = ["Dichiarazione del FOMC", "Verbali FOMC", "Proiezioni Economiche del FOMC"]


# ------------------------------------------------------------------ costi (§5)
_T = pd.read_csv(os.path.join(OUT, "COSTI_TABELLA_CONGELATA.csv"), sep=";", decimal=",")
TAB = {(r.strumento, r.contesto): (r.base_bps / 1e4, r.stress_bps / 1e4) for r in _T.itertuples()}

def ctx_evento(t_ny):
    hm = t_ny.strftime("%H:%M")
    for a, b in FASCE_EVENTO:
        if a <= hm <= b: return f"S1_evento|{a}-{b}"
    return ctx_ny(t_ny)

def ctx_ny(t_ny):
    return "NY|" + t_ny.floor("30min").strftime("%H:%M")

def spread(strumento, contesti, scen):
    j = 0 if scen == "base" else 1
    return np.array([TAB[(strumento, c)][j] for c in contesti])

def commissione(strumento, prezzo):
    prezzo = np.asarray(prezzo, float)
    if strumento in ("EURUSD", "GBPUSD"): return 5.0 / (1e5 * prezzo)
    if strumento == "USDJPY": return np.full(len(prezzo), 5.0 / 1e5)
    if strumento == "XAU": return 6.0 / (100.0 * prezzo)
    return np.zeros(len(prezzo))


# ------------------------------------------------------------------ calendario (UTC+3 fisso)
def calendario():
    c = pd.read_csv(os.path.join(C.REPO, "calendario_economico.csv"), sep=";", skiprows=1, encoding="latin-1", low_memory=False)
    c["ts"] = pd.to_datetime(c.ora_server, format="%Y.%m.%d %H:%M")
    c = c[c.modo_orario == "ORARIO_ESATTO"].copy()
    # 'ora_server' del calendario esportato = UTC + 3 ore FISSE in tutti gli anni (verificato: NFP 08:30, ISM 10:00, FOMC 14:00 NY)
    utc = pd.DatetimeIndex(c.ts - pd.Timedelta(hours=3)).tz_localize("UTC")
    c["T_ny"] = utc.tz_convert(C.NY).tz_localize(None)
    return c

def eventi_s1(cal):
    ids = set(pd.read_csv(os.path.join(C.QUI, "EVENTI_S1_ELENCO_CHIUSO.csv"), sep=";").event_id)
    u = cal[(cal.valuta == "USD") & (cal.importanza == 3) & cal.event_id.isin(ids) & cal.attuale.notna()]
    u = u[(u.T_ny.dt.weekday < 5) & (u.T_ny <= FINE)]
    return pd.DatetimeIndex(sorted(u.T_ny.unique()))

def vietate(cal):
    v = cal[(cal.importanza == 3) | ((cal.valuta == "USD") & cal.evento.isin(FOMC_IMP2))]
    return v[["T_ny", "valuta"]].drop_duplicates()

def vietate_per(viet, strumento):
    return pd.DatetimeIndex(sorted(viet[viet.valuta.isin(VALUTE[strumento])].T_ny.unique()))


# ------------------------------------------------------------------ S1
S1_STRUMENTI = {"EURUSD": ("FTMO", None), "GBPUSD": ("FTMO", None), "USDJPY": ("FTMO", None),
                "XAU": ("PEP", "FTMO"), "US100": ("PEP", "FTMO"), "US500": ("PEP", "FTMO")}
H_S1, C_S1 = (30, 60, 120), (0.10, 0.25)
INDICI_USA = {"US100", "US500", "US30", "US2000"}

def s1_strumento(strumento, feed, ev, viet):
    df = C.carica(strumento, feed); reg = C.FEED[(strumento, feed)][4]
    inizio = pd.Timestamp(C.FEED[(strumento, feed)][3])
    T = ev[(ev >= inizio) & (ev <= FINE)]
    if strumento in INDICI_USA:
        chiusi = {pd.Timestamp(x) for x in holidays.NYSE(years=range(2016, 2025)).keys()}
        T = T[~T.normalize().isin(chiusi)]
    V = vietate_per(viet, strumento); Vv = V.values
    E = pd.DataFrame({"T_ny": T})
    # ingresso escluso se una notizia vietata cade in [T+1, T+5]
    k1 = np.searchsorted(Vv, (T + pd.Timedelta(minutes=1)).values, side="left")
    k5 = np.searchsorted(Vv, (T + pd.Timedelta(minutes=5)).values, side="right")
    E["conflitto"] = k5 > k1
    # prima notizia vietata dopo T (minuto diverso da T)
    kn = np.searchsorted(Vv, T.values, side="right")
    nxt = pd.DatetimeIndex(np.where(kn < len(Vv), Vv[np.clip(kn, 0, len(Vv) - 1)], np.datetime64("NaT")))
    E["E_next"] = nxt
    srv = lambda x: C.a_server(pd.DatetimeIndex(x), NY, reg)
    E["P_pre"] = C.prezzo_prima(df, srv(T))
    E["P_in"] = C.prezzo_a(df, srv(T + pd.Timedelta(minutes=3)))
    for H in H_S1:
        tH = T + pd.Timedelta(minutes=H)
        cap = nxt - pd.Timedelta(minutes=3)
        tout = pd.DatetimeIndex(np.where(~pd.isna(cap) & (cap < tH), cap.values, tH.values))
        valido = tout >= T + pd.Timedelta(minutes=4)
        E[f"t_out_{H}"] = tout
        E[f"P_out_{H}"] = np.where(valido, C.prezzo_a(df, srv(tout)), np.nan)
    giorni = pd.date_range(inizio, FINE, freq="D")
    sig = C.sigma_giornaliera(df, NY, "16:00", reg, giorni)
    E["sigma"] = sig.reindex(T.normalize()).values
    E["r0"] = np.log(E.P_in / E.P_pre)
    E["strumento"], E["feed"] = strumento, feed
    return E

def trade_s1(E, strumento):
    out = []
    b0 = E[~E.conflitto & E.P_pre.notna() & E.P_in.notna() & E.sigma.notna() & (E.r0 != 0)]
    for H in H_S1:
        b = b0[b0[f"P_out_{H}"].notna()]
        for c in C_S1:
            x = b[b.r0.abs() >= c * b.sigma].copy()
            if not len(x): continue
            x["q"] = np.sign(x.r0)
            x["ret"] = np.log(x[f"P_out_{H}"] / x.P_in)
            cin = [ctx_evento(t) for t in x.T_ny]; cout = [ctx_ny(t) for t in pd.DatetimeIndex(x[f"t_out_{H}"])]
            for scen in ("base", "stress"):
                sp = np.where(x.q > 0, spread(strumento, cin, scen), spread(strumento, cout, scen))
                cst = sp + commissione(strumento, x.P_in) + (2 * SLIP_STRESS if scen == "stress" else 0.0)
                x[f"costo_{scen}"] = cst
            x["lordo"] = x.q * x.ret
            x["netto_base"] = x.lordo - x.costo_base; x["netto_stress"] = x.lordo - x.costo_stress
            x["test_id"] = f"S1|c={c:.2f}|H{H}"; x["chiave"] = x.T_ny; x["data_ny"] = x.T_ny.dt.normalize()
            out.append(x)
    return pd.concat(out, ignore_index=True)


# ------------------------------------------------------------------ S2
S2_INDICI = {  # borsa, tz, asta, ritardo ingresso (min), pre-apertura, paniere, feed inferenza, feed concordanza, X2 ammesso
    "US500": ("NYSE", NY, "16:00", 1, "09:25", "USA", "PEP", "FTMO", True),
    "US100": ("NYSE", NY, "16:00", 1, "09:25", "USA", "PEP", "FTMO", True),
    "US30": ("NYSE", NY, "16:00", 1, "09:25", "USA", "PEP", None, True),
    "US2000": ("NYSE", NY, "16:00", 1, "09:25", "USA", "PEP", "FTMO", True),
    "GER40": ("XETRA", "Europe/Berlin", "17:30", 6, "08:55", "EUROPA", "PEP", "FTMO", True),
    "UK100": ("LSE", "Europe/London", "16:30", 6, "07:55", "EUROPA", "PEP", "FTMO", True),
    "FRA40": ("EURONEXT", "Europe/Paris", "17:30", 6, "08:55", "EUROPA", "FTMO", None, False),
}

def a_ny(locali, tz):
    loc = pd.DatetimeIndex(locali)
    return loc.tz_localize(tz, ambiguous="NaT", nonexistent="NaT").tz_convert(C.NY).tz_localize(None)

def s2_indice(indice, feed, viet, placebo=False):
    borsa, tz, asta, rit, pre, _, _, _, x2ok = S2_INDICI[indice]
    df = C.carica(indice, feed); reg = C.FEED[(indice, feed)][4]
    inizio = pd.Timestamp(C.FEED[(indice, feed)][3])
    g = C.giorni_borsa(borsa, inizio, "2023-12-31")
    h, m = map(int, asta.split(":"))
    A = g + pd.Timedelta(hours=h, minutes=m) - (pd.Timedelta(minutes=60) if placebo else pd.Timedelta(0))
    srv = lambda x: C.a_server(pd.DatetimeIndex(x), tz, reg)
    d = pd.DataFrame({"giorno": g})
    d["P_A"] = C.prezzo_prima(df, srv(A))
    d["P_AL"] = C.prezzo_prima(df, srv(A - pd.Timedelta(minutes=15)))
    t_in = A + pd.Timedelta(minutes=rit)
    d["P_in"] = C.prezzo_a(df, srv(t_in))
    d["t_in_ny"] = a_ny(t_in, tz)
    t_x1 = A + pd.Timedelta(minutes=45)
    d["P_X1"] = C.prezzo_a(df, srv(t_x1)); d["t_X1_ny"] = a_ny(t_x1, tz)
    d["P_X2"] = np.nan; d["t_X2_ny"] = pd.NaT
    if x2ok and not placebo:
        nxt = pd.Series(list(g[1:]) + [pd.NaT])
        consecutivo = ((nxt - pd.Series(g)).dt.days == 1).to_numpy()
        ph, pm = map(int, pre.split(":"))
        t_pre_ny = a_ny(pd.DatetimeIndex(nxt) + pd.Timedelta(hours=ph, minutes=pm), tz)
        V = vietate_per(viet, indice).values
        tin = d.t_in_ny.values
        k = np.searchsorted(V, tin, side="right")
        primo = np.where(k < len(V), V[np.clip(k, 0, len(V) - 1)], np.datetime64("NaT"))
        cap = pd.DatetimeIndex(primo) - pd.Timedelta(minutes=3)
        tx2 = pd.DatetimeIndex(np.where(~pd.isna(cap) & (cap < t_pre_ny), cap.values, t_pre_ny.values))
        ok = consecutivo & (tx2 >= pd.DatetimeIndex(tin) + pd.Timedelta(minutes=1))
        d["t_X2_ny"] = tx2
        d["P_X2"] = np.where(ok, C.prezzo_a(df, C.a_server(tx2, NY, reg)), np.nan)
        d["X2_limitata"] = (~pd.isna(cap) & (cap < t_pre_ny))
    d["sigma"] = C.sigma_giornaliera(df, tz, asta, reg, g).values
    d["m"] = np.log(d.P_A / d.P_AL)
    d["indice"], d["feed"], d["paniere"] = indice, feed, S2_INDICI[indice][5]
    return d

def trade_s2(d, indice, placebo=False):
    out = []
    b = d[d.P_A.notna() & d.P_AL.notna() & d.P_in.notna() & d.sigma.notna() & (d.m != 0)]
    paniere = S2_INDICI[indice][5]
    for usc in ("X1", "X2"):
        bb = b[b[f"P_{usc}"].notna()]
        if not len(bb): continue
        for c in (0.0, 0.10):
            x = bb[bb.m.abs() >= c * bb.sigma].copy()
            if not len(x): continue
            x["q"] = -np.sign(x.m)
            x["ret"] = np.log(x[f"P_{usc}"] / x.P_in)
            cin = ["S2|placebo_ingresso" if placebo else "S2|ingresso"] * len(x)
            if usc == "X1":
                cout = ["S2|placebo_X1" if placebo else "S2|X1"] * len(x)
            else:
                cout = [ctx_ny(t) if lim else "S2|X2" for t, lim in zip(pd.DatetimeIndex(x.t_X2_ny), x.X2_limitata)]
            sw = np.zeros(len(x))
            if usc == "X2":
                sl, ss = SWAP_X2[indice]; sw = np.where(x.q > 0, sl, ss)
            for scen in ("base", "stress"):
                sp = np.where(x.q > 0, spread(indice, cin, scen), spread(indice, cout, scen))
                swc = -sw if scen == "base" else -np.where(sw < 0, 1.5 * sw, sw)
                x[f"costo_{scen}"] = sp + swc + (2 * SLIP_STRESS if scen == "stress" else 0.0)
            x["lordo"] = x.q * x.ret
            x["netto_base"] = x.lordo - x.costo_base; x["netto_stress"] = x.lordo - x.costo_stress
            x["test_id"] = f"S2|{paniere}|c={c:.2f}|{usc}" + ("|PLACEBO" if placebo else "")
            x["chiave"] = x.giorno; x["data_ny"] = x.giorno; x["strumento"] = indice
            out.append(x)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


# ------------------------------------------------------------------ aggregazione e statistiche
def z_cols(X):
    X = X.copy()
    X["zb"] = X.netto_base / X.sigma; X["zs"] = X.netto_stress / X.sigma; X["zl"] = X.lordo / X.sigma
    X["bps"] = X.netto_base * 1e4
    return X

def aggrega(X):
    g = X.groupby(["test_id", "chiave"])
    A = g.agg(zb=("zb", "mean"), zs=("zs", "mean"), zl=("zl", "mean"), bps=("bps", "mean"), n_str=("zb", "size"),
              data_ny=("data_ny", "first")).reset_index()
    return A

def t_cr1(x, gruppi):
    m, t, G = C.cr1(x, gruppi)
    p = float(stats.t.sf(t, G - 1)) if (np.isfinite(t) and G > 1) else 1.0
    return m, t, G, p

def stat_test(a):
    x = a.zb.to_numpy(); g = pd.DatetimeIndex(a.data_ny).normalize().to_numpy()
    n = len(x)
    if n < 30: return dict(n=n, p=1.0)
    m, t, G, p = t_cr1(x, g)
    d = pd.DatetimeIndex(a.data_ny)
    anni = pd.Series(x).groupby(d.year).agg(["mean", "size"]); anni = anni[anni["size"] >= 10]
    # influenza: togli l'1% delle date con il maggior |contributo| alla media
    contr = pd.Series(x).groupby(d.normalize()).sum() / n
    k = int(np.ceil(0.01 * len(contr)))
    via = set(contr.abs().sort_values(ascending=False).index[:k])
    mask = ~d.normalize().isin(via)
    return dict(n=n, giorni=G, eventi_anno=n / max(1e-9, (d.max() - d.min()).days / 365.25),
                netto_base_z=m, t=t, p=p, p_boot=C.bootstrap_giorni(x, g),
                netto_stress_z=float(a.zs.mean()), lordo_z=float(a.zl.mean()), netto_base_bps=float(a.bps.mean()),
                meta1=float(x[d < pd.Timestamp("2020-01-01")].mean()) if (d < pd.Timestamp("2020-01-01")).any() else np.nan,
                meta2=float(x[d >= pd.Timestamp("2020-01-01")].mean()),
                anni_validi=int(len(anni)), quota_anni_pos=float((anni["mean"] > 0).mean()) if len(anni) else np.nan,
                senza_influenti_z=float(x[mask].mean()), troncato5_z=float(np.clip(x, -5, 5).mean()),
                primo=str(d.min().date()), ultimo=str(d.max().date()), n_strumenti_medio=float(a.n_str.mean()))


def main():
    os.makedirs(OUT, exist_ok=True)
    cal = calendario(); ev = eventi_s1(cal); viet = vietate(cal)
    print("S1 eventi:", len(ev), "notizie vietate:", len(viet), flush=True)
    # ---- S1
    S1, S1c, ES1 = [], [], []
    for s, (fi, fc) in S1_STRUMENTI.items():
        E = s1_strumento(s, fi, ev, viet); ES1.append(E); S1.append(trade_s1(E, s).assign(strumento=s))
        if fc:
            Ec = s1_strumento(s, fc, ev, viet); S1c.append(trade_s1(Ec, s).assign(strumento=s))
        print("S1", s, "fatto", flush=True)
    S1 = z_cols(pd.concat(S1, ignore_index=True)); S1c = z_cols(pd.concat(S1c, ignore_index=True))
    # ---- S2
    S2, S2c, S2p, ES2 = [], [], [], []
    for i, cfg in S2_INDICI.items():
        d = s2_indice(i, cfg[6], viet); ES2.append(d); S2.append(trade_s2(d, i))
        S2p.append(trade_s2(s2_indice(i, cfg[6], viet, placebo=True), i, placebo=True))
        if cfg[7]: S2c.append(trade_s2(s2_indice(i, cfg[7], viet), i))
        print("S2", i, "fatto", flush=True)
    S2 = z_cols(pd.concat(S2, ignore_index=True)); S2c = z_cols(pd.concat(S2c, ignore_index=True))
    S2p = z_cols(pd.concat(S2p, ignore_index=True))
    assert S1.data_ny.max() < C.FINE_SCOPERTA and S2.data_ny.max() < C.FINE_SCOPERTA

    A1, A2 = aggrega(S1), aggrega(S2)
    righe = []
    for ipotesi, A, X, Xc, conc_str in (("S1", A1, S1, S1c, ["XAU", "US100", "US500"]),
                                        ("S2", A2, S2, S2c, ["US500", "US100", "US2000", "GER40", "UK100"])):
        for tid, a in A.groupby("test_id", sort=True):
            st = stat_test(a); st["test_id"] = tid; st["ipotesi"] = ipotesi
            x = X[X.test_id == tid]
            per_str = x.groupby("strumento").zb.mean()
            st["strumenti_netto_pos"] = int((per_str > 0).sum()); st["strumenti"] = int(len(per_str))
            # concordanza: lordo aggregato sul feed di concordanza, stessi eventi/giorni, strumenti di concordanza
            xp = x[x.strumento.isin(conc_str)]; xc = Xc[(Xc.test_id == tid) & Xc.strumento.isin(conc_str)]
            ap = xp.groupby("chiave").zl.mean(); ac = xc.groupby("chiave").zl.mean()
            comuni = ap.index.intersection(ac.index)
            st["conc_n"] = int(len(comuni)); st["conc_lordo_ftmo"] = float(ac.loc[comuni].mean()) if len(comuni) else np.nan
            st["conc_lordo_pep"] = float(ap.loc[comuni].mean()) if len(comuni) else np.nan
            righe.append(st)
    R = pd.DataFrame(righe)
    R["bh"] = False
    for ip in ("S1", "S2"):
        msk = R.ipotesi == ip
        R.loc[msk, "bh"], _ = C.bh(R.loc[msk, "p"].fillna(1.0).to_numpy(), 0.10)
    # coerenza: stesso c, lordo aggregato > 0 su >= 2 delle 3 H (S1) o su entrambe le uscite (S2)
    def chiave_coer(tid):
        p = tid.split("|"); return "|".join(p[:-1]) if p[0] == "S1" else "|".join(p[:3])
    R["gruppo"] = R.test_id.map(chiave_coer)
    pos = R.groupby("gruppo").lordo_z.apply(lambda s: int((s > 0).sum()))
    R["coer_lordo_pos"] = R.gruppo.map(pos)
    R["coer_ok"] = np.where(R.ipotesi == "S1", R.coer_lordo_pos >= 2,
                            R.coer_lordo_pos >= R.groupby("gruppo").test_id.transform("size")) & (R.strumenti_netto_pos >= np.ceil(R.strumenti / 2))
    conc_ok = (R.conc_n < 100) | (np.sign(R.conc_lordo_ftmo) == np.sign(R.lordo_z))
    R["conc_ok"] = conc_ok
    R["promosso"] = (R.bh & (R.netto_stress_z > 0) & (R.netto_base_bps > 0) & (R.meta1 > 0) & (R.meta2 > 0)
                     & (R.anni_validi >= 3) & (R.quota_anni_pos >= 0.6) & R.coer_ok & (R.senza_influenti_z > 0) & R.conc_ok)
    R["classe"] = np.where(R.promosso, "PROMOSSO", np.where((R.p < 0.05) & (R.netto_base_z > 0), "INDIZIO", "NULLO"))
    R.to_csv(os.path.join(OUT, "S12_PRIMARI.csv"), sep=";", decimal=",", index=False)

    # secondari per strumento (descrittivi; BH solo dentro le configurazioni promosse)
    sec = []
    for X in (S1, S2):
        for (tid, s), x in X.groupby(["test_id", "strumento"]):
            m, t, G, p = t_cr1(x.zb.to_numpy(), x.data_ny.to_numpy()) if len(x) >= 30 else (x.zb.mean(), np.nan, 0, 1.0)
            sec.append(dict(test_id=tid, strumento=s, n=len(x), netto_base_z=m, t=t, p=p, lordo_z=x.zl.mean(),
                            netto_stress_z=x.zs.mean(), netto_base_bps=x.bps.mean(), costo_base_bps=x.costo_base.mean() * 1e4))
    SEC = pd.DataFrame(sec); SEC["bh_dentro_promossi"] = False
    for tid in R[R.promosso].test_id:
        msk = SEC.test_id == tid
        SEC.loc[msk, "bh_dentro_promossi"], _ = C.bh(SEC.loc[msk, "p"].to_numpy(), 0.10)
    SEC.to_csv(os.path.join(OUT, "S12_SECONDARI.csv"), sep=";", decimal=",", index=False)

    # descrittivi: placebo S2, giorni di asta pesante, UK100 X2 senza mercoledi', mancanti
    desc = {}
    AP = aggrega(S2p)
    for tid, a in AP.groupby("test_id"):
        desc[f"placebo|{tid}"] = dict(n=len(a), netto_base_z=float(a.zb.mean()), lordo_z=float(a.zl.mean()))
    def pesante(dd):
        dd = pd.DatetimeIndex(dd)
        terzo_ven = (dd.weekday == 4) & (dd.day >= 15) & (dd.day <= 21) & dd.month.isin([3, 6, 9, 12])
        ultimo_ven_giu = (dd.weekday == 4) & (dd.month == 6) & (dd.day >= 24)
        return terzo_ven | ultimo_ven_giu
    for tid, a in A2.groupby("test_id"):
        p = pesante(a.data_ny)
        desc[f"asta_pesante|{tid}"] = dict(n_pesanti=int(p.sum()), lordo_pesanti=float(a.zl[p].mean()) if p.any() else None,
                                           lordo_altri=float(a.zl[~p].mean()))
    for tid in [t for t in A2.test_id.unique() if t.endswith("X2") and "EUROPA" in t]:
        x = S2[(S2.test_id == tid) & ~((S2.strumento == "UK100") & (pd.DatetimeIndex(S2.data_ny).weekday == 2))]
        a = aggrega(x)
        desc[f"senza_UK100_mercoledi|{tid}"] = dict(n=len(a), netto_base_z=float(a.zb.mean()))
    json.dump(desc, open(os.path.join(OUT, "S12_DESCRITTIVI.json"), "w"), indent=1, default=float)

    # mancanti per strumento, anno, finestra (eventi o giorni ammissibili senza prezzo)
    manc = []
    for E in ES1:
        b = E[~E.conflitto]
        for H in H_S1:
            miss = b[["P_pre", "P_in", f"P_out_{H}", "sigma"]].isna().any(axis=1)
            for an, mm in miss.groupby(b.T_ny.dt.year):
                manc.append(dict(ipotesi="S1", strumento=E.strumento.iloc[0], finestra=f"H{H}", anno=int(an), ammissibili=len(mm), mancanti_quota=float(mm.mean())))
    for d in ES2:
        for usc in ("X1", "X2"):
            if d[f"P_{usc}"].isna().all(): continue
            miss = d[["P_A", "P_AL", "P_in", f"P_{usc}", "sigma"]].isna().any(axis=1)
            for an, mm in miss.groupby(pd.DatetimeIndex(d.giorno).year):
                manc.append(dict(ipotesi="S2", strumento=d.indice.iloc[0], finestra=usc, anno=int(an), ammissibili=len(mm), mancanti_quota=float(mm.mean())))
    pd.DataFrame(manc).to_csv(os.path.join(OUT, "S12_MANCANTI.csv"), sep=";", decimal=",", index=False)

    col = ["test_id", "strumento", "chiave", "data_ny", "q", "sigma", "P_in", "ret", "costo_base", "costo_stress", "netto_base"]
    S1[col + ["r0"]].to_csv(os.path.join(OUT, "S1_trade.csv"), sep=";", decimal=",", index=False)
    S2[col + ["m"]].to_csv(os.path.join(OUT, "S2_trade.csv"), sep=";", decimal=",", index=False)
    A1.to_csv(os.path.join(OUT, "S1_aggregato.csv"), sep=";", decimal=",", index=False)
    A2.to_csv(os.path.join(OUT, "S2_aggregato.csv"), sep=";", decimal=",", index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
    print(R[["test_id", "n", "eventi_anno", "lordo_z", "netto_base_z", "t", "p", "bh", "netto_stress_z", "netto_base_bps",
             "meta1", "meta2", "quota_anni_pos", "coer_ok", "senza_influenti_z", "conc_n", "conc_lordo_ftmo", "classe"]].round(4).to_string(index=False))

if __name__ == "__main__":
    main()
