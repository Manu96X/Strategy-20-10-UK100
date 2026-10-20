#!/usr/bin/env python3
"""Seconda implementazione minimale (puro Python, csv + zoneinfo, nessun pandas)
delle barre di sessione e degli indicatori, per controllare a mano i trade scelti.
Uso: python3 -I verifica_mano.py
"""
import csv
import datetime as dt
from zoneinfo import ZoneInfo
import holidays

F = "/home/user/dati_scoperta/UK100 Pepperstone m1.csv"
NY, LON = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")
FEST = set(holidays.UK(subdiv="ENG", years=range(2016, 2027)).keys())

bars = []  # [dloc, k, o, h, l, c]
cur = None
with open(F) as fh:
    rd = csv.reader(fh, delimiter="\t")
    next(rd)
    for r in rd:
        ts = dt.datetime.strptime(r[0] + " " + r[1], "%Y.%m.%d %H:%M:%S")
        if ts < dt.datetime(2017, 6, 6):
            continue
        lon = (ts - dt.timedelta(hours=7)).replace(tzinfo=NY).astimezone(LON)
        dl = lon.date()
        mins = lon.hour * 60 + lon.minute
        if dl.weekday() >= 5 or dl in FEST or not (480 <= mins < 990):
            continue
        k = (mins - 480) // 60
        o, h, l, c = map(float, r[2:6])
        if cur is not None and cur[0] == dl and cur[1] == k:
            cur[3] = max(cur[3], h); cur[4] = min(cur[4], l); cur[5] = c
        else:
            cur = [dl, k, o, h, l, c]
            bars.append(cur)

n = len(bars)
rsi = [None] * n; atr = [None] * n; sma = [None] * n
ag = al = a = None
for i in range(n):
    if i >= 1:
        ch = bars[i][5] - bars[i - 1][5]
    if i == 14:
        chs = [bars[j][5] - bars[j - 1][5] for j in range(1, 15)]
        ag = sum(max(x, 0) for x in chs) / 14; al = sum(max(-x, 0) for x in chs) / 14
    elif i > 14:
        ag = (ag * 13 + max(ch, 0)) / 14; al = (al * 13 + max(-ch, 0)) / 14
    if i >= 14:
        rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    h, l = bars[i][3], bars[i][4]
    tr = h - l if i == 0 else max(h - l, abs(h - bars[i - 1][5]), abs(l - bars[i - 1][5]))
    bars[i].append(tr)
    if i == 13:
        a = sum(b[6] for b in bars[:14]) / 14
    elif i > 13:
        a = (a * 13 + tr) / 14
    if i >= 13:
        atr[i] = a
    if i >= 39:
        sma[i] = sum(b[5] for b in bars[i - 39:i + 1]) / 40

print("barre totali", n)
for giorno in ["2017-07-24", "2017-11-20", "2017-11-13", "2017-08-11"]:
    g = dt.date.fromisoformat(giorno)
    for i, b in enumerate(bars):
        if b[0] == g:
            s3 = sma[i] - 3 * atr[i]
            print(f"{giorno} idx={i} k={b[1]} O={b[2]} H={b[3]} L={b[4]} C={b[5]} "
                  f"RSI={rsi[i]:.4f} ATR={atr[i]:.6f} SMA40={sma[i]:.4f} SMA-3ATR={s3:.4f}")

import sys
if len(sys.argv) > 1:  # dump completo per confronto con replica_f3.py
    with open(sys.argv[1], "w") as fo:
        fo.write("dloc;k;o;h;l;c;rsi;atr;sma\n")
        for i, b in enumerate(bars):
            fo.write(f"{b[0]};{b[1]};{b[2]};{b[3]};{b[4]};{b[5]};{rsi[i]};{atr[i]};{sma[i]}\n")
