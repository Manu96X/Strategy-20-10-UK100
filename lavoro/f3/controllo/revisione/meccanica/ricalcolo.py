# -*- coding: utf-8 -*-
"""Revisione avversaria F3 - meccanica dei trade e costi.
Ricalcolo INDIPENDENTE (non importa motore_f3/barre) di ogni trade di TRADE_scoperta.csv a partire
da ts_in e d del file, sui dati M1 grezzi di /home/user/dati_scoperta.
Uso: python3 -I ricalcolo.py  -> scrive ricalcolo_trade.pkl e stampa le discrepanze."""
import pandas as pd, numpy as np, datetime as dt, pickle, sys
from zoneinfo import ZoneInfo
import holidays

D = "/home/user/dati_scoperta/"
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
OUT = "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/revisione/meccanica/"
SC = {"lordo": (0.0, 0.0, 0.0, 0.0), "base": (1.0, 0.8, 0.0, 0.5), "stress": (1.5, 2.0, 0.5, 2.0)}  # spread x, slip, mkt, swap
FILE = {("UK100","PEP"):("UK100 Pepperstone m1","2017-06-06"), ("UK100","FTMO"):("UK100 FTMO m1","2021-09-14"),
        ("GER40","PEP"):("GER40 Pepperstone m1","2020-06-11"), ("GER40","FTMO"):("GER40 FTMO m1","2021-12-28"),
        ("US500","PEP"):("US500 m1 - Pepperstone","2020-07-13"), ("US500","FTMO"):("US500 m1 - FTMO","2021-09-14"),
        ("US100","PEP"):("NAS100 m1 - FTPepperstone","2017-06-09"), ("US100","FTMO"):("US100 m1 - FTMO","2021-09-14")}
SPFILE = {"UK100":"UK100 FTMO m1","GER40":"GER40 FTMO m1","US500":"US500 m1 - FTMO","US100":"US100 m1 - FTMO"}
SESS = {"UK100":("Europe/London",8*60,16*60+30), "GER40":("Europe/Berlin",9*60,17*60+30), "US500":("America/New_York",9*60+30,16*60), "US100":("America/New_York",9*60+30,16*60)}
CELLA = {"A1":("UK100","sess",2.5,"24h"),"A2":("UK100","sess",2.5,"24barre"),"A3":("UK100","sess",2.5,"sera"),
         "A4":("UK100","sess",2.0,"24h"),"A5":("UK100","sess",2.0,"24h"),"A6":("UK100","sess",2.0,"24h"),
         "A7":("UK100","sess",2.0,"24barre"),"A9":("UK100","cfd",2.5,"24h"),"A10":("UK100","cfd",2.0,"24h"),
         "B1":("GER40","sess",2.5,"24h"),"B2":("US500","sess",2.5,"24h"),"B3":("US100","sess",2.5,"24h")}
NS_MIN = 60_000_000_000; NS_H = 60*NS_MIN

def tab_spread(nome):
    righe = open("/home/user/Strategy-20-10-UK100/lavoro/f0/risultati/SPREAD_mediana_per_ora_server.csv", encoding="utf-8").read().splitlines()
    hdr = righe[0].split(";")
    for r in righe[1:]:
        v = r.split(";")
        if v[0] == nome and v[1] == "2026":
            m = {hdr[i]: (float(v[i].replace(",", ".")) if v[i] else None) for i in range(2, len(hdr))}
            out = {}
            for h in range(24):
                x = m.get("h%02d" % h)
                if x is None:  # ora senza quote: massimo delle vicine (regola dichiarata dal motore)
                    x = max(y for y in (m.get("h%02d" % ((h-1) % 24)), m.get("h%02d" % ((h+1) % 24))) if y is not None)
                out[h] = x
            return out

def carica(nome, inizio):
    r = pd.read_csv(D + nome + ".csv", sep="\t", dtype=str)
    ts = pd.to_datetime(r.iloc[:, 0] + " " + r.iloc[:, 1], format="%Y.%m.%d %H:%M:%S")
    m = ts >= pd.Timestamp(inizio)
    return dict(ts=ts[m].values.astype("datetime64[ns]").astype("int64"), o=r.iloc[:, 2][m].astype(float).values, h=r.iloc[:, 3][m].astype(float).values,
                l=r.iloc[:, 4][m].astype(float).values)

def srv(ns): return pd.Timestamp(int(ns))

def loc_to_srv(date, minutes, tz):
    t = dt.datetime.combine(date, dt.time()) + dt.timedelta(minutes=int(minutes))
    u = t.replace(tzinfo=ZoneInfo(tz)).astimezone(ZoneInfo("America/New_York"))
    return pd.Timestamp(u.replace(tzinfo=None) + dt.timedelta(hours=7))

def srv_to_loc(ts_ns, tz):
    t = pd.Timestamp(int(ts_ns)).to_pydatetime() - dt.timedelta(hours=7)
    return t.replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo(tz)).replace(tzinfo=None)

class Cal:
    """giornate server di trading (con dati, lun-ven, non festive per il simbolo) e loro ultima quotazione"""
    def __init__(self, F, simb):
        g = pd.Series(F["ts"]).groupby(F["ts"] // (24*NS_H)).max()
        fest = set(holidays.UK(subdiv="ENG", years=range(2016, 2027)).keys()) if simb == "UK100" else set()
        self.ultima = {}
        for day, last in g.items():
            d = (pd.Timestamp(0) + pd.Timedelta(days=int(day))).date()
            if d.weekday() < 5 and d not in fest: self.ultima[d] = int(last)
        self.giorni = sorted(self.ultima)
        self.pos = {d: i for i, d in enumerate(self.giorni)}
    def chiusura_dopo(self, d):
        i = self.pos[d]
        return i == len(self.giorni) - 1 or (self.giorni[i+1] - d).days > 1
    def prossima_chiusura(self, d):
        i = self.pos[d]
        while not self.chiusura_dopo(self.giorni[i]): i += 1
        return self.ultima[self.giorni[i]]

def barre_sess_fini(F, simb):
    tz, a0, c0 = SESS[simb]
    fest = {"UK100": set(holidays.UK(subdiv="ENG", years=range(2016, 2027)).keys()),
            "US500": set(holidays.NYSE(years=range(2016, 2027)).keys()), "US100": set(holidays.NYSE(years=range(2016, 2027)).keys())}.get(simb)
    if fest is None:
        fest = set()
        for y in range(2016, 2027):
            for d, n in holidays.Germany(years=y).items():
                if n in ("Karfreitag", "Ostermontag", "Good Friday", "Easter Monday"): fest.add(d)
            for m, gg in [(1, 1), (5, 1), (12, 24), (12, 25), (12, 26), (12, 31)]: fest.add(dt.date(y, m, gg))
    s = pd.Series(pd.to_datetime(F["ts"])) - pd.Timedelta(hours=7)
    loc = s.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").dt.tz_convert(tz).dt.tz_localize(None)
    mins = loc.dt.hour * 60 + loc.dt.minute
    ok = loc.notna() & (mins >= a0) & (mins < c0) & (loc.dt.weekday < 5)
    ok &= ~loc.dt.date.isin(fest)
    key = pd.DataFrame({"d": loc[ok].dt.date, "k": ((mins[ok] - a0) // 60).astype(int)}).drop_duplicates().sort_values(["d", "k"])
    fini = [loc_to_srv(d, min(a0 + (k+1)*60, c0), tz).value for d, k in zip(key.d, key.k)]
    return list(zip(key.d, key.k)), np.array(fini, dtype="int64")

def simula(F, cal, ts_in, d, scad, tab, scen, simb, sl_mode="codice"):
    spx, slipv, mkt, swp = SC[scen]
    i0 = int(np.searchsorted(F["ts"], ts_in)); assert F["ts"][i0] == ts_in
    giorno = srv(ts_in).date()
    if giorno not in cal.pos: return dict(err="giorno non di trading")
    if cal.chiusura_dopo(giorno) and ts_in >= cal.ultima[giorno] - 2*NS_H: return dict(err="regola 2 ore")
    t_forz = cal.prossima_chiusura(giorno) - 15*NS_MIN
    t_exit = min(scad, t_forz)
    sp = tab[srv(ts_in).hour] * spx
    fill = F["o"][i0] + sp + mkt
    SL, TP = fill - d, fill + 2*d
    j = i0; tipo = None
    while F["ts"][j] < t_exit:
        if F["l"][j] <= SL:
            tipo = "SL"
            px = min(F["o"][j], SL - slipv) if sl_mode == "codice" else min(F["o"][j], SL) - slipv
            slip = slipv
            break
        if F["h"][j] >= TP:
            tipo = "TP"; px = TP; slip = 0.0; break
        j += 1
    if tipo is None:
        px = F["o"][j] - mkt; slip = 0.0
        tipo = "TEMPO" if t_exit == scad else "CHIUSURA"
    gout = srv(F["ts"][j]).date()
    notti = 0; x = giorno
    while x < gout:
        notti += 3 if x.weekday() == 2 else 1
        x += dt.timedelta(days=1)
    swap = notti * swp
    R = (px - fill - swap) / d
    nm = 2 if tipo in ("TEMPO", "CHIUSURA") else 1
    return dict(ts_out=int(F["ts"][j]), fill=fill, sl=SL, tp=TP, px_out=px, tipo=tipo, spread=sp, notti=notti, swap=swap, R=R,
                costo_R=(sp + mkt*nm + slip + swap)/d, j=j, i0=i0, gap_open=F["o"][j] < SL if tipo == "SL" else False)

def main():
    T = pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
    T = T[T.cella != "A8"].copy()
    res = []
    for (simb, fk), (nome, ini) in FILE.items():
        celle = [c for c, v in CELLA.items() if v[0] == simb]
        sub = T[T.cella.isin(celle) & (T.feed == fk)]
        if sub.empty: continue
        F = carica(nome, ini); cal = Cal(F, simb); tab = tab_spread(SPFILE[simb])
        keys, fini = barre_sess_fini(F, simb)
        kpos = {kk: i for i, kk in enumerate(keys)}
        tz = SESS[simb][0]
        print(simb, fk, len(F["ts"]), "M1;", len(keys), "barre sess", flush=True)
        for idx, t in sub.iterrows():
            _, tipo_b, m, usc = CELLA[t.cella]
            dloc = dt.date.fromisoformat(t.data_loc)
            # fine della barra segnale e primo M1 >= fine
            if tipo_b == "sess":
                p = kpos[(dloc, int(t.k))]; fine = int(fini[p])
            else:
                fine = int((pd.Timestamp(t.data_loc) + pd.Timedelta(hours=int(t.k) + 1)).value)
            i_att = int(np.searchsorted(F["ts"], fine))
            ts_in_att = int(F["ts"][i_att])
            ok_ingresso = (ts_in_att == t.ts_in) and (ts_in_att - fine <= 15*NS_MIN)
            if usc == "24h": scad = int(t.ts_in) + 24*NS_H
            elif usc == "24barre": scad = int(fini[p + 24])
            else:
                g0 = srv(t.ts_in).normalize().value
                scad = min(g0 + 23*NS_H + 40*NS_MIN, cal.ultima[srv(t.ts_in).date()] - 15*NS_MIN)
            r = simula(F, cal, int(t.ts_in), float(t.d), scad, tab, t.scenario, simb)
            r2 = simula(F, cal, int(t.ts_in), float(t.d), scad, tab, t.scenario, simb, sl_mode="protocollo")
            r.update(idx=idx, ok_ingresso=ok_ingresso, ritardo_min=(ts_in_att - fine)/NS_MIN, d_ok=abs(t.d - m*t.atr) < 1e-9,
                     R_protocollo=r2.get("R"), scad=scad)
            # buchi >= 2 ore dentro la tenuta
            if "j" in r:
                seg = F["ts"][r["i0"]:r["j"]+1]
                r["buco_max_min"] = float(np.diff(seg).max()/NS_MIN) if len(seg) > 1 else 0.0
            res.append(r)
    Rz = pd.DataFrame(res).set_index("idx")
    pickle.dump(Rz, open(OUT + "ricalcolo_trade.pkl", "wb"))
    X = T.join(Rz, rsuffix="_mio")
    X["dR"] = (X.R - X.R_mio).abs(); X["dC"] = (X.costo_R - X.costo_R_mio).abs()
    print("trade ricalcolati:", len(X), " errori:", X.err.notna().sum() if "err" in X else 0)
    print("ingresso coerente (primo M1 >= fine barra, <=15'):", X.ok_ingresso.sum(), "/", len(X))
    print("d = m*ATR:", X.d_ok.sum(), "/", len(X))
    print("tipo uguale:", (X.tipo == X.tipo_mio).sum(), " ts_out uguale:", (X.ts_out == X.ts_out_mio).sum(),
          " fill |diff|max:", (X.fill - X.fill_mio).abs().max(), " px_out |diff|max:", (X.px_out - X.px_out_mio).abs().max())
    print("notti uguali:", (X.notti == X.notti_mio).sum(), " |dR|max:", X.dR.max(), " |dcosto_R|max:", X.dC.max())
    print("trade con |dR| > 0.001:", (X.dR > 0.001).sum())
    X.to_pickle(OUT + "confronto.pkl")

if __name__ == "__main__":
    main()
