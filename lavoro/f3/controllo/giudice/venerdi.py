import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd
feed = pickle.load(open("cache_UK100_PEP.pkl", "rb"))["feed"]
g = pd.DataFrame({"g": pd.to_datetime(feed.giorni), "ult": pd.to_datetime(feed.ultima), "cd": feed.chiusura_dopo})
g["hm"] = g.ult.dt.strftime("%H:%M"); g["anno"] = g.g.dt.year
f = g[g.cd]
print(f.groupby("anno").hm.value_counts().unstack(fill_value=0).loc[:, lambda d: d.sum() > 2].to_string())
for d in ["2017-10-27", "2018-03-02", "2018-11-23", "2019-11-29", "2021-11-26", "2022-02-21", "2023-06-19"]:
    r = g[g.g == d]; print(d, pd.Timestamp(d).day_name(), r.hm.values, r.cd.values)
