# RAPPORTO F3 — SCOPERTA (dati sigillati < 01/01/2024)
*Generato da `lavoro/f3/genera_rapporto_f3.py` il 20/10/2026. Protocollo: `lavoro/f2/PROTOCOLLO_F2_BOZZA.md` (confermato il 20/10/2026). Feed d'inferenza Pepperstone (UK100 06/06/2017 → 29/12/2023), concordanza FTMO (14/09/2021 → 29/12/2023), costi sempre FTMO. Unità: R netti per trade. Hold-out 2025-2026 e validazione 2024 **non aperti**.*

## 1. Esito
- **Lettura L1** della soglia gialla (una deroga alla volta): **0 verdi, 0 gialle, 13 rosse su 13** → per il §7 («tutte le celle A rosse → strategia bocciata») **la strategia è bocciata**.
- **Lettura L2** (deroghe cumulabili, addendum §8): gialle **A2**, nessuna verde → nessuna cella va avanti in automatico; una gialla avanza **solo con il tuo via esplicito**.
- **La Regola 2** (il grosso dei trade del video) **non ha edge nemmeno lordo**. La **Regola 1** («Monday dip») è positiva ma non significativa dopo la correzione per i test multipli, e rara (~13 trade l'anno).
- Validazione 2024 e hold-out 2025-2026 **non aperti**.

## 2. Verdetti per cella (feed Pepperstone, costi base; concordanza FTMO)

| cella | descrizione | verdetto | verdetto_L2 | n | media | t | placebo_p | media_stress | media_FTMO | n_FTMO | condizioni non superate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | R1 fedele, uscita 24 ore | ROSSO | ROSSO | 82 | +0,106 | 1,02 | 0,174 | +0,067 | +0,118 | 26 | t_ok, placebo_bh, n_ok, anni_ok |
| A2 | R1, uscita 24 barre cash | ROSSO | GIALLO | 82 | +0,260 | 1,89 | 0,015 | +0,210 | +0,125 | 26 | t_ok, placebo_bh, n_ok |
| A3 | R1, uscita la sera (PDF) | ROSSO | ROSSO | 82 | +0,036 | 0,45 | 0,176 | +0,015 | +0,088 | 26 | t_ok, placebo_bh, n_ok, anni_ok |
| A4 | R2 k=2, 24 ore | ROSSO | ROSSO | 441 | -0,016 | -0,33 | 0,147 | -0,078 | -0,071 | 148 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| A5 | R2 k=3, 24 ore | ROSSO | ROSSO | 359 | -0,034 | -0,61 | 0,235 | -0,085 | -0,074 | 121 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| A6 | R2 k=4, 24 ore | ROSSO | ROSSO | 236 | -0,009 | -0,13 | 0,152 | -0,058 | -0,093 | 78 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| A7 | R2 k=3, 24 barre cash | ROSSO | ROSSO | 319 | -0,058 | -0,89 | 0,296 | -0,123 | -0,106 | 107 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| A8 | portafoglio A1 + A5 | ROSSO | ROSSO | 441 | -0,008 | -0,15 | 0,159 | -0,057 | -0,040 | 147 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| A9 | R1 su barre CFD | ROSSO | ROSSO | 161 | -0,004 | -0,05 | 0,261 | -0,114 | -0,057 | 50 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| A10 | R2 k=3 su barre CFD | ROSSO | ROSSO | 689 | -0,052 | -1,10 | 0,169 | -0,147 | -0,017 | 218 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, concordanza, anni_ok |
| B1 | R1 su GER40 | ROSSO | ROSSO | 40 | -0,066 | -0,46 | 0,751 | -0,081 | +0,083 | 23 | media_pos, t_ok, placebo_bh, stress_pos, n_ok, anni_ok |
| B2 | R1 su US500 | ROSSO | ROSSO | 32 | +0,149 | 1,05 | 0,182 | +0,103 | +0,064 | 21 | t_ok, placebo_bh, n_ok |
| B3 | R1 su US100 | ROSSO | ROSSO | 70 | +0,068 | 0,71 | 0,470 | +0,048 | +0,214 | 25 | t_ok, placebo_bh, n_ok, anni_ok |

Condizioni (protocollo §7): media_pos = media netta > 0; t_ok = t raggruppato per giorno ≥ 2,0 (A3: 2,5); placebo_bh = placebo P1 superato dopo Benjamini-Hochberg (q = 0,10, 13 celle); stress_pos = media > 0 con costi di stress; n_ok = n ≥ (2σ/μ)²; concordanza = media > 0 su FTMO; anni_ok = ≥ 60% degli anni con media > 0; costo_ok = costo medio ≤ 12,5% di R.

## 3. Lordo, base e stress (tutte le celle, entrambi i feed)

| cella | feed | scenario | n | media | t | win | costo_R | ic95_basso | ic95_alto | dd_max | perdite_consec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | FTMO | base | 26 | +0,118 | 0,59 | 0,500 | 0,020 | -0,257 | +0,511 | 2,9 | 3 |
| A1 | FTMO | lordo | 26 | +0,134 | 0,67 | 0,500 | 0,000 | -0,242 | +0,526 | 2,8 | 3 |
| A1 | FTMO | stress | 26 | +0,085 | 0,43 | 0,500 | 0,058 | -0,289 | +0,476 | 3,3 | 3 |
| A1 | PEP | base | 82 | +0,106 | 1,02 | 0,561 | 0,021 | -0,097 | +0,310 | 4,7 | 3 |
| A1 | PEP | lordo | 82 | +0,130 | 1,26 | 0,561 | 0,000 | -0,072 | +0,333 | 4,0 | 3 |
| A1 | PEP | stress | 82 | +0,067 | 0,64 | 0,549 | 0,064 | -0,135 | +0,271 | 5,1 | 4 |
| A2 | FTMO | base | 26 | +0,125 | 0,49 | 0,462 | 0,026 | -0,352 | +0,626 | 3,7 | 3 |
| A2 | FTMO | lordo | 26 | +0,144 | 0,56 | 0,462 | 0,000 | -0,333 | +0,645 | 3,6 | 3 |
| A2 | FTMO | stress | 26 | +0,080 | 0,32 | 0,462 | 0,079 | -0,394 | +0,580 | 4,0 | 3 |
| A2 | PEP | base | 82 | +0,260 | 1,89 | 0,561 | 0,029 | -0,006 | +0,529 | 4,4 | 4 |
| A2 | PEP | lordo | 82 | +0,298 | 2,18 | 0,573 | 0,000 | +0,034 | +0,566 | 4,3 | 4 |
| A2 | PEP | stress | 82 | +0,210 | 1,53 | 0,549 | 0,088 | -0,054 | +0,478 | 4,7 | 4 |
| A3 | FTMO | base | 26 | +0,088 | 0,60 | 0,654 | 0,013 | -0,194 | +0,369 | 1,6 | 2 |
| A3 | FTMO | lordo | 26 | +0,099 | 0,67 | 0,654 | 0,000 | -0,183 | +0,380 | 1,5 | 2 |
| A3 | FTMO | stress | 26 | +0,068 | 0,47 | 0,615 | 0,035 | -0,213 | +0,349 | 1,6 | 2 |
| A3 | PEP | base | 82 | +0,036 | 0,45 | 0,585 | 0,014 | -0,120 | +0,192 | 3,8 | 4 |
| A3 | PEP | lordo | 82 | +0,048 | 0,59 | 0,598 | 0,000 | -0,108 | +0,204 | 3,7 | 3 |
| A3 | PEP | stress | 82 | +0,015 | 0,19 | 0,585 | 0,038 | -0,140 | +0,171 | 4,3 | 4 |
| A4 | FTMO | base | 148 | -0,071 | -0,84 | 0,432 | 0,028 | -0,231 | +0,099 | 13,9 | 5 |
| A4 | FTMO | lordo | 148 | -0,035 | -0,41 | 0,432 | 0,000 | -0,193 | +0,135 | 8,6 | 7 |
| A4 | FTMO | stress | 150 | -0,118 | -1,39 | 0,400 | 0,080 | -0,278 | +0,054 | 20,9 | 7 |
| A4 | PEP | base | 441 | -0,016 | -0,33 | 0,465 | 0,029 | -0,111 | +0,083 | 23,7 | 9 |
| A4 | PEP | lordo | 436 | +0,010 | 0,21 | 0,468 | 0,000 | -0,085 | +0,111 | 18,2 | 9 |
| A4 | PEP | stress | 444 | -0,078 | -1,57 | 0,444 | 0,082 | -0,173 | +0,022 | 39,1 | 9 |
| A5 | FTMO | base | 121 | -0,074 | -0,78 | 0,430 | 0,027 | -0,250 | +0,118 | 11,1 | 5 |
| A5 | FTMO | lordo | 122 | -0,032 | -0,34 | 0,434 | 0,000 | -0,210 | +0,159 | 7,2 | 5 |
| A5 | FTMO | stress | 122 | -0,113 | -1,19 | 0,402 | 0,078 | -0,290 | +0,080 | 15,5 | 5 |
| A5 | PEP | base | 359 | -0,034 | -0,61 | 0,451 | 0,028 | -0,141 | +0,077 | 24,2 | 8 |
| A5 | PEP | lordo | 355 | -0,006 | -0,11 | 0,454 | 0,000 | -0,113 | +0,105 | 19,4 | 8 |
| A5 | PEP | stress | 360 | -0,085 | -1,53 | 0,428 | 0,081 | -0,191 | +0,025 | 35,0 | 8 |
| A6 | FTMO | base | 78 | -0,093 | -0,76 | 0,436 | 0,026 | -0,316 | +0,161 | 9,6 | 4 |
| A6 | FTMO | lordo | 78 | -0,042 | -0,34 | 0,436 | 0,000 | -0,265 | +0,209 | 8,8 | 4 |
| A6 | FTMO | stress | 79 | -0,125 | -1,00 | 0,392 | 0,075 | -0,351 | +0,132 | 11,6 | 4 |
| A6 | PEP | base | 236 | -0,009 | -0,13 | 0,462 | 0,027 | -0,141 | +0,133 | 14,1 | 9 |
| A6 | PEP | lordo | 234 | +0,023 | 0,32 | 0,466 | 0,000 | -0,110 | +0,166 | 10,6 | 9 |
| A6 | PEP | stress | 237 | -0,058 | -0,83 | 0,447 | 0,076 | -0,191 | +0,084 | 18,6 | 9 |
| A7 | FTMO | base | 107 | -0,106 | -0,91 | 0,355 | 0,032 | -0,324 | +0,132 | 13,1 | 6 |
| A7 | FTMO | lordo | 107 | -0,081 | -0,69 | 0,355 | 0,000 | -0,298 | +0,159 | 11,0 | 6 |
| A7 | FTMO | stress | 108 | -0,167 | -1,44 | 0,343 | 0,093 | -0,383 | +0,069 | 19,7 | 6 |
| A7 | PEP | base | 319 | -0,058 | -0,89 | 0,395 | 0,033 | -0,185 | +0,073 | 29,2 | 10 |
| A7 | PEP | lordo | 314 | -0,016 | -0,24 | 0,401 | 0,000 | -0,143 | +0,115 | 22,7 | 9 |
| A7 | PEP | stress | 323 | -0,123 | -1,87 | 0,384 | 0,094 | -0,250 | +0,009 | 45,2 | 10 |
| A8 | FTMO | base | 147 | -0,040 | -0,43 | 0,442 | 0,026 | -0,216 | +0,148 | 9,7 | 5 |
| A8 | FTMO | lordo | 148 | -0,003 | -0,03 | 0,446 | 0,000 | -0,180 | +0,187 | 8,4 | 5 |
| A8 | FTMO | stress | 148 | -0,078 | -0,83 | 0,419 | 0,075 | -0,255 | +0,113 | 13,3 | 5 |
| A8 | PEP | base | 441 | -0,008 | -0,15 | 0,472 | 0,027 | -0,112 | +0,101 | 26,5 | 9 |
| A8 | PEP | lordo | 437 | +0,020 | 0,36 | 0,474 | 0,000 | -0,085 | +0,128 | 21,2 | 9 |
| A8 | PEP | stress | 442 | -0,057 | -1,05 | 0,450 | 0,077 | -0,161 | +0,052 | 33,3 | 9 |
| A9 | FTMO | base | 50 | -0,057 | -0,41 | 0,460 | 0,070 | -0,321 | +0,221 | 7,1 | 4 |
| A9 | FTMO | lordo | 50 | +0,052 | 0,36 | 0,520 | 0,000 | -0,218 | +0,334 | 6,6 | 4 |
| A9 | FTMO | stress | 50 | -0,168 | -1,21 | 0,420 | 0,152 | -0,431 | +0,110 | 10,1 | 4 |
| A9 | PEP | base | 161 | -0,004 | -0,05 | 0,497 | 0,077 | -0,162 | +0,157 | 12,9 | 6 |
| A9 | PEP | lordo | 161 | +0,105 | 1,26 | 0,540 | 0,000 | -0,057 | +0,270 | 9,3 | 6 |
| A9 | PEP | stress | 161 | -0,114 | -1,40 | 0,453 | 0,164 | -0,269 | +0,047 | 19,8 | 6 |
| A10 | FTMO | base | 218 | -0,017 | -0,19 | 0,408 | 0,064 | -0,185 | +0,175 | 26,9 | 9 |
| A10 | FTMO | lordo | 211 | +0,059 | 0,63 | 0,436 | 0,000 | -0,113 | +0,253 | 22,6 | 9 |
| A10 | FTMO | stress | 220 | -0,114 | -1,27 | 0,382 | 0,144 | -0,280 | +0,073 | 36,6 | 10 |
| A10 | PEP | base | 689 | -0,052 | -1,10 | 0,396 | 0,068 | -0,143 | +0,044 | 50,1 | 21 |
| A10 | PEP | lordo | 672 | +0,027 | 0,56 | 0,414 | 0,000 | -0,067 | +0,127 | 24,7 | 20 |
| A10 | PEP | stress | 704 | -0,147 | -3,12 | 0,372 | 0,153 | -0,235 | -0,051 | 113,1 | 21 |
| B1 | FTMO | base | 23 | +0,083 | 0,43 | 0,522 | 0,011 | -0,280 | +0,456 | 3,7 | 4 |
| B1 | FTMO | lordo | 23 | +0,092 | 0,48 | 0,522 | 0,000 | -0,271 | +0,465 | 3,6 | 4 |
| B1 | FTMO | stress | 23 | +0,067 | 0,35 | 0,522 | 0,029 | -0,296 | +0,440 | 3,9 | 4 |
| B1 | PEP | base | 40 | -0,066 | -0,46 | 0,500 | 0,012 | -0,339 | +0,213 | 4,1 | 4 |
| B1 | PEP | lordo | 40 | -0,057 | -0,40 | 0,500 | 0,000 | -0,331 | +0,222 | 4,0 | 4 |
| B1 | PEP | stress | 40 | -0,081 | -0,57 | 0,500 | 0,031 | -0,355 | +0,197 | 4,6 | 4 |
| B2 | FTMO | base | 21 | +0,064 | 0,41 | 0,476 | 0,018 | -0,228 | +0,359 | 4,3 | 9 |
| B2 | FTMO | lordo | 21 | +0,081 | 0,52 | 0,524 | 0,000 | -0,211 | +0,376 | 4,1 | 8 |
| B2 | FTMO | stress | 21 | +0,013 | 0,08 | 0,476 | 0,064 | -0,284 | +0,313 | 4,8 | 9 |
| B2 | PEP | base | 32 | +0,149 | 1,05 | 0,531 | 0,021 | -0,124 | +0,422 | 4,3 | 9 |
| B2 | PEP | lordo | 32 | +0,168 | 1,18 | 0,531 | 0,000 | -0,105 | +0,441 | 4,2 | 9 |
| B2 | PEP | stress | 32 | +0,103 | 0,73 | 0,531 | 0,070 | -0,168 | +0,374 | 4,7 | 9 |
| B3 | FTMO | base | 25 | +0,214 | 1,45 | 0,600 | 0,008 | -0,072 | +0,496 | 3,8 | 7 |
| B3 | FTMO | lordo | 25 | +0,228 | 1,56 | 0,600 | 0,000 | -0,054 | +0,507 | 3,6 | 7 |
| B3 | FTMO | stress | 25 | +0,202 | 1,36 | 0,600 | 0,021 | -0,085 | +0,484 | 3,9 | 7 |
| B3 | PEP | base | 70 | +0,068 | 0,71 | 0,557 | 0,014 | -0,118 | +0,254 | 5,7 | 7 |
| B3 | PEP | lordo | 70 | +0,084 | 0,88 | 0,557 | 0,000 | -0,101 | +0,268 | 5,0 | 7 |
| B3 | PEP | stress | 70 | +0,048 | 0,50 | 0,543 | 0,035 | -0,139 | +0,234 | 6,4 | 7 |

`win` = quota di trade con R > 0; `costo_R` = costo medio in R (spread + slippage + swap); `ic95` = intervallo di confidenza al 95% della media (bootstrap per giorno FTMO); `dd_max` = massimo drawdown in R.

## 4. Mix d'uscita e placebo (scenario base)

| cella | feed | n | media | placebo_media | diff_placebo | placebo_p | quota_SL | quota_TP | quota_TEMPO | quota_CHIUSURA |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | FTMO | 26 | +0,118 | +0,070 | +0,048 | 0,393 | 0,308 | 0,077 | 0,615 | — |
| A1 | PEP | 82 | +0,106 | +0,024 | +0,082 | 0,174 | 0,293 | 0,049 | 0,659 | — |
| A2 | FTMO | 26 | +0,125 | +0,084 | +0,040 | 0,412 | 0,500 | 0,192 | 0,308 | — |
| A2 | PEP | 82 | +0,260 | -0,012 | +0,272 | 0,015 | 0,427 | 0,244 | 0,329 | — |
| A3 | FTMO | 26 | +0,088 | +0,038 | +0,050 | 0,313 | 0,231 | — | 0,769 | — |
| A3 | PEP | 82 | +0,036 | -0,024 | +0,059 | 0,176 | 0,207 | — | 0,793 | — |
| A4 | FTMO | 148 | -0,071 | -0,059 | -0,012 | 0,563 | 0,412 | 0,088 | 0,345 | 0,155 |
| A4 | PEP | 441 | -0,016 | -0,064 | +0,048 | 0,147 | 0,415 | 0,084 | 0,354 | 0,147 |
| A5 | FTMO | 121 | -0,074 | -0,068 | -0,006 | 0,521 | 0,421 | 0,074 | 0,347 | 0,157 |
| A5 | PEP | 359 | -0,034 | -0,068 | +0,034 | 0,235 | 0,437 | 0,084 | 0,345 | 0,134 |
| A6 | FTMO | 78 | -0,093 | -0,064 | -0,030 | 0,613 | 0,410 | 0,103 | 0,321 | 0,167 |
| A6 | PEP | 236 | -0,009 | -0,070 | +0,061 | 0,152 | 0,415 | 0,093 | 0,373 | 0,119 |
| A7 | FTMO | 107 | -0,106 | -0,068 | -0,037 | 0,626 | 0,551 | 0,178 | 0,056 | 0,215 |
| A7 | PEP | 319 | -0,058 | -0,089 | +0,031 | 0,296 | 0,539 | 0,169 | 0,078 | 0,213 |
| A8 | FTMO | 147 | -0,040 | -0,043 | +0,004 | 0,478 | 0,401 | 0,075 | 0,395 | 0,129 |
| A8 | PEP | 441 | -0,008 | -0,051 | +0,043 | 0,159 | 0,410 | 0,077 | 0,404 | 0,109 |
| A9 | FTMO | 50 | -0,057 | -0,130 | +0,073 | 0,285 | 0,400 | 0,040 | 0,560 | — |
| A9 | PEP | 161 | -0,004 | -0,055 | +0,051 | 0,261 | 0,429 | 0,056 | 0,516 | — |
| A10 | FTMO | 218 | -0,017 | -0,107 | +0,090 | 0,120 | 0,532 | 0,193 | 0,151 | 0,124 |
| A10 | PEP | 689 | -0,052 | -0,093 | +0,040 | 0,169 | 0,546 | 0,180 | 0,165 | 0,109 |
| B1 | FTMO | 23 | +0,083 | -0,002 | +0,085 | 0,276 | 0,304 | — | 0,696 | — |
| B1 | PEP | 40 | -0,066 | +0,023 | -0,089 | 0,751 | 0,400 | 0,025 | 0,575 | — |
| B2 | FTMO | 21 | +0,064 | +0,008 | +0,056 | 0,371 | 0,143 | — | 0,857 | — |
| B2 | PEP | 32 | +0,149 | +0,021 | +0,128 | 0,182 | 0,188 | — | 0,812 | — |
| B3 | FTMO | 25 | +0,214 | +0,022 | +0,192 | 0,109 | 0,120 | — | 0,880 | — |
| B3 | PEP | 70 | +0,068 | +0,062 | +0,006 | 0,470 | 0,243 | — | 0,743 | 0,014 |

Placebo P1: stessi ingressi spostati a caso (1.000 repliche) su una barra dello stesso anno e della stessa ora (lunedì per R1, qualunque giorno per R2), stesse uscite. `diff_placebo` = media della strategia − media del placebo.

## 5. Per anno (feed Pepperstone, base)

| anno | A1 media | A10 media | A2 media | A5 media | A8 media | A1 n | A10 n | A2 n | A5 n | A8 n |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.017 | -0,020 | +0,024 | +0,588 | -0,135 | -0,116 | 4 | 50 | 4 | 21 | 25 |
| 2.018 | -0,175 | -0,164 | -0,075 | -0,208 | -0,202 | 16 | 118 | 16 | 76 | 92 |
| 2.019 | +0,157 | +0,039 | +0,497 | +0,027 | +0,055 | 13 | 106 | 13 | 47 | 60 |
| 2.020 | +0,256 | -0,035 | +0,553 | +0,075 | +0,106 | 13 | 122 | 13 | 63 | 76 |
| 2.021 | +0,140 | -0,154 | +0,228 | +0,102 | +0,111 | 13 | 90 | 13 | 44 | 57 |
| 2.022 | +0,467 | +0,086 | +0,331 | -0,024 | +0,087 | 15 | 88 | 15 | 51 | 66 |
| 2.023 | -0,328 | -0,099 | -0,179 | -0,050 | -0,084 | 8 | 115 | 8 | 57 | 65 |

## 6. «Monday dip»: lunedì contro martedì-venerdì (placebo P2, stessa regola, base)

| cella | feed | n_lun | media_lun | n_altri | media_altri | diff | t_diff | media_dow1 | media_dow2 | media_dow3 | media_dow4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | PEP | 82 | +0,106 | 421 | -0,039 | +0,145 | 1,29 | -0,003 | -0,139 | +0,043 | -0,075 |
| A2 | PEP | 82 | +0,260 | 421 | -0,071 | +0,331 | 2,26 | -0,194 | -0,151 | +0,086 | -0,075 |
| A3 | PEP | 82 | +0,036 | 421 | -0,043 | +0,079 | 0,91 | -0,004 | -0,027 | -0,057 | -0,075 |
| A1 | FTMO | 26 | +0,118 | 138 | -0,023 | +0,141 | 0,66 | -0,101 | -0,210 | +0,271 | -0,138 |
| A2 | FTMO | 26 | +0,125 | 138 | -0,037 | +0,162 | 0,60 | -0,185 | -0,173 | +0,264 | -0,138 |
| A3 | FTMO | 26 | +0,088 | 138 | -0,030 | +0,118 | 0,76 | -0,019 | -0,048 | +0,068 | -0,138 |
| B1 | PEP | 40 | -0,066 | 231 | +0,014 | -0,080 | -0,52 | +0,042 | -0,210 | +0,132 | +0,054 |
| B1 | FTMO | 23 | +0,083 | 135 | -0,019 | +0,102 | 0,50 | -0,209 | -0,223 | +0,150 | +0,109 |
| B2 | PEP | 32 | +0,149 | 203 | -0,050 | +0,199 | 1,31 | -0,025 | -0,199 | +0,104 | -0,074 |
| B2 | FTMO | 21 | +0,064 | 147 | -0,029 | +0,093 | 0,56 | -0,008 | -0,085 | +0,050 | -0,070 |
| B3 | PEP | 70 | +0,068 | 345 | +0,016 | +0,052 | 0,50 | +0,225 | -0,059 | +0,010 | -0,102 |
| B3 | FTMO | 25 | +0,214 | 149 | +0,048 | +0,166 | 1,04 | +0,179 | +0,178 | -0,033 | -0,113 |

`diff` = media del lunedì − media degli altri giorni; `t_diff` = t della differenza. dow1..dow4 = martedì..venerdì.

## 7. Doppio controllo

**Confronto finale con la replica cieca**: codice scritto da zero da un agente che non ha visto il motore, a cui ho aggiunto soltanto le due correzioni del §7.3 (`controllo/replica_corretta/`). Feed Pepperstone, costi base:

| cella | n_motore | n_replica | in_comune | solo_motore | solo_replica | tipo_diverso | uscita_diversa | max_diff_R | media_motore | media_replica |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | 82 | 82 | 82 | 0 | 0 | 0 | 0 | 0,0000005 | +0,106 | +0,106 |
| A2 | 82 | 82 | 82 | 0 | 0 | 0 | 0 | 0,0000005 | +0,260 | +0,260 |
| A5 | 359 | 359 | 359 | 0 | 0 | 0 | 0 | 0,0000005 | -0,034 | -0,034 |

### 7.1 Come è stato fatto il doppio controllo (20/10/2026)
- **Replica cieca**: un agente ha riscritto il backtest da zero dal solo protocollo, senza vedere il motore (`controllo/replica/replica_f3.py`, più una seconda implementazione in Python puro per barre e indicatori, `verifica_mano.py`), e ha verificato a mano 4 trade sui dati grezzi.
  - **Prima esecuzione: identica trade per trade.** A1 82/82, A2 82/82, A5 358/358; stessi ingressi, uscite e tipi d'uscita; differenza massima di R 5e-7 (arrotondamento).
  - Dopo le correzioni del §7.3 la replica **originale** differisce solo in 5 stop in gap (nuova formula del protocollo `min(open, SL) − slippage`) e in 4 trade vicini ai semi-festivi di fine 2019, come previsto e come calcolato anche dal giudice (`controllo/CONFRONTO_REPLICA.csv`). La replica **corretta** coincide con il motore trade per trade (tabella qui sopra).
- **Revisione avversaria a tre lenti**: anticipo e allineamento dei dati, meccanica dei trade e costi, statistica e verdetti. Gli script dei revisori sono in `controllo/revisione/`.
  - Il revisore della meccanica ha ricalcolato **tutti** i 10.372 trade in modo indipendente.
  - Le barre di sessione sono state ricostruite con le regole dell'ora legale scritte a mano, senza `zoneinfo`: 0 differenze.
  - I dati sigillati non contengono righe del 2024 o successive, e il codice non legge mai l'archivio completo.
  - Gli indicatori, ricalcolati sulla serie troncata alla barra del segnale, danno valori identici: nessun anticipo.
- **Giudice**: ha riprodotto tutte le 72 combinazioni cella × feed × scenario (differenza 4e-16) e il placebo esatto (A2: p = 0,014985). Poi ha rifatto ogni rilievo con codice proprio (`controllo/giudice/`).

### 7.2 Rilievi (12, tutti reali, nessuno cambia i numeri in modo rilevante)
| # | Rilievo | Effetto sulle medie | Esito |
|---|---|---|---|
| 1 | Uscite forzate calcolate dall'ultima quotazione effettiva del giorno (nota solo a posteriori) | ±0,0005 R | invariato; per la validazione e per l'EA servirà il calendario delle sessioni del broker (`SymbolInfoSessionTrade`) |
| 2 | Semi-festivi LSE (24 e 31/12): sessione fino alle 16:30 invece che alle 12:30 | da −0,0025 a +0,0043 R | **corretto** (addendum) |
| 3 | GER40/US500/US100: chiusure dedotte dai dati | 1 trade (B3) | invariato: tutti i giorni senza dati sono festivi programmati |
| 4 | Buchi di dati ≥ 2 ore non trattati come chiusure | fino a −0,013 R (A2) | **non corretto**: il giudice ha verificato che sono guasti del feed (31/12/2019, 10/01/2022), non chiusure note in anticipo. Trattarli come chiusure userebbe informazione futura |
| 5 | Stop in gap: il codice usava `min(open, SL − slip)`, il protocollo dice `min(open, SL) − slip` | al massimo −0,0007 R | **corretto** per allinearlo al protocollo |
| 6-7 | Soglia GIALLO: il testo del §7 non dice cosa fare se una cella ha **entrambe** le deroghe (A2) | cambia il verdetto di A2 | **decisione tua**: vedi §9 |
| 8 | P2 calcolato solo per A1, non per A2 e A3 | — | **corretto** (il §6 lo chiede per tutte le R1) |
| 9 | Limite inferiore dell'IC95 bootstrap di A2 positivo solo con un seme e 5.000 repliche | — | **corretto**: ora 100.000 repliche, IC di A2 [−0,006; +0,529] |
| 10 | t raggruppato senza correzione per pochi gruppi (CR0) | t −0,6% | **corretto**: ora CR1 (più prudente) |
| 11 | Fascia gialla di A3 [1; 2,5) non scritta nel protocollo | nessuno | registrata nell'addendum |
| 12 | Il 2017 parziale conta come anno intero nella quota di anni positivi | nessuno sui verdetti | registrato nell'addendum (il 2017 ha 7 mesi di dati) |

### 7.3 Verifica delle correzioni
Ho rieseguito ogni correzione da sola e l'ho confrontata con la ri-simulazione indipendente del giudice. Le opzioni `--senza-semifestivi` e `--gap-vecchio` di `esegui_f3.py` permettono di riprodurle una per una.
- Stop in gap: **48/48** medie per cella, feed e scenario coincidono entro 5e-6.
- Semi-festivi: **28/28** celle coincidono per numero di trade e media.

I numeri di questo rapporto sono quelli con **tutte** le correzioni. **Controllo finale del risultato combinato**: alla copia della replica cieca ho aggiunto solo le due correzioni (`controllo/replica_corretta/replica_f3_corretta.py`). Coincide con il motore trade per trade: A1 82/82, A2 82/82, A5 359/359, stessi ingressi, uscite e tipi, differenza di R ≤ 5e-7 (`controllo/CONFRONTO_REPLICA_CORRETTA.csv`).


## 8. Addendum «dopo i numeri» — esplorativo, NON cambia i verdetti

| prova | feed | n | trade_anno | media | t | win | quota_SL | quota_TP |
|---|---|---|---|---|---|---|---|---|
| (a) R2 ogni barra k=0 | PEP | 1.667 | 258,9 | -0,058 | -1,16 | 0,448 | 0,420 | 0,073 |
| (a) R2 ogni barra k=3 | PEP | 1.384 | 214,9 | -0,058 | -1,03 | 0,446 | 0,423 | 0,075 |
| (b) R1 uscita 6 barre | PEP | 82 | 12,7 | +0,061 | 0,76 | 0,573 | 0,171 | 0,012 |
| (b) R1 uscita 12 barre | PEP | 82 | 12,7 | +0,155 | 1,31 | 0,537 | 0,354 | 0,061 |
| (b) R1 uscita 18 barre | PEP | 82 | 12,7 | +0,263 | 1,96 | 0,549 | 0,415 | 0,183 |
| (b) R1 uscita 24 barre | PEP | 82 | 12,7 | +0,260 | 1,89 | 0,561 | 0,427 | 0,244 |
| (b) R1 uscita 30 barre | PEP | 82 | 12,7 | +0,234 | 1,62 | 0,488 | 0,463 | 0,256 |
| (b) R1 uscita 36 barre | PEP | 82 | 12,7 | +0,163 | 1,12 | 0,451 | 0,488 | 0,268 |
| (a) R2 ogni barra k=0 | FTMO | 549 | 253,5 | -0,103 | -1,21 | 0,435 | 0,419 | 0,069 |
| (a) R2 ogni barra k=3 | FTMO | 467 | 215,6 | -0,109 | -1,18 | 0,437 | 0,422 | 0,069 |
| (b) R1 uscita 6 barre | FTMO | 26 | 12,0 | +0,110 | 0,75 | 0,577 | 0,192 | 0,000 |
| (b) R1 uscita 12 barre | FTMO | 26 | 12,0 | +0,125 | 0,56 | 0,500 | 0,385 | 0,115 |
| (b) R1 uscita 18 barre | FTMO | 26 | 12,0 | +0,107 | 0,43 | 0,500 | 0,500 | 0,192 |
| (b) R1 uscita 24 barre | FTMO | 26 | 12,0 | +0,125 | 0,49 | 0,462 | 0,500 | 0,192 |
| (b) R1 uscita 30 barre | FTMO | 26 | 12,0 | +0,090 | 0,34 | 0,385 | 0,538 | 0,231 |
| (b) R1 uscita 36 barre | FTMO | 26 | 12,0 | -0,039 | -0,15 | 0,346 | 0,615 | 0,269 |

(a) Entrando a **ogni** barra che soddisfa la Regola 2 (posizioni sovrapposte) si ottengono 215-259 trade/anno, cioè la frequenza dichiarata dal video (~218/anno): il video quasi certamente conta così. Anche così la media è negativa. (b) Regola 1 con uscita dopo N barre cash: stessi 82 ingressi, test fortemente correlati fra loro.

## 9. Decisione che spetta a te

La sola cella discutibile è **A2** (Regola 1 del lunedì, uscita dopo 24 barre cash): media **+0,260 R** su **82** trade, t **1,89**, intervallo di confidenza al 95% **[-0,006; +0,529]** (2,8% delle repliche ≤ 0), placebo p **0,015** (soglia Benjamini-Hochberg 0,0077), lunedì contro altri giorni **+0,331 R** (t 2,26).
- È la migliore di **3 uscite** provate per la stessa regola (24 ore +0,106, sera +0,036): la correzione per test multipli serve proprio a questo.
- **Frequenza**: 12,7 trade l'anno → anche se l'edge fosse vero, **3,3 R l'anno**. Con l'1% di rischio per trade la fase 1 FTMO (+10%) richiederebbe in media **~3,0 anni**.
- **Validazione 2024 quasi cieca**: ~13 trade, errore standard della media ≈ 0,35 R → con l'edge vero di 0,26 R il t atteso sarebbe ≈ 0,74: non distinguerebbe un edge da zero.
- **Raccomandazione**: considerare la strategia **bocciata** (lettura L1) e non spendere la validazione 2024 né l'hold-out su A2; l'effetto del lunedì resta un indizio, non una strategia.
