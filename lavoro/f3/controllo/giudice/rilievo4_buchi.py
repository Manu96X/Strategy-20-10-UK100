# Rilievo 4: buchi > soglia dentro la tenuta trattati come chiusure (variante) vs codice
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
import varianti as V
soglia = float(sys.argv[1]); sims = sys.argv[2:] or ["UK100", "GER40", "US500", "US100"]
T = trade_file()
for sim in sims:
    for fk in ["PEP", "FTMO"]:
        C = pickle.load(open(f"cache_{sim}_{fk}.pkl", "rb")); feed, tab, bs, bc = C["feed"], C["tab"], C["bs"], C["bc"]
        g = V.prepara_buchi(feed, soglia)
        for scen in ["base", "stress"]:
            out, _ = esegui(feed, bs, bc, tab, celle_di(sim), scen, fk, esiti_fn=V.fabbrica_esiti(buchi=True))
            for c, df in out.items():
                f = T[(T.cella == c) & (T.feed == fk) & (T.scenario == scen)]
                if len(f) == len(df) and (f.ts_out.values == df.ts_out.values).all() and np.allclose(f.R.values, df.R.values): continue
                print(f"{sim} {fk} {scen:6s} {c:4s} n {len(f)}->{len(df)}  media {f.R.mean():+.5f} -> {df.R.mean():+.5f}  diff {df.R.mean()-f.R.mean():+.5f}")
                if scen == "base":
                    a = f.set_index("ts_in"); b2 = df.set_index("ts_in")
                    for t in sorted(set(a.index) | set(b2.index)):
                        ra = a.R.get(t, np.nan); rb = b2.R.get(t, np.nan)
                        if not (np.isfinite(ra) and np.isfinite(rb) and abs(ra - rb) < 1e-9):
                            print(f"     {pd.Timestamp(int(t))}  R codice {ra:+.4f} ({a.tipo.get(t,'-')})  R variante {rb:+.4f} ({b2.tipo.get(t,'-')})")
