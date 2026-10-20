# -*- coding: utf-8 -*-
"""Funzioni comuni di S1/S2 (PROTOCOLLO_S1_S2.md): feed sigillati, fusi, prezzi «a t» e «prima di t», sigma giornaliera,
calendari di borsa, costi FTMO in bps, statistiche (CR1 per data di New York, bootstrap per giorno, Benjamini-Hochberg)."""
import os
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo
import holidays

NY = ZoneInfo("America/New_York"); ATENE = ZoneInfo("Europe/Athens")
REPO = "/home/user/Strategy-20-10-UK100"
QUI = os.path.join(REPO, "lavoro", "s1_s2")
CACHE = "/tmp/claude-0/-home-user-Strategy-20-10-UK100/3f32bb43-76e4-56e7-9055-9f1cda27903e/scratchpad/cache_s12"
FINE_SCOPERTA = pd.Timestamp("2024-01-01")

D_TUTTI, D_H1, D_S12 = "/home/user/dati_scoperta_tutti", "/home/user/dati_h1/scoperta", "/home/user/dati_s12/scoperta"
V_H1, V_S12 = "/home/user/dati_h1/validazione_2024", "/home/user/dati_s12/validazione_2024"

# feed: (cartella scoperta, cartella validazione, file, primo giorno M1 vero, regime del fuso)
FEED = {
    ("EURUSD", "FTMO"): (D_H1, V_H1, "EURUSD m1 FTMO", "2016-01-04", "FX_FTMO"),
    ("GBPUSD", "FTMO"): (D_H1, V_H1, "GBPUSD m1 FTMO", "2016-01-04", "FX_FTMO"),
    ("USDJPY", "FTMO"): (D_H1, V_H1, "USDJPY m1 FTMO", "2016-01-04", "FX_FTMO"),
    ("XAU", "PEP"): (D_H1, V_H1, "XAU-USD Pepperstone m1", "2017-06-12", "NY7"),
    ("XAU", "FTMO"): (D_H1, V_H1, "XAU-USD FTMO m1", "2021-01-04", "NY7"),
    ("US100", "PEP"): (D_TUTTI, V_S12, "NAS100 m1 - FTPepperstone", "2017-06-09", "NY7"),
    ("US100", "FTMO"): (D_TUTTI, V_S12, "US100 m1 - FTMO", "2021-09-14", "NY7"),
    ("US500", "PEP"): (D_TUTTI, V_S12, "US500 m1 - Pepperstone", "2020-07-13", "NY7"),
    ("US500", "FTMO"): (D_TUTTI, V_S12, "US500 m1 - FTMO", "2021-09-14", "NY7"),
    ("US30", "PEP"): (D_S12, V_S12, "US30 Pepperstone m1", "2018-01-02", "NY7"),
    ("US2000", "PEP"): (D_S12, V_S12, "US2000 m1 Pepperstone", "2017-06-05", "NY7"),
    ("US2000", "FTMO"): (D_S12, V_S12, "US2000 m1 FTMO", "2018-04-09", "NY7"),
    ("GER40", "PEP"): (D_TUTTI, V_S12, "GER40 Pepperstone m1", "2020-06-11", "NY7"),
    ("GER40", "FTMO"): (D_TUTTI, V_S12, "GER40 FTMO m1", "2021-12-28", "NY7"),
    ("UK100", "PEP"): (D_TUTTI, V_S12, "UK100 Pepperstone m1", "2017-06-06", "NY7"),
    ("UK100", "FTMO"): (D_TUTTI, V_S12, "UK100 FTMO m1", "2021-09-14", "NY7"),
    ("FRA40", "FTMO"): (D_S12, V_S12, "FRA40 m1 FTMO", "2021-09-14", "NY7"),
}


def carica(strumento, feed, campione="scoperta"):
    """M1 (ts server, o, c) dal primo giorno M1 vero; solo copie sigillate."""
    os.makedirs(CACHE, exist_ok=True)
    pk = os.path.join(CACHE, f"{strumento}_{feed}_{campione}.pkl")
    if os.path.exists(pk): return pd.read_pickle(pk)
    ds, dv, nome, inizio, _ = FEED[(strumento, feed)]
    path = os.path.join(ds if campione == "scoperta" else dv, nome + ".csv")
    raw = pd.read_csv(path, sep="\t", dtype=str, usecols=[0, 1, 2, 5])
    raw.columns = ["d", "t", "o", "c"]
    da = pd.Timestamp(inizio).strftime("%Y.%m.%d") if campione == "scoperta" else "2023.11.01"
    raw = raw[raw.d >= da]
    df = pd.DataFrame({"ts": pd.to_datetime(raw.d + " " + raw.t, format="%Y.%m.%d %H:%M:%S").values,
                       "o": raw.o.astype(float).values, "c": raw.c.astype(float).values})
    df = df.drop_duplicates("ts", keep="last").sort_values("ts").reset_index(drop=True)
    if campione == "scoperta": assert df.ts.max() < FINE_SCOPERTA
    # passo modale (minuti) fra barre consecutive del giorno server: le barre di giorni con passo != 1 non si usano
    giorno = df.ts.dt.normalize()
    passo = df.ts.diff().dt.total_seconds().div(60)
    moda = passo.groupby(giorno).agg(lambda x: x.mode().iloc[0] if x.notna().any() else np.nan)
    df["m1_ok"] = (giorno.map(moda) == 1).values
    df.to_pickle(pk)
    return df


def a_server(locali_naive, tz, regime):
    """istanti locali (naive, nel fuso tz) -> ora server del feed. regime: 'NY7' oppure 'FX_FTMO'
    (ora di Atene fino al 31/12/2019, NY+7 dal 2020: verifica_fuso_fx_2019_2020.py)."""
    loc = pd.DatetimeIndex(locali_naive)
    ny = loc.tz_localize(ZoneInfo(tz), ambiguous="NaT", nonexistent="NaT").tz_convert(NY).tz_localize(None)
    ny7 = ny + pd.Timedelta(hours=7)
    if regime == "NY7": return ny7
    ate = loc.tz_localize(ZoneInfo(tz), ambiguous="NaT", nonexistent="NaT").tz_convert(ATENE).tz_localize(None)
    return pd.DatetimeIndex(np.where(ny < pd.Timestamp("2020-01-01"), ate.values, ny7.values))


def prezzo_a(df, T, tol=5):
    """open della prima barra che inizia in [T, T+tol]; valido solo se esiste anche una barra che inizia in [T-tol, T)
    (continuita': niente prezzi di riapertura dopo una pausa) e se il giorno della barra e' M1 (passo modale 1 minuto)."""
    t = df.ts.values; q = np.asarray(pd.DatetimeIndex(T).values, dtype="datetime64[ns]")
    k = np.searchsorted(t, q, side="left"); kc = np.clip(k, 0, len(t) - 1); kp = np.clip(k - 1, 0, len(t) - 1)
    nq = np.isnat(q); q2 = np.where(nq, t[0], q)
    ok = (k < len(t)) & ((t[kc] - q2) <= np.timedelta64(tol, "m")) & ~nq
    ok &= (k >= 1) & ((q2 - t[kp]) <= np.timedelta64(tol, "m"))
    ok &= df.m1_ok.values[kc]
    return np.where(ok, df.o.values[kc], np.nan)


def prezzo_prima(df, T, tol=5):
    """close dell'ultima barra che inizia in [T-tol, T), in un giorno M1 (passo modale 1 minuto)."""
    t = df.ts.values; q = np.asarray(pd.DatetimeIndex(T).values, dtype="datetime64[ns]")
    k = np.searchsorted(t, q, side="left") - 1; kc = np.clip(k, 0, None)
    nq = np.isnat(q); q2 = np.where(nq, t[0], q)
    ok = (k >= 0) & ((q2 - t[kc]) <= np.timedelta64(tol, "m")) & ~nq & df.m1_ok.values[kc]
    return np.where(ok, df.c.values[kc], np.nan)


def sigma_giornaliera(df, tz, hm, regime, giorni):
    """sigma_d per ogni giorno: dev. std dei 20 rendimenti giornalieri precedenti (fino a d-1), prezzo prima di hm locale
    (entro 15 minuti), rendimenti fra giorni validi consecutivi entro 4 giorni di calendario. Ritorna Series indicizzata
    per data (normalizzata)."""
    h, m = map(int, hm.split(":"))
    giorni = pd.DatetimeIndex(giorni).normalize()
    P = prezzo_prima(df, a_server(giorni + pd.Timedelta(hours=h, minutes=m), tz, regime), tol=15)
    d = pd.DataFrame({"P": P}, index=giorni).dropna()
    gap = pd.Series(d.index, index=d.index).diff().dt.days
    r = np.log(d.P / d.P.shift()).where(gap <= 4)
    s = r.dropna().rolling(20, min_periods=20).std().shift(1)
    return s.reindex(d.index).ffill().reindex(giorni)


# ------------------------------------------------------------------ calendari di borsa
NYSE_ANTICIPATE = {pd.Timestamp(x) for x in ["2017-07-03", "2017-11-24", "2018-07-03", "2018-11-23", "2018-12-24",
    "2019-07-03", "2019-11-29", "2019-12-24", "2020-11-27", "2020-12-24", "2021-11-26", "2022-11-25", "2023-07-03",
    "2023-11-24", "2024-07-03", "2024-11-29", "2024-12-24"]}

def giorni_borsa(borsa, da, a):
    """giorni di borsa cassa interi (esclusi festivi e mezze sedute)."""
    anni = range(pd.Timestamp(da).year - 1, pd.Timestamp(a).year + 2)
    g = pd.date_range(da, a, freq="B")
    if borsa == "NYSE":
        fest = set(pd.Timestamp(x) for x in holidays.NYSE(years=anni).keys()) | NYSE_ANTICIPATE
    elif borsa == "LSE":
        fest = set(pd.Timestamp(x) for x in holidays.UK(subdiv="ENG", years=anni).keys())
        for y in anni:   # mezze sedute: ultimo giorno lavorativo prima di Natale e di Capodanno
            for gg in (24, 31):
                x = pd.Timestamp(y, 12, gg)
                while x.weekday() >= 5: x -= pd.Timedelta(days=1)
                fest.add(x)
    else:   # XETRA o EURONEXT (Parigi): festivi della borsa + 24 e 31/12 (chiusura o mezza seduta)
        fest = set()
        for y in anni:
            for d, n in holidays.Germany(years=y).items():
                if n in ("Karfreitag", "Ostermontag", "Good Friday", "Easter Monday"): fest.add(pd.Timestamp(d))
            for mm, gg in [(1, 1), (5, 1), (12, 24), (12, 25), (12, 26), (12, 31)]: fest.add(pd.Timestamp(y, mm, gg))
    return pd.DatetimeIndex([x for x in g if x not in fest])


# ------------------------------------------------------------------ statistiche
def cr1(x, gruppi):
    """media, t con errori raggruppati (CR1) e numero di gruppi."""
    x = np.asarray(x, float); g = pd.factorize(np.asarray(gruppi))[0]
    n = len(x); G = g.max() + 1 if n else 0
    if n < 3 or G < 3: return float(np.mean(x)) if n else np.nan, np.nan, G
    m = x.mean(); e = x - m
    s = np.bincount(g, weights=e, minlength=G)
    v = (s ** 2).sum() / n ** 2 * G / (G - 1)
    return float(m), float(m / np.sqrt(v)), int(G)

def p_unilaterale(t):
    from math import erf, sqrt
    return 1 - 0.5 * (1 + erf(t / sqrt(2))) if np.isfinite(t) else np.nan

def bootstrap_giorni(x, gruppi, nrep=10_000, seed=20261020):
    """p unilaterale (media <= 0) con bootstrap per giorno: ricampiona i giorni con reinserimento."""
    x = np.asarray(x, float); g = pd.factorize(np.asarray(gruppi))[0]; G = g.max() + 1
    som = np.bincount(g, weights=x, minlength=G); cnt = np.bincount(g, minlength=G)
    rng = np.random.default_rng(seed); out = np.empty(nrep)
    for i in range(0, nrep, 2000):
        k = min(2000, nrep - i)
        idx = rng.integers(0, G, size=(k, G))
        out[i:i + k] = som[idx].sum(1) / cnt[idx].sum(1)
    medie_centrate = out - x.mean()          # distribuzione sotto H0 (media spostata a 0)
    return float((1 + (medie_centrate >= x.mean()).sum()) / (1 + nrep))

def bh(p, q=0.10):
    p = np.asarray(p, float); ok = np.isfinite(p); m = ok.sum()
    ordine = np.argsort(np.where(ok, p, np.inf)); k = 0
    for i, j in enumerate(ordine[:m], 1):
        if p[j] <= i / m * q: k = i
    out = np.zeros(len(p), bool); out[ordine[:k]] = True
    soglia = k / m * q if k else 0.0
    return out, soglia
