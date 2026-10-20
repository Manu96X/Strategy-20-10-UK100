# Per ogni trade del CSV: barra segnale chiusa prima dell'ingresso? ingresso = primo M1 >= fine nominale? indicatori causali?
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3"); sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/comune")
import pickle, numpy as np, pandas as pd, motore_f3 as M, barre
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
T = T[~T.cella.isin(["A8"])]
sim_of = {"A": "UK100", "B1": "GER40", "B2": "US500", "B3": "US100"}
for (sim, fk) in [("UK100","PEP"),("UK100","FTMO"),("GER40","PEP"),("US500","PEP"),("US100","PEP")]:
    d = pickle.load(open(f"cache_{sim}_{fk}.pkl","rb")); feed = d["feed"]
    t = T[(T.feed == fk) & (T.cella.map(lambda c: sim_of.get(c, sim_of["A"] if c.startswith("A") else None)) == sim)]
    for tipo, b in [("sess", d["bs"]), ("cfd", d["bc"])]:
        if b is None: continue
        tt = t[t.cella.isin(["A9","A10"])] if tipo == "cfd" else t[~t.cella.isin(["A9","A10"])]
        if len(tt) == 0: continue
        fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64)[tt.s.values]
        tin = pd.to_datetime(tt.ts_in).values.astype(np.int64)
        i0 = np.searchsorted(feed.ts, fine, "left")
        ok1 = (tin >= fine).all(); ok2 = (feed.ts[i0] == tin).all(); ok3 = (tt.i0.values == i0).all()
        rit = (tin - fine) / 6e10
        # ultimo M1 della barra segnale < fine
        print(sim, fk, tipo, "trade:", len(tt), "| ts_in>=fine:", ok1, "| ts_in = primo M1>=fine:", ok2, "| i0 coerente:", ok3,
              "| ritardo min (min/mediana/max):", rit.min(), np.median(rit), rit.max(), "| ritardo>0:", int((rit > 0).sum()))
        # causalita' degli indicatori: ricalcolo su serie TRONCATA alla barra s
        rng = np.random.default_rng(0); ss = rng.choice(np.unique(tt.s.values), min(60, tt.s.nunique()), replace=False)
        mx = 0.0
        for s in ss:
            bb = b.iloc[:s+1]
            r = barre.rsi_wilder(bb.c.to_numpy(), 14)[-1]; a = barre.atr_wilder(bb.h.to_numpy(), bb.l.to_numpy(), bb.c.to_numpy(), 14)[-1]
            m = barre.sma(bb.c.to_numpy(), 40)[-1]
            mx = max(mx, abs(r - b.rsi.iat[s]), abs(a - b.atr.iat[s]), abs(m - b.sma.iat[s]))
        print("   indicatori su serie troncata vs completa, max |diff| su", len(ss), "barre segnale:", mx)
        # valori di rsi/atr registrati nel CSV = quelli della barra s
        print("   rsi CSV = rsi barra s:", np.allclose(tt.rsi.values, b.rsi.values[tt.s.values]), "| atr:", np.allclose(tt.atr.values, b.atr.values[tt.s.values]),
              "| d = m*atr (2.5 R1 / 2.0 R2):", np.allclose(tt.d.values, np.where(tt.cella.isin(["A1","A2","A3","A9","B1","B2","B3"]), 2.5, 2.0) * tt.atr.values))
        print("   barre segnale valide (>=300):", bool((tt.s.values >= 300).all()), "| min s:", int(tt.s.min()))
