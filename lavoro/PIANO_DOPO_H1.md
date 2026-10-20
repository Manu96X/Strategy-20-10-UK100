# DOPO H1 — CONSIDERAZIONI DA QUANT E PIANO PER TROVARE STRATEGIE VALIDE (≥ 0,7 trade al giorno)
*20/10/2026. Basato su: F3 (strategia FTSE), event study (242 test), H1 (`h1_dollaro/RAPPORTO_H1.md`) e su **tutti** i documenti caricati: dossier FTMO rev 3.1, costi reali rev 5.1, verbale del forward, 33 esecuzioni reali, specifiche dei simboli, tre calendari economici, file M1BA bid/ask, chiusure speciali dell'oro, lettura dello stop out, nuovi storici M1 (6 coppie forex, US30, US2000, JP225, FRA40, EU50, HK50). Etichette: [MISURATO] [BACKTEST] [SPECIFICA] [LETTERATURA] [STIMA].*

## 1. Bilancio onesto
| Ricerca | Test | Esito |
|---|---|---|
| Strategia del video (UK100) | 13 celle pre-registrate | nessun edge, nemmeno lordo sulla Regola 2 |
| Event study multi-strumento | 242 test, 10 strumenti | 0 superano la correzione |
| **H1**, il miglior candidato (t −3,8 nella scoperta) | 1 test indipendente | **segno opposto** fuori campione (+0,053, p 0,87) |
| Dossier FTMO §8 (lavoro precedente) | 14 paper, 240 combinazioni di mean reversion, 38 filtri, momentum su 24 strumenti | sopravvivono solo ORB e IM sul NASDAQ |

**Conclusione da quant**:
- Sui CFD liquidi, ai costi FTMO del 2026, i **pattern di solo prezzo** sono di fatto esauriti: giornalieri, di calendario, fra strumenti o di reversione tecnica.
- Ciò che funziona davvero (ORB e IM) ha tre caratteristiche: è **intraday**, è legato a un **flusso a orario noto** (l'apertura USA) e ha un edge modesto (t lordo ≈ 2).
- È la tua stessa lezione: «prosecuzione dopo flussi o livelli strutturali, reversione dopo un flusso a orario noto».

## 2. Cinque lezioni operative
1. **Il premio del vincitore è reale**: il migliore di 100 test (t −3,8) è andato a zero fuori campione. D'ora in poi un candidato passa alla validazione solo se, **già dentro la scoperta**:
   - ha lo stesso segno nelle due metà del periodo (2017-2019 e 2020-2023);
   - lo ha su entrambi i feed;
   - supera la correzione nella sua famiglia.
2. **La frequenza serve anche a confermare.** Restano ~2,8 anni sigillati (2024 + 2025-2026). Con ≥ 0,7 trade al giorno sono ~490 trade, e basta uno Sharpe per trade ≥ 0,09 per avere t ≥ 2. Con 13 trade l'anno non si conferma nulla. **Il tuo obiettivo di frequenza coincide con quello statistico.**
3. **Il costo di tenere la notte** [SPECIFICA]:
   - long sugli indici −0,023% a notte, triplo il venerdì (≈ −8% l'anno se tenuto sempre);
   - long sull'oro −0,0165%;
   - forex: commissione ≈ 0,5 pip a round-trip, swap asimmetrici e quasi sempre a debito (il carry se lo mangia il broker).
   - → Preferire strategie **intraday, flat la notte**. È anche la forma più comoda per la perdita giornaliera FTMO sull'equity e per le regole del conto Standard (weekend, news).
4. **Spread reali del 2026** [MISURATO, file M1BA]:
   - US100: **fisso a 1,45** in orario USA, **1,90** prima dell'apertura (anche nel minuto dei dati delle 15:30 server), **2,08** dopo la chiusura cassa.
   - Oro: 0,60-0,63, p90 **0,86** nel minuto delle notizie.
   - Nel 2022 lo spread si allargava nel minuto delle notizie (max 2,1 contro 0,6); nel 2026 no.
5. **Trappole di fuso**: forex e metalli FTMO seguono l'ora legale europea fino al 2019; il calendario economico è sempre NY+7. Ogni istante va fissato in ora di New York.

## 3. Strade proposte (in ordine di priorità)

### S1 ⭐ — Prosecuzione dopo i dati macro (flusso a orario noto, direzione data dalla notizia)
| Voce | Contenuto |
|---|---|
| Meccanismo | i dati macro cambiano le aspettative e il **flusso di ordini continua per decine di minuti o ore** dopo il primo scatto (Andersen-Bollerslev-Diebold-Vega 2003; Evans-Lyons 2008) [LETTERATURA]. Coerente con il dossier: «gli estremi intraday continuano, non ritornano» |
| Regole da testare | evento = dato ad alto impatto del calendario. Due famiglie: **(a)** verso = sorpresa standardizzata (attuale − previsto), **(b)** verso = primo movimento T → T+2 minuti, se ampio. Ingresso a **T+3 minuti** (fuori dalla finestra FTMO di ±2 minuti), uscita a T+30, T+60 o T+120 minuti, stop sul server |
| Strumenti | EURUSD, USDJPY, GBPUSD (forex FTMO dal 2015), oro, US100/US500 (Pepperstone dal 2017) |
| Frequenza | dati USD ad alto impatto con attuale e previsto: **~280 orari distinti l'anno (1,1 al giorno)** nel 2018-2023; più EUR, GBP, JPY (~110 l'anno). Con un filtro d'ampiezza: **0,6-1 trade al giorno** |
| Costi | spread dal M1BA (minuto delle notizie) + slippage sugli stop 0,8 punti × 2,5 in stress; nessuno swap |
| FTMO | Standard ok: niente ingressi o stop entro ±2 minuti dagli eventi (filtro col calendario MQL5, già popolato sul terminale). Swing senza vincoli |
| Indipendenza | lontano da ORB (09:35 NY) e IM; correlazione da misurare (G6) |
| Potenza | ~1.900 eventi USD nella scoperta (2017-2023); ~700 nel 2024-2026 (fino all'08/10/2026) |

### S2 — Reversione dopo le aste di chiusura (flusso a orario noto)
| Voce | Contenuto |
|---|---|
| Meccanismo | gli ordini «al prezzo di chiusura» spingono il prezzo nell'asta e la pressione **rientra nelle ore successive**, in buona parte entro l'apertura del giorno dopo (Bogousslavsky-Muravyev 2023, *Who trades at the close?*) [LETTERATURA] |
| Regola da testare | movimento degli ultimi 10-15 minuti prima dell'asta (USA 16:00 NY; Xetra 17:30 e LSE 16:30 locali) → posizione contraria dopo l'asta. Due uscite: dopo 30-45 minuti, **prima della pausa** (US100.cash chiude alle 16:50 NY), oppure all'apertura del giorno dopo (paga una notte di swap) |
| Strumenti | US500, US100, US30, US2000; GER40, UK100, FRA40, EU50 |
| Frequenza | 2 finestre al giorno (Europa e USA); col filtro d'ampiezza **0,7-1 trade al giorno** |
| Costi | US100 2,08 punti dopo la chiusura (≈ 0,8 bps): va verificato che il rientro li superi |
| Indipendenza | orari diversi da ORB e IM (IM esce alle 15:55 NY) |

### S3 — ORB sulle altre aperture (trasferimento della tua strategia che funziona)
- Regole dell'ORB **congelate** (nessuna ritaratura) applicate a GER40 (Xetra 09:00), UK100 (Londra 08:00), JP225 (Tokyo 09:00), US500/US30/US2000.
- Meccanismo: il flusso d'apertura, come sul NASDAQ. Aggiunge 1-3 trade al giorno in fusi diversi.
- **Mi servono le regole esatte dell'ORB** (sorgente o specifica, in sola lettura) e la lista dei suoi trade.
- Limite noto (dossier): l'IM non ritarato è morto su GER40 e oro. Un esito negativo resta probabile.

### Moduli a bassa frequenza (solo come aggiunta)
Drift prima del FOMC e giorno prima dei festivi (H2, H3 della rosa): 15-20 eventi l'anno. Da confermare sul 2024-2026 solo se S1/S2/S3 arrivano in validazione.

### Strade che sconsiglio, e perché
- **Varianti di H1** («solo dopo il 2019»): data mining.
- **RSI(2) giornaliero su un paniere di indici** (spunto dai paper):
  - è reversione tecnica senza flusso, contraria alla tua lezione;
  - il dossier la trova viva solo sul DAX;
  - la swap sui long pesa su 3-4 notti.
- **Carry sul forex**: gli swap FTMO sono a debito quasi ovunque.
- **Momentum o mean reversion intraday generici**: già testati (dossier §8).

## 4. Piano operativo (metodo invariato, cancelli G1-G8 del dossier)
| Fase | Cosa | Cancello per andare avanti |
|---|---|---|
| **0. Dati e costi** | sigillo < 2024 di tutti i nuovi storici; calendario pulito (eventi, revisioni, segno della sorpresa, ora NY); tabelle di spread per simbolo e ora (FTMO p75 + taratura M1BA); swap dalla specifica | controllo indipendente dei dati |
| **1. Event study pre-registrato** S1 e S2 (S3 se arrivano le regole) | protocollo scritto e pubblicato prima dei numeri; pochi parametri fissati dalla letteratura; correzione BH per famiglia | BH superato · stesso segno 2017-2019 e 2020-2023 · stesso segno sui due feed · netto > 0 in stress · ≥ 0,7 trade al giorno (o somma dei moduli) |
| **2. Strategia e backtest** | regole complete (stop, uscite, filtro news, sessioni, festivi), costi del 2026, replica cieca e revisione avversaria | G1 e G2 verdi; G3 con altopiano |
| **3. Validazione 2024** (una volta) | solo i candidati promossi | netto > 0 e stesso segno |
| **4. F4: progetto FTMO** | Monte Carlo per giornata intera sull'equity intraday, dimensionamento, correlazione con ORB e IM (G4, G6, G7) | P(violazione) ≈ 0 |
| **5. Hold-out 2025-2026** (una volta, regole congelate) | FTMO + Pepperstone | verdetto finale |
| **6. EA MQL5 e forward** | EA nuovo (nessun EA esistente toccato), test di equivalenza EA ↔ backtest giorno per giorno, forward solo per la meccanica (G5, G8) | |

## 5. Cosa mi serve da te
1. **La scelta**: S1, S2, S3 (consiglio **S1 + S2** in parallelo, due famiglie separate).
2. Le liste dei trade di ORB e IM (`ORB_trades_R_20212026.csv`, `MOMENTUM_trades_R_20212026_FTMO.csv`, citate nel dossier §13) per il cancello G6. `IM_NAS100_trades.csv` ha 2 trade e `RL_XAU_trades.csv` è vuoto: non bastano.
3. Per S3: le regole dell'ORB (sorgente o specifica), in sola lettura.
4. Conferma del protocollo di ogni famiglia prima dei risultati, come sempre.
