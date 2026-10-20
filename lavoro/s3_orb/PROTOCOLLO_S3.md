# PROTOCOLLO PRE-REGISTRATO — S3 «l'ORB di Manu sulle altre aperture» (regole congelate)
*Scritto il 20/10/2026 **prima di qualunque risultato** su S3: lo certifica l'orario del commit. Manu: «Solo se nessuna delle 2 [S1, S2] risulta valida procedi con S3». S3 parte solo dopo che il doppio controllo ha confermato S1 e S2 non valide. Correzioni successive solo come addendum datati «prima/dopo i numeri».*

## 0. Idea, trasparenza, limiti
- **Idea**: l'ORB di Manu (`ORB_US100_-_step18_R_Guardia.mq5`, build 10-09-R) funziona su US100 all'apertura USA (dossier: +0,178 R lordo, t 2,05 su 969 trade 2021-2026; lista del tester PROVA 1 allegata). Il meccanismo dichiarato (Zarattini-Aziz 2023) è il **flusso d'apertura** della sessione cassa. Lo applichiamo **con le stesse regole, senza ritaratura**, alle aperture di altre borse: aggiunge 1-3 trade al giorno in fusi diversi, cioè diversificazione.
- **Già visto**:
  - nulla su queste combinazioni;
  - il dossier riporta che l'**IM** non ritarato è morto su GER40 e oro (strategia diversa);
  - l'EA contiene già un calendario Xetra (apertura alle 10:00 server): se Manu ha già provato l'ORB sul DAX, va dichiarato.
- **Limite**: il backtest è su barre M1 (non su tick reali come il tester MT5). Se stop e target cadono nella stessa barra, vince lo stop (prudenza).
- **Controllo di equivalenza prima di tutto**: la stessa implementazione su US100 FTMO (15/09/2021 → 29/12/2023) deve riprodurre la lista del tester PROVA 1 (filtro di allineamento spento). Le soglie sono fissate ora:
  - ≥ 95% dei giorni con la stessa decisione (trade sì/no e verso);
  - correlazione delle R per trade ≥ 0,90;
  - differenza della R media ≤ 0,05.
  - Se fallisce, S3 si ferma finché l'implementazione non è corretta (correzioni solo prima di guardare gli altri strumenti).
- **Esito dell'equivalenza, ottenuto scrivendo il protocollo e prima di qualunque numero sugli altri strumenti**:
  - **prima versione** (stop e target valutati solo sul bid): stessa decisione 468/468, correlazione delle R 0,975, ma R media 0,220 contro 0,141 del tester → **fallita** sulla terza soglia. Causa: mancava lo spread, e gli short di MT5 escono all'**ask** (5 stop di short mancati per una frazione di spread);
  - **versione corretta** (lato ask ricostruito come bid + spread storico del minuto; long all'ask, short al bid; uscite degli short e loro stop e target sull'ask; stop e target riancorati al fill come nell'EA): stessa decisione **468/468**, stesso verso **100%**, prezzo d'ingresso identico (differenza mediana 0), **correlazione delle R 0,9999**, R media 0,159 contro 0,141 → **superata**. La differenza residua (0,018 R) è lo slittamento reale sugli stop dei tick, che il tester contiene;
  - file: `risultati/EQUIV_US100.json` e `EQUIV_US100_python.csv`.

## 1. Regole dell'ORB (congelate, dal sorgente)
1. **Candela 1** = barra M5 che inizia all'apertura della borsa cassa, costruita dalle barre M1 della stessa finestra di 5 minuti.
2. **Filtri**:
   - range nullo → nessun trade;
   - doji (|close − open| < 5% del range) → nessun trade;
   - **range < 12% dell'ATR(14) giornaliero** → nessun trade.
   - ATR come in MT5: media semplice di 14 true range delle barre D1 del giorno server; si usa l'ultima barra D1 completa (giorno server precedente).
3. **Verso** = verso del corpo della candela 1 (close > open → long).
4. **Ingresso** = open della prima barra M1 che inizia a apertura + 5 minuti (entro 2 minuti; altrimenti nessun trade). Un solo trade al giorno.
5. **Stop** = 10% dell'ATR dall'ingresso; **target** = 8 × la distanza dello stop; entrambi sul server.
6. **Uscita a fine sessione**: 5 minuti prima della chiusura della borsa cassa, all'open della prima barra M1 che inizia a quell'ora (entro 5 minuti).
7. **Esecuzione su barre M1** (bid dei file; ask = bid + spread):
   - i long entrano all'ask ed escono al bid; gli short entrano al bid ed escono all'ask;
   - stop e target sono riancorati al prezzo d'ingresso (come l'EA);
   - long: stop se il low del bid raggiunge il livello, target se lo raggiunge l'high;
   - short: stop e target valutati sull'ask (high e low del bid + spread);
   - se nella stessa barra sono raggiungibili entrambi, vince lo stop;
   - gap oltre il livello → esecuzione all'open della barra.
   - Spread: per l'equivalenza col tester, quello storico del minuto; **per i test, lo spread FTMO di oggi** (tabella congelata, in bps del prezzo, contesto d'ingresso; per l'uscita a fine sessione il suo contesto).
8. **R** = (uscita − ingresso) × verso / distanza dello stop.

## 2. Borse e strumenti
| Strumento | Borsa (calendario) | Apertura → chiusura locale (fine sessione − 5') | Feed d'inferenza | Concordanza |
|---|---|---|---|---|
| GER40 | Xetra | 09:00 → 17:30 (17:25) Francoforte | Pepperstone (11/06/2020) | FTMO (28/12/2021) |
| UK100 | LSE | 08:00 → 16:30 (16:25) Londra | Pepperstone (06/06/2017) | FTMO (14/09/2021) |
| FRA40 | Euronext Parigi | 09:00 → 17:30 (17:25) Parigi | FTMO (14/09/2021) | — |
| JP225 | Tokyo | 09:00 → 15:00 (14:55) Tokyo (prima del 05/11/2024) | FTMO (11/09/2021) | — |
| US500, US30, US2000 | NYSE | 09:30 → 16:00 (15:55) New York; mezze sedute 13:00 (12:55) | Pepperstone (13/07/2020; 02/01/2018; 05/06/2017) | FTMO per US500 e US2000 |

- **Calendari**:
  - festivi di borsa come in S1/S2;
  - Tokyo = festivi nazionali giapponesi + 31/12 e 1-3/01;
  - mezze sedute NYSE con chiusura alle 13:00; mezze sedute europee escluse.
- **Dati**: copie sigillate < 2024 (`dati_scoperta_tutti`, `dati_s12/scoperta`, `dati_s3/scoperta`), fusi verificati (NY+7). Conversione degli orari locali come in S1/S2 (`zoneinfo`).
- Si usano solo barre di giornate M1 (passo modale 1 minuto), come in S1/S2.
- **Hold-out** 2025-2026 mai toccato. **Validazione 2024** solo per i promossi.

## 3. Costi FTMO (di oggi), in bps del prezzo
- **Spread**: p75 FTMO 10/10/2025 → 09/10/2026 al minuto locale esatto ±2 dell'ingresso (apertura + 5') e dell'uscita a fine sessione.
  - Tabella congelata `risultati/COSTI_S3.csv`, prodotta prima dei numeri.
  - US30: regola di S1/S2 (US100 riscalato e massimo con US100 e US500).
  - JP225, GER40, UK100, FRA40, US500, US2000: file FTMO.
- Lo spread entra dal modello bid/ask del §1.7. Si aggiunge lo slittamento sulle uscite a livello (stop e target) = 0,32 bps (gli 0,8 punti misurati su US100 a ~25.000). Commissioni 0.
- **Stress**: spread × 1,5; slittamento sui livelli × 2,5; +0,3 bps per ogni ordine a mercato (ingresso e uscita a fine sessione).
- Nessuno swap (tutto intraday).

## 4. Test e cancelli
- **Test primari: 3 panieri**, valore giornaliero = media delle R nette base degli strumenti del paniere che fanno il trade quel giorno:
  - **EUROPA** (GER40, UK100, FRA40);
  - **ASIA** (JP225);
  - **USA-ALTRI** (US500, US30, US2000).
- **Statistica**: t raggruppato per data (CR1, Student G−1), p unilaterale sulla media netta > 0. **BH q = 0,10 sui 3.**
- **PROMOSSO** se tutte:
  - BH superata;
  - netto stress > 0;
  - netto base > 0 in entrambe le metà (taglio alla data mediana del paniere);
  - ≥ 3 anni con ≥ 10 giorni e ≥ 60% di essi positivi;
  - almeno metà degli strumenti del paniere con netto base > 0;
  - netto base > 0 senza l'1% delle date più influenti;
  - stesso segno del lordo sul feed di concordanza (se ≥ 100 giorni in comune).
- **INDIZIO** / **NULLO** come in S1/S2.
- **Secondari** (descrittivi): R per strumento, quota di uscite a stop/target/fine sessione, R media per anno.
- **Indipendenza (G6), fissata ora**: correlazione giornaliera delle R con l'ORB US100 (lista PROVA 1, solo date < 2024). USA-ALTRI apre allo stesso minuto dell'ORB: se la correlazione supera 0,3, quel paniere **non conta come strategia nuova**, perché è leva sull'ORB esistente.
- **Potenza** [STIMA]:
  - ORB su US100: Sharpe per trade ≈ 0,065;
  - EUROPA ≈ 1.000-1.500 giorni (UK100 dal 2017), soglia BH di primo rango 0,10/3 → t ≈ 1,83: rilevabile al 50% uno Sharpe ≈ 0,05-0,06 per giorno;
  - ASIA ≈ 550 giorni: rilevabile solo ≥ 0,08.

## 5. Dopo
Come S1/S2 §8:
- configurazione unica (regole congelate), tutti gli strumenti del paniere;
- validazione 2024 una volta (p < 0,10 e netto stress ≥ 0);
- F4 con Monte Carlo congiunto con ORB e IM;
- hold-out una volta.

## 6. Doppio controllo
- Test di equivalenza con il tester (§0).
- Replica cieca dal protocollo.
- Controllo a mano di giorni campione.
