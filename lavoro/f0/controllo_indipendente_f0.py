# -*- coding: utf-8 -*-
"""
Controllo INDIPENDENTE dei numeri F0 (codice diverso da audit_m1.py / fuso_e_spread.py / barre.py):
 1) SHA256 dei CSV estratti contro SHA256.txt (hashlib)
 2) righe per anno e quota di barre al minuto :00 con il modulo csv (niente pandas)
 3) inizio dell'M1 continuo per UK100 con regola scritta da capo
 4) fuso: minuto di picco 09:00-12:00 nelle settimane disallineate, solo numpy
 5) RSI/ATR di Wilder: barre.py contro un'implementazione a ciclo esplicito e contro pandas ewm
 6) barre cash: prima barra della giornata alle 10:00 server (normali) / 11:00 (disallineate)
Uso: python3 -I controllo_indipendente_f0.py <cartella_csv> <SHA256.txt> <cartella_risultati>
"""
import sys, os, csv, hashlib, datetime as dt
from collections import defaultdict
import numpy as np

src, shafile, ris = sys.argv[1], sys.argv[2], sys.argv[3]
esito = []

# 1) SHA256
for riga in open(shafile, encoding="utf-8"):
    h, nome = riga.strip().split("  ", 1)
    m = hashlib.sha256()
    with open(os.path.join(src, nome), "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""): m.update(blk)
    esito.append(("sha256 " + nome, m.hexdigest() == h))

# 2-3) conteggi con csv
def conta(nome):
    per_anno = defaultdict(lambda: [0, 0]); per_giorno = defaultdict(lambda: [0, 0])
    prev = None
    with open(os.path.join(src, nome + ".csv"), newline="") as f:
        r = csv.reader(f, delimiter="\t"); next(r)
        for row in r:
            y = row[0][:4]; m00 = row[1][3:5] == "00"
            per_anno[y][0] += 1; per_anno[y][1] += m00
            t = int(row[1][:2]) * 60 + int(row[1][3:5])
            per_giorno[row[0]][0] += 1
            if prev is not None and prev[0] == row[0] and t - prev[1] == 1: per_giorno[row[0]][1] += 1
            prev = (row[0], t)
    return per_anno, per_giorno

import pandas as pd
aud = pd.read_csv(os.path.join(ris, "AUDIT_M1_per_anno.csv"), sep=";", decimal=",")
riass = pd.read_csv(os.path.join(ris, "AUDIT_M1_riassunto.csv"), sep=";", decimal=",")
for nome in ["UK100 FTMO m1", "UK100 Pepperstone m1", "GER40 FTMO m1", "GER40 Pepperstone m1", "US500 m1 - Pepperstone"]:
    pa, pg = conta(nome)
    for y, (n, n00) in pa.items():
        a = aud[(aud.file == nome) & (aud.anno == int(y))].iloc[0]
        esito.append((f"barre {nome} {y}", int(a.barre) == n and abs(a.quota_min00 - round(n00 / n, 4)) < 1e-4))
    giorni = sorted(pg)
    # giornata M1 = almeno 30 barre e oltre metà dei passi consecutivi pari a 1 minuto
    non_m1 = [d for d in giorni if not (pg[d][0] >= 30 and pg[d][1] / max(pg[d][0] - 1, 1) >= 0.5)]
    inizio = (dt.datetime.strptime(non_m1[-1], "%Y.%m.%d") + dt.timedelta(days=1)).strftime("%Y-%m-%d")
    atteso = riass[riass.file == nome].inizio_M1_continuo.iloc[0]
    esito.append((f"inizio M1 {nome} = {inizio}", inizio == atteso))

# 4) fuso con numpy
from zoneinfo import ZoneInfo
NY, LON = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")
def disall(d):
    t = dt.datetime(d.year, d.month, d.day, 12, tzinfo=dt.timezone.utc)
    return (t.astimezone(LON).utcoffset() - t.astimezone(NY).utcoffset()) == dt.timedelta(hours=4)
for nome, ini in [("UK100 FTMO m1", "2021.09.14"), ("UK100 Pepperstone m1", "2017.06.03")]:
    acc = defaultdict(lambda: defaultdict(list))
    prev = None
    with open(os.path.join(src, nome + ".csv"), newline="") as f:
        r = csv.reader(f, delimiter="\t"); next(r)
        for row in r:
            if row[0] < ini: continue
            t = dt.datetime.strptime(row[0] + " " + row[1], "%Y.%m.%d %H:%M:%S"); c = float(row[5])
            if prev and (t - prev[0]).seconds == 60 and (t - prev[0]).days == 0 and 9 <= t.hour < 12:
                cl = "dis" if disall(t.date()) else "nor"
                acc[cl][t.hour * 60 + t.minute].append(abs(np.log(c / prev[1])))
            prev = (t, c)
    for cl, atteso in [("nor", 600), ("dis", 660)]:
        mins = sorted(acc[cl]); medie = np.array([np.mean(acc[cl][m]) for m in mins])
        picco = mins[int(np.argmax(medie))]
        esito.append((f"fuso {nome} settimane {cl}: picco {picco // 60:02d}:{picco % 60:02d}", picco == atteso))

# 5) RSI / ATR
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comune"))
import barre
rng = np.random.default_rng(7)
c = 8000 + np.cumsum(rng.normal(0, 5, 3000)); h = c + rng.uniform(0, 6, 3000); l = c - rng.uniform(0, 6, 3000)
def rsi_ciclo(c, n):
    out = [np.nan] * len(c); g = [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]; p = [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ag = sum(g[:n]) / n; al = sum(p[:n]) / n; out[n] = 100 - 100 / (1 + ag / al)
    for i in range(n, len(g)):
        ag = (ag * (n - 1) + g[i]) / n; al = (al * (n - 1) + p[i]) / n; out[i + 1] = 100 - 100 / (1 + ag / al)
    return np.array(out)
r1 = barre.rsi_wilder(c, 14); r2 = rsi_ciclo(c, 14)
esito.append(("RSI Wilder barre.py = ciclo esplicito (max diff < 1e-9)", np.nanmax(np.abs(r1 - r2)) < 1e-9))
d = pd.Series(c).diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
r3 = 100 - 100 / (1 + up.ewm(alpha=1/14, adjust=False).mean() / dn.ewm(alpha=1/14, adjust=False).mean())
# il seme (media semplice vs primo valore) conta solo nel riscaldamento: dopo 300 barre diff < 1e-7
esito.append(("RSI Wilder = pandas ewm dopo 300 barre di riscaldamento (diff < 1e-7)", np.nanmax(np.abs(r1[300:] - r3.to_numpy()[300:])) < 1e-7))
tr = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])
a = [np.nan] * 3000; v = (h[0] - l[0] + tr[:13].sum()) / 14; a[13] = v
for i in range(14, 3000): v = (v * 13 + tr[i - 1]) / 14; a[i] = v
esito.append(("ATR Wilder barre.py = ciclo esplicito", np.nanmax(np.abs(barre.atr_wilder(h, l, c, 14) - np.array(a))) < 1e-9))

# 6) barre cash: ora server della prima barra
m1 = barre.carica_m1(os.path.join(src, "UK100 FTMO m1.csv"), "2022-01-01", "2025-01-01")
b = barre.h1_cash(m1)
prime = b.groupby("data_locale").ts0.min()
oz = {d: disall(d.date()) for d in prime.index}
# tolleranza 5 minuti: un minuto mancante nel feed (es. 04/06/2024 10:00) sposta il primo M1
ok_n = all(t.hour == 10 and t.minute < 5 for d, t in prime.items() if not oz[d])
ok_d = all(t.hour == 11 and t.minute < 5 for d, t in prime.items() if oz[d])
esito.append(("barra cash 08:00 UK = 10:00 server (normali)", ok_n))
esito.append(("barra cash 08:00 UK = 11:00 server (disallineate)", ok_d))
esito.append(("barre cash per giorno: moda 9", int(b.groupby("data_locale").size().mode().iloc[0]) == 9))

ok = all(e[1] for e in esito)
with open(os.path.join(ris, "CONTROLLO_INDIPENDENTE_F0.txt"), "w", encoding="utf-8") as f:
    for nome, v in esito: f.write(("OK   " if v else "FAIL ") + nome + "\n")
    f.write(f"\nTOTALE: {sum(e[1] for e in esito)}/{len(esito)} OK\n")
for nome, v in esito: print(("OK   " if v else "FAIL ") + nome)
print("TOTALE", sum(e[1] for e in esito), "/", len(esito))
