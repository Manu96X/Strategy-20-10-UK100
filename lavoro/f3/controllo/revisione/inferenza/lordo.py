import numpy as np, pandas as pd
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
m = T.groupby(["cella", "feed", "scenario"]).R.agg(["mean", "count"]).unstack("scenario")
m["ord_ok"] = (m[("mean", "lordo")] >= m[("mean", "base")]) & (m[("mean", "base")] >= m[("mean", "stress")])
pd.set_option("display.width", 200); print(m.round(4).to_string())
print("celle×feed con ordine violato:", (~m.ord_ok).sum())
# per trade: stesso (cella, feed, i0) nei tre scenari
P = T.pivot_table(index=["cella", "feed", "i0"], columns="scenario", values="R")
P3 = P.dropna()
print("trade presenti in tutti e 3 gli scenari:", len(P3), "su", len(P))
v1 = P3[P3.lordo < P3.base - 1e-12]; v2 = P3[P3.base < P3.stress - 1e-12]
print("trade con R_lordo < R_base:", len(v1), " con R_base < R_stress:", len(v2))
print(v1.head(10)); print(v2.head(10))
# costo implicito: base deve avere costo_R >= 0 e lordo costo 0
print(T.groupby("scenario").costo_R.agg(["min", "max", "mean"]))
