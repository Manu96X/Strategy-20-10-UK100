# -*- coding: utf-8 -*-
"""Confronta trade per trade la replica cieca (controllo/replica/REPLICA_<cella>.csv) con il motore
(risultati/TRADE_scoperta.csv, feed PEP, scenario base). Uso: python3 -I confronta_replica.py <cartella_f3>"""
import os, sys
import numpy as np, pandas as pd
f3 = sys.argv[1]
T = pd.read_csv(os.path.join(f3, "risultati", "TRADE_scoperta.csv"), sep=";", decimal=",")
T = T[(T.feed == "PEP") & (T.scenario == "base")]
out = []
for cella in ["A1", "A2", "A5"]:
    p = os.path.join(f3, "controllo", "replica", f"REPLICA_{cella}.csv")
    if not os.path.exists(p): print("manca", p); continue
    Rp = pd.read_csv(p, sep=";")
    for c in ("fill", "sl", "tp", "px_out", "R"):
        if Rp[c].dtype == object: Rp[c] = Rp[c].str.replace(",", ".").astype(float)
    Rp["key"] = pd.to_datetime(Rp.ts_in).dt.strftime("%Y-%m-%d %H:%M")
    Mo = T[T.cella == cella].copy()
    Mo["key"] = pd.to_datetime(Mo.ts_in.astype(np.int64)).dt.strftime("%Y-%m-%d %H:%M")
    Mo["out_key"] = pd.to_datetime(Mo.ts_out.astype(np.int64)).dt.strftime("%Y-%m-%d %H:%M")
    m = Mo.merge(Rp, on="key", how="outer", suffixes=("_mot", "_rep"), indicator=True)
    both = m[m._merge == "both"]
    dR = (both.R_mot - both.R_rep).abs()
    dpx = (both.px_out_mot - both.px_out_rep).abs()
    out.append(dict(cella=cella, n_motore=len(Mo), n_replica=len(Rp), in_comune=len(both),
                    solo_motore=int((m._merge == "left_only").sum()), solo_replica=int((m._merge == "right_only").sum()),
                    tipo_diverso=int((both.tipo_mot != both.tipo_rep).sum()),
                    uscita_diversa=int((both.out_key != pd.to_datetime(both.ts_out_rep).dt.strftime("%Y-%m-%d %H:%M")).sum()),
                    max_diff_R=float(dR.max()) if len(both) else np.nan, n_diff_R_oltre_0001=int((dR > 1e-3).sum()),
                    media_R_motore=Mo.R.mean(), media_R_replica=Rp.R.mean()))
    diff = m[(m._merge != "both")]
    if len(diff): print(cella, "trade non in comune:\n", diff[["key", "_merge"]].head(20).to_string(index=False))
    bad = both[dR > 1e-3]
    if len(bad): print(cella, "differenze di R:\n", bad[["key", "tipo_mot", "tipo_rep", "R_mot", "R_rep", "px_out_mot", "px_out_rep"]].head(20).to_string(index=False))
res = pd.DataFrame(out)
print(res.to_string(index=False))
res.to_csv(os.path.join(f3, "controllo", "CONFRONTO_REPLICA.csv"), sep=";", decimal=",", index=False)
