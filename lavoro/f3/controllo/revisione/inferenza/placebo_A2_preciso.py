# p del placebo P1 per le celle R1 UK100 PEP con 200.000 repliche (a blocchi) + approssimazione analitica
import os, sys, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import motore_f3 as M
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
B = T[T.scenario == "base"]
x = B[B.cella.str.startswith("A")]; h = pd.to_datetime(x.ts_in).dt.hour
tab = np.full(24, np.nan)
for hh, sp in x.groupby(h).spread.first().items(): tab[hh] = sp
cfg = M.SIMBOLI["UK100"]; fl = M.festivi_borsa("ENG", range(2016, 2027))
feed = M.Feed("/home/user/dati_scoperta/UK100 Pepperstone m1.csv", "2017-06-06", fl)
bs = M.indicatori(M.barre_sessione(feed, cfg["tz"], cfg["apre"], cfg["chiude"], fl))
anno, kk, dow = bs.anno.to_numpy(), bs.k.to_numpy(), bs.dow.to_numpy()
NREP, BLK = 200_000, 20_000
for c, usc in [("A1", "24h"), ("A2", "24barre"), ("A3", "sera")]:
    Rb = np.array([np.nan if e is None else e["R"] for e in M.esiti_tutte_le_barre(feed, bs, 2.5, usc, tab, M.SCENARI["base"])])
    tr = B[(B.cella == c) & (B.feed == "PEP")]; mu = tr.R.mean(); n = len(tr)
    pools = [Rb[(anno == a) & (kk == k) & (dow == 0) & np.isfinite(Rb)] for a, k in zip(tr.anno, tr.k)]
    Em = np.mean([p.mean() for p in pools]); Vm = np.sum([p.var(ddof=0) for p in pools]) / n ** 2
    rng = np.random.default_rng(777); cnt = 0
    for _ in range(NREP // BLK):
        s = np.zeros(BLK)
        for p in pools: s += p[rng.integers(0, len(p), BLK)]
        cnt += (s / n >= mu).sum()
    p = (1 + cnt) / (1 + NREP)
    print(f"{c}: n={n} media={mu:.4f} E[placebo]={Em:+.4f} sd={np.sqrt(Vm):.4f} p_MC(200k)={p:.5f} "
          f"IC95 p=[{p-1.96*np.sqrt(p*(1-p)/NREP):.5f},{p+1.96*np.sqrt(p*(1-p)/NREP):.5f}] p_normale={stats.norm.sf((mu-Em)/np.sqrt(Vm)):.5f} "
          f"dim. pool min/mediana={min(map(len,pools))}/{int(np.median(list(map(len,pools))))}")
