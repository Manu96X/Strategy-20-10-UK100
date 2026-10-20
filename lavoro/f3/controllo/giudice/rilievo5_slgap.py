# Rilievo 5: prezzo dello stop in gap = min(open, SL) - slip (protocollo) contro min(open, SL - slip) (codice)
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
import varianti as V
T = trade_file()
for sim in ["UK100", "GER40", "US500", "US100"]:
    for fk in ["PEP", "FTMO"]:
        C = pickle.load(open(f"cache_{sim}_{fk}.pkl", "rb")); feed, tab, bs, bc = C["feed"], C["tab"], C["bs"], C["bc"]
        for scen in ["base", "stress"]:
            out, _ = esegui(feed, bs, bc, tab, celle_di(sim), scen, fk, esiti_fn=V.fabbrica_esiti(sl_protocollo=True))
            for c, df in out.items():
                f = T[(T.cella == c) & (T.feed == fk) & (T.scenario == scen)]
                same = len(f) == len(df) and (f.ts_in.values == df.ts_in.values).all()
                if same:
                    dR = df.R.values - f.R.values; ngap = int((np.abs(dR) > 1e-9).sum())
                    print(f"{sim} {fk} {scen:6s} {c:4s} stessi trade; SL toccati da gap: {ngap:3d}; min dR {dR.min():+.4f}; media {f.R.mean():+.5f} -> {df.R.mean():+.5f} ({df.R.mean()-f.R.mean():+.5f})")
                else:
                    print(f"{sim} {fk} {scen:6s} {c:4s} TRADE DIVERSI n {len(f)}->{len(df)}; media {f.R.mean():+.5f} -> {df.R.mean():+.5f} ({df.R.mean()-f.R.mean():+.5f})")
