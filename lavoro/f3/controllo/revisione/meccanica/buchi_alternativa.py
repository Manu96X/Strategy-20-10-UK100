"""Variante 'letterale' del protocollo §3: un buco di dati > SOGLIA minuti dentro la tenuta e' trattato come chiusura
(uscita forzata all'apertura del primo M1 >= ultima quotazione prima del buco - 15'; niente ingresso nelle 2 ore prima)."""
import pandas as pd, numpy as np, sys
SOGLIA = float(sys.argv[1]) if len(sys.argv) > 1 else 150
X = pd.read_pickle("confronto.pkl")
FILE = {("UK100","PEP"):"UK100 Pepperstone m1", ("UK100","FTMO"):"UK100 FTMO m1", ("GER40","PEP"):"GER40 Pepperstone m1",
        ("GER40","FTMO"):"GER40 FTMO m1", ("US500","PEP"):"US500 m1 - Pepperstone", ("US500","FTMO"):"US500 m1 - FTMO",
        ("US100","PEP"):"NAS100 m1 - FTPepperstone", ("US100","FTMO"):"US100 m1 - FTMO"}
SIMB = lambda c: {"B1":"GER40","B2":"US500","B3":"US100"}.get(c, "UK100")
SC = {"lordo": (0.0, 0.0), "base": (0.0, 0.5), "stress": (0.5, 2.0)}  # mkt, swap
NS = 60_000_000_000
cache = {}
X["R_alt"] = X.R; X["escluso"] = False
for idx, t in X[X.buco_max_min > SOGLIA].iterrows():
    key = (SIMB(t.cella), t.feed)
    if key not in cache:
        r = pd.read_csv("/home/user/dati_scoperta/" + FILE[key] + ".csv", sep="\t", dtype=str)
        ts = pd.to_datetime(r.iloc[:, 0] + " " + r.iloc[:, 1], format="%Y.%m.%d %H:%M:%S").values.astype("datetime64[ns]").astype("int64")
        cache[key] = (ts, r.iloc[:, 2].astype(float).values)
    ts, o = cache[key]
    i0 = np.searchsorted(ts, t.ts_in); j = np.searchsorted(ts, t.ts_out)
    dd = np.diff(ts[i0:j+1]); k = int(np.flatnonzero(dd > SOGLIA*NS)[0]); g0 = ts[i0+k]
    if t.ts_in >= g0 - 120*NS: X.loc[idx, "escluso"] = True; X.loc[idx, "R_alt"] = np.nan; continue
    ie = np.searchsorted(ts, g0 - 15*NS)
    mkt, swp = SC[t.scenario]
    px = o[ie] - mkt
    d0 = pd.Timestamp(int(t.ts_in)).normalize(); d1 = pd.Timestamp(int(ts[ie])).normalize(); nd = 0
    while d0 < d1:
        nd += 3 if d0.weekday() == 2 else 1; d0 += pd.Timedelta(days=1)
    R_alt = (px - t.fill - swp*nd) / t.d   # notti con triplo il mercoledi'
    X.loc[idx, "R_alt"] = R_alt
    print(f"{t.cella:4s} {t.feed:4s} {t.scenario:6s} in {pd.Timestamp(int(t.ts_in))}  buco da {pd.Timestamp(int(g0))}  uscita alt {pd.Timestamp(int(ts[ie]))} px {px:.2f}  R file {t.R:+.4f} -> alt {R_alt:+.4f}  notti {nd} wd_in {pd.Timestamp(int(t.ts_in)).weekday()}")
print("\nEffetto sulla media per cella (solo celle toccate):")
for (c, f, s), g in X.groupby(["cella", "feed", "scenario"]):
    if (g.R_alt != g.R).any() or g.escluso.any():
        print(f"  {c:4s} {f:4s} {s:6s} n {len(g)} -> {int((~g.escluso).sum())}  media {g.R.mean():+.5f} -> {g.R_alt.mean():+.5f}  diff {g.R_alt.mean()-g.R.mean():+.5f}")
