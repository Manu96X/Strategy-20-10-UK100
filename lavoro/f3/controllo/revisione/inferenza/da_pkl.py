# Verifica p-value placebo dalle repliche salvate e P2 con codice proprio (cluster per data di Praga)
import pickle, numpy as np, pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
T = pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
st = pickle.load(open(RIS + "stato_scoperta.pkl", "rb"))
S = pd.read_csv(RIS + "SINTESI_scoperta.csv", sep=";", decimal=",")
B = T[T.scenario == "base"]
print("chiavi P1:", sorted(st["P1"].keys())[:4], "...", len(st["P1"]))
out = []
for (c, f), D in st["P1"].items():
    mu = B[(B.cella == c) & (B.feed == f)].R.mean()
    mp = np.nanmean(D, axis=1)
    p = (1 + (mp >= mu).sum()) / (1 + len(mp))
    s = S[(S.cella == c) & (S.feed == f) & (S.scenario == "base")].iloc[0]
    out.append(dict(cella=c, feed=f, shape=D.shape, n_nan=int(np.isnan(D).sum()), media=mu, placebo_media=mp.mean(),
                    placebo_sd=mp.std(ddof=1), p=p, p_S=s.placebo_p, z=(mu - mp.mean()) / mp.std(ddof=1)))
pd.set_option("display.width", 200); print(pd.DataFrame(out).round(4).to_string(index=False))
NY, PR = ZoneInfo("America/New_York"), ZoneInfo("Europe/Prague")
def dp(ns):
    srv = datetime(1970, 1, 1) + timedelta(microseconds=int(ns) // 1000)
    return (srv - timedelta(hours=7)).replace(tzinfo=NY).astimezone(PR).date()
def se_cl(R, days):
    R = np.asarray(R, float); mu = R.mean(); n = len(R)
    e = pd.Series(R - mu).groupby(np.asarray(days)).sum().to_numpy(); return mu, np.sqrt((e ** 2).sum()) / n
P2 = pd.read_csv(RIS + "P2_scoperta.csv", sep=";", decimal=",")
for (c, f), d2 in st["P2"].items():
    d1 = B[(B.cella == c) & (B.feed == f)]
    m1, s1 = se_cl(d1.R, [dp(x) for x in d1.ts_in]); m2, s2 = se_cl(d2.R, [dp(x) for x in d2.ts_in])
    # alternativa: t della differenza con un unico errore raggruppato (regressione R ~ lunedì, cluster per giorno)
    t = (m1 - m2) / np.hypot(s1, s2)
    r = P2[(P2.cella == c) & (P2.feed == f)].iloc[0]
    print(f"{c} {f}: n_lun={len(d1)} n_altri={len(d2)} diff={m1-m2:+.4f} t_diff={t:.4f} | file: diff={r['diff']:+.4f} t={r.t_diff:.4f}  dow presenti={sorted(d2.dow.unique())}")
