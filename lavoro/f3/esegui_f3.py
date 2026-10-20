# -*- coding: utf-8 -*-
"""
F3 — esegue le 13 celle del protocollo su una fase (scoperta o validazione), sui due feed,
negli scenari lordo / base / stress, con placebo P1 (1.000 repliche), placebo P2 (lunedì contro
martedì-venerdì), Benjamini-Hochberg (q = 0,10) e verdetti del protocollo §7.
Uso: python3 -I esegui_f3.py <cartella_dati_sigillati> <cartella_output> <fase: scoperta|validazione>
"""
import os, sys, json, pickle
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore_f3 as M

ANNI = range(2016, 2027)
NREP = 1000

CELLE = {  # cella: (simbolo, tipo barre, regola, m (stop in ATR), uscita, k_atr R2)
    "A1": ("UK100", "sess", "R1", 2.5, "24h", None),
    "A2": ("UK100", "sess", "R1", 2.5, "24barre", None),
    "A3": ("UK100", "sess", "R1", 2.5, "sera", None),
    "A4": ("UK100", "sess", "R2", 2.0, "24h", 2.0),
    "A5": ("UK100", "sess", "R2", 2.0, "24h", 3.0),
    "A6": ("UK100", "sess", "R2", 2.0, "24h", 4.0),
    "A7": ("UK100", "sess", "R2", 2.0, "24barre", 3.0),
    "A8": ("UK100", "sess", "PORT", None, None, None),     # A1 + A5
    "A9": ("UK100", "cfd", "R1", 2.5, "24h", None),
    "A10": ("UK100", "cfd", "R2", 2.0, "24h", 3.0),
    "B1": ("GER40", "sess", "R1", 2.5, "24h", None),
    "B2": ("US500", "sess", "R1", 2.5, "24h", None),
    "B3": ("US100", "sess", "R1", 2.5, "24h", None),
}

def prepara(simbolo, feed_key, dati):
    cfg = M.SIMBOLI[simbolo]
    nome, inizio = cfg["feed"][feed_key]
    fest_loc = M.festivi_borsa(cfg["cal"], ANNI)
    fest_srv = fest_loc if cfg["cal"] == "ENG" else set()     # FTMO chiude UK100 nei bank holiday (F0)
    feed = M.Feed(os.path.join(dati, nome + ".csv"), inizio, fest_srv)
    tab = M.tabella_spread(cfg["spread_da"])
    bs = M.indicatori(M.barre_sessione(feed, cfg["tz"], cfg["apre"], cfg["chiude"], fest_loc))
    bc = M.indicatori(M.barre_cfd(feed, fest_srv)) if simbolo == "UK100" else None
    return feed, tab, bs, bc

def trades_df(lista, b, cella, feed_key, scen):
    if not lista: return pd.DataFrame()
    df = pd.DataFrame(lista)
    df["cella"], df["feed"], df["scenario"] = cella, feed_key, scen
    df["data_loc"] = b.data.values[df.s]; df["k"] = b.k.values[df.s]; df["dow"] = b.dow.values[df.s]
    df["anno"] = b.anno.values[df.s]
    df["rsi"] = b.rsi.values[df.s]; df["atr"] = b.atr.values[df.s]
    df["dist_sma_atr"] = (b.c.values[df.s] - b.sma.values[df.s]) / b.atr.values[df.s]
    df["ts_in"] = df.ts_in.astype(np.int64); df["ts_out"] = df.ts_out.astype(np.int64)
    return df

def placebo(df_cell, b, esiti_base, regola, rng):
    """P1: per ogni trade, barra a caso dello stesso anno, stessa posizione k (ora), lunedì (R1) o qualunque giorno (R2)."""
    R = np.array([e["R"] if e is not None else np.nan for e in esiti_base])
    ok = ~np.isnan(R)
    chiave = pd.DataFrame({"anno": b.anno.values, "k": b.k.values, "lun": b.dow.values == 0})
    pool = {}
    draws = np.empty((NREP, len(df_cell)))
    for j, (_, t) in enumerate(df_cell.iterrows()):
        key = (t.anno, t.k, True) if regola == "R1" else (t.anno, t.k, None)
        if key not in pool:
            m = ok & (chiave.anno.values == t.anno) & (chiave.k.values == t.k)
            if regola == "R1": m &= chiave.lun.values
            pool[key] = R[m]
        p = pool[key]
        draws[:, j] = rng.choice(p, NREP, replace=True) if len(p) else np.nan
    return draws

def bh(pvals, q=0.10):
    ks = sorted(pvals, key=pvals.get); m = len(ks); soglia = 0
    for i, k in enumerate(ks, 1):
        if pvals[k] <= i / m * q: soglia = i
    return {k: (ks.index(k) < soglia) for k in ks}

def main(dati, out, fase):
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261020)
    tutti, P1, P2, info = [], {}, {}, {}
    for simbolo in ["UK100", "GER40", "US500", "US100"]:
        celle_s = [c for c, v in CELLE.items() if v[0] == simbolo]
        for fk in ["PEP", "FTMO"]:
            feed, tab, bs, bc = prepara(simbolo, fk, dati)
            info[f"{simbolo}_{fk}"] = dict(m1=len(feed.ts), barre_sess=len(bs), barre_cfd=len(bc) if bc is not None else 0,
                                           primo_valido=str(bs.dl[bs.valida].min().date()), ultimo=str(bs.dl.max().date()))
            print(simbolo, fk, info[f"{simbolo}_{fk}"], flush=True)
            cache = {}
            def esiti(tipo, m, usc, scen, sl_prima=True):
                key = (tipo, m, usc, scen, sl_prima)
                if key not in cache:
                    b = bs if tipo == "sess" else bc
                    cache[key] = M.esiti_tutte_le_barre(feed, b, m, usc, tab, M.SCENARI[scen], sl_prima)
                return cache[key]
            for scen in ["lordo", "base", "stress"]:
                per_cella = {}
                for c in celle_s:
                    _, tipo, reg, m, usc, k = CELLE[c]
                    if reg == "PORT": continue
                    b = bs if tipo == "sess" else bc
                    e = esiti(tipo, m, usc, scen)
                    lst = M.segnali_R1(b, e, (0,), 40.0, richiedi_k0=(tipo == "sess")) if reg == "R1" else M.segnali_R2(b, e, k)
                    per_cella[c] = trades_df(lst, b, c, fk, scen)
                if "A1" in per_cella:
                    per_cella["A8"] = pd.concat([per_cella["A1"], per_cella["A5"]]).assign(cella="A8")
                for c, df in per_cella.items(): tutti.append(df)
                if scen == "base":
                    for c in celle_s:
                        _, tipo, reg, m, usc, k = CELLE[c]
                        if reg == "PORT":
                            d1 = P1.get(("A1", fk)); d5 = P1.get(("A5", fk))
                            P1[("A8", fk)] = np.hstack([d1, d5]); continue
                        b = bs if tipo == "sess" else bc
                        P1[(c, fk)] = placebo(per_cella[c], b, esiti(tipo, m, usc, "base"), reg, rng)
                    # P2: stessa R1 negli altri giorni (martedì-venerdì), solo barre di sessione
                    for c in celle_s:
                        _, tipo, reg, m, usc, k = CELLE[c]
                        if reg == "R1" and tipo == "sess" and usc == "24h":
                            lst = M.segnali_R1(bs, esiti(tipo, m, usc, "base"), (1, 2, 3, 4), 40.0, True)
                            P2[(c, fk)] = trades_df(lst, bs, c + "_P2", fk, "base")
            del cache
    T = pd.concat(tutti, ignore_index=True)
    T.to_csv(os.path.join(out, f"TRADE_{fase}.csv"), sep=";", decimal=",", index=False)
    with open(os.path.join(out, f"stato_{fase}.pkl"), "wb") as f:
        pickle.dump(dict(P1=P1, P2=P2, info=info), f)
    print("trade totali:", len(T))

if __name__ == "__main__":
    main(*sys.argv[1:4])
