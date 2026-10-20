# PROTOCOLLO PRE-REGISTRATO — S3 «l'ORB di Manu sulle altre aperture» (regole congelate)
*Versione definitiva del 20/10/2026, **prima di qualunque risultato** su strumenti diversi da US100 (orario del commit). Manu: «Solo se nessuna delle 2 [S1, S2] risulta valida procedi con S3». S1 e S2 sono state confermate NON valide da due repliche cieche, dalla revisione del codice e dal controllo a mano, anche senza i periodi con fuso anomalo (`../s1_s2/RAPPORTO_S1_S2.md`). La bozza è stata rivista da due revisori avversari (statistica e fedeltà all'EA; dati, esecuzione e costi) **senza guardare R fuori da US100**; tutte le correzioni sono integrate qui. Correzioni successive solo come addendum datati.*

## 0. Idea, trasparenza, limiti
- **Idea**: l'ORB di Manu (`ORB_US100_-_step18_R_Guardia.mq5`, build 10-09-R, filtro di allineamento spento) funziona su US100 all'apertura USA (lista del tester PROVA 1: 969 trade 2021-2026, t ≈ 2,0). Il meccanismo è il **flusso d'apertura** della sessione cassa (Zarattini-Aziz 2023). Lo applichiamo **con le stesse regole, senza ritaratura**, alle aperture di **Francoforte, Londra e Tokyo**, per diversificare in fusi diversi.
- **Già visto**:
  - nulla su queste combinazioni;
  - il dossier dice che l'IM (strategia diversa) non ritarato è morto su GER40 e oro;
  - l'EA contiene un calendario Xetra: **se Manu ha già provato l'ORB su GER40, il paniere EUROPA viene promosso solo se supera i cancelli anche senza GER40** (domanda da fare a Manu insieme ai risultati).
- **Potenza, dichiarata ora: è bassa**:
  - lo stesso ORB su US100 nella sola finestra 2021-2023 avrebbe t 1,13 (p 0,13), cioè sarebbe NULLO con queste regole;
  - con costi in R più alti sugli altri strumenti, anche se l'ORB si trasferisse identico la potenza attesa è circa il 30-40% per EUROPA e circa il 10% per ASIA;
  - **un NULLO su ASIA non è informativo; un NULLO su EUROPA lo è solo in parte.**
- **Equivalenza con il tester** (US100 FTMO, 15/09/2021 → 29/12/2023, soglie fissate prima):
  - prima versione (solo bid): fallita sulla R media (0,220 contro 0,141), perché mancavano lo spread e il lato ask degli short;
  - versione corretta (lato ask = bid + spread storico; long all'ask, short al bid; stop e target riancorati al fill): stessa decisione **468/468**, stesso verso 100%, prezzo d'ingresso identico, **correlazione delle R 0,9999**, R media 0,159 contro 0,141 (la differenza è lo slittamento reale dei tick) → **superata**;
  - versione definitiva (questo codice: finestra d'ingresso [apertura+5', apertura+10') e regola del dato mancante a fine sessione): stessa decisione in 575 giorni su 577 (99,7%), stesso verso 100% sui 466 trade in comune, prezzo d'ingresso identico, correlazione delle R 0,9999, R media 0,144 contro 0,126 → **superata** (`risultati/EQUIV_US100.json`). I 2 giorni diversi (27/06 e 07/07/2022) sono esclusi dalla regola del dato mancante: nel file M1 FTMO le barre finiscono alle 22:07 server, mentre il tester aveva i tick fino alle 22:55.
- **Differenze dichiarate rispetto all'EA**: l'EA così com'è non può operare fuori dagli USA (ora server fissa 16:30, sessione di 390 minuti, calendari solo NYSE e Xetra, deviation in punti). Il test modella un EA corretto, con:
  - orari da `zoneinfo`;
  - durata della sessione per borsa;
  - calendari LSE, Xetra (aperta il lunedì di Pentecoste, come mostrano i dati, a differenza di `g_de_closed`) e Tokyo.
  - **Se un paniere è promosso, prima di F4 serve una nuova build con la sua equivalenza sul tester MT5 (GER40, UK100, JP225 FTMO)**: nessun EA esistente viene modificato.

## 1. Regole dell'ORB (congelate, dal sorgente)
1. **Candela 1** = barra M5 che inizia all'apertura della borsa cassa (barre M1 della finestra [apertura, apertura+5')).
2. **Filtri**:
   - range nullo → nessun trade;
   - doji (|close − open| < 5% del range) → nessun trade;
   - range < 12% dell'**ATR(14) D1** (media semplice di 14 true range delle barre D1 del giorno server, come iATR di MT5; ultima barra D1 completa) → nessun trade.
3. **Verso** = verso del corpo della candela 1.
4. **Ingresso**: prima barra M1 che inizia in [apertura+5', apertura+10'), come la finestra dell'EA. Un trade al giorno.
5. **Stop** = 10% dell'ATR, **target** = 8 × stop, riancorati al prezzo d'ingresso, sul server.
6. **Fine sessione**: 5 minuti prima della chiusura cassa, all'open della prima barra che inizia a quell'ora (entro 5 minuti). Se a fine sessione mancano barre (l'ultima è anteriore di oltre 5 minuti), il giorno è escluso come **dato mancante**.
7. **Esecuzione su barre M1** (bid; ask = bid + spread):
   - long all'ask, uscite al bid;
   - short al bid, uscite all'ask (stop e target valutati su high e low dell'ask);
   - stop prima del target nella stessa barra;
   - gap oltre il livello → open della barra.
8. **R** = (uscita − ingresso) × verso / distanza dello stop; include lo spread («R dopo lo spread»).

## 2. Borse, strumenti, dati
| Paniere | Strumento | Borsa | Apertura → fine sessione (locale) | Feed d'inferenza | Concordanza |
|---|---|---|---|---|---|
| **EUROPA** (primario) | GER40 | Xetra | 09:00 → 17:25 Francoforte | Pepperstone (11/06/2020) | FTMO (28/12/2021) |
| **EUROPA** (primario) | UK100 | LSE | 08:00 → 16:25 Londra | Pepperstone (06/06/2017) | FTMO (14/09/2021) |
| **ASIA** (primario) | JP225 | Tokyo | 09:00 → 14:55 Tokyo; dal 05/11/2024 → 15:25 | FTMO (13/09/2021) | — |
| USA-ALTRI (secondario) | US500, US30 | NYSE | 09:30 → 15:55 New York (mezze sedute 12:55) | Pepperstone (13/07/2020; 02/01/2018) | FTMO per US500 |

- **Esclusi a priori per costo** (cancello G1 del dossier, stimato prima dei numeri da ATR e tabella dei costi): spread mediano in R > 0,125 → **FRA40** (≈ 0,15 R) e **US2000** (≈ 0,21 R).
- **USA-ALTRI non è nella famiglia primaria**: apre allo stesso minuto dell'ORB US100 ed è leva sull'ORB, non diversificazione. È riportato come estensione descrittiva.
- **Calendari**:
  - Xetra: festivi della borsa, 24 e 31/12 esclusi, lunedì di Pentecoste aperto;
  - LSE: festivi inglesi, mezze sedute escluse;
  - Tokyo: festivi giapponesi + 31/12 e 1-3/01; il trade resta aperto nella pausa pranzo (il CFD quota);
  - NYSE: festivi e mezze sedute (elenco dell'EA, fino al 2026).
- **Dati**: copie sigillate < 2024; solo giornate M1.
- **Anomalia di fuso** (verificata da due revisori e da me): i feed Pepperstone sono in NY+8 fra novembre 2017 e febbraio 2018. **Si escludono le sedute dal 30/10/2017 al 16/03/2018** per tutti i feed Pepperstone; dopo la finestra resta il tempo per riscaldare l'ATR.
  - Nessun'altra anomalia è stata trovata sui feed di S3 (scansione mensile del picco d'apertura sul tick volume).
- **Hold-out** 2025-2026 mai toccato; **validazione 2024** solo per i promossi.

## 3. Costi FTMO (di oggi)
- **Spread**: tabella congelata `risultati/COSTI_S3.csv` (p75 FTMO 10/10/2025 → 09/10/2026 al minuto esatto ±2 dell'ingresso e della fine sessione), **× 1,14** per gli strumenti senza file M1BA (rapporto fra spread reale M1BA e campo SPREAD misurato su US100: 0,638 / 0,561).
  - US30: regola di S1/S2.
  - Uno spread costante per tutto il trade: quello d'ingresso; a fine sessione, quello del suo contesto.
- **Slittamento sulle uscite a livello** (stop e target): max(0,32 bps; 0,55 × spread d'ingresso in bps).
- **Commissioni**: 0 sugli indici [STIMA: misurato 0 solo su US100.cash; va verificato sul conto per gli altri simboli].
- **Stress**: simulazione rifatta con spread × 1,5 (anche nella logica di stop e target degli short), slittamento sui livelli × 2,5, +0,3 bps per ogni ordine a mercato.
- **Operabilità in F4**: uno strumento con costo medio (spread + slittamento) > 0,125 R è dichiarato «non operabile» anche se il paniere è promosso.

## 4. Test, cancelli, verdetto
- **Test primari: 2 panieri**, valore giornaliero = media delle R nette (dopo spread e slittamento) degli strumenti che fanno il trade quel giorno:
  - **EUROPA** (GER40, UK100);
  - **ASIA** (JP225).
- **Statistica**: t raggruppato per data (CR1, Student G−1), p unilaterale sulla media netta > 0. **BH q = 0,10 su 2.**
- **PROMOSSO** se tutte:
  - BH superata;
  - netto stress > 0;
  - netto > 0 in entrambe le metà (taglio alla data mediana);
  - ≥ 3 anni con ≥ 10 giorni e ≥ 60% di essi positivi;
  - almeno metà degli strumenti del paniere con netto > 0;
  - netto > 0 senza l'1% delle date più influenti;
  - concordanza: stesso segno sul feed FTMO, **stessi strumenti e stessi giorni**, se ci sono ≥ 100 giorni in comune.
- **Indipendenza G6** (per ogni paniere, liste del tester con date < 2024), sulla serie giornaliera dell'**unione dei giorni** (zero nei giorni senza trade):
  - correlazione con ORB P1 e con IM G;
  - quota di giorni con un trade nello stesso verso e con le posizioni aperte insieme all'ORB o all'IM.
  - **Soglie**: correlazione > 0,3 o quota > 50% → il paniere non conta come strategia nuova.
- **Verdetto**:
  - **S3 è valida** se almeno un paniere primario è PROMOSSO e ha G6 verde;
  - un paniere promosso con G6 rosso è una possibile estensione dell'ORB, con rischio congiunto, non una strategia nuova;
  - un INDIZIO non porta a nessuna ritaratura.
- **Secondari** (descrittivi):
  - R per strumento;
  - quote di uscite a stop, target e fine sessione;
  - R per anno;
  - costo medio in R (spread e slittamento);
  - USA-ALTRI;
  - **notizie**: quota di uscite a livello entro ±2 minuti da eventi ad alto impatto della valuta dell'indice o USD. Oltre il 2%, l'eventuale strategia va su conto Swing oppure richiede una regola «flat sulle news», da testare a parte.

## 5. Dopo
- Strategia = tutti gli strumenti operabili del paniere promosso.
- Nuova build dell'EA con la sua equivalenza.
- **Validazione 2024** una volta (p < 0,10 e netto stress ≥ 0), con la potenza dichiarata prima assumendo metà dell'effetto della scoperta.
- F4 con Monte Carlo congiunto con ORB e IM.
- Hold-out una volta.

## 6. Doppio controllo
- Controllo a mano di giornate campione: settimane disallineate (14/03/2022 e 31/10/2022 per l'Europa), JP225 in inverno (02:00 server) e in estate (03:00 server).
- Replica cieca dal protocollo, se un paniere risulta promosso o vicino alla soglia.
