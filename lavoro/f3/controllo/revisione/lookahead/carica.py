# Revisione look-ahead: prepara UK100 (sola lettura del motore, dati sigillati) e salva in cache pickle locale
import sys, os, pickle
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import esegui_f3 as E, motore_f3 as M
DATI = "/home/user/dati_scoperta"
OUT = os.path.dirname(os.path.abspath(__file__))
sim, fk = sys.argv[1], sys.argv[2]
feed, tab, bs, bc = E.prepara(sim, fk, DATI)
pickle.dump(dict(feed=feed, tab=tab, bs=bs, bc=bc), open(os.path.join(OUT, f"cache_{sim}_{fk}.pkl"), "wb"))
print(sim, fk, len(feed.ts), len(bs), None if bc is None else len(bc))
