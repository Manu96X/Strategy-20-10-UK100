# Rilievi 6-12: letture della soglia GIALLO, P2 per A2/A3, bootstrap IC di A2, CR0/CR1, anni parziali
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
T = trade_file(); S = pd.read_csv(RIS + "SINTESI_scoperta.csv", sep=";", decimal=",")
B = S[(S.feed == "PEP") & (S.scenario == "base")].set_index("cella"); ST = S[(S.feed == "PEP") & (S.scenario == "stress")].set_index("cella")
F = S[(S.feed == "FTMO") & (S.scenario == "base")].set_index("cella")
rej = E.bh(B.placebo_p.to_dict(), 0.10)
print("== Rilievi 6/7/11: verdetti con tre letture; soglia BH rango 1 = 0.10/13 =", 0.10 / 13, "; p minimo:", B.placebo_p.min(), B.placebo_p.idxmin())
for c in E.CELLE:
    b = B.loc[c]; ts = 2.5 if c == "A3" else 2.0
    base = dict(media_pos=b.media > 0, stress_pos=ST.loc[c].media > 0, concordanza=F.loc[c].media > 0, anni_ok=b.anni_pos >= 0.6, costo_ok=b.costo_R <= 0.125)
    t_ok, n_ok, pbh, praw = b.t >= ts, b.n >= b.n_req, bool(rej[c]), b.placebo_p < 0.10
    verde = all(base.values()) and t_ok and n_ok and pbh
    L1 = verde or (all(base.values()) and pbh and 1.0 <= b.t < ts) or (all(base.values()) and t_ok and n_ok and praw)
    L2 = verde or (all(base.values()) and (t_ok and n_ok or 1.0 <= b.t < ts) and (pbh or praw))
    L3 = verde or (all(base.values()) and n_ok and (t_ok or 1.0 <= b.t < ts) and (pbh or praw))
    L2lett = verde or (all(base.values()) and (t_ok and n_ok or 1.0 <= b.t < 2.0) and (pbh or praw))   # banda letterale anche per A3
    f = lambda v: "VERDE" if verde else ("GIALLO" if v else "ROSSO")
    ko = [k for k, v in {**base, "t_ok": t_ok, "n_ok": n_ok, "placebo_bh": pbh}.items() if not v]
    print(f"{c:4s} t={b.t:6.3f} p={b.placebo_p:.4f} n={int(b.n)} n_req={b.n_req:7.1f} anni={b.anni_pos:.3f} stress={ST.loc[c].media:+.4f} ftmo={F.loc[c].media:+.4f} | L1(codice)={f(L1)} L2={f(L2)} L3={f(L3)} L2_banda_lett={f(L2lett)} | ko={ko}")
V = pd.read_csv(RIS + "VERDETTI_scoperta.csv", sep=";", decimal=","); print("verdetti nel file:", dict(zip(V.cella, V.verdetto)))

print("\n== Rilievo 10: t CR0 (codice) vs CR1 vs iid, e Rilievo 12: anni con/senza 2017")
for c in ["A1", "A2", "A3", "B2", "B3"]:
    g = T[(T.cella == c) & (T.feed == "PEP") & (T.scenario == "base")]
    s = M.statistiche(g, nboot=10); G = len(np.unique(M.giorno_ftmo(g.ts_in)))
    pa = g.groupby("anno").R.agg(["count", "mean"])
    pa2 = pa.drop(2017, errors="ignore")
    print(f"{c}: n={len(g)} G={G} t_CR0={s['t']:.4f} t_CR1={s['t']*np.sqrt((G-1)/G):.4f} t_iid={s['t_iid']:.4f} | anni_pos={s['anni_pos']:.3f} senza2017={(pa2['mean']>0).mean():.3f} n2017={int(pa['count'].get(2017,0))} media2017={pa['mean'].get(2017,np.nan):+.3f}")

print("\n== Rilievo 9: IC95 bootstrap di A2 PEP base per seme (5000 repliche) e con 400.000 repliche")
g = T[(T.cella == "A2") & (T.feed == "PEP") & (T.scenario == "base")]
for sd in range(1, 6):
    s = M.statistiche(g, nboot=5000, seed=sd); print(f"  seme {sd}: IC95 = ({s['ic95'][0]:+.4f}, {s['ic95'][1]:+.4f})")
gid = pd.factorize(M.giorno_ftmo(g.ts_in))[0]; R = g.R.to_numpy()
som = pd.Series(R).groupby(gid).sum().to_numpy(); cnt = pd.Series(1, index=range(len(R))).groupby(gid).sum().to_numpy()
rng = np.random.default_rng(99); bm = np.concatenate([(som[k].sum(1) / cnt[k].sum(1)) for k in (rng.integers(0, len(som), (50000, len(som))) for _ in range(8))])
print(f"  400k repliche (seme 99): IC95 = ({np.percentile(bm,2.5):+.4f}, {np.percentile(bm,97.5):+.4f}); quota <= 0: {(bm<=0).mean():.4f}")
