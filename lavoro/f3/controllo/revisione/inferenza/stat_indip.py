# Revisione indipendente: statistiche per cella da TRADE_scoperta.csv (non importa motore_f3)
import sys, numpy as np, pandas as pd
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
T = pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
S = pd.read_csv(RIS + "SINTESI_scoperta.csv", sep=";", decimal=",")
NY, PR = ZoneInfo("America/New_York"), ZoneInfo("Europe/Prague")
_cache = {}
def data_praga(ns):
    # ts_in = ora server naive (NY+7) in ns -> data a Praga, conversione scritta da capo con datetime
    if ns in _cache: return _cache[ns]
    srv = datetime(1970, 1, 1) + timedelta(microseconds=ns // 1000)
    ny = (srv - timedelta(hours=7)).replace(tzinfo=NY)          # fold=0 sulle ore ambigue
    d = ny.astimezone(PR).date(); _cache[ns] = d; return d
def stat(g, nboot=4000, seed=12345):
    R = g.R.to_numpy(float); n = len(R); mu = R.mean(); sd = R.std(ddof=1)
    day = np.array([data_praga(int(x)) for x in g.ts_in])
    df = pd.DataFrame({"R": R, "d": day})
    agg = df.groupby("d").R.agg(["sum", "count"])
    G = len(agg)
    # CR0: var(mu) = sum_g (sum_i (R_i - mu))^2 / n^2
    e = agg["sum"].to_numpy() - mu * agg["count"].to_numpy()
    se0 = np.sqrt((e ** 2).sum()) / n
    se1 = se0 * np.sqrt(G / (G - 1))                               # CR1 (correzione G/(G-1))
    rng = np.random.default_rng(seed); s, c = agg["sum"].to_numpy(), agg["count"].to_numpy()
    idx = rng.integers(0, G, (nboot, G)); bm = s[idx].sum(1) / c[idx].sum(1)
    pa = g.groupby("anno").R.mean()
    return dict(n=n, G=G, media=mu, sd=sd, t_CR0=mu / se0, t_CR1=mu / se1, t_iid=mu / (sd / np.sqrt(n)),
                n_req=(2 * sd / mu) ** 2 if mu > 0 else np.inf, anni_pos=(pa > 0).mean(), n_anni=len(pa),
                ic_lo=np.percentile(bm, 2.5), ic_hi=np.percentile(bm, 97.5), costo_R=g.costo_R.mean())
rows = []
for (c, f, sc), g in T.groupby(["cella", "feed", "scenario"], sort=False):
    r = stat(g); r.update(cella=c, feed=f, scenario=sc); rows.append(r)
X = pd.DataFrame(rows)
SS = S[["cella", "feed", "scenario", "n", "media", "t", "t_iid", "n_req", "anni_pos", "ic95_basso", "ic95_alto", "costo_R"]].copy()
SS.columns = ["cella", "feed", "scenario"] + [c + "_S" for c in SS.columns[3:]]
M = X.merge(SS, on=["cella", "feed", "scenario"])
for a, b in [("n", "n_S"), ("media", "media_S"), ("t_CR0", "t_S"), ("t_iid", "t_iid_S"), ("anni_pos", "anni_pos_S"), ("costo_R", "costo_R_S")]:
    print(f"max |{a} - {b}| = {np.nanmax(np.abs(M[a].astype(float) - M[b].astype(float))):.3e}")
fin = np.isfinite(M.n_req) & np.isfinite(M.n_req_S)
print("max |n_req rel diff| =", np.max(np.abs(M.n_req[fin] / M.n_req_S[fin] - 1)), " inf coincidenti:", ((~np.isfinite(M.n_req)) == (~np.isfinite(M.n_req_S))).all())
print("max |IC basso diff| =", np.max(np.abs(M.ic_lo - M.ic95_basso_S)), " max |IC alto diff| =", np.max(np.abs(M.ic_hi - M.ic95_alto_S)))
pd.set_option("display.width", 250)
P = M[(M.feed == "PEP") & (M.scenario == "base")]
print(P[["cella", "n", "G", "media", "sd", "t_CR0", "t_S", "t_CR1", "t_iid", "n_req", "anni_pos", "n_anni", "ic_lo", "ic_hi", "ic95_basso_S", "ic95_alto_S", "costo_R"]].round(4).to_string(index=False))
X.to_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/revisione/inferenza/stat_indip.csv", sep=";", decimal=",", index=False)
