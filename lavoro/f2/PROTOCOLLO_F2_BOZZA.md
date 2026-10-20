# PROTOCOLLO F2 — BOZZA DA CONFERMARE
### Strategia «FTSE 100 — Monday dip + RSI» (specifica: `lavoro/f1/SPECIFICA_STRATEGIA_UK100.md`)
*Scritto il 20/10/2026 **prima di qualunque risultato di strategia**. Dati guardati finora: solo qualità, fuso, spread per ora e ATR mediano per anno (F0). Diventa vincolante con il tuo «confermo»; ogni modifica successiva sarà un addendum datato «prima/dopo i numeri».*

---

## 1. Ipotesi

- **H1 (R1 Monday dip)**: comprare UK100 il lunedì sotto l'apertura cash con RSI 14 < 40 rende in media più di zero al netto dei costi **e più del placebo**.
- **H2 (R2)**: comprare quando la chiusura è ≥ k ATR sotto la SMA 40 con RSI 14 < 35 rende più di zero al netto **e più del placebo**, con **dose-risposta** (k = 4 ≥ k = 3 ≥ k = 2).
- **H3**: il portafoglio R1 + R2 rende più di zero al netto.
- **H4 (punto del PDF)**: il Monday dip esiste anche su GER40, US500, US100 e **il lunedì è diverso dagli altri giorni**.

## 2. Dati e campioni

| Uso | UK100 | GER40 | US500 | US100 |
|---|---|---|---|---|
| **Scoperta, feed d'inferenza** | Pepperstone **06/06/2017 → 31/12/2023** | Pepperstone 11/06/2020 → 2023 | Pepperstone 13/07/2020 → 2023 | NAS100 Pepperstone 09/06/2017 → 2023 |
| Scoperta, concordanza | FTMO **14/09/2021 → 31/12/2023** | FTMO 28/12/2021 → 2023 | FTMO 14/09/2021 → 2023 | FTMO 14/09/2021 → 2023 |
| Validazione | 2024, entrambi i feed | idem | idem | idem |
| **Hold-out sigillato** | **01/01/2025 → fine**, entrambi i feed, aperto **una volta** a regole congelate | idem | idem | idem |

⚠️ **Scostamento dal tuo prompt** (che dice «valida su FTMO, replica su Pepperstone»): UK100 FTMO è M1 vero **solo dal 14/09/2021** (prima D1/H1 travestiti, F0 §2) → in scoperta avrebbe ~2,3 anni, ~110 lunedì: potenza insufficiente. Propongo **inferenza su Pepperstone** (6,5 anni) e FTMO come **concordanza** sullo stesso periodo + **costi sempre FTMO**. Da confermare.

Fuso: server = New York + 7 per tutti i file e gli anni (F0 §4). Sessioni cash da ora locale (Londra 08:00-16:30; Xetra 09:00-17:30; NYSE 09:30-16:00) via `zoneinfo`.

## 3. Simulazione

- Prezzi: M1 **bid** del feed; **ask = bid + spread FTMO 2026 per ora server** (mediana del campo SPREAD 2026, F0 §5; per GER40/US500/US100 la stessa tabella dei loro file FTMO).
- Segnale sulla barra cash **chiusa**; ingresso all'apertura del **primo M1 successivo**, all'ask.
- SL e TP **riancorati al fill**; uscite valutate sul bid M1: SL se `low ≤ SL` (prezzo = min(open, SL) − slippage), TP se `high ≥ TP` (prezzo = TP). **SL e TP nello stesso minuto → prima lo SL** (sensibilità: prima il TP).
- Uscita a tempo all'apertura del primo M1 ≥ scadenza, al bid.
- Weekend e chiusure ≥ 2 ore (festivi): uscita 15 minuti prima dell'ultima quotazione; niente ingressi nelle 2 ore prima. Lunedì festivo: niente R1.
- Gap alla riapertura: lo stop si esegue all'apertura del primo M1 (peggiore del livello).
- Risultato in **R netti** = (uscita − fill − costi) ÷ distanza dello stop.

## 4. Costi (G1)

| Voce | Base | Stress | Etichetta |
|---|---|---|---|
| Spread | FTMO 2026 per ora (cash ≈ 0,65-0,85; dopo le 18:30 server ≈ 0,85-1,65 punti) | **+50%** | [BACKTEST] dal campo SPREAD (= minimo del minuto: sottostima) |
| Slippage sullo stop | +0,8 punti | **× 2,5** = 2,0 | [MISURATO] su US100.cash, trasferito come [STIMA] |
| Ordini a mercato (ingresso, uscita a tempo) | 0 | **+0,5 punti** per ordine | [MISURATO]/[STIMA] |
| Commissioni | 0 | 0 | [STIMA]: 0 su US100.cash [MISURATO], da confermare sulla specifica |
| **Swap long** | **−0,5 punti/notte**, triplo il mercoledì | **−2,0 punti/notte** | [STIMA] — **manca la specifica di UK100.cash** |

Riportati anche: costo totale in % di R (soglia ≤ 12,5%) e **spread di pareggio**. Stima a priori: stop R2 ≈ 2 × 22 = 44 punti → costo base ≈ 3-4% di R, stress ≈ 8-11% di R (swap compreso, 1 notte) [STIMA].

## 5. Celle (tutte nella stessa correzione Benjamini-Hochberg, q = 0,10)

| # | Cella | Note |
|---|---|---|
| A1 | **R1 fedele**: barre cash, uscita **24 ore** | primaria R1 |
| A2 | R1, uscita **24 barre cash** (≈ 2,7 sedute) | grafico del video |
| A3 | R1, uscita **la sera stessa** (23:40 server) | PDF · è intraday mean reversion → soglia verde **t ≥ 2,5** |
| A4 | R2 k = 2, 24 ore | |
| A5 | **R2 k = 3, 24 ore** | primaria R2 |
| A6 | R2 k = 4, 24 ore | |
| A7 | R2 k = 3, 24 barre cash | |
| A8 | **Portafoglio A1 + A5** | H3 |
| A9 | R1 su barre H1 **CFD** (ora server), apertura = primo prezzo della settimana | alternativa «24 ore» |
| A10 | R2 k = 3 su barre H1 CFD | |
| B1 | R1 su **GER40** (Xetra 09:00-17:30) | H4 |
| B2 | R1 su **US500** (NYSE 09:30-16:00) | H4 |
| B3 | R1 su **US100** (NYSE) | H4 |

**Nessun'altra cella**: sensibilità e robustezza (§8) servono solo a giudicare l'altopiano delle celle verdi.

## 6. Nullo e placebo

- **Nullo**: media dei R netti = 0, t con errore raggruppato per **giorno FTMO** d'ingresso (01:00 server).
- **Placebo P1 (drift + meccanica delle uscite)**, per ogni cella: 1.000 repliche dell'intero insieme di trade, ogni ingresso spostato a caso su un giorno dello **stesso anno**, **stesso giorno della settimana** (R1) o qualunque (R2), **stessa ora di barra**, stesse uscite con l'ATR del momento. p-value = quota di repliche con media ≥ quella della strategia. **È il p-value che entra in Benjamini-Hochberg.**
- **Placebo P2 (solo R1 e B1-B3)**: stessa regola applicata martedì-venerdì (ognuno col proprio open cash) → differenza lunedì − altri giorni, t raggruppato. Risponde al «punto da confermare» del PDF.

## 7. Soglie (fissate ora)

**Scoperta, per cella** (feed d'inferenza, costi base):
- 🟢 **VERDE** se **tutte**: media netta > 0 con **t ≥ 2,0** (A3: 2,5); placebo P1 superato **dopo** Benjamini-Hochberg; media netta > 0 **anche sotto stress**; `n ≥ (2σ/μ)²`; media > 0 anche sul feed di concordanza (FTMO) nel periodo comune; ≥ 60% degli anni con media > 0; costo base ≤ 12,5% di R.
- 🟡 **GIALLO**: come verde ma 1,0 ≤ t < 2,0, oppure placebo superato solo prima della correzione (p < 0,10) → avanza **solo con il tuo via esplicito**.
- 🔴 **ROSSO**: tutto il resto → cella scartata. **Tutte le celle A rosse → strategia bocciata**, rapporto e stop.

**Validazione 2024** (celle verdi/gialle): 🟢 media netta > 0 su entrambi i feed e > placebo; 🟡 > 0 su un feed; 🔴 ≤ 0 su entrambi → niente hold-out.

**Hold-out 2025 → fine** (una sola apertura, regole congelate): 🟢 media netta > 0 su entrambi i feed e scarto dalla scoperta entro 2 errori standard; 🔴 ≤ 0 su entrambi.

**Potenza attesa** [STIMA dai numeri del video, σ ≈ 1,3 R]: R1 ≈ 30 trade/anno → ~195 in scoperta → visibile solo se μ ≥ ~0,19 R; R2 ≈ 150/anno → ~1.000 → visibile se μ ≥ ~0,08 R. **La R1 da sola rischia il giallo per mancanza di potenza**, non per assenza di edge: lo dico ora.

## 8. Robustezza (solo per celle verdi, riportata tutta)

Soglie RSI ± 2 e ± 5 · multipli dello stop ± 0,5 ATR (target sempre 2× stop) · uscita 12/24/36 ore · periodi RSI/ATR 10/14/20 · ingresso ritardato di 1, 5, 15 minuti · RSI di Cutler al posto di Wilder · rientro R2 solo dopo che l'RSI è tornato sopra 35 · risultati **per anno** (2025-26 a parte) · senza il 2020 · distribuzione dei R (asimmetria, quota dei 20 trade migliori), mix d'uscita (SL/TP/tempo/weekend), serie di perdite consecutive. **Si sceglie l'altopiano, mai il picco.**

## 9. Doppio controllo

Ogni numero da codice; un secondo script **indipendente** ricalcola trade per trade la cella primaria (A1, A5) con logica scritta da capo; deve coincidere su ingressi, uscite e R.

## 10. Cosa NON faccio fino al tuo via
Nessun backtest, nessun numero di rendimento, nessuna apertura di 2024-2026 per la strategia.

## 11. Decisioni che servono da te
1. **Feed d'inferenza**: Pepperstone per l'inferenza, FTMO per concordanza e costi (§2)? 
2. **Uscita primaria**: 24 ore (parole del video) — A2 e A3 come varianti?
3. **«Molto sotto la media»**: griglia k = 2/3/4 ATR, primaria k = 3?
4. **Barre cash** come primarie (A9-A10 su barre CFD come varianti)?
5. **Swap**: mi esporti la specifica di `UK100.cash` (swap long/short, giorno del triplo, commissione, contract size, sessioni)? Fino ad allora uso −0,5 / −2,0 punti/notte.
6. **File mancanti** (§1 del rapporto F0): GUIDA + script di audit originali, sorgenti dei 6 EA, trade degli EA (per G6), `specifiche_simboli.csv`.
