# M1 mancanti: ritardo dell'uscita a tempo rispetto alla scadenza; buchi > 15 min dentro i trade
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd, motore_f3 as M
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
T = T[(T.scenario == "base") & (T.cella != "A8")]
sim_of = lambda c: "UK100" if c.startswith("A") else {"B1": "GER40", "B2": "US500", "B3": "US100"}[c]
H = 3600e9
for (sim, fk) in [("UK100","PEP"),("UK100","FTMO"),("GER40","PEP"),("US500","PEP"),("US100","PEP")]:
    d = pickle.load(open(f"cache_{sim}_{fk}.pkl","rb")); feed = d["feed"]
    t = T[(T.feed == fk) & (T.cella.map(sim_of) == sim)].copy()
    tin = pd.to_datetime(t.ts_in).values.astype(np.int64); tout = pd.to_datetime(t.ts_out).values.astype(np.int64)
    # 24h TEMPO: ritardo
    m = t.cella.isin(["A1","A4","A5","A6","A9","A10","B1","B2","B3"]).values & (t.tipo == "TEMPO").values
    rit = (tout[m] - (tin[m] + 24*H)) / 6e10
    print(sim, fk, "uscite 24h TEMPO:", m.sum(), " ritardo (min) max:", rit.max() if len(rit) else None, " >5 min:", int((rit > 5).sum()), " <0:", int((rit < 0).sum()))
    # buchi > 15 min (stesso giorno server) dentro la vita del trade
    gaps = np.diff(feed.ts); ig = np.flatnonzero((gaps > 15*6e10) & (feed.data_srv[1:] == feed.data_srv[:-1]))
    gt = feed.ts[ig]
    n_aff = 0; es = []
    for a, b_, c in zip(tin, tout, t.cella.values):
        k = np.searchsorted(gt, a); 
        if k < len(gt) and gt[k] < b_: n_aff += 1; es.append((c, pd.Timestamp(a), pd.Timestamp(gt[k]), (feed.ts[ig[k]+1]-gt[k])/6e10))
    print("   buchi intragiornalieri >15 min nel feed:", len(ig), " trade che ne attraversano uno:", n_aff, es[:6])
