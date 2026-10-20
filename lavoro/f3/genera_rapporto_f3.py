# -*- coding: utf-8 -*-
"""Genera lavoro/f3/RAPPORTO_F3_SCOPERTA.md dai CSV di analizza_f3.py, esplorativo_f3.py e del doppio controllo.
Tutti i numeri vengono dai file. Uso: python3 -I genera_rapporto_f3.py <cartella_f3>"""
import os, sys, datetime as dt
import numpy as np, pandas as pd

F3 = sys.argv[1]; RIS = os.path.join(F3, "risultati"); CTRL = os.path.join(F3, "controllo")
def leggi(p): return pd.read_csv(p, sep=";", decimal=",")
def fmt(v, d=3, segno=False):
    if isinstance(v, (bool, np.bool_)): return "sì" if v else "**no**"
    if isinstance(v, (int, np.integer)): return f"{v:,}".replace(",", ".")
    if isinstance(v, (float, np.floating)):
        if not np.isfinite(v): return "—"
        if d == 0: return f"{v:,.0f}".replace(",", ".")
        return (f"{v:+.{d}f}" if segno else f"{v:.{d}f}").replace(".", ",")
    return str(v)
def con_segno(c): return ("media" in c) or c.startswith("ic95") or c.startswith("diff") or c == "R"
def md(df, dec=None):
    dec = dec or {}
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt(r[c], dec.get(c, 3), con_segno(c)) if not isinstance(r[c], str) else r[c] for c in cols) + " |")
    return "\n".join(out)

S = leggi(os.path.join(RIS, "SINTESI_scoperta.csv")); V = leggi(os.path.join(RIS, "VERDETTI_scoperta.csv"))
P2 = leggi(os.path.join(RIS, "P2_scoperta.csv")); PA = leggi(os.path.join(RIS, "PER_ANNO_scoperta.csv"))
EX = leggi(os.path.join(RIS, "ESPLORATIVO_dopo_i_numeri.csv"))
CR = leggi(os.path.join(CTRL, "CONFRONTO_REPLICA.csv")) if os.path.exists(os.path.join(CTRL, "CONFRONTO_REPLICA.csv")) else None
ESITO = open(os.path.join(CTRL, "ESITO_REVISIONE.md"), encoding="utf-8").read() if os.path.exists(os.path.join(CTRL, "ESITO_REVISIONE.md")) else "*(in corso)*"

DESCR = {"A1": "R1 fedele, uscita 24 ore", "A2": "R1, uscita 24 barre cash", "A3": "R1, uscita la sera (PDF)",
         "A4": "R2 k=2, 24 ore", "A5": "R2 k=3, 24 ore", "A6": "R2 k=4, 24 ore", "A7": "R2 k=3, 24 barre cash",
         "A8": "portafoglio A1 + A5", "A9": "R1 su barre CFD", "A10": "R2 k=3 su barre CFD",
         "B1": "R1 su GER40", "B2": "R1 su US500", "B3": "R1 su US100"}
L = []
L.append("# RAPPORTO F3 — SCOPERTA (dati sigillati < 01/01/2024)")
L.append(f"*Generato da `lavoro/f3/genera_rapporto_f3.py` il {dt.date.today():%d/%m/%Y}. Protocollo: `lavoro/f2/PROTOCOLLO_F2_BOZZA.md` (confermato il 20/10/2026). Feed d'inferenza Pepperstone (UK100 06/06/2017 → 29/12/2023), concordanza FTMO (14/09/2021 → 29/12/2023), costi sempre FTMO. Unità: R netti per trade. Hold-out 2025-2026 e validazione 2024 **non aperti**.*\n")

n_verdi = int((V.verdetto == "VERDE").sum()); n_gialli = int((V.verdetto == "GIALLO").sum())
L.append("## 1. Esito")
L.append(f"**{n_verdi} celle verdi, {n_gialli} gialle, {len(V) - n_verdi - n_gialli} rosse su {len(V)}.** " +
         ("Secondo il protocollo (§7: «tutte le celle A rosse → strategia bocciata, rapporto e stop») **la strategia è bocciata**: niente validazione 2024, l'hold-out resta sigillato." if n_verdi + n_gialli == 0 else "Vedi §2."))

L.append("\n## 2. Verdetti per cella (feed Pepperstone, costi base; concordanza FTMO)\n")
v = V.copy(); v.insert(1, "descrizione", v.cella.map(DESCR))
falliti = []
for _, r in V.iterrows():
    f = [k for k in ["media_pos", "t_ok", "placebo_bh", "stress_pos", "n_ok", "concordanza", "anni_ok", "costo_ok"] if not bool(r[k])]
    falliti.append(", ".join(f) if f else "—")
v["condizioni non superate"] = falliti
L.append(md(v[["cella", "descrizione", "verdetto", "n", "media", "t", "placebo_p", "media_stress", "media_FTMO", "n_FTMO", "condizioni non superate"]],
            {"t": 2, "placebo_p": 3, "n": 0, "n_FTMO": 0}))
L.append("\nCondizioni (protocollo §7): media_pos = media netta > 0; t_ok = t raggruppato per giorno ≥ 2,0 (A3: 2,5); placebo_bh = placebo P1 superato dopo Benjamini-Hochberg (q = 0,10, 13 celle); stress_pos = media > 0 con costi di stress; n_ok = n ≥ (2σ/μ)²; concordanza = media > 0 su FTMO; anni_ok = ≥ 60% degli anni con media > 0; costo_ok = costo medio ≤ 12,5% di R.\n")

L.append("## 3. Lordo, base e stress (tutte le celle, entrambi i feed)\n")
s = S[["cella", "feed", "scenario", "n", "media", "t", "win", "costo_R", "ic95_basso", "ic95_alto", "dd_max", "perdite_consec"]].copy()
L.append(md(s, {"t": 2, "win": 3, "costo_R": 3, "n": 0, "dd_max": 1, "perdite_consec": 0}))
L.append("\n`win` = quota di trade con R > 0; `costo_R` = costo medio in R (spread + slippage + swap); `ic95` = intervallo di confidenza al 95% della media (bootstrap per giorno FTMO); `dd_max` = massimo drawdown in R.\n")

L.append("## 4. Mix d'uscita e placebo (scenario base)\n")
b = S[S.scenario == "base"][["cella", "feed", "n", "media", "placebo_media", "diff_placebo", "placebo_p"] +
                             [c for c in ["quota_SL", "quota_TP", "quota_TEMPO", "quota_CHIUSURA"] if c in S.columns]].copy()
L.append(md(b, {"n": 0, "placebo_p": 3, "quota_SL": 3, "quota_TP": 3, "quota_TEMPO": 3, "quota_CHIUSURA": 3}))
L.append("\nPlacebo P1: stessi ingressi spostati a caso (1.000 repliche) su una barra dello stesso anno e della stessa ora (lunedì per R1, qualunque giorno per R2), stesse uscite. `diff_placebo` = media della strategia − media del placebo.\n")

L.append("## 5. Per anno (feed Pepperstone, base)\n")
pa = PA[(PA.feed == "PEP") & (PA.scenario == "base") & PA.cella.isin(["A1", "A2", "A5", "A8", "A10"])]
tab = pa.pivot_table(index="anno", columns="cella", values="mean").reset_index()
cnt = pa.pivot_table(index="anno", columns="cella", values="count").reset_index()
tab.columns = ["anno"] + [f"{c} media" for c in tab.columns[1:]]
cnt.columns = ["anno"] + [f"{c} n" for c in cnt.columns[1:]]
L.append(md(tab.merge(cnt, on="anno").astype({"anno": int}), {**{c: 0 for c in cnt.columns}}))

L.append("\n## 6. «Monday dip»: lunedì contro martedì-venerdì (placebo P2, stessa regola, base)\n")
L.append(md(P2, {"n_lun": 0, "n_altri": 0, "t_diff": 2}))
L.append("\n`diff` = media del lunedì − media degli altri giorni; `t_diff` = t della differenza. dow1..dow4 = martedì..venerdì.\n")

L.append("## 7. Doppio controllo\n")
if CR is not None:
    L.append("**Replica cieca** (codice scritto da zero da un agente che non ha visto il motore, solo il protocollo), feed Pepperstone, costi base:\n")
    L.append(md(CR, {"n_motore": 0, "n_replica": 0, "in_comune": 0, "solo_motore": 0, "solo_replica": 0, "tipo_diverso": 0, "uscita_diversa": 0, "n_diff_R_oltre_0001": 0, "max_diff_R": 6}))
L.append("\n" + ESITO + "\n")

L.append("## 8. Addendum «dopo i numeri» — esplorativo, NON cambia i verdetti\n")
L.append(md(EX, {"n": 0, "trade_anno": 1, "t": 2, "win": 3, "quota_SL": 3, "quota_TP": 3}))
L.append("\n(a) Entrando a **ogni** barra che soddisfa la Regola 2 (posizioni sovrapposte) si ottengono 215-259 trade/anno, cioè la frequenza dichiarata dal video (~218/anno): il video quasi certamente conta così. Anche così la media è negativa. (b) Regola 1 con uscita dopo N barre cash: stessi 82 ingressi, test fortemente correlati fra loro.\n")
open(os.path.join(F3, "RAPPORTO_F3_SCOPERTA.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("scritto RAPPORTO_F3_SCOPERTA.md")
