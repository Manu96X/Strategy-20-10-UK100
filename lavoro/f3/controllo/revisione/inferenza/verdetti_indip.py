# BH e verdetti §7 riscritti da capo, con tre letture della soglia GIALLO
import pickle, numpy as np, pandas as pd
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
X = pd.read_csv("stat_indip.csv", sep=";", decimal=",")
T = pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
V0 = pd.read_csv(RIS + "VERDETTI_scoperta.csv", sep=";", decimal=",").set_index("cella")
mio = pickle.load(open("placebo_indip_1000_4242.pkl", "rb"))
CEL = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "B1", "B2", "B3"]
mu = T[(T.scenario == "base") & (T.feed == "PEP")].groupby("cella").R.mean()
p_mio = {c: (1 + (mio[(c, "PEP")].mean(1) >= mu[c]).sum()) / 1001 for c in CEL}
def bh_qvalues(p):
    k = sorted(p, key=p.get); m = len(k); q = {}; run = 1.0
    for i in range(m, 0, -1):
        run = min(run, p[k[i - 1]] * m / i); q[k[i - 1]] = run
    return q
for nome, p in [("motore", V0.placebo_p.to_dict()), ("mio seme 4242", p_mio)]:
    q = bh_qvalues(p)
    print(nome, "| p minimo:", min(p, key=p.get), round(min(p.values()), 4), "| soglia BH rango 1 = 0,10/13 =", round(0.1 / 13, 5),
          "| celle con q_BH <= 0,10:", [c for c in CEL if q[c] <= 0.10], "| q_BH A2 =", round(q["A2"], 4))
b = X[(X.feed == "PEP") & (X.scenario == "base")].set_index("cella")
s = X[(X.feed == "PEP") & (X.scenario == "stress")].set_index("cella")
f = X[(X.feed == "FTMO") & (X.scenario == "base")].set_index("cella")
q = bh_qvalues(V0.placebo_p.to_dict())
rows = []
for c in CEL:
    ts = 2.5 if c == "A3" else 2.0
    C = dict(media_pos=b.media[c] > 0, t_ok=b.t_CR0[c] >= ts, placebo_bh=q[c] <= 0.10, stress_pos=s.media[c] > 0,
             n_ok=b.n[c] >= b.n_req[c], concordanza=f.media[c] > 0, anni_ok=b.anni_pos[c] >= 0.6, costo_ok=b.costo_R[c] <= 0.125)
    praw = V0.placebo_p[c] < 0.10; tband = 1.0 <= b.t_CR0[c] < ts
    resto = all(C[k] for k in ("media_pos", "stress_pos", "concordanza", "anni_ok", "costo_ok"))
    verde = all(C.values())
    # L1 (codice): due deroghe alternative, una sola alla volta; in deroga-t si rinuncia anche a n_ok
    L1 = verde or (resto and C["placebo_bh"] and tband) or (resto and C["t_ok"] and C["n_ok"] and praw and not C["placebo_bh"])
    # L2: deroghe cumulabili (t in banda e/o placebo solo grezzo), n_ok tolto quando t e' in banda
    L2 = verde or (resto and (C["t_ok"] and C["n_ok"] or tband) and (C["placebo_bh"] or praw))
    # L3: deroghe cumulabili ma n_ok sempre richiesto
    L3 = verde or (resto and C["n_ok"] and (C["t_ok"] or tband) and (C["placebo_bh"] or praw))
    v = lambda g: "VERDE" if verde else ("GIALLO" if g else "ROSSO")
    rows.append(dict(cella=c, t=round(b.t_CR0[c], 3), p=round(V0.placebo_p[c], 4), n=b.n[c], n_req=round(b.n_req[c], 1),
                     anni=round(b.anni_pos[c], 3), stress=round(s.media[c], 4), ftmo=round(f.media[c], 4),
                     L1_codice=v(L1), file=V0.verdetto[c], L2_cumul=v(L2), L3_cumul_nreq=v(L3),
                     cond_ko=",".join(k for k, x in C.items() if not x),
                     coincide_cond=all(bool(V0.loc[c, k]) == bool(C[k]) for k in C)))
pd.set_option("display.width", 250); print(pd.DataFrame(rows).to_string(index=False))
