# EVENT STUDY MULTI-STRUMENTO — RAPPORTO (dati di scoperta < 2024)
*Generato da `genera_rapporto_event_study.py` il 20/10/2026. Piano pre-registrato: `PIANO_EVENT_STUDY.md` (commit precedente ai risultati). 242 test, 7 famiglie, 10 strumenti. Correzione di Benjamini-Hochberg (q = 0,10) calcolata dal workflow e ricalcolata in modo indipendente (`consolida_event_study.py`): stesso esito, classi identiche 242/242.*

## 1. Esito
- **Test che superano Benjamini-Hochberg: 0 su 242.** Nessun effetto PROMETTENTE.
- p < 0,05: **19** (attesi per caso 12,1); p < 0,01: **4** (attesi 2,4). Leggero eccesso, concentrato su un gruppo: **il dollaro (USDX) segue con un giorno di ritardo metalli e indici**.
- INDIZI (p < 0,05 senza correzione, anni e concordanza ok): **19**.

## 2. Per famiglia

| famiglia | effetto | test | p_min | p_sotto_005 | indizi |
|---|---|---|---|---|---|
| A | Turn of the month e ribilanciamento | 18 | 0,1429 | 0 | 0 |
| B | FOMC (prima e dopo) | 20 | 0,0025 | 3 | 3 |
| C | Scadenze opzioni e festivi | 20 | 0,0370 | 2 | 2 |
| E | Lunedì in calo → recupero | 24 | 0,0715 | 0 | 0 |
| F | Correlazioni fra strumenti | 108 | 0,0005 | 11 | 11 |
| G | Flussi orari materie prime | 12 | 0,0102 | 2 | 2 |
| I | Momentum di serie storica | 40 | 0,0330 | 1 | 1 |

## 3. I 20 test con p più basso

| famiglia | test_id | n | eventi_anno | media_z | t | p_primario | quota_anni_stesso_segno | netto_base_z | netto_stress_z | conc_ftmo_media | classe_mia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F | F1:XAU->USDX | 1133 | 227 | -0,123 | -3,82 | 0,0005 | 1,00 | +0,022 | -0,119 | — | INDIZIO |
| F | F1:XAG->USDX | 1133 | 227 | -0,103 | -3,12 | 0,0020 | 1,00 | -0,037 | -0,178 | — | INDIZIO |
| B | B2_VIX | 30 | 8 | +0,633 | +1,92 | 0,0025 | 0,75 | — | — | — | INDIZIO |
| F | F1:UK100->BRENT | 1384 | 231 | +0,083 | +2,60 | 0,0080 | 0,83 | +0,020 | -0,081 | — | INDIZIO |
| G | G2_XAU_notte | 1610 | 249 | +0,043 | +2,57 | 0,0102 | 0,86 | -0,054 | -0,132 | +0,016 | INDIZIO |
| F | F1:BRENT->BRENT | 1392 | 232 | +0,075 | +2,13 | 0,0110 | 0,67 | -0,037 | -0,138 | — | INDIZIO |
| F | F1:USDX->UK100 | 1133 | 227 | +0,079 | +2,19 | 0,0125 | 0,60 | -0,037 | -0,218 | +0,109 | INDIZIO |
| G | G2_BRENT_notte | 1404 | 248 | +0,051 | +2,44 | 0,0147 | 0,83 | -0,008 | -0,108 | — | INDIZIO |
| F | F1:GER40->USDX | 859 | 215 | -0,089 | -2,35 | 0,0165 | 0,75 | -0,026 | -0,155 | — | INDIZIO |
| B | B2_USDX | 35 | 8 | -0,395 | -1,37 | 0,0205 | 0,80 | +0,325 | +0,208 | — | INDIZIO |
| F | F1:US500->USDX | 837 | 209 | -0,086 | -2,30 | 0,0225 | 0,75 | -0,018 | -0,146 | — | INDIZIO |
| F | F1:UK100->USDX | 1134 | 227 | -0,072 | -2,11 | 0,0240 | 0,60 | -0,022 | -0,162 | — | INDIZIO |
| F | F1:USDX->GER40 | 859 | 215 | +0,083 | +2,19 | 0,0255 | 0,75 | +0,067 | +0,002 | +0,038 | INDIZIO |
| I | I_VIX_L1 | 44 | 11 | -0,318 | -2,26 | 0,0330 | 1,00 | — | — | — | INDIZIO |
| C | C5_US500 | 31 | 8 | -0,361 | -1,42 | 0,0370 | 1,00 | +0,318 | +0,231 | -0,492 | INDIZIO |
| F | F1:XAG->USOIL | 653 | 218 | +0,088 | +1,92 | 0,0375 | 0,67 | +0,045 | -0,034 | — | INDIZIO |
| F | F1:XAU->USOIL | 653 | 218 | +0,085 | +1,89 | 0,0445 | 1,00 | +0,036 | -0,043 | — | INDIZIO |
| B | B1_VIX | 30 | 8 | -0,399 | -2,10 | 0,0455 | 0,75 | — | — | — | INDIZIO |
| C | C2_GER40 | 42 | 10 | -0,657 | -1,45 | 0,0465 | 1,00 | +0,580 | +0,448 | -0,458 | INDIZIO |
| F | F1:US100->USDX | 1130 | 226 | -0,061 | -1,83 | 0,0565 | 0,60 | -0,050 | -0,191 | — | NULLO |

`media_z` = effetto medio per evento in multipli della volatilità giornaliera (per le regressioni: pendenza). `netto_*_z` = trade nel verso dell'effetto, dopo costi FTMO (spread, commissione, swap).

## 4. Verifica avversaria (ricalcolo da zero dei 6 migliori)

| test | verdetto | motivo |
|---|---|---|
| F1:XAU->USDX | CONFERMATO | Ricalcolo da zero (x = z XAU al giorno d, chiusura 16:00 NY; y = z USDX al giorno di trading successivo; sigma di y sui 20 rendimenti fino a d incluso). Ottengo n 1147 contro 1133 e b -0.107 contro -0.1226. Corr -0.111 contro -0.117, t -3.79 contro -3.82, p di… |
| B2_VIX | FRAGILE | Riprodotto esattamente: n 30 (tutte le riunioni programmate dal 29/04/2020 al 13/12/2023, compresa quella di giovedì 05/11/2020), media z 0.6328, t 1.915, p del placebo 0.0025 (sigma che include il giorno FOMC). Anomala 0.653 contro 0.637. Ingresso all'M1 dell… |
| G2_XAU_notte | NON CONFERMATO | I numeri grezzi si riproducono: n 1618 contro 1610, media z 0.0458 contro 0.0435, t 2.70 contro 2.57 (p normale 0.007), 6 anni su 7 positivi, netto base -0.0515 z (identico al valore dichiarato con l'ora dell'M1 delle 22), stress -0.125. Il risultato però conf… |
| F1:XAG->USDX | FRAGILE | Riprodotto. Ho riscritto allineamento e regressione da zero: OLS di z_USDX(d+1) su z_XAG(d), t robusto HC1, che equivale a CR1 con un evento per data, p con 2000 permutazioni. Risultato: b tra -0.091 e -0.095 (originale -0.103), t tra -2.9 e -3.1, p=0.0015. Il… |
| F1:UK100->BRENT | FRAGILE | Riprodotto. Con la sigma del segnale che include il giorno d: b=0.078 (originale 0.083), t=2.38, p perm=0.010, p a shift=0.011. Con la sigma fino a d-1: b=0.066, t=2.27, p=0.018. Con UK100 misurato alle 16:00 NY invece che alla chiusura cash delle 11:30-12:30 … |
| F1:BRENT->BRENT | FRAGILE | Riprodotto solo sul p del placebo, al limite. Con la sigma del segnale che include d: b=0.0735 (originale 0.0749), t=2.11, p perm=0.0145. Con la sigma fino a d-1: b=0.063, t HC1=1.85 (sotto 1.96), p perm=0.017. Il p per permutazione è più ottimista del t robus… |

## 5. Addendum «dopo i numeri» (non cambia la classificazione)
```
XAU->USDX: n 1012, pendenza -0.1070, p permutazione (200.000) = 0.000590  | soglia BH rango 1 = 0.000413, rango 2 = 0.000826
XAG->USDX: n 1012, pendenza -0.0974, p permutazione (200.000) = 0.002230  | soglia BH rango 1 = 0.000413, rango 2 = 0.000826
          test strumento  n  media_z  anomala  t_welch  p_welch
   B1 pre-FOMC     US500 27   0.2610   0.2255   1.4273   0.1654
C4 pre-festivo     US500 32   0.1749   0.1303   1.0297   0.3111
   B1 pre-FOMC     US100 51   0.2939   0.2293   2.4109   0.0196
C4 pre-festivo     US100 60   0.1802   0.1158   1.1264   0.2646
   B1 pre-FOMC     GER40 28   0.3874   0.3869   2.3917   0.0240
C4 pre-festivo     GER40 11   0.5171   0.5102   3.1753   0.0099
   B1 pre-FOMC     UK100 51   0.0254   0.0424   0.3386   0.7364
C4 pre-festivo     UK100 40   0.2043   0.2220   1.8929   0.0658
B1 paniere dei 4 indici, un valore per data: n date 51, anomala media +0.149 z, t 1.64, p 0.1077
C4 paniere dei 4 indici, un valore per data: n date 81, anomala media +0.167 z, t 2.09, p 0.0400
```
- Con 200.000 permutazioni il p di XAU→USDX resta **sopra** la soglia di rango 1 (0,000413): l'esito «0 su 242» non dipende dalla risoluzione del placebo.
- Drift pre-FOMC: positivo su US100 e GER40 (test di Welch p ≈ 0,02), debole su US500, nullo su UK100. Pre-festivi: paniere dei 4 indici p 0,04. Sono **indizi** coerenti con la letteratura, non prove.
