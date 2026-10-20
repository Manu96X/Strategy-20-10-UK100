# -*- coding: utf-8 -*-
"""Spread FTMO del forex per ora server, ultimi 12 mesi disponibili (10/10/2025 -> 09/10/2026): SOLO la colonna
SPREAD (dato di costo, non di rendimento: nessun prezzo letto). Campo SPREAD = minimo del minuto (F0).
Uscita: risultati/SPREAD_FX_FTMO_per_ora.csv (mediana e p75 in pip per ora server)."""
import subprocess, io, sys
import pandas as pd
SRC = "/home/user/dati_m1_nuovi"
PIP = {"EURUSD": 10, "GBPUSD": 10, "AUDUSD": 10, "USDCHF": 10, "USDCAD": 10, "USDJPY": 10}  # punti per pip
righe = []
for p in PIP:
    txt = subprocess.run(["awk", "-F\t", 'NR > 1 && $1 >= "2025.10.10" {print $1"\t"$2"\t"$9}', f"{SRC}/{p} m1 FTMO.csv"],
                         capture_output=True, text=True, check=True).stdout
    d = pd.read_csv(io.StringIO(txt), sep="\t", names=["data", "ora", "sp"])
    d["h"] = d.ora.str[:2].astype(int)
    g = d.groupby("h").sp
    t = pd.DataFrame({"mediana_pip": g.median() / PIP[p], "p75_pip": g.quantile(0.75) / PIP[p], "n": g.size()})
    t["coppia"] = p
    righe.append(t.reset_index())
    print(p, "righe", len(d), "prima", d.data.min(), "ultima", d.data.max())
T = pd.concat(righe)
T.to_csv(sys.argv[1], sep=";", decimal=",", index=False)
print(T.pivot(index="h", columns="coppia", values="mediana_pip").round(2).to_string())
