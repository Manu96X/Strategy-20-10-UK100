# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA F: correlazioni e anticipi fra strumenti
(Hanna 2024). 108 test esatti. Solo dati di scoperta sigillati (< 01/01/2024) tramite eventi_comune.

Serie comune: prezzo alle 16:00 di New York (EC.prezzo_alle: close dell'ultimo M1 che inizia prima dell'istante,
entro 15 minuti) per tutti i 10 strumenti, giorni feriali (data di calendario di New York); l'istante NY e'
convertito nel fuso dello strumento (colonna 'loc' di EC.carica) con zoneinfo.
  x_i(d) = ln(P_i(d)/P_i(d-1)), d-1 = riga valida precedente entro 4 giorni di calendario (altrimenti NaN);
  sig_i(d) = dev.std dei 20 rendimenti (validi) fino a d INCLUSO (rolling 20 sui rendimenti non mancanti);
  z_i(d)  = x_i(d) / sig_i(d).

F1 (100 test, 10 predittori x 10 bersagli, anche i=j): y_j(d+1) = ln(P_j(d+1)/P_j(d)) / sig_j(d), con d+1 = riga
    valida successiva del bersaglio entro 4 giorni di calendario; regressione OLS y_j(d+1) = a + b*z_i(d).
    media_z = media_anomala = b; t = HC1; p_primario = permutazione (2000 rimescolamenti di z_i, bilaterale);
    quota anni = quota degli anni (con >= 20 osservazioni) con b dell'anno dello stesso segno di b;
    netto: ogni giorno posizione segno(b*z_i(d)) sul bersaglio da 16:00 NY di d a 16:00 NY di d+1, ingresso all'ask
    con spread dell'ora server 23 (istruzioni F1), notti di calendario; media sugli z netti (giorni con segnale 0
    esclusi). Feed d'inferenza per predittore e bersaglio; concordanza: predittore sul feed d'inferenza e bersaglio
    sul feed FTMO (se esiste e non e' gia' il feed d'inferenza).
F2 (8 test): evento = VIX (Pepperstone) alle 16:00 NY del giorno d >= massimo delle ultime 10 chiusure 16:00 NY
    (incluso d). Bersagli US500, US100, GER40, UK100 (serie 16:00 NY): F2a finestra d -> d+1 riga di trading,
    F2b d -> d+3 righe di trading (ogni passo entro 4 giorni di calendario). z = W / sig_bersaglio(d).
    Benchmark e pool placebo: tutte le finestre di 1 (F2a) o 3 (F2b) righe del bersaglio con ingresso nello stesso
    periodo del VIX e negli stessi anni degli eventi. t = EC.t_cluster; p = EC.p_placebo; quota anni con >= 2 eventi;
    netto con verso = segno della media anomala, spread dell'ora server 23 (come F1, vedi note).
Esecuzione: python3 -I famiglia_F.py
"""
import os, sys
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

sys.path.insert(0, '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study')
import eventi_comune as EC

QUI = '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study'
OUT = os.path.join(QUI, 'risultati', 'famiglia_F.csv')
ORDINE = ["US500", "US100", "GER40", "UK100", "XAU", "XAG", "BRENT", "USOIL", "VIX", "USDX"]
INDICI = ["US500", "US100", "GER40", "UK100"]
NREP = 2000
NY = ZoneInfo("America/New_York")
ORA_INGRESSO = 23            # ora server dell'ingresso alle 16:00 NY (istruzioni F1)
MIN_OBS_ANNO = 20
_CACHE = {}

# EC.tabella_spread rilegge i CSV a ogni chiamata (lentissimo in un loop su ~100.000 trade): memoizzazione in
# memoria, solo in questo processo (il file eventi_comune.py non viene toccato; risultato identico).
_tab_orig = EC.tabella_spread
_TAB = {}
def _tab_cache(s):
    if s not in _TAB: _TAB[s] = _tab_orig(s)
    return _TAB[s]
EC.tabella_spread = _tab_cache


def serie16(s, f):
    """Serie giornaliera alle 16:00 NY (giorni feriali NY) dello strumento s sul feed f."""
    if (s, f) in _CACHE: return _CACHE[(s, f)]
    m1 = EC.carica(s, f)
    tz = ZoneInfo(EC.STRUMENTI[s]["tz"])
    ts = pd.to_datetime(m1.ts)
    # date NY = data server - 7 ore (ora server = NY + 7)
    dny = (ts - pd.Timedelta(hours=7)).dt.normalize()
    date = pd.date_range(dny.min(), dny.max(), freq="D")
    date = date[date.weekday < 5]
    ist_ny = pd.DatetimeIndex([pd.Timestamp(x.year, x.month, x.day, 16, 0, tzinfo=NY) for x in date])
    ist_loc = ist_ny.tz_convert(tz).tz_localize(None)
    P, tsu = EC.prezzo_alle(m1, ist_loc)
    d = pd.DataFrame({"dt": date, "P": P, "ts_P": pd.to_datetime(tsu)})
    d = d.dropna(subset=["P"]).reset_index(drop=True)
    assert d.dt.max() < pd.Timestamp("2024-01-01"), "dati oltre il 2023!"
    gap = (d.dt - d.dt.shift()).dt.days
    d["r"] = np.where(gap <= 4, np.log(d.P / d.P.shift()), np.nan)
    # sigma = dev.std degli ultimi 20 rendimenti VALIDI fino a d incluso (i rendimenti mancanti per buchi > 4 giorni
    # non azzerano la finestra); nelle righe con r mancante vale la sigma dell'ultima riga valida (nota a d)
    rs = d.r.dropna().rolling(20, min_periods=20).std()
    d["sig"] = rs.reindex(d.index).ffill()
    d["z"] = d.r / d.sig
    # finestre in avanti di 1 e 3 righe (ogni passo entro 4 giorni)
    for L in (1, 3):
        ok = np.ones(len(d), bool)
        for k in range(1, L + 1):
            g = (d.dt.shift(-k) - d.dt.shift(-k + 1)).dt.days
            ok &= (g <= 4).to_numpy()
        Pf = d.P.shift(-L)
        d[f"W{L}"] = np.where(ok, np.log(Pf / d.P), np.nan)
        d[f"P{L}"] = np.where(ok, Pf, np.nan)
        d[f"dt{L}"] = d.dt.shift(-L)
        d[f"y{L}"] = d[f"W{L}"] / d.sig
    d["anno"] = d.dt.dt.year
    d = d.set_index("dt", drop=False)
    _CACHE[(s, f)] = d
    return d


def costi_z(s, Pe, Pu, verso, sig, notti, scen):
    if EC.tabella_spread(s) is None: return np.full(len(Pe), np.nan)
    c = np.array([EC.costo_trade(s, Pe[k], ORA_INGRESSO, notti[k], scen) for k in range(len(Pe))])
    return (verso * (Pu - Pe) - c) / (sig * Pe)


def hc1(x, y):
    n = len(x); X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X); beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    meat = (X * (e ** 2)[:, None]).T @ X
    V = XtX_inv @ meat @ XtX_inv * n / (n - 2)
    return beta, beta[1] / np.sqrt(V[1, 1])


def f1(pi, fi, pj, fj, seed):
    a = serie16(pi, fi); b = serie16(pj, fj)
    df = pd.DataFrame({"x": a.z}).join(b[["y1", "P", "P1", "sig", "dt1", "W1", "anno", "ts_P"]], how="inner")
    df = df.dropna(subset=["x", "y1"])
    x = df.x.to_numpy(); y = df.y1.to_numpy(); n = len(x)
    beta, t = hc1(x, y); bb = beta[1]
    xc = x - x.mean(); yc = y - y.mean(); sxx = (xc ** 2).sum()
    rng = np.random.default_rng(seed)
    perm = np.argsort(rng.random((NREP, n)), axis=1)
    bp = (xc[perm] @ yc) / sxx
    p = float((1 + (np.abs(bp) >= abs(bb)).sum()) / (1 + NREP))
    # per anno
    ya = {}
    for an, g in df.groupby("anno"):
        if len(g) >= MIN_OBS_ANNO and g.x.var() > 0:
            ya[int(an)] = float(np.polyfit(g.x, g.y1, 1)[0])
    quota = float(np.mean([np.sign(v) == np.sign(bb) for v in ya.values()])) if ya else np.nan
    # netto
    verso = np.sign(bb * x); m = verso != 0
    notti = ((df.dt1 - df.index.to_series()).dt.days).to_numpy()
    Pe = df.P.to_numpy(); Pu = df.P1.to_numpy(); sig = df.sig.to_numpy()
    nb = costi_z(pj, Pe[m], Pu[m], verso[m], sig[m], notti[m], "base")
    ns = costi_z(pj, Pe[m], Pu[m], verso[m], sig[m], notti[m], "stress")
    lordo_z = verso[m] * y[m]
    bps = float(np.mean(verso[m] * df.W1.to_numpy()[m]) * 1e4)
    anni = df.anno.to_numpy()
    return dict(n=n, b=bb, a=beta[0], t=t, p=p, quota=quota, ya=ya, anni_validi=len(ya),
                eventi_anno=n / len(np.unique(anni)), netto_base=float(np.mean(nb)) if np.isfinite(nb).any() else np.nan,
                netto_stress=float(np.mean(ns)) if np.isfinite(ns).any() else np.nan, lordo_z=float(lordo_z.mean()),
                bps=bps, corr=float(np.corrcoef(x, y)[0, 1]), primo=str(df.index.min().date()),
                ultimo=str(df.index.max().date()), hit=float(np.mean(lordo_z > 0)),
                b_senza2020=float(np.polyfit(x[anni != 2020], y[anni != 2020], 1)[0]) if (anni != 2020).sum() > 20 else np.nan)


def f2(bers, fb, L, seed, vix):
    d = serie16(bers, fb)
    ev_dates = vix.index[vix.ev.to_numpy()]
    inizio_vix = vix.index[vix.P.rolling(10, min_periods=10).max().notna().to_numpy()].min()
    fine_vix = vix.index.max()
    yk, Wk, Pk, dk = f"y{L}", f"W{L}", f"P{L}", f"dt{L}"
    e = d.loc[d.index.isin(ev_dates)].dropna(subset=[yk])
    z = e[yk].to_numpy(); W = e[Wk].to_numpy(); anni = e.anno.to_numpy()
    pool_all = d[(d.index >= inizio_vix) & (d.index <= fine_vix)].dropna(subset=[yk])
    pool = pool_all[pool_all.anno.isin(np.unique(anni))]
    zp = pool[yk].to_numpy()
    bench = float(zp.mean()); anom = float(z.mean() - bench)
    p = EC.p_placebo(z.mean(), zp, len(z), NREP, seed)
    t = EC.t_cluster(z, e.index.to_numpy())
    t_an = EC.t_cluster(z - bench, e.index.to_numpy())
    ya = pd.Series(z - bench).groupby(anni).agg(["mean", "size"]); ya = ya[ya["size"] >= 2]
    quota = float((np.sign(ya["mean"]) == np.sign(anom)).mean()) if len(ya) else np.nan
    verso = 1.0 if anom > 0 else -1.0
    notti = ((e[dk] - e.index.to_series()).dt.days).to_numpy()
    Pe = e.P.to_numpy(); Pu = e[Pk].to_numpy(); sig = e.sig.to_numpy()
    nb = costi_z(bers, Pe, Pu, verso, sig, notti, "base"); ns = costi_z(bers, Pe, Pu, verso, sig, notti, "stress")
    # descrittivo: netto con l'ora server dell'M1 effettivamente usato (22) invece di 23
    c22 = np.array([EC.costo_trade(bers, Pe[k], pd.Timestamp(e.ts_P.iloc[k]).hour, notti[k], "base") for k in range(len(Pe))])
    nb22 = float(np.mean((verso * (Pu - Pe) - c22) / (sig * Pe)))
    return dict(n=len(z), media_z=float(z.mean()), anom=anom, bench=bench, bps=float(W.mean() * 1e4), t=t, t_an=t_an,
                p=p, quota=quota, anni_validi=len(ya), eventi_anno=len(z) / len(np.unique(anni)),
                netto_base=float(np.mean(nb)), netto_stress=float(np.mean(ns)), nb22=nb22, per_anno=ya["mean"].round(3).to_dict(),
                pool_n=len(zp), verso=verso, hit=float(np.mean(np.sign(W) == verso)), mediana=float(np.median(z)),
                primo=str(e.index.min().date()), ultimo=str(e.index.max().date()),
                senza2020=float(z[anni != 2020].mean() - zp[pool.anno.to_numpy() != 2020].mean()),
                ev_date=set(e.index))


def main():
    righe = []; seed = 6000
    # ------------------------------------------------------------------ F1
    for pi in ORDINE:
        fi = EC.FEED_INFERENZA[pi]
        for pj in ORDINE:
            fj = EC.FEED_INFERENZA[pj]; seed += 1
            r = f1(pi, fi, pj, fj, seed)
            c = (f1(pi, fi, pj, "FTMO", seed + 1000)
                 if (fj != "FTMO" and "FTMO" in EC.STRUMENTI[pj]["feed"]) else None)
            righe.append(dict(
                test_id=f"F1:{pi}->{pj}", famiglia="F", strumento=pj, predittore=pi, feed=f"{fi}->{fj}", n=r["n"],
                media_z=r["b"], media_anomala=r["b"], bps=r["bps"], t=r["t"], t_anomala=np.nan, p_primario=r["p"],
                quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"], eventi_anno=r["eventi_anno"],
                netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                conc_ftmo_media=(c["b"] if c else np.nan), conc_ftmo_n=(c["n"] if c else np.nan),
                benchmark_z=r["a"], seed=seed, periodo=f"{r['primo']}..{r['ultimo']}",
                note=(f"OLS y_{pj}(d+1) su z_{pi}(d); b={r['b']:.4f}, corr={r['corr']:.4f}, intercetta={r['a']:.4f}; "
                      f"lordo z medio strategia segno(b*x)={r['lordo_z']:.4f}, hit={r['hit']:.3f}; bps=lordi medi della "
                      f"strategia; b senza 2020={r['b_senza2020']:.4f}; b per anno={ {k: round(v, 3) for k, v in r['ya'].items()} }"
                      + (f"; FTMO bersaglio: b={c['b']:.4f}, t={c['t']:.2f}, p={c['p']:.3f}, n={c['n']}, periodo {c['primo']}..{c['ultimo']}" if c else ""))))
            print(righe[-1]["test_id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in righe[-1].items()
                                         if k in ["n", "media_z", "t", "p_primario", "quota_anni_stesso_segno",
                                                  "netto_base_z", "conc_ftmo_media"]}, flush=True)
    # ------------------------------------------------------------------ F2
    vix = serie16("VIX", "PEP").copy()
    vix["ev"] = (vix.P >= vix.P.rolling(10, min_periods=10).max()).to_numpy()
    print("eventi VIX:", int(vix.ev.sum()), "su", int(vix.P.rolling(10, min_periods=10).max().notna().sum()))
    for L, nome in [(1, "F2a"), (3, "F2b")]:
        for b in INDICI:
            fb = EC.FEED_INFERENZA[b]; seed += 1
            r = f2(b, fb, L, seed, vix)
            c = f2(b, "FTMO", L, seed + 1000, vix) if (fb != "FTMO" and "FTMO" in EC.STRUMENTI[b]["feed"]) else None
            righe.append(dict(
                test_id=f"{nome}:{b}", famiglia="F", strumento=b, predittore="VIX", feed=fb, n=r["n"],
                media_z=r["media_z"], media_anomala=r["anom"], bps=r["bps"], t=r["t"], t_anomala=r["t_an"],
                p_primario=r["p"], quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"],
                eventi_anno=r["eventi_anno"], netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                conc_ftmo_media=(c["anom"] if c else np.nan), conc_ftmo_n=(c["n"] if c else np.nan),
                benchmark_z=r["bench"], seed=seed, periodo=f"{r['primo']}..{r['ultimo']}",
                note=(f"VIX 16:00 NY >= max 10 chiusure -> {b} 16:00 NY d -> d+{L} righe; bench={r['bench']:.4f} su "
                      f"{r['pool_n']} finestre; verso {'long' if r['verso'] > 0 else 'short'}; hit={r['hit']:.3f}; "
                      f"mediana z={r['mediana']:.3f}; netto base con ora server M1 (22)={r['nb22']:.4f}; "
                      f"anomala senza 2020={r['senza2020']:.3f}; anomala per anno={r['per_anno']}"
                      + (f"; FTMO: z={c['media_z']:.3f}, anom={c['anom']:.3f}, p={c['p']:.3f}, periodo {c['primo']}..{c['ultimo']}" if c else ""))))
            print(righe[-1]["test_id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in righe[-1].items()
                                         if k in ["n", "media_z", "media_anomala", "t", "p_primario", "quota_anni_stesso_segno",
                                                  "netto_base_z", "netto_stress_z", "conc_ftmo_media", "conc_ftmo_n"]}, flush=True)
    out = pd.DataFrame(righe)
    assert len(out) == 108, len(out)
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("scritto", OUT, len(out))


if __name__ == "__main__":
    main()
