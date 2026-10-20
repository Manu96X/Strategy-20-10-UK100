# -*- coding: utf-8 -*-
"""
F0 - Verifica del fuso orario del server, anno per anno, e profilo dello spread per ora.
Ipotesi H_NY7: server = New York + 7 (segue l'ora legale USA).
Ipotesi H_EU : server = UTC+2/+3 con l'ora legale EUROPEA (EET/EEST).
Le due ipotesi differiscono SOLO nelle settimane "disallineate" (USA in ora legale,
Europa no: marzo e fine ottobre/inizio novembre):
  - apertura Londra/Xetra (08:00 UK, 09:00 CET): H_NY7 -> 11:00 server, H_EU -> 10:00
  - apertura cassa USA (09:30 NY):               H_NY7 -> 16:30 server, H_EU -> 15:30
  - dati USA delle 08:30 NY (NFP, CPI):          H_NY7 -> 15:30 server, H_EU -> 14:30
Misura: media del rendimento assoluto a 1 minuto per minuto del giorno; il picco
all'apertura identifica il fuso. Solo periodi M1 veri (da audit).
Uso: python3 -I fuso_e_spread.py <cartella_csv> <cartella_output>
"""
import sys, os
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

FILES = {  # file: (inizio M1 vero, tipo)
    "UK100 FTMO m1": ("2021-09-14", "EU"), "UK100 Pepperstone m1": ("2017-06-03", "EU"),
    "GER40 FTMO m1": ("2021-12-28", "EU"), "GER40 Pepperstone m1": ("2020-06-11", "EU"),
    "US500 m1 - FTMO": ("2021-09-14", "US"), "US500 m1 - Pepperstone": ("2020-07-13", "US"),
    "US100 m1 - FTMO": ("2021-09-14", "US"), "NAS100 m1 - FTPepperstone": ("2017-06-09", "US"),
}
NY, LON = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")

def classe_giorno(d):
    t = pd.Timestamp(d) + pd.Timedelta(hours=12)
    ny = t.tz_localize("UTC").tz_convert(NY).utcoffset().total_seconds() / 3600
    lo = t.tz_localize("UTC").tz_convert(LON).utcoffset().total_seconds() / 3600
    return "disallineata" if (lo - ny) == 4 else "normale"

def carica(path, inizio):
    raw = pd.read_csv(path, sep="\t", dtype=str)
    raw.columns = [c.strip("<>").lower() for c in raw.columns]
    dig = int(raw["close"].head(20000).str.split(".").str[1].str.len().fillna(0).max())
    df = pd.DataFrame({"ts": pd.to_datetime(raw["date"] + " " + raw["time"], format="%Y.%m.%d %H:%M:%S"),
                       "c": raw["close"].astype(float), "sp": raw["spread"].astype(float) * 10.0 ** (-dig)})
    return df[df.ts >= inizio].reset_index(drop=True)

def finestra_picco(prof, h0, h1):
    w = prof[(prof.index >= h0 * 60) & (prof.index < h1 * 60)]
    m = int(w.idxmax()); return f"{m // 60:02d}:{m % 60:02d}", float(w.max())

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    righe, spread_rows = [], []
    for nome, (inizio, tipo) in FILES.items():
        df = carica(os.path.join(src, nome + ".csv"), inizio)
        df["d"] = df.ts.dt.normalize()
        df["y"] = df.ts.dt.year
        df["mod"] = df.ts.dt.hour * 60 + df.ts.dt.minute
        prev_ok = (df.ts.diff().dt.total_seconds() == 60)
        df["r"] = np.where(prev_ok, np.abs(np.log(df.c / df.c.shift())), np.nan)
        classi = {d: classe_giorno(d) for d in df.d.unique()}
        df["cl"] = df.d.map(classi)
        df["ven"] = df.ts.dt.weekday == 4
        df["primo_ven"] = df.ven & (df.ts.dt.day <= 7)
        for y, g in df.groupby("y"):
            for cl, gc in g.groupby("cl"):
                prof = gc.groupby("mod").r.mean()
                base = prof.median()
                rec = {"file": nome, "anno": y, "settimane": cl, "giorni": gc.d.nunique()}
                if tipo == "EU":
                    rec["picco_09_12"], v = finestra_picco(prof, 9, 12)
                rec["picco_15_18"], v2 = finestra_picco(prof, 15, 18)
                for hhmm in ["10:00", "11:00", "14:30", "15:30", "16:30"]:
                    m = int(hhmm[:2]) * 60 + int(hhmm[3:])
                    rec["r_" + hhmm + "_xmed"] = round(float(prof.get(m, np.nan) / base), 2)
                pv = gc[gc.primo_ven].groupby("mod").r.mean()
                if len(pv):
                    rec["nfp_picco_13_17"], _ = finestra_picco(pv, 13, 17)
                righe.append(rec)
            # spread per ora server (mediana del minimo del minuto), giorni normali
            sp = g[g.cl == "normale"].groupby(g.ts.dt.hour).sp.median()
            spread_rows.append({"file": nome, "anno": y, **{f"h{h:02d}": round(v, 2) for h, v in sp.items()}})
        print(nome, "ok", flush=True)
    pd.DataFrame(righe).to_csv(os.path.join(dst, "FUSO_verifica_per_anno.csv"), index=False, sep=";", decimal=",")
    pd.DataFrame(spread_rows).to_csv(os.path.join(dst, "SPREAD_mediana_per_ora_server.csv"), index=False, sep=";", decimal=",")
