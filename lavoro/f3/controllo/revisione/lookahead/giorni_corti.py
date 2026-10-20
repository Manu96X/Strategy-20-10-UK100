# Giornate di trading con pochi M1 (H1/D1 travestiti o buchi) dopo la data d'inizio del feed
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import pickle, numpy as np, pandas as pd
for (sim, fk) in [("UK100","PEP"),("UK100","FTMO"),("GER40","PEP"),("US500","PEP"),("US100","PEP")]:
    d = pickle.load(open(f"cache_{sim}_{fk}.pkl","rb")); feed, bs = d["feed"], d["bs"]
    n = pd.Series(feed.data_srv).value_counts().sort_index()
    passo = pd.Series(np.diff(feed.ts)/6e10, index=pd.to_datetime(feed.data_srv[1:])).groupby(level=0).agg(lambda s: s.mode().iat[0])
    print(sim, fk, "giorni:", len(n), " con <600 M1:", int((n < 600).sum()), " passo modale != 1 min:", int((passo != 1).sum()),
          " barre sessione con n_m1 < 30:", int((bs.n_m1 < 30).sum()), "di", len(bs))
    print("   giorni <600 M1:", [str(pd.Timestamp(x).date()) for x in n[n < 600].index][:20])
