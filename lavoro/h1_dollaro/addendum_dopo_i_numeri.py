# -*- coding: utf-8 -*-
"""ADDENDUM «DOPO I NUMERI» (20/10/2026, dopo lo stadio A ROSSO): descrittivo, fuori dal verdetto.
Pendenza del paniere forex (W1) su S anno per anno 2017-2023 (solo dati di scoperta < 2024; il 2024 resta sigillato),
e correlazione giornaliera alle 16:00 NY fra segnale metalli e paniere del dollaro nello stesso giorno, per anno."""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h1_motore as M
B = M.tabella_giornaliera("scoperta", "2016-11-01", "2023-12-31")
B = B[B.S.notna() & B.y1.notna() & B.sigB.notna() & ~((B.dt.dt.year == 2020) & (B.fusi_diversi | B.fusi_diversi1))]
B["zB"] = B.rB / B.sigB
out = {}
for an, g in B.groupby(B.dt1.dt.year):
    b, t, _ = M.ols(g.S.to_numpy(), g.y1.to_numpy())
    out[int(an)] = dict(n=int(len(g)), b=round(b, 4), t=round(t, 2), corr_stesso_giorno=round(float(g[["S", "zB"]].dropna().corr().iloc[0, 1]), 3))
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(M.QUI, "risultati", "H1_addendum_per_anno.json"), "w"), indent=1)
