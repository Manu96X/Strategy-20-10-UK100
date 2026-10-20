# R2 (A5) e A10: barre con condizione vera ma esito None, per motivo; e quante dipendono da un'ultima quotazione anomala
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd, motore_f3 as M
for fk in ["PEP","FTMO"]:
    d = pickle.load(open(f"cache_UK100_{fk}.pkl","rb")); feed, tab = d["feed"], d["tab"]
    g = pd.DataFrame({"g": pd.to_datetime(feed.giorni), "hm": (feed.ultima - feed.giorni.astype("datetime64[ns]").astype(np.int64))/3.6e12})
    g["anno"] = g.g.dt.year; g["dow"] = g.g.dt.weekday
    moda = g.groupby(["anno","dow"]).hm.transform(lambda s: s.round(2).mode().iat[0]); anom = (g.hm < moda - 0.5).values
    for nome, b in [("sess", d["bs"]), ("cfd", d["bc"])]:
        es = M.esiti_tutte_le_barre(feed, b, 2.0, "24h", tab, M.SCENARI["base"])
        fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64); i0s = np.searchsorted(feed.ts, fine, "left")
        cond = b.valida.values & (b.c.values <= b.sma.values - 3*b.atr.values) & (b.rsi.values < 35)
        mot = {}
        for s in np.flatnonzero(cond):
            if es[s] is not None: continue
            i0 = i0s[s]
            if i0 >= len(feed.ts): m = "fine dati"
            elif feed.ts[i0] - fine[s] > 15*M.MIN: m = "primo M1 >15 min"
            else:
                k = feed.info_giorno(i0)
                if k is None: m = "giorno non di trading"
                elif feed.chiusura_dopo[k] and feed.ts[i0] >= feed.ultima[k] - 2*M.ORA: m = "regola 2 ore" + (" (ultima ANOMALA)" if anom[k] else "")
                else: m = "altro"
            mot[m] = mot.get(m, 0) + 1
        print(fk, nome, "barre con condizione R2 k=3:", int(cond.sum()), " esito None per motivo:", mot)
