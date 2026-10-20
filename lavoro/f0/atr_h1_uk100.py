# -*- coding: utf-8 -*-
"""ATR 14 di Wilder sulle barre H1 di UK100 (sessione cash di Londra e CFD ora server), mediana per anno.
Serve solo a stimare la distanza dello stop (costo in R). Uso: python3 -I atr_h1_uk100.py <cartella_csv> <cartella_risultati>"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comune"))
import barre
src, dst = sys.argv[1], sys.argv[2]
rows = []
for f, ini in [("UK100 FTMO m1", "2021-09-14"), ("UK100 Pepperstone m1", "2017-06-03")]:
    m1 = barre.carica_m1(os.path.join(src, f + ".csv"), ini)
    for tipo, b in [("cash", barre.h1_cash(m1)), ("cfd", barre.h1_cfd(m1))]:
        b["atr"] = barre.atr_wilder(b.h, b.l, b.c, 14)
        key = b.ora_locale if tipo == "cash" else b.ora_server
        b["y"] = key.dt.year
        for y, g in b.groupby("y"):
            rows.append({"file": f, "barre": tipo, "anno": y, "barre_H1": len(g),
                         "barre_giorno": round(len(g) / g[key.name].dt.normalize().nunique(), 1),
                         "ATR14_med": round(np.nanmedian(g.atr), 1), "stop2ATR_med": round(2 * np.nanmedian(g.atr), 1),
                         "stop2.5ATR_med": round(2.5 * np.nanmedian(g.atr), 1)})
pd.DataFrame(rows).to_csv(os.path.join(dst, "ATR_H1_per_anno_UK100.csv"), sep=";", decimal=",", index=False)
