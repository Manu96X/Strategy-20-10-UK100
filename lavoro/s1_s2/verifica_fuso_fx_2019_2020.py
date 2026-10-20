# -*- coding: utf-8 -*-
"""Fuso del forex FTMO nelle settimane di disallineamento 2019-2020 (dati di scoperta sigillati): correlazione fra i
rendimenti al minuto di EURUSD (FTMO) e dell'USDX (Pepperstone, sempre NY+7) con lo sfasamento di -60, 0, +60 minuti.
L'USDX viene spostato di sh minuti: massimo |corr| a 0 = FTMO gia' NY+7; a -60 = FTMO segue l'ora di Atene
(NY+6 in quelle settimane). La correlazione e' negativa perche' EURUSD e USDX vanno in verso opposto."""
import numpy as np, pandas as pd
D = "/home/user/dati_h1/scoperta/"
def m1(nome, da, a):
    r = pd.read_csv(D + nome, sep="\t", usecols=[0, 1, 5], dtype=str); r.columns = ["d", "t", "c"]
    r = r[(r.d >= da) & (r.d <= a)]
    s = pd.Series(r.c.astype(float).values, index=pd.to_datetime(r.d + " " + r.t, format="%Y.%m.%d %H:%M:%S"))
    return np.log(s).diff()
SETT = {"2019-03-11..22 (attesa Atene)": ("2019.03.11", "2019.03.22"), "2019-10-28..11-01": ("2019.10.28", "2019.11.01"),
        "2020-03-09..27": ("2020.03.09", "2020.03.27"), "2020-10-26..30": ("2020.10.26", "2020.10.30"),
        "2021-03-15..26 (attesa NY+7)": ("2021.03.15", "2021.03.26")}
for nome, (da, a) in SETT.items():
    e = m1("EURUSD m1 FTMO.csv", da, a); u = m1("USDX pepperstone m1.csv", da, a)
    out = {}
    for sh in (-60, 0, 60):
        uu = u.copy(); uu.index = uu.index + pd.Timedelta(minutes=sh)   # USDX in ora "FTMO ipotetica"
        j = pd.concat([e, uu], axis=1, join="inner").dropna()
        out[sh] = round(float(j.corr().iloc[0, 1]), 3)
    print(nome, "corr per sfasamento (min):", out, "->", {0: "NY+7", -60: "Atene (NY+6)", 60: "NY+8 (?)"}[max(out, key=lambda k: abs(out[k]))])
