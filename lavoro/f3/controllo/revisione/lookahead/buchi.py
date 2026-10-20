# Giorni feriali non festivi SENZA dati (il motore li tratta come "chiusura nota" -> uscita forzata il giorno prima)
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd, motore_f3 as M
sim, fk = sys.argv[1], sys.argv[2]
d = pickle.load(open(f"cache_{sim}_{fk}.pkl","rb")); feed = d["feed"]
cfg = M.SIMBOLI[sim]; fest = M.festivi_borsa(cfg["cal"], range(2016, 2027))
fest_srv = fest if cfg["cal"] == "ENG" else set()
giorni = pd.to_datetime(feed.giorni)
tutti = pd.bdate_range(giorni.min(), giorni.max())
mancanti = [x.date() for x in tutti if x not in set(giorni) and x.date() not in fest_srv]
print(sim, fk, "feriali non festivi (calendario del motore) senza dati:", len(mancanti))
print("  di cui festivi della borsa cash locale:", [m for m in mancanti if m in fest])
print("  NON festivi in alcun calendario:", [m for m in mancanti if m not in fest])
# ultime quotazioni anomale: giorni con chiusura dopo e ultima quotazione molto prima della moda
ult = pd.to_datetime(feed.ultima); g = pd.DataFrame({"g": giorni, "ult": ult, "cd": feed.chiusura_dopo})
g["hm"] = (g.ult - g.g).dt.total_seconds() / 3600; g["anno"] = g.g.dt.year; g["dow"] = g.g.dt.weekday
moda = g.groupby(["anno", "dow"]).hm.agg(lambda s: s.round(2).mode().iat[0])
g["moda"] = [moda[(a, w)] for a, w in zip(g.anno, g.dow)]
an = g[g.cd & (g.hm < g.moda - 0.5)]
print("  giorni prima di chiusura con ultima quotazione >30 min prima della moda:", len(an))
print(an[["g","ult","moda","dow"]].assign(g=an.g.dt.date).to_string(index=False))
