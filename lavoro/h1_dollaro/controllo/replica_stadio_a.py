"""Replica indipendente dello Stadio A del protocollo H1 (dollaro segue i metalli).

Scritto da zero a partire da PROTOCOLLO_H1.md. Eseguire con: python3 -I replica_stadio_a.py
"""
import os
import sys
import json
import datetime as dt
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

DATI = "/home/user/dati_h1/scoperta"
SPREAD_CSV = "/home/user/Strategy-20-10-UK100/lavoro/h1_dollaro/risultati/SPREAD_FX_FTMO_per_ora.csv"
SPEC_CSV = "/home/user/Strategy-20-10-UK100/specifiche_simboli.csv"
OUT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(OUT, "cache")
os.makedirs(CACHE, exist_ok=True)

NY = ZoneInfo("America/New_York")
ATH = ZoneInfo("Europe/Athens")
UTC = dt.timezone.utc

FILES = {
    "EURUSD": "EURUSD m1 FTMO.csv",
    "GBPUSD": "GBPUSD m1 FTMO.csv",
    "AUDUSD": "AUDUSD m1 FTMO.csv",
    "USDJPY": "USDJPY m1 FTMO.csv",
    "USDCHF": "USDCHF m1 FTMO.csv",
    "USDCAD": "USDCAD m1 FTMO.csv",
    "XAU": "XAU-USD Pepperstone m1.csv",
    "XAG": "XAG-USD Pepperstone m1.csv",
    "USDX": "USDX pepperstone m1.csv",
}
PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "USDCAD"]
VERSO = {"EURUSD": -1, "GBPUSD": -1, "AUDUSD": -1, "USDJPY": 1, "USDCHF": 1, "USDCAD": 1}
PEPPER = {"XAU", "XAG", "USDX"}
START = "2016.11.01"
FINE_A = pd.Timestamp("2019-04-19")
MAXGAP = 4
NPERM = 100_000


# ---------------------------------------------------------------- caricamento
def carica(sym):
    cp = os.path.join(CACHE, sym + ".npz")
    if os.path.exists(cp):
        z = np.load(cp)
        return z["t"], z["o"], z["c"]
    df = pd.read_csv(os.path.join(DATI, FILES[sym]), sep="\t", usecols=[0, 1, 2, 5],
                     names=["d", "h", "o", "c"], header=0, dtype={"d": str, "h": str})
    df = df[df["d"] >= START]
    t = pd.to_datetime(df["d"] + " " + df["h"], format="%Y.%m.%d %H:%M:%S").values.astype("datetime64[ns]")
    o = df["o"].to_numpy(float)
    c = df["c"].to_numpy(float)
    order = np.argsort(t, kind="stable")
    t, o, c = t[order], o[order], c[order]
    # duplicati di timestamp: tieni l'ultimo
    keep = np.ones(len(t), bool)
    keep[:-1] = t[1:] != t[:-1]
    t, o, c = t[keep], o[keep], c[keep]
    np.savez(cp, t=t, o=o, c=c)
    return t, o, c


def passo_modale(t):
    """dict data server (datetime64[D]) -> passo modale in minuti fra barre consecutive dello stesso giorno."""
    days = t.astype("datetime64[D]")
    diff = (t[1:] - t[:-1]).astype("timedelta64[m]").astype(np.int64)
    same = days[1:] == days[:-1]
    df = pd.DataFrame({"d": days[1:][same], "m": diff[same]})
    mode = df.groupby("d")["m"].agg(lambda s: s.value_counts().sort_index().idxmax())
    return {np.datetime64(k, "D"): int(v) for k, v in mode.items()}


# ---------------------------------------------------------------- fusi
def server_time(sym, ny_naive):
    """ny_naive: datetime naive in ora di New York -> datetime naive in ora server."""
    if sym in PEPPER:
        return ny_naive + dt.timedelta(hours=7)
    if ny_naive.year <= 2020:
        aware = ny_naive.replace(tzinfo=NY)
        return aware.astimezone(ATH).replace(tzinfo=None)
    return ny_naive + dt.timedelta(hours=7)


def athens_diverso(ny_naive):
    aware = ny_naive.replace(tzinfo=NY)
    a = aware.astimezone(ATH).replace(tzinfo=None)
    return a != ny_naive + dt.timedelta(hours=7)


# ---------------------------------------------------------------- prezzi
def prezzo_close_prima(t, c, mode, Ts):
    """close dell'ultima barra che inizia strettamente prima di T, entro 15 min (60 se giorno a barre H1)."""
    Ts = np.asarray(Ts, dtype="datetime64[ns]")
    idx = np.searchsorted(t, Ts, side="left") - 1
    out = np.full(len(Ts), np.nan)
    for i, (T, j) in enumerate(zip(Ts, idx)):
        if j < 0:
            continue
        lag = (T - t[j]).astype("timedelta64[s]").astype(np.int64) / 60.0
        tol = 60 if mode.get(T.astype("datetime64[D]"), 1) == 60 else 15
        if 0 < lag <= tol:
            out[i] = c[j]
    return out


def prezzo_open_dopo(t, o, Ts, tol=15):
    Ts = np.asarray(Ts, dtype="datetime64[ns]")
    idx = np.searchsorted(t, Ts, side="left")
    out = np.full(len(Ts), np.nan)
    for i, (T, j) in enumerate(zip(Ts, idx)):
        if j >= len(t):
            continue
        lead = (t[j] - T).astype("timedelta64[s]").astype(np.int64) / 60.0
        if 0 <= lead <= tol:
            out[i] = o[j]
    return out


# ---------------------------------------------------------------- serie
def rendimenti(dates, P):
    """righe = date con prezzo valido (ordinate). r(d) = ln(P(d)/P(prev)) se buco <= 4 gg."""
    dates = pd.DatetimeIndex(dates)
    gap = np.r_[np.nan, (dates[1:] - dates[:-1]).days.to_numpy(float)]
    r = np.r_[np.nan, np.log(P[1:] / P[:-1])]
    r[~(gap <= MAXGAP)] = np.nan
    return r


def sigma20(r):
    """std (ddof=1) degli ultimi 20 rendimenti validi con indice <= d; NaN se meno di 20."""
    s = pd.Series(r)
    v = s.dropna()
    sd = v.rolling(20).std(ddof=1)
    out = pd.Series(np.nan, index=s.index)
    out.loc[sd.index] = sd.values
    out = out.ffill()
    # prima del primo rendimento valido la ffill non introduce nulla di spurio
    return out.to_numpy()


def successivo(dates):
    """indice della riga successiva se entro 4 gg, altrimenti -1."""
    dates = pd.DatetimeIndex(dates)
    nxt = np.full(len(dates), -1)
    gap = (dates[1:] - dates[:-1]).days.to_numpy()
    ok = gap <= MAXGAP
    nxt[:-1][ok] = np.arange(1, len(dates))[ok]
    return nxt


# ---------------------------------------------------------------- statistica
def ols_hc1(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ X.T @ y
    e = y - X @ beta
    meat = (X * e[:, None] ** 2).T @ X
    V = XtXi @ meat @ XtXi * n / (n - 2)
    return beta[1], beta[1] / np.sqrt(V[1, 1])


def perm_p(x, y, nperm=NPERM, seed=20261020):
    x = np.asarray(x, float)
    yc = np.asarray(y, float) - np.mean(y)
    obs = x @ yc
    rng = np.random.default_rng(seed)
    cnt = 0
    done = 0
    while done < nperm:
        k = min(5000, nperm - done)
        P = np.array([rng.permutation(x) for _ in range(k)])
        cnt += int(np.sum(P @ yc <= obs + 1e-15))
        done += k
    return (cnt + 1) / (nperm + 1)


def main():
    # ----- giorni feriali NY
    days = pd.bdate_range("2016-11-01", "2023-12-29")
    T16 = [dt.datetime(d.year, d.month, d.day, 16, 0) for d in days]
    T0820 = [dt.datetime(d.year, d.month, d.day, 8, 20) for d in days]

    P16 = {}
    O0820 = {}
    info = {}
    for sym in FILES:
        t, o, c = carica(sym)
        mode = passo_modale(t)
        Ts = np.array([np.datetime64(server_time(sym, x)) for x in T16], dtype="datetime64[ns]")
        P16[sym] = prezzo_close_prima(t, c, mode, Ts)
        if sym in PAIRS:
            Te = np.array([np.datetime64(server_time(sym, x)) for x in T0820], dtype="datetime64[ns]")
            O0820[sym] = prezzo_open_dopo(t, o, Te)
        h1days = sorted(str(k) for k, v in mode.items() if v == 60)
        info[sym] = dict(primo=str(t[0]), ultimo=str(t[-1]), n_giorni_H1=len(h1days),
                         H1_da=h1days[0] if h1days else None, H1_a=h1days[-1] if h1days else None,
                         n_prezzi16=int(np.isfinite(P16[sym]).sum()))
        print(sym, info[sym], flush=True)

    D = pd.DataFrame({k: v for k, v in P16.items()}, index=days)
    for k in PAIRS:
        D["o_" + k] = O0820[k]

    # ----- metalli: serie proprie
    z = {}
    for m in ["XAU", "XAG"]:
        s = D[m].dropna()
        r = rendimenti(s.index, s.to_numpy())
        sg = sigma20(r)
        z[m] = pd.Series(r / sg, index=s.index)
    S = (z["XAU"].reindex(days) + z["XAG"].reindex(days)) / 2.0

    # ----- paniere
    B = D[PAIRS + ["o_" + k for k in PAIRS]].dropna(subset=PAIRS)
    bd = B.index
    nxt = successivo(bd)
    rk = {}
    for k in PAIRS:
        rk[k] = VERSO[k] * rendimenti(bd, B[k].to_numpy())
    rB = np.mean([rk[k] for k in PAIRS], axis=0)
    sigB = sigma20(rB)
    sig_k = {k: sigma20(rk[k]) for k in PAIRS}

    has1 = nxt >= 0
    j = np.where(has1, nxt, 0)
    W1 = np.full(len(bd), np.nan)
    W2 = np.full(len(bd), np.nan)
    w1k = {}
    w2k = {}
    for k in PAIRS:
        p0 = B[k].to_numpy()
        w1k[k] = np.where(has1, VERSO[k] * np.log(p0[j] / p0), np.nan)
        oe = B["o_" + k].to_numpy()
        w2k[k] = np.where(has1, VERSO[k] * np.log(p0[j] / oe[j]), np.nan)
    W1 = np.mean([w1k[k] for k in PAIRS], axis=0)
    W2 = np.mean([w2k[k] for k in PAIRS], axis=0)  # NaN se manca un ingresso
    dt1 = pd.DatetimeIndex(np.where(has1, bd[j], pd.NaT))

    G = pd.DataFrame({"dt": bd, "dt1": dt1, "S": S.reindex(bd).to_numpy(), "sigB": sigB,
                      "W1": W1, "W2": W2}, index=bd)
    G["y1"] = G["W1"] / G["sigB"]
    G["y2"] = G["W2"] / G["sigB"]

    stadioA = G["S"].notna() & G["y1"].notna() & G["sigB"].notna() & (G["dt1"] <= FINE_A)
    A = G[stadioA].copy()
    assert A["dt1"].max() <= FINE_A and A["dt"].max() < pd.Timestamp("2024-01-01")

    res = {}
    b, t = ols_hc1(A["S"], A["y1"])
    p = perm_p(A["S"].to_numpy(), A["y1"].to_numpy())
    res["A1"] = dict(n=len(A), b=b, t_hc1=t, p_unilaterale=p,
                     primo_d=str(A.index[0].date()), ultimo_d1=str(A["dt1"].max().date()))
    print("A1", res["A1"], flush=True)

    # ----- costi
    sp = pd.read_csv(SPREAD_CSV, sep=";", decimal=",")
    spread = {(r.coppia, int(r.h)): max(float(r.p75_pip), 0.1) for r in sp.itertuples()}
    spec = pd.read_csv(SPEC_CSV, sep=";", skiprows=1)
    spec = spec.set_index("simbolo")
    swapf = {}
    for k in PAIRS:
        rr = spec.loc[k]
        swapf[k] = (float(rr.swap_long) * float(rr.valore_1_punto_1_lotto) / float(rr.nozionale_1_lotto),
                    float(rr.swap_short) * float(rr.valore_1_punto_1_lotto) / float(rr.nozionale_1_lotto))
    print("swap frac/notte", swapf)
    pipsz = {k: (0.01 if k == "USDJPY" else 0.0001) for k in PAIRS}

    def costo_coppia(k, dirc, p_in, h_in, h_out, notti, stress):
        """dirc = +1 compra la coppia, -1 vende. Restituisce costo in frazione (positivo = costo)."""
        sp_pip = spread[(k, h_in)] if dirc > 0 else spread[(k, h_out)]
        if stress:
            sp_pip = sp_pip * 1.5 + 0.2
        c = sp_pip * pipsz[k] / p_in
        c += 5.0 / (100000.0 * p_in) if k.endswith("USD") and not k.startswith("USD") else 5.0 / 100000.0
        if notti:
            sw = swapf[k][0] if dirc > 0 else swapf[k][1]
            sw = sw * notti
            if stress and sw < 0:
                sw *= 1.5
            c -= sw
        return c

    def strategia(df, finestra, stress):
        pos = -np.sign(df["S"].to_numpy())
        lordo = pos * df[finestra].to_numpy()
        cost = np.zeros(len(df))
        for i, (d, row) in enumerate(df.iterrows()):
            cs = []
            for k in PAIRS:
                dirc = pos[i] * VERSO[k]
                if dirc == 0:
                    cs.append(0.0)
                    continue
                if finestra == "W2":
                    p_in = row["o_" + k + "_1"]
                    cs.append(costo_coppia(k, dirc, p_in, 15, 22, 0, stress))
                else:
                    p_in = row[k]
                    notti = 3 if d.weekday() == 2 else 1
                    cs.append(costo_coppia(k, dirc, p_in, 22, 22, notti, stress))
            cost[i] = np.mean(cs)
        sg = df["sigB"].to_numpy()
        nz = (lordo - cost) / sg
        return dict(n=len(df), netto_z=nz.mean(), t=nz.mean() / (nz.std(ddof=1) / np.sqrt(len(nz))),
                    lordo_z=(lordo / sg).mean(), costo_z=(cost / sg).mean())

    A2 = A.join(B[PAIRS])
    for k in PAIRS:
        A2["o_" + k + "_1"] = B["o_" + k].reindex(A2["dt1"]).to_numpy()
    A2w2 = A2[A2["y2"].notna()]
    res["W2_base"] = strategia(A2w2, "W2", False)
    res["W2_stress"] = strategia(A2w2, "W2", True)
    res["W1_base"] = strategia(A2, "W1", False)
    res["W1_stress"] = strategia(A2, "W1", True)
    for k in ["W2_base", "W2_stress", "W1_base", "W1_stress"]:
        print(k, res[k])

    # ----- USDX
    u = D["USDX"].dropna()
    ru = rendimenti(u.index, u.to_numpy())
    su = sigma20(ru)
    nu = successivo(u.index)
    pu = u.to_numpy()
    yu = np.where(nu >= 0, np.log(pu[np.where(nu >= 0, nu, 0)] / pu), np.nan) / su
    U = pd.DataFrame({"yu": yu, "du1": pd.DatetimeIndex(np.where(nu >= 0, u.index[np.where(nu >= 0, nu, 0)], pd.NaT))},
                     index=u.index)
    U["S"] = S.reindex(U.index)
    CA = U[U["S"].notna() & U["yu"].notna() & (U["du1"] <= FINE_A)]
    b, t = ols_hc1(CA["S"], CA["yu"])
    res["C1_USDX"] = dict(n=len(CA), b=b, t_hc1=t)
    print("C1", res["C1_USDX"])

    # ----- A0
    def escluso2020(d, d1):
        out = False
        for x in (d, d1):
            if x.year == 2020:
                for hh, mm in ((16, 0), (8, 20)):
                    if athens_diverso(dt.datetime(x.year, x.month, x.day, hh, mm)):
                        out = True
        return out

    a0 = G[G["S"].notna() & G["y1"].notna() & (G.index >= "2019-04-22") & (G.index <= "2023-12-29")].copy()
    a0 = a0[[not escluso2020(d, d1) for d, d1 in zip(a0.index, a0["dt1"])]]
    a0 = a0.join(U[["yu"]])
    a0c = a0[a0["yu"].notna()]
    b, t = ols_hc1(a0c["S"], a0c["y1"])
    res["A0_forex"] = dict(n=len(a0c), b=b, t_hc1=t)
    b, t = ols_hc1(a0c["S"], a0c["yu"])
    res["A0_USDX"] = dict(n=len(a0c), b=b, t_hc1=t)
    b, t = ols_hc1(a0["S"], a0["y1"])
    res["A0_forex_tutti_giorni"] = dict(n=len(a0), b=b, t_hc1=t)
    print("A0", res["A0_forex"], res["A0_USDX"], res["A0_forex_tutti_giorni"])

    # ----- per coppia
    res["per_coppia"] = {}
    for k in PAIRS:
        yk = w1k[k] / sig_k[k]
        Kd = pd.DataFrame({"S": G["S"], "yk": yk, "dt1": G["dt1"]}, index=bd)
        Kd = Kd[Kd["S"].notna() & Kd["yk"].notna() & (Kd["dt1"] <= FINE_A)]
        b, t = ols_hc1(Kd["S"], Kd["yk"])
        res["per_coppia"][k] = dict(n=len(Kd), b=b, t_hc1=t)
    print("per coppia", res["per_coppia"])

    # ----- controlli fuso: ora server usata
    res["info_file"] = info
    res["controlli"] = dict(
        n_giorni_paniere=len(bd), n_giorni_W2_A=len(A2w2),
        server_16NY_2017_03_15=str(server_time("EURUSD", dt.datetime(2017, 3, 15, 16))),
        server_16NY_2017_07_03=str(server_time("EURUSD", dt.datetime(2017, 7, 3, 16))),
        server_16NY_2017_11_01=str(server_time("EURUSD", dt.datetime(2017, 11, 1, 16))),
        server_16NY_2018_01_10=str(server_time("EURUSD", dt.datetime(2018, 1, 10, 16))),
        max_dt1_A=str(A["dt1"].max().date()),
    )

    out = A[["dt", "dt1", "S", "sigB", "W1", "W2", "y1", "y2"]].copy()
    out["dt"] = out["dt"].dt.strftime("%Y-%m-%d")
    out["dt1"] = out["dt1"].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(OUT, "giornaliero_replica.csv"), sep=";", index=False, float_format="%.10g")
    with open(os.path.join(OUT, "risultati_replica.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)


if __name__ == "__main__":
    main()
