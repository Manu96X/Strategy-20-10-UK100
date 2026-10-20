# -*- coding: utf-8 -*-
"""
Funzioni comuni: caricamento M1 (export MT5, ora server = New York + 7, verificato in F0),
ora locale di borsa, barre H1 "di sessione cash" e barre H1 "CFD" (ora server),
indicatori di Wilder (RSI, ATR) e SMA calcolati SOLO su barre chiuse.

RSI di Wilder (1978), come in MT5 iRSI e TradingView ta.rsi (verificato sui papers:
Panigrahi et al. 2021, Hill 2019 appendice 1):
  variazione_t = close_t - close_{t-1}; G = max(var,0), L = max(-var,0)
  prima media = media semplice delle prime n G e L; poi AG_t = (AG_{t-1}*(n-1) + G_t)/n
  RS = AG/AL; RSI = 100 - 100/(1+RS)   (AL = 0 -> RSI = 100)
ATR di Wilder: TR_t = max(h-l, |h-c_{t-1}|, |l-c_{t-1}|), stessa media di Wilder.
"""
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")

def carica_m1(path, inizio=None, fine=None):
    raw = pd.read_csv(path, sep="\t", dtype=str)
    raw.columns = [c.strip("<>").lower() for c in raw.columns]
    dig = int(raw["close"].head(20000).str.split(".").str[1].str.len().fillna(0).max())
    df = pd.DataFrame({
        "ts": pd.to_datetime(raw["date"] + " " + raw["time"], format="%Y.%m.%d %H:%M:%S"),
        "o": raw["open"].astype(float), "h": raw["high"].astype(float),
        "l": raw["low"].astype(float), "c": raw["close"].astype(float),
        "sp": raw["spread"].astype(float) * 10.0 ** (-dig)})
    if inizio is not None: df = df[df.ts >= pd.Timestamp(inizio)]
    if fine is not None: df = df[df.ts < pd.Timestamp(fine)]
    return df.reset_index(drop=True)

def ora_locale(ts_server, tz):
    """ora server (NY+7) -> ora locale della borsa (tz IANA)."""
    ny_naive = ts_server - pd.Timedelta(hours=7)
    utc = ny_naive.dt.tz_localize(NY, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    return utc.dt.tz_convert(ZoneInfo(tz)).dt.tz_localize(None)

def h1_cash(m1, tz="Europe/London", apre="08:00", chiude="16:30"):
    """Barre H1 della sola sessione cash in ora locale (ultima barra eventualmente corta).
    Ogni barra porta ts_server di inizio (primo M1) e di fine (ultimo M1 + 1 minuto)."""
    loc = ora_locale(m1.ts, tz)
    hh, mm = map(int, apre.split(":")); ch, cm = map(int, chiude.split(":"))
    mins = loc.dt.hour * 60 + loc.dt.minute
    sel = (mins >= hh * 60 + mm) & (mins < ch * 60 + cm) & loc.notna()
    x = m1[sel].copy(); x["loc"] = loc[sel]
    x["k"] = x["loc"].dt.floor("h")
    g = x.groupby("k")
    b = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(),
                      "ts0": g.ts.first(), "ts1": g.ts.last() + pd.Timedelta(minutes=1), "n_m1": g.size()})
    b.index.name = "ora_locale"
    b["data_locale"] = b.index.normalize()
    return b.reset_index()

def h1_cfd(m1):
    """Barre H1 come le mostra MT5 (ora server)."""
    x = m1.copy(); x["k"] = x.ts.dt.floor("h")
    g = x.groupby("k")
    b = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(),
                      "ts0": g.ts.first(), "ts1": g.ts.last() + pd.Timedelta(minutes=1), "n_m1": g.size()})
    b.index.name = "ora_server"
    return b.reset_index()

def _wilder(x, n):
    x = np.asarray(x, float); out = np.full(len(x), np.nan)
    if len(x) < n: return out
    out[n - 1] = np.nanmean(x[:n])
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out

def rsi_wilder(c, n=14):
    c = np.asarray(c, float); d = np.diff(c, prepend=np.nan)
    g = np.where(d > 0, d, 0.0); l = np.where(d < 0, -d, 0.0)
    ag = _wilder(g[1:], n); al = _wilder(l[1:], n)
    ag = np.concatenate([[np.nan], ag]); al = np.concatenate([[np.nan], al])
    with np.errstate(divide="ignore", invalid="ignore"):
        rsi = np.where(al == 0, 100.0, 100 - 100 / (1 + ag / al))
    rsi[np.isnan(ag)] = np.nan
    return rsi

def atr_wilder(h, l, c, n=14):
    h, l, c = (np.asarray(v, float) for v in (h, l, c))
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    tr[0] = h[0] - l[0]
    return _wilder(tr, n)

def sma(c, n=40):
    return pd.Series(np.asarray(c, float)).rolling(n, min_periods=n).mean().to_numpy()
