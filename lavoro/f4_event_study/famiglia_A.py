# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA A: turn of the month e ribilanciamento di fine mese.
18 test esatti:
  A1 (10): per ogni strumento sul feed d'inferenza, finestra chiusura TD-2 -> chiusura TD+3 (4 rendimenti giornalieri).
           TD-1 = ultimo giorno di trading del mese nella tabella giornaliera; TD+k = k-esimo giorno di trading del mese dopo.
           p = placebo bilaterale (2000 estrazioni di finestre di 4 rendimenti negli stessi anni).
  A2 (8):  US500, US100, GER40, UK100 x {y1: TD-4 -> TD-1, y2: TD-1 -> TD+2}; y = a + b*s, s = rendimento del mese fino a
           TD-4 in z per radice dei giorni. media_z = media_anomala = b; t = t HC1 di b; p = permutazione di s (2000).
Solo dati di scoperta sigillati (< 01/01/2024) tramite eventi_comune.
"""
import sys, os
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f4_event_study")
import numpy as np
import pandas as pd
import eventi_comune as EC

OUT = "/home/user/Strategy-20-10-UK100/lavoro/f4_event_study/risultati/famiglia_A.csv"
NREP = 2000
FINE_DATI = pd.Timestamp("2023-12-29").date()   # ultima riga sigillata = vero ultimo giorno di trading di dicembre 2023


def tabella(s, f):
    d = EC.giornaliero(s, f).copy().reset_index(drop=True)
    # sigma d'ingresso: 20 rendimenti FINO al giorno incluso (la colonna sigma del modulo e' quella dei 20 PRECEDENTI)
    d["sig_in"] = d.r.rolling(20, min_periods=20).std()
    d["ora_C"] = pd.to_datetime(d.ts_C).dt.hour
    d["per"] = pd.to_datetime(d.data).dt.to_period("M")
    return d


def fine_mese(d):
    """Indici di riga dei TD-1: ultimo giorno del mese presente in tabella (la riga dopo e' del mese successivo).
    L'ultima riga conta solo se e' il 29/12/2023 (vero ultimo giorno di trading)."""
    per = d.per.values
    idx = [i for i in range(len(d) - 1) if per[i + 1] != per[i]]
    if d.data.iloc[-1] == FINE_DATI:
        idx.append(len(d) - 1)
    return np.array(idx, int)


def costo_netto(s, d, ie, iu, verso, scen):
    """netto in unita' z per trade dalla chiusura della riga ie alla chiusura della riga iu, verso +1/-1."""
    pe, pu = d.C.values[ie], d.C.values[iu]
    notti = np.array([(d.data.values[b] - d.data.values[a]).days for a, b in zip(ie, iu)])
    out = []
    for k in range(len(ie)):
        c = EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]], notti[k], scen)
        out.append((verso[k] * (pu[k] - pe[k]) - c) / (d.sig_in.values[ie[k]] * pe[k]))
    return float(np.mean(out)) if len(out) else np.nan


# ----------------------------------------------------------------------------------------------- A1
def eventi_A1(d):
    """Eventi validi: (riga TD-2, riga TD+3, anno del TD-1)."""
    per = d.per.values; n = len(d); ev = []
    for i in fine_mese(d):
        if i + 3 >= n or i - 1 < 0: continue
        if not (per[i + 1] == per[i] + 1 and per[i + 3] == per[i + 1]): continue   # TD+1..TD+3 nel mese dopo
        if per[i - 1] != per[i]: continue                                          # TD-2 nello stesso mese
        if not np.isfinite(d.sig_in.values[i - 1]): continue
        ev.append((i - 1, i + 3, int(d.anno.values[i])))
    return ev


def pool_finestre(d, L):
    j = np.arange(len(d) - L)
    z = np.log(d.C.values[j + L] / d.C.values[j]) / d.sig_in.values[j]
    ok = np.isfinite(z)
    return z[ok], d.anno.values[j][ok]


def analisi_A1(s, f, seed):
    d = tabella(s, f)
    ev = eventi_A1(d)
    if not ev: return None
    ie = np.array([e[0] for e in ev]); iu = np.array([e[1] for e in ev]); anni = np.array([e[2] for e in ev])
    W = np.log(d.C.values[iu] / d.C.values[ie]); z = W / d.sig_in.values[ie]
    zp, ap = pool_finestre(d, 4)
    bench = zp.mean()
    anom = z.mean() - bench
    p = EC.p_placebo(z.mean(), zp[np.isin(ap, np.unique(anni))], len(z), NREP, seed)
    t = EC.t_cluster(z, d.data.values[ie])
    t_an = EC.t_cluster(z - bench, d.data.values[ie])
    ya = pd.Series(z - bench).groupby(anni).agg(["mean", "size"])
    ya = ya[ya["size"] >= 2]
    quota = float((np.sign(ya["mean"]) == np.sign(anom)).mean()) if len(ya) else np.nan
    verso = np.full(len(ie), 1.0 if anom > 0 else -1.0)
    has_cost = EC.tabella_spread(s) is not None
    nb = costo_netto(s, d, ie, iu, verso, "base") if has_cost else np.nan
    ns = costo_netto(s, d, ie, iu, verso, "stress") if has_cost else np.nan
    return dict(n=len(z), media_z=z.mean(), media_anomala=anom, bps=W.mean() * 1e4, bench=bench, t=t, t_anomala=t_an,
                p=p, quota=quota, anni_validi=len(ya), eventi_anno=len(z) / len(np.unique(anni)), netto_base=nb,
                netto_stress=ns, per_anno=ya["mean"].round(3).to_dict(), date_ie=d.data.values[ie],
                primo=d.data.values[ie[0]], ultimo=d.data.values[iu[-1]], pool_n=len(zp))


# ----------------------------------------------------------------------------------------------- A2
def eventi_A2(d):
    """Per ogni mese m con TD-1 del mese precedente (p) e TD-1 del mese (e): righe p, e-3 (TD-4), e, e+2 (TD+2 o -1)."""
    fm = fine_mese(d); per = d.per.values; n = len(d); ev = []
    for a, e in zip(fm[:-1], fm[1:]):
        if per[e] != per[a] + 1: continue                 # mesi consecutivi
        q = e - 3                                         # TD-4
        if q <= a or per[q] != per[e]: continue           # TD-4 nel mese m e almeno un rendimento dopo TD-1 precedente
        ok2 = (e + 2 < n) and per[e + 1] == per[e] + 1 and per[e + 2] == per[e + 1]
        ev.append((a, q, e, e + 2 if ok2 else -1))
    return ev


def ols_hc1(x, y):
    X = np.column_stack([np.ones(len(x)), x]); n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X); beta = XtXi @ X.T @ y; u = y - X @ beta
    V = XtXi @ (X.T * u ** 2) @ X @ XtXi * n / (n - k)
    return beta, np.sqrt(np.diag(V))


def slope(x, y):
    xc = x - x.mean(); return (xc @ (y - y.mean())) / (xc @ xc)


def analisi_A2(s, f, quale, seed):
    d = tabella(s, f); C = d.C.values; sg = d.sig_in.values
    righe = []
    for a, q, e, e2 in eventi_A2(d):
        ss = np.log(C[q] / C[a]) / (sg[q] * np.sqrt(q - a))
        if quale == "y1": ie, iu = q, e
        else:
            if e2 < 0: continue
            ie, iu = e, e2
        y = np.log(C[iu] / C[ie]) / sg[ie]
        if np.isfinite(ss) and np.isfinite(y):
            righe.append((ss, y, ie, iu, int(d.anno.values[e]), np.log(C[iu] / C[ie])))
    if len(righe) < 5: return None
    x = np.array([r[0] for r in righe]); y = np.array([r[1] for r in righe])
    ie = np.array([r[2] for r in righe]); iu = np.array([r[3] for r in righe]); anni = np.array([r[4] for r in righe])
    W = np.array([r[5] for r in righe])
    beta, se = ols_hc1(x, y); b = beta[1]
    rng = np.random.default_rng(seed)
    bp = np.array([slope(rng.permutation(x), y) for _ in range(NREP)])
    p = float((1 + (np.abs(bp) >= abs(b)).sum()) / (1 + NREP))
    pa = {}
    for yy in np.unique(anni):
        m = anni == yy
        if m.sum() >= 6 and np.std(x[m]) > 0: pa[int(yy)] = float(slope(x[m], y[m]))
    quota = float(np.mean([np.sign(v) == np.sign(b) for v in pa.values()])) if pa else np.nan
    verso = np.sign(b * x); verso[verso == 0] = 1.0
    nb = costo_netto(s, d, ie, iu, verso, "base"); ns = costo_netto(s, d, ie, iu, verso, "stress")
    return dict(n=len(y), media_z=b, media_anomala=b, a=beta[0], bps=float(np.mean(verso * W) * 1e4), t=b / se[1],
                p=p, quota=quota, anni_validi=len(pa), eventi_anno=len(y) / len(np.unique(anni)), netto_base=nb,
                netto_stress=ns, per_anno={k: round(v, 3) for k, v in pa.items()}, corr=np.corrcoef(x, y)[0, 1],
                lordo_z=float(np.mean(verso * y)), primo=d.data.values[ie[0]], ultimo=d.data.values[iu[-1]])


# ----------------------------------------------------------------------------------------------- main
def main():
    righe = []; seed = 1000
    for s in EC.STRUMENTI:
        f = EC.FEED_INFERENZA[s]; seed += 1
        r = analisi_A1(s, f, seed)
        c = analisi_A1(s, "FTMO", seed + 500) if (f != "FTMO" and "FTMO" in EC.STRUMENTI[s]["feed"]) else None
        righe.append(dict(test_id=f"A1_{s}", strumento=s, feed=f, n=r["n"], media_z=r["media_z"],
                          media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"], t_anomala=r["t_anomala"],
                          p_primario=r["p"], quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"],
                          eventi_anno=r["eventi_anno"], netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                          conc_ftmo_media=(c["media_anomala"] if c else np.nan), conc_ftmo_n=(c["n"] if c else np.nan),
                          benchmark_z=r["bench"], periodo=f"{r['primo']}..{r['ultimo']}",
                          note=f"TD-2 close -> TD+3 close; bench={r['bench']:.4f}; pool={r['pool_n']}; anomala per anno={r['per_anno']}"))
        print(righe[-1]["test_id"], {k: righe[-1][k] for k in ["n", "media_z", "media_anomala", "t", "p_primario",
              "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z", "conc_ftmo_media", "conc_ftmo_n"]})
    for s in ["US500", "US100", "GER40", "UK100"]:
        f = EC.FEED_INFERENZA[s]
        for quale in ["y1", "y2"]:
            seed += 1
            r = analisi_A2(s, f, quale, seed)
            c = analisi_A2(s, "FTMO", quale, seed + 500)
            fin = "TD-4 -> TD-1 (attesa b<0)" if quale == "y1" else "TD-1 -> TD+2 (attesa b>0)"
            righe.append(dict(test_id=f"A2_{s}_{quale}", strumento=s, feed=f, n=r["n"], media_z=r["media_z"],
                              media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"], t_anomala=np.nan,
                              p_primario=r["p"], quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"],
                              eventi_anno=r["eventi_anno"], netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                              conc_ftmo_media=c["media_anomala"], conc_ftmo_n=c["n"], benchmark_z=np.nan,
                              periodo=f"{r['primo']}..{r['ultimo']}",
                              note=f"{fin}; b=pendenza (media_z=media_anomala=b); a={r['a']:.4f}; corr={r['corr']:.3f}; "
                                   f"lordo_z segno(b*s)={r['lordo_z']:.4f}; bps = media lorda del trade segno(b*s); b per anno={r['per_anno']}"))
            print(righe[-1]["test_id"], {k: righe[-1][k] for k in ["n", "media_z", "t", "p_primario",
                  "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z", "conc_ftmo_media", "conc_ftmo_n"]})
    out = pd.DataFrame(righe)
    assert len(out) == 18
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("scritto", OUT, len(out))


if __name__ == "__main__":
    main()
