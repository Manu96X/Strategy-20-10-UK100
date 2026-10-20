#!/usr/bin/env python3
"""Replica indipendente del backtest F3 (celle A1, A2, A5) su UK100 Pepperstone M1.

Scritta da zero seguendo SOLO le convenzioni del compito di verifica.
Dati: /home/user/dati_scoperta (nessuna riga >= 2024-01-01).
Uso: python3 -I replica_f3.py
"""
import os
import sys
import datetime as dt

import numpy as np
import pandas as pd
import holidays

FILE = "/home/user/dati_scoperta/UK100 Pepperstone m1.csv"
OUT = os.path.dirname(os.path.abspath(__file__))
INIZIO = pd.Timestamp("2017-06-06 00:00")
SPREAD = [5.71, 5.31, 4.85, 4.15, 3.95, 3.75, 3.65, 3.65, 3.85, 1.65, 0.85, 0.75,
          0.75, 0.65, 0.75, 0.75, 0.75, 0.75, 0.85, 1.65, 1.45, 1.45, 1.45, 5.71]
assert len(SPREAD) == 24
FEST = holidays.UK(subdiv="ENG", years=range(2016, 2027))
FEST_SET = set(FEST.keys())
MIN = np.int64(60 * 10**9)
ORA = 60 * MIN


# ---------------------------------------------------------------- dati M1
def carica_m1():
    df = pd.read_csv(FILE, sep="\t")
    df.columns = [c.strip("<>").lower() for c in df.columns]
    ts = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M:%S")
    df["ts"] = ts
    df = df[df["ts"] >= INIZIO].reset_index(drop=True)
    assert df["ts"].is_monotonic_increasing and df["ts"].is_unique
    return df


def server_a_londra(ts_server):
    """ts server naive -> ora locale Londra naive."""
    ny = (ts_server - pd.Timedelta(hours=7)).dt.tz_localize(
        "America/New_York", ambiguous="raise", nonexistent="raise")
    return ny.dt.tz_convert("Europe/London").dt.tz_localize(None)


def londra_a_server(ts_lon):
    """ts locale Londra naive (DatetimeIndex/Series) -> ts server naive."""
    s = pd.Series(ts_lon)
    lo = s.dt.tz_localize("Europe/London", ambiguous="raise", nonexistent="raise")
    return lo.dt.tz_convert("America/New_York").dt.tz_localize(None) + pd.Timedelta(hours=7)


# ---------------------------------------------------------------- barre di sessione
def barre_sessione(m1):
    lon = server_a_londra(m1["ts"])
    dloc = lon.dt.normalize()
    minuti = (lon - dloc) / pd.Timedelta(minutes=1)
    dd = dloc.dt.date
    feriale = dloc.dt.weekday < 5
    nonfest = ~dd.isin(FEST_SET)
    # correzione 2: 24 e 31/12 feriali non festivi -> chiusura cash alle 12:30 (750 minuti)
    semi = pd.Series([(d.month == 12 and d.day in (24, 31) and d.weekday() < 5 and d not in FEST_SET) for d in dd], index=dd.index)
    chiude = np.where(semi, 750, 990)
    insess = (minuti >= 480) & (minuti < chiude)
    sel = feriale & nonfest & insess
    s = m1.loc[sel, ["ts", "open", "high", "low", "close"]].copy()
    s["dloc"] = dloc[sel].values
    s["k"] = ((minuti[sel] - 480) // 60).astype(int).values
    g = s.groupby(["dloc", "k"], sort=True)
    b = g.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
              close=("close", "last"), n=("ts", "size")).reset_index()
    # fine nominale (Londra) e in ora server
    ch_b = np.array([750 if (d.month == 12 and d.day in (24, 31) and d.weekday() < 5 and d.date() not in FEST_SET) else 990 for d in b["dloc"]])
    fine_lon = b["dloc"] + pd.to_timedelta(np.minimum(480 + (b["k"].to_numpy() + 1) * 60, ch_b), unit="m")
    b["fine_lon"] = fine_lon
    b["fine_srv"] = londra_a_server(fine_lon).values
    return b


# ---------------------------------------------------------------- indicatori
def rsi_wilder(c, n=14):
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    dlt = np.diff(c)
    g = np.where(dlt > 0, dlt, 0.0)
    p = np.where(dlt < 0, -dlt, 0.0)
    ag = g[:n].mean()
    al = p[:n].mean()

    def val(ag, al):
        return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    out[n] = val(ag, al)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + g[i - 1]) / n
        al = (al * (n - 1) + p[i - 1]) / n
        out[i] = val(ag, al)
    return out


def atr_wilder(h, l, c, n=14):
    h, l, c = (np.asarray(x, float) for x in (h, l, c))
    tr = np.empty(len(h))
    tr[0] = h[0] - l[0]
    pc = c[:-1]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - pc), np.abs(l[1:] - pc)))
    out = np.full(len(h), np.nan)
    a = tr[:n].mean()
    out[n - 1] = a
    for i in range(n, len(h)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def sma(c, n=40):
    return pd.Series(np.asarray(c, float)).rolling(n, min_periods=n).mean().values


# ---------------------------------------------------------------- motore
class Motore:
    def __init__(self, m1):
        self.ts = m1["ts"].values.astype("datetime64[ns]").astype(np.int64)
        self.o = m1["open"].values.astype(float)
        self.h = m1["high"].values.astype(float)
        self.l = m1["low"].values.astype(float)
        self.c = m1["close"].values.astype(float)
        dsrv = m1["ts"].dt.normalize()
        self.dsrv_i = dsrv.values.astype("datetime64[D]").astype(np.int64)  # giorni epoch
        # calendario di trading (date server)
        u = pd.Series(self.ts).groupby(self.dsrv_i).max()
        giorni = []
        for di, last in u.items():
            d = dt.date(1970, 1, 1) + dt.timedelta(days=int(di))
            if d.weekday() < 5 and d not in FEST_SET:
                giorni.append((int(di), int(last)))
        self.td = np.array([g[0] for g in giorni], np.int64)
        self.td_set = set(self.td.tolist())
        self.ultimo = {g[0]: g[1] for g in giorni}
        chius = np.zeros(len(self.td), bool)
        chius[:-1] = np.diff(self.td) > 1
        chius[-1] = True
        self.chius = chius
        self.chius_dopo = {int(d): bool(x) for d, x in zip(self.td, chius)}

    def dstar(self, d):
        """primo giorno di trading >= d seguito da chiusura"""
        i = np.searchsorted(self.td, d, side="left")
        while not self.chius[i]:
            i += 1
        return int(self.td[i])

    def simula(self, fine_srv, atr, m, t_regola_fn):
        """Ritorna dict trade o None. fine_srv in int64 ns."""
        i0 = int(np.searchsorted(self.ts, fine_srv, side="left"))
        if i0 >= len(self.ts):
            return None
        tin = int(self.ts[i0])
        if tin - fine_srv > 15 * MIN:
            return None
        D = int(self.dsrv_i[i0])
        if D not in self.td_set:
            return None
        if self.chius_dopo[D] and tin >= self.ultimo[D] - 2 * ORA:
            return None
        hh = int((tin // ORA) % 24)
        fill = self.o[i0] + SPREAD[hh]
        d = m * atr
        sl = fill - d
        tp = fill + 2 * d
        t_reg = t_regola_fn(tin)
        if t_reg is None:
            return None
        t_forz = self.ultimo[self.dstar(D)] - 15 * MIN
        t_usc = min(t_reg, t_forz)
        if t_usc <= tin:
            return None
        j = int(np.searchsorted(self.ts, t_usc, side="left"))
        if j >= len(self.ts):
            return None
        lw = self.l[i0:j]
        hg = self.h[i0:j]
        hit = np.nonzero((lw <= sl) | (hg >= tp))[0]
        if len(hit):
            x = i0 + int(hit[0])
            if self.l[x] <= sl:
                px = min(self.o[x], sl) - 0.8   # correzione 1: protocollo §3
                tipo = "SL"
            else:
                px = tp
                tipo = "TP"
        else:
            x = j
            px = self.o[x]
            tipo = "TEMPO" if t_usc == t_reg else "CHIUSURA"
        tout = int(self.ts[x])
        din, dout = int(self.dsrv_i[i0]), int(self.dsrv_i[x])
        notti = dout - din
        swap = 0.0
        for dd in range(din, dout):
            wd = (dt.date(1970, 1, 1) + dt.timedelta(days=dd)).weekday()
            swap += 1.5 if wd == 2 else 0.5
        R = (px - fill - swap) / d
        return dict(i0=i0, x=x, ts_in=tin, ts_out=tout, fill=fill, sl=sl, tp=tp,
                    px_out=px, tipo=tipo, notti=notti, swap=swap, d=d, R=R,
                    t_regola=t_reg, t_forzata=t_forz, t_uscita=t_usc)


def fmt_ts(x):
    return pd.Timestamp(int(x)).strftime("%Y-%m-%d %H:%M")


def esegui():
    m1 = carica_m1()
    b = barre_sessione(m1)
    b["rsi"] = rsi_wilder(b["close"].values)
    b["atr"] = atr_wilder(b["high"].values, b["low"].values, b["close"].values)
    b["sma"] = sma(b["close"].values)
    idx = np.arange(len(b))
    b["valida"] = (idx >= 300) & b["rsi"].notna() & b["atr"].notna() & b["sma"].notna()
    fine = b["fine_srv"].values.astype("datetime64[ns]").astype(np.int64)
    eng = Motore(m1)

    risultati = {}
    # ---- A1 / A2
    for cella, m in (("A1", 2.5), ("A2", 2.5)):
        trades = []
        lun = b[b["dloc"].dt.weekday == 0]
        for dl, grp in lun.groupby("dloc", sort=True):
            if int(grp["k"].iloc[0]) != 0:
                continue
            ap = float(grp["open"].iloc[0])
            for s in grp.index:
                r = b.loc[s]
                if not r["valida"]:
                    continue
                if not (r["close"] < ap and r["rsi"] < 40):
                    continue
                if cella == "A1":
                    fn = lambda tin: tin + 24 * ORA
                else:
                    fn = (lambda tin, s=s: int(fine[s + 24]) if s + 24 < len(b) else None)
                t = eng.simula(int(fine[s]), float(r["atr"]), m, fn)
                if t is None:
                    continue
                t.update(s=s, data_locale=dl.date(), k=int(r["k"]))
                trades.append(t)
                break
        risultati[cella] = trades
    # ---- A5
    trades = []
    ultimo_out = -np.inf
    cond = (b["valida"] & (b["close"] <= b["sma"] - 3 * b["atr"]) & (b["rsi"] < 35)).values
    for s in np.nonzero(cond)[0]:
        if fine[s] < ultimo_out:
            continue
        t = eng.simula(int(fine[s]), float(b["atr"].iat[s]), 2.0, lambda tin: tin + 24 * ORA)
        if t is None:
            continue
        t.update(s=int(s), data_locale=b["dloc"].iat[s].date(), k=int(b["k"].iat[s]))
        trades.append(t)
        ultimo_out = t["ts_out"]
    risultati["A5"] = trades

    for cella, tr in risultati.items():
        df = pd.DataFrame([{
            "data_locale": t["data_locale"].isoformat(), "k": t["k"],
            "ts_in": fmt_ts(t["ts_in"]), "ts_out": fmt_ts(t["ts_out"]),
            "fill": round(t["fill"], 4), "sl": round(t["sl"], 4), "tp": round(t["tp"], 4),
            "px_out": round(t["px_out"], 4), "tipo": t["tipo"], "notti": t["notti"],
            "R": round(t["R"], 6)} for t in tr])
        df.to_csv(os.path.join(OUT, f"REPLICA_{cella}.csv"), sep=";", index=False)
        print(f"{cella}: n={len(df)} mediaR={df['R'].mean():.6f} sommaR={df['R'].sum():.4f} "
              f"tipi={df['tipo'].value_counts().to_dict()}")
    return m1, b, eng, risultati


if __name__ == "__main__":
    esegui()
