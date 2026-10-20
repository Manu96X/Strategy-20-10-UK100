import numpy as np, pandas as pd
C="cache/"
def ser(s):
    z=np.load(C+s+".npz"); return pd.Series(z["c"],index=pd.DatetimeIndex(z["t"]))
e=ser("EURUSD"); u=ser("USDX")
for a,b in [("2018-03-12","2018-03-23"),("2018-06-04","2018-06-15"),("2019-10-28","2019-11-01"),("2020-03-09","2020-03-20"),("2021-03-15","2021-03-26")]:
    ee=np.log(e[a:b]).diff(); uu=np.log(u[a:b]).diff()
    out=[]
    for h in (-1,0,1):
        x=ee.copy(); x.index=x.index+pd.Timedelta(hours=h)
        j=pd.concat([x,uu],axis=1).dropna(); out.append((h,round(j.corr().iloc[0,1],3)))
    print(a,b,"corr(EURUSD shift h, USDX):",out)
G=pd.read_csv("giornaliero_replica.csv",sep=";")
print(G[G.y2.isna()][["dt","dt1"]].to_string())
print("S==0:",(G.S==0).sum(), "rows",len(G), G.dt.min(), G.dt1.max())
