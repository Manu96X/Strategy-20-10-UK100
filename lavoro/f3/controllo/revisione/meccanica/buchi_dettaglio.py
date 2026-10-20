import pandas as pd, numpy as np
X = pd.read_pickle("confronto.pkl")
FILE = {("UK100","PEP"):"UK100 Pepperstone m1", ("UK100","FTMO"):"UK100 FTMO m1", ("GER40","PEP"):"GER40 Pepperstone m1",
        ("GER40","FTMO"):"GER40 FTMO m1", ("US500","PEP"):"US500 m1 - Pepperstone", ("US100","PEP"):"NAS100 m1 - FTPepperstone"}
SIMB = lambda c: {"B1":"GER40","B2":"US500","B3":"US100"}.get(c, "UK100")
cache = {}
b = X[(X.buco_max_min > 150)].copy()
rows = []
for idx, t in b.iterrows():
    key = (SIMB(t.cella), t.feed)
    if key not in cache:
        r = pd.read_csv("/home/user/dati_scoperta/" + FILE[key] + ".csv", sep="\t", usecols=[0, 1])
        cache[key] = pd.to_datetime(r.iloc[:, 0] + " " + r.iloc[:, 1], format="%Y.%m.%d %H:%M:%S").values.astype("datetime64[ns]").astype("int64")
    ts = cache[key]; i0 = np.searchsorted(ts, t.ts_in); j = np.searchsorted(ts, t.ts_out)
    seg = ts[i0:j+1]; k = np.argmax(np.diff(seg))
    rows.append(dict(cella=t.cella, feed=t.feed, scen=t.scenario, ingresso=pd.Timestamp(t.ts_in), uscita=pd.Timestamp(t.ts_out), tipo=t.tipo,
                     buco_da=pd.Timestamp(seg[k]), buco_a=pd.Timestamp(seg[k+1]), minuti=(seg[k+1]-seg[k])/6e10, R=round(t.R, 4)))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).to_string())
