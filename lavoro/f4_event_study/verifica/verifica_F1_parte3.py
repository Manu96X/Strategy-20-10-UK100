# -*- coding: utf-8 -*-
"""Parte 3: rifilatura simmetrica, Spearman con permutazione, strategia solo su segnali forti (|x|>soglia) netta dei costi."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verifica_F1 import *
def sig_incl(d):
    d = d.copy(); d["z"] = d.r / d.r.rolling(20, min_periods=20).std(); return d
for s, tg in [("XAG", "USDX"), ("UK100", "BRENT"), ("BRENT", "BRENT")]:
    A = allinea(sig_incl(serie_cash(s, "PEP")), serie_cash(tg, "PEP")); b = ols(A.x, A.y)[0]
    print("=" * 80, "\n", s, "->", tg)
    for c in (2.5, 3.0):
        m = (A.x.abs() <= c) & (A.y.abs() <= c); print(f"  scarta |x|>{c} o |y|>{c} (n tolti {(~m).sum()}): b,t,corr =", [round(v, 4) for v in ols(A.x[m], A.y[m])])
    rx = A.x.rank().values; ry = A.y.rank().values; rs = np.corrcoef(rx, ry)[0, 1]
    rng = np.random.default_rng(3); pp = np.array([np.corrcoef(rx[rng.permutation(len(rx))], ry)[0, 1] for _ in range(2000)])
    print("  Spearman", round(rs, 4), "p perm", round((1 + (np.abs(pp) >= abs(rs)).sum()) / 2001, 4))
    # segno del giorno dopo nel verso del segnale (hit rate)
    sg = np.sign(b * A.x) * np.sign(A.y); print("  hit rate segno:", round((sg > 0).mean(), 4), "n", len(A))
    notti = (pd.to_datetime(A.d_tgt) - pd.to_datetime(A.d_sig)).dt.days.values
    cz = np.array([EC.costo_trade(tg, P, 23, nn, "base") for P, nn in zip(A.C_prev.values, notti)])
    cz = np.log(1 + cz / A.C_prev.values) / A.sigma.values
    for th in (0, 1, 1.5, 2):
        m = A.x.abs() > th; g = np.sign(b * A.x[m]) * A.y[m]
        print(f"  |x|>{th}: n={m.sum()} ({m.sum()/len(A)*100:.0f}%), lordo z={g.mean():.4f}, costo z={np.nanmean(cz[m]):.4f}, netto z={g.mean()-np.nanmean(cz[m]):.4f}, t lordo={g.mean()/g.std()*np.sqrt(len(g)):.2f}, no2020 lordo={ (np.sign(b*A.x[m & (A.anno!=2020)])*A.y[m & (A.anno!=2020)]).mean():.4f}")
