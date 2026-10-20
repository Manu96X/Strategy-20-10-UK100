# -*- coding: utf-8 -*-
"""Parte 2: specifica con sigma del segnale che include il giorno d (piano: 'fino al giorno d'ingresso incluso'),
feed FTMO, controllo per l'autocorrelazione propria del bersaglio, singoli eventi estremi, controlli a mano."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verifica_F1 import *

def sig_incl(d):
    d = d.copy(); d["z"] = d.r / d.r.rolling(20, min_periods=20).std(); return d

def multi(df, extra):
    X = np.column_stack([np.ones(len(df)), df.x.values, extra]); y = df.y.values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ beta
    XtXi = np.linalg.inv(X.T @ X); meat = (X * e[:, None]).T @ (X * e[:, None])
    V = XtXi @ meat @ XtXi * len(y) / (len(y) - X.shape[1])
    return beta[1], beta[1] / np.sqrt(V[1, 1]), beta[2], beta[2] / np.sqrt(V[2, 2])

casi = [("XAG", "USDX"), ("UK100", "BRENT"), ("BRENT", "BRENT")]
for s, tg in casi:
    print("=" * 100); print(s, "->", tg, "| x con sigma incl. d")
    S = sig_incl(serie_cash(s, "PEP")); T = serie_cash(tg, "PEP")
    A = allinea(S, T); R = scheda(A, "PEP"); stampa(R)
    print("   costi (netto, costo medio) z:", {k: tuple(round(x, 4) for x in v) for k, v in costi(A, R["b"], tg).items()})
    # bps lordi della strategia
    g = np.sign(R["b"] * A.x) * A.r * 1e4; print("   bps lordi medi strategia:", round(g.mean(), 2))
    # singolo evento piu' influente
    xc = A.x - A.x.mean(); contr = (xc * (A.y - A.y.mean())) * np.sign(R["b"])
    o = contr.sort_values(ascending=False)
    quota = o.head(5).sum() / (np.sign(R["b"]) * (xc * (A.y - A.y.mean())).sum())
    print("   quota del numeratore dai 5 giorni piu' favorevoli:", round(quota, 3), "| 1 giorno:", round(o.head(1).sum() / contr.sum(), 3))
    for k in [1, 3, 5, 10, 20]:
        r_ = A.drop(o.index[:k]); print(f"   senza i {k} giorni piu' favorevoli: b={ols(r_.x, r_.y)[0]:.4f} t={ols(r_.x, r_.y)[1]:.2f}")
    # sottoperiodi a meta'
    mid = len(A) // 2; print("   meta' 1:", [round(v, 4) for v in ols(A.x[:mid], A.y[:mid])], "meta' 2:", [round(v, 4) for v in ols(A.x[mid:], A.y[mid:])])
    # controllo: ritardo proprio del bersaglio
    if s != tg:
        own = sig_incl(T)["z"].reindex(A.d_sig.values).values
        ok = np.isfinite(own); B = A[ok]
        print("   y ~ x + z_bersaglio(d): b_x=%.4f t=%.2f | b_own=%.4f t=%.2f" % multi(B, own[ok]))
        print("   corr contemporanea x(d) con z_bersaglio(d):", round(np.corrcoef(B.x, own[ok])[0, 1], 3))
    # tabella z per anno della strategia lorda
    A["g"] = np.sign(R["b"] * A.x) * A.y
    print("   lordo strategia per anno:", A.groupby("anno").g.mean().round(3).to_dict())

print("=" * 100); print("FEED FTMO / PROXY")
def run(nome, S, T):
    A = allinea(S, T)
    if len(A) < 50: print(nome, "n", len(A)); return
    b, t, c = ols(A.x, A.y); p = p_perm(A.x, A.y, b)
    print(f"  {nome}: n={len(A)} b={b:.4f} t={t:.2f} p={p:.3f} periodo {A.d_tgt.min()}..{A.d_tgt.max()} per anno", {int(a): round(ols(g.x, g.y)[0], 3) for a, g in A.groupby('anno')})
    return A
run("XAG FTMO -> USDX PEP", sig_incl(serie_cash("XAG", "FTMO")), serie_cash("USDX", "PEP"))
run("XAG PEP -> USDX PEP (dal 2021-02)", sig_incl(serie_cash("XAG", "PEP")).loc[pd.Timestamp("2021-01-04").date():], serie_cash("USDX", "PEP").loc[pd.Timestamp("2021-02-02").date():])
run("XAU PEP -> USDX PEP", sig_incl(serie_cash("XAU", "PEP")), serie_cash("USDX", "PEP"))
run("USDX PEP -> USDX PEP", sig_incl(serie_cash("USDX", "PEP")), serie_cash("USDX", "PEP"))
run("UK100 FTMO -> USOIL FTMO", sig_incl(serie_cash("UK100", "FTMO")), serie_cash("USOIL", "FTMO"))
run("UK100 PEP -> USOIL FTMO", sig_incl(serie_cash("UK100", "PEP")), serie_cash("USOIL", "FTMO"))
run("UK100 PEP -> BRENT PEP (dal 2021-09-14)", sig_incl(serie_cash("UK100", "PEP")).loc[pd.Timestamp("2021-08-01").date():], serie_cash("BRENT", "PEP").loc[pd.Timestamp("2021-10-12").date():])
run("USOIL FTMO -> USOIL FTMO", sig_incl(serie_cash("USOIL", "FTMO")), serie_cash("USOIL", "FTMO"))
run("BRENT PEP -> BRENT PEP (dal 2021-05)", sig_incl(serie_cash("BRENT", "PEP")).loc[pd.Timestamp("2021-04-05").date():], serie_cash("BRENT", "PEP").loc[pd.Timestamp("2021-05-03").date():])
run("BRENT PEP -> USOIL FTMO", sig_incl(serie_cash("BRENT", "PEP")), serie_cash("USOIL", "FTMO"))
for idx in ["GER40", "US500", "US100"]:
    run(f"{idx} PEP -> BRENT PEP (coerenza meccanismo)", sig_incl(serie_cash(idx, "PEP")), serie_cash("BRENT", "PEP"))

print("=" * 100); print("CONTROLLI A MANO")
def mostra(s, f, giorno, ore_server):
    m1 = EC.carica(s, f); d0 = pd.Timestamp(giorno)
    x = m1[(m1.ts >= d0 + pd.Timedelta(hours=ore_server[0])) & (m1.ts < d0 + pd.Timedelta(hours=ore_server[1]))]
    print(f"  {s} {f} {giorno}: M1 tra {ore_server} server ->", len(x), "barre; ultime:", x[["ts", "loc", "c"]].tail(3).to_dict("records"))
    d = EC.giornaliero(s, f); r = d[d.data == d0.date()]
    print("     tabella giornaliera:", r[["data", "C", "ts_C", "r"]].to_dict("records") if len(r) else "GIORNO ASSENTE")
mostra("UK100", "PEP", "2019-03-12", (18, 20))       # DST USA gia' attivo, Londra no: chiusura 16:30 Londra = 12:30 NY = 19:30 server
mostra("UK100", "PEP", "2019-04-12", (18, 20))       # entrambi DST: 16:30 Londra = 11:30 NY = 18:30 server
mostra("BRENT", "PEP", "2020-03-06", (22, 24)); mostra("BRENT", "PEP", "2020-03-09", (22, 24))
mostra("USDX", "PEP", "2019-07-04", (19, 24)); mostra("USDX", "PEP", "2019-07-05", (22, 24))
mostra("BRENT", "PEP", "2019-04-19", (0, 24))       # Venerdi' Santo
mostra("BRENT", "PEP", "2020-11-26", (18, 24))      # Thanksgiving
mostra("XAG", "PEP", "2019-12-24", (18, 24)); mostra("USDX", "PEP", "2019-12-24", (18, 24))
mostra("BRENT", "PEP", "2019-01-21", (18, 24))      # MLK
