# Verifica che l'harness riproduca TRADE_scoperta.csv (tutti i simboli, feed, scenari)
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
T = trade_file()
sim = sys.argv[1]
for fk in ["PEP", "FTMO"]:
    feed, tab, bs, bc = E.prepara(sim, fk, DATI)
    pickle.dump(dict(feed=feed, tab=tab, bs=bs, bc=bc), open(f"/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice/cache_{sim}_{fk}.pkl", "wb"))
    for scen in ["lordo", "base", "stress"]:
        out, _ = esegui(feed, bs, bc, tab, celle_di(sim), scen, fk)
        for c, df in out.items():
            f = T[(T.cella == c) & (T.feed == fk) & (T.scenario == scen)]
            ok = len(f) == len(df) and (f.ts_in.values == df.ts_in.values).all() and (f.ts_out.values == df.ts_out.values).all()
            dR = np.abs(f.R.values - df.R.values).max() if len(f) == len(df) else np.nan
            print(f"{sim} {fk} {scen:6s} {c:4s} n_file={len(f)} n_rif={len(df)} ts_ok={ok} max|dR|={dR:.2e} media={df.R.mean():+.5f}")
