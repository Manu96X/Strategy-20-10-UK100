# -*- coding: utf-8 -*-
"""F0-bis: fuso orario e spread per ora degli strumenti NON indice (oro, argento, petrolio, VIX, dollaro).
Test decisivo del fuso: nelle settimane disallineate (USA in ora legale, Europa no) i dati USA delle 08:30 NY
cadono alle 15:30 server con NY+7 e alle 14:30 con l'ipotesi EU; la chiusura del giorno (17:00 NY) a 00:00 server.
Uso: python3 -I fuso_spread_altri.py <cartella_csv_completi> <cartella_out>"""
import sys, os
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
NY, LON = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")
FILES = {"XAU-USD FTMO m1": "2021-01-04", "XAU-USD Pepperstone m1": "2017-06-12", "XAG-USD FTMO m1": "2021-01-04",
         "XAG-USD Pepperstone m1": "2017-06-12", "BRENT m1 - Pepperstone": "2018-04-02", "USOIL m1 - FTMO": "2021-04-05",
         "VIX Pepperstone m1": "2020-03-04", "USDX pepperstone m1": "2019-04-22", "DXY FTMO m1": "2024-11-27"}
def disall(d):
    t = pd.Timestamp(d) + pd.Timedelta(hours=12)
    return (t.tz_localize("UTC").tz_convert(LON).utcoffset() - t.tz_localize("UTC").tz_convert(NY).utcoffset()) == pd.Timedelta(hours=4)
src, dst = sys.argv[1], sys.argv[2]; righe, spr = [], []
for f, ini in FILES.items():
    raw = pd.read_csv(os.path.join(src, f + ".csv"), sep="\t", dtype=str); raw.columns = [c.strip("<>").lower() for c in raw.columns]
    dig = int(raw.close.head(20000).str.split(".").str[1].str.len().fillna(0).max())
    df = pd.DataFrame({"ts": pd.to_datetime(raw.date + " " + raw.time, format="%Y.%m.%d %H:%M:%S"), "c": raw.close.astype(float),
                       "sp": raw.spread.astype(float) * 10.0 ** -dig})
    df = df[df.ts >= ini].reset_index(drop=True)
    ok = df.ts.diff().dt.total_seconds() == 60
    df["r"] = np.where(ok, np.abs(np.log(df.c / df.c.shift())), np.nan)
    df["d"] = df.ts.dt.normalize(); df["mod"] = df.ts.dt.hour * 60 + df.ts.dt.minute
    cl = {d: disall(d) for d in df.d.unique()}; df["dis"] = df.d.map(cl)
    for dis, g in df.groupby("dis"):
        prof = g.groupby("mod").r.mean(); med = prof.median()
        righe.append({"file": f, "settimane": "disallineate" if dis else "normali", "giorni": g.d.nunique(),
                      **{f"r_{h}_xmed": round(float(prof.get(int(h[:2]) * 60 + int(h[3:]), np.nan) / med), 2) for h in ["14:30", "15:30", "16:30", "17:30"]}})
    y = df.ts.dt.year.max()
    s = df[(df.ts.dt.year == y) & ~df.dis].groupby(df.ts.dt.hour).sp.median()
    spr.append({"file": f, "anno": y, **{f"h{h:02d}": round(v, 3) for h, v in s.items()}})
    print(f, "ok", flush=True)
R = pd.DataFrame(righe); S = pd.DataFrame(spr)
R.to_csv(os.path.join(dst, "FUSO_altri_strumenti.csv"), sep=";", decimal=",", index=False)
S.to_csv(os.path.join(dst, "SPREAD_altri_strumenti_ultimo_anno.csv"), sep=";", decimal=",", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(R.to_string(index=False)); print(S.to_string(index=False))
