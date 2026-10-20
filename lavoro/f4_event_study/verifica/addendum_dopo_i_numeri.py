# -*- coding: utf-8 -*-
"""ADDENDUM «DOPO I NUMERI» (20/10/2026) — non cambia la classificazione pre-registrata, la precisa.
1) Risoluzione del p: con 2.000 permutazioni il p minimo è 0,0005 > soglia BH di rango 1 (0,10/242 = 0,000413).
   Ricalcolo il p di XAU->USDX e XAG->USDX con 200.000 permutazioni (codice mio, indipendente da famiglia_F.py).
2) Pre-FOMC (B1) e pre-festivo (C4) sugli indici: ricalcolo indipendente e test di Welch (varianza degli eventi
   diversa da quella del pool), anche raggruppando i 4 indici per data (un valore medio per evento).
Solo dati sigillati < 2024."""
import sys, os
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import eventi_comune as EC
NY = ZoneInfo("America/New_York")
rng = np.random.default_rng(424242)

def px16(s, feed):
    m1 = EC.carica(s, feed); tz = ZoneInfo(EC.STRUMENTI[s]["tz"])
    giorni = pd.bdate_range("2017-06-01", "2023-12-29")
    ist = [(g + pd.Timedelta(hours=16)).tz_localize(NY).tz_convert(tz).tz_localize(None) for g in giorni]
    p, _ = EC.prezzo_alle(m1, ist)
    return pd.Series(p, index=giorni)

# 1) lead-lag metalli -> dollaro
P = pd.DataFrame({s: px16(s, EC.FEED_INFERENZA[s]) for s in ["XAU", "XAG", "USDX"]}).dropna()
gap = P.index.to_series().diff().dt.days
r = np.log(P / P.shift()); r[gap > 4] = np.nan
z = r / r.rolling(20, min_periods=20).std()
for pred in ["XAU", "XAG"]:
    d = pd.DataFrame({"x": z[pred], "y": z["USDX"].shift(-1)}).dropna()
    x, y = d.x.to_numpy(), d.y.to_numpy(); xc = x - x.mean()
    b = (xc * (y - y.mean())).sum() / (xc ** 2).sum()
    cnt = 0; N = 200000
    for blk in range(0, N, 20000):
        perm = np.array([rng.permutation(x) for _ in range(20000)])
        pc = perm - perm.mean(axis=1, keepdims=True)
        bp = (pc * (y - y.mean())).sum(axis=1) / (pc ** 2).sum(axis=1)
        cnt += (np.abs(bp) >= abs(b)).sum()
    p = (1 + cnt) / (1 + N)
    print(f"{pred}->USDX: n {len(d)}, pendenza {b:+.4f}, p permutazione (200.000) = {p:.6f}  | soglia BH rango 1 = {0.10/242:.6f}, rango 2 = {2*0.10/242:.6f}")

# 2) pre-FOMC e pre-festivi sugli indici (Welch contro tutte le finestre della stessa forma)
def welch(e, pool):
    e, pool = np.asarray(e), np.asarray(pool)
    t = (e.mean() - pool.mean()) / np.sqrt(e.var(ddof=1) / len(e) + pool.var(ddof=1) / len(pool))
    from scipy import stats
    return t, 2 * stats.t.sf(abs(t), df=len(e) - 1)
fomc = [pd.Timestamp(f) for f in EC.FOMC]
righe, per_data = [], {}
for s in ["US500", "US100", "GER40", "UK100"]:
    fk = EC.FEED_INFERENZA[s]; m1 = EC.carica(s, fk); tz = ZoneInfo(EC.STRUMENTI[s]["tz"])
    d1 = EC.giornaliero(s, fk); d1["sig_in"] = d1.r.rolling(20, min_periods=20).std()
    sig = pd.Series(d1.sig_in.values, index=d1.dl)
    gg = list(d1.dl)
    # finestre 14:00 NY giorno g -> 13:55 NY giorno di trading successivo, per tutti i g
    a = [(g + pd.Timedelta(hours=14)).tz_localize(NY).tz_convert(tz).tz_localize(None) for g in gg[:-1]]
    bb = [(g + pd.Timedelta(hours=13, minutes=55)).tz_localize(NY).tz_convert(tz).tz_localize(None) for g in gg[1:]]
    pa, _ = EC.prezzo_alle(m1, a); pb, _ = EC.prezzo_alle(m1, bb)
    w = pd.DataFrame({"g": gg[:-1], "g2": gg[1:], "z": np.log(pb / pa) / sig.reindex(gg[:-1]).values}).dropna()
    ev = w[w.g2.isin(fomc)]; pool = w[~w.g2.isin(fomc) & ~w.g.isin(fomc)]
    t, p = welch(ev.z, pool.z)
    righe.append(dict(test="B1 pre-FOMC", strumento=s, n=len(ev), media_z=ev.z.mean(), anomala=ev.z.mean() - pool.z.mean(), t_welch=t, p_welch=p))
    for _, e in ev.iterrows(): per_data.setdefault(("B1", e.g2), []).append(e.z - pool.z.mean())
    # pre-festivo: chiusura giorno prima -> chiusura del giorno pre-festivo
    fest = EC.festivi(EC.STRUMENTI[s]["cal"])
    d1["z1"] = d1.r / d1.sig_in.shift(1)
    pre = [i for i in range(1, len(d1)) if (lambda nx: nx in fest)((d1.dl.iat[i] + pd.offsets.BDay(1)).date())]
    zz = d1.z1.iloc[pre].dropna(); poolc = d1.z1.dropna()
    t, p = welch(zz, poolc)
    righe.append(dict(test="C4 pre-festivo", strumento=s, n=len(zz), media_z=zz.mean(), anomala=zz.mean() - poolc.mean(), t_welch=t, p_welch=p))
    for i in pre:
        if np.isfinite(d1.z1.iat[i]): per_data.setdefault(("C4", d1.dl.iat[i]), []).append(d1.z1.iat[i] - poolc.mean())
R = pd.DataFrame(righe); pd.set_option("display.width", 200); print(R.round(4).to_string(index=False))
for fam in ["B1", "C4"]:
    v = np.array([np.mean(x) for (f, d), x in per_data.items() if f == fam])
    from scipy import stats
    t = v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))
    print(f"{fam} paniere dei 4 indici, un valore per data: n date {len(v)}, anomala media {v.mean():+.3f} z, t {t:.2f}, p {2*stats.t.sf(abs(t), len(v)-1):.4f}")
