# -*- coding: utf-8 -*-
"""REVISIONE AVVERSARIA di F1:XAU->USDX (ricalcolo da zero, senza famiglia_*.py). Solo dati sigillati < 2024.
x = z giornaliero di XAU nel giorno d (chiusura 16:00 NY); y = z giornaliero di USDX nel giorno di trading successivo
(sigma = 20 rendimenti fino a d incluso = sigma di EC al giorno d+1). Statistica = pendenza OLS di y su x."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import eventi_comune as EC

NREP = 2000

def coppie(fx="PEP", fy="PEP", y_strum="USDX", x_strum="XAU"):
    X = EC.giornaliero(x_strum, fx)[["data", "z", "r", "C"]].rename(columns={"z": "x", "r": "rx", "C": "Cx"})
    Y = EC.giornaliero(y_strum, fy)[["data", "dl", "z", "r", "C", "sigma"]].copy()
    Y["y"] = Y.z.shift(-1); Y["data_y"] = Y.data.shift(-1); Y["zy_oggi"] = Y.z
    Y["sig_ingr"] = Y.sigma.shift(-1); Y["C_ingr"] = Y.C
    m = X.merge(Y, on="data").dropna(subset=["x", "y"]).reset_index(drop=True)
    m["anno"] = pd.to_datetime(m.data).dt.year
    m["notti"] = (pd.to_datetime(m.data_y) - pd.to_datetime(m.data)).dt.days
    return m

def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); xc = x - x.mean()
    b = (xc * (y - y.mean())).sum() / (xc ** 2).sum(); e = y - y.mean() - b * xc; n = len(x)
    se = np.sqrt((e ** 2).sum() / (n - 2) / (xc ** 2).sum())
    se_hc = np.sqrt(((xc * e) ** 2).sum()) / (xc ** 2).sum() * np.sqrt(n / (n - 2))
    return b, b / se, b / se_hc, np.corrcoef(x, y)[0, 1]

def perm_p(x, y, b, nrep=NREP, seed=0):
    rng = np.random.default_rng(seed); x = np.asarray(x, float); y = np.asarray(y, float)
    xc = x - x.mean(); den = (xc ** 2).sum(); yc = y - y.mean(); c = 0
    for _ in range(nrep):
        if abs((rng.permutation(xc) * yc).sum() / den) >= abs(b): c += 1
    return (1 + c) / (1 + nrep)

def riga(m, nome):
    b, t, thc, r = ols(m.x, m.y); p = perm_p(m.x, m.y, b)
    return dict(caso=nome, n=len(m), b=round(b, 4), t=round(t, 3), t_hc=round(thc, 3), corr=round(r, 4), p_perm=round(p, 5))

if __name__ == "__main__":
    m = coppie()
    out = [riga(m, "base PEP->PEP")]
    out.append(riga(m[m.anno != 2020], "senza 2020"))
    # robustezza agli estremi
    w = m.copy(); w["x"] = w.x.clip(-3, 3); w["y"] = w.y.clip(-3, 3); out.append(riga(w, "winsor +-3"))
    k = (m.x * (m.y - m.y.mean())).abs().rank(ascending=False)
    out.append(riga(m[k > 10], "senza i 10 punti piu' influenti"))
    out.append(riga(m[k > 25], "senza i 25 punti piu' influenti"))
    from scipy.stats import spearmanr
    rs = spearmanr(m.x, m.y)
    out.append(dict(caso="Spearman", n=len(m), corr=round(rs.statistic, 4), p_perm=round(rs.pvalue, 5)))
    # controllo per l'autocorrelazione propria di USDX e per il co-movimento di oggi
    import numpy.linalg as la
    mm = m.dropna(subset=["zy_oggi"])
    A = np.column_stack([np.ones(len(mm)), mm.x, mm.zy_oggi]); beta = la.lstsq(A, mm.y, rcond=None)[0]
    e = mm.y - A @ beta; s2 = (e ** 2).sum() / (len(mm) - 3); cov = s2 * la.inv(A.T @ A)
    out.append(dict(caso="y ~ x + z_USDX(d)", n=len(mm), b=round(beta[1], 4), t=round(beta[1] / np.sqrt(cov[1, 1]), 3),
                    b_usdx_oggi=round(beta[2], 4), t_usdx_oggi=round(beta[2] / np.sqrt(cov[2, 2]), 3),
                    corr_contemp=round(np.corrcoef(mm.x, mm.zy_oggi)[0, 1], 3)))
    # asincronia: XAU alle 15:45 (15 min prima) e USDX dalle 16:15
    xm = EC.carica("XAU", "PEP"); ym = EC.carica("USDX", "PEP")
    dl = pd.to_datetime(m.data)
    def zz(m1, t0, t1, sig):
        a, _ = EC.prezzo_alle(m1, t0); b_, _ = EC.prezzo_alle(m1, t1); return np.log(b_ / a) / sig
    Xd = EC.giornaliero("XAU", "PEP").set_index("data")
    prevx = Xd.dl.shift(1).reindex(m.data).values
    for lab, ty0, ty1, tx0, tx1 in [
            ("x 16:00->16:00, y 16:15->16:00", dl + pd.Timedelta(hours=16, minutes=15), pd.to_datetime(m.data_y) + pd.Timedelta(hours=16), None, None),
            ("x 16:00->16:00, y 20:05->16:00 (riapertura ICE)", dl + pd.Timedelta(hours=20, minutes=5), pd.to_datetime(m.data_y) + pd.Timedelta(hours=16), None, None),
            ("x 15:45->15:45, y 16:00->16:00", None, None, pd.to_datetime(prevx) + pd.Timedelta(hours=15, minutes=45), dl + pd.Timedelta(hours=15, minutes=45)),
            ("x giorno 08:20->16:00, y 16:00->16:00", None, None, dl + pd.Timedelta(hours=8, minutes=20), dl + pd.Timedelta(hours=16)),
            ("x notte 16:00(d-1)->08:20, y 16:00->16:00", None, None, pd.to_datetime(prevx) + pd.Timedelta(hours=16), dl + pd.Timedelta(hours=8, minutes=20)),
            ("x 16:00->16:00, y 16:00->08:20 (notte)", dl + pd.Timedelta(hours=16), pd.to_datetime(m.data_y) + pd.Timedelta(hours=8, minutes=20), None, None),
            ("x 16:00->16:00, y 08:20->16:00 (giorno dopo)", pd.to_datetime(m.data_y) + pd.Timedelta(hours=8, minutes=20), pd.to_datetime(m.data_y) + pd.Timedelta(hours=16), None, None)]:
        q = m.copy()
        if ty0 is not None: q["y"] = zz(ym, ty0, ty1, m.sig_ingr.values)
        if tx0 is not None: q["x"] = zz(xm, tx0, tx1, Xd.sigma.reindex(m.data).values)
        q = q.replace([np.inf, -np.inf], np.nan).dropna(subset=["x", "y"])
        out.append(riga(q, lab))
    # feed: XAU FTMO -> USDX PEP (periodo comune) e PEP->PEP nello stesso periodo
    mf = coppie(fx="FTMO"); out.append(riga(mf, "XAU FTMO -> USDX PEP (2021-2023)"))
    out.append(riga(m[m.data.isin(mf.data)], "XAU PEP -> USDX PEP stesso periodo"))
    # simmetria: USDX->XAU (non richiesto, controllo di coerenza)
    tab = pd.DataFrame(out); print(tab.to_string(index=False))
    # per anno
    pa = m.groupby("anno").apply(lambda g: pd.Series(dict(n=len(g), b=ols(g.x, g.y)[0], t=ols(g.x, g.y)[1]))).round(4)
    print(pa.to_string())
    # trade: short USDX se XAU sale (verso dell'effetto), netto in z
    g = -np.sign(m.x) * m.y
    cb = np.array([EC.costo_trade("USDX", c, 23, n, "base") for c, n in zip(m.C_ingr, m.notti)]) / m.C_ingr / m.sig_ingr
    cs = np.array([EC.costo_trade("USDX", c, 23, n, "stress") for c, n in zip(m.C_ingr, m.notti)]) / m.C_ingr / m.sig_ingr
    print("trade segno: lordo z %.4f t %.2f | netto base %.4f | netto stress %.4f | costo medio base %.4f z" %
          (g.mean(), g.mean() / g.std() * np.sqrt(len(g)), (g - cb).mean(), (g - cs).mean(), cb.mean()))
    sel = m.x.abs() > 1; gs = g[sel]
    print("solo |x|>1: n %d lordo %.4f netto base %.4f" % (sel.sum(), gs.mean(), (gs - cb[sel]).mean()))
    print("bps medi della pendenza (b * sigma media USDX): %.2f" % (ols(m.x, m.y)[0] * m.sig_ingr.mean() * 1e4))
    # 3 casi a mano
    for dd in ["2019-11-27", "2020-03-18", "2022-12-23"]:
        r = m[m.data.astype(str) == dd]
        print(dd, r[["data", "x", "data_y", "y", "notti"]].to_string(index=False, header=False))
    Xg = EC.giornaliero("XAU", "PEP"); Yg = EC.giornaliero("USDX", "PEP")
    for dd in ["2019-11-27", "2019-11-28", "2019-11-29", "2020-03-18", "2020-03-19", "2022-12-23", "2022-12-26", "2022-12-27"]:
        a = Xg[Xg.data.astype(str) == dd]; b = Yg[Yg.data.astype(str) == dd]
        print(dd, "XAU", a[["C", "ts_C", "z"]].values.tolist(), "USDX", b[["C", "ts_C", "z"]].values.tolist())
