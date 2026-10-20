import pandas as pd, numpy as np
r = pd.read_csv("/home/user/dati_scoperta/UK100 Pepperstone m1.csv", sep="\t", usecols=[0, 1])
ts = pd.to_datetime(r.iloc[:, 0] + " " + r.iloc[:, 1], format="%Y.%m.%d %H:%M:%S")
ts = ts[ts >= "2017-06-06"].reset_index(drop=True)
g = ts.diff().dt.total_seconds() / 60
df = pd.DataFrame({"prev": ts.shift(1), "min": g})
df = df[(df["min"] >= 60) & (df["min"] < 30 * 60)]   # pause infrasettimanali
df["anno"] = df.prev.dt.year
print(df.groupby("anno")["min"].agg(n="size", n_ge120=lambda x: (x >= 120).sum(), n_gt150=lambda x: (x > 150).sum(), mediana="median"))
X = pd.read_pickle("confronto.pkl")
print("\ntrade con differenza |R_protocollo - R| > 0.001 per scenario (SL in gap):")
print((X.assign(dd=(X.R_protocollo - X.R).abs() > 0.001)).groupby("scenario").dd.sum())
