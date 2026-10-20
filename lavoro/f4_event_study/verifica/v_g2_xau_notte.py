# -*- coding: utf-8 -*-
"""REVISIONE AVVERSARIA di G2_XAU_notte (ricalcolo da zero). Notte = 16:00 NY del giorno di trading precedente ->
08:20 NY del giorno d; z = ln(P1/P0) / sigma (20 rendimenti fino al giorno d'ingresso incluso = sigma EC del giorno d).
Benchmark: (a) 0 (come dichiarato); (b) finestre della stessa durata (16h20) che iniziano a ogni ora intera
(placebo, stesse date); (c) il giorno 08:20 -> 16:00. Feed FTMO dal 04/01/2021."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import eventi_comune as EC

NREP = 2000

def notte(feed="PEP", t0=(16, 0), t1=(8, 20), g0=None):
    d = EC.giornaliero("XAU", feed).copy(); m1 = EC.carica("XAU", feed)
    d["dl_prev"] = d.dl.shift(1)
    p0, ts0 = EC.prezzo_alle(m1, d.dl_prev + pd.Timedelta(hours=t0[0], minutes=t0[1]))
    p1, ts1 = EC.prezzo_alle(m1, d.dl + pd.Timedelta(hours=t1[0], minutes=t1[1]))
    pg, _ = EC.prezzo_alle(m1, d.dl + pd.Timedelta(hours=16))
    d["p0"], d["ts0"], d["p1"], d["ts1"] = p0, ts0, p1, ts1
    d["zn"] = np.log(p1 / p0) / d.sigma
    d["zg"] = np.log(pg / p1) / d.sigma                      # giorno 08:20 -> 16:00 (stessa sigma)
    d["notti"] = (d.dl - d.dl_prev).dt.days
    return d.dropna(subset=["zn"]).reset_index(drop=True)

def pool_spostato(feed="PEP"):
    """Finestre di 16h20 che iniziano alle h:00 NY (h = 0..23) del giorno di trading precedente; se la fine cade nel
    weekend/pausa senza prezzo, si sposta di 48 ore (come la notte del lunedi'). Sigma = sigma EC del giorno d."""
    d = EC.giornaliero("XAU", feed).copy(); m1 = EC.carica("XAU", feed); d["dl_prev"] = d.dl.shift(1)
    d = d.dropna(subset=["sigma", "dl_prev"]); out = {}
    for h in range(24):
        s = d.dl_prev + pd.Timedelta(hours=h); e = s + pd.Timedelta(hours=16, minutes=20)
        p0, _ = EC.prezzo_alle(m1, s); p1, _ = EC.prezzo_alle(m1, e)
        p1b, _ = EC.prezzo_alle(m1, e + pd.Timedelta(hours=48))
        p1 = np.where(np.isfinite(p1), p1, p1b)
        z = np.log(p1 / p0) / d.sigma.values
        out[h] = pd.Series(z, index=d.data.values)
    return pd.DataFrame(out)

def descr(x, nome):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return dict(caso=nome, n=len(x), media=round(x.mean(), 4), t=round(x.mean() / x.std(ddof=1) * np.sqrt(len(x)), 3),
                mediana=round(np.median(x), 4), quota_pos=round((x > 0).mean(), 3))

if __name__ == "__main__":
    d = notte(); out = [descr(d.zn, "notte PEP (base)")]
    from scipy.stats import norm
    out[-1]["p_norm"] = round(2 * norm.sf(abs(out[-1]["t"])), 4)
    out.append(descr(d[d.anno != 2020].zn, "senza 2020"))
    out.append(descr(d.zn.clip(-3, 3), "winsor +-3"))
    s = d.zn.sort_values(); out.append(descr(s.iloc[16:-16], "trim 1%+1%"))
    out.append(descr(d.zg, "giorno 08:20->16:00"))
    out.append(descr(d.zn - d.zg, "notte - giorno"))
    out.append(descr(d.zn + d.zg, "close-to-close (somma)"))
    out.append(descr(d[d.notti == 1].zn, "notti feriali (1 notte)"))
    out.append(descr(d[d.notti >= 3].zn, "notte del lunedi' (weekend)"))
    # varianti d'orario (dopo i numeri): ingresso dopo il rollover delle 17:00 (niente swap)
    for t0, t1, lab in [((18, 5), (8, 20), "18:05 -> 08:20 (dopo il rollover)"), ((16, 0), (3, 0), "16:00 -> 03:00 (fino a Londra)"),
                        ((3, 0), (8, 20), "03:00 -> 08:20 (Londra)")]:
        if t0[0] < 12:   # inizio nello stesso giorno d
            dd = EC.giornaliero("XAU", "PEP").copy(); m1 = EC.carica("XAU", "PEP")
            a, _ = EC.prezzo_alle(m1, dd.dl + pd.Timedelta(hours=t0[0], minutes=t0[1])); b, _ = EC.prezzo_alle(m1, dd.dl + pd.Timedelta(hours=t1[0], minutes=t1[1]))
            z = np.log(b / a) / dd.sigma; z = z[(dd.data >= d.data.min())]
            out.append(descr(z, lab))
        else:
            out.append(descr(notte(t0=t0, t1=t1).zn, lab))
    # placebo: finestre spostate
    P = pool_spostato(); P = P.loc[P.index.isin(d.data)]
    medie_h = P.mean().round(4); print("media z delle finestre di 16h20 per ora d'inizio (NY):"); print(medie_h.to_string())
    pool = P.values.ravel(); pool = pool[np.isfinite(pool)]
    p_pl = EC.p_placebo(d.zn.mean(), pool, len(d), NREP, 0)
    # placebo per blocchi: la media della notte e' estrema fra le 24 ore d'inizio? (rango)
    rango = (medie_h >= medie_h[16]).sum()
    tab = pd.DataFrame(out); print(tab.to_string(index=False))
    print("placebo (finestre 16h20 a ogni ora, stesse date): media pool %.4f, anomala %.4f, p %.4f; rango della 16:00 fra 24 ore: %d"
          % (pool.mean(), d.zn.mean() - pool.mean(), p_pl, rango))
    # differenza accoppiata notte vs media delle altre partenze nello stesso giorno (tiene conto della correlazione)
    alt = P.drop(columns=[16]).mean(axis=1); diff = (P[16] - alt).dropna()
    print("notte - media altre partenze (accoppiata): media %.4f t %.2f n %d" % (diff.mean(), diff.mean() / diff.std() * np.sqrt(len(diff)), len(diff)))
    print("per anno:"); print(d.groupby("anno").zn.agg(["count", "mean"]).round(4).to_string())
    print("giorno per anno:"); print(d.groupby("anno").zg.agg(["count", "mean"]).round(4).to_string())
    # costi (long): ora server dell'ingresso dall'M1 usato
    ora = pd.to_datetime(d.ts0).dt.hour
    cb = np.array([EC.costo_trade("XAU", p, h, n, "base") for p, h, n in zip(d.p0, ora, d.notti)]) / d.p0 / d.sigma
    cs = np.array([EC.costo_trade("XAU", p, h, n, "stress") for p, h, n in zip(d.p0, ora, d.notti)]) / d.p0 / d.sigma
    print("netto base %.4f, stress %.4f, costo medio base %.4f z, ora server modale %d, notti medie %.2f, bps lordi %.2f"
          % ((d.zn - cb).mean(), (d.zn - cs).mean(), cb.mean(), ora.mode()[0], d.notti.mean(), (np.log(d.p1 / d.p0)).mean() * 1e4))
    # FTMO
    f = notte("FTMO"); dp = d[d.data.isin(f.data)]
    print("FTMO:", descr(f.zn, "FTMO"), "| PEP stesso periodo:", descr(dp.zn, "PEP"))
    print("FTMO per anno:", f.groupby("anno").zn.mean().round(4).to_dict(), "PEP stesso periodo:", dp.groupby("anno").zn.mean().round(4).to_dict())
    j = f[["data", "zn"]].merge(dp[["data", "zn"]], on="data"); print("corr PEP-FTMO notte", round(np.corrcoef(j.zn_x, j.zn_y)[0, 1], 3), "n", len(j))
    # estremi
    print("10 notti piu' estreme:"); print(d.reindex(d.zn.abs().sort_values(ascending=False).index).head(10)[["data", "dl_prev", "p0", "p1", "zn"]].to_string(index=False))
    print("contributo top 10 positivi: media senza %.4f" % d.zn.drop(d.zn.nlargest(10).index).mean())
    # 3 casi a mano
    for x in ["2017-07-05", "2019-11-29", "2022-03-14"]:
        r = d[d.data.astype(str) == x]
        print(x, r[["dl_prev", "p0", "ts0", "p1", "ts1", "zn", "notti"]].to_string(index=False, header=False))
