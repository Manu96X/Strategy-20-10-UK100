# SPECIFICA DELLA STRATEGIA CANDIDATA «FTSE 100 — Monday dip + RSI»
*20/10/2026 · ricavata da `Nuova strategia FTSE 100.pdf`, dalle 31 immagini `Spiegazione strategia (n).jpeg` (reel Instagram di quant_labde, «Try this UK100 strategy for the next 21 days…») e dai 6 papers `ssrn-*.pdf`. **Nessun backtest eseguito**: qui c'è solo cosa dice la fonte, cosa ne deduco e cosa resta da decidere.*

Etichette: [VIDEO] letto nelle immagini · [PDF] dal tuo documento · [BACKTEST] calcolato da noi sui dati (solo F0: volatilità e spread) · [PAPER] dai papers · [STIMA] mia deduzione, con metodo.

---

## 1. Cosa dice la fonte

| Elemento | Contenuto | Fonte |
|---|---|---|
| Strumento | FTSE 100 («Two rules · one index») | [VIDEO] img 2, 4 |
| Timeframe | candele **H1**: media «40-hour average» = media mobile a 40 barre orarie | [VIDEO] img 11-13 |
| Indicatori | **RSI 14** (etichetta «RSI 14» sul grafico), **MA 40**, **ATR** (periodo non indicato) | [VIDEO] img 6, 19, 13 |
| **Regola 1** «Monday dip» | **solo il lunedì**; indice debole = prezzo **sotto l'apertura del lunedì** (linea tratteggiata all'open della prima candela del lunedì) **e RSI 14 < 40** → **BUY** alla chiusura della candela | [VIDEO] img 3, 5-7, 9 · [PDF] |
| Stop / target R1 | stop **2,5 ATR**; target «twice your risk» = **5 ATR** | [VIDEO] img 8, 14 · [PDF] |
| **Regola 2** | prezzo **molto sotto la media a 40 ore** e **RSI 14 < 35** → **BUY** | [VIDEO] img 12, 13, 19, 15 · [PDF] |
| Stop / target R2 | stop **2 ATR**; «same target» = 2× rischio = **4 ATR** | [VIDEO] img 16, 17 · [PDF] |
| Uscita a tempo | **«Out after 24 hours, always»** (R1); «same target, **same limit**» (R2) | [VIDEO] img 10, 17 |
| Gestione | no griglia, no martingala | [VIDEO] img 18 |
| Risultati dichiarati | **+312,9%** a **0,75%** di rischio per trade, drawdown massimo **12%**, win rate **50,8%**, **1.908 trade dal 2017**; nessuna parola su costi, spread, dati usati | [VIDEO] img 20-24, 30 |
| Monday dip altrove | «shows up on the DAX, S&P 500 and Nasdaq»; profilo medio settimanale: calo il lunedì, salita fino al venerdì | [VIDEO] img 25-27 |
| Terzo setup | citato, non spiegato → **escluso** | [PDF] |

### 1.1 Differenze fra PDF e video
1. **Uscita**: PDF = chiusura **lunedì sera prima delle 23:00 italiane** se né stop né target; video = **dopo 24 ore, sempre**, per entrambe le regole.
2. **R2 senza limite di tempo** nel PDF; nel video «same limit» (24 ore).
3. «Indice debole – in trend ribassista» (PDF) = nel video è solo **prezzo sotto l'apertura del lunedì**: nessun altro filtro di trend visibile.

---

## 2. Cosa ne deduco [STIMA]

1. **Le barre H1 del video sono della sola sessione cash di Londra (08:00-16:30, 9 barre al giorno)**, non del CFD 24 ore. Due prove indipendenti:
   - il venerdì nel grafico ha ~9 candele, non ~23 (img 5, 9);
   - l'ATR implicito nelle immagini è **≈ 22 punti** (stop 2,5 ATR ≈ 55 punti a img 8; stop 2 ATR ≈ 43 punti a img 16) e la mediana dell'**ATR 14 H1 sulla sessione cash** di UK100 nel 2023-2025 è **21,6-22,6 punti**, mentre sulle barre H1 CFD 24 ore è **14,5-16,5** [BACKTEST, `lavoro/f0/RAPPORTO_F0.md` §6].
2. **«Apertura del lunedì» = apertura cash delle 08:00 di Londra** (10:00 server; 11:00 nelle settimane disallineate di marzo e ottobre-novembre).
3. **«24 ore» è ambiguo**: le parole dicono 24 ore; il riquadro grafico di img 10 copre **24 candele**, che su barre cash sono **≈ 2,7 sedute**. Vanno testate entrambe, più l'uscita serale del PDF.
4. **«Molto sotto la media» non è quantificato.** Nelle immagini la distanza al momento del BUY è **3,3-4,4 ATR** (img 13: 71 punti; img 15: ~95 punti; ATR ≈ 22). Proposta: distanza misurata in ATR, griglia k = 2 / 3 / 4.
5. **Numeri dichiarati**: 1.908 trade in ~8,5-9 anni ≈ **210-225 l'anno**. La R1 non può superare ~50 l'anno (un lunedì a settimana) → la R2 ne fa ~160-175: la soglia «molto lontano» non è estrema, oppure la R2 rientra più volte nello stesso episodio. +312,9% a 0,75% = **+0,10 R/trade** se composto (ln 4,129 / 1.908 / 0,0075) o **+0,22 R/trade** se semplice (417 R / 1.908); drawdown 12% = **16 R**. Sono numeri **lordi** e non verificabili.
6. **Il drift da solo non basta a spiegarli**: FTSE ≈ +3%/anno di prezzo ≈ 1 punto al giorno ≈ **0,02 R per giorno di detenzione** con stop ~45-55 punti.

---

## 3. Cosa insegnano i 6 papers (e cosa no)

| Paper | Cosa serve a noi |
|---|---|
| Panigrahi, Vachhani, Chaudhury 2021 (ssrn-3986000) | **formula di Wilder**: prime medie semplici su 14 periodi, poi `AG = (AG_prec×13 + guadagno)/14` (idem perdite), RSI = 100 − 100/(1+AG/AL). Strategie 50-50 e **60-40**: RSI < 40 = **inizio di un trend ribassista** (lettura di tendenza, non di ipervenduto). Nessun costo, test descrittivo su NIFTY settimanale |
| Hill 2019 (ssrn-3412429) | RSI 14 di Wilder (appendice numerica: verificata, 2,37×13+6,02 → 2,63). **RSI < 30 solo il 3,5% del tempo** (azioni S&P 500, giornaliero); in tendenza rialzista l'RSI resta **sopra 40**: scendere sotto 40 = perdita di consistenza del trend. I segnali rialzisti funzionano meglio **anche per il drift** dell'indice. «Commissions and slippage are not considered» |
| Hanna 2024 (ssrn-4808230) | **RSI corti (2-4) giornalieri dell'S&P 500**: ipervenduto → rendimento positivo il giorno dopo; edge **più affidabile sopra la media a 200 giorni, più ampio sotto**. È la letteratura più vicina alla R2 (rimbalzo a 1-3 giorni dopo un eccesso) |
| Requejo (ssrn-4708400, dati 1996-2022 + paper trading 2023) | mean reversion con TSI + RSI su SPY/QQQ, holding medio 5 giorni: **regole non pubblicate → non replicabile** |
| Knowles 2015 (ssrn-2670343) | RSI a 12 mesi per allocazione fra asset: mostra la variante a **medie semplici** (Cutler), diversa da quella di Wilder. Non pertinente all'orizzonte orario |
| Broadfoot, Leveau 2022 (ssrn-4438260) | guida al trend following (RSI a 60 giorni, MACD, filtri): contesto, non pertinente |

**Conseguenze pratiche**
1. **RSI = Wilder (RSI 14 con media di Wilder)**, come `iRSI` di MT5 e `ta.rsi` di TradingView. Il seme iniziale conta solo nel riscaldamento: dopo **300 barre** la differenza fra implementazioni è < 1e-8 [BACKTEST, controllo F0] → l'EA e il Python devono avere ≥ 300 barre di storia prima del primo segnale.
2. **RSI 14 < 40 non è un estremo**: è «debolezza». Il filtro della R1 è poco selettivo; l'informazione vera, se c'è, sta nel lunedì e nella distanza dalla media (R2).
3. **I papers non provano l'edge di questa strategia**: dati giornalieri, azioni o ETF USA, **senza costi**, nessuno sul FTSE né su barre orarie. Danno la formula e un'ipotesi di meccanismo (rimbalzo a 1-3 giorni), non la prova.
4. Il bias rialzista degli indici gonfia ogni segnale «compra»: serve un **placebo** (ingressi long casuali con le stesse uscite) che tolga il drift.

---

## 4. Meccanismo dichiarato (ipotesi falsificabili)

- **R2 — rimbalzo dopo vendite forzate**: un calo rapido e ampio (molti ATR sotto la media di 40 ore) è spesso de-risking, stop e richieste di margine, non informazione; chi compra fornisce liquidità ed è pagato con un rimbalzo a 1-3 giorni, più il premio azionario. **Previsioni**: batte il placebo; il rendimento **cresce con la distanza** (k = 2 → 3 → 4); funziona fuori dall'orario d'ingresso scelto (± 1 barra).
- **R1 — Monday dip**: notizie del weekend e riduzione del rischio all'apertura del lunedì; la pressione si esaurisce entro 1-2 giorni. **Previsioni**: lo stesso segnale negli altri giorni (martedì-venerdì) rende **meno**; il fenomeno si vede anche su DAX, S&P 500 e Nasdaq (affermazione del video).

---

## 5. Regole formali proposte (versione «fedele»)

| Voce | Definizione |
|---|---|
| Simbolo | `UK100.cash` FTMO (feed di prova: anche Pepperstone UK100) |
| Barre del segnale | H1 della **sessione cash di Londra 08:00-16:30** (ultima barra 16:00-16:30), costruite dagli M1; ora server = New York + 7 [verificato in F0] → 10:00-18:30 server (11:00-19:30 nelle settimane disallineate) |
| Indicatori | RSI 14 Wilder, ATR 14 Wilder, SMA 40 delle chiusure, tutti sulle barre cash **chiuse**; riscaldamento ≥ 300 barre |
| R1 | lunedì; a ogni chiusura di barra cash: `close < apertura cash del lunedì` **e** `RSI14 < 40` → BUY; **un solo trade per lunedì** (primo segnale); lunedì festivo = niente R1 |
| R2 | qualunque giorno; a ogni chiusura di barra cash: `close ≤ SMA40 − k·ATR14` **e** `RSI14 < 35` → BUY; una sola posizione R2 aperta alla volta; dopo l'uscita si rientra alla prima barra successiva in cui la condizione è vera |
| Ingresso | al primo M1 dopo la chiusura della barra segnale, a mercato (ask) |
| Stop / target | R1: SL = fill − 2,5·ATR, TP = fill + 5·ATR · R2: SL = fill − 2·ATR, TP = fill + 4·ATR · **sul server, riancorati al fill** |
| Uscita a tempo | 24 ore (variante 24 barre cash; variante PDF stessa sera) |
| Weekend e festivi | **chiusura prima del weekend e dei giorni di chiusura** (conto Standard FTMO e niente gap); niente ingressi nelle 2 ore prima di una chiusura ≥ 2 ore |
| R1 e R2 insieme | regole indipendenti: fino a 2 posizioni aperte |

---

## 6. Vincoli del prompt

- **Non ORB, non intraday momentum**: è un acquisto in debolezza con tenuta fino a 24 ore o più. ✔
- **Non simile ai tuoi 6 EA** (dalla descrizione del prompt; i sorgenti non sono nella repository): strumento diverso (UK100), logica opposta alla prosecuzione (compra la debolezza). ✔ — da riverificare sui sorgenti.
- ⚠️ **Vicina a famiglie già bocciate**: «mean reversion intraday su indici CFD» (240 combinazioni) e «RSI(2)». Differenze: tenuta **overnight fino a 1-3 giorni** (non intraday), strumento **UK100 mai testato**, distanza da una media oraria. La **variante PDF (uscita la sera stessa) È intraday mean reversion** → nel protocollo ha una soglia più severa. L'unico sopravvissuto delle tue ricerche (pullback **giornaliero** GER40, RSI2 < 10: +0,21 R, t 2,6) è dello stesso tipo di orizzonte della R2: indizio a favore, non prova.
- **Regole FTMO**: posizioni overnight (lecite in challenge; Standard funded: chiudere prima del weekend — già nelle regole); notizie: su Standard funded uno SL/TP eseguito entro ±2 minuti da una notizia selezionata è violazione → conto Swing o filtro; **swap long di UK100.cash ignoto** (manca la specifica).
- **Indipendenza G6**: non calcolabile finché mancano i trade dei tuoi EA.
