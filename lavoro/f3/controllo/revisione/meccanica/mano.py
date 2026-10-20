# -*- coding: utf-8 -*-
"""Ricalcolo 'a mano' di trade scelti: legge le RIGHE DI TESTO grezze del CSV M1 (nessun motore, nessun pandas per i prezzi)."""
import csv, datetime as dt
from zoneinfo import ZoneInfo
D = "/home/user/dati_scoperta/"
FILE = {("UK100","PEP"):"UK100 Pepperstone m1", ("UK100","FTMO"):"UK100 FTMO m1", ("GER40","PEP"):"GER40 Pepperstone m1",
        ("GER40","FTMO"):"GER40 FTMO m1", ("US500","PEP"):"US500 m1 - Pepperstone", ("US100","PEP"):"NAS100 m1 - FTPepperstone"}
SP = {"UK100": {9:1.65,10:0.85,11:0.75,12:0.75,13:0.65,14:0.75,15:0.75,16:0.75,17:0.75,18:0.85,19:1.65,20:1.45,21:1.45,22:1.45,23:5.71,1:5.31,2:4.85,3:4.15,4:3.95,5:3.75,6:3.65,7:3.65,8:3.85},
      "GER40": {14:1.13,17:1.23}, "US500": {17:0.56}, "US100": {17:1.45}}   # dalla riga 2026 di SPREAD_mediana_per_ora_server.csv
SC = {"lordo": (0.0, 0.0, 0.0, 0.0), "base": (1.0, 0.8, 0.0, 0.5), "stress": (1.5, 2.0, 0.5, 2.0)}
ULTIMA = {}  # cache ultima quotazione per giorno

def righe(simb, feed, da, a):
    """righe M1 grezze con da <= ts <= a (datetime server)"""
    out = []
    with open(D + FILE[(simb, feed)] + ".csv", encoding="utf-8") as f:
        next(f)
        pref = {(da + dt.timedelta(days=i)).strftime("%Y.%m.%d") for i in range((a - da).days + 2)}
        for r in f:
            if r[:10] not in pref: continue
            v = r.rstrip("\n").split("\t")
            t = dt.datetime.strptime(v[0] + " " + v[1], "%Y.%m.%d %H:%M:%S")
            if da <= t <= a: out.append((t, float(v[2]), float(v[3]), float(v[4]), r.rstrip("\n").replace("\t", " ")))
    return out

def ultima(simb, feed, giorno):
    rr = righe(simb, feed, dt.datetime.combine(giorno, dt.time()), dt.datetime.combine(giorno, dt.time(23, 59)))
    return rr[-1][0] if rr else None

def trade(nome, simb, feed, scen, t_in, d, scad, chius=None, sl_prima=True):
    spx, slip, mkt, swp = SC[scen]
    t_exit = scad if chius is None else min(scad, chius - dt.timedelta(minutes=15))
    rr = righe(simb, feed, t_in, t_exit + dt.timedelta(hours=6))
    assert rr[0][0] == t_in, rr[0]
    o0 = rr[0][1]; sp = SP[simb][t_in.hour] * spx
    fill = o0 + sp + mkt; SL = fill - d; TP = fill + 2 * d
    print(f"\n=== {nome}  [{scen}]  riga d'ingresso: {rr[0][4]}")
    print(f"  fill = open {o0} + spread {SP[simb][t_in.hour]}x{spx} + mkt {mkt} = {fill:.4f};  d = {d:.6f};  SL = {SL:.4f}  TP = {TP:.4f}")
    print(f"  scadenza regola = {scad}   chiusura forzata = {None if chius is None else chius - dt.timedelta(minutes=15)}  -> t_exit = {t_exit}")
    minL, maxH = 1e18, -1e18
    for (t, o, h, l, raw) in rr:
        if t >= t_exit:
            px = o - mkt; tipo = "TEMPO" if (chius is None or t_exit == scad) else "CHIUSURA"; tout = t; s_ = 0.0
            print(f"  nessun SL/TP prima di t_exit (low min {minL}, high max {maxH}); riga d'uscita: {raw}")
            break
        hitS, hitT = l <= SL, h >= TP
        if hitS or hitT:
            if hitS and (not hitT or sl_prima):
                px = min(o, SL - slip); tipo = "SL"; s_ = slip
                print(f"  low min prima = {minL}; riga SL: {raw}  -> px = min(open {o}, SL-slip {SL - slip:.4f}) = {px:.4f}"
                      f"   [protocollo: min(open,SL)-slip = {min(o, SL) - slip:.4f}]" + ("  ** anche TP nello stesso minuto **" if hitT else ""))
            else:
                px = TP; tipo = "TP"; s_ = 0.0
                print(f"  high max prima = {maxH}; riga TP: {raw}  -> px = TP {TP:.4f}")
            tout = t; break
        minL, maxH = min(minL, l), max(maxH, h)
    notti = 0; x = t_in.date()
    while x < tout.date():
        notti += 3 if x.weekday() == 2 else 1; x += dt.timedelta(days=1)
    swap = notti * swp; R = (px - fill - swap) / d
    nm = 2 if tipo in ("TEMPO", "CHIUSURA") else 1
    cR = (sp + mkt * nm + s_ + swap) / d
    print(f"  uscita {tout} {tipo}; notti {notti} (mercoledi' x3) -> swap {swap};  R = ({px:.4f} - {fill:.4f} - {swap}) / {d:.6f} = {R:.6f};  costo_R = {cR:.6f}")
    return dict(nome=nome, tipo=tipo, ts_out=tout, R=R, costo_R=cR, fill=fill, px=px, notti=notti)

def S(s): return dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
def fine_sess_srv(giorno, minuti, tz):
    t = dt.datetime.combine(giorno, dt.time()) + dt.timedelta(minutes=minuti)
    ny = t.replace(tzinfo=ZoneInfo(tz)).astimezone(ZoneInfo("America/New_York")).replace(tzinfo=None)
    return ny + dt.timedelta(hours=7)
