# -*- coding: utf-8 -*-
"""Fuso dei feed Pepperstone settimana per settimana (dati sigillati < 2024): per ogni settimana, media di |rendimento a
1 minuto| della barra che inizia all'apertura cassa (09:30 NY per gli indici USA, 08:00 Londra per UK100) e, per l'oro, alle
08:30 NY (dati USA), sotto le ipotesi di ora server NY+6, NY+7, NY+8. L'ipotesi giusta ha il picco.
Uso: python3 -I fuso_settimanale_pepperstone.py <file> <tz> <hh:mm> <da> <a>"""
import sys
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
f, tz, hm, da, a = sys.argv[1:6]
r = pd.read_csv(f, sep="\t", usecols=[0, 1, 5], dtype=str); r.columns = ["d", "t", "c"]
r = r[(r.d >= da.replace("-", ".")) & (r.d <= a.replace("-", "."))]
s = pd.Series(r.c.astype(float).values, index=pd.to_datetime(r.d + " " + r.t, format="%Y.%m.%d %H:%M:%S"))
ret = np.log(s).diff().abs()
ret = ret[(s.index.to_series().diff() == pd.Timedelta(minutes=1)).values]
h, m = map(int, hm.split(":"))
giorni = pd.date_range(da, a, freq="B")
loc = (giorni + pd.Timedelta(hours=h, minutes=m)).tz_localize(ZoneInfo(tz)).tz_convert(ZoneInfo("America/New_York")).tz_localize(None)
righe = []
for off in (6, 7, 8):
    v = ret.reindex(loc + pd.Timedelta(hours=off))
    righe.append(pd.Series(v.values, index=giorni, name=f"NY+{off}"))
D = pd.concat(righe, axis=1)
W = D.groupby(D.index.to_period("W")).mean() * 1e4
W["migliore"] = W.idxmax(axis=1)
pd.set_option("display.max_rows", 200)
print(W.round(2).to_string())
