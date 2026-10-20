# Ricostruisce la tabella spread per ora server dai trade (scenario base, spread x1), senza leggere il file F0 (dati 2026)
import pandas as pd, numpy as np, pickle
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
T = pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
st = pickle.load(open(RIS + "stato_scoperta.pkl", "rb"))
P2 = pd.concat([d.assign(cella=k[0]) for k, d in st["P2"].items()])
X = pd.concat([T[T.scenario == "base"], P2])
X["simb"] = X.cella.map(lambda c: {"B1": "GER40", "B2": "US500", "B3": "US100"}.get(c, "UK100"))
X["ora"] = (X.ts_in.astype(np.int64) // 3600_000_000_000) % 24
out = {}
for s, g in X.groupby("simb"):
    u = g.groupby("ora").spread.agg(["min", "max", "count"])
    assert (u["max"] - u["min"]).abs().max() < 1e-12, s
    v = np.full(24, np.nan); v[u.index.values] = u["min"].values; out[s] = v
    print(s, "ore coperte:", list(u.index), "\n  ", np.round(v, 4))
pickle.dump(out, open("spread_tab.pkl", "wb"))
