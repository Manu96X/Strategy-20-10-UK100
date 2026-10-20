# Apertura del lunedi': la prima barra k=0 parte dal minuto 08:00 locale? R1 su barre CFD (A9): apertura = primo prezzo della settimana?
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3"); sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/comune")
import pickle, numpy as np, pandas as pd, motore_f3 as M, barre
for fk in ["PEP", "FTMO"]:
    d = pickle.load(open(f"cache_UK100_{fk}.pkl","rb")); feed, bs, bc = d["feed"], d["bs"], d["bc"]
    m1 = feed.m1; loc = barre.ora_locale(m1.ts, "Europe/London")
    x = m1.assign(loc=loc); x = x[(x["loc"].dt.weekday == 0) & (x["loc"].dt.hour == 8)]
    prim = x.groupby(x["loc"].dt.normalize())["loc"].min()
    ritardo = (prim - prim.index - pd.Timedelta(hours=8)).dt.total_seconds() / 60
    print(fk, "lunedi': primo M1 della barra 08:00 in ritardo (>0 min):", int((ritardo > 0).sum()), "su", len(ritardo), ritardo[ritardo > 0].to_dict())
    # A9: apertura usata = open della prima barra CFD del lunedi' server; e' anche il primo prezzo dopo il weekend?
    mon = bc[bc.dow == 0].groupby("dl").first()
    prev = []
    for dl, r in mon.iterrows():
        i = np.searchsorted(feed.ts, pd.Timestamp(dl).value)  # primo M1 del lunedi' server
        gap_h = (feed.ts[i] - feed.ts[i-1]) / 3.6e12 if i > 0 else np.nan
        prev.append(gap_h)
    prev = np.array(prev)
    print(fk, "A9: lunedi' CFD:", len(mon), " ora server della prima barra (conteggi):", mon.k.value_counts().sort_index().to_dict(),
          " pausa prima del primo M1 del lunedi' < 24h (cioe' NON e' riapertura dopo weekend):", int((prev < 24).sum()))
