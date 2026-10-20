# -*- coding: utf-8 -*-
"""Tabella dei costi CONGELATA per S1/S2 (PROTOCOLLO_S1_S2.md §5), versione definitiva prima dei numeri.
Fonti (solo dati di costo): colonna SPREAD (minimo del minuto) dei file FTMO dal 10/10/2025 al 09/10/2026 e spread
all'apertura del minuto (ask_o - bid_o) dei file M1BA (US100, oro) del 2025-2026. Il close del minuto serve SOLO come
denominatore per esprimere lo spread in bps (nessun rendimento calcolato). Nel 2025-2026 il server FTMO e' NY+7 tutto l'anno.
Il calendario esportato e' in UTC+3 FISSO: istante UTC = ora_server - 3 h.

Contesti (spread in bps, p75):
  S1_evento|<fascia>  : minuti T+3..T+5 dopo i dati USD ad alto impatto, per fascia oraria NY dell'evento;
  NY|<hh:mm>          : mezz'ora di New York (tutti i giorni feriali) che inizia a hh:mm;
  S2|<nome>           : minuto locale esatto +-2 minuti di ingresso, X1, pre-apertura X2 e placebo di S2.
Regole (§5): US100 e oro -> massimo fra FTMO e M1BA 2025-26 nello stesso contesto (se il M1BA ha >= 20 minuti);
forex -> base = max(2 x p75, 0,2 pip), stress = max(3 x p75, 0,3 pip); indici e oro -> stress = 1,5 x base;
US30 (nessun file FTMO) -> massimo fra lo spread della specifica riscalato col rapporto contesto/quotazione congelata di
US100 e lo spread di US100 e US500 nello stesso contesto.
Uscita: risultati/COSTI_TABELLA_CONGELATA.csv."""
import io, os, subprocess
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo

REPO = "/home/user/Strategy-20-10-UK100"
QUI = os.path.join(REPO, "lavoro", "s1_s2")
NY = ZoneInfo("America/New_York")
FILE = {"US100": "/home/user/dati_m1/US100 m1 - FTMO.csv", "US500": "/home/user/dati_m1/US500 m1 - FTMO.csv",
        "GER40": "/home/user/dati_m1/GER40 FTMO m1.csv", "UK100": "/home/user/dati_m1/UK100 FTMO m1.csv",
        "XAU": "/home/user/dati_m1/XAU-USD FTMO m1.csv", "US2000": "/home/user/dati_m1_nuovi/US2000 m1 FTMO.csv",
        "FRA40": "/home/user/dati_m1_nuovi/FRA40 m1 FTMO.csv", "EURUSD": "/home/user/dati_m1_nuovi/EURUSD m1 FTMO.csv",
        "GBPUSD": "/home/user/dati_m1_nuovi/GBPUSD m1 FTMO.csv", "USDJPY": "/home/user/dati_m1_nuovi/USDJPY m1 FTMO.csv"}
PIP = {"EURUSD": 1e-4, "GBPUSD": 1e-4, "USDJPY": 1e-2}
PREZZO_TIPICO_FX = {"EURUSD": 1.16, "GBPUSD": 1.34, "USDJPY": 150.0}   # solo per convertire i minimi in pip
DA, A = "2025.10.10", "2026.10.09"
FASCE_EVENTO = [("08:00", "08:59"), ("09:00", "09:59"), ("10:00", "11:59"), ("12:00", "16:59")]
S2_MINUTI = {
    "US500": ("America/New_York", {"ingresso": "16:01", "X1": "16:45", "X2": "09:25", "placebo_ingresso": "15:01", "placebo_X1": "15:45"}),
    "US100": ("America/New_York", {"ingresso": "16:01", "X1": "16:45", "X2": "09:25", "placebo_ingresso": "15:01", "placebo_X1": "15:45"}),
    "US2000": ("America/New_York", {"ingresso": "16:01", "X1": "16:45", "X2": "09:25", "placebo_ingresso": "15:01", "placebo_X1": "15:45"}),
    "GER40": ("Europe/Berlin", {"ingresso": "17:36", "X1": "18:15", "X2": "08:55", "placebo_ingresso": "16:36", "placebo_X1": "17:15"}),
    "FRA40": ("Europe/Paris", {"ingresso": "17:36", "X1": "18:15", "X2": "08:55", "placebo_ingresso": "16:36", "placebo_X1": "17:15"}),
    "UK100": ("Europe/London", {"ingresso": "16:36", "X1": "17:15", "X2": "07:55", "placebo_ingresso": "15:36", "placebo_X1": "16:15"})}


def leggi(path):
    txt = subprocess.run(["awk", "-F\t", f'NR > 1 && $1 >= "{DA}" && $1 <= "{A}" {{print $1"\\t"$2"\\t"$6"\\t"$9}}', path],
                         capture_output=True, text=True, check=True).stdout
    d = pd.read_csv(io.StringIO(txt), sep="\t", names=["d", "t", "c", "sp"], dtype=str)
    dig = int(d.c.head(5000).str.split(".").str[1].str.len().max())
    ts = pd.to_datetime(d.d + " " + d.t, format="%Y.%m.%d %H:%M:%S")
    sp = d.sp.astype(float) * 10.0 ** (-dig)
    return pd.DataFrame({"ny": ts - pd.Timedelta(hours=7), "bps": sp / d.c.astype(float) * 1e4})

def leggi_m1ba(pat):
    fs = sorted(x for x in os.listdir(REPO) if x.startswith(pat) and ("2025.0" in x or "2026.0" in x))
    b = pd.concat([pd.read_csv(os.path.join(REPO, x), sep=";") for x in fs])
    ts = pd.to_datetime(b.minuto_server, format="%Y.%m.%d %H:%M")
    return pd.DataFrame({"ny": (ts - pd.Timedelta(hours=7)).values, "bps": ((b.ask_o - b.bid_o) / b.bid_o * 1e4).values}), fs

def eventi_usd_ny(da, a):
    c = pd.read_csv(os.path.join(REPO, "calendario_economico.csv"), sep=";", skiprows=1, encoding="latin-1", low_memory=False)
    c = c[(c.valuta == "USD") & (c.importanza == 3) & (c.modo_orario == "ORARIO_ESATTO")]
    utc = pd.to_datetime(c.ora_server, format="%Y.%m.%d %H:%M") - pd.Timedelta(hours=3)
    ny = pd.DatetimeIndex(utc).tz_localize("UTC").tz_convert(NY).tz_localize(None)
    return pd.DatetimeIndex(sorted(set(ny[(ny >= da) & (ny <= a)])))

def serie(d):
    s = d.set_index("ny").bps
    return s[~s.index.duplicated()]

def contesti(d, ev):
    out, s = {}, serie(d)
    for (a, b) in FASCE_EVENTO:
        e = ev[(ev.strftime("%H:%M") >= a) & (ev.strftime("%H:%M") <= b)]
        k = np.concatenate([(e + pd.Timedelta(minutes=m)).values for m in (3, 4, 5)])
        v = s.reindex(k).dropna()
        out[f"S1_evento|{a}-{b}"] = (v.quantile(.75), len(v))
    for k, g in d.groupby(d.ny.dt.floor("30min").dt.strftime("%H:%M")):
        out[f"NY|{k}"] = (g.bps.quantile(.75), len(g))
    return out

def contesti_s2(d, strumento, giorni):
    out, s = {}, serie(d)
    tz, minuti = S2_MINUTI[strumento]
    for nome, hm in minuti.items():
        h, m = map(int, hm.split(":"))
        ny = (giorni + pd.Timedelta(hours=h, minutes=m)).tz_localize(ZoneInfo(tz)).tz_convert(NY).tz_localize(None)
        k = np.concatenate([(ny + pd.Timedelta(minutes=j)).values for j in (-2, -1, 0, 1, 2)])
        v = s.reindex(k).dropna()
        out[f"S2|{nome}"] = (v.quantile(.75), len(v))
    return out

ev = eventi_usd_ny(pd.Timestamp("2025-10-10"), pd.Timestamp("2026-10-09 23:59"))
FT = {}
for s, f in FILE.items():
    d = leggi(f); FT[s] = contesti(d, ev)
    if s in S2_MINUTI: FT[s].update(contesti_s2(d, s, pd.date_range("2025-10-10", "2026-10-09", freq="B")))
    print(s, "ok", flush=True)
MB = {}
for s, pat in (("US100", "M1BA_US100.cash_"), ("XAU", "M1BA_XAUUSD_")):
    d, fs = leggi_m1ba(pat); print(s, "M1BA:", fs)
    MB[s] = contesti(d, eventi_usd_ny(d.ny.min(), d.ny.max()))
    if s in S2_MINUTI: MB[s].update(contesti_s2(d, s, pd.DatetimeIndex(sorted(set(d.ny.dt.normalize())))))

righe = []
for s in FT:
    for ctx, (v, n) in FT[s].items():
        m1ba = MB.get(s, {}).get(ctx, (np.nan, 0))
        vb = max(v, m1ba[0]) if (np.isfinite(m1ba[0]) and m1ba[1] >= 20) else v
        if s in PIP:
            pip_bps = PIP[s] / PREZZO_TIPICO_FX[s] * 1e4
            base, stress = max(2 * vb, 0.2 * pip_bps), max(3 * vb, 0.3 * pip_bps)
        else:
            base, stress = vb, 1.5 * vb
        righe.append(dict(strumento=s, contesto=ctx, base_bps=base, stress_bps=stress, p75_ftmo_bps=v, p75_m1ba_bps=m1ba[0],
                          n_ftmo=n, n_m1ba=m1ba[1]))
T = pd.DataFrame(righe)
spec_us30, congelata_us100 = 2.63 / 51691.16 * 1e4, 1.53 / 30903.34 * 1e4
for ctx in T[T.strumento == "US100"].contesto:
    u100 = T[(T.strumento == "US100") & (T.contesto == ctx)].base_bps.iloc[0]
    u500 = T[(T.strumento == "US500") & (T.contesto == ctx)].base_bps
    base = float(np.nanmax([spec_us30 * u100 / congelata_us100, u100, u500.iloc[0] if len(u500) else np.nan]))
    righe.append(dict(strumento="US30", contesto=ctx, base_bps=base, stress_bps=1.5 * base, p75_ftmo_bps=np.nan,
                      p75_m1ba_bps=np.nan, n_ftmo=0, n_m1ba=0))
T = pd.DataFrame(righe)
os.makedirs(os.path.join(QUI, "risultati"), exist_ok=True)
T.to_csv(os.path.join(QUI, "risultati", "COSTI_TABELLA_CONGELATA.csv"), sep=";", decimal=",", index=False)
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 500)
print(T[T.contesto.str.startswith(("S1", "S2"))].round(3).to_string(index=False))
