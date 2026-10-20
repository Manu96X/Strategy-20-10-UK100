# -*- coding: utf-8 -*-
"""REVISIONE AVVERSARIA di B2_VIX (ricalcolo da zero). Finestra: 14:05 NY del giorno FOMC -> 16:00 NY del giorno di
trading successivo del VIX. z = ln(P1/P0) / sigma (20 rendimenti giornalieri fino al giorno prima del FOMC: alle 14:05
il rendimento del giorno non e' ancora noto; variante con sigma che include il giorno). Placebo: stesse finestre orarie
nei giorni senza FOMC (tutti i giorni; solo mercoledi'). Controllo dei roll del future VIX sottostante al CFD."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import eventi_comune as EC

NREP = 2000

def scadenze_vix(anni=range(2020, 2025)):
    """Scadenza del future VIX: mercoledi' 30 giorni prima del terzo venerdi' del mese successivo
    (se quel venerdi' e' festivo si anticipa: caso ignorato, nessun effetto sulle date 2020-2023 tranne aprile 2022)."""
    out = []
    for y in anni:
        for mth in range(1, 13):
            ny, nm = (y, mth + 1) if mth < 12 else (y + 1, 1)
            out.append(pd.Timestamp(EC.terzo_venerdi(ny, nm)) - pd.Timedelta(days=30))
    return pd.DatetimeIndex(out)

def finestre(sig_incl=False):
    d = EC.giornaliero("VIX", "PEP").copy(); m1 = EC.carica("VIX", "PEP")
    d["dl_next"] = d.dl.shift(-1)
    p0, ts0 = EC.prezzo_alle(m1, d.dl + pd.Timedelta(hours=14, minutes=5))
    p1, ts1 = EC.prezzo_alle(m1, d.dl_next + pd.Timedelta(hours=16))
    d["p0"], d["ts0"], d["p1"], d["ts1"] = p0, ts0, p1, ts1
    sig = d.r.rolling(20).std() if sig_incl else d.sigma
    d["w"] = np.log(d.p1 / d.p0); d["zz"] = d.w / sig
    d["fomc"] = d.data.astype(str).isin(EC.FOMC)
    return d.dropna(subset=["zz"]).reset_index(drop=True)

def t_simple(x):
    x = np.asarray(x, float); return x.mean() / x.std(ddof=1) * np.sqrt(len(x))

def stat(ev, pool, nome, seed=0):
    p = EC.p_placebo(ev.mean(), pool, len(ev), NREP, seed)
    # placebo "studentizzato": t di Welch evento vs pool (tiene conto della varianza degli eventi)
    from scipy.stats import ttest_ind, mannwhitneyu
    tw = ttest_ind(ev, pool, equal_var=False)
    mw = mannwhitneyu(ev, pool)
    return dict(caso=nome, n=len(ev), media=round(ev.mean(), 4), anomala=round(ev.mean() - pool.mean(), 4), t=round(t_simple(ev), 3),
                p_placebo=round(p, 4), p_welch=round(tw.pvalue, 4), p_mannwhitney=round(mw.pvalue, 4),
                mediana=round(np.median(ev), 3), quota_pos=round((ev > 0).mean(), 3), media_pool=round(pool.mean(), 4), sd_ev=round(ev.std(), 3), sd_pool=round(pool.std(), 3))

if __name__ == "__main__":
    d = finestre(); ev = d[d.fomc]; pool = d[~d.fomc]
    print("eventi FOMC nel periodo VIX:", [x for x in EC.FOMC if x >= "2020-03-04"].__len__(), "trovati:", len(ev))
    out = [stat(ev.zz.values, pool.zz.values, "base (pool tutti i giorni)")]
    poolw = d[(~d.fomc) & (d.dl.dt.weekday == 2)]
    out.append(stat(ev.zz.values, poolw.zz.values, "pool solo mercoledi'"))
    e2 = ev[ev.anno != 2020]; out.append(stat(e2.zz.values, pool[pool.anno != 2020].zz.values, "senza 2020"))
    e3 = ev[ev.data.astype(str) != "2020-06-10"]; out.append(stat(e3.zz.values, pool.zz.values, "senza 2020-06-10"))
    srt = ev.sort_values("zz"); e4 = srt.iloc[2:-2]; out.append(stat(e4.zz.values, pool.zz.values, "trim 2+2"))
    e5 = srt.iloc[:-3]; out.append(stat(e5.zz.values, pool.zz.values, "senza i 3 piu' alti"))
    d2 = finestre(sig_incl=True); out.append(stat(d2[d2.fomc].zz.values, d2[~d2.fomc].zz.values, "sigma incl. giorno FOMC"))
    # roll del future: finestre che contengono una scadenza VIX
    sc = scadenze_vix(); d["roll"] = d.apply(lambda r: ((sc >= r.dl) & (sc <= r.dl_next)).any(), axis=1)
    print("eventi FOMC con scadenza VIX nella finestra:", ev.data[d.loc[ev.index, "roll"]].astype(str).tolist())
    print("media pool finestre con scadenza %.3f (n %d) vs senza %.3f" % (d[(~d.fomc) & d.roll].zz.mean(), ((~d.fomc) & d.roll).sum(), d[(~d.fomc) & ~d.roll].zz.mean()))
    er = ev[~d.loc[ev.index, "roll"]]; out.append(stat(er.zz.values, d[(~d.fomc) & ~d.roll].zz.values, "senza finestre con scadenza VIX"))
    tab = pd.DataFrame(out); print(tab.to_string(index=False))
    print("bps medi: %.1f" % (ev.w.mean() * 1e4))
    print(ev.groupby("anno").zz.agg(["count", "mean", "median"]).round(3).to_string())
    print(ev[["data", "p0", "ts0", "p1", "ts1", "zz"]].sort_values("zz").to_string(index=False))
    # salti di roll: gap piu' grandi fra M1 consecutivi (riapertura dopo la pausa)
    m1 = EC.carica("VIX", "PEP"); g = np.log(m1.o / m1.c.shift()); dt = m1.ts.diff().dt.total_seconds() / 60
    q = pd.DataFrame({"ts": m1.ts, "loc": m1["loc"], "gap": g, "min": dt}); q = q[q["min"] > 30]
    q["vicino_scadenza_gg"] = [int(np.min(np.abs((sc - x.normalize()).days))) for x in q["loc"]]
    print(q.reindex(q.gap.abs().sort_values(ascending=False).index).head(25).to_string(index=False))
