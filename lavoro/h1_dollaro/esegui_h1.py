# -*- coding: utf-8 -*-
"""Esecuzione di H1 secondo PROTOCOLLO_H1.md.
Uso: python3 -I esegui_h1.py A     (stadio A + analisi descrittive, solo dati di scoperta < 2024)
     python3 -I esegui_h1.py B     (stadio B, 2024: si apre SOLO se A1 non e' ROSSO)"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h1_motore as M

OUT = os.path.join(M.QUI, "risultati")
FINE_A = pd.Timestamp("2019-04-19")
INIZIO_SCOPERTA_USDX = pd.Timestamp("2019-04-22")


def campione(B, filtro):
    ok = B.S.notna() & B.y1.notna() & B.sigB.notna() & filtro
    return B[ok].copy()

def pendenza(x, y, nrep=100_000):
    b, t, e = M.ols(x, y)
    return dict(n=int(len(x)), b=b, t_hc1=t, p_unilaterale=M.p_perm_unilaterale(x, y, nrep) if nrep else None)

def senza_influenti(x, y, quota=0.02):
    b, t, e = M.ols(x, y)
    n = len(x); h = 1 / n + (x - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum()
    s2 = (e ** 2).sum() / (n - 2); D = e ** 2 / (2 * s2) * h / (1 - h) ** 2
    tieni = D < np.quantile(D, 1 - quota)
    b2, t2, _ = M.ols(x[tieni], y[tieni])
    return dict(n=int(tieni.sum()), b=b2, t_hc1=t2, p_unilaterale=M.p_perm_unilaterale(x[tieni], y[tieni], 20_000))

def blocco_strategia(A, spread, swap):
    out = {}
    W2 = A[A.y2.notna()]
    for fin, D in (("W2", W2), ("W1", A)):
        for sc in ("base", "stress"):
            netto, lordo, costo = M.strategia(D, D.S, fin, sc, spread, swap)
            m, t, n = M.t_media(netto)
            out[f"{fin}_{sc}"] = dict(n=n, netto_z=m, t=t, lordo_z=float(np.nanmean(lordo)), costo_z=float(np.nanmean(costo)),
                                     quota_positivi=float(np.mean(netto > 0)))
    return out

def verdetto_A1(r):
    if r["b"] < 0 and r["p_unilaterale"] < 0.05: return "VERDE"
    if r["b"] < 0 and r["p_unilaterale"] < 0.20: return "GIALLO"
    return "ROSSO"


def stadio_A():
    spread, swap = M.tabella_spread(), M.swap_frazione()
    B = M.tabella_giornaliera("scoperta", "2016-11-01", "2023-12-31")
    assert B.dt.max() < pd.Timestamp("2024-01-01")
    A = campione(B, B.dt1 <= FINE_A)
    R = {"periodo_A": [str(A.dt.min().date()), str(A.dt1.max().date())]}
    x, y = A.S.to_numpy(), A.y1.to_numpy()
    R["A1"] = pendenza(x, y); R["A1"]["verdetto"] = verdetto_A1(R["A1"])
    R["A2_e_W1_netto"] = blocco_strategia(A, spread, swap)
    # --- descrittive
    R["per_anno"] = {}
    for an, g in A.groupby(A.dt1.dt.year):
        nb, _, _ = M.strategia(g[g.y2.notna()], g[g.y2.notna()].S, "W2", "base", spread, swap)
        R["per_anno"][int(an)] = dict(n=int(len(g)), b=M.ols(g.S.to_numpy(), g.y1.to_numpy())[0],
                                      W2_netto_base=float(np.nanmean(nb)))
    R["per_coppia"] = {}
    for k, s in M.COPPIE.items():
        yk = (s * np.log(A[f"P1_{k}"] / A[f"P_{k}"]) / A[f"sig_{k}"]).to_numpy(); ok = np.isfinite(yk)
        R["per_coppia"][k] = pendenza(x[ok], yk[ok], 20_000)
    for nome, col in (("solo_XAU", "zXAU"), ("solo_XAG", "zXAG")):
        D = A[A[col].notna()]
        R[nome] = pendenza(D[col].to_numpy(), D.y1.to_numpy(), 20_000)
    R["W2_pendenza"] = pendenza(A[A.y2.notna()].S.to_numpy(), A[A.y2.notna()].y2.to_numpy(), 20_000)
    R["senza_2pct_influenti"] = senza_influenti(x, y)
    D = A[A.y2.notna()]; Sl = D.S / D.S.abs().mean()
    nb, lb, cb = M.strategia(D, D.S, "W2", "base", spread, swap)
    R["W2_lineare_base"] = dict(netto_z=float(np.nanmean(Sl.abs().to_numpy() * nb)),
                                lordo_z=float(np.nanmean(-Sl.to_numpy() * D.y2.to_numpy())))
    # prezzo robusto (mediana degli ultimi 5 close) per i file forex
    Br = M.tabella_giornaliera("scoperta", "2016-11-01", "2019-06-30", robusto=True)
    Ar = campione(Br, Br.dt1 <= FINE_A)
    R["prezzo_robusto"] = pendenza(Ar.S.to_numpy(), Ar.y1.to_numpy(), 20_000)
    # C1: USDX Pepperstone nello stadio A (mai visto)
    U = M.serie_usdx("scoperta", "2016-11-01", "2023-12-31")
    J = A[["S"]].join(U[["y1", "dt1"]].rename(columns={"y1": "yU", "dt1": "dt1U"}), how="inner").dropna()
    J = J[J.dt1U <= FINE_A]
    R["C1_USDX_stadioA"] = pendenza(J.S.to_numpy(), J.yU.to_numpy(), 20_000)
    # A0: diagnostico sul periodo della scoperta (forex contro USDX sugli stessi giorni)
    P0 = campione(B, (B.dt >= INIZIO_SCOPERTA_USDX) & ~((B.dt.dt.year == 2020) & (B.fusi_diversi | B.fusi_diversi1)))
    J0 = P0[["S", "y1"]].join(U[["y1"]].rename(columns={"y1": "yU"}), how="inner").dropna()
    R["A0_forex_periodo_scoperta"] = pendenza(J0.S.to_numpy(), J0.y1.to_numpy(), 20_000)
    R["A0_USDX_stessi_giorni"] = pendenza(J0.S.to_numpy(), J0.yU.to_numpy(), 20_000)
    R["A0_corr_paniere_USDX"] = float(np.corrcoef(J0.y1, J0.yU)[0, 1])
    # concordanza: segnale dai metalli FTMO (fuso come il forex FTMO fino al 2020)
    try:
        mf = {m: M.serie(f"{m}_FTMO", "scoperta", "2016-11-01", "2019-06-30", M.regime_ftmo_fx) for m in ("XAU", "XAG")}
        SF = ((mf["XAU"].z + mf["XAG"].z) / 2).reindex(A.index)
        ok = SF.notna().to_numpy()
        R["segnale_metalli_FTMO"] = pendenza(SF.to_numpy()[ok], y[ok], 20_000)
        R["corr_segnale_PEP_FTMO"] = float(np.corrcoef(SF.to_numpy()[ok], x[ok])[0, 1])
    except Exception as e:
        R["segnale_metalli_FTMO"] = f"non calcolato: {e}"
    # qualità del campione
    R["qualita"] = dict(righe_comuni=int(len(B)), giorni_A=int(len(A)), giorni_A_con_W2=int(A.y2.notna().sum()),
                        sd_S=float(A.S.std()), sd_y1=float(A.y1.std()), sd_y2=float(A.y2.std()),
                        sigB_mediana_bps=float(A.sigB.median() * 1e4), giorni_fusi_diversi_A=int(A.fusi_diversi.sum()))
    cols = ["dt", "dt1", "zXAU", "zXAG", "S", "rB", "sigB", "W1", "W2", "y1", "y2"]
    A[cols].to_csv(os.path.join(OUT, "H1_stadio_A_giornaliero.csv"), sep=";", decimal=",", index=False)
    json.dump(R, open(os.path.join(OUT, "H1_stadio_A.json"), "w"), indent=1, default=float)
    return R


def stadio_B():
    RA = json.load(open(os.path.join(OUT, "H1_stadio_A.json")))
    if RA["A1"]["verdetto"] == "ROSSO":
        sys.exit("A1 ROSSO: H1 bocciata, il 2024 resta sigillato.")
    spread, swap = M.tabella_spread(), M.swap_frazione()
    BA = M.tabella_giornaliera("scoperta", "2016-11-01", "2023-12-31")
    A = campione(BA, BA.dt1 <= FINE_A)
    B = M.tabella_giornaliera("validazione_2024", "2023-11-01", "2024-12-31")
    V = campione(B, (B.dt1 >= pd.Timestamp("2024-01-01")) & (B.dt1 <= pd.Timestamp("2024-12-31")))
    R = {"periodo_B": [str(V.dt.min().date()), str(V.dt1.max().date())]}
    R["B1"] = pendenza(V.S.to_numpy(), V.y1.to_numpy())
    AB = pd.concat([A, V])
    R["A_piu_B"] = pendenza(AB.S.to_numpy(), AB.y1.to_numpy())
    R["B2_e_W1_netto"] = blocco_strategia(V, spread, swap)
    R["AB_strategia"] = blocco_strategia(AB, spread, swap)
    R["B_W2_pendenza"] = pendenza(V[V.y2.notna()].S.to_numpy(), V[V.y2.notna()].y2.to_numpy(), 20_000)
    R["B_per_coppia"] = {}
    for k, s in M.COPPIE.items():
        yk = (s * np.log(V[f"P1_{k}"] / V[f"P_{k}"]) / V[f"sig_{k}"]).to_numpy(); ok = np.isfinite(yk)
        R["B_per_coppia"][k] = pendenza(V.S.to_numpy()[ok], yk[ok], 20_000)
    U = M.serie_usdx("validazione_2024", "2023-11-01", "2024-12-31")
    J = V[["S"]].join(U[["y1", "dt1"]].rename(columns={"y1": "yU", "dt1": "dt1U"}), how="inner").dropna()
    J = J[(J.dt1U >= pd.Timestamp("2024-01-01"))]
    R["B_USDX"] = pendenza(J.S.to_numpy(), J.yU.to_numpy(), 20_000)
    # verdetto pre-registrato
    sA = RA["A2_e_W1_netto"]; sB = R["B2_e_W1_netto"]; sAB = R["AB_strategia"]
    effetto = (R["A_piu_B"]["p_unilaterale"] < 0.05) and RA["A1"]["b"] < 0 and R["B1"]["b"] < 0
    netto = (sA["W2_base"]["netto_z"] > 0 and sB["W2_base"]["netto_z"] > 0 and sAB["W2_stress"]["netto_z"] > 0
             and sAB["W2_base"]["t"] >= 1.645)
    R["verdetto"] = "PROMOSSA alla F4" if (effetto and netto) else ("EFFETTO REALE MA NON SFRUTTABILE" if effetto else "BOCCIATA")
    cols = ["dt", "dt1", "zXAU", "zXAG", "S", "rB", "sigB", "W1", "W2", "y1", "y2"]
    V[cols].to_csv(os.path.join(OUT, "H1_stadio_B_giornaliero.csv"), sep=";", decimal=",", index=False)
    json.dump(R, open(os.path.join(OUT, "H1_stadio_B.json"), "w"), indent=1, default=float)
    return R


if __name__ == "__main__":
    R = stadio_A() if sys.argv[1] == "A" else stadio_B()
    print(json.dumps(R, indent=1, default=float))
