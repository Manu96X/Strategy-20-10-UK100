import sys, csv, datetime as dt
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/revisione/meccanica")
from mano import *
# righe del file
F = {}
with open("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter=";"):
        t = dt.datetime(1970, 1, 1) + dt.timedelta(microseconds=int(r["ts_in"]) // 1000)
        F[(r["cella"], r["feed"], r["scenario"], t)] = r
fl = lambda x: float(x.replace(",", "."))
def ns2dt(x): return dt.datetime(1970, 1, 1) + dt.timedelta(microseconds=int(x) // 1000)
casi = []
def caso(nome, cella, simb, feed, scen, t_in, m, scad, chius=None, fine_barra=None):
    r = F[(cella, feed, scen, t_in)]
    d = fl(r["d"]); print(f"\n##### {nome}: cella {cella} {feed} {scen}  data_loc {r['data_loc']} k {r['k']}  d = {m} x ATR {fl(r['atr']):.6f} = {m*fl(r['atr']):.6f} (file {d:.6f})")
    if fine_barra: print(f"  fine barra segnale (server) = {fine_barra}; primo M1 >= fine = ingresso {t_in}")
    x = trade(nome, simb, feed, scen, t_in, d, scad, chius)
    att = dict(tipo=r["tipo"], ts_out=ns2dt(r["ts_out"]), R=fl(r["R"]), costo_R=fl(r["costo_R"]), fill=fl(r["fill"]), px=fl(r["px_out"]), notti=int(r["notti"]))
    dR = abs(x["R"] - att["R"])
    print(f"  CONFRONTO  atteso: {x['tipo']} {x['ts_out']} R {x['R']:+.6f} costo_R {x['costo_R']:.6f}  |  file: {att['tipo']} {att['ts_out']} R {att['R']:+.6f} costo_R {att['costo_R']:.6f}  |dR| {dR:.2e}")
    casi.append((nome, cella, feed, scen, str(t_in), x["tipo"], att["tipo"], round(x["R"], 6), round(att["R"], 6), dR, abs(x["costo_R"] - att["costo_R"])))
L = "Europe/London"
# 1 A1 TEMPO 24h (lunedi' k=0: barra 08-09 Londra = 09:00 locale -> server 11:00 in luglio)
t = S("2017-07-24 11:00"); caso("T1 A1 TEMPO 24h", "A1", "UK100", "PEP", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2017,7,24), 9*60, L))
# 2 A1 SL ordinario
t = S("2017-11-13 12:00"); caso("T2 A1 SL", "A1", "UK100", "PEP", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2017,11,13), 10*60, L))
# 3 A1 TP
t = S("2018-03-26 18:00"); caso("T3 A1 TP", "A1", "UK100", "PEP", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2018,3,26), 16*60, L))
# 4 A1 stress (stesso ingresso di T1): mkt 0.5 all'ingresso e all'uscita, spread x1.5, swap 2
t = S("2017-07-24 11:00"); caso("T4 A1 TEMPO stress", "A1", "UK100", "PEP", "stress", t, 2.5, t + dt.timedelta(hours=24))
# 5 A5 venerdi': chiusura forzata 15' prima dell'ultima quotazione del venerdi'
t = S("2017-07-28 18:00"); u = ultima("UK100", "PEP", dt.date(2017, 7, 28)); print("\nultima quotazione ven 28/07/2017:", u)
caso("T5 A5 CHIUSURA venerdi'", "A5", "UK100", "PEP", "base", t, 2.0, t + dt.timedelta(hours=24), chius=u)
# 6 A5 mercoledi' -> giovedi' (swap triplo)
t = S("2017-09-06 11:00"); caso("T6 A5 mercoledi' swap x3", "A5", "UK100", "PEP", "base", t, 2.0, t + dt.timedelta(hours=24))
# 7 A10 stress: SL in gap mercoledi' notte (CFD, barra 18-19 server)
t = S("2018-12-05 19:00"); caso("T7 A10 SL in gap stress", "A10", "UK100", "PEP", "stress", t, 2.0, t + dt.timedelta(hours=24), fine_barra=S("2018-12-05 19:00"))
# 8 A2 24 barre cash: lun k0 -> +24 barre = mer k6 (9 barre/giorno: lun k1-k8 = 8, mar 9 -> 17, mer k0-k6 = 7 -> 24) fine 15:00 Londra
t = S("2017-07-24 11:00"); caso("T8 A2 TEMPO 24 barre", "A2", "UK100", "PEP", "base", t, 2.5, fine_sess_srv(dt.date(2017,7,26), 15*60, L))
# 9 A3 sera stessa 23:40 server
t = S("2017-09-18 11:00"); u = ultima("UK100", "PEP", dt.date(2017, 9, 18)); print("\nultima quotazione lun 18/09/2017:", u)
caso("T9 A3 sera 23:40", "A3", "UK100", "PEP", "base", t, 2.5, min(S("2017-09-18 23:40"), u - dt.timedelta(minutes=15)))
# 10 A9 notturno stress (spread 05:00 = 3.75 x 1.5)
t = S("2017-07-17 05:00"); caso("T10 A9 CFD notte stress", "A9", "UK100", "PEP", "stress", t, 2.5, t + dt.timedelta(hours=24), fine_barra=S("2017-07-17 05:00"))
# 11 A7 24 barre limitate dal venerdi'
t = S("2017-08-11 11:00"); u = ultima("UK100", "PEP", dt.date(2017, 8, 11)); print("\nultima quotazione ven 11/08/2017:", u)
caso("T11 A7 CHIUSURA venerdi' (24 barre)", "A7", "UK100", "PEP", "base", t, 2.0, fine_sess_srv(dt.date(2017,8,15), 15*60, L), chius=u)
# 12 B1 GER40 FTMO
t = S("2022-02-14 14:00"); caso("T12 B1 GER40 FTMO", "B1", "GER40", "FTMO", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2022,2,14), 13*60, "Europe/Berlin"))
# 13 B2 US500 PEP
t = S("2020-09-21 17:30"); caso("T13 B2 US500 PEP", "B2", "US500", "PEP", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2020,9,21), 10*60+30, "America/New_York"))
# 14 B3 US100 PEP
t = S("2017-08-21 17:30"); caso("T14 B3 US100 PEP", "B3", "US100", "PEP", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2017,8,21), 10*60+30, "America/New_York"))
# 15 A1 buco dati 31/12/2019
t = S("2019-12-30 18:30"); caso("T15 A1 SL dopo buco dati", "A1", "UK100", "PEP", "base", t, 2.5, t + dt.timedelta(hours=24), fine_barra=fine_sess_srv(dt.date(2019,12,30), 16*60+30, L))
print("\nRIEPILOGO")
for c in casi: print(c)
print("max |dR| =", max(c[9] for c in casi), " max |dcosto_R| =", max(c[10] for c in casi))
