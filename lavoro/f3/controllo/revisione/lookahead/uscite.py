# Uscite: nessun M1 fra ingresso e uscita tocca SL/TP; uscita <= scadenza; prezzi SL non migliori del livello
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
for fk in ["PEP", "FTMO"]:
    feed = pickle.load(open(f"cache_UK100_{fk}.pkl","rb"))["feed"]
    t = T[(T.feed == fk) & T.cella.str.startswith("A") & (T.cella != "A8")]
    tin = pd.to_datetime(t.ts_in).values.astype(np.int64); tout = pd.to_datetime(t.ts_out).values.astype(np.int64)
    i0 = np.searchsorted(feed.ts, tin); j = np.searchsorted(feed.ts, tout)
    bad_pre = 0; bad_tipo = 0; bad_px = 0
    for a, b_, sl, tp, tipo, px, o in zip(i0, j, t.sl.values, t.tp.values, t.tipo.values, t.px_out.values, feed.o[j]):
        if ((feed.l[a:b_] <= sl) | (feed.h[a:b_] >= tp)).any(): bad_pre += 1
        if tipo == "SL" and not (feed.l[b_] <= sl and px <= sl + 1e-9): bad_tipo += 1
        if tipo == "TP" and not (feed.h[b_] >= tp and abs(px - tp) < 1e-9): bad_tipo += 1
        if tipo in ("TEMPO", "CHIUSURA") and px > o + 1e-9: bad_px += 1
    print(fk, "trade A:", len(t), "| SL/TP toccati prima dell'uscita registrata:", bad_pre, "| tipo/prezzo SL-TP incoerenti:", bad_tipo,
          "| uscite a mercato sopra l'open dell'M1:", bad_px, "| ts_out < ts_in:", int((tout < tin).sum()))
