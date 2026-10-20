# DOSSIER FTMO — COSA ABBIAMO IMPARATO DAL VIVO
### Pacchetto d'ingresso per una chat che sviluppa una nuova strategia da portare su FTMO (MetaTrader 5)
### Fonte: forward test di due Expert Advisor su 4 conti demo FTMO Free Trial (21/08 → 02/10/2026, 30 sedute), misure dal vivo precedenti dal 04/08, backtest 2021-2026 e ricerche del progetto · **Revisione 3.1 del 06/10/2026** *(vedi in fondo cosa cambia)*

> ### COSA TROVI QUI
> Tutto ciò che il nostro progetto ha **misurato dal vivo** o **verificato** e che decide se una strategia nuova sopravvive su FTMO: **costi reali di esecuzione**, **regole FTMO per come funzionano davvero** (comprese quelle viste solo dal vivo), **trappole della piattaforma** che nessun backtest mostra, **infrastruttura**, **metodo statistico**, **idee già testate e scartate** e una **checklist di validazione o scarto** (§11).
> **Da dove viene**: due EA in forward su FTMO — un **breakout di apertura** su `US100.cash` M5 (*ORB*) e un **intraday momentum** su NASDAQ 100 M1 (*IM*) — più cinque anni di backtest su dati FTMO e uno studio esterno indipendente. Sullo stesso terminale gira anche un EA sull'oro **in dry run**, i cui dati di simbolo sono al §2.4.
> **Etichette di affidabilità**, usate ovunque:
> **[MISURATO]** letto da log e report reali del conto FTMO · **[BACKTEST]** calcolato sulle nostre serie 2021-2026 · **[REGOLA FTMO]** verificata su ftmo.com il 26/09/2026 · **[STUDIO ESTERNO]** lavoro di una chat indipendente, verificato dal progetto · **[STIMA]** derivato, con metodo dichiarato.
>
> **Se hai cinque minuti: §1 (le regole d'oro) e §11 (la checklist).** Per i costi nel dettaglio c'è il documento gemello `COSTI_ESECUZIONE_REALI_FTMO_US100` (rev 5.1, md5 `6e361905d7fe8d1bf4de4f53506b16cd`), e i dati grezzi, trade per trade, sono in `ESECUZIONI_REALI_FTMO_US100_TRADE.csv` (md5 `24346a19fb9a7a8d0ad0b185150d772a`).

---

## 0. ISTRUZIONI PER LA CHAT CHE RICEVE QUESTO DOCUMENTO

1. **I numeri di costo vengono da UN simbolo (`US100.cash`) e da UN server (`FTMO-Demo`).** Le regole, le trappole e il metodo valgono ovunque; i numeri di spread e slippage vanno ri-misurati su ogni simbolo nuovo (per l'oro abbiamo solo commissioni, istantanee di spread e la specifica dello swap, §2.4).
2. **Applica la checklist del §11** a ogni strategia e dichiara quali voci passano e quali no. Una strategia che non passa il cancello dei costi (G1) non va oltre, per quanto bello sia il backtest.
3. **Non rifare ciò che è al §8** senza un motivo nuovo e forte: sono mesi di lavoro già spesi, con esito negativo documentato.
4. **Non giudicare una strategia dal P&L di poche settimane**, né nostro né tuo (§7.3): il nostro forward è passato dal 2° al 53° percentile in quattro sedute, e ha chiuso a 30 sedute al 36°.
5. **Fissa i criteri di decisione prima di vedere i numeri**, e non cambiarli dopo. È la regola di metodo che il nostro progetto considera la più importante.
6. **Se ti servono numeri che qui non ci sono, ricalcolali dal CSV** dei trade: 33 righe, una per trade, con fill, slippage, uscite, P&L, R e tempi d'esecuzione, riconciliate al centesimo con i Report Cronistorici.

### 0.1 Glossario minimo
- **R**: l'unità di rischio del trade. Per il breakout è la perdita prevista allo stop (distanza dello stop × lotti × valore del punto), e un risultato in R non dipende dalla taglia della posizione. Per il momentum **1R = 500 $ nominali** (lotti = 500 $ ÷ distanza dalla banda, salvo un tetto al nozionale che a volte li riduce) e lo stop protettivo sta a −2R.
- **Fill**: prezzo realmente eseguito. **Slippage**: differenza fra fill e prezzo richiesto; qui sempre con **`+` = sfavorevole**.
- **Uscita a livello**: chiusura eseguita dal server su stop loss o take profit. **Uscita a mercato**: ordine di chiusura inviato dall'EA (a orario, su segnale, dopo un riavvio).
- **Riancorare**: spostare stop e target subito dopo il fill, perché la distanza dal prezzo eseguito sia esattamente quella voluta.
- **Seduta**: un giorno di apertura della borsa USA. **Ora server**: l'ora del server FTMO (§4). **Catch-all**: chiusura automatica di una posizione rimasta aperta dal giorno prima.
- **Fase 1 / fase 2**: le due tappe della challenge 2-Step. **Funded**: il conto finanziato (*FTMO Account*). **Standard / Swing**: i due tipi di conto FTMO; cambiano la leva e i vincoli su news e weekend (§3.2).
- **Freno giornaliero / totale**: blocchi interni dei nostri EA, più stretti dei limiti FTMO, che fermano il trading prima di violarli.
- **Report Cronistorico** (o cronistoria): il report della cronologia di MetaTrader 5, con prezzi eseguiti, commissioni e swap. È la fonte di verità dei costi.

---

## 1. LE DICIASSETTE REGOLE D'ORO

1. **Usa lo spread di OGGI, non la media storica.** Su `US100.cash` all'apertura USA la mediana è passata da **0,60 punti nel 2021 a 1,45 nel 2026**: lo spread di oggi è **1,4 volte la media 2021-2026** (1,02) e **2,4 volte quello del 2021**. Un backtest pluriennale con lo spread medio sottostima il costo attuale di circa il **30%**; uno tarato sul 2021, di circa il **60%**. **Anche in orario USA le letture dal vivo danno 1,45**, non lo 0,80 della mediana storica. [MISURATO][BACKTEST]
2. **Le commissioni dipendono dal simbolo.** `US100.cash` **0,00** (33 trade su 33, anche sul conto Swing); **FX 2,50 $ per lotto per lato**; **oro 3,00 $ per lotto per lato**. [MISURATO]
3. **Lo slippage d'ingresso a mercato è rumore, non costo**: media **−0,02 punti**, deviazione standard **2,22** su **35** ordini, 17 sfavorevoli e 17 favorevoli, estremi −6,50 e +5,71. Non sposta la media ma **sposta il rischio** (da 0,81× a 1,13× del voluto nei casi estremi): si neutralizza **riancorando stop e target al prezzo eseguito**. [MISURATO]
4. **Lo slippage sugli stop del server è un costo sistematico**: in media **+0,59 punti sul breakout** (+1,5% di uno stop da 40 punti, 15 casi su 19 sfavorevoli) e **≈0,8 punti su tutti i 22 stop** osservati; peggiori **+6,85%** della distanza (2,58 punti) e **+5,51 punti** (28/09, in un movimento rapido **senza notizie in calendario**). Il backtest ne prevede rari casi oltre il 20%. In un backtest MT5 su tick reali **è già dentro** (regola 7). Sui target del server non abbiamo misure: uno solo colpito dal vivo, senza rilevare lo slippage. [MISURATO][BACKTEST]
5. **Le uscite a mercato non pagano lo slippage di attraversamento** (il loro slippage d'esecuzione non è misurabile dai log: lo assumiamo come quello d'ingresso, media ≈0). Il costo di una strategia dipende dal suo **mix di uscite**, contato sul backtest e non su poche settimane: dal vivo, in due settimane consecutive, le uscite a livello sono state **0 su 7** e poi **5 su 6**. [MISURATO][STIMA]
6. **Costo in R = costo in punti ÷ distanza dello stop.** 1,45 punti di spread pesano 0,036 R su uno stop da 40 punti e **0,097 R su uno da 15**; uno slittamento sullo stop come quello del 28/09 (+5,51) ne pesa 0,14 e **0,37**. Regola pratica (è il filtro costi del nostro momentum): `distanza ≥ 8 × (spread + 2 × 1,0)`, dove 1,0 è uno slippage prudente di 1 punto per lato → costo ≤ 12,5% di R; con lo spread di oggi, distanza ≥ 27,6 punti. [BACKTEST][MISURATO]
7. **Non sottrarre i costi due volte.** Se la lista trade viene da prezzi reali o da un backtest MT5 su tick reali, spread storico e attraversamento degli stop sono già dentro: **controlla la perdita media agli stop in R** (§2.2). Da noi: backtest −1,0225 R, dal vivo −1,0181 R su 15 stop. [MISURATO][BACKTEST]
8. **Il tester MT5 non modella lo slippage degli ordini a mercato** (0,00 su 39 ordini), **e su FTMO `CTrade::ResultPrice()` restituisce il prezzo richiesto, non quello eseguito.** Lo slippage si misura con `POSITION_PRICE_OPEN` o con il Report Cronistorico. [MISURATO]
9. **I limiti FTMO si verificano sull'equity intragiornaliera**, non sul P&L di chiusura: il minimo intraday è in media **1,39 volte peggiore** della chiusura nei giorni negativi. [STUDIO ESTERNO]
10. **Una challenge è un problema a barriere dominato dalla varianza**, non dalla media: contano la dispersione e le **sequenze di perdite** più dell'edge medio. Sul funded vale il contrario. [BACKTEST]
11. **Il P&L di poche settimane non misura l'edge.** Un forward serve a verificare la **meccanica** (ordini, uscite, riavvii, costi), non a stabilire se la strategia guadagna. Il nostro, a 30 sedute, ha chiuso a **−1.150 $**: **36° percentile** con l'edge storico intatto e **verosimiglianza 1:1** fra «edge intatto» ed «edge nullo» — cioè nessuna informazione sull'edge, esattamente come previsto. [MISURATO][STIMA]
12. **Monte Carlo con bootstrap per GIORNATA INTERA**, mai per singolo trade: il secondo cancella le correlazioni e produce certezze false (ci è successo: LR 14,7:1 invece di 2,19:1). [STIMA]
13. **Tutto ciò che può stare sul server deve starci.** Stop e target sul server funzionano a terminale spento; le uscite a orario e a segnale no. **Le tre notti con posizioni aperte del nostro forward sono state tutte causate dal PC spento**, e il **02/10 il terminale spento ha fatto perdere un'intera seduta** → VPS. [MISURATO]
14. **Un EA deve leggere i codici di errore e non ritentare all'infinito.** FTMO vieta come iperattività **più di 2.000 richieste al server al giorno**; un nostro EA ne ha generate **~3.000 in 5 minuti**. [MISURATO][REGOLA FTMO]
15. **Il Free Trial FTMO NON è la challenge**: target **5%** invece di 10%, **2** giorni minimi invece di 4, durata **14 giorni**. E dal vivo **si è chiuso da solo al raggiungimento degli obiettivi**, tre giorni prima della scadenza (FTMO non lo scrive: è un'inferenza dai log). Esiste anche in versione **Swing** (leva 1:30). Passare il Free Trial non prova niente. [REGOLA FTMO][MISURATO]
16. **Sul conto finanziato Standard** le posizioni vanno chiuse prima del weekend, e **uno stop o un target eseguito entro ±2 minuti da una notizia selezionata da FTMO è una violazione**. Durante la challenge nessuno dei due vincoli vale. [REGOLA FTMO]
17. **Leva e margine dipendono dal tipo di conto.** Standard: leva di conto **1:100**, e `US100.cash` a margine **2,00% del nozionale (1:50)**, misurato. Swing: leva di conto **1:30**, margine degli indici non misurato. Prima di dimensionare una strategia con nozionali grandi: `ACCOUNT_LEVERAGE` e `OrderCalcMargin()` sul conto vero. [MISURATO]

---

## 2. COSTI REALI DI ESECUZIONE — `US100.cash` su FTMO

### 2.1 La tabella dei costi *(stop medio di riferimento: 40,47 punti, media dei 19 trade del breakout con riancoraggio)*

| Voce | Valore | In R (stop 40,47) | Quando si paga | Fonte |
|---|---|---|---|---|
| **Spread** | **1,45 punti** alle 16:35 server, 23 ingressi su 23 | **0,036 R** | **una volta** per round-trip | [MISURATO] |
| **Slippage d'ingresso** (ordine a mercato) | media **−0,02**, dev.st **2,22**, IC95% [−0,78 ; +0,74], n=35 | **≈ 0** in media | sempre, come **varianza** | [MISURATO] |
| **Slippage sugli stop del server** | breakout: media **+1,51%** della distanza = **+0,59 punti** (n=19, stop da 36 a 59 punti), range −1,65% … +6,85% · tutti i 22 stop: **≈0,8 punti**, mediana 0,6, peggiore **5,51** | **0,015 R** *(0,020 R con 0,8 punti)* | **solo** sulle uscite a livello | [MISURATO] |
| … coda | breakout: 1 caso su 19 oltre il 5%; il backtest ne prevede il 9,4% (p99 16,8%) e **3 su 778 oltre il 20%**, il peggiore al **63%** · momentum: un caso da 5,51 punti | di solito **0,05-0,17 R**; oltre 0,20 R in 3 casi su 778 (massimo **0,63 R**) | circa 1 stop su 10 | [BACKTEST][MISURATO] |
| **Target (TP) del server** | dal vivo uno solo (04/08, eseguito a terminale spento), slippage non rilevato; nel tester su tick reali eseguito al livello o **meglio** (+8,019 R medio su 72 target da 8R, mai peggio) | ≈ 0 | uscite al target | [MISURATO][BACKTEST] |
| **Uscita a mercato** | nessuno slippage di attraversamento; quello d'esecuzione non è misurabile dai log, si assume come all'ingresso | ≈ 0 oltre lo spread | uscite a orario/segnale | [STIMA] |
| **Commissioni** | **0,00** su tutti i 33 trade | 0 | mai (solo su questo simbolo) | [MISURATO] |
| **Swap** | ≤ 0,28 $ per lotto per notte, **segno variabile** | trascurabile | solo overnight | [MISURATO] |

**Conferma che il backtest rappresentava bene lo stop**: nel backtest la perdita media agli stop è **−1,0225 R** (cioè +2,25% di slippage già incorporato); dal vivo, su 15 stop con riancoraggio, **−1,0181 R**. Coincidono entro mezzo punto percentuale (il backtest è appena più prudente). [MISURATO][BACKTEST]

### 2.2 Ricetta per applicare i costi a una strategia nuova

**Primo passo, sempre: capire che cosa il backtest contiene già.** Guarda la **perdita media delle uscite allo stop, espressa in R**:
- se è **esattamente la perdita nominale** (−1,000 R), il backtest esegue gli stop esattamente al livello → l'attraversamento **non** è dentro;
- se è **peggiore** (il nostro backtest MT5 su tick reali: **−1,0225 R**), l'attraversamento è **già dentro**, alla granularità del tick — e dal vivo abbiamo misurato −1,0181 R, cioè la stessa cosa;
- in un **backtest a barre** l'attraversamento può essere dentro in misura da verificare: nella serie del nostro momentum (742 trade: la serie del backtest in Python su barre M1, non quella del tester MT5, che ne ha 633) gli stop protettivi sotto −2R sono 106 su 116 e valgono in media **−2,081 R**, cioè circa **+4%** della distanza (gli altri 10 hanno taglia ridotta dal tetto al nozionale); dal vivo i tre stop protettivi valgono in media **−2,051 R** (+0,18%, +0,73% e +6,15%). **Con tre casi non si può dire se il backtest a barre sovrastimi o sottostimi.** [BACKTEST][MISURATO]

| Tipo di backtest | Da aggiungere (in R per trade) |
|---|---|
| **A — Tester MT5, «Ogni tick basato su tick reali»**, dati FTMO | `Δspread / d` (spread di oggi **meno** quello storico già dentro) + commissioni + swap. Ordini a mercato (ingressi e uscite a mercato): media 0, **stress +0,5 punti per ordine**. **Niente** slippage a livello: c'è già (verificalo con la regola sopra) |
| **B — Backtest che esegue gli stop esattamente al livello** (perdita media agli stop = nominale) | spread **intero** una volta per round-trip `/ d` + `f_livello × s_livello` + commissioni + swap. Ordini a mercato: media 0, stress +0,5 punti per ordine |

- `d` = distanza dello stop in punti. `f_livello` = frazione di uscite **allo stop** del server **nel backtest** (i target, per prudenza, contali come gli stop: dal vivo non li abbiamo misurati). `s_livello` = slippage medio sullo stop **in punti** diviso per `d`: su `US100.cash` **≈0,8 punti** (media dei 22 stop dal vivo: 0,59 sui 19 del breakout, 2,12 sui 3 del momentum per via del caso da 5,51; mediana 0,61; nel backtest su tick reali 2,25% di uno stop medio di ~30 punti ≈0,7), cioè **2,0% di uno stop da 40 punti ma 5,3% di uno da 15**. Lo slippage dipende dalla velocità del mercato quando attraversa il livello, non dalla distanza: ragiona in punti e ri-misuralo su ogni simbolo. **Stress: × 2,5** (≈2 punti); il caso peggiore osservato è 5,51. [MISURATO][STIMA]
- Se lo stop **non** viene riancorato al fill, lo slippage d'ingresso aggiunge varianza al rischio: circa ±6% per trade a una deviazione standard su uno stop da 40 punti; nei casi estremi 0,81×-1,13×.
- **Due esempi estremi, stesso broker e stesso strumento**: breakout con l'**80,3%** di uscite allo stop (più il 7,4% al target) → paga quasi sempre l'attraversamento; momentum con il **15,6%** → quasi mai. [BACKTEST]
- **Esempio svolto — il nostro breakout (tipo A)**: stop a −1,0225 R → attraversamento già dentro; spread di oggi (1,45) contro quello storico del backtest → **−0,0144 R/trade**; slippage d'ingresso **−0,0089 R** (stima prudente del 30/08 su 9 ordini: oggi, su 35, la media è ≈0); commissioni e swap 0 → costo residuo **−0,0233 R**, edge netto **+0,155 R/trade** contro +0,178 lordo. [BACKTEST][STIMA]

### 2.3 Lo spread dipende dall'ora e dall'anno

| Momento (ora server) | Spread `US100.cash` | Fonte |
|---|---|---|
| **16:35** (5 minuti dopo l'apertura cassa USA) | **1,45** · storico 2021-26: mediana 1,00, max 1,79, mai sopra 2,0 | [MISURATO][BACKTEST] |
| Orario USA, 17:00 → 22:30 | **1,45 in tutte le letture dal vivo** · storico 2021-26: mediana **0,80**, p95 1,45 → **per il 2026 usa 1,45** | [MISURATO] istantanee · [BACKTEST] · [STIMA] |
| Mattina europea e primo pomeriggio (10:50 → 15:15) | **1,25 – 1,95** | [MISURATO] |
| **Ora che precede l'apertura cassa** (15:29 → 16:11; dati macro delle 15:30) | **1,95 – 2,19** (3 letture) | [MISURATO] |
| Ultima ora di quotazione (23:12) | 1,53 | [MISURATO] |
| Notte e weekend | il terminale mostra 1,53: è **l'ultima quotazione congelata**, non uno spread negoziabile | [MISURATO] |

**Mediana per anno alle 16:35 server: 2021 0,60 · 2022 0,60 · 2023 1,00 · 2024 1,10 · 2025 1,20 · 2026 1,45.** [BACKTEST]

### 2.4 Altri simboli dello stesso conto: commissioni e primo profilo dell'oro [MISURATO salvo dove indicato]

| Simbolo | Commissione | Base della misura |
|---|---|---|
| `US100.cash` | **0,00** | tutti i 33 trade dal 17/08 |
| EURUSD, USDJPY | **2,50 $ per lotto per lato** (5,00 $ a round-trip) | 1 lotto e 0,1 lotti |
| XAUUSD | **3,00 $ per lotto per lato** (0,03 $ per 0,01 lotti) | 6 affari da 0,01 lotti, calcolo confermato da un nostro EA |

**Oro (`XAUUSD`)** — istantanee lette dal rapporto di avvio di un nostro EA in dry run (nessun ordine reale):
- **spread** in orario di contrattazione **0,35 – 0,51 $ per oncia**, mediana **0,405**, media 0,40 (20 istantanee, 28/09 → 06/10); 0,43 congelato nel weekend;
- **costo round-trip ≈46 $ per lotto** (spread 40 $ + commissioni 6 $) [STIMA];
- **swap** dalla specifica (in punti, 1 punto = 1 $ per lotto): **long da −64,90 a −90,35**, **short da −4,20 a −8,30** per lotto per notte — **a debito in entrambe le direzioni**, e cambia quasi ogni giorno nel pomeriggio [SPECIFICA DEL SIMBOLO; nessuna posizione overnight reale];
- contract size 100, 1,00 di prezzo = 100 $ per lotto, volume 0,01 – 100, stops level e freeze level 0, filling FOK/IOC;
- ATR(14) M15 fra 5,45 e 11,0 $ nelle istantanee → lo spread vale il 4-7% di un ATR M15;
- **`DXY.cash`** è disponibile su FTMO con storico M1, utile per filtri sul dollaro.

**Spread su FX e slippage su FX e oro non sono misurati.** Per una strategia su quei simboli vanno misurati da capo (§1 del documento gemello spiega come).

### 2.5 Swap su `US100.cash` [MISURATO]

| Notte | Direzione | $ per lotto per notte |
|---|---|---|
| lun→mar 24-25/08 | short | **+0,28** (a credito) |
| mar→mer 15-16/09 | short | **−0,07** (a debito) |
| mer→gio 23-24/09 | short (due posizioni) | **+0,127** (stesso tasso su entrambe) |

Piccolo e di **segno non prevedibile dalla direzione**. Mai misurato su long né sul weekend; il giorno dello swap triplo per questo simbolo non è verificato. Per una strategia overnight: leggere swap long/short e giorno del triplo nella **Specifica** del simbolo in MT5. *(Sull'oro lo swap è di un altro ordine di grandezza: §2.4.)*

### 2.6 Qualità d'esecuzione [MISURATO]

| Grandezza | Valore |
|---|---|
| Ingressi a mercato (n=33, tutti, dai journal) | mediana **236 ms**, 31 su 33 fra 195 e 364 ms; due casi alti (420 e 825 ms). **Dopo l'aggiornamento del terminale a build 6230 (28/09): mediana 311 ms su 6, contro 232 ms prima** |
| Uscite a mercato | mediana **214 ms** (n=11); **1.296 ms** sul primo ordine dopo la riapertura delle 01:05 |
| `PositionModify` | mediana 100 ms, 50 – 315 ms (n=28) |
| Ping dal PC di casa (Italia) | 29 – 76 ms · **VPS MetaTrader Londra: 1,3 – 1,8 ms** |
| Rifiuti **sul prezzo** (requote, off quotes) | **0** su 35 ingressi e 11 uscite a mercato |
| Deviation | **ignorata in entrambe le direzioni**: con deviation 5,0 sono passati senza requote un fill a −6,50 (a favore) e uno a **+5,71 (contro)**. È l'esecuzione *Market*. **Non contarci come protezione** |

---

## 3. REGOLE FTMO — come funzionano davvero

### 3.1 Challenge 2-Step (100k) [REGOLA FTMO]

| Regola | Valore | Dettaglio che conta |
|---|---|---|
| Target | **+10%** fase 1 · **+5%** fase 2 | vale col **bilancio** e **tutte le posizioni chiuse** |
| Perdita giornaliera massima | **5%** del capitale iniziale | ricalcolata alle **00:00 CE(S)T** sul **bilancio** di quel momento; l'**equity**, flottante compreso, non deve mai scendere sotto `bilancio delle 00:00 − 5.000` |
| Perdita massima | **10% statico** | l'equity non deve mai scendere sotto 90.000; non segue i massimi |
| Giorni minimi di trading | **4** | giorno = data CE(S)T in cui **si apre** almeno una posizione |
| Durata | **illimitata** | |
| Premio / rimborso | fino al 90% · quota rimborsata al primo payout | quota della 100k: **540 €** |
| News e weekend | **liberi** durante la valutazione | |

**Conseguenze di disegno**: la perdita giornaliera **include il flottante** → conta l'escursione avversa intraday, non la chiusura; il massimo statico rende prezioso il **cuscinetto** costruito all'inizio; il target chiede posizioni chiuse → un blocco al target va progettato con **margine** (un blocco sull'equity senza margine chiude a mercato e può realizzare **sotto** il target: in un nostro test si è chiuso a soli 78,77 $ sopra, per fortuna del tick).

### 3.2 Conto finanziato (FTMO Account) [REGOLA FTMO]
- **Standard**: posizioni da chiudere **prima del weekend** o se la pausa di rollover supera le 2 ore; **news**: vietato aprire o chiudere — **incluse le esecuzioni di stop e target** — da **2 minuti prima a 2 minuti dopo** le notizie selezionate da FTMO. Violazione → possibile chiusura del conto.
- **Swing**: nessuno dei due vincoli. **Leva più bassa**: dal vivo il conto Swing aveva leva di conto **1:30** contro **1:100** dello Standard. [MISURATO]
- **Costi a confronto** [MISURATO]: su un Free Trial **Swing** (FTMO-Demo, 28/09 → 02/10) i costi d'esecuzione su `US100.cash` sono risultati **identici** a quelli dei conti Standard — spread 1,45 su 4 ingressi su 4, commissioni 0,00 su 6 trade. Campione minimo, ma nessun segnale di differenza.
- **Conseguenza**: una strategia intraday con stop sul server attivo alle **10:00 di New York** (17:00 server, l'ora dei dati ISM, JOLTS, fiducia dei consumatori) su un conto Standard corre un rischio di violazione **che nessun backtest mostra**. Dal vivo [MISURATO]: **nessuno dei nostri 22 stop è caduto entro ±2 minuti da un dato USD ad alto impatto** del calendario MQL5 (il più vicino: 3,5 minuti prima), ma **due posizioni del breakout hanno attraversato un dato delle 10:00** (10/09 e 24/09). Il calendario di FTMO non coincide necessariamente con quello di MQL5. Valutare Swing (pagando la leva più bassa) o una gestione esplicita delle finestre news.

### 3.3 Free Trial [REGOLA FTMO][MISURATO]
- **14 giorni**, **uno alla volta** (si può cancellare e aprirne un altro). Esiste in versione **Standard** e **Swing** (il nostro quarto conto, aperto il 28/09, era un `$100k FTMO Free Trial Swing 2-Step`, leva 1:30).
- 2-Step trial: **una sola fase, target 5%, 2 giorni minimi**, per il resto gli obiettivi della challenge (perdita giornaliera 5%, massima 10%). 1-Step trial: obiettivi della 1-Step con target 5%.
- **Dal vivo**: il nostro terzo conto ha raggiunto il 5% il 24/09 alle 22:55 server con le posizioni chiuse; al collegamento successivo il journal mostrava `trading has been disabled - disabled on server`, **tre giorni prima della scadenza**. *(FTMO non lo scrive esplicitamente: è un'inferenza forte, coerente con quanto accade quando si supera una fase.)* Il quarto conto ha chiuso le cinque sedute del forward a −2,80%, lontano sia dal target sia dai limiti.
- **Al cambio conto MT5 disattiva da solo il trading automatico** (trappola T11): riabilitato a mano in 17-23 secondi entrambe le volte.
- **Conseguenze**: il Free Trial è un **banco di prova meccanico**, non una simulazione della challenge; una strategia che va bene **chiude il conto prima del tempo** (serve aprirne subito un altro); il server è `FTMO-Demo`, quello dei nostri numeri di costo.

### 3.4 Pratiche vietate rilevanti per un EA [REGOLA FTMO]
- **Iperattività**: EA che causano **più di 2.000 richieste al server al giorno** → da avvertimento fino a esclusione dalla valutazione o chiusura del conto.
- Limiti della piattaforma: **200 ordini aperti contemporaneamente** e **2.000 posizioni al giorno**.
- **Una richiesta rifiutata resta una richiesta al server** (se il terminale la inoltra, e il journal le registra una per una): un EA che ritenta a ogni tick dopo un rifiuto supera il limite in minuti (§5, trappole T17-T19). [STIMA]

### 3.5 Altre verifiche del progetto [STUDIO ESTERNO]
- **1-Step**: perdita massima **trailing** di fine giornata, giornaliera **3%**, **Best Day Rule**. Per una strategia a vincite rare e grandi (win rate 19%, payoff 8R), nel Monte Carlo dello studio esterno la probabilità di passare crolla a **~35%** contro **~95%** della 2-Step nelle stesse condizioni → scartata. *(Metrica dello studio, non confrontabile con le probabilità del §12.)*
- **Più conti in parallelo**: consentiti (fino a 400.000 $ di capitale finanziato, anche con la stessa strategia), ma conti identici sono **perfettamente correlati** e il costo dei VPS annulla il beneficio.
- **Scaling plan**: richiede ~10% di profitto in 4 mesi.

---

## 4. TEMPO E SESSIONI — dove si sbaglia senza accorgersene

| Fatto | Valore | Fonte |
|---|---|---|
| **Fuso del server FTMO** | **New York + 7 ore**, segue l'ora legale **americana** (non EET fisso) | [BACKTEST] profili di volume FTMO 2021-26 · [STUDIO ESTERNO] settimane di disallineamento 2024-25 su dati Pepperstone, stessa struttura |
| Apertura cassa USA | **16:30 server tutto l'anno**, anche nelle settimane di disallineamento fra ora legale USA ed europea | [BACKTEST] 89 giorni su 89 di disallineamento |
| Borse europee | nelle settimane di disallineamento **si spostano** (Xetra apre alle 11:00 server) → derivare gli orari da GMT + regole dell'exchange, **mai** da un'ora server fissa | [STUDIO ESTERNO] |
| **Giorno FTMO** (reset della perdita giornaliera) | 00:00 CE(S)T = **01:00 server**; **02:00 server** nelle settimane di disallineamento | [STIMA] dai due fusi; l'EA sull'oro lo calcola da sé e stampa «ore 01:00 server = 00:00 CE(S)T» [MISURATO] |
| **Orario di quotazione `US100.cash`** | **01:05 → 23:49 server**; pausa di **76 minuti**; riapertura delle 01:05 confermata dal vivo | [BACKTEST][MISURATO] |
| Mezze sedute USA | chiusura alle **19:59 server** (34 giorni in 5 anni) | [BACKTEST] |
| Festività insidiose | 07/04/2023, **09/01/2025**, 03/04/2026: quotazioni parziali fino alle 16:14-16:29 → senza calendario NYSE un EA **entra a borsa chiusa** | [BACKTEST] |
| **Calendario economico MQL5** | **disponibile e popolato** sul terminale FTMO: 64.986 eventi 2021-2026 esportati il 30/09 (22.171 in USD), datati in **ora server** (Non-Farm Payrolls 15:30, ISM 17:00) | [MISURATO] |
| Log di MT5 | Experts e Journal in **ora locale del PC**, Report Cronistorico in **ora server**; orologio del PC fino a ~1,6 s indietro rispetto al server | [MISURATO] |
| Nomi dei simboli FTMO | gli indici CFD in MT5 hanno il suffisso `.cash` (`US100.cash`, `DXY.cash`); le commodity `.c`. **FTMO non quota il VIX**: un filtro VIX va alimentato dall'esterno (§8) | [MISURATO] · lista ufficiale dei simboli sul sito FTMO, verificata il 29/08/2026 |
| **Dati FTMO** | l'export M1 contiene **D1 travestito da M1 fino al 21/01/2021** e **H1 fino al 13/09/2021**: M1 vero **solo dal 14/09/2021** | [BACKTEST] |

---

## 5. TRAPPOLE DI MT5 SU FTMO — nessuna è visibile in backtest

| # | Trappola | Rimedio |
|---|---|---|
| T1 | `TimeCurrent()` **non avanza senza tick**: una chiusura a orario su `OnTimer` non scatta | `TimeTradeServer()` |
| T2 | **Le variabili globali si azzerano a ogni reinizializzazione** (riavvio, cambio parametri, sincronizzazione VPS, cambio conto). Un catch-all ci ha chiuso a +2,60R un trade con target a 8R | rileggere lo stato dal server: `POSITION_TIME`, storico dei deal |
| T3 | `CTrade::ResultPrice()` su FTMO = **prezzo richiesto** → slippage sempre loggato a 0,00 | `POSITION_PRICE_OPEN` o `DEAL_PRICE` |
| T4 | **Dopo `OrderSend` la posizione può non essere ancora in cache** (1 caso su 5; 2 ingressi su 4 nell'ultima settimana): la lettura fallisce in silenzio | attesa attiva fino a 1 s (si risolve in 57-66 ms), con riga di allarme se fallisce |
| T5 | Stop calcolato sul prezzo richiesto → il rischio effettivo cambia con lo slippage d'ingresso: circa **±6%** a una deviazione standard su 40 punti, **0,81×-1,13×** nei casi estremi osservati, molto di più con stop stretti | **riancorare SL e TP al fill** |
| T6 | SL/TP sul server **vengono eseguiti a terminale spento**; le uscite a orario o a segnale **no** | tutto ciò che può, sul server |
| T7 | `PositionModify` con TP = 0 **cancella** il take profit | ripassare sempre il TP corrente |
| T8 | Una reinizializzazione dentro la finestra d'ingresso può aprire **un secondo trade** nello stesso giorno | stato «già operato» letto dallo storico, non dalla memoria |
| T9 | Il tester non è deterministico se non lo si forza | Ritardi = «Latenza zero, esecuzione ideale» per ogni confronto |
| T10 | Il nome del file non prova quale sorgente è compilato | stampare un **BUILD_ID nel commento degli ordini** e verificarlo nel report; il log di MetaEditor data ogni compilazione |
| T11 | **Al cambio conto MT5 spegne da solo il trading automatico**: l'EA gira senza operare | riabilitarlo a mano e controllarlo |
| T12 | Parametri del tester e parametri sul grafico sono **due elenchi separati** | impostarli in entrambi |
| T13 | Experts e Journal hanno file dallo stesso nome in cartelle diverse; **MT5 ruota i log a inizio mese** (un giorno perso) | archiviare ogni sera con rinomina |
| T14 | **Due EA con lo stesso magic** gestiscono la stessa posizione | magic distinti, sempre |
| T15 | Sostituendo un EA con uno dal **nome diverso**, MT5 riapre con i **valori di default** | ricontrollare voce per voce |
| T16 | Le **GlobalVariable** vivono nel terminale, non nel conto: la sincronizzazione verso il VPS **non le copia** (baseline che si sposta in silenzio) | parametri espliciti come input |
| **T17** | **Ritentativi a raffica** su rifiuti permanenti: `[Trade disabled]` (10017), `[Market closed]` (10018), trading automatico disattivato (10026, 10027). Visti dal vivo: **~3.000 richieste in 5 minuti** e **~65 in 3 minuti** | classificare i codici; non ritentare quelli permanenti; tetto e attesa sugli altri; budget di richieste giornaliero |
| **T18** | Il controllo «posso operare?» deve guardare **conto, terminale, EA e simbolo** (`ACCOUNT_TRADE_ALLOWED`, `ACCOUNT_TRADE_EXPERT`, `TERMINAL_TRADE_ALLOWED`, `MQL_TRADE_ALLOWED`, `SYMBOL_TRADE_MODE`) — il nostro guardava solo `MQL_TRADE_ALLOWED` e `ACCOUNT_TRADE_EXPERT` e non si è accorto del conto disabilitato. Il pre-flight completo del nostro EA sull'oro, invece, lo ha visto subito (`conto NO`) | pre-flight completo |
| **T19** | Durante la pausa notturna gli ordini vengono rifiutati; **il primo ordine dopo la riapertura impiega ~1,3 s** | controllare la sessione (`SymbolInfoSessionTrade`) prima di inviare |
| **T20** | Uno slippage loggato **dopo ritentativi** è misurato contro l'**ultimo** tentativo, non contro il segnale: l'inseguimento del prezzo sparisce dal log | loggare il prezzo del primo tentativo; tetto all'inseguimento |
| T21 | Il **calendario economico MQL5** deve essere disponibile sul terminale, altrimenti un filtro news torna vuoto ed è **silenziosamente inattivo**. **Verificato il 30/09: sul terminale FTMO è popolato** (64.986 eventi). Resta da verificare che l'EA lo legga al momento del check: la riga di blocco del nostro filtro non è mai comparsa nei log disponibili | stampare a ogni giornata quanti eventi l'EA ha caricato |
| T22 | Il **volume** dei CFD è il numero di tick del broker, non volume di mercato: filtri tipo RVOL non discriminano | non usarlo come informazione di mercato |
| T23 | Un riavvio con posizioni aperte **sposta i riferimenti dei freni giornalieri** tenuti in memoria, in entrambe le direzioni: freno più stretto se in profitto (può tagliare i vincitori), **più largo se in perdita** — osservato il 28/09: riavvio con −260 $ di flottante, freno allargato di 260 $ | freni ricalcolati dallo storico del server |
| T24 | Un controllo di volume sulla candela d'apertura dà **falsi allarmi** nei giorni di dati macro pre-apertura: **5 falsi allarmi in 30 sedute** (04/09, 10/09, 11/09, 30/09, 01/10), **tutti** in giorni con dati USA ad alto impatto alle 15:30 server (Non-Farm Payrolls, prezzi alla produzione, inflazione, PCE e PIL, sussidi) | verificare l'orario sul report, non sul volume |
| T25 | Il terminale si **aggiorna da solo** (6090 → 6140 → 6182 → 6230: tre aggiornamenti fra il 20/08 e il 28/09). In backtest innocuo; nel live, dopo la 6230, la latenza mediana degli ingressi è passata da 232 a 311 ms (6 ordini) | annotare la build e ricontrollare i tempi d'esecuzione |
| **T26** | **Il tipo di conto cambia la leva** (Standard 1:100, Swing 1:30) e quindi il margine; sullo Standard `US100.cash` vuole il 2,00% del nozionale | `ACCOUNT_LEVERAGE` e `OrderCalcMargin()` prima di dimensionare |

---

## 6. INFRASTRUTTURA — il rischio che ha dominato davvero [MISURATO]

- **Uptime del PC di casa**: su 29 sedute valutabili il terminale era acceso al **64,9%** dei momenti decisionali della strategia intraday (226 check su 348), e **all'ora della chiusura di fine giornata era acceso in circa 8 sedute su 29**; tre sere su cinque dell'ultima settimana è stato spento fra 8 e 17 minuti prima della chiusura delle 22:55 server. Il **02/10 il terminale è rimasto spento per l'intera seduta**: è la prima volta che è saltata la finestra d'ingresso del breakout. Primo forward di agosto: 4 giornate perse su 8.
- **Tre notti con posizioni aperte, tutte per PC spento** prima della chiusura di fine giornata. In una (23-24/09) erano aperti **20,65 lotti**: un gap di circa +1,1% alla riapertura avrebbe consumato **da solo** l'intero limite di perdita giornaliera. Il 28/09 il terminale è rimasto spento 41 minuti con due posizioni aperte: un check semi-orario dell'intraday è saltato e la posizione è poi uscita allo stop, con lo slittamento peggiore del forward.
- **La rete non è stata il problema**: cadute di connessione fino a 4 minuti e mezzo, riparate da sole, **zero trade compromessi** (anche il 28/09, con una riconnessione di un secondo a posizione aperta).
- **VPS MetaTrader** (Londra, ~15 $/mese): latenza **1,3-1,8 ms** contro 29-76 ms da casa (misurata dal terminale; il VPS non è mai stato usato nel forward). Regole, dalla documentazione: sincronizzazione **solo dal PC verso il VPS**, **mai con posizioni aperte**; le GlobalVariable non vengono copiate (T16); sul VPS il trading automatico è sempre attivo.
- **Conseguenze di disegno**: uscite sul server dove possibile; se la strategia usa uscite a orario, **modellare la probabilità di perderle** o prevedere il VPS dal primo giorno; mai dipendere da un'azione manuale.

---

## 7. METODO DI VALIDAZIONE — cosa abbiamo imparato, coi numeri

### 7.1 Quanti trade servono per vedere un edge [BACKTEST]
`n ≈ (1,96 × σ / μ)²`. Per il nostro breakout (μ +0,178 R, σ 2,72) servono **890 trade**; per il momentum (μ +0,144 R, σ 2,77) **1.428**. Con payoff asimmetrico (win rate 19%, vincite da 8R) la **mediana di breve periodo è negativa anche con edge reale**, e una finestra di 5 trade chiude positiva nel 52,7% dei casi: testa o croce.

### 7.2 Cosa un forward può misurare [STUDIO ESTERNO]
Potenza di un test «edge vivo contro edge zero» con Sharpe ~1,3: **21% a 5 mesi, 58% a 24 mesi**. Potenza di rilevare un raddoppio dello slippage: **96% in un mese**. → Il forward serve a **esecuzione e meccanica**: ordini eseguiti, ogni tipo di uscita visto almeno una volta, riavvii, riconciliazione al centesimo.

### 7.3 La prova dal vivo che il P&L breve non dice nulla [MISURATO][STIMA]
Dopo 20 sedute il nostro forward era a **−8.333 $** (2° percentile, verosimiglianza 2,95:1 **contro** l'edge); **quattro sedute dopo** era a **+1.672 $** contando i soli EA (53° percentile, 1,1:1). **A 30 sedute ha chiuso a −1.131 $ contando i soli EA** (−1.150 $ con alcuni trade manuali di prova): **36° percentile** con l'edge intatto, verosimiglianza **1,0:1** fra edge intatto ed edge nullo *(bootstrap per giornata intera, 40.000 simulazioni; replica del calcolo a 24 sedute entro un punto)*. Il 19/09 i numeri sembravano dire «forse è rotto», il 24/09 «funziona», il 02/10 di nuovo «forse no»: **non dicevano niente in nessuno dei tre momenti**.

### 7.4 Monte Carlo: per giornata intera e sull'equity intraday
- **Bootstrap per giornata intera** sulla sequenza reale: le R giornaliere delle nostre due strategie hanno correlazione **0,22**, e campionare trade per trade la cancella. Un nostro calcolo trade-per-trade (08/09, dopo 12 sedute) dava probabilità 0,17% e verosimiglianza 14,7:1 contro l'edge; rifatto per giornata intera: 4,84% e 2,19:1. [STIMA]
- **Limiti FTMO sull'equity intragiornaliera** (1,39× peggiore della chiusura). [STUDIO ESTERNO]
- **Blocchi di più giornate** come controllo della dipendenza seriale.

### 7.5 Challenge e funded sono problemi opposti [BACKTEST][STUDIO ESTERNO]
- **Challenge = barriere** (+10.000 contro il freno): domina la varianza. Un edge ridotto del 19% costa solo ~2 punti di probabilità di essere finanziati entro 6 mesi. Criterio utile: **quanti stop consecutivi sopporta il freno totale** — a 1.000 $/R con freno 7.500 sono 7 (7.500 / 1.022); nel nostro storico il **17,8%** delle serie di perdite consecutive supera 7 (27 su 152, massimo 26).
- **Funded = crescita senza barriera superiore**: conta la **frazione di Kelly** (`f* = μ/σ²`; per il nostro breakout, con l'edge netto: 0,155 / 7,37 = 0,021, cioè 2.104 $ per trade su 100k). Nel modello dello studio esterno (serie del breakout, floor statico −10.000 $, dimensionamento a buffer, cuscinetto 5.000 $, prelievo mensile del 90% dell'eccedenza): a **1.000 $/R (≈ metà Kelly)** il conto sopravvive il **71%** a 36 mesi e rende ~4.700 $/anno; a **500 $/R (≈ un quarto)** sopravvive il **100%** e rende ~16.000 $/anno. Oltre una certa soglia più rischio significa meno crescita (volatility drag).
- **Dimensionamento a buffer** (`rischio = 5% × (equity − 90.000)`): si contrae da solo avvicinandosi al floor e lo rende **irraggiungibile per costruzione**.

### 7.6 Robustezza [STUDIO ESTERNO][BACKTEST]
- **Riottimizzare costa**: walk-forward ancorato su 27 combinazioni → Sharpe **0,98** riselezionando contro **1,31** coi parametri fissi.
- **Altopiano, non picco**: si sceglie la zona in cui i vicini funzionano (es. target 7-8-9R), mai il punto isolato che fuori campione cambia segno.
- **Fortuna di calendario**: nella replica esterna del nostro momentum (dati Pepperstone, con filtro VIX) spostare di 15 minuti la griglia decisionale porta lo Sharpe da **1,09 a 0,33** (−70%); senza filtro VIX il minimo scende a 0,03. Una griglia che sta sul massimo della superficie contiene fortuna.
- **Cross-feed**: la stessa strategia rende **+0,204 R/trade su Pepperstone e +0,144 su FTMO** → testare sul feed del broker dove si opererà.
- **Controllo negativo**: su US500 la stessa strategia è **morta dal 2023** — se una strategia funziona ovunque, sospetta il fitting.
- **Replica indipendente**: il nostro breakout rifatto da zero su un altro broker è risultato entro **0,50 sigma**. È il test più forte contro un errore d'implementazione.
- **Test di equivalenza EA ↔ backtest** (logica dell'EA tradotta in Python e confrontata giorno per giorno): ha trovato un errore di conversione oraria — l'EA avrebbe operato alle 13:30 invece che alle 16:30 — che nessun controllo statico avrebbe visto. E due versioni «uguali» del momentum (ingresso continuo dentro lo slot contro solo al confine) coincidono sul totale (+0,134 contro +0,144 R/trade) ma non sul 2026 (−0,46 R contro −7,45 R): **i dettagli d'esecuzione contano**.

### 7.7 Regime 2026 [BACKTEST][MISURATO]
Nel 2026, forward compreso (fino al 01/10): breakout **+0,032 R/trade su 151** (IC95% [−0,36 ; +0,42]; storico +0,178), momentum **−0,102 su 107** (IC95% [−0,46 ; +0,25]; storico +0,144). Nessuno dei due è statisticamente diverso né da zero né dalla media storica, ma **il 2026 è stato peggiore**: valida ogni strategia nuova **anche sul solo 2025-2026**.
Un indizio coerente: **gli stop rapidissimi sono più frequenti nel 2026**. Dal vivo 5 stop del breakout su 19 sono arrivati entro 60 secondi dall'ingresso (26%), contro l'8,1% del backtest 2021-2026 ma il **13,5% del solo 2026** (probabilità di vederne almeno 5 su 19: 10% con la frequenza 2026, 1,5% con quella storica). Mediana del tempo allo stop: 5,1 minuti dal vivo, 6,3 nel backtest 2026, 7,3 su tutto lo storico.

### 7.8 Pre-registrazione
Scrivere prima: ipotesi, metrica, soglie verde/giallo/rosso, cosa si fa in ogni caso. Mai spostare una soglia dopo aver visto il numero — **quando un argomento tecnico e il proprio interesse puntano nella stessa direzione, sospettare dell'argomento**. Un «veto» monetario su poche settimane è una **protezione dalla rovina**, non un test dell'edge (verosimiglianza ~1,3:1). *Il nostro criterio a due verdetti, pre-registrato, ha dato rosso a 15 sedute e verde a 30: nessuno dei due esiti diceva qualcosa sull'edge, e così è stato dichiarato prima.*

---

## 8. GIÀ TESTATO E SCARTATO — non ripartire da zero

*Tutto su CFD, costi reali, dati 2018/2021-2026 (FTMO o Pepperstone). Un'idea con un meccanismo davvero diverso non è esclusa; una variante di queste sì.*

| Idea | Esito | Fonte |
|---|---|---|
| **14 paper accademici** di trading sistematico | **uno solo** produce edge netto su un singolo CFD in MT5 — ed è quello già in uso (*Beat the Market*) | [STUDIO ESTERNO] |
| **Mean reversion intraday su CFD** — gap-fade, stretch 5 minuti, reversal dopo shock, fade di fine sessione — su NAS100, US500, GER40 e oro (XAUUSD) (**240 combinazioni**, famiglie × strumenti × varianti) | **tutte morte dopo i costi**: *gli estremi intraday continuano, non ritornano*. Unico sopravvissuto un pullback **daily** su GER40 (RSI2<10: +0,21 R, t 2,6), specifico del DAX | [STUDIO ESTERNO] |
| **38 filtri e overlay**: VWAP, EMA12/50, gap, regime di volatilità, NR4, inside day, filtri cross-market, target simmetrici, stop strutturali, uscite temporali, vol targeting | **nessuno migliora in modo robusto**; overlay d'ingresso e vol targeting **peggiorano** | [STUDIO ESTERNO] |
| **Momentum intraday su 24 strumenti** (indici, metalli, energia, FX, VIX) | **sopravvive ai costi solo su NAS100** (+3,5 bps netti, t 2,6); US500 +0,9; tutti gli altri ≤ +0,2 (HK50 −3,3; CN50 −14,8; gas naturale −133) | [STUDIO ESTERNO] |
| Stesse regole del momentum senza ritaratura | **XAUUSD −5.492 $**, **GER40 −2.656 $**, US500 morto dal 2023 | [BACKTEST] |
| **Gestione della posizione** su breakout e momentum: parziali, breakeven, trailing, rapporto rischio/rendimento fisso | tutti peggiorativi (sul momentum: breakeven −25% del P&L, parziali −25%, RR 1:1 −37%, RR 1:3 miraggio fuori campione). **L'edge sta nella coda destra** | [BACKTEST] |
| **Ricerca di edge ad alto win rate** | 3 ipotesi pre-registrate, tutte bocciate: **ogni win rate misurato cade entro ±2 punti da quello previsto da «nessuna informazione + costi»** | [BACKTEST] |
| RVOL / volume relativo sui CFD | inutilizzabile (T22) | [BACKTEST] |
| **Filtro VIX** sul momentum | archiviato: t 1,08, altopiano che crolla cambiando di un giorno il lookback, segno invertito in 2 anni su 6. ⚠️ **Il CFD «VIX» dei broker è il future front-month** (beta 0,547): lo spot va letto dal CSV ufficiale Cboe via `WebRequest()` | [STUDIO ESTERNO] |
| Riottimizzazione periodica dei parametri | −0,33 di Sharpe | [STUDIO ESTERNO] |
| Challenge 1-Step | P(passare) ~35% contro ~95% | [STUDIO ESTERNO] |
| Conti multipli con la stessa strategia | nessun beneficio (correlazione perfetta) | [STUDIO ESTERNO] |
| Martingala, griglia, mediare in perdita | rifiutati a priori. **Firma da riconoscere**: equity liscia, win rate alto, rari buchi enormi | [STUDIO ESTERNO] |
| Rischio che cresce avvicinandosi a una scadenza | dominato dal rischio fisso | [BACKTEST] |

---

## 9. SE LA NUOVA STRATEGIA DEVE GIRARE ACCANTO ALLE NOSTRE

- **Configurazione della nostra challenge**: breakout a **1.000 $ fissi per R** (uno stop costa ~1.022 $), momentum a **500 $ nominali** (fino a ~1.000 $ per trade allo stop protettivo), **freno giornaliero condiviso a 2.000 $**, **freno totale a 7.500 $**. Contro limiti FTMO di 5.000 / 10.000 lo spazio residuo è **poco**.
- I limiti FTMO sono **di conto**, e i nostri freni leggono **l'equity di conto**: una terza strategia sullo stesso conto **interagisce con i nostri freni** e li fa scattare prima. Stesso conto solo **ricalcolando da zero il budget di rischio** con un Monte Carlo congiunto per giornata intera.
- **Il valore di una strategia parallela è la bassa correlazione.** Una seconda strategia di momentum sul NASDAQ agli stessi orari è **leva nascosta**, non diversificazione (è già successo: uno studio esterno ha scritto un EA che duplicava il nostro e lo ha scartato).
- **Magic number distinti** e diversi dai nostri: breakout **20260715**, momentum **26082701**.
- **Mai sul conto di un forward altrui**: trade manuali o un terzo EA su un conto di misura ne sporcano il bilancio, che è la misura. *(Sul nostro conto di misura è rimasto agganciato un EA sull'oro in dry run: nessun ordine, quindi nessun effetto — ma è una deviazione dichiarata.)*
- **Non sviluppare né compilare sul terminale del conto di misura durante le sedute**: il 29/09 una compilazione di EA nuovi nella stessa cartella è stata seguita da un riavvio del terminale a seduta in corso. Innocuo quel giorno (nessuna posizione aperta), ma è la classe di azione che azzera la memoria degli EA (T2, T8, T23). Usa un'installazione separata di MT5 per lo sviluppo.

---

## 10. COSA NON SAPPIAMO — limiti di questo dossier

1. **Tutto viene da conti demo** (`FTMO-Demo`, sia Standard sia Swing). Challenge e conto finanziato possono stare su server diversi: nessuna misura lì.
2. **La coda estrema dello slippage sugli stop** (oltre il 20% della distanza) non è mai stata campionata. In punti il peggiore visto è 5,51.
3. **Spread e slippage su simboli diversi da `US100.cash`**: non misurati (le commissioni sì; per l'oro solo istantanee di spread e specifica dello swap, §2.4).
4. **Esecuzione nei minuti delle notizie macro**: mai campionata su uno stop (nessuno dei 22 è caduto entro ±2 minuti da un dato ad alto impatto).
5. **Gap di weekend** e notti con eventi: tre pause notturne attraversate con posizioni aperte (24→25/08, 15→16/09, 23→24/09). La riapertura è stata osservata solo il 24/09, senza gap rilevante; nelle altre due notti il gap non è misurato, ma non ha fatto scattare lo stop. Mai un weekend.
6. **Ordini pendenti, chiusure parziali, swap su long e nel weekend**: nessuna misura.
7. **Il costo residuo della strategia di momentum** non è mai stato misurato direttamente (stima prudente 0,05 R per trade; tetto di 0,125 R imposto dal suo filtro costi). Dal vivo: slippage d'ingresso medio +0,03 punti su 10 ingressi, 3 uscite su 10 allo stop.
8. **La chiusura automatica del Free Trial** agli obiettivi è un'inferenza dai log, non una regola scritta da FTMO.
9. **Nove settimane** di misure dal vivo: nessuna in condizioni di stress estremo; un solo movimento rapido documentato (28/09).
10. **Margine degli indici su un conto Swing**: non misurato.

---

## 11. CHECKLIST DI VALIDAZIONE O SCARTO — da applicare a ogni strategia nuova

**Ogni cancello: VERDE, GIALLO o ROSSO, con il numero accanto. Soglie da scrivere PRIMA di guardare i risultati.**

| # | Cancello | Verde se… |
|---|---|---|
| **G1** | **Costi** | expectancy **netta** > 0 con: spread **di oggi** per quel simbolo e quell'ora (su `US100.cash` 1,45 anche in orario USA, fino a 2,19 nell'ora prima dell'apertura) · commissioni del simbolo · slippage sugli stop (≈0,8 punti su `US100.cash`) × frazione di uscite a livello, **se il backtest non lo contiene già** (§2.2) · swap se overnight (sull'oro è grande, §2.4). **E resta > 0 sotto stress** (spread +50%, slippage sugli stop × 2,5, +0,5 punti su ogni ordine a mercato). Costo totale ≤ **12,5% di R** consigliato |
| **G2** | **Campione** | t ≥ 2 sulla media **netta**; n ≥ `(2σ/μ)²`; distribuzione delle R riportata (asimmetria, quota dei 20 trade migliori). *Taratura: sui soli dati FTMO le nostre due strategie non sarebbero verdi (t netto 1,78 e ~0,9, §12); le sosteniamo con il paper d'origine, la replica indipendente e un secondo feed. Decidi prima se G2 è una soglia dura o se un giallo con conferme esterne basta* |
| **G3** | **Robustezza** | altopiano nei parametri; fuori campione o walk-forward; risultato per anno, con **2025-2026 a parte**; dati **FTMO dal 14/09/2021** (o del broker d'arrivo); nessuna riottimizzazione |
| **G4** | **Regole FTMO** | Monte Carlo per giornata intera **sull'equity intraday**: P(fase 1), P(entrambe), P(funded entro 6 mesi), quote attese, **P(violazione del floor) ≈ 0**; peggior giornata contro il 5%; serie di stop contro il freno totale |
| **G5** | **Operatività** | SL/TP sul server · stato letto dal server dopo ogni riavvio · `TimeTradeServer()` · codici di errore classificati e **budget di richieste << 2.000/giorno anche nel caso peggiore** · pre-flight conto/terminale/EA/simbolo · leva e margine verificati sul tipo di conto (`OrderCalcMargin`) · calendario festività e mezze sedute · orari derivati da GMT e regole dell'exchange · BUILD_ID nel commento · magic distinto · blocco al target con margine · equivalenza EA ↔ backtest verificata giorno per giorno |
| **G6** | **Portafoglio** | correlazione delle R giornaliere con le nostre strategie; budget di rischio congiunto se stesso conto |
| **G7** | **Funded** | niente weekend su conto Standard (o scelta Swing, che però ha leva 1:30) · nessuno stop o target probabile entro ±2 minuti dalle news su conto Standard · dimensionamento pensato per la crescita (Kelly), non per la barriera |
| **G8** | **Forward** | cancelli **meccanici** pre-registrati: ordini eseguiti, ogni tipo di uscita visto dal vivo, riconciliazione al centesimo con la cronistoria, nessun ordine fallito, nessun doppio trade. **Non si usa il P&L del forward come prova dell'edge** |

**Segnali rossi — scarto immediato, salvo prova contraria forte:**
- l'edge c'è solo **lordo**, o sparisce con lo spread del 2026;
- stop così stretto che lo spread supera il 5% di R senza un payoff che lo compensi;
- il risultato viene da un **picco** di parametri con vicini molto peggiori;
- **equity liscia + win rate alto + rari buchi enormi** (firma di martingala, griglia, media in perdita);
- usa il **volume** dei CFD come informazione di mercato;
- è una **mean reversion intraday** su indici CFD o oro (240 combinazioni già testate: morte tutte tranne un pullback daily sul DAX);
- richiede di **modificare o reinviare ordini ad alta frequenza** (budget di richieste);
- serve **tenere nel weekend** su un conto finanziato Standard;
- è validata su dati FTMO **prima del 14/09/2021** o su **poche settimane di P&L**.

---

## 12. NUMERI DI RIFERIMENTO — le nostre due strategie *(per confronto)*

| | Breakout d'apertura (ORB) | Intraday momentum (IM) |
|---|---|---|
| Strumento, timeframe | `US100.cash` M5 | `US100.cash` M1 |
| Trade (15/09/2021 → 30/07/2026) | **969** (circa 4 giorni su 5) | **742** (circa metà dei giorni, max 3 al giorno) |
| Media, deviazione standard | **+0,178 R**, 2,72 | **+0,144 R**, 2,77 |
| t sulla media (dati FTMO), lorda / netta | **2,05** / **1,78** | **1,41** / **~0,9** (su dati Pepperstone l'edge è più alto: +0,204 R/trade) |
| Win rate | **19,3%** | **41,0%** |
| Uscite | 80,3% stop · 7,4% target 8R · 12,3% fine giornata | 46,4% fine giornata · 38,0% rientro in banda · 15,6% stop a −2R |
| Drawdown massimo | −37,2 R | −41,6 R |
| Concentrazione | i 20 trade migliori valgono il **93%** della somma | il trade migliore vale **+54 R** |
| Trade per distinguere l'edge da zero | **890** | **1.428** |
| Edge netto dei costi | **+0,155 R/trade** (esempio svolto al §2.2) | non misurato (costo residuo stimato in via prudente a 0,05 R) |
| Correlazione giornaliera fra i due | **0,22** | |
| P(funded entro 6 mesi) nella nostra configurazione | **76-87%** secondo il modello (due stime indipendenti) | |
| Quote di challenge attese per arrivare al funded | **2,7-2,8 quote da 540 €** (~1.440-1.490 €; budget prudente 1.500 €) | |
| **Forward FTMO, 30 sedute (21/08 → 02/10/2026)** | **22 trade, 4 vincenti, −4,46 R** · uscite: 18 stop, 3 fine giornata, 1 catch-all | **10 trade, 3 vincenti, −3,49 R** · uscite: 3 stop, 3 banda, 2 fine giornata, 2 catch-all |
| Somma del forward sui 4 conti | **−1.150,23 $** (solo EA −1.130,95): sopra la soglia pre-registrata di −6.437 $ → **verdetto monetario VERDE**; 36° percentile con l'edge intatto | |
| Regime 2026, backtest + forward | **+0,032 R/trade su 151** | **−0,102 R/trade su 107** |

---

## 13. FONTI E TRACCIABILITÀ

**Documenti del progetto** (chiedili all'utente, Manu, se ti servono i dettagli):
`COSTI_ESECUZIONE_REALI_FTMO_US100` rev 5.1 (md5 `6e361905d7fe8d1bf4de4f53506b16cd`) · `ESECUZIONI_REALI_FTMO_US100_TRADE.csv` (33 trade, md5 `24346a19fb9a7a8d0ad0b185150d772a`) · `VERBALE_FORWARD_SEDUTE` (sedute 1-30, ogni trade riconciliato al centesimo) · `MEMORIA_PROGETTO_ORB_MOMENTUM` (decisioni, trappole, numeri) · `HANDOFF_RICERCA_EDGE_ESTERNA_30-08-2026` (md5 `0e5d90d6580b92f79c2c5e056f01c0ed`, lo studio esterno) · serie `ORB_trades_R_20212026.csv` (md5 `08ef75849302017c487afc36c9c65333`) e `MOMENTUM_trades_R_20212026_FTMO.csv` (md5 `a4d046494a856852b8f76e219e037626`).

**Regole FTMO, verificate il 26/09/2026:**
[Free Trial](https://ftmo.com/en/ftmo-free-trial/) · [FAQ Free Trial](https://ftmo.com/en/faq/how-about-a-free-trial/) · [Obiettivi di trading](https://ftmo.com/en/trading-objectives/) · [Challenge 2-Step](https://ftmo.com/en/2-step-challenge/) · [Pratiche vietate](https://ftmo.com/en/forbidden-trading-practices/) · [Strumenti e strategie](https://ftmo.com/en/faq/which-instruments-can-i-trade-and-what-strategies-am-i-allowed-to-use/) · [News](https://ftmo.com/en/faq/can-i-trade-news/) · [Overnight e weekend](https://ftmo.com/en/faq/do-i-have-to-close-my-positions-overnight-or-before-the-weekend/).

*Le regole FTMO cambiano: prima di una decisione con soldi veri, riverificale sul sito. La leva del conto Swing (1:30) è letta dal terminale, non dal sito.*

---

### Storico delle revisioni
- **Revisione 1** (26/09/2026): prima stesura.
- **Revisione 2** (26/09/2026, doppio controllo su fonti primarie — serie CSV, Report Cronistorico, sorgenti degli EA, memoria e studio esterno del progetto, pagine ufficiali FTMO riverificate). **Correzioni che cambiano l'uso dei numeri**: (1) la ricetta dei costi (§2.2) poteva far **contare due volte** lo slippage sugli stop in un backtest MT5 su tick reali — ora distingue i tipi di backtest e indica il controllo da fare; (2) lo slippage sugli stop è ora espresso **in punti (≈0,7)**: in percentuale della distanza veniva sottostimato per gli stop stretti; stress × 2,5; (3) lo spread di oggi è 1,4 volte la media storica e 2,4 volte quello del 2021, non «oltre il doppio» della media; (4) la coda dello slippage sugli stop arriva a 0,63 R nel backtest, non «fino a 0,20 R»; (5) la misura «su SL/TP» riguardava solo gli stop: sui target non abbiamo misure (uno solo colpito dal vivo, il 04/08); (6) aggiunta l'avvertenza sui backtest a barre: la serie del momentum (Python su barre M1) gonfia l'attraversamento degli stop, almeno +4% della distanza contro +0,2-0,7% dal vivo; (7) sul netto dei soli dati FTMO le nostre strategie hanno t 1,78 e ~0,9: aggiunta la taratura del cancello G2. **Altre**: regola 8 precisata; lo slippage d'esecuzione delle uscite a mercato è stimato, non misurato; chiusura automatica del Free Trial e deviation ignorata dichiarate come inferenze; le pause notturne attraversate sono tre, non una; quota della challenge in euro (540 €) e quote attese 2,7-2,8; Kelly calcolato sull'edge netto, con il contesto del modello (§7.5); la fortuna di calendario (§7.6) e il confronto con la 1-Step (§3.5) vengono dallo studio esterno, con le sue metriche; FTMO non quota il VIX; T5 aggiornata ai dati attuali; aggiunti il glossario (§0.1), l'esempio svolto (§2.2) e il test di equivalenza (§7.6); correzioni minori (deviazione standard 2,72, ping 29-76 ms, orologio del PC, fonti del fuso orario, periodo delle misure, attribuzione dei numeri sulla gestione della posizione, R del momentum nel glossario, +1.672 $ riferito ai soli EA, mean reversion «tutte morte tranne una»).
- **Revisione 3** (06/10/2026): forward chiuso a **30 sedute** (6 trade nuovi, 28/09-01/10, su un Free Trial **Swing**); costi ricalcolati da zero sulla tabella dei 33 trade (`ESECUZIONI_REALI_FTMO_US100_TRADE.csv`, nuova, riconciliata al centesimo con le cronistorie dei quattro conti). **Cosa cambia per chi usa i numeri**: (1) slippage sugli stop raccomandato **≈0,8 punti** invece di ≈0,7, dopo un caso da **5,51 punti** in un movimento rapido senza notizie; (2) **spread in orario USA: usare 1,45**, non lo 0,80 storico; nuova fascia cara nell'ora che precede l'apertura cassa (fino a 2,19); (3) **ritirata** l'affermazione (rev 2, punto 6) che il backtest a barre del momentum «gonfia» l'attraversamento: con tre stop dal vivo la media è vicina a quella del backtest; (4) nuova regola d'oro 17 e trappola T26 su **leva e margine per tipo di conto** (Standard 1:100 con indici all'1:50 misurato, Swing 1:30); (5) **deviation ignorata anche su un fill contrario** (+5,71 oltre 5,0): da inferenza a misura; (6) primo profilo di costo dell'**oro** (§2.4); (7) **calendario MQL5 verificato popolato** sul terminale FTMO (T21) e confronto stop/notizie (§3.2); (8) esito del forward e regime 2026 aggiornati (§7.3, §7.7, §12), con la nota sugli stop rapidissimi più frequenti nel 2026. **Correzioni minori**: rischio senza riancoraggio nei casi estremi 0,81× (non 0,83×); T25 aggiornata (con la build 6230 gli aggiornamenti automatici del terminale sono tre); T24 ora conta 5 falsi allarmi, tutti in giorni con dati alle 15:30 server; tempi d'esecuzione letti dai journal per tutti gli ordini (mediana 232 ms fino al 24/09, non 234 su 20 «documentati»).
- **Revisione 3.1** (06/10/2026, doppio controllo prima della consegna): tabella dei trade riverificata con un secondo script indipendente contro le cronistorie e i journal (0 differenze su 33 trade) e tutte le statistiche citate ricalcolate da zero (coincidono, salvo un arrotondamento sull'ultima cifra). **Precisazioni**: la commissione zero vale per «i 33 trade dal 17/08», non «del forward» (il trade del 17/08 lo precede); mediana dello spread dell'oro **0,405** (media 0,40). Nessun valore misurato né alcuna conclusione cambia.

*Dossier compilato il 26/09/2026 e aggiornato il 06/10/2026 dal progetto ORB US100 + Intraday Momentum NAS100 su FTMO. Ogni numero marcato [MISURATO] è ricostruibile dai log di MetaTrader 5, dai Report Cronistorici archiviati e dalla tabella dei trade; ogni trade del forward è stato riconciliato al centesimo contro l'estratto conto. **Revisione 3.1.***
