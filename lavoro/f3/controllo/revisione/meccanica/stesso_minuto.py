import sys, pandas as pd, numpy as np
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/revisione/meccanica")
import ricalcolo as RC
X = pd.read_pickle("confronto.pkl")
SIMB = lambda c: {"B1":"GER40","B2":"US500","B3":"US100"}.get(c, "UK100")
X["simb"] = X.cella.map(SIMB)
out = []
for (s, f), g in X.groupby(["simb", "feed"]):
    nome, ini = RC.FILE[(s, f)]; F = RC.carica(nome, ini)
    for idx, t in g.iterrows():
        j = int(t.j)
        out.append(dict(idx=idx, both=(F["l"][j] <= t.sl) and (F["h"][j] >= t.tp), tp_gap=(t.tipo == "TP") and (F["o"][j] > t.tp),
                        tp_gap_R=(F["o"][j] - t.tp) / t.d if t.tipo == "TP" and F["o"][j] > t.tp else 0.0))
Y = X.join(pd.DataFrame(out).set_index("idx"))
print("SL e TP nello stesso minuto (risolti come SL):", int(Y.both.sum()))
print(Y[Y.both][["cella", "feed", "scenario", "ts_in", "tipo", "R"]].assign(ts_in=lambda x: pd.to_datetime(x.ts_in)).to_string())
print("TP con apertura gia' oltre il TP (eseguiti al TP, prudente):", int(Y.tp_gap.sum()), " R lasciato max", Y.tp_gap_R.max())
