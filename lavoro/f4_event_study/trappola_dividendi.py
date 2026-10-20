# -*- coding: utf-8 -*-
"""Trappola dei dividendi: gap notturno (chiusura cash del giorno prima -> apertura cash) per giorno della settimana.
Il FTSE 100 è un indice di PREZZO: le società vanno ex-dividendo quasi sempre di GIOVEDÌ -> calo meccanico all'apertura
del giovedì, compensato dal broker con un accredito sulle posizioni long (se lo applica). Il DAX è total return: niente calo.
Uso: python3 -I trappola_dividendi.py <dati_sigillati>"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "f3"))
import motore_f3 as M, esegui_f3 as E
for sim in ["UK100", "GER40", "US500"]:
    feed, tab, bs, _ = E.prepara(sim, "PEP", sys.argv[1])
    g = bs.groupby("dl").agg(o=("o", "first"), c=("c", "last"), dow=("dow", "first"), k0=("k", "min")).reset_index()
    g = g[g.k0 == 0]
    g["gap"] = g.o - g.c.shift(); g["gap_pct"] = 100 * g.gap / g.c.shift()
    g = g[(g.dl - g.dl.shift()).dt.days.between(1, 3)]   # giorno precedente di borsa (anche venerdì->lunedì)
    t = g.groupby("dow").agg(n=("gap", "size"), gap_medio_punti=("gap", "mean"), gap_medio_pct=("gap_pct", "mean"))
    print(sim, "(Pepperstone, scoperta) gap notturno per giorno (0=lun):"); print(t.round(3).to_string())
    oth = g[g.dow != 3].gap_pct; thu = g[g.dow == 3].gap_pct
    print(f"  giovedì - altri giorni = {thu.mean() - oth.mean():+.3f}%  (t = {(thu.mean() - oth.mean()) / np.sqrt(thu.var() / len(thu) + oth.var() / len(oth)):.2f})\n")
