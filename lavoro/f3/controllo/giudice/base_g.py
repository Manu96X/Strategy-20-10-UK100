# Harness del giudice: usa motore_f3/esegui_f3 in SOLA LETTURA (import), tabella spread ricostruita dai trade.
import sys, os, pickle
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import motore_f3 as M, esegui_f3 as E
DATI = "/home/user/dati_scoperta"
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
_TAB = pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spread_tab.pkl"), "rb"))
_MAP = {"UK100 FTMO m1": "UK100", "GER40 FTMO m1": "GER40", "US500 m1 - FTMO": "US500", "US100 m1 - FTMO": "US100"}
M.tabella_spread = lambda f, anno=2026: _TAB[_MAP[f]].copy()
assert "dati_m1" not in DATI
def trade_file():
    return pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
def celle_di(sim):
    return [c for c, v in E.CELLE.items() if v[0] == sim and v[2] != "PORT"]
def esegui(feed, bs, bc, tab, celle, scen, fk, esiti_fn=None, segn_R1=None):
    """riproduce le celle come esegui_f3.main; esiti_fn permette varianti del motore"""
    esiti_fn = esiti_fn or M.esiti_tutte_le_barre
    out = {}; cache = {}
    for c in celle:
        _, tipo, reg, m, usc, k = E.CELLE[c]
        b = bs if tipo == "sess" else bc
        key = (tipo, m, usc)
        if key not in cache: cache[key] = esiti_fn(feed, b, m, usc, tab, M.SCENARI[scen])
        e = cache[key]
        lst = M.segnali_R1(b, e, (0,), 40.0, richiedi_k0=(tipo == "sess")) if reg == "R1" else M.segnali_R2(b, e, k)
        out[c] = E.trades_df(lst, b, c, fk, scen)
    return out, cache
