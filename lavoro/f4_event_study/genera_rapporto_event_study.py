# -*- coding: utf-8 -*-
"""Genera RAPPORTO_EVENT_STUDY.md da RIEPILOGO_EVENT_STUDY.csv, dall'output del workflow (verifiche) e dall'addendum.
Uso: python3 -I genera_rapporto_event_study.py <cartella_event_study>"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd
B = sys.argv[1]; RIS = os.path.join(B, "risultati")
T = pd.read_csv(os.path.join(RIS, "RIEPILOGO_EVENT_STUDY.csv"), sep=";", decimal=",")
W = json.load(open(os.path.join(RIS, "output_workflow_event_study.json"), encoding="utf-8"))["result"]
ADD = open(os.path.join(RIS, "ADDENDUM_dopo_i_numeri.txt"), encoding="utf-8").read()
def f(v, d=3, s=False):
    if v is None or (isinstance(v, float) and not np.isfinite(v)): return "—"
    if isinstance(v, (bool, np.bool_)): return "sì" if v else "no"
    if isinstance(v, (int, np.integer)): return str(v)
    return (f"{v:+.{d}f}" if s else f"{v:.{d}f}").replace(".", ",")
def md(df, fmt):
    out = ["| " + " | ".join(df.columns) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
    for _, r in df.iterrows(): out.append("| " + " | ".join(fmt.get(c, lambda x: str(x))(r[c]) for c in df.columns) + " |")
    return "\n".join(out)
NOMI = {"A": "Turn of the month e ribilanciamento", "B": "FOMC (prima e dopo)", "C": "Scadenze opzioni e festivi",
        "E": "Lunedì in calo → recupero", "F": "Correlazioni fra strumenti", "G": "Flussi orari materie prime", "I": "Momentum di serie storica"}
L = [f"# EVENT STUDY MULTI-STRUMENTO — RAPPORTO (dati di scoperta < 2024)",
     f"*Generato da `genera_rapporto_event_study.py` il {dt.date.today():%d/%m/%Y}. Piano pre-registrato: `PIANO_EVENT_STUDY.md` (commit precedente ai risultati). 242 test, 7 famiglie, 10 strumenti. Correzione di Benjamini-Hochberg (q = 0,10) calcolata dal workflow e ricalcolata in modo indipendente (`consolida_event_study.py`): stesso esito, classi identiche {int((T.classe == T.classe_mia).sum())}/{len(T)}.*\n",
     "## 1. Esito",
     f"- **Test che superano Benjamini-Hochberg: {int(T.bh_mio.sum())} su {len(T)}.** Nessun effetto PROMETTENTE.",
     f"- p < 0,05: **{int((T.p_primario < 0.05).sum())}** (attesi per caso {f(0.05*len(T),1)}); p < 0,01: **{int((T.p_primario < 0.01).sum())}** (attesi {f(0.01*len(T),1)}). Leggero eccesso, concentrato su un gruppo: **il dollaro (USDX) segue con un giorno di ritardo metalli e indici**.",
     f"- INDIZI (p < 0,05 senza correzione, anni e concordanza ok): **{int((T.classe_mia == 'INDIZIO').sum())}**.\n",
     "## 2. Per famiglia\n"]
fam = T.groupby("famiglia").agg(test=("test_id", "size"), p_min=("p_primario", "min"), p_sotto_005=("p_primario", lambda x: int((x < 0.05).sum())),
                                indizi=("classe_mia", lambda x: int((x == "INDIZIO").sum()))).reset_index()
fam.insert(1, "effetto", fam.famiglia.map(NOMI))
L.append(md(fam, {"p_min": lambda x: f(x, 4)}))
L.append("\n## 3. I 20 test con p più basso\n")
c = ["famiglia", "test_id", "n", "eventi_anno", "media_z", "t", "p_primario", "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z", "conc_ftmo_media", "classe_mia"]
top = T.sort_values("p_primario").head(20)[c]
L.append(md(top, {"eventi_anno": lambda x: f(x, 0), "media_z": lambda x: f(x, 3, True), "t": lambda x: f(x, 2, True), "p_primario": lambda x: f(x, 4),
                  "quota_anni_stesso_segno": lambda x: f(x, 2), "netto_base_z": lambda x: f(x, 3, True), "netto_stress_z": lambda x: f(x, 3, True), "conc_ftmo_media": lambda x: f(x, 3, True)}))
L.append("\n`media_z` = effetto medio per evento in multipli della volatilità giornaliera (per le regressioni: pendenza). `netto_*_z` = trade nel verso dell'effetto, dopo costi FTMO (spread, commissione, swap).\n")
L.append("## 4. Verifica avversaria (ricalcolo da zero dei 6 migliori)\n")
rows = []
for v in W["verifiche"]:
    for x in v["verifiche"]: rows.append(dict(test=x["test_id"], verdetto=x["verdetto"].upper(), motivo=x["motivazione"][:260].replace("|", "/") + "…"))
L.append(md(pd.DataFrame(rows), {}))
L.append("\n## 5. Addendum «dopo i numeri» (non cambia la classificazione)\n```\n" + ADD.strip() + "\n```")
L.append("- Con 200.000 permutazioni il p di XAU→USDX resta **sopra** la soglia di rango 1 (0,000413): l'esito «0 su 242» non dipende dalla risoluzione del placebo.")
L.append("- Drift pre-FOMC: positivo su US100 e GER40 (test di Welch p ≈ 0,02), debole su US500, nullo su UK100. Pre-festivi: paniere dei 4 indici p 0,04. Sono **indizi** coerenti con la letteratura, non prove.")
open(os.path.join(B, "RAPPORTO_EVENT_STUDY.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("scritto RAPPORTO_EVENT_STUDY.md")
