import pandas as pd, numpy as np
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
X = pd.read_pickle("confronto.pkl")
X["tin"] = pd.to_datetime(X.ts_in); X["tout"] = pd.to_datetime(X.ts_out)
X["wd_in"] = X.tin.dt.weekday
cols = ["cella","feed","scenario","tin","tout","tipo","fill","sl","tp","px_out","d","spread","slip","notti","swap","R","costo_R"]
print("gap SL (base/stress):"); print(X[X.gap_open & (X.scenario!="lordo")][cols+["R_protocollo"]].sort_values("R").head(8).to_string())
print("\nnotti=3 A5 PEP base:"); print(X[(X.cella=="A5")&(X.feed=="PEP")&(X.scenario=="base")&(X.notti==3)][cols].head(4).to_string())
print("\nCHIUSURA venerdi A5 PEP base:"); print(X[(X.cella=="A5")&(X.feed=="PEP")&(X.scenario=="base")&(X.tipo=="CHIUSURA")][cols].head(3).to_string())
print("\nTP A1 PEP base:"); print(X[(X.cella=="A1")&(X.feed=="PEP")&(X.scenario=="base")&(X.tipo=="TP")][cols].to_string())
print("\nA2 PEP base TEMPO:"); print(X[(X.cella=="A2")&(X.feed=="PEP")&(X.scenario=="base")&(X.tipo=="TEMPO")][cols].head(3).to_string())
print("\nA9 PEP stress:"); print(X[(X.cella=="A9")&(X.feed=="PEP")&(X.scenario=="stress")][cols].head(3).to_string())
print("\nB:"); print(X[X.cella.isin(["B1","B2","B3"])&(X.scenario=="base")].groupby(["cella","feed"]).head(1)[cols].to_string())
