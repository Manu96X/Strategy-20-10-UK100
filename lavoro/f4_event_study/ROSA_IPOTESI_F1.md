# ROSA DI IPOTESI (F1) — dopo la strategia FTSE e l'event study
*20/10/2026. Basata su: rapporto F3 (strategia del video bocciata), `RAPPORTO_EVENT_STUDY.md` (242 test pre-registrati, 0 superano la correzione), verifica avversaria e addendum «dopo i numeri». Etichette: [EVENT STUDY] numeri sul campione di scoperta < 2024 · [LETTERATURA] · [STIMA].*

## 0. Prima risposta: varianti della strategia FTSE — **nessuna raccomandabile**
- **Regola 2**: zero edge anche lordo, su ogni variante (k, uscita, tipo di barre) e anche «come il video», con posizioni sovrapposte (−0,06 R). Cercare altre soglie sarebbe solo data mining.
- **Regola 1** («Monday dip»): positiva ma debole e rara (12,7 trade l'anno).
  - La sua generalizzazione su 10 strumenti («lunedì in calo → martedì/mercoledì», famiglia E) non supera la correzione: miglior caso US500 +0,35 z, p 0,07.
  - Su GER40 non c'è.
- **Conclusione**: la strategia del video non ha un nucleo da salvare. Le ipotesi sotto vengono dall'event study e dalla letteratura.

## 1. Il quadro onesto
Su 10 strumenti e 7 famiglie di flussi a data nota (fine mese, FOMC, scadenze, festivi, lunedì, correlazioni, momentum) **nessun effetto supera la correzione** sul 2017-2023. Questo conferma la tua lezione: i CFD liquidi non regalano edge di calendario. Restano **indizi** coerenti con meccanismi noti, e un solo gruppo statisticamente forte: **il ritardo del dollaro**. Ogni ipotesi scelta si conferma **solo** sul 2024 (validazione) e sul 2025-2026 (hold-out), entrambi sigillati, oppure su **strumenti nuovi mai visti**.

## 2. Le ipotesi, in ordine di raccomandazione

### ⭐ H1 — Il dollaro segue con un giorno di ritardo metalli e azioni (correlazione fra strumenti)
| Voce | Contenuto |
|---|---|
| Evidenza | XAU oggi → USDX domani: pendenza −0,11/−0,12 z, t −3,8, **stesso segno in 5 anni su 5**, regge senza il 2020, con statistiche robuste e con ingressi ritardati; **p con 200.000 permutazioni 0,00059** (soglia della correzione 0,00041: manca di poco). Stesso segno con XAG (t −3,1), US500, GER40, UK100 e US100 → USDX (t da −1,8 a −2,3), e USDX → GER40/UK100 (+). [EVENT STUDY, verificato da un revisore] |
| Meccanismo (da provare) | il dollaro si riprezza in ritardo rispetto ai mercati globali di rischio e dei metalli; ipotesi: ribilanciamento delle coperture valutarie degli investitori esteri (vedi H4), eseguito nella sessione di New York del giorno dopo. Il revisore ha verificato che l'effetto sta nella sessione 08:20-16:00 NY del giorno dopo, quindi non è un prezzo stantio |
| Regola candidata | segnale alle 16:00 NY = media degli z di oggi di XAU e XAG (eventualmente + indici) → posizione sul dollaro per il giorno dopo: **short USD se metalli in salita** |
| Strumenti | DXY.cash su FTMO (dati FTMO solo dal 26/11/2024); meglio **EURUSD/GBPUSD/AUDUSD/USDCHF** (costo in R ~3 volte più basso) — **dati da caricare** |
| Frequenza | ~225 trade l'anno (uno al giorno) |
| Costo | DXY.cash ≈ 0,05 z per trade → netto base solo +0,02 z, stress −0,12 z. EURUSD ≈ 0,013 z (spread 0,13-0,16 pip + 2,5 $/lotto/lato) [STIMA] |
| Potenza sulla conferma | 2024-2026 ≈ 650 giorni → t atteso ≈ 2,7 se la pendenza resta −0,107 |
| Indipendenza | coppie e dollaro: possibile legame con RL (oro con filtro DXY) e gotobi (USDJPY), ma su orizzonte e meccanismo diversi; da misurare (servono i trade dei tuoi EA) |
| Perché non è bocciata | non è mean reversion tecnica, fix o RSI(2) sul forex, né relative value intraday: è una previsione **fra strumenti a un giorno** |
| **Punto debole** | meccanismo non dimostrato; dipende anche dai giorni di coda (senza il 2% dei punti più influenti p 0,075). **Test decisivo e pulito: le coppie forex 2017-2023, mai guardate** |

### H2 — Drift prima del FOMC sugli indici (modulo)
| Voce | Contenuto |
|---|---|
| Evidenza | anomalo +0,23 z su US100 (Welch p 0,02), +0,39 z su GER40 (p 0,02), +0,23 z su US500 (p 0,17), +0,04 su UK100; FTMO dello stesso segno su tutti (+0,26/+0,38) [EVENT STUDY, addendum]. Letteratura: Lucca-Moench 2015; Brusa-Savor-Wilson 2020 (effetto globale, solo per la Fed) [LETTERATURA] |
| Regola | long US100 (+ GER40) dalle 14:00 NY del giorno prima alle 13:55 NY del giorno FOMC |
| Frequenza / costo | 8 l'anno; costo ≈ 0,01 z |
| FTMO | **perfettamente conforme**: esce 5 minuti prima della notizia, una sola notte, mai il weekend |
| Potenza | ~22 eventi nel 2024-2026: conferma debole (t atteso ~1,5-2,5) |
| Ruolo | modulo aggiuntivo, non strategia da sola |

### H3 — Giorno prima dei festivi sugli indici (modulo)
| Voce | Contenuto |
|---|---|
| Evidenza | paniere dei 4 indici +0,17 z per evento, p 0,04 (addendum); segno positivo su tutti e 4 e su FTMO [EVENT STUDY]. Ariel 1990; Kim-Park 1994 [LETTERATURA] |
| Regola / frequenza | long dalla chiusura del giorno prima alla chiusura del pre-festivo; 6-9 eventi l'anno per indice |
| Ruolo | modulo, come H2 |

### H4 — Coperture valutarie di fine mese sul dollaro (Melvin-Prins 2015) — **nuova, mai testata**
| Voce | Contenuto |
|---|---|
| Meccanismo | i gestori esteri con azioni USA coperte ribilanciano la copertura a fine mese: se le azioni USA sono salite vendono dollari, alla fix delle 16:00 di Londra dell'ultimo giorno → il dollaro si muove in modo prevedibile. È un **flusso strutturale a orario noto** (§8), diverso da gotobi |
| Legame con H1 | è la spiegazione più plausibile del ritardo del dollaro |
| Strumenti / frequenza | DXY.cash o EURUSD; 12 eventi l'anno |
| Rischio | tu hai bocciato la «fix di Londra» sul forex: va chiarito se era questo segnale (prestazione relativa delle azioni nel mese) o la sola reversione alla fix |

### H5 — Lunedì in calo → recupero martedì-mercoledì (solo componente)
Dall'event study (E1/E2): US500 +0,35 z (p 0,07), UK100 +0,16 z (p 0,09), FTMO concorde; GER40 nullo. Coerente con la cella A2 della F3. **Debole**: lo metterei solo dentro un paniere «calendario» con H2 e H3.

## 3. Altre strade (dati, non ipotesi)
1. **Coppie forex Pepperstone M1 2017-2026** (EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF): sono il campione **nuovo e pulito** per H1 e H4.
2. **Più indici e strumenti** (US2000, JP225, HK50, AUS200, EU50): danno ampiezza ai panieri di H2, H3 e H5 e aumentano la potenza.
3. **Calendario economico MQL5 esportato** (64.986 eventi, con valori attesi ed effettivi): permette studi sulla sorpresa dei dati (CPI, NFP, PMI) e sui drift prima di BCE/BoE.
4. **Storia più lunga** (per esempio dati M1/D1 2005-2016 di un altro fornitore): la potenza dei moduli a bassa frequenza (H2, H3) sale molto (160 FOMC invece di 50).
5. **Trade dei tuoi EA**: servono per misurare l'indipendenza (G6) di qualunque ipotesi scelta.

## 4. Raccomandazione
- **H1, con i dati forex**: è l'unica con frequenza, potenza ed evidenza sufficienti per diventare una strategia vera. Si testa prima sulle coppie forex 2017-2023, mai guardate, poi sul 2024-2026 sigillato.
- In parallelo, opzionale: un **paniere «calendario»** H2 + H3 (+ H5) come modulo a bassa frequenza, conforme FTMO, da confermare sul 2024-2026.
- **H4** va scritta come protocollo insieme a H1, perché ne è il meccanismo candidato.
