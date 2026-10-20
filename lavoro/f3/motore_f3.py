# -*- coding: utf-8 -*-
"""
F3 — motore di backtest della strategia «FTSE 100 — Monday dip + RSI»,
secondo `lavoro/f2/PROTOCOLLO_F2_BOZZA.md` (confermato da Manu il 20/10/2026).

Simulazione (protocollo §3):
- prezzi M1 BID del feed; ask = bid + spread FTMO 2026 per ora server (× moltiplicatore dello scenario);
- segnale su barra (di sessione o CFD) CHIUSA; ingresso all'apertura del primo M1 con ts >= fine nominale
  della barra (se il primo M1 arriva oltre 15 minuti dopo: niente trade);
- SL = fill - d, TP = fill + 2d, d = m × ATR14 della barra segnale (riancorati al fill);
- uscite sul bid M1 dall'M1 d'ingresso compreso: SL se low <= SL (prezzo = min(open, SL - slippage)),
  TP se high >= TP (prezzo = TP); SL e TP nello stesso minuto -> prima lo SL (opzione sl_prima=False: prima il TP);
- uscita a tempo all'apertura del primo M1 con ts >= scadenza (bid - extra mercato);
- chiusure >= 2 ore (weekend, festivi, giorni senza dati): uscita forzata 15 minuti prima dell'ultima
  quotazione della giornata che le precede; niente ingressi nelle 2 ore prima della chiusura;
- swap: notti (cambi di data server) × swap dello scenario, triplo la notte del mercoledì;
- R = (uscita - fill - swap) / d.
"""
import os, sys
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo
import holidays

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comune"))
import barre

NY = ZoneInfo("America/New_York")
PRAGA = ZoneInfo("Europe/Prague")
MIN = 60 * 10**9          # un minuto in ns
ORA = 60 * MIN

SCENARI = {
    "lordo":  dict(spread=0.0, slip=0.0, mkt=0.0, swap=0.0),
    "base":   dict(spread=1.0, slip=0.8, mkt=0.0, swap=0.5),
    "stress": dict(spread=1.5, slip=2.0, mkt=0.5, swap=2.0),
}

SIMBOLI = {
    "UK100": dict(tz="Europe/London", apre="08:00", chiude="16:30", cal="ENG", spread_da="UK100 FTMO m1",
                  feed={"PEP": ("UK100 Pepperstone m1", "2017-06-06"), "FTMO": ("UK100 FTMO m1", "2021-09-14")}),
    "GER40": dict(tz="Europe/Berlin", apre="09:00", chiude="17:30", cal="XETRA", spread_da="GER40 FTMO m1",
                  feed={"PEP": ("GER40 Pepperstone m1", "2020-06-11"), "FTMO": ("GER40 FTMO m1", "2021-12-28")}),
    "US500": dict(tz="America/New_York", apre="09:30", chiude="16:00", cal="NYSE", spread_da="US500 m1 - FTMO",
                  feed={"PEP": ("US500 m1 - Pepperstone", "2020-07-13"), "FTMO": ("US500 m1 - FTMO", "2021-09-14")}),
    "US100": dict(tz="America/New_York", apre="09:30", chiude="16:00", cal="NYSE", spread_da="US100 m1 - FTMO",
                  feed={"PEP": ("NAS100 m1 - FTPepperstone", "2017-06-09"), "FTMO": ("US100 m1 - FTMO", "2021-09-14")}),
}

def festivi_borsa(cal, anni):
    """Giorni di chiusura della borsa cash (date locali)."""
    if cal == "ENG":   # LSE = bank holiday di Inghilterra (coincidono con le chiusure FTMO 2022-2025, F0)
        return set(holidays.UK(subdiv="ENG", years=anni).keys())
    if cal == "NYSE":
        return set(holidays.NYSE(years=anni).keys())
    if cal == "XETRA":  # Xetra: 1/1, venerdì santo, lunedì dell'Angelo, 1/5, 24-26/12, 31/12
        out = set()
        for y in anni:
            de = holidays.Germany(years=y)
            for d, n in de.items():
                if n in ("Karfreitag", "Ostermontag", "Good Friday", "Easter Monday"): out.add(d)
            for m, g in [(1, 1), (5, 1), (12, 24), (12, 25), (12, 26), (12, 31)]:
                out.add(pd.Timestamp(y, m, g).date())
        return out
    raise ValueError(cal)

def locale_a_server(loc_naive, tz):
    """ora locale di borsa (naive) -> ora server (naive) = New York + 7."""
    s = pd.Series(pd.to_datetime(loc_naive))
    ny = s.dt.tz_localize(ZoneInfo(tz), ambiguous="NaT", nonexistent="NaT").dt.tz_convert(NY).dt.tz_localize(None)
    return ny + pd.Timedelta(hours=7)

def tabella_spread(file_ftmo, anno=2026):
    t = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "f0", "risultati",
                                 "SPREAD_mediana_per_ora_server.csv"), sep=";", decimal=",")
    r = t[(t.file == file_ftmo) & (t.anno == anno)].iloc[0]
    v = np.array([r.get(f"h{h:02d}", np.nan) for h in range(24)], float)
    for h in range(24):   # ore senza quotazioni FTMO (es. 00): il massimo delle ore vicine
        if not np.isfinite(v[h]):
            vic = [v[(h - 1) % 24], v[(h + 1) % 24]]
            v[h] = np.nanmax(vic) if np.isfinite(vic).any() else np.nanmax(v)
    return v

class Feed:
    """Serie M1 di un feed + calendario delle chiusure (in date server)."""
    def __init__(self, path, inizio, festivi_server):
        m1 = barre.carica_m1(path, inizio)
        self.m1 = m1
        self.ts = m1.ts.values.astype("datetime64[ns]").astype(np.int64)
        self.o, self.h, self.l, self.c = (m1[k].to_numpy(float) for k in "ohlc")
        self.ora = m1.ts.dt.hour.to_numpy()
        sd = m1.ts.dt.normalize()
        self.data_srv = sd.values.astype("datetime64[D]")
        # giornate server di trading = con dati, feriali, non festive
        g = pd.DataFrame({"d": sd, "ts": m1.ts}).groupby("d").ts.agg(["min", "max"])
        g = g[[d.weekday() < 5 and d.date() not in festivi_server for d in g.index]]
        self.giorni = g.index.values.astype("datetime64[D]")
        self.ultima = g["max"].values.astype("datetime64[ns]").astype(np.int64)
        gap = np.diff(self.giorni).astype(int)
        self.chiusura_dopo = np.append(gap > 1, True)          # dopo questo giorno c'è una chiusura
        # per ogni giorno di trading: prossima chiusura (ultima quotazione del giorno che la precede)
        prox = np.empty(len(self.giorni), np.int64); cur = self.ultima[-1]
        for i in range(len(self.giorni) - 1, -1, -1):
            if self.chiusura_dopo[i]: cur = self.ultima[i]
            prox[i] = cur
        self.prossima_chiusura = prox
        # per ogni M1: indice del suo giorno di trading (-1 se il giorno non è di trading) e numero del giorno
        self.giorno_int = self.data_srv.astype(np.int64)                 # giorni dall'1/1/1970 (giovedì)
        gi = self.giorni.astype(np.int64)
        k = np.searchsorted(gi, self.giorno_int)
        k = np.clip(k, 0, len(gi) - 1)
        self.k_giorno = np.where(gi[k] == self.giorno_int, k, -1)

    def info_giorno(self, i):
        """indice del giorno di trading dell'M1 i (None se festivo / non di trading)."""
        k = self.k_giorno[i]
        return None if k < 0 else int(k)

NYSE_ANTICIPATE = ["2017-07-03", "2017-11-24", "2018-07-03", "2018-11-23", "2018-12-24", "2019-07-03", "2019-11-29",
                   "2019-12-24", "2020-11-27", "2020-12-24", "2021-11-26", "2022-11-25", "2023-07-03", "2023-11-24",
                   "2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03", "2025-11-28", "2025-12-24"]

def chiusure_anticipate(cal, anni, festivi_loc):
    """Giorni di chiusura anticipata della borsa cash -> minuto locale di chiusura (addendum 20/10/2026).
    LSE: 24/12 e 31/12 feriali alle 12:30. NYSE: elenco ufficiale alle 13:00. Xetra: 24 e 31/12 sono festivi."""
    out = {}
    if cal == "ENG":
        for y in anni:
            for g in (24, 31):
                d = pd.Timestamp(y, 12, g).date()
                if d.weekday() < 5 and d not in festivi_loc: out[d] = 12 * 60 + 30
    if cal == "NYSE":
        for x in NYSE_ANTICIPATE: out[pd.Timestamp(x).date()] = 13 * 60
    return out

def barre_sessione(feed, tz, apre, chiude, festivi_loc, anticipate=None):
    """Barre H1 della sessione cash ancorate all'apertura (es. 09:30 -> 09:30-10:30 ...); ultima barra corta.
    anticipate: {data locale: minuto di chiusura} per i giorni di chiusura anticipata."""
    loc = barre.ora_locale(feed.m1.ts, tz)
    ah, am = map(int, apre.split(":")); ch, cm = map(int, chiude.split(":"))
    mins = loc.dt.hour * 60 + loc.dt.minute
    a0, c0 = ah * 60 + am, ch * 60 + cm
    data_loc = loc.dt.normalize()
    chiude_g = pd.Series(c0, index=loc.index)
    if anticipate:
        chiude_g = data_loc.dt.date.map(lambda d: anticipate.get(d, c0)).fillna(c0).astype(int)
    sel = (mins >= a0) & (mins < chiude_g) & loc.notna()
    sel &= data_loc.dt.weekday < 5
    sel &= ~data_loc.dt.date.isin(festivi_loc)
    x = feed.m1[sel].copy()
    x["dl"] = data_loc[sel]; x["k"] = ((mins[sel] - a0) // 60).astype(int)
    g = x.groupby(["dl", "k"], sort=True)
    b = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "n_m1": g.size()}).reset_index()
    c_b = b.dl.dt.date.map(lambda d: (anticipate or {}).get(d, c0)).astype(int)
    fine_loc = b.dl + pd.to_timedelta(np.minimum(a0 + (b.k + 1) * 60, c_b), unit="m")
    b["fine_srv"] = locale_a_server(fine_loc, tz).values
    b["data"] = b.dl.dt.date
    b["dow"] = b.dl.dt.weekday
    b["anno"] = b.dl.dt.year
    return b.dropna(subset=["fine_srv"]).reset_index(drop=True)

def barre_cfd(feed, festivi_server):
    x = feed.m1.copy(); x["k"] = x.ts.dt.floor("h")
    g = x.groupby("k", sort=True)
    b = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "n_m1": g.size()}).reset_index()
    b["fine_srv"] = b.k + pd.Timedelta(hours=1)
    b["dl"] = b.k.dt.normalize(); b["data"] = b.dl.dt.date; b["dow"] = b.dl.dt.weekday
    b["anno"] = b.dl.dt.year; b["k"] = b.k.dt.hour            # "k" = ora server (posizione nella giornata)
    b = b[(b.dow < 5) & ~b.data.isin(festivi_server)].reset_index(drop=True)
    return b

def indicatori(b, warmup=300):
    b = b.copy()
    b["rsi"] = barre.rsi_wilder(b.c.to_numpy(), 14)
    b["atr"] = barre.atr_wilder(b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy(), 14)
    b["sma"] = barre.sma(b.c.to_numpy(), 40)
    b["valida"] = (np.arange(len(b)) >= warmup) & b[["rsi", "atr", "sma"]].notna().all(axis=1)
    return b

GAP_PROTOCOLLO = True   # addendum 20/10/2026: stop in gap = min(open, SL) - slippage, come scritto nel protocollo §3

def simula(feed, i0, t_regola, d, tab_spread, sc, sl_prima=True):
    """Un trade long dall'M1 i0. Ritorna dict o None (non simulabile)."""
    ts = feed.ts
    k = feed.info_giorno(i0)
    if k is None: return None
    chius = feed.prossima_chiusura[k]
    if feed.chiusura_dopo[k] and ts[i0] >= feed.ultima[k] - 2 * ORA: return None   # regola delle 2 ore
    t_forz = chius - 15 * MIN
    t_exit = min(t_regola, t_forz)
    if t_exit <= ts[i0]: return None
    ie = int(np.searchsorted(ts, t_exit, "left"))
    if ie >= len(ts): return None
    sp = tab_spread[feed.ora[i0]] * sc["spread"]
    fill = feed.o[i0] + sp + sc["mkt"]
    SL, TP = fill - d, fill + 2 * d
    seg_l, seg_h = feed.l[i0:ie], feed.h[i0:ie]
    a = np.flatnonzero(seg_l <= SL); b_ = np.flatnonzero(seg_h >= TP)
    jsl = a[0] if len(a) else np.inf; jtp = b_[0] if len(b_) else np.inf
    slip = 0.0
    if jsl < np.inf and (jsl < jtp or (jsl == jtp and sl_prima)):
        j = i0 + int(jsl); tipo = "SL"
        if GAP_PROTOCOLLO:
            px = min(feed.o[j], SL) - sc["slip"]; slip = sc["slip"]   # il gap oltre lo stop è movimento di prezzo
        else:                                                           # versione della prima esecuzione (prima del controllo)
            px = min(feed.o[j], SL - sc["slip"]); slip = min(SL - px, sc["slip"])
    elif jtp < np.inf:
        j = i0 + int(jtp); px = TP; tipo = "TP"
    else:
        j = ie; px = feed.o[ie] - sc["mkt"]; tipo = "TEMPO" if t_exit == t_regola else "CHIUSURA"
    de, du = feed.giorno_int[i0], feed.giorno_int[j]
    notti = 0
    for x in range(de, du):                       # una notte per ogni cambio di data server
        notti += 3 if (x + 3) % 7 == 2 else 1     # (giorno 0 = giovedì 1/1/1970): mercoledì -> triplo
    swap = notti * sc["swap"]
    R = (px - fill - swap) / d
    n_mkt = 2 if tipo in ("TEMPO", "CHIUSURA") else 1
    return dict(i0=i0, ts_in=ts[i0], ts_out=ts[j], fill=fill, sl=SL, tp=TP, px_out=px, d=d, tipo=tipo,
                spread=sp, slip=slip, notti=notti, swap=swap, R=R,
                costo_R=(sp + sc["mkt"] * n_mkt + slip + swap) / d)

def scadenza(regola_t, b, s, i0, feed):
    """Scadenza (ns) della regola d'uscita a tempo per un segnale sulla barra s."""
    ts_in = int(feed.ts[i0])
    if regola_t == "24h": return ts_in + 24 * ORA
    if regola_t == "24barre":
        if s + 24 >= len(b): return None
        return int(pd.Timestamp(b.fine_srv.iat[s + 24]).value)
    if regola_t == "sera":
        k = feed.info_giorno(i0)
        if k is None: return None
        d0 = int(feed.giorni[k].astype("datetime64[ns]").astype(np.int64))
        return min(d0 + 23 * ORA + 40 * MIN, int(feed.ultima[k]) - 15 * MIN)
    raise ValueError(regola_t)

def esiti_tutte_le_barre(feed, b, m, regola_t, tab, sc, sl_prima=True):
    """Simula un trade da OGNI barra valida (serve per segnali e placebo). Ritorna lista allineata a b (None se no)."""
    fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64)
    i0s = np.searchsorted(feed.ts, fine, "left")
    out = [None] * len(b)
    atr = b.atr.to_numpy(); val = b.valida.to_numpy()
    for s in range(len(b)):
        if not val[s]: continue
        i0 = i0s[s]
        if i0 >= len(feed.ts) or feed.ts[i0] - fine[s] > 15 * MIN: continue
        t_r = scadenza(regola_t, b, s, i0, feed)
        if t_r is None: continue
        r = simula(feed, i0, t_r, m * atr[s], tab, sc, sl_prima)
        if r is not None:
            r["s"] = s; out[s] = r
    return out

def segnali_R1(b, esiti, giorni_sett=(0,), soglia_rsi=40.0, richiedi_k0=True):
    """Primo segnale tradabile per giornata: close < apertura della giornata e RSI < soglia.
    Apertura = open della prima barra della giornata; con richiedi_k0 (barre di sessione) la prima barra
    deve essere quella d'apertura (k = 0), altrimenti la giornata è saltata."""
    tr = []
    c, rsi, val = b.c.to_numpy(), b.rsi.to_numpy(), b.valida.to_numpy()
    for (dl, dow), g in b.groupby(["dl", "dow"], sort=True):
        if dow not in giorni_sett: continue
        if richiedi_k0 and g.k.iat[0] != 0: continue
        apertura = g.o.iat[0]
        for s in g.index:
            if val[s] and c[s] < apertura and rsi[s] < soglia_rsi and esiti[s] is not None:
                tr.append(esiti[s]); break
    return tr

def segnali_R2(b, esiti, k_atr, soglia_rsi=35.0):
    tr = []; libero_da = -np.inf
    fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64)
    c, sma, atr, rsi, val = (b[x].to_numpy() for x in ("c", "sma", "atr", "rsi", "valida"))
    for s in range(len(b)):
        if not val[s] or esiti[s] is None or fine[s] < libero_da: continue
        if c[s] <= sma[s] - k_atr * atr[s] and rsi[s] < soglia_rsi:
            tr.append(esiti[s]); libero_da = esiti[s]["ts_out"]
    return tr

def giorno_ftmo(ts_ns):
    s = pd.Series(pd.to_datetime(np.asarray(ts_ns, dtype="int64")))
    return barre.ora_locale(s, "Europe/Prague").dt.date.values

def statistiche(df, nboot=100000, seed=1):
    """df: trade con colonne R, ts_in, tipo, costo_R, anno."""
    out = {"n": len(df)}
    if len(df) == 0: return out
    R = df.R.to_numpy(); n = len(R); mu = R.mean(); sd = R.std(ddof=1) if n > 1 else np.nan
    gid = pd.factorize(giorno_ftmo(df.ts_in))[0]
    dev = pd.Series(R - mu).groupby(gid).sum().to_numpy()
    G = len(dev)
    se_c = np.sqrt((dev ** 2).sum()) / n * (np.sqrt(G / (G - 1)) if G > 1 else np.nan)   # CR1 (addendum 20/10/2026)
    out.update(media=mu, sd=sd, t=mu / se_c if se_c > 0 else np.nan, t_iid=mu / (sd / np.sqrt(n)) if n > 1 else np.nan,
               n_req=(2 * sd / mu) ** 2 if mu > 0 else np.inf, win=(R > 0).mean(),
               somma=R.sum(), asimmetria=pd.Series(R).skew(), costo_R=df.costo_R.mean())
    rng = np.random.default_rng(seed); ug = np.unique(gid); somme = pd.Series(R).groupby(gid).sum().reindex(ug).to_numpy()
    cnt = pd.Series(1, index=range(n)).groupby(gid).sum().reindex(ug).to_numpy()
    bm = []
    for blocco in range(0, nboot, 5000):
        k = rng.integers(0, len(ug), (min(5000, nboot - blocco), len(ug)))
        bm.append(somme[k].sum(axis=1) / cnt[k].sum(axis=1))
    bm = np.concatenate(bm)
    out["ic95"] = (float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))); out["boot_quota_le0"] = float((bm <= 0).mean())
    eq = np.cumsum(R[np.argsort(df.ts_in.to_numpy())]); out["dd_max"] = float((np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max())
    sgn = (R[np.argsort(df.ts_in.to_numpy())] <= 0).astype(int); mx = cur = 0
    for v in sgn: cur = cur + 1 if v else 0; mx = max(mx, cur)
    out["perdite_consec"] = mx
    srt = np.sort(R)[::-1]; out["quota_top20"] = srt[:20].sum() / R.sum() if R.sum() != 0 else np.nan
    per_anno = df.groupby("anno").R.agg(["count", "mean"])
    out["anni_pos"] = float((per_anno["mean"] > 0).mean()); out["per_anno"] = per_anno
    out["mix"] = df.tipo.value_counts(normalize=True).to_dict()
    out["R_per_tipo"] = df.groupby("tipo").R.mean().to_dict()
    return out
