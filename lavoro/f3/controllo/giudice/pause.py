# Distribuzione dei buchi intra-settimana (esclusi quelli che coprono un weekend) per anno, UK100 PEP
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd
feed = pickle.load(open("cache_UK100_PEP.pkl", "rb"))["feed"]
ts = pd.to_datetime(feed.ts); d = np.diff(feed.ts) / 6e10
a = pd.DataFrame({"da": ts[:-1], "a": ts[1:], "min": d})
a = a[(a["min"] >= 100) & ((a.a - a.da) < pd.Timedelta(hours=40))]
a["anno"] = a.da.dt.year
print(a.assign(c120=a["min"] >= 120, c150=a["min"] > 150, c180=a["min"] > 180).groupby("anno")[["c120", "c150", "c180"]].sum())
print(a[a["min"] > 150].to_string())
