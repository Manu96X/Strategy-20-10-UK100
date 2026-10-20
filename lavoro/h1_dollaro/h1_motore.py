# -*- coding: utf-8 -*-
"""
Motore di H1 (PROTOCOLLO_H1.md, commit 854fac8 del 20/10/2026, prima dei risultati).
Segnale: S(d) = media degli z alle 16:00 NY di XAU e XAG (Pepperstone). Bersaglio: paniere del dollaro sulle 6 coppie
forex FTMO. Finestre W1 (16:00 NY d -> 16:00 NY d+1) e W2 (08:20 NY d+1 -> 16:00 NY d+1).
Definizioni identiche a famiglia_F.py dell'event study (prezzo = close dell'ultima barra che inizia prima dell'istante,
entro 15 minuti; 60 minuti nei giorni a barre H1; sigma sugli ultimi 20 rendimenti validi fino a d incluso).
"""
import os
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

NY, ATENE = ZoneInfo("America/New_York"), ZoneInfo("Europe/Athens")
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", ".."))
DIR = {"scoperta": "/home/user/dati_h1/scoperta", "validazione_2024": "/home/user/dati_h1/validazione_2024"}
CACHE = "/tmp/claude-0/-home-user-Strategy-20-10-UK100/3f32bb43-76e4-56e7-9055-9f1cda27903e/scratchpad/cache_h1"

# verso "dollaro forte": -1 per XXXUSD, +1 per USDXXX
COPPIE = {"EURUSD": -1, "GBPUSD": -1, "AUDUSD": -1, "USDJPY": +1, "USDCHF": +1, "USDCAD": +1}
PIP = {k: (0.01 if k == "USDJPY" else 0.0001) for k in COPPIE}
FILE = {**{k: f"{k} m1 FTMO" for k in COPPIE}, "XAU": "XAU-USD Pepperstone m1", "XAG": "XAG-USD Pepperstone m1",
        "USDX": "USDX pepperstone m1", "XAU_FTMO": "XAU-USD FTMO m1", "XAG_FTMO": "XAG-USD FTMO m1"}
COMM_RT_USD = 5.0          # 2,50 $ per lotto per lato (dossier FTMO, misurato su EURUSD e USDJPY)
LOTTO = 100000.0
SPREAD_MIN_PIP = 0.1
ORA_SRV = {"08:20": 15, "15:59": 22}   # ora server (NY+7, tabella costi 2025-26) degli ordini


# ---------------------------------------------------------------- costi
def tabella_spread():
    t = pd.read_csv(os.path.join(QUI, "risultati", "SPREAD_FX_FTMO_per_ora.csv"), sep=";", decimal=",")
    return {(r.coppia, int(r.h)): max(float(r.p75_pip), SPREAD_MIN_PIP) for r in t.itertuples()}

def swap_frazione():
    """Swap per notte in frazione del nozionale (long, short) dalla specifica FTMO (punti x valore del punto / nozionale)."""
    s = pd.read_csv(os.path.join(REPO, "specifiche_simboli.csv"), sep=";", skiprows=1)
    s = s.set_index("simbolo")
    out = {}
    for k in COPPIE:
        r = s.loc[k]
        v = float(r.valore_1_punto_1_lotto); noz = float(r.nozionale_1_lotto)
        out[k] = (float(r.swap_long) * v / noz, float(r.swap_short) * v / noz)
    return out


# ---------------------------------------------------------------- dati
def carica(chiave, dataset, da="2016.11.01"):
    os.makedirs(CACHE, exist_ok=True)
    pk = os.path.join(CACHE, f"{chiave}_{dataset}_{da}.pkl")
    if os.path.exists(pk): return pd.read_pickle(pk)
    raw = pd.read_csv(os.path.join(DIR[dataset], FILE[chiave] + ".csv"), sep="\t", dtype=str, usecols=[0, 1, 2, 5])
    raw.columns = ["d", "t", "o", "c"]
    raw = raw[raw.d >= da]
    df = pd.DataFrame({"ts": pd.to_datetime(raw.d + " " + raw.t, format="%Y.%m.%d %H:%M:%S").values,
                       "o": raw.o.astype(float).values, "c": raw.c.astype(float).values})
    assert df.ts.is_monotonic_increasing
    # passo modale (minuti) del giorno server: 60 = giorno a barre H1
    giorno = df.ts.dt.normalize()
    passo = df.ts.diff().dt.total_seconds().div(60)
    moda = passo.groupby(giorno).agg(lambda s: s.mode().iloc[0] if s.notna().any() else np.nan)
    df["passo"] = giorno.map(moda).values
    df.to_pickle(pk)
    return df

def regime_ftmo_fx(date):
    """'EU' (server = ora di Atene) fino al 2020, 'NY7' dal 2021. Flag 'incerto': giorni 2020 in cui i due fusi differiscono."""
    date = pd.DatetimeIndex(date)
    reg = np.where(date < pd.Timestamp("2021-01-01"), "EU", "NY7")
    return reg

def istanti_server(date, hh, mm, regime):
    """Istante hh:mm di New York nei giorni 'date', convertito in ora server secondo il regime ('EU' o 'NY7' per giorno)."""
    date = pd.DatetimeIndex(date).normalize()
    ny_naive = date + pd.Timedelta(hours=hh, minutes=mm)
    ny7 = ny_naive + pd.Timedelta(hours=7)
    eu = ny_naive.tz_localize(NY).tz_convert(ATENE).tz_localize(None)
    reg = np.asarray(regime) if not isinstance(regime, str) else np.full(len(date), regime)
    return pd.DatetimeIndex(np.where(reg == "EU", eu.values, ny7.values)), np.asarray(eu.values != ny7.values)

def prezzo_alle(df, T, robusto=False):
    """close dell'ultima barra che inizia prima di T: entro 15 minuti, o 60 nei giorni a barre H1.
    robusto=True: mediana degli ultimi 5 close (solo come controllo descrittivo)."""
    t = df.ts.values; q = np.asarray(T, dtype="datetime64[ns]")
    k = np.searchsorted(t, q, side="left") - 1
    kc = np.clip(k, 0, None)
    dt = (q - t[kc]) / np.timedelta64(1, "m")
    tol = np.where(df.passo.values[kc] >= 60, 60, 15)
    ok = (k >= 0) & (dt <= tol)
    if robusto:
        c = df.c.values
        idx = np.clip(kc[:, None] - np.arange(5)[None, :], 0, None)
        px = np.median(c[idx], axis=1)
    else:
        px = df.c.values[kc]
    return np.where(ok, px, np.nan)

def apertura_alle(df, T):
    """open della prima barra che inizia a T o dopo, entro 15 minuti."""
    t = df.ts.values; q = np.asarray(T, dtype="datetime64[ns]")
    k = np.searchsorted(t, q, side="left"); kc = np.clip(k, None, len(t) - 1)
    ok = (k < len(t)) & ((t[kc] - q) / np.timedelta64(1, "m") <= 15)
    return np.where(ok, df.o.values[kc], np.nan)

def serie(chiave, dataset, inizio, fine, regime, con_0820=False, robusto=False):
    df = carica(chiave, dataset)
    date = pd.date_range(inizio, fine, freq="D"); date = date[date.weekday < 5]
    reg = regime(date) if callable(regime) else regime
    T16, diverso = istanti_server(date, 16, 0, reg)
    d = pd.DataFrame({"dt": date, "P": prezzo_alle(df, T16, robusto), "reg": reg, "fusi_diversi": diverso})
    if con_0820:
        T08, _ = istanti_server(date, 8, 20, reg)
        d["O"] = apertura_alle(df, T08)
    d = d.dropna(subset=["P"]).set_index("dt", drop=False)
    gap = (d.dt - d.dt.shift()).dt.days
    d["r"] = np.where(gap <= 4, np.log(d.P / d.P.shift()), np.nan)
    rs = d.r.dropna().rolling(20, min_periods=20).std()
    d["sig"] = rs.reindex(d.index).ffill()
    d["z"] = d.r / d.sig
    return d

def tabella_giornaliera(dataset, inizio, fine, robusto=False):
    """Una riga per giorno d (righe comuni alle 6 coppie): segnale, paniere, finestre W1/W2 sul giorno d+1."""
    pep = "NY7"
    met = {m: serie(m, dataset, inizio, fine, pep) for m in ("XAU", "XAG")}
    fx = {k: serie(k, dataset, inizio, fine, regime_ftmo_fx, con_0820=True, robusto=robusto) for k in COPPIE}
    comuni = None
    for k, d in fx.items():
        comuni = d.index if comuni is None else comuni.intersection(d.index)
    B = pd.DataFrame(index=comuni); B["dt"] = comuni
    for k, d in fx.items():
        B[f"P_{k}"] = d.P.reindex(comuni); B[f"O_{k}"] = d.O.reindex(comuni)
    B["fusi_diversi"] = fx["EURUSD"].fusi_diversi.reindex(comuni).values
    gap = (B.dt - B.dt.shift()).dt.days
    rb = sum(s * np.log(B[f"P_{k}"] / B[f"P_{k}"].shift()) for k, s in COPPIE.items()) / len(COPPIE)
    B["rB"] = np.where(gap <= 4, rb, np.nan)
    rs = B.rB.dropna().rolling(20, min_periods=20).std()
    B["sigB"] = rs.reindex(B.index).ffill()
    for k, s in COPPIE.items():   # sigma della singola coppia (descrittivo per coppia)
        rk = np.where(gap <= 4, np.log(B[f"P_{k}"] / B[f"P_{k}"].shift()), np.nan)
        B[f"sig_{k}"] = pd.Series(rk, index=B.index).dropna().rolling(20, min_periods=20).std().reindex(B.index).ffill()
    # giorno successivo (riga comune successiva entro 4 giorni)
    g1 = (B.dt.shift(-1) - B.dt).dt.days
    ok1 = (g1 <= 4).to_numpy()
    B["dt1"] = B.dt.shift(-1)
    for k in COPPIE:
        B[f"P1_{k}"] = np.where(ok1, B[f"P_{k}"].shift(-1), np.nan)
        B[f"O1_{k}"] = np.where(ok1, B[f"O_{k}"].shift(-1), np.nan)
    B["fusi_diversi1"] = B.fusi_diversi.shift(-1).fillna(False).astype(bool)
    B["W1"] = sum(s * np.log(B[f"P1_{k}"] / B[f"P_{k}"]) for k, s in COPPIE.items()) / len(COPPIE)
    B["W2"] = sum(s * np.log(B[f"P1_{k}"] / B[f"O1_{k}"]) for k, s in COPPIE.items()) / len(COPPIE)
    B["y1"] = B.W1 / B.sigB; B["y2"] = B.W2 / B.sigB
    B["zXAU"] = met["XAU"].z.reindex(B.index); B["zXAG"] = met["XAG"].z.reindex(B.index)
    B["S"] = (B.zXAU + B.zXAG) / 2
    return B

def serie_usdx(dataset, inizio, fine):
    d = serie("USDX", dataset, inizio, fine, "NY7")
    g1 = (d.dt.shift(-1) - d.dt).dt.days
    d["dt1"] = d.dt.shift(-1)
    d["y1"] = np.where(g1 <= 4, np.log(d.P.shift(-1) / d.P), np.nan) / d.sig
    return d


# ---------------------------------------------------------------- statistiche
def ols(x, y):
    n = len(x); X = np.column_stack([np.ones(n), x])
    XtXi = np.linalg.inv(X.T @ X); beta = XtXi @ X.T @ y
    e = y - X @ beta
    V = XtXi @ ((X * (e ** 2)[:, None]).T @ X) @ XtXi * n / (n - 2)
    return float(beta[1]), float(beta[1] / np.sqrt(V[1, 1])), e

def p_perm_unilaterale(x, y, nrep=100_000, seed=20261020):
    """p unilaterale per b < 0: quota delle permutazioni di x con pendenza <= osservata."""
    xc = x - x.mean(); yc = y - y.mean(); sxx = (xc ** 2).sum(); b = (xc @ yc) / sxx
    rng = np.random.default_rng(seed); cont = 0; fatti = 0
    while fatti < nrep:
        m = min(5000, nrep - fatti)
        perm = np.argsort(rng.random((m, len(x))), axis=1)
        cont += int(((xc[perm] @ yc) / sxx <= b).sum()); fatti += m
    return (1 + cont) / (1 + nrep)

def costo_coppie(B, dir_coppia, ingresso, uscita, scenario, spread, swap=None):
    """Costo per coppia in frazione del prezzo (positivo = costo). dir_coppia: DataFrame +1 compra la coppia, -1 vende.
    ingresso/uscita: 'W1' (15:59 NY -> 15:59 NY) o 'W2' (08:20 NY -> 15:59 NY)."""
    h_in = ORA_SRV["15:59"] if ingresso == "W1" else ORA_SRV["08:20"]; h_out = ORA_SRV["15:59"]
    tot = {}
    for k in COPPIE:
        Pin = B[f"P_{k}"] if ingresso == "W1" else B[f"O1_{k}"]
        dk = dir_coppia[k].to_numpy()
        sp = np.where(dk > 0, spread[(k, h_in)], spread[(k, h_out)])
        if scenario == "stress": sp = 1.5 * sp + 0.2
        c = sp * PIP[k] / Pin
        noz = LOTTO * (Pin if k.endswith("USD") else 1.0)
        c = c + COMM_RT_USD / noz
        if swap is not None:
            sl, ss = swap[k]
            sw = np.where(dk > 0, sl, ss) * np.where(B.dt.dt.weekday.to_numpy() == 2, 3, 1)
            if scenario == "stress": sw = np.where(sw < 0, 1.5 * sw, sw)
            c = c - sw
        tot[k] = np.where(dk != 0, c, 0.0)
    return pd.DataFrame(tot, index=B.index)

def strategia(B, segnale, finestra, scenario, spread, swap):
    """Posizione sul dollaro = -segno(segnale); ritorna z netti per giorno (paniere a pesi uguali)."""
    pos = -np.sign(segnale.to_numpy())
    dirc = pd.DataFrame({k: pos * s for k, s in COPPIE.items()}, index=B.index)
    lordo = pos * B[finestra].to_numpy()
    if finestra == "W1":
        c = costo_coppie(B, dirc, "W1", "W1", scenario, spread, swap)
    else:
        c = costo_coppie(B, dirc, "W2", "W2", scenario, spread, None)
    costo = c.mean(axis=1).to_numpy()
    return (lordo - costo) / B.sigB.to_numpy(), lordo / B.sigB.to_numpy(), costo / B.sigB.to_numpy()

def t_media(v):
    v = v[np.isfinite(v)]
    return float(v.mean()), float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))), int(len(v))
