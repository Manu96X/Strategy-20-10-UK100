# -*- coding: utf-8 -*-
"""
Modulo comune dell'EVENT STUDY (F1-bis, 20/10/2026). Solo dati di scoperta sigillati (< 01/01/2024).

Convenzioni (PIANO_EVENT_STUDY.md):
- ora server = New York + 7 (verificato in F0 e in fuso_spread_altri.py per tutti gli strumenti);
- chiusura giornaliera = prezzo dell'ultimo M1 che INIZIA prima dell'orario di chiusura locale (entro 15 minuti);
  indici: chiusura della borsa cash; materie prime, VIX, dollaro: 16:00 di New York;
- rendimento giornaliero r_d = ln(C_d / C_{d-1}) fra giorni di trading consecutivi;
- sigma_d = deviazione standard dei 20 rendimenti precedenti (d-20 .. d-1): nota prima del giorno d;
- unità "z" = rendimento / sigma del giorno d'ingresso (rendimento in multipli della volatilità giornaliera).
"""
import os, sys, pickle
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo
import holidays

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "comune"))
import barre

DATI = "/home/user/dati_scoperta_tutti"
CACHE = "/tmp/claude-0/-home-user-Strategy-20-10-UK100/3f32bb43-76e4-56e7-9055-9f1cda27903e/scratchpad/cache_eventi"
NY = ZoneInfo("America/New_York")

# strumento: feed -> (file, primo giorno M1 vero); chiusura locale; apertura cash (solo indici); calendario festivi
STRUMENTI = {
    "US500": dict(feed={"PEP": ("US500 m1 - Pepperstone", "2020-07-13"), "FTMO": ("US500 m1 - FTMO", "2021-09-14")},
                  tz="America/New_York", apre="09:30", chiude="16:00", cal="NYSE", tipo="indice", ftmo_spread="US500 m1 - FTMO"),
    "US100": dict(feed={"PEP": ("NAS100 m1 - FTPepperstone", "2017-06-09"), "FTMO": ("US100 m1 - FTMO", "2021-09-14")},
                  tz="America/New_York", apre="09:30", chiude="16:00", cal="NYSE", tipo="indice", ftmo_spread="US100 m1 - FTMO"),
    "GER40": dict(feed={"PEP": ("GER40 Pepperstone m1", "2020-06-11"), "FTMO": ("GER40 FTMO m1", "2021-12-28")},
                  tz="Europe/Berlin", apre="09:00", chiude="17:30", cal="XETRA", tipo="indice", ftmo_spread="GER40 FTMO m1"),
    "UK100": dict(feed={"PEP": ("UK100 Pepperstone m1", "2017-06-06"), "FTMO": ("UK100 FTMO m1", "2021-09-14")},
                  tz="Europe/London", apre="08:00", chiude="16:30", cal="ENG", tipo="indice", ftmo_spread="UK100 FTMO m1"),
    "XAU": dict(feed={"PEP": ("XAU-USD Pepperstone m1", "2017-06-12"), "FTMO": ("XAU-USD FTMO m1", "2021-01-04")},
                tz="America/New_York", apre=None, chiude="16:00", cal=None, tipo="metallo", ftmo_spread="XAU-USD FTMO m1"),
    "XAG": dict(feed={"PEP": ("XAG-USD Pepperstone m1", "2017-06-12"), "FTMO": ("XAG-USD FTMO m1", "2021-01-04")},
                tz="America/New_York", apre=None, chiude="16:00", cal=None, tipo="metallo", ftmo_spread="XAG-USD FTMO m1"),
    "BRENT": dict(feed={"PEP": ("BRENT m1 - Pepperstone", "2018-04-02")},
                  tz="America/New_York", apre=None, chiude="16:00", cal=None, tipo="energia", ftmo_spread="USOIL m1 - FTMO"),
    "USOIL": dict(feed={"FTMO": ("USOIL m1 - FTMO", "2021-04-05")},
                  tz="America/New_York", apre=None, chiude="16:00", cal=None, tipo="energia", ftmo_spread="USOIL m1 - FTMO"),
    "VIX": dict(feed={"PEP": ("VIX Pepperstone m1", "2020-03-04")},
                tz="America/New_York", apre=None, chiude="16:00", cal=None, tipo="volatilita", ftmo_spread=None),
    "USDX": dict(feed={"PEP": ("USDX pepperstone m1", "2019-04-22")},
                 tz="America/New_York", apre=None, chiude="16:00", cal=None, tipo="valuta", ftmo_spread="DXY FTMO m1"),
}
FEED_INFERENZA = {s: ("PEP" if "PEP" in v["feed"] else "FTMO") for s, v in STRUMENTI.items()}

# Costi FTMO [STIMA salvo dove indicato]: commissione in % del nozionale per lato, swap in % del prezzo per notte di calendario
COSTI = {
    "indice":     dict(comm=0.0,     swap_base=0.005, swap_stress=0.02),    # US100.cash: commissione 0 [MISURATO], swap ≤0,28$/lotto/notte [MISURATO]
    "metallo":    dict(comm=0.0007,  swap_base=0.03,  swap_stress=0.04),    # oro: 0,0007%/lato [MISURATO]; swap long -65/-90 $/lotto [SPECIFICA] ≈ 0,03%
    "energia":    dict(comm=0.0007,  swap_base=0.01,  swap_stress=0.03),
    "valuta":     dict(comm=0.0,     swap_base=0.005, swap_stress=0.02),
    "volatilita": dict(comm=0.0,     swap_base=0.0,   swap_stress=0.0),     # VIX non quotato da FTMO: costi non applicabili
}

FOMC = ["2017-02-01", "2017-03-15", "2017-05-03", "2017-06-14", "2017-07-26", "2017-09-20", "2017-11-01", "2017-12-13",
        "2018-01-31", "2018-03-21", "2018-05-02", "2018-06-13", "2018-08-01", "2018-09-26", "2018-11-08", "2018-12-19",
        "2019-01-30", "2019-03-20", "2019-05-01", "2019-06-19", "2019-07-31", "2019-09-18", "2019-10-30", "2019-12-11",
        "2020-01-29", "2020-04-29", "2020-06-10", "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16",
        "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
        "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
        "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13"]
# riunioni programmate; comunicato alle 14:00 di New York (= 21:00 server). Marzo 2020: riunione del 18 annullata
# (tagli d'emergenza del 3 e del 15 marzo, non programmati -> esclusi).

NYSE_ANTICIPATE = ["2017-07-03", "2017-11-24", "2018-07-03", "2018-11-23", "2018-12-24", "2019-07-03", "2019-11-29",
                   "2019-12-24", "2020-11-27", "2020-12-24", "2021-11-26", "2022-11-25", "2023-07-03", "2023-11-24"]

def festivi(cal, anni=range(2016, 2027)):
    if cal == "ENG": return set(holidays.UK(subdiv="ENG", years=anni).keys())
    if cal == "NYSE": return set(holidays.NYSE(years=anni).keys())
    if cal == "XETRA":
        out = set()
        for y in anni:
            for d, n in holidays.Germany(years=y).items():
                if n in ("Karfreitag", "Ostermontag", "Good Friday", "Easter Monday"): out.add(d)
            for m, g in [(1, 1), (5, 1), (12, 24), (12, 25), (12, 26), (12, 31)]: out.add(pd.Timestamp(y, m, g).date())
        return out
    return set()

def terzo_venerdi(y, m):
    d = pd.Timestamp(y, m, 1); d += pd.Timedelta(days=(4 - d.weekday()) % 7)
    return (d + pd.Timedelta(days=14)).date()

def carica(strumento, feed):
    """M1 del feed (dal primo giorno M1 vero) con ora locale dello strumento. In cache su disco."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"m1_{strumento}_{feed}.pkl")
    if os.path.exists(p): return pd.read_pickle(p)
    nome, inizio = STRUMENTI[strumento]["feed"][feed]
    m1 = barre.carica_m1(os.path.join(DATI, nome + ".csv"), inizio)
    m1["loc"] = barre.ora_locale(m1.ts, STRUMENTI[strumento]["tz"])
    m1 = m1.dropna(subset=["loc"]).reset_index(drop=True)
    m1.to_pickle(p)
    return m1

def prezzo_alle(m1, ore_locali):
    """Prezzo (close dell'ultimo M1 che inizia prima dell'istante locale, entro 15 minuti) per una serie di istanti locali.
    Ritorna (prezzo, ts_server dell'M1 usato); NaN se non c'è un M1 nei 15 minuti precedenti."""
    t = m1["loc"].values.astype("datetime64[ns]")
    q = pd.to_datetime(pd.Series(ore_locali)).values.astype("datetime64[ns]")
    k = np.searchsorted(t, q, side="left") - 1
    ok = (k >= 0) & (q - t[np.clip(k, 0, None)] <= np.timedelta64(15, "m"))
    px = np.where(ok, m1.c.values[np.clip(k, 0, None)], np.nan)
    ts = np.where(ok, m1.ts.values[np.clip(k, 0, None)], np.datetime64("NaT"))
    return px, ts

def apertura_alle(m1, ore_locali):
    """Open del primo M1 che inizia all'istante locale o dopo (entro 15 minuti)."""
    t = m1["loc"].values.astype("datetime64[ns]")
    q = pd.to_datetime(pd.Series(ore_locali)).values.astype("datetime64[ns]")
    k = np.searchsorted(t, q, side="left")
    ok = (k < len(t)) & (t[np.clip(k, None, len(t) - 1)] - q <= np.timedelta64(15, "m"))
    return np.where(ok, m1.o.values[np.clip(k, None, len(t) - 1)], np.nan)

def giornaliero(strumento, feed):
    """Tabella giornaliera: data locale, C (chiusura), O (apertura cash per gli indici), r, sigma (20 gg precedenti), z.
    Giorni di trading = feriali locali con prezzo alla chiusura, esclusi i festivi della borsa (indici)."""
    p = os.path.join(CACHE, f"d1_{strumento}_{feed}.pkl")
    if os.path.exists(p): return pd.read_pickle(p)
    cfg = STRUMENTI[strumento]; m1 = carica(strumento, feed)
    fest = festivi(cfg["cal"]) if cfg["cal"] else set()
    date = pd.Series(m1["loc"].dt.normalize().unique())
    date = date[(date.dt.weekday < 5) & ~date.dt.date.isin(fest)].reset_index(drop=True)
    hh, mm = map(int, cfg["chiude"].split(":"))
    # mezze sedute (LSE 24 e 31/12 alle 12:30; NYSE elenco ufficiale alle 13:00): chiusura anticipata
    ant = {}
    if cfg["cal"] == "ENG":
        # LSE: mezza seduta l'ultimo giorno lavorativo prima di Natale e prima di Capodanno (24 e 31/12, o il venerdì prima)
        for y in range(2016, 2027):
            for g in (24, 31):
                x = pd.Timestamp(y, 12, g)
                while x.weekday() >= 5: x -= pd.Timedelta(days=1)
                ant[x.date()] = (12, 30)
    if cfg["cal"] == "NYSE":
        ant = {pd.Timestamp(x).date(): (13, 0) for x in NYSE_ANTICIPATE}
    ore = [dl + pd.Timedelta(hours=ant.get(dl.date(), (hh, mm))[0], minutes=ant.get(dl.date(), (hh, mm))[1]) for dl in date]
    C, ts_c = prezzo_alle(m1, ore)
    d = pd.DataFrame({"data": date.dt.date, "dl": date, "C": C, "ts_C": ts_c})
    if cfg["apre"]:
        ah, am = map(int, cfg["apre"].split(":"))
        d["O"] = apertura_alle(m1, date + pd.Timedelta(hours=ah, minutes=am))
    d = d.dropna(subset=["C"]).reset_index(drop=True)
    d["r"] = np.log(d.C / d.C.shift())
    d["sigma"] = d.r.rolling(20, min_periods=20).std().shift(1)
    d["z"] = d.r / d.sigma
    d["anno"] = d.dl.dt.year; d["dow"] = d.dl.dt.weekday; d["mese"] = d.dl.dt.to_period("M")
    d.to_pickle(p)
    return d

def tabella_spread(strumento):
    """Spread FTMO 2026 (mediana del minimo del minuto) per ora server, in unità di prezzo."""
    f = STRUMENTI[strumento]["ftmo_spread"]
    if f is None: return None
    for nome in ["SPREAD_mediana_per_ora_server.csv", "SPREAD_altri_strumenti_ultimo_anno.csv"]:
        base = os.path.join(QUI, "..", "f0", "risultati", nome) if nome.startswith("SPREAD_mediana") else os.path.join(QUI, "risultati", nome)
        t = pd.read_csv(base, sep=";", decimal=",")
        t = t[t.file == f]
        if len(t):
            r = t.sort_values("anno").iloc[-1]
            v = np.array([r.get(f"h{h:02d}", np.nan) for h in range(24)], float)
            v[~np.isfinite(v)] = np.nanmax(v)
            return v
    return None

def costo_trade(strumento, prezzo, ora_server_ingresso, notti, scenario="base"):
    """Costo di un round-trip in unità di prezzo: spread una volta (×1,5 nello stress) + commissione 2 lati
    + swap × notti di calendario (+0,5×spread per ordine a mercato nello stress)."""
    cfg = STRUMENTI[strumento]; c = COSTI[cfg["tipo"]]; tab = tabella_spread(strumento)
    if tab is None: return np.nan
    sp = tab[int(ora_server_ingresso) % 24]
    if scenario == "stress":
        return 1.5 * sp + 2 * 0.5 * sp + 2 * c["comm"] / 100 * prezzo + notti * c["swap_stress"] / 100 * prezzo
    return sp + 2 * c["comm"] / 100 * prezzo + notti * c["swap_base"] / 100 * prezzo

def t_cluster(x, gruppi):
    """t della media con errore raggruppato (CR1)."""
    x = np.asarray(x, float); n = len(x)
    if n < 3: return np.nan
    mu = x.mean(); dev = pd.Series(x - mu).groupby(np.asarray(gruppi)).sum().to_numpy(); G = len(dev)
    se = np.sqrt((dev ** 2).sum()) / n * np.sqrt(G / (G - 1)) if G > 1 else np.nan
    return mu / se if se > 0 else np.nan

def p_placebo(media_evento, pool, n, nrep=2000, seed=0):
    """p bilaterale: quota di medie di n estrazioni casuali dal pool lontane dalla media del pool almeno quanto l'evento."""
    pool = np.asarray(pool, float); pool = pool[np.isfinite(pool)]
    if len(pool) < 10 or n < 2: return np.nan
    rng = np.random.default_rng(seed)
    m = pool[rng.integers(0, len(pool), (nrep, n))].mean(axis=1)
    c = pool.mean()
    return float((1 + (np.abs(m - c) >= abs(media_evento - c)).sum()) / (1 + nrep))

def bh(pvals, q=0.10):
    p = np.asarray(pvals, float); m = np.isfinite(p).sum(); ordine = np.argsort(np.where(np.isfinite(p), p, np.inf))
    ok = np.zeros(len(p), bool); soglia = 0
    for i, j in enumerate(ordine[:m], 1):
        if p[j] <= i / m * q: soglia = i
    ok[ordine[:soglia]] = True
    return ok
