# usa il motore in SOLA LETTURA (python3 -I -B: nessun .pyc scritto)
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import esegui_f3 as E, motore_f3 as M
for simb, fk in [("UK100", "PEP"), ("UK100", "FTMO")]:
    feed, tab, bs, bc = E.prepara(simb, fk, "/home/user/dati_scoperta")
    for nome, b, m, k0 in [("A1", bs, 2.5, True), ("A9", bc, 2.5, False)]:
        e = M.esiti_tutte_le_barre(feed, b, m, "24h", tab, M.SCENARI["base"])
        salt = []; tot = 0
        for (dl, dow), g in b.groupby(["dl", "dow"], sort=True):
            if dow != 0 or (k0 and g.k.iat[0] != 0): continue
            ap = g.o.iat[0]
            sig = [s for s in g.index if b.valida[s] and b.c[s] < ap and b.rsi[s] < 40]
            if not sig: continue
            tot += 1
            if e[sig[0]] is None:
                alt = next((s for s in sig if e[s] is not None), None)
                salt.append((str(dl.date()), int(b.k[sig[0]]), None if alt is None else int(b.k[alt]),
                             str(pd.Timestamp(b.fine_srv[sig[0]]))))
        print(simb, fk, nome, "lunedi' con segnale:", tot, " primo segnale non simulabile:", len(salt))
        for x in salt[:15]: print("   ", x)
