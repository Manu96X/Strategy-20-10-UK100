# (1) P2 anche per A2/A3 (non calcolato dal motore: solo celle 24h); (2) data di Praga vs "server - 1h"; (3) anni senza 2017
import sys, numpy as np, pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import motore_f3 as M
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
B = T[T.scenario == "base"]
NY, PR = ZoneInfo("America/New_York"), ZoneInfo("Europe/Prague")
def dp(ns):
    srv = datetime(1970, 1, 1) + timedelta(microseconds=int(ns) // 1000)
    return (srv - timedelta(hours=7)).replace(tzinfo=NY).astimezone(PR).date()
def dsrv1(ns): return (datetime(1970, 1, 1) + timedelta(microseconds=int(ns) // 1000) - timedelta(hours=1)).date()
P = B[B.feed == "PEP"]
diff = sum(dp(x) != dsrv1(x) for x in P.ts_in.unique())
print("trade PEP base: ingressi distinti", P.ts_in.nunique(), "con data Praga != data(server-1h):", diff)
def tcl(R, d):
    R = np.asarray(R, float); mu = R.mean(); e = pd.Series(R - mu).groupby(np.asarray(d)).sum().to_numpy()
    return mu, np.sqrt((e ** 2).sum()) / len(R)
x = B[B.cella.str.startswith("A")]; tab = np.full(24, np.nan)
for hh, sp in x.groupby(pd.to_datetime(x.ts_in).dt.hour).spread.first().items(): tab[hh] = sp
cfg = M.SIMBOLI["UK100"]; fl = M.festivi_borsa("ENG", range(2016, 2027))
for fk, (nome, ini) in cfg["feed"].items():
    feed = M.Feed(f"/home/user/dati_scoperta/{nome}.csv", ini, fl)
    bs = M.indicatori(M.barre_sessione(feed, cfg["tz"], cfg["apre"], cfg["chiude"], fl))
    for c, usc in [("A1", "24h"), ("A2", "24barre"), ("A3", "sera")]:
        e = M.esiti_tutte_le_barre(feed, bs, 2.5, usc, tab, M.SCENARI["base"])
        lun = M.segnali_R1(bs, e, (0,), 40.0, True); alt = M.segnali_R1(bs, e, (1, 2, 3, 4), 40.0, True)
        R1 = [t["R"] for t in lun]; R2 = [t["R"] for t in alt]
        m1, s1 = tcl(R1, [dp(t["ts_in"]) for t in lun]); m2, s2 = tcl(R2, [dp(t["ts_in"]) for t in alt])
        chk = np.isclose(m1, B[(B.cella == c) & (B.feed == fk)].R.mean())
        print(f"P2 {c} {fk}: lun n={len(R1)} media={m1:+.4f} (coincide con TRADE: {chk}) | mar-ven n={len(R2)} media={m2:+.4f} | diff={m1-m2:+.4f} t_diff={(m1-m2)/np.hypot(s1,s2):.3f}")
pa = P.groupby(["cella", "anno"]).R.mean().unstack()
for c in ["A1", "A2", "A3", "B2", "B3"]:
    r = pa.loc[c].dropna(); r2 = r.drop(2017, errors="ignore")
    print(c, "anni_pos con 2017:", round((r > 0).mean(), 3), " senza 2017 (parziale):", round((r2 > 0).mean(), 3), " n 2017:", int(((P.cella == c) & (P.anno == 2017)).sum()))
