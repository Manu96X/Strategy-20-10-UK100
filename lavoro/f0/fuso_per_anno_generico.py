# -*- coding: utf-8 -*-
"""Verifica del fuso NY+7 anno per anno per QUALSIASI file M1 (forex, indici, materie prime).
Test: nelle settimane disallineate (USA in ora legale, Europa no) i dati USA delle 08:30 NY cadono alle 15:30 server
con NY+7 e alle 14:30 con server EET a ora legale europea. Anche nelle settimane normali deve esserci il picco alle 15:30.
Uso: python3 -I fuso_per_anno_generico.py <cartella_csv> <out_csv>"""
import sys, os, glob
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
NY, LON = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")
def disall(d):
    t = pd.Timestamp(d) + pd.Timedelta(hours=12)
    return (t.tz_localize("UTC").tz_convert(LON).utcoffset() - t.tz_localize("UTC").tz_convert(NY).utcoffset()) == pd.Timedelta(hours=4)
righe = []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.csv"))):
    nome = os.path.basename(p)[:-4]
    raw = pd.read_csv(p, sep="\t", dtype=str, usecols=[0, 1, 5]); raw.columns = ["d", "t", "c"]
    df = pd.DataFrame({"ts": pd.to_datetime(raw.d + " " + raw.t, format="%Y.%m.%d %H:%M:%S"), "c": raw.c.astype(float)})
    ok = df.ts.diff().dt.total_seconds() == 60
    df["r"] = np.where(ok, np.abs(np.log(df.c / df.c.shift())), np.nan)
    df["dd"] = df.ts.dt.normalize(); df["mod"] = df.ts.dt.hour * 60 + df.ts.dt.minute; df["y"] = df.ts.dt.year
    cl = {d: disall(d) for d in df.dd.unique()}; df["dis"] = df.dd.map(cl)
    # solo i venerdì che sono primi venerdì del mese (NFP) e tutti i giorni: due misure
    for (y, dis), g in df.groupby(["y", "dis"]):
        if g.dd.nunique() < 3: continue
        prof = g.groupby("mod").r.mean(); med = prof.median()
        if not np.isfinite(med) or med == 0: continue
        righe.append(dict(file=nome, anno=y, settimane="disallineate" if dis else "normali", giorni=g.dd.nunique(),
                          r1430=round(float(prof.get(870, np.nan) / med), 2), r1530=round(float(prof.get(930, np.nan) / med), 2),
                          r1630=round(float(prof.get(990, np.nan) / med), 2), verdetto=("NY+7" if prof.get(930, 0) / med >= 1.8 and prof.get(930, 0) > 1.3 * prof.get(870, 0) else
                                                                                            ("EU (14:30)" if prof.get(870, 0) / med >= 1.8 and prof.get(870, 0) > 1.3 * prof.get(930, 0) else "incerto"))))
    print(nome, "ok", flush=True)
R = pd.DataFrame(righe); R.to_csv(sys.argv[2], sep=";", decimal=",", index=False)
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 400)
print(R[R.settimane == "disallineate"].to_string(index=False))
print(R[(R.settimane == "normali") & (R.verdetto != "NY+7")].to_string(index=False))
