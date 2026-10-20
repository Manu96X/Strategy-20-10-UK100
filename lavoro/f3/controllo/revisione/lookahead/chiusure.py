# Trade la cui uscita (CHIUSURA, o "sera" limitata da ultima-15) dipende da un'ultima quotazione ANOMALA del giorno
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd, motore_f3 as M
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
T = T[(T.scenario == "base") & (T.cella != "A8")]
sim_of = lambda c: "UK100" if c.startswith("A") else {"B1": "GER40", "B2": "US500", "B3": "US100"}[c]
tot = []
for (sim, fk) in [("UK100","PEP"),("UK100","FTMO"),("GER40","PEP"),("US500","PEP"),("US100","PEP")]:
    feed = pickle.load(open(f"cache_{sim}_{fk}.pkl","rb"))["feed"]
    g = pd.DataFrame({"g": pd.to_datetime(feed.giorni), "ult": pd.to_datetime(feed.ultima), "cd": feed.chiusura_dopo})
    g["hm"] = (g.ult - g.g).dt.total_seconds()/3600; g["anno"] = g.g.dt.year; g["dow"] = g.g.dt.weekday
    moda = g.groupby(["anno","dow"]).hm.agg(lambda s: s.round(2).mode().iat[0]); g["moda"] = [moda[(a,w)] for a,w in zip(g.anno,g.dow)]
    g["anom"] = g.hm < g.moda - 0.5
    gi = g.set_index("g")
    t = T[(T.feed == fk) & (T.cella.map(sim_of) == sim)].copy()
    t["tout"] = pd.to_datetime(t.ts_out); t["gout"] = t.tout.dt.normalize()
    t = t.join(gi[["ult","anom","moda","cd"]], on="gout")
    forz = t[(t.tipo == "CHIUSURA") | ((t.cella == "A3") & (t.tipo == "TEMPO") & (t.tout.dt.hour*60 + t.tout.dt.minute < 23*60+40))]
    an = forz[forz.anom == True]
    print(f"{sim} {fk}: trade base={len(t)}  uscite forzate da 'ultima quotazione'={len(forz)}  di cui in giorni con ultima anomala={len(an)}")
    if len(an): print(an[["cella","ts_in","ts_out","tipo","R","ult","moda"]].to_string(index=False))
    tot.append(an)
