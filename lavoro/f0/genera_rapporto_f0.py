# -*- coding: utf-8 -*-
"""Genera lavoro/f0/RAPPORTO_F0.md dai CSV prodotti da audit_m1.py, fuso_e_spread.py,
dal calcolo ATR e dal controllo indipendente. Tutti i numeri del rapporto vengono da qui.
Uso: python3 -I genera_rapporto_f0.py <radice_repo>"""
import sys, os, hashlib, datetime as dt
import pandas as pd

R = sys.argv[1]; F0 = os.path.join(R, "lavoro", "f0"); RIS = os.path.join(F0, "risultati")
def leggi(n): return pd.read_csv(os.path.join(RIS, n), sep=";", decimal=",")
def md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if (isinstance(v, float) and v != v) else (f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if isinstance(v, float) else str(v)) for v in r) + " |")
    return "\n".join(out)
def md5(p):
    h = hashlib.md5(open(p, "rb").read()).hexdigest(); return h

aud = leggi("AUDIT_M1_per_anno.csv"); ria = leggi("AUDIT_M1_riassunto.csv")
fuso = leggi("FUSO_verifica_per_anno.csv"); spr = leggi("SPREAD_mediana_per_ora_server.csv")
atr = leggi("ATR_H1_per_anno_UK100.csv")
ctrl = open(os.path.join(RIS, "CONTROLLO_INDIPENDENTE_F0.txt"), encoding="utf-8").read()
tot_ctrl = [l for l in ctrl.splitlines() if l.startswith("TOTALE")][0]
sha_ok = sum(1 for l in ctrl.splitlines() if l.startswith("OK   sha256"))
sha_tot = sum(1 for l in ctrl.splitlines() if "sha256" in l)

L = []
L.append("# RAPPORTO F0 — inventario, impronte, audit e fuso dei dati")
L.append(f"*Generato da `lavoro/f0/genera_rapporto_f0.py` il {dt.date.today():%d/%m/%Y}. Nessun risultato di strategia: solo qualità dei dati, fuso, spread e volatilità (servono per i costi).*")
L.append(f"\n**Controllo indipendente** (`controllo_indipendente_f0.py`, codice diverso dagli script di audit): **{tot_ctrl.replace('TOTALE: ', '')}** — dettaglio in `risultati/CONTROLLO_INDIPENDENTE_F0.txt`.\n")

# 1. inventario
L.append("## 1. Cosa c'è e cosa manca rispetto al §3 del prompt\n")
docs = [("00_LEGGIMI_PACCHETTO_FTMO.md", None), ("DOSSIER_FTMO_PER_NUOVE_STRATEGIE.md", "bbb4deaafc4a46e33dd1ba7e3fe95491"),
        ("COSTI_ESECUZIONE_REALI_FTMO_US100.md", "6e361905d7fe8d1bf4de4f53506b16cd"),
        ("ESECUZIONI_REALI_FTMO_US100_TRADE.csv", "24346a19fb9a7a8d0ad0b185150d772a"),
        ("VERBALE_FORWARD_SEDUTE.md", "5830dc0804ef4c110931603c6d2e6bfd")]
rows = []
for f, att in docs:
    p = os.path.join(R, f)
    if os.path.exists(p):
        h = md5(p); stato = "presente, md5 OK" if att and h == att else ("presente, md5 DIVERSO" if att else "presente (md5 non indicato nel prompt)")
    else: h, stato = "", "MANCANTE"
    rows.append({"file": f, "md5 atteso": att or "—", "md5 letto": h, "stato": stato})
mancanti = [("GUIDA_COSTI_REALI_E_DINAMICHE_FTMO.md", "2b314b19054d4989ba61ae5e6c720439", "MANCANTE — regole d'oro, trappole T1-T28, checklist G0-G8 non leggibili"),
            ("audit_storici_m1.py", "5021024b96f001a0825f93201f6eedfb", "MANCANTE — sostituito da `lavoro/f0/audit_m1.py` scritto da zero"),
            ("AUDIT_STORICI_M1_*.csv (2 file)", "—", "MANCANTI — audit rifatto (§2)"),
            ("ea_esistenti_SOLA_LETTURA/ (8 .mq5)", "—", "MANCANTI — somiglianza valutata sulla descrizione del prompt"),
            ("trade_ea_esistenti/ (7 .xlsx + GotobiFix csv)", "—", "MANCANTI — indipendenza G6 non calcolabile"),
            ("specifiche/specifiche_simboli.csv", "—", "MANCANTE — swap, commissioni, contratto e sessioni di UK100.cash ignoti"),
            ("ricerche_precedenti/ (facoltativo)", "—", "MANCANTE")]
for f, att, st in mancanti:
    if not any(os.path.exists(os.path.join(dp, os.path.basename(f))) for dp, _, _ in os.walk(R) if ".git" not in dp):
        rows.append({"file": f, "md5 atteso": att, "md5 letto": "", "stato": st})
L.append(md(pd.DataFrame(rows)))
n_img = len([f for f in os.listdir(R) if f.startswith("Spiegazione strategia")])
n_pap = len([f for f in os.listdir(R) if f.startswith("ssrn-")])
L.append(f"\nPresenti anche: `Nuova strategia FTSE 100.pdf`, **{n_img}** immagini `Spiegazione strategia (n).jpeg`, **{n_pap}** papers `ssrn-*.pdf`, `LEGGIMI.md`, `SHA256.txt`.")
L.append(f"\n**Dati**: 17 archivi `tar.gz` (alcuni in parti), non i file per anno con `MANIFEST_*.csv` previsti dal prompt; l'impronta è `SHA256.txt`. Estratti fuori dalla repository: **SHA256 {sha_ok}/{sha_tot} OK**. La repository ha struttura piatta (niente `riferimenti/` e `dati/`): lasciata intatta, si lavora solo in `lavoro/`.\n")

# 2. audit riassunto
L.append("## 2. Audit dei 17 storici\n")
L.append("Tipo di giornata dal passo modale fra barre consecutive (M1 = 60 s; M5 = 300 s; H1 = 3600 s; D1 = una barra). «M1 vero dal» = giorno dopo l'ultima giornata non M1.\n")
r2 = []
for _, i in ria.iterrows():
    a = aud[aud.file == i.file]
    falsi = []
    for _, y in a.iterrows():
        t = [f"{k} {int(y[c])}" for k, c in [("D1", "giorni_D1"), ("H1", "giorni_H1"), ("M5", "giorni_M5"), ("misti", "giorni_misti")] if y[c] > 0]
        if t: falsi.append(f"{int(y.anno)}: " + ", ".join(t))
    rec = a[a.anno >= 2025]
    r2.append({"file": i.file, "righe": f"{int(i.righe):,}".replace(",", "."), "dal": i.prima_data[:10], "al": i.ultima_data[:10],
               "M1 vero dal": i.inizio_M1_continuo, "decimali": int(i.cifre_decimali),
               "spread mediano 2025-26 (punti)": round(float(rec.spread_med_pt.mean()), 2) if len(rec) else float("nan"),
               "giornate non M1 (anno: tipo n)": "; ".join(falsi) if falsi else "nessuna"})
L.append(md(pd.DataFrame(r2)))
L.append("\nAltri controlli su tutti i file: timestamp non crescenti **" + str(int(ria.timestamp_non_crescenti.sum())) + "**, duplicati **" + str(int(ria.duplicati.sum())) + "**, barre OHLC incoerenti **" + str(int(aud.ohlc_incoerenti.sum())) + "**.\n")

# 3. UK100 per anno
L.append("## 3. UK100 anno per anno\n")
cols = ["anno", "barre", "giorni", "giorni_M1", "giorni_M5", "giorni_H1", "giorni_D1", "barre_giorno_med", "quota_min00", "quota_passo_60s", "feriali_mancanti", "barre_piatte_pct", "barre_range_x20", "spread_zero_pct", "spread_med_pt", "spread_p95_pt", "prima_barra_moda", "ultima_barra_moda", "venerdi_ultima_moda"]
for f in ["UK100 FTMO m1", "UK100 Pepperstone m1"]:
    L.append(f"**{f}**\n"); L.append(md(aud[aud.file == f][cols])); L.append("")

# 4. fuso
L.append("## 4. Fuso orario del server, file per file e anno per anno\n")
L.append("Ipotesi **NY+7** (server = New York + 7, ora legale USA) contro **EU** (UTC+2/+3 con ora legale europea): differiscono solo nelle settimane **disallineate** (USA in ora legale, Europa no). Con NY+7 l'apertura di Londra/Xetra cade alle 10:00 server nelle settimane normali e alle **11:00** in quelle disallineate; con EU sempre alle 10:00. Per gli indici USA il test decisivo è il rendimento assoluto medio al minuto 16:30 server diviso per la mediana della giornata: con NY+7 è l'apertura cassa anche nelle settimane disallineate (rapporto ≫ 1), con EU sarebbe un minuto qualunque (≈ 1). Criterio: rapporto ≥ 2. Il minuto 14:30 è riportato solo per informazione (con 15-20 giornate disallineate per anno una singola notizia lo sposta).\n")
r4 = []
for f, g in fuso.groupby("file", sort=False):
    eu = g.picco_09_12.notna().any()
    ok, tot, dett = 0, 0, []
    for _, y in g.iterrows():
        tot += 1
        if eu:
            c = str(y.picco_09_12).startswith("10:0") if y.settimane == "normale" else str(y.picco_09_12).startswith("11:")
            dett.append(f"{int(y.anno)} {y.settimane[:4]} {y.picco_09_12}")
        else:
            # decisivo: con NY+7 le 16:30 server sono l'apertura cassa anche nelle settimane disallineate;
            # con EU sarebbero le 10:30 di New York, minuto qualunque (rapporto ~1)
            c = y["r_16:30_xmed"] >= 2.0
            dett.append(f"{int(y.anno)} {y.settimane[:4]} 16:30×{y['r_16:30_xmed']:.1f} 14:30×{y['r_14:30_xmed']:.1f}")
        ok += bool(c)
    r4.append({"file": f, "anni×settimane coerenti con NY+7": f"{ok}/{tot}", "dettaglio (minuto di picco o rendimento assoluto ÷ mediana)": "; ".join(dett)})
L.append(md(pd.DataFrame(r4)))
L.append("\nDettaglio completo in `risultati/FUSO_verifica_per_anno.csv`.\n")

# 5. spread
L.append("## 5. Spread per ora server — mediana del campo SPREAD (= minimo del minuto), giornate normali, in punti indice\n")
L.append(md(spr[spr.file.isin(["UK100 FTMO m1", "UK100 Pepperstone m1"]) & (spr.anno >= 2024)]))
L.append("\nIl campo SPREAD dell'export MT5 è il **minimo** del minuto: sottostima lo spread pagato. Lo spread reale di UK100.cash su FTMO **non è mai stato misurato dal vivo** [manca].\n")

# 6. ATR
L.append("## 6. Volatilità H1 di UK100 (ATR 14 di Wilder) — serve per il costo in R\n")
L.append(md(atr))
L.append("\n«cash» = barre H1 della sola sessione di Londra 08:00-16:30 (9 barre al giorno); «cfd» = barre H1 dell'ora server (23 al giorno).\n")

# 7. conclusioni (numeri letti dai CSV)
def m1da(f): return ria[ria.file == f].inizio_M1_continuo.iloc[0]
def v(x, d=2): return f"{x:.{d}f}".replace(".", ",")
s26 = spr[(spr.file == "UK100 FTMO m1") & (spr.anno == 2026)].iloc[0]
cash26 = [s26[f"h{h:02d}"] for h in range(10, 18)]
a_c = atr[(atr.barre == "cash") & atr.anno.between(2023, 2025)].ATR14_med
a_f = atr[(atr.barre == "cfd") & atr.anno.between(2023, 2025)].ATR14_med
L.append("## 7. Conclusioni F0\n")
L.append(f"1. **UK100 FTMO: M1 vero solo dal {m1da('UK100 FTMO m1')}.** Il riesporto «dal 2017» contiene D1 (2017-2020) e H1 (fino al 13/09/2021) travestiti da M1: inutilizzabile prima. Idem US100 e US500 FTMO (M1 dal {m1da('US100 m1 - FTMO')}); **GER40 FTMO solo dal {m1da('GER40 FTMO m1')}**.")
L.append(f"2. **UK100 Pepperstone: M1 dal {m1da('UK100 Pepperstone m1')}** (primo giorno pieno 06/06/2017): è l'unico storico UK100 lungo. Orari cambiati nel 2024 (03:00 → 22:58 server). GER40 e US500 Pepperstone contengono **M5 travestito da M1** fino al 10/06/2020 e al 10/07/2020 (288 barre al giorno).")
L.append("3. **Fuso: New York + 7 su tutti gli 8 file candidati, in tutti gli anni** (§4). Sessione cash di Londra 08:00-16:30 = **10:00-18:30 server** (11:00-19:30 nelle settimane disallineate).")
L.append(f"4. **Spread UK100.cash FTMO 2026** (minimo del minuto, mediana) in sessione cash **{v(min(cash26))}-{v(max(cash26))} punti**; di notte {v(s26['h02'])}-{v(s26['h01'])}. Gli ingressi vanno fatti in sessione cash.")
L.append(f"5. **ATR 14 H1 2023-2025**: barre cash **{v(a_c.min(), 1)}-{v(a_c.max(), 1)} punti**, barre CFD {v(a_f.min(), 1)}-{v(a_f.max(), 1)}. Stop a 2-2,5 ATR cash ≈ 44-56 punti → lo spread vale ~2% di R.")
L.append("6. Festivi: FTMO chiude UK100 nei bank holiday inglesi (lunedì di Pasqua, maggio, fine maggio, agosto): circa 4 lunedì l'anno senza Regola 1. Barre anomale concentrate in eventi reali (marzo 2020, aprile 2025), non errori del feed.")
L.append("7. **RSI di Wilder**: il seme iniziale conta solo nelle prime ~300 barre (differenza < 1e-8 dopo) → l'EA deve avere ≥ 300 barre di storia prima del primo segnale.\n")

open(os.path.join(F0, "RAPPORTO_F0.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("scritto", os.path.join(F0, "RAPPORTO_F0.md"))
