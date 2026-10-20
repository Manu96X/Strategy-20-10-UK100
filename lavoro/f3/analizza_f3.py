# -*- coding: utf-8 -*-
"""
F3 — statistiche, placebo, Benjamini-Hochberg e verdetti del protocollo (§6-§7) dai trade di esegui_f3.py.
Uso: python3 -I analizza_f3.py <cartella_risultati> <fase>
Scrive: SINTESI_<fase>.csv (una riga per cella × feed × scenario), VERDETTI_<fase>.csv, PER_ANNO_<fase>.csv, P2_<fase>.csv
"""
import os, sys, pickle
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore_f3 as M
from esegui_f3 import CELLE, bh

def carica(ris, fase):
    T = pd.read_csv(os.path.join(ris, f"TRADE_{fase}.csv"), sep=";", decimal=",")
    st = pickle.load(open(os.path.join(ris, f"stato_{fase}.pkl"), "rb"))
    return T, st

def main(ris, fase):
    T, st = carica(ris, fase)
    righe, per_anno = [], []
    for (c, fk, scen), g in T.groupby(["cella", "feed", "scenario"], sort=False):
        s = M.statistiche(g)
        r = {k: v for k, v in s.items() if k not in ("per_anno", "mix", "R_per_tipo", "ic95")}
        r.update(cella=c, feed=fk, scenario=scen, ic95_basso=s["ic95"][0], ic95_alto=s["ic95"][1],
                 **{f"quota_{k}": v for k, v in s["mix"].items()}, **{f"R_{k}": v for k, v in s["R_per_tipo"].items()})
        if scen == "base" and (c, fk) in st["P1"]:
            D = st["P1"][(c, fk)]
            mp = np.nanmean(D, axis=1)
            r["placebo_media"] = float(np.mean(mp)); r["placebo_p"] = float((1 + (mp >= s["media"]).sum()) / (1 + len(mp)))
            r["diff_placebo"] = s["media"] - r["placebo_media"]
        righe.append(r)
        pa = s["per_anno"].reset_index(); pa["cella"], pa["feed"], pa["scenario"] = c, fk, scen; per_anno.append(pa)
    S = pd.DataFrame(righe)
    ordine = list(CELLE)
    S["o"] = S.cella.map({c: i for i, c in enumerate(ordine)}); S = S.sort_values(["o", "feed", "scenario"]).drop(columns="o")
    S.to_csv(os.path.join(ris, f"SINTESI_{fase}.csv"), sep=";", decimal=",", index=False)
    pd.concat(per_anno).to_csv(os.path.join(ris, f"PER_ANNO_{fase}.csv"), sep=";", decimal=",", index=False)

    # P2: lunedì contro martedì-venerdì (feed d'inferenza e concordanza), scenario base
    p2 = []
    for (c, fk), d2 in st["P2"].items():
        d1 = T[(T.cella == c) & (T.feed == fk) & (T.scenario == "base")]
        s1, s2 = M.statistiche(d1, nboot=10), M.statistiche(d2, nboot=10)
        se1, se2 = s1["media"] / s1["t"], s2["media"] / s2["t"]
        diff = s1["media"] - s2["media"]
        p2.append(dict(cella=c, feed=fk, n_lun=s1["n"], media_lun=s1["media"], n_altri=s2["n"], media_altri=s2["media"],
                       diff=diff, t_diff=diff / np.sqrt(se1 ** 2 + se2 ** 2),
                       **{f"media_dow{d}": d2[d2.dow == d].R.mean() for d in (1, 2, 3, 4)}))
    P2 = pd.DataFrame(p2); P2.to_csv(os.path.join(ris, f"P2_{fase}.csv"), sep=";", decimal=",", index=False)

    if fase != "scoperta": return S, None, P2
    # Verdetti (protocollo §7), feed d'inferenza = PEP, concordanza = FTMO
    base = S[(S.feed == "PEP") & (S.scenario == "base")].set_index("cella")
    stress = S[(S.feed == "PEP") & (S.scenario == "stress")].set_index("cella")
    conc = S[(S.feed == "FTMO") & (S.scenario == "base")].set_index("cella")
    pv = base.placebo_p.to_dict(); rej = bh(pv, 0.10)
    V = []
    for c in CELLE:
        b = base.loc[c]; tsoglia = 2.5 if c == "A3" else 2.0
        cond = dict(media_pos=b.media > 0, t_ok=b.t >= tsoglia, placebo_bh=bool(rej[c]), stress_pos=stress.loc[c].media > 0,
                    n_ok=b.n >= b.n_req, concordanza=conc.loc[c].media > 0 if c in conc.index else False,
                    anni_ok=b.anni_pos >= 0.6, costo_ok=b.costo_R <= 0.125)
        verde = all(cond.values())
        # L1 (lettura della prima esecuzione): una sola deroga alla volta
        altri = {k: v for k, v in cond.items() if k not in ("t_ok", "n_ok")}
        giallo_a = all(altri.values()) and (1.0 <= b.t < tsoglia)
        altri_b = {k: v for k, v in cond.items() if k != "placebo_bh"}
        giallo_b = all(altri_b.values()) and (b.placebo_p < 0.10)
        verd = "VERDE" if verde else ("GIALLO" if (giallo_a or giallo_b) else "ROSSO")
        # L2 (lettura cumulativa, addendum 20/10/2026 «dopo i numeri»): le due deroghe possono valere insieme
        resto = {k: v for k, v in cond.items() if k not in ("t_ok", "n_ok", "placebo_bh")}
        giallo_l2 = all(resto.values()) and (b.t >= 1.0) and (bool(rej[c]) or b.placebo_p < 0.10)
        verd2 = "VERDE" if verde else ("GIALLO" if giallo_l2 else "ROSSO")
        V.append(dict(cella=c, verdetto=verd, verdetto_L2=verd2, n=int(b.n), media=b.media, t=b.t, placebo_p=b.placebo_p,
                      media_stress=stress.loc[c].media, media_FTMO=conc.loc[c].media if c in conc.index else np.nan,
                      n_FTMO=int(conc.loc[c].n) if c in conc.index else 0, **cond))
    V = pd.DataFrame(V); V.to_csv(os.path.join(ris, f"VERDETTI_{fase}.csv"), sep=";", decimal=",", index=False)
    return S, V, P2

if __name__ == "__main__":
    S, V, P2 = main(sys.argv[1], sys.argv[2])
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    cols = ["cella", "feed", "scenario", "n", "media", "t", "win", "costo_R", "placebo_media", "placebo_p", "anni_pos", "quota_SL", "quota_TP", "quota_TEMPO", "quota_CHIUSURA"]
    print(S[[c for c in cols if c in S.columns]].round(3).to_string(index=False))
    if V is not None: print(V.round(3).to_string(index=False))
    print(P2.round(3).to_string(index=False))
