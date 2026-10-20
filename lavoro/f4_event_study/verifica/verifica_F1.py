# -*- coding: utf-8 -*-
"""Revisione avversaria F1 (lead-lag giornaliero). Codice indipendente: usa solo eventi_comune (dati sigillati < 2024)."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import eventi_comune as EC

NREP = 2000

def serie_cash(s, f):
    d = EC.giornaliero(s, f)[["data", "C", "ts_C", "r", "sigma", "z"]].copy()
    return d.set_index("data")

def serie_ny(s, f, hh=16, mm=0, ritardo_min=0):
    """Chiusura alle hh:mm New York per TUTTI gli strumenti (ora server = NY+7), giorni feriali."""
    m1 = EC.carica(s, f)
    ts = m1.ts
    date = pd.Series(ts.dt.normalize().unique())
    date = date[date.dt.weekday < 5]
    cfg = EC.STRUMENTI[s]
    fest = EC.festivi(cfg["cal"]) if cfg["cal"] else set()
    date = date[~date.dt.date.isin(fest)].reset_index(drop=True)
    q = date + pd.Timedelta(hours=hh + 7, minutes=mm + ritardo_min)
    t = ts.values.astype("datetime64[ns]"); qq = q.values.astype("datetime64[ns]")
    k = np.searchsorted(t, qq, side="left") - 1
    ok = (k >= 0) & (qq - t[np.clip(k, 0, None)] <= np.timedelta64(15, "m"))
    C = np.where(ok, m1.c.values[np.clip(k, 0, None)], np.nan)
    d = pd.DataFrame({"data": date.dt.date, "C": C}).dropna().reset_index(drop=True)
    d["r"] = np.log(d.C / d.C.shift()); d["sigma"] = d.r.rolling(20, min_periods=20).std().shift(1); d["z"] = d.r / d.sigma
    return d.set_index("data")

def allinea(sig, tgt, ingresso=None):
    """per ogni giorno di trading del bersaglio d+1: x = z del segnale nel giorno di trading precedente del bersaglio (stessa data esatta)."""
    T = tgt.copy(); T["prev"] = pd.Series(T.index, index=T.index).shift(1)
    T = T.dropna(subset=["prev", "z"])
    x = sig["z"].reindex(T["prev"].values).values
    out = pd.DataFrame({"d_sig": T["prev"].values, "d_tgt": T.index, "x": x, "y": T["z"].values,
                        "r": T["r"].values, "sigma": T["sigma"].values, "C_prev": tgt["C"].reindex(T["prev"].values).values})
    if ingresso is not None:  # rendimento da un prezzo d'ingresso ritardato alla chiusura del giorno dopo
        Pin = ingresso["C"].reindex(out.d_sig.values).values
        out["y"] = np.log(T["C"].values / Pin) / out["sigma"].values
    out = out.replace([np.inf, -np.inf], np.nan).dropna(subset=["x", "y"]).reset_index(drop=True)
    out["anno"] = pd.to_datetime(out.d_tgt).dt.year
    return out

def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    xc = x - x.mean(); b = (xc * (y - y.mean())).sum() / (xc ** 2).sum()
    a = y.mean() - b * x.mean(); e = y - a - b * x
    se = np.sqrt((xc ** 2 * e ** 2).sum() / (xc ** 2).sum() ** 2 * n / (n - 2))  # HC1 (= CR1 con un evento per data)
    return b, b / se, np.corrcoef(x, y)[0, 1]

def p_perm(x, y, b, nrep=NREP, seed=1):
    rng = np.random.default_rng(seed); x = np.asarray(x, float); y = np.asarray(y, float)
    xc = x - x.mean(); den = (xc ** 2).sum(); yc = y - y.mean()
    bb = np.array([(xc[rng.permutation(len(x))] * yc).sum() / den for _ in range(nrep)])
    return (1 + (np.abs(bb) >= abs(b)).sum()) / (1 + nrep)

def p_blocchi(x, y, b, L=5, nrep=NREP, seed=2):
    """placebo a blocchi circolari: sposta il segnale di uno shift casuale (>= 20 giorni) -> preserva autocorrelazioni."""
    rng = np.random.default_rng(seed); x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    xc = x - x.mean(); den = (xc ** 2).sum(); yc = y - y.mean()
    bb = np.array([(np.roll(xc, rng.integers(20, n - 20)) * yc).sum() / den for _ in range(nrep)])
    return (1 + (np.abs(bb) >= abs(b)).sum()) / (1 + nrep)

def scheda(df, nome):
    b, t, c = ols(df.x, df.y); p = p_perm(df.x, df.y, b); pb = p_blocchi(df.x, df.y, b)
    no20 = df[df.anno != 2020]; b2, t2, _ = ols(no20.x, no20.y); p2 = p_perm(no20.x, no20.y, b2)
    pa = {int(a): (len(g), round(ols(g.x, g.y)[0], 4)) for a, g in df.groupby("anno")}
    # robustezza agli estremi
    w = df.copy(); w["x"] = w.x.clip(-3, 3); w["y"] = w.y.clip(-3, 3); bw, tw, _ = ols(w.x, w.y)
    sp = pd.Series(df.x).rank().corr(pd.Series(df.y).rank())
    xc = df.x - df.x.mean(); contr = xc * (df.y - df.y.mean())
    idx = np.argsort(-np.sign(b) * contr.values)[:10]  # 10 giorni che spingono di più nel verso dell'effetto
    r10 = df.drop(df.index[idx]); b10, t10, _ = ols(r10.x, r10.y)
    # strategia: segno(b*x) sul bersaglio, lordo z
    g = np.sign(b * df.x) * df.y
    return dict(nome=nome, n=len(df), b=b, t=t, corr=c, p_perm=p, p_blocchi=pb, b_no2020=b2, t_no2020=t2, p_no2020=p2,
                per_anno=pa, b_wins3=bw, t_wins3=tw, spearman=sp, b_senza10=b10, t_senza10=t10,
                lordo_strategia_z=g.mean(), hit=(g > 0).mean(), periodo=f"{df.d_tgt.min()}..{df.d_tgt.max()}",
                top10=[(str(df.d_sig.iloc[i]), round(df.x.iloc[i], 2), round(df.y.iloc[i], 2)) for i in idx[:5]])

def costi(df, b, tgt_name):
    """netto della strategia segno(b*x) in z: costo (prezzo) / (C_prev * sigma)."""
    out = {}
    for sc in ("base", "stress"):
        notti = (pd.to_datetime(df.d_tgt) - pd.to_datetime(df.d_sig)).dt.days.values
        cst = np.array([EC.costo_trade(tgt_name, P, 23, nn, sc) for P, nn in zip(df.C_prev.values, notti)])
        cz = np.log(1 + cst / df.C_prev.values) / df.sigma.values
        g = np.sign(b * df.x.values) * df.y.values
        out[sc] = (np.nanmean(g - cz), np.nanmean(cz))
    return out

def stampa(R):
    for k, v in R.items():
        if isinstance(v, float): v = round(v, 4)
        print(f"   {k}: {v}")

if __name__ == "__main__":
    casi = [("XAG", "USDX"), ("UK100", "BRENT"), ("BRENT", "BRENT")]
    for s, tg in casi:
        print("=" * 100); print(f"{s} -> {tg}")
        # (A) chiusure come EC.giornaliero (indici alla chiusura cash locale)
        A = allinea(serie_cash(s, "PEP"), serie_cash(tg, "PEP"))
        R = scheda(A, "A cash/16NY PEP"); stampa(R)
        print("   costi:", {k: tuple(round(x, 4) for x in v) for k, v in costi(A, R["b"], tg).items()})
        # (B) tutto alle 16:00 NY
        B = allinea(serie_ny(s, "PEP"), serie_ny(tg, "PEP"))
        print("-- B tutto 16:00 NY"); R = scheda(B, "B 16NY"); [print(f"   {k}: {R[k]}") for k in ("n", "b", "t", "p_perm", "b_no2020", "per_anno")]
        # (C) ingresso ritardato 16:05 NY
        C = allinea(serie_cash(s, "PEP"), serie_cash(tg, "PEP"), ingresso=serie_ny(tg, "PEP", ritardo_min=5))
        print("-- C ingresso 16:05 NY"); R = scheda(C, "C"); [print(f"   {k}: {R[k]}") for k in ("n", "b", "t", "p_perm", "b_no2020")]
        # (D) chiusura alternativa 15:00 NY e 17:00 NY? (solo bersaglio a 15:30 NY)
        D = allinea(serie_ny(s, "PEP", 15, 30), serie_ny(tg, "PEP", 15, 30))
        print("-- D tutto 15:30 NY"); R = scheda(D, "D"); [print(f"   {k}: {R[k]}") for k in ("n", "b", "t", "p_perm", "b_no2020")]
