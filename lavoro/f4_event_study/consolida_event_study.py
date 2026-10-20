# -*- coding: utf-8 -*-
"""Consolida l'event study: legge l'output strutturato del workflow (JSON), ricalcola IN MODO INDIPENDENTE
Benjamini-Hochberg (q = 0,10) e le classi del piano §0, confronta con il calcolo del workflow e con i CSV
delle famiglie, scrive risultati/RIEPILOGO_EVENT_STUDY.csv.
Uso: python3 -I consolida_event_study.py <output_workflow.json> <cartella_event_study>"""
import os, sys, json, glob
import numpy as np, pandas as pd

wf, base = sys.argv[1], sys.argv[2]
J = json.load(open(wf, encoding="utf-8"))
R = J["result"] if "result" in J else J
T = pd.DataFrame(R["test"])
print("test:", len(T), "per famiglia:", T.groupby("famiglia").size().to_dict())

# BH indipendente
p = T.p_primario.astype(float).to_numpy(); ok = np.isfinite(p); m = ok.sum()
ordine = np.argsort(np.where(ok, p, np.inf)); k = 0
for i, j in enumerate(ordine[:m], 1):
    if p[j] <= i / m * 0.10: k = i
bh = np.zeros(len(p), bool); bh[ordine[:k]] = True
T["bh_mio"] = bh
segno = np.sign(T.media_anomala.fillna(T.media_z).astype(float))
conc = T.conc_ftmo_media.isna() | (np.sign(T.conc_ftmo_media.astype(float)) == segno)
anni = T.quota_anni_stesso_segno.fillna(0).astype(float) >= 0.6
netto = T.netto_base_z.fillna(-1).astype(float) > 0
T["classe_mia"] = np.where(bh & conc & anni & netto, "PROMETTENTE", np.where((T.p_primario.astype(float) < 0.05) & conc & anni, "INDIZIO", "NULLO"))
print(f"BH: workflow {R['n_bh']} superati (soglia p {R['soglia_bh']:.5f}); ricalcolo indipendente {k} superati")
print("classi uguali al workflow:", int((T.classe == T.classe_mia).sum()), "/", len(T))

# confronto con i CSV delle famiglie (stesso numero di righe per famiglia)
for f in sorted(glob.glob(os.path.join(base, "risultati", "famiglia_*.csv"))):
    if "descrittivo" in f: continue
    try:
        c = pd.read_csv(f, sep=";", decimal=",")
        print(os.path.basename(f), "righe CSV:", len(c))
    except Exception as e:
        print(os.path.basename(f), "illeggibile:", e)

T.to_csv(os.path.join(base, "risultati", "RIEPILOGO_EVENT_STUDY.csv"), sep=";", decimal=",", index=False)
cols = ["famiglia", "test_id", "strumento", "n", "eventi_anno", "media_z", "media_anomala", "t", "p_primario", "bh_mio",
        "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z", "conc_ftmo_media", "classe_mia"]
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 300)
top = T.sort_values("p_primario").head(30)[cols]
print(top.round(4).to_string(index=False))
