import pandas as pd, numpy as np, sys
D="/home/user/dati_scoperta/"
for f in ["UK100 Pepperstone m1","UK100 FTMO m1","GER40 Pepperstone m1","US500 m1 - Pepperstone","NAS100 m1 - FTPepperstone"]:
    r = pd.read_csv(D+f+".csv", sep="\t", usecols=[0,1])
    ts = pd.to_datetime(r.iloc[:,0]+" "+r.iloc[:,1], format="%Y.%m.%d %H:%M:%S")
    ts = ts[ts>="2020-01-01"]
    g = ts.diff().dt.total_seconds()/60
    big = g[g>=60]
    prev = ts.shift(1)[big.index]
    df = pd.DataFrame({"prev":prev,"next":ts[big.index],"min":big})
    df["prev_hm"]=df.prev.dt.strftime("%H:%M"); df["next_hm"]=df.next.dt.strftime("%H:%M"); df["wd"]=df.prev.dt.weekday
    wk = df[(df.next-df.prev)<pd.Timedelta(hours=30)]
    print(f, "gap >=60min infrasettimanali (<30h):", len(wk))
    print(wk.groupby(["prev_hm","next_hm"]).size().sort_values(ascending=False).head(6).to_string())
    print("  di cui >=120 min:", (wk["min"]>=120).sum())
