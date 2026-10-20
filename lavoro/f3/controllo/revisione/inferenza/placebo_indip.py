# Placebo P1 rifatto con codice di campionamento proprio e seme proprio.
# Usa le funzioni di SIMULAZIONE del motore (sola lettura, non e' la mia lente) per ottenere l'esito di ogni barra;
# la tabella spread e' ricostruita dai trade (colonna spread, scenario base) per NON leggere file derivati dal 2026.
import os, sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import motore_f3 as M
DATI = "/home/user/dati_scoperta"
RIS = "/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/"
OUT = os.path.dirname(os.path.abspath(__file__))
T = pd.read_csv(RIS + "TRADE_scoperta.csv", sep=";", decimal=",")
B = T[T.scenario == "base"].copy()
CELLE = {"A1": ("UK100", "sess", "R1", 2.5, "24h"), "A2": ("UK100", "sess", "R1", 2.5, "24barre"),
         "A3": ("UK100", "sess", "R1", 2.5, "sera"), "A4": ("UK100", "sess", "R2", 2.0, "24h"),
         "A5": ("UK100", "sess", "R2", 2.0, "24h"), "A6": ("UK100", "sess", "R2", 2.0, "24h"),
         "A7": ("UK100", "sess", "R2", 2.0, "24barre"), "A9": ("UK100", "cfd", "R1", 2.5, "24h"),
         "A10": ("UK100", "cfd", "R2", 2.0, "24h"), "B1": ("GER40", "sess", "R1", 2.5, "24h"),
         "B2": ("US500", "sess", "R1", 2.5, "24h"), "B3": ("US100", "sess", "R1", 2.5, "24h")}
SYM_CELLE = {"UK100": [c for c in CELLE if c[0] == "A"], "GER40": ["B1"], "US500": ["B2"], "US100": ["B3"]}
def tab_da_trade(celle):
    x = B[B.cella.isin(celle)]; h = pd.to_datetime(x.ts_in).dt.hour
    v = np.full(24, np.nan)
    for hh, sp in x.groupby(h).spread.first().items(): v[hh] = sp
    miss = [h for h in range(24) if not np.isfinite(v[h])]
    for h in range(24):
        if not np.isfinite(v[h]):
            vic = [v[(h - 1) % 24], v[(h + 1) % 24]]
            v[h] = np.nanmax(vic) if np.isfinite(vic).any() else np.nanmax(v)
    return v, miss
NREP = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
SEME = int(sys.argv[2]) if len(sys.argv) > 2 else 4242
rng = np.random.default_rng(SEME)
ris = {}; esiti_R = {}
for sym, celle in SYM_CELLE.items():
    cfg = M.SIMBOLI[sym]; tab, miss = tab_da_trade(celle); print(sym, "ore spread mancanti (riempite):", miss, flush=True)
    for fk in ["PEP", "FTMO"]:
        nome, inizio = cfg["feed"][fk]
        fl = M.festivi_borsa(cfg["cal"], range(2016, 2027)); fs = fl if cfg["cal"] == "ENG" else set()
        feed = M.Feed(os.path.join(DATI, nome + ".csv"), inizio, fs)
        bs = M.indicatori(M.barre_sessione(feed, cfg["tz"], cfg["apre"], cfg["chiude"], fl))
        bc = M.indicatori(M.barre_cfd(feed, fs)) if sym == "UK100" else None
        cache = {}
        for c in celle:
            _, tipo, reg, m, usc = CELLE[c]; b = bs if tipo == "sess" else bc
            key = (tipo, m, usc)
            if key not in cache:
                e = M.esiti_tutte_le_barre(feed, b, m, usc, tab, M.SCENARI["base"])
                cache[key] = np.array([np.nan if x is None else x["R"] for x in e])
            Rb = cache[key]
            tr = B[(B.cella == c) & (B.feed == fk)]
            # controllo: R del trade == R della barra s nel ricalcolo (verifica tabella spread ricostruita)
            dR = np.nanmax(np.abs(Rb[tr.s.to_numpy()] - tr.R.to_numpy()))
            anno, kk, dow = b.anno.to_numpy(), b.k.to_numpy(), b.dow.to_numpy()
            draws = np.empty((NREP, len(tr)))
            for j, (a, k) in enumerate(zip(tr.anno.to_numpy(), tr.k.to_numpy())):
                msk = (anno == a) & (kk == k) & np.isfinite(Rb)
                if reg == "R1": msk &= (dow == 0)
                pool = Rb[msk]
                draws[:, j] = pool[rng.integers(0, len(pool), NREP)]
            ris[(c, fk)] = draws
            mu = tr.R.mean(); mp = draws.mean(1)
            print(f"{c} {fk}: n={len(tr)} maxdiff_R_ricalcolo={dR:.2e} media={mu:+.4f} placebo={mp.mean():+.4f} p={(1+(mp>=mu).sum())/(1+NREP):.4f}", flush=True)
        del cache
for fk in ["PEP", "FTMO"]:
    ris[("A8", fk)] = np.hstack([ris[("A1", fk)], ris[("A5", fk)]])
    mu = B[(B.cella.isin(["A1", "A5"])) & (B.feed == fk)].R.mean(); mp = ris[("A8", fk)].mean(1)
    print(f"A8 {fk}: media={mu:+.4f} placebo={mp.mean():+.4f} p={(1+(mp>=mu).sum())/(1+NREP):.4f}")
pickle.dump(ris, open(os.path.join(OUT, f"placebo_indip_{NREP}_{SEME}.pkl"), "wb"))
