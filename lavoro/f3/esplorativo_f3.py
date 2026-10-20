# -*- coding: utf-8 -*-
"""
ADDENDUM «DOPO I NUMERI» (20/10/2026) — ESPLORATIVO, NON CAMBIA I VERDETTI DEL PROTOCOLLO.
(a) Versione «come nel video»: R2 con ingresso a OGNI barra che soddisfa la condizione (posizioni sovrapposte),
    per capire se i ~218 trade/anno dichiarati vengono da qui e se così l'edge compare.
(b) Regola 1 al variare dell'orizzonte d'uscita (N barre cash): A2 (24 barre) è un altopiano o un picco?
Solo dati di scoperta sigillati (< 2024), feed Pepperstone (inferenza) e FTMO (concordanza), costi base.
Uso: python3 -I esplorativo_f3.py <dati_scoperta> <cartella_risultati>
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore_f3 as M, esegui_f3 as E

def esiti_N(feed, b, m, N, tab, sc):
    """come M.esiti_tutte_le_barre ma con uscita dopo N barre di sessione."""
    fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64)
    i0s = np.searchsorted(feed.ts, fine, "left"); out = [None] * len(b)
    for s in range(len(b)):
        if not b.valida.iat[s] or s + N >= len(b): continue
        i0 = i0s[s]
        if i0 >= len(feed.ts) or feed.ts[i0] - fine[s] > 15 * M.MIN: continue
        r = M.simula(feed, i0, int(fine[s + N]), m * b.atr.iat[s], tab, sc)
        if r is not None: r["s"] = s; out[s] = r
    return out

def riga(nome, fk, lst, b):
    if not lst: return dict(prova=nome, feed=fk, n=0)
    df = E.trades_df(lst, b, nome, fk, "base"); s = M.statistiche(df, nboot=10)
    anni = (b.dl[b.valida].max() - b.dl[b.valida].min()).days / 365.25
    return dict(prova=nome, feed=fk, n=s["n"], trade_anno=s["n"] / anni, media=s["media"], t=s["t"], win=s["win"],
                quota_SL=s["mix"].get("SL", 0), quota_TP=s["mix"].get("TP", 0))

def main(dati, ris):
    righe = []
    for fk in ["PEP", "FTMO"]:
        feed, tab, bs, _ = E.prepara("UK100", fk, dati)
        sc = M.SCENARI["base"]
        e24 = M.esiti_tutte_le_barre(feed, bs, 2.0, "24h", tab, sc)
        for k in [0.0, 3.0]:
            m = (bs.valida & (bs.c <= bs.sma - k * bs.atr) & (bs.rsi < 35)).to_numpy()
            lst = [e24[s] for s in range(len(bs)) if m[s] and e24[s] is not None]
            righe.append(riga(f"(a) R2 ogni barra k={k:g}", fk, lst, bs))
        for N in [6, 12, 18, 24, 30, 36]:
            eN = esiti_N(feed, bs, 2.5, N, tab, sc)
            righe.append(riga(f"(b) R1 uscita {N} barre", fk, M.segnali_R1(bs, eN, (0,), 40.0, True), bs))
        print(fk, "ok", flush=True)
    R = pd.DataFrame(righe)
    R.to_csv(os.path.join(ris, "ESPLORATIVO_dopo_i_numeri.csv"), sep=";", decimal=",", index=False)
    pd.set_option("display.width", 200); print(R.round(3).to_string(index=False))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
