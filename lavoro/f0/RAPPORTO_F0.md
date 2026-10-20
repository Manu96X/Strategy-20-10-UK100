# RAPPORTO F0 — inventario, impronte, audit e fuso dei dati
*Generato da `lavoro/f0/genera_rapporto_f0.py` il 20/10/2026. Nessun risultato di strategia: solo qualità dei dati, fuso, spread e volatilità (servono per i costi).*

**Controllo indipendente** (`controllo_indipendente_f0.py`, codice diverso dagli script di audit): **82/82 OK** — dettaglio in `risultati/CONTROLLO_INDIPENDENTE_F0.txt`.

## 1. Cosa c'è e cosa manca rispetto al §3 del prompt

| file | md5 atteso | md5 letto | stato |
|---|---|---|---|
| 00_LEGGIMI_PACCHETTO_FTMO.md | — | 3aef2fb34ca38eb05d92f4e782b24aef | presente (md5 non indicato nel prompt) |
| DOSSIER_FTMO_PER_NUOVE_STRATEGIE.md | bbb4deaafc4a46e33dd1ba7e3fe95491 | bbb4deaafc4a46e33dd1ba7e3fe95491 | presente, md5 OK |
| COSTI_ESECUZIONE_REALI_FTMO_US100.md | 6e361905d7fe8d1bf4de4f53506b16cd | 6e361905d7fe8d1bf4de4f53506b16cd | presente, md5 OK |
| ESECUZIONI_REALI_FTMO_US100_TRADE.csv | 24346a19fb9a7a8d0ad0b185150d772a | 24346a19fb9a7a8d0ad0b185150d772a | presente, md5 OK |
| VERBALE_FORWARD_SEDUTE.md | 5830dc0804ef4c110931603c6d2e6bfd | 5830dc0804ef4c110931603c6d2e6bfd | presente, md5 OK |
| GUIDA_COSTI_REALI_E_DINAMICHE_FTMO.md | 2b314b19054d4989ba61ae5e6c720439 |  | MANCANTE — regole d'oro, trappole T1-T28, checklist G0-G8 non leggibili |
| audit_storici_m1.py | 5021024b96f001a0825f93201f6eedfb |  | MANCANTE — sostituito da `lavoro/f0/audit_m1.py` scritto da zero |
| AUDIT_STORICI_M1_*.csv (2 file) | — |  | MANCANTI — audit rifatto (§2) |
| ea_esistenti_SOLA_LETTURA/ (8 .mq5) | — |  | MANCANTI — somiglianza valutata sulla descrizione del prompt |
| trade_ea_esistenti/ (7 .xlsx + GotobiFix csv) | — |  | MANCANTI — indipendenza G6 non calcolabile |
| specifiche/specifiche_simboli.csv | — |  | MANCANTE — swap, commissioni, contratto e sessioni di UK100.cash ignoti |
| ricerche_precedenti/ (facoltativo) | — |  | MANCANTE |

Presenti anche: `Nuova strategia FTSE 100.pdf`, **31** immagini `Spiegazione strategia (n).jpeg`, **6** papers `ssrn-*.pdf`, `LEGGIMI.md`, `SHA256.txt`.

**Dati**: 17 archivi `tar.gz` (alcuni in parti), non i file per anno con `MANIFEST_*.csv` previsti dal prompt; l'impronta è `SHA256.txt`. Estratti fuori dalla repository: **SHA256 17/17 OK**. La repository ha struttura piatta (niente `riferimenti/` e `dati/`): lasciata intatta, si lavora solo in `lavoro/`.

## 2. Audit dei 17 storici

Tipo di giornata dal passo modale fra barre consecutive (M1 = 60 s; M5 = 300 s; H1 = 3600 s; D1 = una barra). «M1 vero dal» = giorno dopo l'ultima giornata non M1.

| file | righe | dal | al | M1 vero dal | decimali | spread mediano 2025-26 (punti) | giornate non M1 (anno: tipo n) |
|---|---|---|---|---|---|---|---|
| BRENT m1 - Pepperstone | 2.860.707 | 2017-08-28 | 2026-08-28 | 2018-03-31 | 3 | 0,02 | 2018: D1 1 |
| DXY FTMO m1 | 593.321 | 2024-11-26 | 2026-10-09 | 2024-11-26 | 3 | 0,02 | nessuna |
| GER40 FTMO m1 | 1.632.495 | 2017-12-28 | 2026-10-09 | 2021-12-28 | 2 | 1,64 | 2017: D1 2; 2018: D1 136; 2019: D1 233; 2020: D1 258; 2021: D1 94, H1 159 |
| GER40 Pepperstone m1 | 2.113.045 | 2017-01-02 | 2026-09-18 | 2020-06-11 | 1 | 1,20 | 2017: misti 252; 2018: H1 118, misti 133; 2019: H1 182, misti 73; 2020: M5 43, misti 71 |
| NAS100 m1 - FTPepperstone | 3.256.223 | 2017-01-03 | 2026-09-18 | 2017-06-09 | 1 | 1,30 | 2017: H1 112 |
| UK100 FTMO m1 | 1.704.709 | 2017-12-28 | 2026-10-09 | 2021-09-14 | 2 | 1,70 | 2017: D1 2; 2018: D1 157, misti 148; 2019: D1 253; 2020: D1 257; 2021: D1 9, H1 167 |
| UK100 Pepperstone m1 | 3.033.501 | 2017-01-03 | 2026-08-28 | 2017-06-03 | 1 | 1,80 | 2017: H1 105 |
| US100 m1 - FTMO | 1.780.816 | 2017-12-29 | 2026-10-09 | 2021-09-14 | 2 | 1,52 | 2017: D1 1; 2018: D1 258; 2019: D1 259; 2020: D1 259; 2021: D1 13, H1 167, misti 1 |
| US500 m1 - FTMO | 1.758.281 | 2017-12-29 | 2026-10-09 | 2021-09-14 | 2 | 0,56 | 2017: D1 1; 2018: D1 258; 2019: D1 259; 2020: D1 259; 2021: D1 13, H1 168 |
| US500 m1 - Pepperstone | 2.205.128 | 2017-01-03 | 2026-09-18 | 2020-07-11 | 1 | 0,40 | 2017: D1 257; 2018: D1 257; 2019: D1 58, misti 200; 2020: H1 43, M5 9, misti 84 |
| USDX pepperstone m1 | 2.927.735 | 2017-01-03 | 2026-08-28 | 2019-04-20 | 3 | 0,05 | 2017: H1 102; 2018: misti 1; 2019: D1 1 |
| USOIL m1 - FTMO | 1.995.765 | 2020-12-31 | 2026-10-09 | 2021-04-03 | 3 | 0,05 | 2021: M5 1 |
| VIX Pepperstone m1 | 1.716.168 | 2020-03-03 | 2026-08-28 | 2023-05-18 | 2 | 0,16 | 2020: misti 1; 2021: misti 20; 2022: misti 13; 2023: misti 9 |
| XAG-USD FTMO m1 | 3.409.182 | 2017-01-03 | 2026-10-09 | 2021-01-02 | 3 | 0,04 | 2021: D1 1 |
| XAG-USD Pepperstone m1 | 3.235.165 | 2017-01-03 | 2026-08-28 | 2017-06-09 | 3 | 0,03 | 2017: H1 112 |
| XAU-USD FTMO m1 | 3.426.068 | 2017-01-03 | 2026-10-09 | 2021-01-02 | 2 | 0,34 | 2021: D1 1 |
| XAU-USD Pepperstone m1 | 3.278.844 | 2017-01-03 | 2026-09-18 | 2017-06-10 | 2 | 0,14 | 2017: H1 113 |

Altri controlli su tutti i file: timestamp non crescenti **0**, duplicati **0**, barre OHLC incoerenti **0**.

## 3. UK100 anno per anno

**UK100 FTMO m1**

| anno | barre | giorni | giorni_M1 | giorni_M5 | giorni_H1 | giorni_D1 | barre_giorno_med | quota_min00 | quota_passo_60s | feriali_mancanti | barre_piatte_pct | barre_range_x20 | spread_zero_pct | spread_med_pt | spread_p95_pt | prima_barra_moda | ultima_barra_moda | venerdi_ultima_moda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 2 | 2 | 0 | 0 | 0 | 2 | 1,00 | 1,00 |  | 0 | 0,00 | 0 | 100,00 | 0,00 | 0,00 | 00:00 | 00:00 | 00:00 |
| 2018 | 453 | 305 | 0 | 0 | 0 | 157 | 1,00 | 1,00 | 0,00 | 3 | 0,00 | 0 | 100,00 | 0,00 | 0,00 | 00:00 | 00:00 | 00:00 |
| 2019 | 253 | 253 | 0 | 0 | 0 | 253 | 1,00 | 1,00 |  | 7 | 0,00 | 0 | 100,00 | 0,00 | 0,00 | 00:00 | 00:00 | 00:00 |
| 2020 | 257 | 257 | 0 | 0 | 0 | 257 | 1,00 | 1,00 |  | 4 | 0,00 | 0 | 100,00 | 0,00 | 0,00 | 00:00 | 00:00 | 00:00 |
| 2021 | 107221 | 253 | 77 | 0 | 167 | 9 | 23,00 | 0,05 | 0,96 | 7 | 2,86 | 414 | 19,19 | 0,80 | 7,20 | 01:00 | 23:00 | 23:00 |
| 2022 | 334885 | 250 | 250 | 0 | 0 | 0 | 1.359,00 | 0,02 | 0,99 | 9 | 1,83 | 20 | 0,00 | 0,80 | 6,20 | 01:05 | 23:49 | 23:49 |
| 2023 | 326685 | 251 | 251 | 0 | 0 | 0 | 1.313,00 | 0,02 | 0,97 | 8 | 3,69 | 8 | 0,00 | 0,70 | 6,10 | 01:05 | 23:49 | 23:49 |
| 2024 | 333942 | 254 | 254 | 0 | 0 | 0 | 1.324,50 | 0,02 | 0,98 | 7 | 4,35 | 19 | 0,00 | 1,05 | 6,10 | 01:05 | 23:49 | 23:49 |
| 2025 | 337492 | 253 | 253 | 0 | 0 | 0 | 1.354,00 | 0,02 | 0,99 | 7 | 1,61 | 148 | 0,01 | 1,75 | 5,85 | 01:05 | 23:49 | 22:54 |
| 2026 | 263519 | 196 | 196 | 0 | 0 | 0 | 1.363,00 | 0,02 | 1,00 | 5 | 0,51 | 15 | 0,00 | 1,65 | 5,51 | 01:05 | 23:49 | 22:49 |

**UK100 Pepperstone m1**

| anno | barre | giorni | giorni_M1 | giorni_M5 | giorni_H1 | giorni_D1 | barre_giorno_med | quota_min00 | quota_passo_60s | feriali_mancanti | barre_piatte_pct | barre_range_x20 | spread_zero_pct | spread_med_pt | spread_p95_pt | prima_barra_moda | ultima_barra_moda | venerdi_ultima_moda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 170510 | 252 | 147 | 0 | 105 | 0 | 1.093,50 | 0,03 | 0,91 | 7 | 8,70 | 241 | 20,65 | 1,00 | 4,00 | 01:00 | 23:58 | 23:00 |
| 2018 | 309196 | 254 | 254 | 0 | 0 | 0 | 1.229,50 | 0,02 | 0,95 | 6 | 8,56 | 14 | 0,00 | 1,00 | 6,50 | 01:00 | 23:58 | 23:58 |
| 2019 | 319752 | 253 | 253 | 0 | 0 | 0 | 1.269,00 | 0,02 | 0,95 | 7 | 5,93 | 9 | 0,00 | 1,00 | 6,50 | 00:01 | 23:59 | 23:59 |
| 2020 | 357576 | 259 | 259 | 0 | 0 | 0 | 1.389,00 | 0,02 | 0,98 | 2 | 2,20 | 48 | 0,00 | 2,00 | 4,00 | 00:01 | 23:59 | 23:59 |
| 2021 | 357059 | 260 | 260 | 0 | 0 | 0 | 1.384,00 | 0,02 | 0,98 | 0 | 2,66 | 7 | 0,00 | 2,00 | 4,00 | 00:01 | 23:58 | 23:54 |
| 2022 | 355865 | 255 | 255 | 0 | 0 | 0 | 1.413,00 | 0,02 | 0,99 | 4 | 1,58 | 20 | 0,00 | 2,00 | 4,00 | 00:01 | 23:58 | 23:54 |
| 2023 | 341896 | 254 | 254 | 0 | 0 | 0 | 1.359,00 | 0,02 | 0,98 | 5 | 2,70 | 14 | 0,00 | 2,00 | 6,00 | 01:00 | 23:58 | 22:54 |
| 2024 | 320270 | 254 | 254 | 0 | 0 | 0 | 1.199,00 | 0,02 | 0,99 | 7 | 1,68 | 21 | 0,60 | 1,80 | 6,00 | 03:00 | 22:58 | 22:54 |
| 2025 | 301542 | 253 | 253 | 0 | 0 | 0 | 1.198,00 | 0,02 | 1,00 | 7 | 0,86 | 98 | 0,00 | 1,80 | 2,40 | 03:00 | 22:58 | 22:54 |
| 2026 | 199835 | 167 | 167 | 0 | 0 | 0 | 1.199,00 | 0,02 | 1,00 | 4 | 0,18 | 5 | 0,00 | 1,80 | 2,20 | 03:00 | 22:58 | 22:54 |

## 4. Fuso orario del server, file per file e anno per anno

Ipotesi **NY+7** (server = New York + 7, ora legale USA) contro **EU** (UTC+2/+3 con ora legale europea): differiscono solo nelle settimane **disallineate** (USA in ora legale, Europa no). Con NY+7 l'apertura di Londra/Xetra cade alle 10:00 server nelle settimane normali e alle **11:00** in quelle disallineate; con EU sempre alle 10:00. Per gli indici USA il test decisivo è il rendimento assoluto medio al minuto 16:30 server diviso per la mediana della giornata: con NY+7 è l'apertura cassa anche nelle settimane disallineate (rapporto ≫ 1), con EU sarebbe un minuto qualunque (≈ 1). Criterio: rapporto ≥ 2. Il minuto 14:30 è riportato solo per informazione (con 15-20 giornate disallineate per anno una singola notizia lo sposta).

| file | anni×settimane coerenti con NY+7 | dettaglio (minuto di picco o rendimento assoluto ÷ mediana) |
|---|---|---|
| UK100 FTMO m1 | 12/12 | 2021 disa 11:00; 2021 norm 10:00; 2022 disa 11:00; 2022 norm 10:00; 2023 disa 11:00; 2023 norm 10:00; 2024 disa 11:00; 2024 norm 10:00; 2025 disa 11:00; 2025 norm 10:00; 2026 disa 11:00; 2026 norm 10:00 |
| UK100 Pepperstone m1 | 20/20 | 2017 disa 11:02; 2017 norm 10:00; 2018 disa 11:01; 2018 norm 10:00; 2019 disa 11:00; 2019 norm 10:00; 2020 disa 11:00; 2020 norm 10:00; 2021 disa 11:00; 2021 norm 10:00; 2022 disa 11:00; 2022 norm 10:00; 2023 disa 11:00; 2023 norm 10:00; 2024 disa 11:00; 2024 norm 10:00; 2025 disa 11:00; 2025 norm 10:00; 2026 disa 11:00; 2026 norm 10:00 |
| GER40 FTMO m1 | 11/11 | 2021 norm 10:00; 2022 disa 11:05; 2022 norm 10:00; 2023 disa 11:00; 2023 norm 10:00; 2024 disa 11:00; 2024 norm 10:00; 2025 disa 11:16; 2025 norm 10:00; 2026 disa 11:00; 2026 norm 10:00 |
| GER40 Pepperstone m1 | 14/14 | 2020 disa 11:00; 2020 norm 10:00; 2021 disa 11:00; 2021 norm 10:00; 2022 disa 11:07; 2022 norm 10:00; 2023 disa 11:00; 2023 norm 10:00; 2024 disa 11:00; 2024 norm 10:00; 2025 disa 11:16; 2025 norm 10:00; 2026 disa 11:00; 2026 norm 10:00 |
| US500 m1 - FTMO | 12/12 | 2021 disa 16:30×5.1 14:30×0.9; 2021 norm 16:30×3.5 14:30×1.2; 2022 disa 16:30×3.0 14:30×0.9; 2022 norm 16:30×3.7 14:30×1.2; 2023 disa 16:30×3.4 14:30×1.3; 2023 norm 16:30×5.0 14:30×1.2; 2024 disa 16:30×5.5 14:30×1.6; 2024 norm 16:30×4.9 14:30×1.1; 2025 disa 16:30×4.3 14:30×1.2; 2025 norm 16:30×4.8 14:30×1.4; 2026 disa 16:30×4.4 14:30×2.3; 2026 norm 16:30×4.5 14:30×1.2 |
| US500 m1 - Pepperstone | 14/14 | 2020 disa 16:30×3.1 14:30×0.7; 2020 norm 16:30×3.3 14:30×1.0; 2021 disa 16:30×3.5 14:30×1.6; 2021 norm 16:30×3.9 14:30×1.1; 2022 disa 16:30×3.6 14:30×0.9; 2022 norm 16:30×3.9 14:30×1.2; 2023 disa 16:30×3.6 14:30×1.4; 2023 norm 16:30×5.2 14:30×1.2; 2024 disa 16:30×5.8 14:30×1.6; 2024 norm 16:30×4.8 14:30×1.1; 2025 disa 16:30×4.3 14:30×1.2; 2025 norm 16:30×4.7 14:30×1.4; 2026 disa 16:30×4.4 14:30×2.3; 2026 norm 16:30×4.5 14:30×1.2 |
| US100 m1 - FTMO | 12/12 | 2021 disa 16:30×4.7 14:30×1.4; 2021 norm 16:30×5.5 14:30×1.2; 2022 disa 16:30×4.0 14:30×0.9; 2022 norm 16:30×4.8 14:30×1.2; 2023 disa 16:30×3.4 14:30×1.2; 2023 norm 16:30×6.6 14:30×1.3; 2024 disa 16:30×6.1 14:30×1.3; 2024 norm 16:30×5.1 14:30×1.1; 2025 disa 16:30×4.6 14:30×1.1; 2025 norm 16:30×5.5 14:30×1.4; 2026 disa 16:30×5.2 14:30×2.0; 2026 norm 16:30×5.6 14:30×1.2 |
| NAS100 m1 - FTPepperstone | 20/20 | 2017 disa 16:30×2.8 14:30×0.7; 2017 norm 16:30×4.2 14:30×1.0; 2018 disa 16:30×5.8 14:30×0.9; 2018 norm 16:30×4.2 14:30×1.1; 2019 disa 16:30×6.6 14:30×1.0; 2019 norm 16:30×4.4 14:30×1.3; 2020 disa 16:30×4.2 14:30×0.6; 2020 norm 16:30×4.0 14:30×1.1; 2021 disa 16:30×5.2 14:30×1.4; 2021 norm 16:30×5.3 14:30×1.2; 2022 disa 16:30×4.8 14:30×1.0; 2022 norm 16:30×4.9 14:30×1.3; 2023 disa 16:30×3.5 14:30×1.2; 2023 norm 16:30×6.5 14:30×1.3; 2024 disa 16:30×6.1 14:30×1.4; 2024 norm 16:30×5.0 14:30×1.1; 2025 disa 16:30×4.7 14:30×1.1; 2025 norm 16:30×5.4 14:30×1.4; 2026 disa 16:30×5.2 14:30×1.9; 2026 norm 16:30×5.6 14:30×1.1 |

Dettaglio completo in `risultati/FUSO_verifica_per_anno.csv`.

## 5. Spread per ora server — mediana del campo SPREAD (= minimo del minuto), giornate normali, in punti indice

| file | anno | h01 | h02 | h03 | h04 | h05 | h06 | h07 | h08 | h09 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 | h00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UK100 FTMO m1 | 2024 | 6,10 | 6,10 | 2,10 | 2,10 | 2,10 | 2,10 | 2,10 | 2,10 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 6,10 |  |
| UK100 FTMO m1 | 2025 | 5,75 | 5,45 | 4,25 | 3,85 | 3,65 | 3,45 | 3,55 | 3,75 | 1,45 | 0,95 | 0,85 | 0,85 | 0,85 | 0,85 | 0,85 | 0,95 | 0,95 | 1,32 | 1,85 | 1,55 | 1,55 | 1,65 | 6,11 |  |
| UK100 FTMO m1 | 2026 | 5,31 | 4,85 | 4,15 | 3,95 | 3,75 | 3,65 | 3,65 | 3,85 | 1,65 | 0,85 | 0,75 | 0,75 | 0,65 | 0,75 | 0,75 | 0,75 | 0,75 | 0,85 | 1,65 | 1,45 | 1,45 | 1,45 | 5,71 |  |
| UK100 Pepperstone m1 | 2024 | 6,00 | 6,00 | 4,00 | 4,00 | 4,00 | 4,00 | 4,00 | 4,00 | 2,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 2,00 | 2,00 | 2,00 | 2,00 | 6,00 |  |
| UK100 Pepperstone m1 | 2025 |  |  | 1,90 | 1,80 | 1,80 | 1,80 | 1,80 | 1,80 | 1,80 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,80 | 1,80 | 1,80 | 1,80 |  |  |
| UK100 Pepperstone m1 | 2026 |  |  | 2,00 | 1,90 | 1,90 | 1,90 | 1,80 | 1,80 | 1,80 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,20 | 1,80 | 1,80 | 1,80 | 1,80 |  |  |

Il campo SPREAD dell'export MT5 è il **minimo** del minuto: sottostima lo spread pagato. Lo spread reale di UK100.cash su FTMO **non è mai stato misurato dal vivo** [manca].

## 6. Volatilità H1 di UK100 (ATR 14 di Wilder) — serve per il costo in R

| file | barre | anno | barre_H1 | barre_giorno | ATR14_med | stop2ATR_med | stop2.5ATR_med |
|---|---|---|---|---|---|---|---|
| UK100 FTMO m1 | cash | 2021 | 685 | 8,90 | 21,40 | 42,70 | 53,40 |
| UK100 FTMO m1 | cash | 2022 | 2242 | 9,00 | 29,40 | 58,80 | 73,50 |
| UK100 FTMO m1 | cash | 2023 | 2251 | 9,00 | 22,20 | 44,50 | 55,60 |
| UK100 FTMO m1 | cash | 2024 | 2278 | 9,00 | 21,90 | 43,70 | 54,70 |
| UK100 FTMO m1 | cash | 2025 | 2269 | 9,00 | 22,60 | 45,20 | 56,50 |
| UK100 FTMO m1 | cash | 2026 | 1762 | 9,00 | 34,70 | 69,40 | 86,70 |
| UK100 FTMO m1 | cfd | 2021 | 1751 | 22,70 | 15,50 | 31,00 | 38,80 |
| UK100 FTMO m1 | cfd | 2022 | 5702 | 22,80 | 21,20 | 42,40 | 52,90 |
| UK100 FTMO m1 | cfd | 2023 | 5736 | 22,90 | 14,50 | 29,10 | 36,30 |
| UK100 FTMO m1 | cfd | 2024 | 5805 | 22,90 | 15,20 | 30,50 | 38,10 |
| UK100 FTMO m1 | cfd | 2025 | 5732 | 22,70 | 16,50 | 33,00 | 41,20 |
| UK100 FTMO m1 | cfd | 2026 | 4452 | 22,70 | 24,80 | 49,50 | 61,90 |
| UK100 Pepperstone m1 | cash | 2017 | 1317 | 9,00 | 17,90 | 35,80 | 44,70 |
| UK100 Pepperstone m1 | cash | 2018 | 2269 | 9,00 | 22,30 | 44,50 | 55,70 |
| UK100 Pepperstone m1 | cash | 2019 | 2273 | 9,00 | 23,00 | 46,00 | 57,50 |
| UK100 Pepperstone m1 | cash | 2020 | 2330 | 9,00 | 31,40 | 62,70 | 78,40 |
| UK100 Pepperstone m1 | cash | 2021 | 2334 | 9,00 | 22,10 | 44,30 | 55,30 |
| UK100 Pepperstone m1 | cash | 2022 | 2287 | 9,00 | 29,20 | 58,50 | 73,10 |
| UK100 Pepperstone m1 | cash | 2023 | 2276 | 9,00 | 21,80 | 43,70 | 54,60 |
| UK100 Pepperstone m1 | cash | 2024 | 2278 | 9,00 | 21,60 | 43,10 | 53,90 |
| UK100 Pepperstone m1 | cash | 2025 | 2269 | 9,00 | 22,60 | 45,20 | 56,50 |
| UK100 Pepperstone m1 | cash | 2026 | 1503 | 9,00 | 34,50 | 69,10 | 86,40 |
| UK100 Pepperstone m1 | cfd | 2017 | 3323 | 22,60 | 11,70 | 23,40 | 29,20 |
| UK100 Pepperstone m1 | cfd | 2018 | 5749 | 22,60 | 16,10 | 32,20 | 40,20 |
| UK100 Pepperstone m1 | cfd | 2019 | 5908 | 23,40 | 15,00 | 30,00 | 37,50 |
| UK100 Pepperstone m1 | cfd | 2020 | 6155 | 23,80 | 21,90 | 43,70 | 54,70 |
| UK100 Pepperstone m1 | cfd | 2021 | 6163 | 23,70 | 14,90 | 29,80 | 37,30 |
| UK100 Pepperstone m1 | cfd | 2022 | 6048 | 23,70 | 20,40 | 40,80 | 51,00 |
| UK100 Pepperstone m1 | cfd | 2023 | 5854 | 23,00 | 14,10 | 28,30 | 35,30 |
| UK100 Pepperstone m1 | cfd | 2024 | 5394 | 21,20 | 15,50 | 30,90 | 38,70 |
| UK100 Pepperstone m1 | cfd | 2025 | 5042 | 19,90 | 16,90 | 33,80 | 42,20 |
| UK100 Pepperstone m1 | cfd | 2026 | 3340 | 20,00 | 26,50 | 52,90 | 66,20 |

«cash» = barre H1 della sola sessione di Londra 08:00-16:30 (9 barre al giorno); «cfd» = barre H1 dell'ora server (23 al giorno).

## 7. Conclusioni F0

1. **UK100 FTMO: M1 vero solo dal 2021-09-14.** Il riesporto «dal 2017» contiene D1 (2017-2020) e H1 (fino al 13/09/2021) travestiti da M1: inutilizzabile prima. Idem US100 e US500 FTMO (M1 dal 2021-09-14); **GER40 FTMO solo dal 2021-12-28**.
2. **UK100 Pepperstone: M1 dal 2017-06-03** (primo giorno pieno 06/06/2017): è l'unico storico UK100 lungo. Orari cambiati nel 2024 (03:00 → 22:58 server). GER40 e US500 Pepperstone contengono **M5 travestito da M1** fino al 10/06/2020 e al 10/07/2020 (288 barre al giorno).
3. **Fuso: New York + 7 su tutti gli 8 file candidati, in tutti gli anni** (§4). Sessione cash di Londra 08:00-16:30 = **10:00-18:30 server** (11:00-19:30 nelle settimane disallineate).
4. **Spread UK100.cash FTMO 2026** (minimo del minuto, mediana) in sessione cash **0,65-0,85 punti**; di notte 4,85-5,31. Gli ingressi vanno fatti in sessione cash.
5. **ATR 14 H1 2023-2025**: barre cash **21,6-22,6 punti**, barre CFD 14,1-16,9. Stop a 2-2,5 ATR cash ≈ 44-56 punti → lo spread vale ~2% di R.
6. Festivi: FTMO chiude UK100 nei bank holiday inglesi (lunedì di Pasqua, maggio, fine maggio, agosto): circa 4 lunedì l'anno senza Regola 1. Barre anomale concentrate in eventi reali (marzo 2020, aprile 2025), non errori del feed.
7. **RSI di Wilder**: il seme iniziale conta solo nelle prime ~300 barre (differenza < 1e-8 dopo) → l'EA deve avere ≥ 300 barre di storia prima del primo segnale.

