# -*- coding: utf-8 -*-
"""Test unitari delle funzioni comuni di S1/S2 (nessun rendimento: solo orari, calendari, ricerca delle barre)."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s12_comune as C
ok = 0
def chk(cond, msg):
    global ok
    assert cond, msg; ok += 1
# fusi: 08:30 NY -> server
t = pd.DatetimeIndex(["2019-03-15 08:30", "2019-06-14 08:30", "2020-03-13 08:30", "2023-11-03 08:30"])
s7 = C.a_server(t, "America/New_York", "NY7"); sfx = C.a_server(t, "America/New_York", "FX_FTMO")
chk(list(s7.strftime("%H:%M")) == ["15:30"] * 4, "NY7 sempre 15:30")
chk(list(sfx.strftime("%H:%M")) == ["14:30", "15:30", "15:30", "15:30"], f"FX FTMO: Atene nel 2019 disallineato {list(sfx)}")
# Europa -> server NY7: 17:30 Berlino il 15/03/2023 (USA in ora legale, Europa no) = 12:30 NY = 19:30 server
chk(C.a_server(pd.DatetimeIndex(["2023-03-15 17:30"]), "Europe/Berlin", "NY7")[0] == pd.Timestamp("2023-03-15 19:30"), "Berlino disallineato")
chk(C.a_server(pd.DatetimeIndex(["2023-06-15 17:30"]), "Europe/Berlin", "NY7")[0] == pd.Timestamp("2023-06-15 18:30"), "Berlino normale")
chk(C.a_server(pd.DatetimeIndex(["2023-06-15 16:30"]), "Europe/London", "NY7")[0] == pd.Timestamp("2023-06-15 18:30"), "Londra normale")
# prezzi su dati sintetici
df = pd.DataFrame({"ts": pd.to_datetime(["2023-01-02 10:00", "2023-01-02 10:01", "2023-01-02 10:07"]), "o": [1., 2., 3.], "c": [1.5, 2.5, 3.5], "m1_ok": [True, True, True]})
chk(C.prezzo_a(df, pd.DatetimeIndex(["2023-01-02 10:01"]))[0] == 2.0, "prezzo_a esatto")
chk(C.prezzo_a(df, pd.DatetimeIndex(["2023-01-02 10:02"]))[0] == 3.0, "prezzo_a entro 5 minuti con continuita'")
chk(np.isnan(C.prezzo_a(df, pd.DatetimeIndex(["2023-01-02 10:07"]))[0]), "prezzo_a senza barra nei 5 minuti prima (riapertura) escluso")
chk(np.isnan(C.prezzo_a(df, pd.DatetimeIndex(["2023-01-02 10:00"]))[0]), "prezzo_a alla prima barra: nessuna continuita'")
df2 = df.assign(m1_ok=[True, False, True]); chk(np.isnan(C.prezzo_a(df2, pd.DatetimeIndex(["2023-01-02 10:01"]))[0]), "barra di giorno non M1 esclusa")
chk(np.isnan(C.prezzo_a(df, pd.DatetimeIndex(["2023-01-02 09:50"]))[0]), "prezzo_a oltre 5 minuti")
chk(C.prezzo_prima(df, pd.DatetimeIndex(["2023-01-02 10:01"]))[0] == 1.5, "prezzo_prima esclude la barra che inizia a T")
chk(C.prezzo_prima(df, pd.DatetimeIndex(["2023-01-02 10:05"]))[0] == 2.5, "prezzo_prima entro 5 minuti")
chk(np.isnan(C.prezzo_prima(df, pd.DatetimeIndex(["2023-01-02 10:07"]))[0]), "prezzo_prima: barra di 6 minuti prima esclusa")
chk(np.isnan(C.prezzo_prima(df, pd.DatetimeIndex(["2023-01-02 10:20"]))[0]), "prezzo_prima oltre 5 minuti")
# calendario UTC+3 fisso -> New York
import s12_test as S
cal = S.calendario()
nfp = cal[(cal.evento == "Libri Paga Non Agricoli")]
chk((nfp.T_ny.dt.strftime("%H:%M") == "08:30").mean() > 0.99, "NFP alle 08:30 NY")
x = nfp[nfp.T_ny.dt.date == pd.Timestamp("2023-02-03").date()]
chk(len(x) == 1 and x.T_ny.iloc[0] == pd.Timestamp("2023-02-03 08:30"), "NFP invernale 03/02/2023 -> 08:30 NY")
chk(C.a_server(pd.DatetimeIndex(["2023-02-03 08:30"]), "America/New_York", "NY7")[0] == pd.Timestamp("2023-02-03 15:30"), "-> 15:30 server")
chk(C.a_server(pd.DatetimeIndex(["2019-01-04 08:30"]), "America/New_York", "FX_FTMO")[0] == pd.Timestamp("2019-01-04 15:30"), "NFP invernale 2019 forex FTMO 15:30")
chk(C.a_server(pd.DatetimeIndex(["2019-03-12 08:30"]), "America/New_York", "FX_FTMO")[0] == pd.Timestamp("2019-03-12 14:30"), "CPI disallineato 2019 forex FTMO 14:30")
fomc = cal[cal.evento == "Decisione del Tasso di Interesse della Fed"]
chk((fomc.T_ny.dt.strftime("%H:%M") == "14:00").mean() > 0.95, "FOMC alle 14:00 NY")
# calendari
g = C.giorni_borsa("NYSE", "2019-07-01", "2019-07-08")
chk(pd.Timestamp("2019-07-04") not in g and pd.Timestamp("2019-07-03") not in g and pd.Timestamp("2019-07-05") in g, "NYSE luglio 2019")
g = C.giorni_borsa("LSE", "2019-12-20", "2020-01-03")
chk(pd.Timestamp("2019-12-24") not in g and pd.Timestamp("2019-12-31") not in g and pd.Timestamp("2019-12-26") not in g and pd.Timestamp("2019-12-27") in g, "LSE Natale 2019")
g = C.giorni_borsa("XETRA", "2021-03-29", "2021-04-09")
chk(pd.Timestamp("2021-04-02") not in g and pd.Timestamp("2021-04-05") not in g and pd.Timestamp("2021-04-06") in g, "Xetra Pasqua 2021")
g = C.giorni_borsa("NYSE", "2022-04-14", "2022-04-19")
chk(pd.Timestamp("2022-04-15") not in g, "NYSE Venerdi Santo 2022")
# statistiche
x = np.array([1., 2., 3., 4.]); m, t, G = C.cr1(x, [1, 2, 3, 4]); chk(abs(m - 2.5) < 1e-12 and G == 4, "cr1")
chk(abs(C.p_unilaterale(1.6448536) - 0.05) < 1e-6, "p unilaterale")
b, s = C.bh([0.001, 0.02, 0.5, 0.04], 0.10); chk(list(b) == [True, True, False, True], f"bh {b}")
print("test unitari superati:", ok)
