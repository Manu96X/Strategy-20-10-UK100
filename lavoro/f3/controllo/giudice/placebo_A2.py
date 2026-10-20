# Riproduce il placebo P1 di A1 e A2 (stesso flusso rng di esegui_f3) e lo ricalcola per la variante "buchi 150'"
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
import varianti as V
C = pickle.load(open("cache_UK100_PEP.pkl", "rb")); feed, tab, bs, bc = C["feed"], C["tab"], C["bs"], C["bc"]
def pval(df, D):
    mp = np.nanmean(D, axis=1); s = M.statistiche(df)
    return s, (1 + (mp >= s["media"]).sum()) / (1 + len(mp)), mp.mean()
for nome, fn in [("CODICE", None), ("BUCHI150", V.fabbrica_esiti(buchi=True))]:
    if fn is not None: V.prepara_buchi(feed, 150)
    out, cache = esegui(feed, bs, bc, tab, ["A1", "A2"], "base", "PEP", esiti_fn=fn)
    rng = np.random.default_rng(20261020)           # stesso seme e stesso ordine (A1 poi A2) di esegui_f3
    D1 = E.placebo(out["A1"], bs, cache[("sess", 2.5, "24h")], "R1", rng)
    D2 = E.placebo(out["A2"], bs, cache[("sess", 2.5, "24barre")], "R1", rng)
    for c, D in [("A1", D1), ("A2", D2)]:
        s, p, pm = pval(out[c], D)
        print(f"{nome:8s} {c} n={s['n']} media={s['media']:+.5f} t={s['t']:.4f} t_iid={s['t_iid']:.4f} n_req={s['n_req']:.1f} anni_pos={s['anni_pos']:.3f} costo={s['costo_R']:.4f} IC95=({s['ic95'][0]:+.4f},{s['ic95'][1]:+.4f}) placebo_media={pm:+.5f} p(1000,flusso orig)={p:.6f}")
    # p con 20.000 repliche e seme indipendente (errore MC piccolo)
    rng2 = np.random.default_rng(777)
    D2b = E.placebo.__globals__["np"] and None
    E.NREP_old = E.NREP; E.NREP = 20000
    D2b = E.placebo(out["A2"], bs, cache[("sess", 2.5, "24barre")], "R1", rng2); E.NREP = E.NREP_old
    s, p, pm = pval(out["A2"], D2b)
    print(f"{nome:8s} A2 p(20000 repliche, seme 777)={p:.5f}  placebo_media={pm:+.5f}")
    pickle.dump(out["A2"], open(f"A2_{nome}.pkl", "wb"))
