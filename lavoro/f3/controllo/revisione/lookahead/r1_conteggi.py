import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import motore_f3 as M
d = pickle.load(open(f"cache_{sys.argv[1]}_{sys.argv[2]}.pkl","rb")); feed, tab, bs = d["feed"], d["tab"], d["bs"]
b = bs
mon = b[b.dow==0]
gl = mon.groupby("dl")
print("lunedi con barre:", gl.ngroups, " con k0 come prima barra:", (gl.k.first()==0).sum())
print("barre per lunedi (distribuzione):", gl.size().value_counts().sort_index().to_dict())
# condizione segnale grezza
c=b.c.values; rsi=b.rsi.values; val=b.valida.values
cnt_cond=0; cnt_cond_val=0
for dl,g in gl:
    if g.k.iat[0]!=0: continue
    ap=g.o.iat[0]
    cond=(c[g.index]<ap)&(rsi[g.index]<40)
    cnt_cond+=cond.any(); cnt_cond_val+=(cond&val[g.index]).any()
print("lunedi con condizione R1 vera almeno una volta:", cnt_cond, " su barre valide:", cnt_cond_val)
es = M.esiti_tutte_le_barre(feed, b, 2.5, "24h", tab, M.SCENARI["base"])
tr = M.segnali_R1(b, es, (0,), 40.0, True)
print("trade A1 base:", len(tr))
# perche' esiti None sulle barre con condizione vera
fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64)
i0s = np.searchsorted(feed.ts, fine, "left")
mot={}
for dl,g in gl:
    if g.k.iat[0]!=0: continue
    ap=g.o.iat[0]
    for s in g.index:
        if val[s] and c[s]<ap and rsi[s]<40:
            if es[s] is None:
                i0=i0s[s]
                if i0>=len(feed.ts): m="fine dati"
                elif feed.ts[i0]-fine[s]>15*M.MIN: m="primo M1 >15 min"
                else:
                    k=feed.info_giorno(i0)
                    m = "giorno non di trading" if k is None else ("regola 2 ore" if feed.chiusura_dopo[k] and feed.ts[i0]>=feed.ultima[k]-2*M.ORA else "altro")
                mot[m]=mot.get(m,0)+1
print("motivi esiti None su barre-segnale R1:", mot)
