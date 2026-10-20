# -*- coding: utf-8 -*-
"""Tabella dei costi CONGELATA per S3 (PROTOCOLLO_S3.md §3): spread p75 in bps al minuto locale esatto +-2 dell'ingresso
(apertura + 5') e dell'uscita a fine sessione (chiusura - 5'), dai file FTMO 10/10/2025 -> 09/10/2026 (solo colonna SPREAD;
il close serve solo come denominatore). US100: massimo con lo spread reale M1BA 2025-26. US30: regola di S1/S2.
Uscita: risultati/COSTI_S3.csv (strumento; contesto; base_bps; stress_bps; n)."""
import io, os, subprocess
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo

REPO = "/home/user/Strategy-20-10-UK100"
QUI = os.path.join(REPO, "lavoro", "s3_orb")
NY = ZoneInfo("America/New_York")
FILE = {"US100": "/home/user/dati_m1/US100 m1 - FTMO.csv", "US500": "/home/user/dati_m1/US500 m1 - FTMO.csv",
        "GER40": "/home/user/dati_m1/GER40 FTMO m1.csv", "UK100": "/home/user/dati_m1/UK100 FTMO m1.csv",
        "US2000": "/home/user/dati_m1_nuovi/US2000 m1 FTMO.csv", "FRA40": "/home/user/dati_m1_nuovi/FRA40 m1 FTMO.csv",
        "JP225": "/home/user/dati_m1_nuovi/JP225 m1 FTMO.csv"}
MINUTI = {"US100": ("America/New_York", "09:35", "15:55"), "US500": ("America/New_York", "09:35", "15:55"),
          "US2000": ("America/New_York", "09:35", "15:55"), "GER40": ("Europe/Berlin", "09:05", "17:25"),
          "UK100": ("Europe/London", "08:05", "16:25"), "FRA40": ("Europe/Paris", "09:05", "17:25"),
          "JP225": ("Asia/Tokyo", "09:05", "14:55")}
DA, A = "2025.10.10", "2026.10.09"

def leggi(path):
    txt = subprocess.run(["awk", "-F\t", f'NR > 1 && $1 >= "{DA}" && $1 <= "{A}" {{print $1"\\t"$2"\\t"$6"\\t"$9}}', path],
                         capture_output=True, text=True, check=True).stdout
    d = pd.read_csv(io.StringIO(txt), sep="\t", names=["d", "t", "c", "sp"], dtype=str)
    dig = int(d.c.head(5000).str.split(".").str[1].str.len().max())
    ts = pd.to_datetime(d.d + " " + d.t, format="%Y.%m.%d %H:%M:%S")
    s = pd.Series((d.sp.astype(float) * 10.0 ** (-dig) / d.c.astype(float) * 1e4).values, index=ts - pd.Timedelta(hours=7))
    return s[~s.index.duplicated()]

def contesto(s, tz, hm, giorni):
    h, m = map(int, hm.split(":"))
    ny = (giorni + pd.Timedelta(hours=h, minutes=m)).tz_localize(ZoneInfo(tz)).tz_convert(NY).tz_localize(None)
    k = np.concatenate([(ny + pd.Timedelta(minutes=j)).values for j in (-2, -1, 0, 1, 2)])
    v = s.reindex(k).dropna()
    return v.quantile(.75), len(v)

giorni = pd.date_range("2025-10-10", "2026-10-09", freq="B")
righe = []
for st, f in FILE.items():
    s = leggi(f); tz, ing, usc = MINUTI[st]
    for nome, hm in (("ingresso", ing), ("uscita_fine_sessione", usc)):
        v, n = contesto(s, tz, hm, giorni)
        righe.append(dict(strumento=st, contesto=nome, p75_ftmo_bps=v, n=n))
    print(st, "ok", flush=True)
# US100: massimo con M1BA 2025-26 (spread all'apertura del minuto)
fs = sorted(x for x in os.listdir(REPO) if x.startswith("M1BA_US100.cash_") and ("2025.0" in x or "2026.0" in x))
b = pd.concat([pd.read_csv(os.path.join(REPO, x), sep=";") for x in fs])
mb = pd.Series(((b.ask_o - b.bid_o) / b.bid_o * 1e4).values, index=pd.to_datetime(b.minuto_server, format="%Y.%m.%d %H:%M") - pd.Timedelta(hours=7))
mb = mb[~mb.index.duplicated()]
gmb = pd.DatetimeIndex(sorted(set(mb.index.normalize())))
T = pd.DataFrame(righe)
T["p75_m1ba_bps"] = np.nan
for nome, hm in (("ingresso", "09:35"), ("uscita_fine_sessione", "15:55")):
    v, n = contesto(mb, "America/New_York", hm, gmb)
    T.loc[(T.strumento == "US100") & (T.contesto == nome), "p75_m1ba_bps"] = v
T["base_bps"] = np.where(T.p75_m1ba_bps.notna(), np.maximum(T.p75_ftmo_bps, T.p75_m1ba_bps), T.p75_ftmo_bps)
spec_us30, congelata_us100 = 2.63 / 51691.16 * 1e4, 1.53 / 30903.34 * 1e4
for nome in ("ingresso", "uscita_fine_sessione"):
    u100 = T[(T.strumento == "US100") & (T.contesto == nome)].base_bps.iloc[0]
    u500 = T[(T.strumento == "US500") & (T.contesto == nome)].base_bps.iloc[0]
    T = pd.concat([T, pd.DataFrame([dict(strumento="US30", contesto=nome, p75_ftmo_bps=np.nan, n=0, p75_m1ba_bps=np.nan,
                                         base_bps=max(spec_us30 * u100 / congelata_us100, u100, u500))])], ignore_index=True)
T["stress_bps"] = 1.5 * T.base_bps
os.makedirs(os.path.join(QUI, "risultati"), exist_ok=True)
T.to_csv(os.path.join(QUI, "risultati", "COSTI_S3.csv"), sep=";", decimal=",", index=False)
print(T.round(3).to_string(index=False))
