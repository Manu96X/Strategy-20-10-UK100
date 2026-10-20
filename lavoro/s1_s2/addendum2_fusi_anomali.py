# -*- coding: utf-8 -*-
"""ADDENDUM 2 «DOPO I NUMERI» (20/10/2026): sensibilita' alle anomalie di fuso trovate dal controllo a mano.
Periodi esclusi: feed Pepperstone 30/10/2017 -> 04/03/2018 (NY+8 invece di NY+7, verificato sul tick volume dell'apertura
USA); GBPUSD FTMO 08/02/2019 -> 20/09/2019 (UTC+1); forex FTMO 30/10/2017 -> 02/11/2017 (NY+7 invece dell'ora di Atene).
Ricalcola i 14 test primari di S1/S2 (netto base z, t CR1, p) senza i trade colpiti; ricalcola anche la pendenza A1 di H1."""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s12_comune as C
R = os.path.join(C.QUI, "risultati")
PEP = pd.Timestamp("2017-10-30"), pd.Timestamp("2018-03-04 23:59")
def colpito(x, ipotesi):
    d = pd.to_datetime(x.data_ny)
    pep = {"S1": ["XAU", "US100", "US500"], "S2": ["US500", "US100", "US30", "US2000", "GER40", "UK100"]}[ipotesi]
    m = x.strumento.isin(pep) & (d >= PEP[0]) & (d <= PEP[1])
    if ipotesi == "S1":
        m |= (x.strumento == "GBPUSD") & (d >= "2019-02-08") & (d <= "2019-09-20")
        m |= x.strumento.isin(["EURUSD", "GBPUSD", "USDJPY"]) & (d >= "2017-10-30") & (d <= "2017-11-02")
    return m
out = []
for ip in ("S1", "S2"):
    X = pd.read_csv(os.path.join(R, f"{ip}_trade.csv"), sep=";", decimal=",")
    X["zb"] = X.netto_base / X.sigma
    for tag, Y in (("originale", X), ("senza_anomalie", X[~colpito(X, ip)])):
        A = Y.groupby(["test_id", "chiave"]).agg(zb=("zb", "mean"), data_ny=("data_ny", "first")).reset_index()
        for tid, a in A.groupby("test_id"):
            m, t, G = C.cr1(a.zb.to_numpy(), pd.to_datetime(a.data_ny).dt.normalize().to_numpy())
            out.append(dict(test_id=tid, versione=tag, n=len(a), netto_base_z=m, t=t, p=float(stats.t.sf(t, G - 1))))
O = pd.DataFrame(out).pivot(index="test_id", columns="versione", values=["n", "netto_base_z", "t", "p"])
pd.set_option("display.width", 220)
print(O.round(4).to_string())
O.to_csv(os.path.join(R, "ADDENDUM2_SENSIBILITA_FUSI.csv"), sep=";", decimal=",")
# H1 stadio A: pendenza senza i giorni colpiti (segnale Pepperstone nell'inverno 2017-18; GBPUSD nel paniere dal 08/02/2019)
H = pd.read_csv(os.path.join(C.REPO, "lavoro", "h1_dollaro", "risultati", "H1_stadio_A_giornaliero.csv"), sep=";", decimal=",", parse_dates=["dt", "dt1"])
k = ~(((H.dt >= PEP[0]) & (H.dt <= PEP[1])) | (H.dt1 >= pd.Timestamp("2019-02-08")) | ((H.dt >= "2017-10-30") & (H.dt <= "2017-11-02")))
for tag, h in (("originale", H), ("senza_anomalie", H[k])):
    b = np.polyfit(h.S, h.y1, 1)[0]
    print("H1 A1", tag, "n", len(h), "pendenza", round(b, 4))
