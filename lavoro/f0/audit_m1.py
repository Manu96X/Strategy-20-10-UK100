# -*- coding: utf-8 -*-
"""
F0 - Audit degli storici M1 (export MT5, TAB) anno per anno.
Scritto da zero: audit_storici_m1.py originale NON presente nella repository.
Sola lettura sui CSV. Uso:
    python3 -I audit_m1.py <cartella_csv> <cartella_output>
Per ogni file e anno: barre, giorni, barre/giorno, quota di barre al minuto :00
(1/60 = M1 vero, 1,0 = H1/D1 travestito), spaziatura a 1 minuto, tipo di giornata dal passo modale (M1/M5/H1/D1), OHLC incoerenti,
duplicati, barre piatte, spread (zero, costante, mediana, p95, in punti indice),
barre anomale (range o tickvol fuori scala), primo/ultimo minuto modali, giorni
feriali mancanti, inizio dell'M1 continuo.
"""
import sys, os, glob
import numpy as np
import pandas as pd

def decimali(serie_str):
    s = serie_str.head(20000)
    d = s.str.split(".").str[1].str.len().fillna(0)
    return int(d.max())

def carica(path):
    raw = pd.read_csv(path, sep="\t", dtype=str)
    raw.columns = [c.strip("<>").lower() for c in raw.columns]
    dig = decimali(raw["close"])
    df = pd.DataFrame({
        "ts": pd.to_datetime(raw["date"] + " " + raw["time"], format="%Y.%m.%d %H:%M:%S"),
        "o": raw["open"].astype(float), "h": raw["high"].astype(float),
        "l": raw["low"].astype(float), "c": raw["close"].astype(float),
        "tv": raw["tickvol"].astype(np.int64), "sp": raw["spread"].astype(np.int64),
    })
    return df, dig

def tipo_giorno(g):
    n = len(g); f00 = (g.ts.dt.minute == 0).mean()
    if n == 1: return "D1"
    if f00 >= 0.9: return "H1"
    if f00 < 0.2 and n >= 30: return "M1"
    return "misto"

def audit_file(path):
    nome = os.path.basename(path).replace(".csv", "")
    df, dig = carica(path)
    pt = 10.0 ** (-dig)
    df["y"] = df.ts.dt.year
    df["d"] = df.ts.dt.normalize()
    mono = int((df.ts.diff().dt.total_seconds() <= 0).sum())
    dup = int(df.ts.duplicated().sum())
    # tipo di ogni giornata
    gd = df.groupby("d")
    n_day = gd.size()
    # passo modale fra barre consecutive dello stesso giorno: 60 s = M1, 300 s = M5, 3600 s = H1
    passo = df.ts.diff().dt.total_seconds().where(df.d.eq(df.d.shift()))
    q60_day = (passo == 60).groupby(df.d).sum() / (n_day - 1).clip(lower=1)
    q300_day = (passo == 300).groupby(df.d).sum() / (n_day - 1).clip(lower=1)
    q3600_day = (passo == 3600).groupby(df.d).sum() / (n_day - 1).clip(lower=1)
    tipo = pd.Series(np.where(n_day == 1, "D1", np.where(q3600_day >= 0.5, "H1",
                    np.where(q300_day >= 0.5, "M5", np.where((q60_day >= 0.5) & (n_day >= 30), "M1", "misto")))),
                    index=n_day.index)
    non_m1 = tipo[tipo != "M1"]
    inizio_m1 = (non_m1.index.max() + pd.Timedelta(days=1)) if len(non_m1) else n_day.index.min()
    # se dopo l'ultimo giorno non-M1 non c'è nulla, l'M1 non esiste
    righe = []
    for y, g in df.groupby("y"):
        gg = g.copy()
        dt = gg.ts.diff().dt.total_seconds()
        stesso = gg.d.eq(gg.d.shift())
        rng = (gg.h - gg.l)
        med_rng = rng[rng > 0].median() if (rng > 0).any() else np.nan
        tv_med = gg.tv.median()
        ndg = gg.groupby("d").size()
        wd = pd.bdate_range(gg.d.min(), gg.d.max())
        mancanti = len(set(wd) - set(ndg.index))
        sp = gg.sp
        mode_sp = sp.mode().iloc[0] if len(sp) else np.nan
        prima = gg.groupby("d").ts.min().dt.strftime("%H:%M").mode()
        ultima = gg.groupby("d").ts.max().dt.strftime("%H:%M").mode()
        lun = gg[gg.ts.dt.weekday == 0].groupby("d").ts.min().dt.strftime("%H:%M").mode()
        ven = gg[gg.ts.dt.weekday == 4].groupby("d").ts.max().dt.strftime("%H:%M").mode()
        tipi = tipo[tipo.index.year == y].value_counts().to_dict()
        righe.append({
            "file": nome, "anno": y, "barre": len(gg), "giorni": gg.d.nunique(),
            "giorni_M1": tipi.get("M1", 0), "giorni_M5": tipi.get("M5", 0), "giorni_H1": tipi.get("H1", 0),
            "giorni_D1": tipi.get("D1", 0), "giorni_misti": tipi.get("misto", 0),
            "barre_giorno_med": float(ndg.median()), "barre_giorno_p10": float(ndg.quantile(0.10)),
            "quota_min00": round((gg.ts.dt.minute == 0).mean(), 4),
            "quota_passo_60s": round((dt[stesso] == 60).mean(), 4) if stesso.any() else np.nan,
            "feriali_mancanti": mancanti,
            "ohlc_incoerenti": int(((gg.h < gg[["o", "c"]].max(axis=1)) | (gg.l > gg[["o", "c"]].min(axis=1)) | (gg.h < gg.l)).sum()),
            "barre_piatte_pct": round(100 * (rng == 0).mean(), 2),
            "range_med_pt": round(med_rng, 3) if med_rng == med_rng else np.nan,
            "barre_range_x20": int((rng > 20 * med_rng).sum()) if med_rng == med_rng else 0,
            "barre_tickvol_x50": int((gg.tv > 50 * max(tv_med, 1)).sum()),
            "spread_zero_pct": round(100 * (sp == 0).mean(), 2),
            "spread_moda_pct": round(100 * (sp == mode_sp).mean(), 2),
            "spread_med_pt": round(sp.median() * pt, 3), "spread_p95_pt": round(sp.quantile(0.95) * pt, 3),
            "prima_barra_moda": prima.iloc[0] if len(prima) else "", "ultima_barra_moda": ultima.iloc[0] if len(ultima) else "",
            "lunedi_prima_moda": lun.iloc[0] if len(lun) else "", "venerdi_ultima_moda": ven.iloc[0] if len(ven) else "",
        })
    out = pd.DataFrame(righe)
    info = {"file": nome, "cifre_decimali": dig, "punto": pt, "prima_data": str(df.ts.min()),
            "ultima_data": str(df.ts.max()), "righe": len(df), "timestamp_non_crescenti": mono,
            "duplicati": dup, "inizio_M1_continuo": str(inizio_m1.date()),
            "giorni_non_M1_dopo_2021_09_14": int(((tipo != "M1") & (tipo.index >= "2021-09-14")).sum())}
    return out, info

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    tutti, infos = [], []
    for p in sorted(glob.glob(os.path.join(src, "*.csv"))):
        o, i = audit_file(p)
        tutti.append(o); infos.append(i)
        print(i, flush=True)
    pd.concat(tutti).to_csv(os.path.join(dst, "AUDIT_M1_per_anno.csv"), index=False, sep=";", decimal=",")
    pd.DataFrame(infos).to_csv(os.path.join(dst, "AUDIT_M1_riassunto.csv"), index=False, sep=";", decimal=",")
