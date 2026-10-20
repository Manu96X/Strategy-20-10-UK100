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
