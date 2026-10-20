# VERBALE DEL FORWARD ORB + MOMENTUM — SEDUTE 1→30 · FORWARD CHIUSO
*Documento cumulativo. Si aggiunge una sezione per seduta. Ultimo aggiornamento: 06/10/2026, §18 (sedute 26-30, secondo verdetto e doppio controllo del pacchetto). Autorevole insieme a `HANDOFF_ESECUTIVO_FORWARD_21-08-2026.md` (md5 `bdaa26ee0a58bfad838d0a28e01c6fe9`), che resta il verbale del pregresso 19–21/08.*

---

## 0. CUSTODIA — VERIFICA md5 (22/08/2026, prima azione)

**25 file su 25 del `MANIFEST_CUSTODIA_25_FILE.md` verificati: TUTTI COMBACIANO.** Nessuna divergenza, nessuna ri-codifica da adjudicare col contenuto. Verificato anche il manifest stesso (`ae6e11fee99cc8438002f66de988ce8f`) e il handoff guida (`bdaa26ee0a58bfad838d0a28e01c6fe9`) contro le impronte dichiarate da Manu nel messaggio di consegna.

| # | File | md5 calcolato | Esito |
|---|---|---|---|
| 1 | HANDOFF_ESECUTIVO_FORWARD_21-08-2026.md | bdaa26ee0a58bfad838d0a28e01c6fe9 | ✅ |
| 2 | HANDOFF_ORB_MOMENTUM_19-08-2026.md | 74e51911ad07bc314d9d6db0a197cec0 | ✅ |
| 3 | RISPOSTE_LACUNE_7_2_19-08-2026.md | 1341927184228cb5e63c0095a89db9de | ✅ |
| 4 | RISPOSTA_PER_CHAT_ORB_18-08-2026__1_.md | 016c37a8099db7a37a066723c08d5bf1 | ✅ |
| 5 | PASSAGGIO_AL_FUNDED.md | 40349962664c1251752956ca7b2aad2f | ✅ |
| 6 | ORB_US100_-_step15_O.mq5 | e970417c52a7f06baed94083d2d93ed0 | ✅ |
| 7 | ORB_US100_-_step14_N.mq5 | a1d3153393f4bab5c592922b37add8c1 | ✅ |
| 8 | IntradayMomentum_NAS100_D.mq5 | 1051f186b0f7df8f235b536b3c4012a0 | ✅ |
| 9 | IntradayMomentum_NAS100_C.mq5 | b9902df86982635aa0a1cd684864e1c3 | ✅ |
| 10 | ORB_trades_R_20212026.csv | 08ef75849302017c487afc36c9c65333 | ✅ |
| 11 | MOMENTUM_trades_R_20212026_FTMO.csv | a4d046494a856852b8f76e219e037626 | ✅ |
| 12 | Ultima_run.xlsx | 129574720905718b555ebbcf97a1fb7e | ✅ |
| 13 | Acceptance_O.xlsx | 21a5bb2fcb6d8a5faaa2207cadb5a267 | ✅ |
| 14 | T1_C.xlsx | 95a26d89f43e22134f128d7c17de4930 | ✅ |
| 15 | T1_D.xlsx | 280e494261bd33557ddd9d5db42cf06f | ✅ |
| 16 | T2_C.xlsx | 3e6b985ad73628ad92ec09897c083289 | ✅ |
| 17 | T2_D.xlsx | 3e9029a2a90d3c36ad3ed1cf72bafc93 | ✅ |
| 18 | T3_D.xlsx | 95a236f5e27876dcef0c77b6a840dc8c | ✅ |
| 19 | T3bis_D.xlsx | 821bfa813410f61537abae29746de1e5 | ✅ |
| 20 | 20260812.log | c7ccc3fdece5184636efa30525f10264 | ✅ |
| 21 | 20260813.log | 5ed468cb7d6b7ed2f38a818e79462dd7 | ✅ |
| 22 | 20260817.log | f4abf2a58a3674043838303c5b15b851 | ✅ |
| 23 | 20260818.log | 115eadcdb8fc9615aaeeacaf98f0b9ca | ✅ |
| 24 | 20260820_tester_diario.log | 6202d4d2210e43dca571a00b2c95c99e | ✅ |
| 25 | 20260820_journal_terminale.log | d33ace41d3a00ef649487f88214c1079 | ✅ |

**Nuovi in custodia (log e rapporti del forward, non nel manifest):**

| File | md5 | Righe |
|---|---|---|
| 20260821_experts.log | `f9235601b49d47bee369d661988962bd` | 8 |
| 20260821_journal.log | `b359b484c7a478fd77ded2d1b9643762` | 22 |
| ReportHistory_20260821.xlsx (CronoStoria) | `c8e747ae175ad282bd825724227622fa` | — |

### 0.1 Verifiche supplementari sul contenuto (non solo impronta)
- **Diff N→O riprodotto**: 10 righe marcate = `BUILD_ID` + `InpRiskMode`/`InpRiskFixedUSD` da `const` a `input` (default **invariati**: `RISK_BUFFER` / `300.0`) + 4 righe di commento. Nient'altro. Combacia col §2 del handoff.
- **Diff C→D riprodotto**: 10 righe esatte = header, `BUILD_ID`, `DAY_GUARD_CAP` 4400→**2000**, 3 righe di commento. Combacia.
- **Righe effettive**: `IntradayMomentum_NAS100_D.mq5` = **711** (712 dichiarate: off-by-one cosmetico già a verbale, confermato); `..._C.mq5` = 709 come dichiarato; ORB O = 1507, N = 1503.
- **Diario tester 20/08**: 23.769 righe ✅; riga `[IM] GUARDIA EQUITY: 97255 <= 100000-2000 — niente altri trade oggi` a `2022.01.24 17:30:45` ✅.
- **Ricostruzione indipendente delle 8 run del diario** (segmentando sulle righe di Init):

| Run | Build | Ingressi | Chiusure @22:55:00 | Giorni preparati |
|---|---|---|---|---|
| 1 | ORB 08-18-O | — | 3 (EoD via TIMER) | — |
| 2 | IM 08-13-C | 90 | 41 | 147 |
| 3 | IM 08-19-D | **90** | 41 | 147 |
| 4 | IM 08-13-C | 633 | 288 | 1204 |
| 5 | IM 08-19-D | **633** | 288 | 1204 |
| 6 | IM 08-19-D | 1 | 0 | 1 |
| 7 | IM 08-19-D | 1 | 0 | 1 |
| 8 | IM 08-19-D | 2 | 0 | 1 |

  Conferma indipendente di: **T1 90≡90**, **T2 633≡633**, **T3 eseguito due volte con esito identico** (determinismo), **T3-bis con esattamente 2 ingressi** (il terzo bloccato dalla guardia).

### 0.2 Due correzioni al §4 del handoff (cosmetiche, a verbale per tradizione)
1. Le occorrenze di `[IM] riavvio con posizione aperta di oggi: lasciata correre` nel diario sono **1.179**, non 1.178.
2. Le **288 chiusure alle 22:55:00 esatte** appartengono a **ciascuna delle due run T2** (run 4 e 5), non alla run T3. La sostanza — *OnTimer vivo nel tester* — resta vera e anzi rafforzata: l'ORB mostra in più 3 righe `[ORB] EoD via TIMER`, tutte a 22:55:00.

---

## 1. SEDUTA 1 — venerdì 21/08/2026 — **CERTIFICATA (1/15)**

Attesi pre-registrati PRIMA di aprire i log (file `ATTESI_SEDUTA1_PRE-REGISTRATI.md`).
Ora dei log = ora locale italiana = ora server −1.

### 1.1 Cancelli attesi → esito
| # | Atteso | Esito |
|---|---|---|
| A1 | Init `ORB 08-18-O`, buffer 5%, cap 1500 → **475$**/trade, baseline 100000.00 | ✅ letterale (14:34:33) |
| A2 | `=== Giorno 20260821 \| Open (server): 2026.08.21 16:30 \| Cut: 22:55 \| EqRef: 99497.56 ===` | ✅ letterale, ATR(D1) 475.53 |
| A3 | ENTRY **oppure** SKIP alle 15:35:0x, un solo trade | ✅ `ENTRY SHORT` alle **15:35:00.505** |
| A4 | Uscita per STOP / TP / EoD 21:55 | STOP HIT alle **17:36:12** → **EoD dal vivo ancora mai vista** |
| A5 | Nessun DAILY/TOTAL CAP, nessun TARGET | ✅ nessuno |
| A6 | Riga `SL/TP riallineati al fill` con slippage ≠ 0 | ❌ **ASSENTE** — vedi §1.3 |
| B1 | Init `IM 08-19-D` | ✅ (14:34:33) `point=0.01 tickval=0.01 minlot=0.01` |
| B2 | Riga `pronto` | ✅ `2026.08.21 pronto (IM 08-19-D): open=29384.2 prevClose=29215.0 sig17=0.360%` alle 15:30:00 |
| B3 | Eventuali ingressi IM (max 3) | **zero ingressi** — prezzo mai fuori banda ai check eseguiti |
| B4 | Prima riga del filtro news | non pervenuta: **nessun ingresso tentato**, il filtro non ha avuto occasione di parlare. Aperto invariato |
| B5 | Nessuna GUARDIA EQUITY / HALT / kill | ✅ nessuna |
| C2 | Un solo ORB e un solo IM caricati | ✅ `step15_O` su M5 + `IM_D` su M1, una sola volta |
| C3/C4 | `trading has been enabled`, mai `disabled`; nessun tocco 15:35–15:40 | ✅ |
| C1 | Terminale su 15:00 → 22:15 locali | ❌ **VIOLATO** — vedi §1.4 |

### 1.2 Il trade — quadratura al centesimo
```
buffer  = 5% × (99.497,56 − 90.000)          = 474,878 $
dist    = 10% × ATR(D1) 475,53               =  47,553 pt
lotti   = floor(474,878 / 47,553 ; 0,01)     =   9,98      [log: 9,98]   ✓
SL      = 29.278,03 + 47,553 = 29.325,583    → 29.325,58   [journal]     ✓
TP      = 29.278,03 − 8×47,553 = 28.897,606  → 28.897,61   [journal]     ✓
R prog. = 9,98 × 47,553                      = 474,58 $    [log: R$ 475] ✓
```
Filtri: `rangeC1 23,2% ATR` ≥ soglia 12% ✅ · `spread 1,45 pt` = **esattamente la mediana storica FTMO** ✅ · ingresso **al secondo** — 16:35:00 server, come in ogni seduta precedente ✅.

**Uscita**: stop colpito alle 17:36:12, `deal #503513040 buy 9,98 @ 29.325,58` = **esattamente il livello di SL** → **slippage sullo stop 0,00 pt** (2° campione dell'aperto n.7; il 1° era 0,33 pt).

### 1.3 IL RILIEVO DELLA SEDUTA — l'ancoraggio SL/TP al fill NON è scattato
**Fatto**: il log EA dichiara `fill 29278.03` e `slip 0.00 pt`. Il **Journal** dichiara `deal #503347578 sell 9.98 US100.cash at **29274.23**`.

- Slippage d'ingresso **reale = 3,80 pt** (sfavorevole), non 0,00.
- SL e TP sono rimasti calcolati sul prezzo **richiesto** (29.278,03), come dimostrato al centesimo dai due valori sul server (29.325,58 / 28.897,61 quadrano solo con 29.278,03).
- Manca la riga `[ORB] SL/TP riallineati al fill` — presente invece sul trade del 17/08. **È la firma diagnostica del mancato ancoraggio.**

**Conseguenze misurate**
| | Progettato | Reale |
|---|---|---|
| Distanza di stop | 47,55 pt | **51,35 pt** |
| Rischio del trade | 474,58 $ | **512,47 $** (+7,99%) |
| Perdita | −1,000 R | **−1,080 R** |
| TP in R effettivi | 8,00 R | **7,33 R** |

Perdita = 9,98 × 51,35 = **−512,47 $**. Extra imputabile allo slippage = 9,98 × 3,80 = **37,92 $ = 0,080 R**. Nessuna commissione (coerente col trade del 17/08: −502,44 su rischio ancorato 499,64 = solo differenza di prezzo).

**Meccanismo — nuova trappola 5.14, a verbale.**
In `TryEnter`, subito dopo `g_trade.Sell(...)`, l'EA chiama `GetMyPosition()` per leggere `POSITION_PRICE_OPEN`. L'ordine è stato eseguito **in 204,450 ms** e il `deal` compare nel journal a `15:35:00.506`, un millisecondo **dopo** la riga ENTRY dell'EA (`15:35:00.505`): la posizione **non era ancora nella cache del terminale**, quindi `haveF = false`, `fill = ResultPrice()` = prezzo **richiesto**, e l'intero blocco `if(InpAnchorSLToFill && haveF)` è stato **saltato in silenzio**.
È la terza manifestazione della famiglia 5.3: *il campo `slip` del log non è una misura, è un artefatto*. Il corollario del handoff — **lo slippage si misura solo incrociando log e CronoStoria/Journal** — è confermato dal vivo per la seconda volta.
**Non è un bug nuovo del codice: è una condizione di gara che rende la correzione 5.3/5.4 intermittente.** Il 17/08 era scattata, il 21/08 no.

**Che cosa NON si fa adesso**: non si tocca la build. Il divieto §13 (nessun cambio di parametri né di EA durante il forward) vale, e cambiare build a forward avviato azzererebbe il valore del test. La frequenza del fenomeno si misura trade per trade sulle 14 sedute rimanenti — la firma è la presenza/assenza della riga `SL/TP riallineati al fill` — e la decisione su un'eventuale build P si prende al verdetto del 12–13/09, prima dell'acquisto della challenge.

**Materialità**: uno sforo del +8,0% sul rischio per trade rientra nell'involucro già verbalizzato al §7 del handoff (*"'500 nominale / 1.000 massimo' è nominale, sforabile ~7% per costi"*). Il modello di rischio non si rompe. Ma **l'aperto n.4 non è verde**: il controllo richiesto ("rischio reale coincidente col voluto") è **fallito**, e questo è precisamente ciò che il forward doveva scoprire.

### 1.4 ANOMALIA DI UPTIME — seduta chiusa in anticipo
`19:40:13 System — terminal stopped due to system shutdown`. Il terminale si è spento **alle 19:40 locali**, contro l'obbligo di restare acceso e connesso **15:00 → 22:15**. Non è una sospensione né un crash di MT5: è uno spegnimento del sistema operativo.
**CAUSA ACCERTATA (dichiarata da Manu il 22/08): il PC è stato spento da lui.** Non è un difetto di configurazione: le correzioni del 13/08 hanno tenuto. È un errore di procedura, e come tale si corregge con la disciplina, non col software. Aperto chiuso.

**Danno materiale: nessuno.** L'ORB era già chiuso (17:36) e l'IM non aveva posizioni.
**Danno al test: sì.** I check semi-orari IM delle **20:00, 20:30, 21:00, 21:30 locali** (21:00–22:30 server) **non sono avvenuti**: 4 su 12 persi. La seduta 1 è quindi **certificata ma incompleta sul lato momentum**, e l'eventuale EoD delle 21:55 non poteva comunque essere osservata.
Le correzioni del 13/08 (sospensione *Mai*, coperchio *Non intervenire*, ore di attività 14:00–23:00) coprono sospensione e riavvii automatici, **non uno spegnimento**. Le 19:40 cadono dentro le ore di attività, quindi un riavvio automatico di Windows Update era già escluso: la causa va accertata.

### 1.5 Contabilità
| | |
|---|---|
| Bilancio inizio seduta | 99.497,56 |
| ORB | **−512,47** (1 trade, stop) |
| Momentum | **0,00** (nessun ingresso) |
| **Risultato seduta 1** | **−512,47 $** |
| Bilancio atteso a fine seduta | **98.985,09** — da confermare in CronoStoria |
| **Somma progressiva del forward** | **−512,47 $** |
| Conteggio | **seduta 1 di 15** · prossima: lun 24/08 · ultima: ven 11/09 |

*Nessun giudizio sui dollari intermedi (divieto §13). Il criterio pre-registrato — somma dei due EA ≥ 0 alla fine delle 15 sedute — si applica solo al verdetto del 12–13/09.*

### 1.6 Mappa degli aperti, aggiornata
| # | Aperto | Prima | Ora |
|---|---|---|---|
| 4 | Trade puliti ORB con CronoStoria-check | 1/3 | **2/3 — ma il check del 2° è FALLITO** (§1.3) |
| 5 | Prima EoD 22:55 dal vivo | mai vista | **mai vista** (stop alle 17:36; e comunque terminale spento alle 21:55) |
| 6 | Slippage d'ingresso | n=3: +2,10 / +2,84 / −0,50 | **n=4: +2,10 / +2,84 / −0,50 / +3,80** — media +2,06 pt, tutti e 4 misurabili solo via CronoStoria |
| 7 | Slippage sullo stop | n=1: 0,33 pt | **n=2: 0,33 / 0,00 pt** |
| 7.1.4 | Interferenza fra le guardie | non osservata | non osservabile (IM fermo, ORB chiuso presto) |
| — | Prima riga del filtro news | attesa | ancora attesa (nessun ingresso IM tentato) |
| 10 | Regime 2026 | watch permanente | invariato — 1 trade non è un dato |
| **NUOVO** | **5.14 — ancoraggio SL/TP intermittente per condizione di gara** | — | **CONFERMATO dalla CronoStoria (§1.7); frequenza da misurare ogni trade** |
| **NUOVO** | Uptime: spegnimento del PC in seduta | — | **CHIUSO**: PC spento da Manu, errore di procedura |
| **NUOVO** | **R1 — un riavvio in seduta azzera i riferimenti dei freni giornalieri di ENTRAMBI gli EA** | — | **aperto, mitigazione operativa** (Piano §3) |
| **NUOVO** | **R2 — baseline su GlobalVariable, vulnerabile alla sincronizzazione VPS** | — | **aperto, si chiude con 2 parametri** (Piano §3) |
| **NUOVO** | **R3 — interferenza freni IM→ORB in config challenge** | non quantificata | **QUANTIFICATA** (Piano §4) |

### 1.7 CRONOSTORIA DEL 21/08 — IL RIANCORAGGIO NON È SCATTATO: PROVA DEFINITIVA
CronoStoria consegnata il 22/08 (`ReportHistory1514282053.xlsx`, md5 `c8e747ae175ad282bd825724227622fa`, generata 2026.08.22 15:19).

**Confronto fra la riga *Ordini* e la riga *Posizioni* — è la firma decisiva:**

| Trade | Ordine inviato con S/L – T/P | Posizione risultante S/L – T/P | Riancoraggio |
|---|---|---|---|
| 17/08 (build N) | 30161.25 – 29630.93 | **30161.75 – 29631.43** | ✅ **avvenuto** (PositionModify) |
| 21/08 (build O) | 29325.58 – 28897.61 | **29325.58 – 28897.61** | ❌ **MAI avvenuto** |

Sul 21/08 i due valori sono **identici**: nessuna `PositionModify` è stata inviata. Prova materiale, non inferenza.

**Prezzo di apertura della posizione = 29.274,23** (riga *Posizioni*), mentre il log EA aveva stampato `fill 29278.03`. Poiché `POSITION_PRICE_OPEN` valeva 29.274,23, se l'EA l'avesse letto avrebbe (a) stampato 29274.23 e (b) calcolato `slWanted` = 29.321,78 ≠ 29.325,58, quindi la modify sarebbe partita. Non è successo né l'uno né l'altro. **Resta in piedi una sola spiegazione: `GetMyPosition()` ha restituito `false`** — la posizione non era ancora nella cache del terminale — e l'EA è ricaduto su `ResultPrice()`, che su FTMO è il prezzo **richiesto** (trappola 5.3). **Ipotesi (a) del §1.3 confermata, ipotesi (b) esclusa.**

**Quadratura al centesimo, tutto confermato:**

| | Valore |
|---|---|
| Apertura posizione | 29.274,23 (contro 29.278,03 nel log) → slippage **3,80 pt** |
| Chiusura | 29.325,58 = **esattamente lo S/L** → slippage sullo stop **0,00 pt** |
| Commissioni / Swap | **0,00 / 0,00** → nessun costo oltre il prezzo (confermato anche sul trade del 17/08) |
| Profitto | **−512,47** — identico al valore pre-calcolato prima di ricevere il file |
| Bilancio | **98.985,09** — identico al pre-calcolo |
| Commento d'ordine | **`ORB 08-18-O`** → prova che gira la build giusta (regola 5.9) ✅ |

Confermato anche il trade del 17/08: apertura 30.102,83, chiusura **30.162,08** contro S/L 30.161,75 → slippage sullo stop **0,33 pt**; perdita 8,48 × 59,25 = **−502,44** ✓; commento `ORB 08-13-N` ✓.

---

## 2. ERRORI A VERBALE DI QUESTA CHAT
Emersi nella riverifica del 22/08 chiesta da Manu, che non era convinto dei rilievi. **Aveva ragione su due punti su tre.**

1. **Gravità di R1 sovrastimata.** Avevo scritto che con due riavvii in una giornata si sfonda il limite giornaliero FTMO. Falso: il kill-switch del momentum è **senza stato** (`DayStats` ricalcola da `HistorySelect` sullo storico del server) e sopravvive a qualunque numero di riavvii, cappando l'IM a ~−2.500$ realizzati. Peggior caso reale ≈ **−3.580$** contro −5.000. Il rilievo resta come degrado di margine (da ~2.500 a ~1.400), non come rischio di breccia.
2. **Magnitudine di R3 sovrastimata.** I "+11,2R esposti" sono un limite superiore condizionato a un'ipotesi sfavorevole sul flottante ORB. Guardando i tempi, 3 casi su 4 hanno il freno che scatterebbe a ridosso dell'EoD su trade da ~+1,4R: costo una frazione di R. Avrei anche dovuto dichiarare in v1 due limiti del metodo (flottante IM non modellato; traiettorie dell'IM da solo).
3. **Errore di metodo.** Ho chiesto a Manu di scegliere il criterio del verdetto (A/B/C) **prima** di aver misurato quanto vale lo scorporo dell'opzione B (68–380$) e se prolungare il forward serva (no: 15→30 sedute guadagna 5 punti e costa ~8 punti di P(funded ≤6m)). Erano due conti da mezz'ora e cambiano la scelta. La decisione va rifatta finché siamo ciechi.

4. **Atteso di acceptance incompleto** (25/08). Avevo pre-registrato *"esattamente 79"* e *"esattamente 181"* differenze; sono 80 e 182. La differenza in più è l'aggiornamento automatico del terminale MT5 da build 6090 a 6140, che compare nell'intestazione del rapporto. Non prevedibile, ma l'atteso era comunque errato. Dettagli e conseguenze in §4.5.

Nessuno dei quattro tocca la trappola **5.14**, che è confermata con prova tripla (§1.7).

---

## 3. PROSSIMA AZIONE
**Richiesta a Manu (una sola)**: esportare la **CronoStoria del 21/08** in XLSX e consegnarla. Serve a (a) confermare al centesimo la perdita di 512,47 e il bilancio 98.985,09, (b) leggere il **prezzo di apertura della posizione** e distinguere in modo definitivo fra le due meccaniche possibili del §1.3 (posizione non ancora in cache → `ResultPrice()`, oppure `POSITION_PRICE_OPEN` letto pari al richiesto), (c) chiudere il controllo dell'aperto n.4 sul secondo trade.

**Istruzione operativa, non negoziabile per le 14 sedute rimanenti**: terminale acceso e connesso **15:00 → 22:15 italiane**, PC attaccato alla corrente, nessuno spegnimento. Un'anomalia si fotografa e si annota, non si tocca.

---

## 4. ACCEPTANCE DELLE BUILD P ed E — 25/08/2026 — **VERDE**

### 4.1 Custodia
| File | md5 |
|---|---|
| `TP_ORB.xlsx` | `6c6531bd6e55c20fd5701e1dc9649399` |
| `TE_IM.xlsx` | `3f5f228ae69a5e0dae5380fab349cc82` |
| `20260825.log` (diario tester, UTF-16, 2.140 righe) | `b799c0a76569d4cc771e058b51d8cc8c` |

### 4.2 Parametri delle due run — verificati uno per uno nel diario, **tutti esatti**
**T-P**: `ORB_US100_-_step16_P.ex5` · US100.cash M5 · 2021.09.15→2021.12.31 · *generating based on real ticks* · 100.000 USD 1:100 · `InpTargetBufferUSD=500` (unico modificato) · `InpRiskMode=2` (buffer) · tutti gli altri ai default. Init stampato: **`ORB 08-22-P`**, `BUFFER 5.00% x (equity-90000), cap 1500$ -> 500$ per trade`.
**T-E**: `IntradayMomentum_NAS100_E.ex5` · US100.cash M1 · 2022.06.01→2022.12.31 · *1 minutes OHLC ticks generating* · 100.000 USD 1:100 · `InpDSTMode=0`, `InpRiskDollars=500`, tutti default. Init stampato: **`IM 08-22-E`**.

### 4.3 Confronto cella per cella — esito

**T-P vs `Acceptance_O.xlsx`** — stesso foglio, stesse dimensioni (240×14), **1958 celle piene in entrambi**.

| Differenze | Quante | Pre-registrata? |
|---|---|---|
| commento di build `ORB 08-18-O` → `ORB 08-22-P` | **78** (= 39 trade × 2) | ✅ sì |
| nome Expert `..._step15_O` → `..._step16_P` | **1** | ✅ sì |
| **`FTMO-Demo (Build 6090)` → `FTMO-Demo (Build 6140)`** | **1** | ❌ **no** — vedi §4.5 |
| **qualunque altra cella** | **0** | — |

Riscontri diretti: **39 operazioni** · profitto netto **10.512,60** → bilancio **110.512,60** · ultimo affare **2021.11.17 16:51:38** · commento dell'ultimo ingresso **`ORB 08-22-P`**.

**T-E vs `T1_D.xlsx`** — stesse dimensioni (441×14), **4067 celle piene in entrambi**.

| Differenze | Quante | Pre-registrata? |
|---|---|---|
| tag di build `IM 08-19-D` → `IM 08-22-E` | **180** (= 90 trade × 2) | ✅ sì |
| nome Expert `..._D` → `..._E` | **1** | ✅ sì |
| build del terminale 6090 → 6140 | **1** | ❌ no |
| **qualunque altra cella** | **0** | — |

**90 operazioni** · profitto netto **6.571,94**.

### 4.4 Prova supplementare, più forte del confronto XLSX: **diff riga per riga dei diari**
Estratti i messaggi con data simulata dalle run di acceptance, normalizzando **solo** il BUILD_ID e il nome del file:

| | Righe confrontate | **Righe diverse** |
|---|---|---|
| ORB — build O (20/08) vs build P (25/08) | 533 vs 533 | **0** |
| Momentum — T1 build D (20/08) vs build E (25/08) | 1.384 vs 1.384 | **0** |

Zero. Ogni timestamp simulato, ogni prezzo, ogni lotto, ogni ordine, ogni riga di sistema: identici. **La build P è la build O e la build E è la build D, in backtest, alla riga.**

Contabilità di controllo dell'ORB: **39 ingressi = 35 STOP HIT + 3 `EoD via TIMER` + 1 `TARGET DI FASE RAGGIUNTO`** — e le 3 chiusure EoD via timer sono esattamente le 3 della run O del 20/08. Slippage nel tester **0,00 su 39 ordini** (esecuzione ideale, come deve essere); spread medio all'ingresso 0,44 punti indice.

### 4.5 L'ottantesima differenza: il terminale si è aggiornato da solo — **errore mio di pre-registrazione**
Avevo dichiarato *"esattamente 79"* e *"esattamente 181"*. Sono **80** e **182**. La differenza in più è la stessa in entrambi i file: la riga 2 del rapporto, **`FTMO-Demo (Build 6090)` → `FTMO-Demo (Build 6140)`**. MT5 si è aggiornato fra il 20/08 e il 25/08.

Non potevo prevederlo, ma l'atteso era comunque sbagliato e va a verbale come **errore n.4 di questa chat**. La sostanza non è toccata: la differenza è **nell'ambiente, non nell'EA**, e il fatto che *tutte* le altre celle e *tutte* le 1.917 righe di diario siano identiche la dimostra innocua.

Anzi, è un cancello superato gratis che non avevamo previsto: **i risultati sono riproducibili attraverso un aggiornamento del terminale MT5.**
**Ma va annotato**: il terminale **live** è ora su build 6140 mentre la seduta 1 girava su 6090. Nel tester l'aggiornamento è provato innocuo; nel **live** il percorso d'esecuzione — invio dell'ordine e aggiornamento della cache delle posizioni — potrebbe comportarsi diversamente, ed è esattamente il meccanismo della trappola 5.14. Variabile da tenere a verbale.

### 4.6 Le 90 righe `failed modify … [Invalid stops]` del momentum: **pre-esistenti, innocue**
Sono esattamente **90 nella run D del 20/08 e 90 nella run E di oggi** — una per ingresso — e compaiono in *ogni* run del momentum mai fatta (633 per le run intere, 1 per ciascun T3, 2 per T3-bis). Causa: nel tester lo slippage è nullo, quindi `slNew` coincide con lo stop già presente e il server rifiuta una modifica che non cambia nulla. L'ORB non produce questo rumore perché ha una guardia (`if(|slWanted − sl| > tick)`) che il momentum non ha. **Nessun effetto sui risultati. Non introdotte dalla build E.**

### 4.7 **CORREZIONE IMPORTANTE AL CANCELLO 1(e) DEL CRITERIO D**
Questa scoperta cambia come si legge il forward, e va corretta **adesso**.

Avevo scritto: *«la riga di riancoraggio deve comparire su OGNI ingresso; una sola assenza è rosso»*. **È sbagliato.** In entrambi gli EA la riga viene stampata **solo se il riancoraggio ha davvero spostato lo stop**, cioè solo se lo slippage è di almeno un tick. Con slippage nullo — che dal vivo capita — il riancoraggio funziona benissimo e **non stampa niente**. Il criterio come scritto avrebbe prodotto falsi rossi.

> **Formulazione corretta del cancello 1(e)** — sostituisce la precedente:
> - **ROSSO** se compare anche una sola volta `*** ATTENZIONE: posizione NON leggibile dopo l'invio ***` (ORB o IM). È la riga aggiunta dalle build P/E: è inequivocabile e prima non esisteva.
> - **ROSSO** se, incrociando log e CronoStoria, un ingresso ha slippage reale ≥ 0,01 e **manca** la riga di riancoraggio.
> - **VERDE** altrimenti. L'assenza della riga con slippage nullo è il comportamento corretto.
> - Segnale positivo da contare a parte: `[ORB] posizione visibile dopo attesa: riancoraggio possibile (fill …)` compare **solo** quando la prima lettura fallisce e l'attesa la risolve — cioè è **la prova diretta che la correzione ha lavorato**.

---

## 5. SEDUTE 2 e 3 — lun 24/08 e mar 25/08 — **CERTIFICATE (3/15)**

Custodia: `20260824_experts` `9d2f…` / `20260824_journal` / `20260825_experts` / `20260825_journal` (UTF-16, consegnati il 25/08).

### 5.1 IL FATTO STORICO — **il momentum ha eseguito il suo primo ordine dal vivo**
`24/08 15:59:59.825 — [IM] entry SHORT lots=4.48 dist=111.6` · ordine #526479820 eseguito in **232,385 ms** · deal #504691230 **sell 4.48 @ 28.943,03**.
Sizing esatto: `500 / 111,6 = 4,4803 → 4,48 lotti` → rischio nominale **500,00 $** al centesimo. Cap notional non vincolante (4,48 « 13,82). Stop protettivo a 2×dist → `sl 29.167,48`.
**Cancello 1(a) del criterio D: 1 ordine su 3 richiesti.**

### 5.2 I TRE TRADE, AL CENTESIMO

| | ORB 24/08 | IM 24/08 | ORB 25/08 |
|---|---|---|---|
| ATR(D1) · dist | 452,03 · 45,203 | — · 111,6 | 409,71 · 40,971 |
| Rischio target | 5%×8.985,09 = **449,25** | **500,00** | 5%×7.532,65 = **376,63** |
| Lotti | 9,93 ✓ | 4,48 ✓ | 9,19 ✓ |
| Prezzo **richiesto** (log) | 29.035,33 | 28.944,28 | 29.301,48 |
| Prezzo **eseguito** (journal) | **29.035,03** | **28.943,03** | **29.300,98** |
| **Slippage reale** | **+0,30** | **+1,25** | **−0,50** (favorevole) |
| `slip` stampato dall'EA | 0.00 | — | 0.00 |
| Riga di riancoraggio | **ASSENTE** | **ASSENTE** | **ASSENTE** |
| Tempo di esecuzione | 206,218 ms | 232,385 ms | 215,586 ms |

Verifiche di coerenza: SL e TP di ogni trade quadrano **solo** col prezzo richiesto (ORB 24/08: `29.035,33 + 45,203 = 29.080,53` ✓ e `− 8×45,203 = 28.673,71` ✓; ORB 25/08: `29.301,48 − 40,971 = 29.260,51` ✓ e `+ 8×40,971 = 29.629,25` ✓). **Il riancoraggio non è mai avvenuto.**

### 5.3 LA TRAPPOLA 5.14 È QUASI SISTEMATICA — **1 successo su 5**

| Data | Build | Riancoraggio | Slippage |
|---|---|---|---|
| 17/08 | ORB N | ✅ **scattato** | −0,50 |
| 21/08 | ORB O | ❌ | +3,80 |
| 24/08 | ORB O | ❌ | +0,30 |
| 25/08 | ORB O | ❌ | −0,50 |
| 24/08 | **IM D** | ❌ | +1,25 |

**Con la build O: 0 su 3. Con l'IM: 0 su 1, al primo ordine della sua vita** — esattamente come previsto per costruzione il 22/08. La regola pre-registrata (`k/n ≥ 1/3` → build P/E) è **superata di slancio**: k/n = 4/5 = 80%.
Serie slippage d'ingresso ORB, n=6: +2,10 / +2,84 / −0,50 / +3,80 / +0,30 / −0,50 → **media +1,34 pt**. Slippage sullo stop, n=3: 0,33 / 0,00 / 0,88 → media 0,40 pt.

### 5.4 IL PC SPENTO CON DUE POSIZIONI APERTE — il rilievo più serio
`24/08 16:17:07 — experts removed, terminal shutdown`. In quel momento erano aperte **entrambe** le posizioni (ORB short 9,93 e IM short 4,48). Alla riaccensione del 25/08 alle 11:02:46 il terminale sincronizza **`0 positions`**: si sono chiuse entrambe a terminale spento.

Entrambe erano protette dallo **stop sul server** ✓. Ma **nessuna delle due chiusure gestite dall'EA era possibile**: né l'EoD 22:55 dell'ORB, né l'uscita di banda o l'EoD del momentum. Il momentum, senza terminale, **non ha alcuna uscita se non lo stop a −2R**.

**Ricostruzione dai bilanci** (98.985,09 → 97.532,65 = **−1.452,44**):
- ORB stoppato a 29.080,53 → 9,93 × 45,50 = **−451,82**
- IM stoppato a 29.167,48 → 4,48 × 224,45 = **−1.005,54**
- somma dei prezzi = −1.457,36 · **osservato −1.452,44** · differenza **+4,92 $**

Quei 4,92$ di scarto sono compatibili con uno **swap positivo su due posizioni short** (0,34 $/lotto su 14,41 lotti). Lo swap si applica al rollover di mezzanotte: **indizio forte che le due posizioni siano rimaste aperte tutta la notte**. Da confermare con la CronoStoria — è l'unica fonte che dà ora e prezzo di chiusura e la voce swap separata.

Se confermato, il costo non è lo stop in sé ma **l'EoD mancata**: l'ORB avrebbe chiuso alle 22:55 al prezzo di allora invece che allo stop, e la posizione è rimasta esposta al gap nella finestra dei 76 minuti senza quotazioni.

### 5.5 R1 OSSERVATO DAL VIVO — il riferimento del freno giornaliero si sposta a ogni riavvio
Il 25/08 l'ORB ha stampato l'intestazione della giornata **tre volte**, con `EqRef` diverso ogni volta:
`11:02:47 → EqRef 97.532,65` · `17:22:03 → EqRef 97.152,64` · `19:07:38 → EqRef 97.152,64`.
È **esattamente** il rilievo R1: `g_dailyRefEq` si riassegna all'equity corrente a ogni reinizializzazione, e con lui il freno giornaliero riparte da zero. Lo stesso vale per `g_dayStartEq` del momentum, che il 25/08 ha ristampato `pronto` a ogni riavvio. Innocuo quel giorno (nessuna posizione aperta), ma **il rilievo passa da teorico a osservato**.

### 5.6 Il messaggio `riavvio con posizione aperta di oggi: lasciata correre` è **fuorviante**
Compare il 24/08 alle 16:00:11, dodici secondi dopo l'apertura della posizione IM — e **non c'era stato alcun riavvio**. Il codice lo stampa al primo `OnTimer` che vede una posizione del giorno con `g_keepAliveLogged==false`, cioè **sempre, alla prima apparizione di una posizione**. Spiega anche le 1.179 occorrenze nel diario del tester. **Non è un segnale di anomalia: va letto come "c'è una posizione aperta e la lascio correre".** A verbale per non spaventarsi in futuro.

### 5.7 Contabilità

| Seduta | Data | ORB | IM | Risultato | Bilancio |
|---|---|---|---|---|---|
| 1 | 21/08 | −512,47 | 0 | **−512,47** | 98.985,09 |
| 2 | 24/08 | −451,82 | −1.005,54 | **−1.452,44** *(incl. ~+4,92 swap)* | 97.532,65 |
| 3 | 25/08 | −380,01 | 0 | **−380,01** | 97.152,64 |
| | | | | **progressivo −2.344,92** | |

**Veto di regime del criterio D: ≥ −5.000 $. Siamo a −2.344,92 con 12 sedute da giocare.**

### 5.8 UPTIME — **il cancello 1(d) è già matematicamente perso. Errore mio.**

| Seduta | Terminale acceso | Buco | Check IM persi |
|---|---|---|---|
| 1 (21/08) | 14:34 → **19:40** | 2h35 | 4 su 12 + EoD |
| 2 (24/08) | 15:28 → **16:17** | 5h58 | **11 su 12 + EoD, con 2 posizioni aperte** |
| 3 (25/08) | 11:02 → 17:41, 19:07 → … | 1h26 | 3 su 12 |

Tre sedute su tre incomplete. Il cancello chiedeva **≥13 sedute piene su 15**: restano 12 sedute, quindi **il massimo raggiungibile è 12 < 13**. Il cancello è impossibile da superare, e non per colpa degli EA.

**ERRORE MIO, il quinto**: ho fissato "13 su 15" il 22/08 senza fare il conto, quando la seduta 1 era **già** compromessa — mi restava un margine di 1 su 14. Una soglia scritta senza aritmetica.

> **Riformulazione del cancello 1(d)** — più severa in sostanza, non più permissiva. L'uptime non è un fine: è lo strumento per raccogliere le osservazioni dei cancelli 1(a) e 1(b). Quindi:
> **1(d) nuovo**: le osservazioni che soddisfano 1(a) (≥3 ordini IM) e 1(b) (≥1 EoD 22:55) devono provenire da momenti in cui **il terminale era acceso quando l'evento è avvenuto**. Se all'11/09 quei due cancelli non sono soddisfatti, **il forward si prolunga finché non lo sono**. Non si abbassa l'asticella: si continua a misurare.
> Sparisce il conteggio arbitrario "13 su 15", che misurava la disciplina invece della macchina.

### 5.9 DECISIONE SULL'UPTIME — 25/08/2026: **si resta sul PC**
Messa sul tavolo l'anticipazione del VPS per le 12 sedute rimanenti (~15$, uptime risolto per costruzione, latenza misurata dal journal del 24/08 a **1,77 ms via 'VPS London LD6 25' contro i 75,96 ms attuali**). **Manu sceglie di restare sul PC con disciplina ferrea.** Motivazione a favore: nessuna variabile nuova nel forward, coerenza col handoff (*«VPS NON si usa nel forward»*). Decisione registrata, non si riapre.

Conseguenza: le 12 sedute rimanenti dipendono interamente dalla procedura. Tutte e tre le interruzioni finora sono state **spegnimenti volontari**, non guasti: le correzioni del 13/08 (sospensione *Mai*, coperchio *Non intervenire*) hanno tenuto. Il rimedio è quindi procedurale.

> **PROTOCOLLO DI SEDUTA — cinque righe, da qui all'11/09**
> 1. **14:50** — accendi MT5. Verifica: spia verde in basso a destra · **Algo Trading verde** · due EA sui grafici con **icona blu**.
> 2. **15:35–15:40** — mani giù. Non toccare nulla, per nessun motivo.
> 3. **Fino alle 22:15** — non chiudere MT5, non spegnere il PC. **Il PC lo puoi usare per altro**: MT5 lavora da solo in secondo piano, non serve guardarlo.
> 4. **22:15** — apri la scheda **Strumenti → Trading**. Se è vuota, puoi chiudere. **Se c'è una posizione aperta, NON chiudere.**
> 5. **REGOLA D'ORO — quella che mancava**: *prima di spegnere, guarda sempre la scheda Trading.* Il 24/08 era l'unica cosa che serviva.
>
> Nota diagnostica sul punto 4: alle 22:15 il conto **deve** essere piatto, perché l'EoD chiude tutto alle 21:55. Se alle 22:15 trovi ancora una posizione, non è una svista tua: è un'anomalia dell'EA. Screenshot, log, e me lo dici.
> Se sei costretto a spegnere in seduta con una posizione aperta, **dimmelo**: quella seduta va marcata come osservazione non valida, non nascosta.

---

## 6. CRONOSTORIA DEL 25/08 — quello che è successo davvero il 24/08
CronoStoria consegnata il 25/08 alle 19:21 (md5 `a37ba601a4cf36848d4d37ddb4639872`).

### 6.1 Le due posizioni del 24/08 hanno avuto destini opposti

| | ORB | **Momentum** |
|---|---|---|
| Apertura | 24/08 **16:35:00** sell 9,93 @ 29.035,03 | 24/08 **17:00:00** sell 4,48 @ 28.943,03 |
| S/L – T/P | 29.080,53 – 28.673,71 | 29.167,48 – **nessun T/P** |
| Chiusura | 24/08 **18:37:52** @ 29.079,98 | **25/08 08:56:52** @ 29.167,88 |
| Durata | 2 h 03 | **15 h 57 — TUTTA LA NOTTE** |
| Swap | 0,00 | **1,24** |
| Risultato | **−446,35** | **−1.006,09** netti |

L'ORB si è chiuso da solo allo stop **con il PC già spento** (16:17 locale = 17:17 server): il server ha eseguito, come da disegno 5.5. Il momentum invece **è rimasto short per sedici ore**, ha attraversato il rollover di mezzanotte (da cui lo swap di 1,24) ed è uscito solo perché il mattino dopo il prezzo è arrivato al suo stop protettivo.

### 6.2 **Spegnere il PC è costato denaro. Dimostrazione, non stima.**
Il momentum chiude a mercato: rientro in banda o **EoD alle 22:55 server**. Entrambe richiedono il terminale acceso. Alle 22:55 del 24/08 il terminale era spento da cinque ore e mezza.

La posizione ha resistito fino alle **08:56:52 del 25/08**: ne segue che **in nessun istante prima di quell'ora il prezzo aveva toccato 29.167,48**. Quindi alle 22:55 del 24/08 il prezzo era **strettamente sotto** il livello di stop, e l'EoD avrebbe chiuso a un prezzo **necessariamente migliore**.

- Perdita subita: **−1.006,09** (= −2,01R, lo stop protettivo pieno)
- Perdita che l'EoD avrebbe prodotto: **strettamente minore**, di quantità ignota
- Limite superiore del risparmio mancato: se alle 22:55 il prezzo fosse stato al livello delle 18:37 (29.080), l'EoD avrebbe chiuso a **−783 $** invece di −1.006 → **~223 $ persi**; se fosse stato più in basso, di più.

Non è tutto: il backtest chiude **sempre** alle 22:55. Una posizione lasciata overnight **non è nel modello**. Ha attraversato la finestra dei 76 minuti in cui il CFD non quota, esposta a un gap che nessuna guardia poteva fermare. Quella notte è andata bene. **La statistica su cui poggia tutto il progetto non contempla quel rischio.**

### 6.3 Asimmetria strutturale, a verbale
Nella riga della posizione il momentum ha il campo **T/P vuoto**: quel sistema non usa take profit. Conseguenza: **a terminale spento l'ORB è protetto in entrambe le direzioni** (stop *e* take profit sono sul server), **il momentum solo in perdita**. Se il prezzo fosse corso a suo favore, la posizione sarebbe rimasta aperta a correre senza alcuna uscita, indefinitamente. È una proprietà del disegno, non un difetto — ma va saputa.

### 6.4 TRAPPOLA 5.14 — prova materiale definitiva su tutti e cinque i trade
Confronto fra la riga **Ordini** (livelli inviati) e la riga **Posizioni** (livelli effettivi). Se il riancoraggio avviene, differiscono.

| Trade | Ordine S/L – T/P | Posizione S/L – T/P | Riancoraggio |
|---|---|---|---|
| 17/08 ORB N | 30161.25 – 29630.93 | **30161.75 – 29631.43** | ✅ **avvenuto** |
| 21/08 ORB O | 29325.58 – 28897.61 | 29325.58 – 28897.61 | ❌ |
| 24/08 ORB O | 29080.53 – 28673.71 | 29080.53 – 28673.71 | ❌ |
| **24/08 IM D** | **29167.48** | **29167.48** | ❌ |
| 25/08 ORB O | 29260.51 – 29629.25 | 29260.51 – 29629.25 | ❌ |

**1 su 5.** Prova materiale, non inferenza. E i commenti d'ordine (`ORB 08-13-N`, `ORB 08-18-O` ×3, `IM 08-19-D`) confermano quale build girava ogni volta — regola 5.9 rispettata.

### 6.5 **Ma la 5.14, finora, è costata 3,98 $**
Onestà dei conti. Sforo del rischio imputabile al mancato riancoraggio, trade per trade:

| Trade | Rischio progettato | Sforo 5.14 |
|---|---|---|
| 21/08 ORB | 474,58 | **+37,92** |
| 24/08 ORB | 448,87 | +2,98 |
| 24/08 IM | 999,94 | +5,60 |
| 25/08 ORB | 376,52 | **−4,60** *(slippage favorevole)* |
| | | **totale +41,90 $** |

Su 2.344,92 $ di perdite del forward, la trappola pesa **1,8%** — e senza il 21/08 pesa **4 $**. **Non è lei la causa delle perdite.** Va corretta perché è *sistematica* e perché un giorno arriverà un +3,80 pt con lotti doppi, non perché stia svuotando il conto. Il rilievo resta, l'allarme si ridimensiona.

### 6.6 Slippage sullo stop — **molto meglio dell'atteso**. Aperto n.7 quasi chiuso.

| Data | S/L | Eseguito | Scarto |
|---|---|---|---|
| 17/08 ORB short | 30.161,75 | 30.162,08 | +0,33 sfavorevole |
| 21/08 ORB short | 29.325,58 | 29.325,58 | 0,00 |
| 24/08 ORB short | 29.080,53 | **29.079,98** | **−0,55 favorevole** |
| 24/08 IM short | 29.167,48 | 29.167,88 | +0,40 sfavorevole |
| 25/08 ORB long | 29.260,51 | 29.259,63 | +0,88 sfavorevole |

Media **+0,21 pt = 0,47%** della distanza di stop, contro il **2,25%** atteso dal backtest (aperto n.7 del handoff). Su n=5 è ancora poco, ma l'esecuzione di FTMO sugli stop è finora **migliore** di quanto il modello assumesse.

### 6.7 Correzioni contabili al §5.7
I valori esatti dalla CronoStoria: ORB 24/08 **−446,35** (avevo scritto −451,82: si è chiuso 0,55 pt *meglio* dello stop) · IM **−1.006,09 netti** (−1.007,33 di prezzo, **+1,24 di swap**). La somma della seduta 2 resta **−1.452,44** e il progressivo **−2.344,92**: invariati.

### 6.8 Note minori
- Il primo ingresso del momentum dal vivo è caduto sul check delle **17:00 server = 10:00 ET**, cioè proprio la fascia dei dati macro USA che pesa il 29,9% dei suoi ingressi storici. **Nessuna riga `entry bloccata da news filter`**: il filtro non ha bloccato (lunedì, nessun dato high-impact a quell'ora). Aperto del filtro news ancora senza osservazioni.
- Cinque trade, cinque perdite. Nulla di anomalo: con win rate ORB 18,9%, quattro stop di fila hanno probabilità 43%.
- **L'EoD delle 22:55 dal vivo resta mai vista** (aperto n.5) — e il 24/08 è stata l'occasione mancata.

---

## 7. SEDUTA 4 — mercoledì 26/08/2026 — **CERTIFICATA (4/15)** — prima seduta con le build P ed E

Custodia: `20260826_experts` `810ffc82aa50b829092e3e8f6bdb57dc` · `20260826_journal` `990070938be2a8efa2854fafe070df5d` · `Cronistoria.xlsx` `73569da4edcff8c9b2c697cd6ab8ea4c`.

### 7.1 **LA CORREZIONE 5.14 HA FUNZIONATO. Prova diretta.**
```
15:34:59.697  deal #506694595 buy 8.95 @ 29185.28        (ordine eseguito in 260,841 ms)
15:34:59.754  [ORB] posizione visibile dopo attesa: riancoraggio possibile (fill 29185.28)
15:34:59.818  [ORB] SL/TP riallineati al fill: SL 29149.94 -> 29145.34 | TP 29509.43 -> 29504.83 (slippage 4.60 pt)
```
La riga **`posizione visibile dopo attesa`** è quella aggiunta dalla build P, e viene stampata **solo** quando la prima lettura della posizione fallisce e l'attesa la risolve. La sua presenza dimostra due cose insieme:
1. **la condizione di gara si è ripresentata** — con la build O questo sarebbe stato il **quinto** riancoraggio mancato di fila;
2. **l'attesa l'ha risolta**, in ~57 ms (un solo ciclo da 50 ms).

Il journal conferma la `modify` andata a buon fine: `accepted modify … -> sl: 29145.34, tp: 29504.83` · `done in 63.810 ms`.

**Conferma materiale dalla CronoStoria** — ordine contro posizione, per la prima volta dal 17/08:

| | S/L | T/P |
|---|---|---|
| **Ordine** inviato (riga 26) | 29.149,94 | 29.509,43 |
| **Posizione** risultante (riga 13) | **29.145,34** | **29.504,83** |

Diversi ⇒ `PositionModify` eseguita ⇒ **riancoraggio avvenuto**. Commento d'ordine `ORB 08-22-P`: gira la build giusta (regola 5.9).

| Data | Build | Riancoraggio |
|---|---|---|
| 17/08 | ORB N | ✅ |
| 21, 24, 25/08 | ORB O | ❌ ❌ ❌ |
| 24/08 | IM D | ❌ |
| **26/08** | **ORB P** | ✅ **1 su 1** |

### 7.2 Il trade, al centesimo
```
ATR(D1) 399,43  ->  dist = 39,943
buffer  = 5% × (97.152,64 − 90.000) = 357,632
lotti   = 357,632 / 39,943 = 8,9536  ->  8,95            [log: 8,95]        ✓
entry richiesto = SL_ordine + dist = 29.149,94 + 39,943 = 29.189,88
fill reale      = 29.185,28   ->  slippage 4,60 pt FAVOREVOLE               ✓
SL riancorato   = 29.185,28 − 39,943 = 29.145,337 -> 29.145,34              ✓
TP riancorato   = 29.185,28 + 8×39,943 = 29.504,827 -> 29.504,83            ✓
rischio effettivo = 8,95 × 39,94 = 357,46 $  =  ESATTAMENTE il progettato   ✓
```
Uscita: stop alle 16:35:25 server, `sell 8.95 @ 29.144,93` contro SL 29.145,34 → slippage sullo stop **0,41 pt**. Perdita **−361,13** · bilancio **96.791,51** ✓ (CronoStoria e pannello concordano al centesimo).

### 7.3 **Onestà: oggi il riancoraggio è costato 45 $**
Lo slippage era **favorevole**. Senza riancoraggio lo stop sarebbe rimasto a 29.149,94 → rischio 8,95 × 35,34 = **316,29 $** (l'88,5% del target) e il TP sarebbe stato a **9,17R** invece di 8R. Il trade è finito allo stop, quindi riportare il rischio al valore corretto è costato **~45 $**.

**È il comportamento giusto.** Il riancoraggio non serve a guadagnare: serve a rendere il rischio **esattamente quello deciso**, in entrambe le direzioni. Su un conto con freni stretti, un rischio che oscilla fra 0,88× e 1,10× del target è un problema di controllo, non di P&L. Metà delle volte il riancoraggio farà risparmiare, metà costerà: il valore è nella **varianza tolta**, non nella media.

### 7.4 Slippage — le due serie si stanno appiattendo
**Ingresso ORB** (n=7): +2,10 / +2,84 / −0,50 / +3,80 / +0,30 / −0,50 / **−4,60** → media **+0,49 pt** (era +2,06 su n=4).
**Sullo stop** (n=6): +0,33 / 0,00 / −0,55 / +0,40 / +0,88 / +0,41 → media **+0,245 pt = 0,6%** della distanza, contro il **2,25%** atteso dal backtest.

Lo slippage d'ingresso su FTMO è **sostanzialmente simmetrico attorno a zero**. Conseguenza: il *costo medio* della trappola 5.14 era sovrastimato — ma la sua **dispersione** no, ed è esattamente ciò che il riancoraggio elimina.

### 7.5 Verifiche di configurazione — tutte verdi
Dai pannelli sui grafici, tutto quadra al centesimo: `[BUILD ORB 08-22-P]` · `trading ATTIVO` · `timer EoD ON` · `baseline 100000.00` (**sopravvissuta alla sostituzione dell'EA**: la GlobalVariable è legata a login+magic, non al file) · `rif giorno 97152.64` · `buffer sopra floor 6792` (= 96.791,51 − 90.000 ✓) · rischio corrente **340 $** (= 5% × 6.791,51 ✓) · `Freni: giorno −1500$ (margine 1139$)` (= 96.791,51 − 95.652,64 ✓) `| totale −8000$ (margine 4792$)` (= 96.791,51 − 92.000 ✓).
Momentum: `IM 08-22-E` · `Stato: ATTIVO` · `Rischio/trade: 500$` · `DST: US` · bande disegnate ✓. ORB: livelli e marker disegnati ✓.
**Non verificabili dai pannelli**: `Ferma tutto` (deve essere **false**) e `>>>` (deve essere **500**). Irrilevanti a equity 96.791 — il target scatterebbe a 110.500 — ma da controllare con calma nella finestra proprietà.

### 7.6 Il momentum **non ha operato oggi**
`[IM] 2026.08.26 pronto (IM 08-22-E): open=29103.4 prevClose=29199.0 sig17=0.330%` alle 15:32:18, poi nessun ingresso: il prezzo non è mai uscito dalle bande ai check. Pannello: `P&L oggi: 0$ perdite chiuse: 0`. **Oggi c'è stato un solo trade, l'ORB.** Cancello 1(a) resta a **1 ordine IM su 3**.

### 7.7 Uptime — buco di 14 minuti a cavallo dell'apertura
Terminale: 09:51:23→09:51:45 (22 s) · 11:37:13→**15:18:17** · **15:32:16**→in corso.
Sostituzione degli EA eseguita alle **11:40:38** (ORB O→P) e **11:45:34** (IM D→E), **prima delle 15:00** ✓ come prescritto.
Il buco **15:18–15:32** copre l'apertura della sessione cash (15:30 locali). **Nessun danno**: l'ORB legge la candela di apertura dallo storico, alla riaccensione il feed si è risincronizzato e l'ingresso è avvenuto regolarmente alle 15:34:59. Il momentum ha preparato la giornata alle 15:32:18 leggendo l'open dallo storico, e non ha perso alcun check (il primo è alle 16:00).
**Dato utile a verbale**: gli EA reggono un'accensione tardiva purché il terminale sia su e sincronizzato **prima delle 15:35**. Ma il margine era di due minuti: non è una procedura, è stata fortuna.

### 7.8 Contabilità

| Seduta | Data | Risultato | Bilancio |
|---|---|---|---|
| 1 | 21/08 | −512,47 | 98.985,09 |
| 2 | 24/08 | −1.452,44 | 97.532,65 |
| 3 | 25/08 | −380,01 | 97.152,64 |
| **4** | **26/08** | **−361,13** | **96.791,51** |
| | | **progressivo −2.706,05** | |

Sei trade, sei perdite. Statisticamente nulla di anomalo: cinque stop ORB di fila con win rate 18,89% hanno probabilità del **35%**. **Veto di regime ≥ −5.000 $: margine residuo 2.294 $ con 11 sedute da giocare.** Probabilità stimata di chiudere sotto il veto con l'edge storico: **~21%**.

---

## 8. CAMBIO CONTO DEMO — pre-registrazione del 26/08/2026

Il conto **1514282053** (`$100k FTMO Free Trial 2-Step`, aperto il 13/08) **scade il 30/08/2026**, che cade di domenica. Il forward finisce l'11/09. Serve quindi un secondo conto.

### 8.1 Calendario
| Sedute | Date | Conto |
|---|---|---|
| 1–4 | 21, 24, 25, 26/08 | **1514282053** — già fatte |
| 5–6 | **27, 28/08** | **1514282053** — le ultime due |
| — | 29–30/08 | weekend: si apre il conto nuovo |
| 7–15 | 31/08 · 1, 2, 3, 4/09 · 8, 9, 10, 11/09 | **conto nuovo** *(7/09 Labor Day chiuso)* |

**Sei sedute sul conto 1, nove sul conto 2.**

### 8.2 **REGOLA CONTABILE — fissata ORA, prima di conoscere l'esito delle sedute 5 e 6**
> Il risultato del forward è **la somma dei risultati sui due conti**, non il bilancio finale del secondo:
> ```
> RISULTATO FORWARD = (bilancio finale conto 1 − 99.497,56)
>                   + (bilancio finale conto 2 − 100.000,00)
> ```
> dove **99.497,56** è il bilancio del conto 1 all'inizio della seduta 1 (21/08).
> Alla data odierna il primo addendo vale **−2.706,05**.
>
> **Il veto di regime del criterio D (≥ −5.000 $) si applica a questa somma.** L'azzeramento del bilancio a 100.000 è un artefatto amministrativo dell'infrastruttura demo, non un evento del sistema: **non cancella nulla**. Nessuna rilettura, nessuna eccezione.

### 8.3 Dichiarazione: il rischio per trade dell'ORB risale
Sul conto nuovo il buffer riparte da `5% × (100.000 − 90.000) = **500 $/trade**`, contro i **340 $** attuali (il buffer si è contratto con le perdite, come da disegno). Le nove sedute finali avranno quindi oscillazioni in dollari **~47% più ampie** delle prime sei. È il comportamento voluto della modalità buffer, **dichiarato adesso** perché non venga scoperto dopo. **Il criterio non si tocca.**

### 8.4 Le tre trappole del cambio conto
1. **Trappola 5.10 — MT5 spegne da solo il trading automatico.** Al cambio conto compare `automated trading is disabled because the account has been changed`. Se non ci si accorge, gli EA girano in **modalità OSSERVAZIONE**: valutano, loggano, e **non aprono nulla**. Va riabilitato a mano.
2. **La baseline.** `ORB_BASE_<login>_<magic>` è legata al login: sul conto nuovo la variabile non esiste e l'EA la crea leggendo il balance a `OnInit`. Se l'EA si inizializza **prima** che il terminale abbia sincronizzato il nuovo conto, potrebbe agganciare un valore sbagliato **e conservarlo**. Rimedio preventivo al §8.5; rimedio a posteriori: Strumenti → **Variabili Globali** (F3), cancellare `ORB_BASE_…`, ricaricare l'EA.
3. **La CronoStoria del conto 1 va esportata prima della scadenza.** Dopo, potrebbe non essere più accessibile. **Venerdì 28/08 è l'ultima occasione utile.**

### 8.5 Cambio di parametro raccomandato — **baseline esplicita**
Sul conto nuovo, invece di lasciare 0 (automatico), impostare:

| EA | Etichetta nella finestra MT5 | Valore |
|---|---|---|
| ORB | `0 = usa il balance al primo avvio (conto pulito)` | **100000** |
| IM | `0 = baseline automatica al primo avvio (per login+magic)` | **100000** |

**Il valore è identico a quello che l'automatismo produrrebbe** (il conto nuovo parte da 100.000): non è un cambio di comportamento, è rendere esplicito ciò che è già implicito, eliminando la trappola 2. Ed è **esattamente la configurazione prevista per la challenge** (rilievo R2 del piano v2): la si prova qui, in demo, invece che per la prima volta su un conto pagato.

---

## 9. ATTRIBUZIONE DEI SEI STOP E DECISIONE SUL RIPORTO — 27/08/2026

Domanda posta da Manu: quanti stop del conto 1514282053 sono stati **falsati** da comportamento errato o da mancanza di connessione/VPS, e se convenga riportare il risultato sul conto nuovo o ripartire da zero.

### 9.1 Attribuzione trade per trade — **uno su sei, e solo parzialmente**

| # | Data | EA | Terminale | Chiusura | Falsato? |
|---|---|---|---|---|---|
| 1 | 17/08 | ORB N | acceso | stop sul server | **NO** — riancoraggio ✅, rischio corretto |
| 2 | 21/08 | ORB O | acceso (fino 19:40) | stop 17:36:12 | **NO** — chiuso 2h04 prima dello spegnimento |
| 3 | 24/08 | ORB O | **spento** dalle 16:17 | stop 18:37:52 sul server | **NO** — l'EoD era alle 22:55, lo stop è arrivato prima. Con PC acceso, identico |
| 4 | 24/08 | **IM D** | **spento** | **25/08 08:56:52**, dopo 15h57 | **SÌ** — unico caso materiale |
| 5 | 25/08 | ORB O | acceso | stop | **NO** |
| 6 | 26/08 | ORB P | acceso | stop 16:35:25 | **NO** — riancoraggio ✅, rischio 357,46 = esattamente il progettato |

**Connessione internet / assenza di VPS: zero stop attribuibili.** Le tre cadute nel journal (24/08 15:32:10 e 15:56:48, 25/08 14:46:55) sono riconnessioni automatiche di pochi secondi, senza effetto su ordini o posizioni. **Tutte e tre le interruzioni sono state spegnimenti volontari del PC**, non guasti — già a verbale al §5.9.

### 9.2 Contaminazione totale del progressivo, in dollari

| Voce | Importo | Natura |
|---|---|---|
| Trappola 5.14 (difetto di build, **corretto** dalla P/E) | **41,90 $** | apparato |
| EoD mancata del 24/08 sull'IM | **0 → ~223 $** | comportamento |
| **Totale contaminato** | **42 → 265 $** | |
| **Progressivo al 26/08** | **−2.706,05 $** | |
| **Quota contaminata** | **1,5% → 9,8%** | |

> **Oltre il 90% del drawdown è comportamento genuino dei due EA in un regime avverso.** Il veto di regime del criterio D **non è materialmente contaminato** e conserva intero il suo significato.

Il costo vero del PC spento **non sono gli stop**: sono **18 check semi-orari dell'IM persi** (4 + 11 + 3) e **2 EoD mancate** — occasioni non colte, non stop falsati — più una notte di esposizione scoperta che nessun modello prezza.

### 9.3 Sei trade non misurano l'edge — i numeri, dalle serie storiche in custodia

Ricalcolato da `ORB_trades_R_20212026.csv` (md5 `08ef75849302017c487afc36c9c65333`) e `MOMENTUM_trades_R_20212026_FTMO.csv` (md5 `a4d046494a856852b8f76e219e037626`):

| | n | media | sd | win rate | trade per distinguere l'edge da zero al 95% |
|---|---|---|---|---|---|
| ORB | 969 | **+0,1784 R** | 2,7148 R | 19,30% | **890** |
| Momentum | 742 | **+0,1437 R** | 2,7703 R | 40,97% | **1.428** |

- **4 stop ORB consecutivi ricorrono nel 41,6% di tutte le finestre storiche di 4 trade.** È l'esito più probabile, non un'anomalia.
- Forward osservato (4 ORB + 1 IM) = **−6,12 R** contro un atteso di **+0,86 R**, sd 6,10 R → **z = −1,14**; bootstrap: **P(≤ −6,12 R) = 4,9%**. Sfortuna nel 5° percentile, non rottura.
- **Il conto precedente chiuso in profitto non è una prova.** Una finestra ORB di 5 trade chiude positiva nel **52,7%** dei casi: è testa o croce. Vale zero come evidenza, in entrambe le direzioni.
- Proprietà strutturale da tenere a mente: con win rate 19% e payoff 8R la distribuzione è fortemente asimmetrica a destra, quindi **la mediana di breve periodo è negativa anche con edge reale**. Essere sotto dopo sei trade è lo stato normale del sistema.

### 9.4 Quello che sei trade **sì** misurano: la fedeltà d'esecuzione — ed è positiva

| Grandezza | Backtest | Misurato dal vivo |
|---|---|---|
| Slippage d'ingresso ORB (n=7) | — | media **+0,49 pt**, simmetrico attorno a zero |
| Slippage sullo stop (n=6) | **2,25%** della distanza | **0,6%** (media +0,245 pt) |
| Riancoraggio SL/TP build P | atteso 1/1 | **1/1**, verificato al centesimo |
| Stop server-side con terminale spento | atteso onorato | **onorato**, 2 volte su 2 |

**L'esecuzione reale su FTMO costa meno di quanto il backtest assumesse.** È l'unica informazione statisticamente utile dei primi sei trade, e depone **a favore** dell'applicabilità.

### 9.5 DECISIONE — **il riporto si applica. Nessun azzeramento.**

La regola contabile del §8.2 è stata fissata il **26/08, prima di conoscere l'esito delle sedute 5 e 6**, e resta:
```
RISULTATO FORWARD = (bilancio finale conto 1 − 99.497,56) + (bilancio finale conto 2 − 100.000,00)
```
Azzerare ora significherebbe scartare la parte sfavorevole del campione dopo averla vista: **è la definizione di selection bias**, ed è l'errore di metodo n.3 (§2) ripetuto in forma peggiore. Prova dell'asimmetria: se i primi sei trade fossero stati vincenti, nessuno proporrebbe di azzerarli.

**Va però tenuto separato**: il riporto vale per **la misura del forward**, non per un giudizio sull'edge dei due EA — giudizio che sei trade non consentono in nessuna direzione (§9.3).

### 9.6 **ERRORE MIO, il sesto** — la probabilità di veto era sottostimata

Il 26/08 ho dichiarato **~21%** di probabilità di chiudere sotto il veto. Rifatta con bootstrap a livello di giornata sulle serie in custodia, modellando le 2 sedute residue sul conto 1 (buffer ~340 $) e le 9 sul conto 2 (buffer che riparte da 500 $), il valore corretto è:

| Scenario | P(veto < −5.000 $) | P(forward positivo) | Mediana |
|---|---|---|---|
| **Reale (cambio conto)** | **29,9%** | 31,1% | −2.668 $ |
| Ipotetico senza cambio conto | 25,5% | 27,3% | −2.771 $ |

Il cambio conto pesa solo **+4,4 punti**: il resto era una stima grezza. **Il criterio non si tocca** — il §5 del piano v2 già prescrive che cancello 2 rosso significhi *«non si compra; si riapre il punto del regime»*, non *«si abbandona»*. Il numero va conosciuto, non usato per spostare l'asticella.

---

## 10. MEMORIA DEL PROGETTO — 27/08/2026

Consolidato in un documento unico tutto ciò che il progetto ha visto, risolto, deciso, sbagliato, rimandato e lasciato aperto: `MEMORIA_PROGETTO_ORB_MOMENTUM.md`, md5 **`360e0ce0227ed5ecadbcdb4997c5816d`**, 21 sezioni.

Contiene, in forma di registro: le **16 trappole tecniche** 5.1→5.16 con lo stato di ciascuna (5.15 e 5.16 numerate da quel documento, prima erano senza numero) · i **rilievi R1-R3 e N1-N3** · le **16 decisioni chiuse** · le **13 questioni aperte** con lo stato al 27/08 · le **8 cose deliberatamente posticipate** e quando si faranno · i **19 errori a verbale** di tutte le chat · il **criterio D** nella formulazione corrente con le due riformulazioni dei cancelli 1(d) e 1(e) · le **tabelle parametri a quattro colonne** (backtest / forward / challenge / funded) per entrambi gli EA · i **protocolli operativi** (seduta, cambio conto, challenge, funded, VPS) · il **registro md5** completo · i **numeri chiave**.

**Verifiche eseguite prima della consegna**: tre passate di controllo incrociato contro tutte e dodici le fonti in custodia, con 30 + 14 + 4 rilievi trovati e sanati.

**Tre correzioni fattuali emerse dalla verifica, che vanno a verbale a sé:**
1. **Valore punto US100.cash = 1 $/punto/lotto**, non 1.000. Nelle fonti è scritto «1,000» con la virgola decimale italiana. L'aritmetica lo conferma (9,98 × 47,553 = 474,58 $). Errore di fattore mille evitato.
2. **Win rate ORB**: le fonti riportano **18,89%** (handoff §3.1, usato nei calcoli di questo verbale) e **19,89%** (dichiarato altrove). Ricalcolando dal CSV in custodia con convenzione `R > 0` stretto: **19,30%** (187 su 969) — **l'unico valore riproducibile**. Lo scarto è immateriale e l'uso di 18,89% è leggermente **pessimistico** sulle serie di stop (35,1% contro 34,2% per cinque perdite di fila), quindi nulla di ciò che è stato deciso cambia.
3. **md5 di `PIANO_ATTERRAGGIO_CHALLENGE_22-08-2026.md`**: calcolato `839a451e3ccaaea5afc3d915b411253c`, mentre il v2 ne dichiara `548ea0a97c8da85bd5efd29af3f92718`. Testate ed **escluse** le ipotesi LF→CRLF e newline finale. **Discrepanza non attribuita, a verbale** — il documento è comunque superato dal v2.

**Aperto nuovo registrato**: `PASSAGGIO_AL_FUNDED.md` è **obsoleto**. Prescrive build **O** e baseline **0**; il piano v2 §7.7 prescriveva di aggiornarlo alla correzione 5.14 e **l'aggiunta non è mai stata fatta**. Va riscritto per build **P** e baseline esplicita (rilievo R2) prima di essere usato.

---

## 11. SEDUTE 5 e 6 — gio 27/08 e ven 28/08 — **CERTIFICATE (6/15)** — chiusura del conto 1

Custodia: `20260827_experts` `ee5a917d371473a4fa1648542a099179` · `20260827_journal` `665451d54f0ef95524d7f0687c5f25c6` · `20260828_experts` `69e69af6f5af3c3ca2e348031488a6c0` · `20260828_journal` `83eb469a2d59dd7f7919545aed381e6f` · `CronoStoria_20260828.xlsx` `06951162d823d43ab115b25fd3a07bd9` (generata 2026.08.28 17:35, **copre tutti e 8 i trade del conto 1** — l'obbligo del §8.4 punto 3 è assolto).

### 11.1 I due trade, al centesimo

| | **ORB 27/08** | **ORB 28/08** |
|---|---|---|
| ATR(D1) · dist | 387,86 · **38,786** | 382,01 · **38,201** |
| Buffer = 5%×(bilancio−90.000) | 5%×6.791,51 = **339,58** | 5%×6.438,45 = **321,92** |
| Lotti calcolati / log | 8,7551 → **8,75** / 8,75 ✓ | 8,4270 → **8,42** / 8,42 ✓ |
| Entry **richiesto** (da SL dell'ordine) | 29.399,334 | 29.548,029 |
| **Fill reale** | **29.400,03** | **29.548,33** |
| Slippage d'ingresso | **0,70 pt FAVOREVOLE** | **0,30 pt FAVOREVOLE** |
| SL riancorato — calcolato / CronoStoria | 29.438,82 / **29.438,82** ✓ | 29.586,53 / **29.586,53** ✓ |
| TP riancorato — calcolato / CronoStoria | 29.089,74 / **29.089,74** ✓ | 29.242,72 / **29.242,72** ✓ |
| **Rischio effettivo** | 8,75 × 38,786 = **339,38 $** | 8,42 × 38,201 = **321,65 $** |
| Uscita (stop) | 16:40:08 @ **29.440,38** | 16:37:11 @ **29.586,98** |
| Slippage sullo stop | **+1,56 pt = 4,02%** della distanza | **+0,45 pt = 1,18%** |
| Perdita | **−353,06** (= −1,040 R) | **−325,43** (= −1,012 R) |
| Commissioni / swap | 0,00 / 0,00 | 0,00 / 0,00 |
| Commento d'ordine | **`ORB 08-22-P`** ✓ | **`ORB 08-22-P`** ✓ |
| Durata | 5 min 08 s | 2 min 11 s |

### 11.2 **RIANCORAGGIO 3 SU 3 CON LA BUILD P — prova materiale**
Confronto riga *Ordini* (livelli inviati) contro riga *Posizioni* (livelli in vigore):

| Trade | Ordine S/L – T/P | Posizione S/L – T/P | Riancoraggio |
|---|---|---|---|
| 17/08 ORB N | 30161.25 – 29630.93 | **30161.75 – 29631.43** | ✅ |
| 21/08 ORB O | 29325.58 – 28897.61 | 29325.58 – 28897.61 | ❌ |
| 24/08 ORB O | 29080.53 – 28673.71 | 29080.53 – 28673.71 | ❌ |
| 24/08 IM D | 29167.48 | 29167.48 | ❌ |
| 25/08 ORB O | 29260.51 – 29629.25 | 29260.51 – 29629.25 | ❌ |
| **26/08 ORB P** | 29149.94 – 29509.43 | **29145.34 – 29504.83** | ✅ |
| **27/08 ORB P** | 29438.12 – 29089.04 | **29438.82 – 29089.74** | ✅ |
| **28/08 ORB P** | 29586.23 – 29242.42 | **29586.53 – 29242.72** | ✅ |

**Build O: 0 su 4 (più l'IM). Build P: 3 su 3.**

**E c'è di più — la correzione lavora davvero, non è ridondante.** La riga `[ORB] posizione visibile dopo attesa` viene stampata **solo** quando la prima lettura della posizione fallisce e l'attesa la risolve:

| | 26/08 | 27/08 | 28/08 |
|---|---|---|---|
| `posizione visibile dopo attesa` | **SÌ** (~57 ms) | **SÌ** (~58 ms) | no |
| Lettura | fallita al primo colpo | fallita al primo colpo | riuscita subito |

**La condizione di gara si è ripresentata su 2 dei 3 trade, e l'attesa l'ha risolta entrambe le volte in un solo ciclo da 50 ms.** Con la build O quei due sarebbero stati due riancoraggi mancati in più. Nessuna riga `*** ATTENZIONE: posizione NON leggibile dopo l'invio ***`: **cancello 1(e) VERDE su 3 su 3**.

### 11.3 Contabilità e chiusura del conto 1

| Seduta | Data | Risultato | Bilancio |
|---|---|---|---|
| 1 | 21/08 | −512,47 | 98.985,09 |
| 2 | 24/08 | −1.452,44 | 97.532,65 |
| 3 | 25/08 | −380,01 | 97.152,64 |
| 4 | 26/08 | −361,13 | 96.791,51 |
| **5** | **27/08** | **−353,06** | **96.438,45** |
| **6** | **28/08** | **−325,43** | **96.113,02** |

**Bilancio finale del conto 1: 96.113,02** — CronoStoria e ricostruzione concordano al centesimo, e il drawdown dichiarato dal rapporto (−3.886,98 dal deposito di 100.000) quadra col trade del 17/08 incluso.

> **Primo addendo della regola §8.2, ora DEFINITIVO:**
> `96.113,02 − 99.497,56 = **−3.384,54 $**`
> Restano 9 sedute sul conto 2. **Margine residuo dal veto di regime (−5.000): 1.615,46 $.**

**Otto trade, otto perdite** (7 ORB + 1 IM). Sette stop ORB consecutivi hanno probabilità **22,3%**; la serie più lunga nel backtest 2021-2026 è di **26**. Nessuna anomalia statistica.

### 11.4 Una preoccupazione che si scioglie: gli stop fulminei sono NORMALI
Le ultime tre uscite ORB sono arrivate dopo **25 secondi**, **5 min 08 s** e **2 min 11 s**. Misurato sui 778 stop del backtest:

| | mediana | ≤1 min | ≤2 min | ≤3 min | ≤5 min | ≤10 min |
|---|---|---|---|---|---|---|
| Tempo allo stop | **7 min** | 8,1% | 17,6% | 27,1% | **38,3%** | 57,6% |

**La mediana storica del tempo-allo-stop è di sette minuti.** I nostri tre cadono al 1,3°, 38,9° e 20,3° percentile: uno rapido, due assolutamente ordinari. È la firma normale di un breakout con stop stretto (10% dell'ATR daily). **Nessun segnale.**

### 11.5 Serie di esecuzione aggiornate — l'esecuzione FTMO continua a costare meno dell'atteso

- **Slippage d'ingresso ORB (n=9)**: +2,10 / +2,84 / −0,50 / +3,80 / +0,30 / −0,50 / −4,60 / **−0,70** / **−0,30** → media **+0,271 pt**. **Gli ultimi quattro sono tutti favorevoli.**
- **Slippage sullo stop (n=8)**: media **+0,435 pt = 0,99% della distanza**, contro il **2,25%** atteso dal backtest. In % per trade: +0,56 / 0,00 / −1,21 / +0,18 / +2,17 / +1,03 / **+4,02** / +1,18.
  > Il **+4,02% del 27/08 è il peggiore finora** ed è il **primo campione che comincia a toccare la coda** che il backtest prevede (9,4% dei casi oltre il 5%, 3 su 778 oltre il 20%). Dentro l'involucro, ma l'aperto n.7 **non si chiude**: la coda resta non campionata.
- **Tempi di esecuzione (n=7)**: media **220,3 ms**, range 204–261. Stabili.
- **Commissioni: 0,00 su tutti e 8 i trade.** Swap: solo +1,24, sull'unica notte aperta.

### 11.6 Verifica di orologio superata
Il 28/08 il journal (ora locale) data l'ingresso alle **15:34:58,771**, mentre la CronoStoria (ora server) lo data alle **16:35:00**. Non è un ingresso anticipato: è l'orologio del PC **~1,2 s indietro** rispetto a quello del broker. L'EA usa `TimeTradeServer()` (trappola 5.1) e ha operato sulla candela giusta. **Controllo passato**, ma va a verbale che il margine di deriva esiste.

### 11.7 Prima caduta di connessione vera del forward — **si è riparata da sola**
`28/08 14:26:53 connection to FTMO-Demo lost` → `14:31:19 authorized … through Access Server 2c` (prima era 1b). **Buco di 4 min 26 s, interamente PRIMA della sessione**, nessuna posizione aperta, nessun danno. Ping 43-45 ms.
È la prima disconnessione non volontaria in sei sedute e **si è risolta da sé cambiando access point**: dato utile a verbale sul dibattito VPS — l'infrastruttura di rete non è il problema, lo è l'interruttore del PC.

### 11.8 **UPTIME — è ora il rischio dominante sul verdetto, e non dipende dagli EA**

| Seduta | Terminale acceso | Check IM eseguiti | Acceso alle 21:55? |
|---|---|---|---|
| 1 (21/08) | 14:34 → **19:40** | 8/12 | **NO** |
| 2 (24/08) | 15:28 → **16:17** | 1/12 | **NO** |
| 3 (25/08) | 11:02 → 17:41 · 19:07 → … | 9/12 | probabile sì |
| 4 (26/08) | 11:37 → 15:18 · 15:32 → … | 12/12 | non documentato |
| **5 (27/08)** | 11:36 → **17:37** *(spegnimento volontario: `exit with code 0`)* | **4/12** | **NO** |
| **6 (28/08)** | 13:53 → … *(nessuna riga di chiusura: ancora acceso all'export)* | 12/12 presunti | non documentato |
| | | **46 su 72 = 64%** | **confermato NO in 3 su 6** |

**Conseguenze misurate, non stimate:**

1. **Il momentum ha girato al 64% del tempo.** Ingressi attesi in 6 sedute: **4,2** con uptime pieno, **2,7** con quello reale. Ne è arrivato **1**.
   - P(≤1 ingresso) **con uptime pieno = 4,8%** → sarebbe stato un campanello.
   - P(≤1 ingresso) **con l'uptime reale = 21,3%** → **normale.**
   > **Il silenzio del momentum è spiegato dai check persi, non da un'anomalia dell'EA né del regime.** Ma il cancello 1(a) è a **1 ordine su 3** anche per questo.

2. **Il cancello 1(b) — la chiusura EoD delle 22:55 osservata dal vivo — è ancora a ZERO dopo sei sedute.** È l'unico meccanismo del progetto mai verificato sul campo, aperto n.5 dall'inizio. Può essere soddisfatto **solo** se il terminale è acceso alle **21:55 italiane** con una posizione aperta. In tre sedute su sei era spento a quell'ora.

3. **Fattibilità dei due cancelli sulle 9 sedute residue** (bootstrap giornaliero, 100.000 simulazioni):

| Cancello | Con **uptime pieno** | Con l'uptime tenuto finora (64%) |
|---|---|---|
| **1(a)** — servono ancora 2 ordini IM | **99,4%** | 93,0% |
| **1(b)** — serve 1 EoD osservata | **98,8%** | 93,5% |

> Il 93,5% dell'1(b) è **ottimistico**: il modello distribuisce i buchi di uptime in modo uniforme, mentre i buchi reali cadono **proprio nella fascia serale** in cui l'EoD scatta. Il numero vero è più basso.

4. **Se all'11/09 i cancelli 1(a) e 1(b) non sono verdi, il forward si prolunga** (regola già registrata al §5.8). Ogni giorno di trading in più costa **0,3-0,4 punti** di P(funded ≤6 mesi).

### 11.9 Veto di regime — la stima aggiornata

Bootstrap giornaliero sulle 9 sedute residue, conto 2 da 100.000 con buffer che riparte da 500 $/R:

| | Valore |
|---|---|
| Mediana del risultato finale del forward | **−3.591 $** |
| p5 / p25 / p75 / p95 | −8.613 / −6.123 / +47 / +8.764 |
| **P(veto di regime, < −5.000 $)** | **36,4%** |
| P(forward ≥ 0) | 25,2% |

Traiettoria della stima: **21% (26/08) → 29,9% (27/08) → 36,4% (28/08)**. Sale perché il progressivo peggiora e perché sul conto nuovo il rischio per trade risale da 322 a 500 $. **Il criterio non si tocca** — il §5 del piano v2 prescrive che cancello 2 rosso significhi *«non si compra; si riapre il punto del regime»*, non *«si abbandona»*. Il numero va conosciuto, non usato per spostare l'asticella.

### 11.10 Esito
**Sedute 5 e 6 CERTIFICATE. Conto 1514282053 chiuso a 96.113,02.** Nessuna anomalia meccanica: quadratura al centesimo su entrambi i trade, riancoraggio 3 su 3, build corretta provata dal commento d'ordine, guardie mai scattate, nessun ordine fallito, nessun doppio trade. **Cancelli 1(c) e 1(e): verdi.**
**Via libera all'apertura del conto 2 e alla prosecuzione del forward.**

---

## 12. STUDIO PARALLELO ESTERNO (VIX / ricerca edge) — VERIFICA CRITICA — 30/08/2026

Custodia: `HANDOFF_RICERCA_EDGE_ESTERNA_30-08-2026.md` md5 `0e5d90d6580b92f79c2c5e056f01c0ed` · `cboe_vix.csv` md5 `cb7b2a20c824841d9de62984415062c3` (9.261 sedute dal 1990) · script `vix_crosscheck.py`, `finale.py`, `funded_reale.py`, `stabilita.py`, `check_mql5.py`, `ea_equivalence.py`, `orb_rebuild.py` · conversazione integrale (280 paragrafi) estratta e archiviata.

**Metodo della verifica**: ho rieseguito da zero, sui nostri file in custodia, ogni affermazione numerica che cambia una decisione. Non ho accettato nulla sulla parola.

### 12.1 CONFERMATO — riprodotto cifra per cifra

| Affermazione esterna | Mia replica indipendente | Esito |
|---|---|---|
| Media degli stop ORB **−1,0225R** = eccedenza **2,25%** della distanza | **−1,0225** (n=778) → **+2,25%** | ✅ **identico** |
| Media stop protettivo IM **−2,0549** = eccedenza 2,74% | **−2,0549** (n=116) → **+2,74%** | ✅ **identico** |
| TP ORB **+8,0191** (eccedenza favorevole da gap-through) | **+8,0191** → +0,239% | ✅ **identico** |
| Gate VIX k=3: aperto n=341 (+0,2584), chiuso n=401 (+0,0462), diff **+0,2122**, **t=1,08** | **identico su tutte e cinque le cifre** | ✅ |
| Bootstrap P(diff > 0) = 87% | **86%** (20.000 ricampionamenti, IC95% −0,200…+0,573) | ✅ |
| 2026 dell'IM da **−7,45R a +5,42R** col gate | **identico** | ✅ |
| Altopiano stretto sul lookback: k=1,2,3 funzionano, k≥4 collassa | **k=1 +0,218 · k=2 +0,224 · k=3 +0,212 · k=4 +0,004 · k=5 −0,060** | ✅ |
| Correlazione ORB↔IM **0,220** | coerente con il nostro 0,223 | ✅ |
| Il veto è **protezione dalla rovina, non test dell'edge** | **quantificato: vedi §12.4** | ✅ **e rafforzato** |

> **Il contributo più prezioso dell'intero studio è il §1.2**: *i costi di uscita sono GIÀ dentro le nostre serie in R*. La media degli stop a −1,0225 **è** il 2,25% di slippage che il backtest assumeva. Chiunque, in futuro, sottraesse di nuovo un costo d'uscita dalle nostre serie **conterebbe due volte lo stesso costo**. Resta da sottrarre **solo l'ingresso: −0,0233 R/trade** (spread 0,0144 + slippage 0,0089) → **edge ORB netto +0,1551 R/trade**. Questo numero entra nella memoria del progetto.

### 12.2 SMENTITO — tre correzioni sostanziali

**C1 — «ORB a 500 $/R sul funded» NON è una raccomandazione nuova: è già la nostra configurazione.**
`PASSAGGIO_AL_FUNDED.md` prescrive modalità **buffer**, 5% del margine residuo sopra un floor a 90.000, cap 1.500. Quindi:

| Bilancio | Nostro rischio effettivo |
|---|---|
| **100.000 (primo giorno di funded)** | **500 $/R** |
| 105.000 | 750 $/R |
| 110.000 | 1.000 $/R |
| 120.000 e oltre | 1.500 $/R (cap) |

Il loro modello (`funded_reale.py`) usa `orisk = orb_risk × (10000 + eq)/10000`: la riga *«ORB 1000 buffer da solo (VOSTRA)»* parte da **1.000 $/R a equity zero**, cioè **il doppio** del nostro. La riga che loro raccomandano — **500 $/R** — corrisponde esattamente al nostro buffer 5% a bilancio 100.000.
> **Conseguenza**: la loro tabella «1.000$/R → 76% di sopravvivenza» descrive una configurazione **che non abbiamo mai scelto**; la riga «500$/R → 100% e 16.023 $/anno» è una **validazione indipendente della decisione già chiusa**. **Non c'è alcuna riapertura da mettere a verbale, e la decisione chiusa non si tocca.** Il punto 4 delle loro istruzioni finali (§12 del loro handoff) va **respinto**.
> Va invece **preso** il ragionamento sottostante: siamo al 24% di Kelly (`f* = μ/σ² = 0,1551/7,370 = 2.104 $`), e il buffer alza il rischio **solo dopo** aver costruito il cuscinetto — a 1.000 $/R ci si arriva a bilancio 110.000, quando il floor dista 20.000 e non 10.000. **È esattamente il comportamento voluto.**

**C2 — Il conteggio delle sequenze di stop è sbagliato: non 19, ma 26.**
Il loro `finale.py` conta le sequenze sulla serie **giornaliera**: un giorno in cui l'ORB **non opera** vale 0,00, non è negativo, e **spezza la serie**. Ma per il freno totale conta la sequenza di **trade** consecutivi, non di giorni di calendario.

| Metodo | Serie massima | Sequenze che superano 7 |
|---|---|---|
| Loro (per giorno) | 19 | **11,0%** (23 su 210) |
| **Corretto (per trade)** | **26** | **17,8%** (27 su 152) |

**La loro conclusione regge e ne esce rafforzata**: a 1.000 $/R il freno 7.500 sopporta 7 stop (7.500 / 1.022 = 7,33), e le sequenze lo superano nel **17,8%** dei casi — non nell'11%. A 1.500 $/R ne sopporterebbe 5. **La raccomandazione di alzare il rischio in challenge, che loro avevano già ritirato, resta scartata a maggior ragione.**
*Precisazione dovuta*: superare il freno totale **non è rovina** — chiude il tentativo e si ricompra. Questo criterio misura il consumo di quote, non la sopravvivenza.

**C3 — L'argomento «togliendo i 5 migliori per lato il gate migliora (t=2,37)» non è ammissibile.**
Riprodotto il numero (+0,3122, t=2,37), ma **il test è sulla grandezza sbagliata**: l'edge dell'IM vive nella **coda destra** (max +54,23R; 344 uscite EoD). Togliere i cinque trade migliori toglie l'edge, non il rumore. Lo stesso vale per il test sulle mediane (Mann-Whitney p=0,011): entrambe le mediane sono **negative** (−0,330 e −0,614), e la mediana non è la grandezza che paga la challenge.
> **Onestà di metodo**: la mia ipotesi iniziale era che il gate escludesse gli outlier buoni. **È falsa e la ritiro.** Il leave-one-out mostra che il trade più grande della serie (09/04/2025, **+54,23R**, il giorno dopo il picco VIX a 52,33) sta sul lato **chiuso**: togliendolo la differenza **sale** da +0,2122 a +0,3477. Il gate misura ciò che misura **nonostante** l'outlier, non grazie a lui.

### 12.3 IL MOTIVO VERO PER CUI IL GATE VIX VA ARCHIVIATO — più forte del loro

Loro archiviano il gate su base **operativa** (vale +1 punto e dimezza le occasioni del cancello 1(a)). Confermo la decisione, ma la base statistica è più dura di così. Due test che loro non hanno fatto:

**Walk-forward ingenuo — il gate non regge fuori campione in 2 casi su 3:**

| Addestramento fino a | Differenza in-sample | Differenza out-of-sample | |
|---|---|---|---|
| 01/01/2023 | **+0,839** | **−0,044** | ❌ non conferma |
| 01/01/2024 | +0,317 | +0,120 | ✅ conferma |
| 01/01/2025 | +0,310 | **+0,005** | ❌ non conferma |

**Effetto del gate DENTRO ciascun regime di volatilità — si inverte proprio nello stress:**

| Regime | Gate aperto | Gate chiuso | Differenza |
|---|---|---|---|
| VIX < 15 | +0,112 (n=78) | +0,111 (n=64) | **+0,000** |
| VIX 15–20 | +0,327 | −0,050 | +0,376 (t 1,66) |
| VIX 20–30 | +0,415 | −0,062 | +0,478 (t 1,74) |
| **VIX > 30** | **−0,489** (n=19) | **+0,697** (n=40) | **−1,186** |

> Il gate non separa nulla quando la volatilità è bassa, sembra funzionare nella fascia intermedia e **si inverte nel regime di stress**, che è quello in cui l'IM guadagna di più (R medio **+0,315** sopra VIX 30 contro +0,111 sotto 15). Sommato all'altopiano stretto (crolla già a k=4) e ai due anni con segno invertito su sei, **è la firma di un artefatto in-sample.**
> **GATE VIX: ARCHIVIATO. Confermato, con motivazione rafforzata.** Non si implementa né in challenge né sul funded. Resta l'unica ipotesi documentata su *cosa sia cambiato nel 2026* se il verdetto dovesse essere rosso per veto — ma come punto di partenza per un'indagine, non come soluzione.

### 12.4 **PRE-REGISTRAZIONE: cosa significa un verdetto ROSSO** — la lacuna era reale, si chiude oggi

L'osservazione dell'altra chat è **corretta e importante**: avevamo un criterio per decidere *se* comprare, non per decidere *cosa fare se non si compra*. Con il 36,4% di probabilità di veto, sarebbe stata decisa **dopo** aver visto i numeri — proprio ciò che il metodo vieta (errore 8.5).

**Prima ho misurato quanto informa un veto rosso** (bootstrap giornaliero, 40.000 simulazioni, 9 sedute residue dal progressivo di −3.384,54, serie con media traslata per costruire le ipotesi alternative):

| Ipotesi | P(veto rosso) | Rapporto di verosimiglianza contro «edge intatto» |
|---|---|---|
| Edge storico **intatto** | **36,6%** | — |
| Edge **dimezzato** | 41,7% | **1,14 : 1** |
| Edge **nullo** | 47,1% | **1,29 : 1** |
| Edge **negativo** (−1×) | 57,4% | 1,57 : 1 |

> **Un veto rosso vale 1,3 : 1.** Sulla scala di Jeffreys è **evidenza trascurabile** (serve ≥3:1 per «sostanziale», ≥10:1 per «forte»). Il veto **non è un test dell'edge e non va letto come tale**: è una protezione dalla rovina, e la chat esterna ha ragione. Ora c'è il numero.
> Un secondo forward da conto pulito: rosso nel **12,8%** dei casi con edge intatto contro **23,1%** con edge nullo → **LR 1,8 : 1**, ancora debole, al prezzo di **4,4 punti** di P(funded ≤6m).

> ### REGOLA PRE-REGISTRATA — fissata il **30/08/2026**, con 9 sedute ancora da giocare
> **Se al verdetto del 12–13/09 il CANCELLO 1 (meccanica) è VERDE e il CANCELLO 2 (veto di regime) è ROSSO:**
> 1. **Non si compra la challenge.** Il criterio D è onorato alla lettera.
> 2. **Il forward prosegue per altre 15 sedute**, con la **stessa identica configurazione**: stesse build P ed E, stessi parametri, stesso protocollo. Nessuna modifica, nessun filtro nuovo, nessun gate VIX.
> 3. Al termine il criterio D si applica **una seconda e ultima volta**, sulla **somma cumulativa delle 30 sedute** — non su una finestra nuova — con soglia **−6.437 $** invece di −5.000.
>    *Perché −6.437*: è la soglia che mantiene **esattamente lo stesso 13,0% di falso positivo** su una finestra doppia. Verificato: −5.000 su 15 sedute → 13,0%; **−5.000 su 30 sedute → 20,3%** (sarebbe una trappola); **−6.437 su 30 sedute → 13,0%**. **Non è un secondo tiro gratis: è la stessa severità statistica su una finestra più lunga.**
> 4. **Se anche il secondo verdetto è rosso, il progetto si ferma.** La questione del regime (aperto n.10) diventa ricerca, non deployment. Nessun terzo tentativo, nessuna riformulazione.
> 5. **Se il CANCELLO 1 è rosso**, vale quanto già scritto: non si compra, si corregge **quel punto** e si rifà **solo quello**.
>
> **Dichiarazione di onestà, come vuole il metodo**: questa regola è scritta **sapendo** che il progressivo è a −3.384,54 e che P(veto) è 36,4%. Non siamo ciechi come il 22/08. Ma la scelta è fra scriverla ora, con l'esito ancora ignoto, e scriverla dopo averlo visto — e la seconda è strettamente peggiore. La scelta fra le quattro opzioni possibili è stata posta a Manu con i costi misurati di ciascuna, e **Manu ha scelto questa**.

### 12.5 TRAPPOLA OPERATIVA CONFERMATA — e più grave di come l'hanno descritta

Verificati uno per uno i `input` dichiarati nel sorgente `ORB_US100_-_step16_P.mq5`. **I default sono questi:**

| Etichetta MT5 | Default nel file | Serve in challenge |
|---|---|---|
| Modalita' rischio | `RISK_BUFFER` | **Dollari fissi sulla baseline** |
| Rischio $ fisso | 300 | **1000** |
| Freno giornaliero | 1500 | **2000** |
| Freno totale | 8000 | **7500** |
| Baseline del conto | **0** | **100000** |
| Ferma tutto quando la fase e' superata | **true** | true |
| **`>>> METTERE A 500 PRIMA DI OPERARE`** | **0,0** | **500** |
| Disegna livelli e marker | false | false |

**Correzione al loro §1-bis**: i default **non sono la configurazione funded** (quella vuole `Ferma tutto = false`). Sono una **terza configurazione, che non corrisponde a nessuna fase** — ed è peggio.
**Il pericolo vero, che loro non isolano**: `Ferma tutto = true` **insieme a** `>>> = 0` significa **target-lock al tocco esatto**, senza il margine di 500 $. È precisamente il fallimento-al-tocco che il progetto ha eliminato con una decisione chiusa (*«senza margine, un test si chiuse a soli 78,77 $ sopra il target per fortuna del tick»*). **Caricando l'EA da zero su una challenge, quella protezione non c'è.**
Per l'IM build E i default sono più benigni (rischio 500 ✓, `Ferma tutto = false` → va messo a **true** in challenge, baseline 0 → **100000**, filtro news e riancoraggio già `true` ✓).
> **Va a registro come estensione della trappola 5.16**, e la verifica voce per voce prima dell'acquisto della challenge diventa **obbligatoria**.

### 12.6 Divergenza sulle stime, dichiarata e non risolta
Loro stimano **P(funded ≤6m) = 86,9%**, noi **75,9%**. Le cause sono almeno due: (a) la loro stima **non include il costo del forward** (la nostra sì: 82,0 → 77,6 → 75,9); (b) nel loro Monte Carlo il freno giornaliero è implementato come `dd = max(dd, dmin)`, quindi **una giornata che tocca il freno ma chiude positiva viene contata positiva** — in realtà il freno avrebbe fermato tutto sulla perdita. Entrambe spingono verso l'alto.
Confronto corretto: **loro 86,9% contro il nostro 81,5% al lordo del costo-forward** (handoff §8.4) e **80,3%** del nostro simulatore. **Scarto ~5-6 punti, direzione e ordine di grandezza concordi. Nessuna delle due è "quella giusta"; si tengono entrambe come banda.**

### 12.7 Cosa portiamo a casa e teniamo per dopo

**Acquisito subito, entra nella memoria:**
1. **Costi di uscita già dentro le serie** → **edge ORB netto +0,1551 R/trade**. Mai più sottrarre costi d'uscita.
2. **Il veto vale 1,3 : 1** → non si legge come test dell'edge, né in verde né in rosso.
3. **Regola pre-registrata del §12.4** → la lacuna è chiusa.
4. **Trappola dei default** (§12.5) → verifica obbligatoria prima dell'acquisto.
5. **Replica indipendente dell'ORB**: 1.035 trade su feed Pepperstone, +0,2186 R/trade lordo contro il nostro +0,2240, **0,50 sigma**. È **l'unica prova esterna** che l'edge non sia un artefatto della nostra implementazione o del nostro export. Non era producibile internamente.
6. **La griglia HH:00/HH:30 dell'IM non si sposta mai**: spostarla di 15 minuti costa il **70%** dello Sharpe. Se un giorno servisse escludere una finestra news, si **salta il singolo check**, non si sposta la griglia.
7. **Riottimizzare costa −0,33 di Sharpe** (walk-forward ancorato, 27 combinazioni): il divieto del §13 ora ha un numero.
8. **I limiti FTMO vanno verificati sull'equity INTRAGIORNALIERA**: il minimo intraday è in media **1,39×** peggiore della chiusura. Qualunque simulazione futura che usi il P&L di fine giornata **sottostima il rischio di violazione del 39%**.
9. **Fuso del server = New York + 7 ore, non EET fisso**: i nostri orari 16:35 / 22:55 sono corretti tutto l'anno, ma qualunque estensione a strumenti europei o asiatici deve derivare gli orari da GMT + regole DST dell'exchange.
10. **Sorgente VIX**: il CFD "VIX" dei broker è sul **future front-month** (beta 0,547 sulle variazioni %, segno a 3 sedute discorde nell'11,5% dei casi). L'unica sorgente valida è lo **spot Cboe** via `WebRequest()`. Se un giorno servisse il VIX, questo è già risolto.

**Tecniche riutilizzabili, archiviate:**
- **`ea_equivalence.py` — test di equivalenza per traduzione**: riscrivere la logica dell'EA in Python e confrontarla giorno per giorno col motore di backtest. **Ha trovato un bug che nessun controllo statico avrebbe rilevato** (conversione oraria che produceva 13:30 invece di 16:30). **È la tecnica più preziosa dell'intero studio dopo il §1.2**, e va usata sulla prossima build che tocchi la logica.
- `check_mql5.py` — controllo statico di sorgenti MQL5, complementare al nostro template di controlli.
- `vix_crosscheck.py` + `cboe_vix.csv` — riutilizzabili su qualunque lista trade futura.

**Da NON riaprire (chiuso da loro, verificato da me):**
14 paper accademici → uno solo sopravvive ai costi ed **è quello che già usiamo** · mean reversion intraday su CFD indici: **240 celle, tutte morte** · 38 filtri e overlay: tutti neutri o dannosi · momentum multi-asset: **24 strumenti, solo NAS100 sopravvive ai costi** · passaggio alla 1-Step: **scartato** (Max Loss trailing e daily 3%, P(pass) ~35% contro ~95%) · conti multipli in parallelo: **scartato** (perfettamente correlati, e il costo VPS annulla il beneficio) · gate VIX: **archiviato**.

---

## 13. RI-VALIDAZIONE AVVERSARIALE DEL §12 — 30/08/2026, su richiesta di Manu

Manu ha chiesto di rivedere le conclusioni del §12 perché non se ne fidava del tutto. Ho rifatto i sei punti **cercando di romperli**. Esito: **quattro confermati e rafforzati, uno confermato con una rivelazione che avevo omesso, uno che conteneva due mie sovra-affermazioni — ora ritirate.**

### 13.1 Punto 1 (i costi di uscita sono già nelle serie) — **CONFERMATO con prova nuova**
Non mi ero accorto di avere una verifica empirica diretta: **i nostri stop reali**. Calcolando R = perdita ÷ (lotti × distanza) sui trade veri:

| Trade | R reale | Sforo |
|---|---|---|
| 26/08 build P | −1,0103 | +1,03% |
| 27/08 build P | −1,0402 | +4,02% |
| 28/08 build P | −1,0118 | +1,18% |
| **media build P (riancoraggio garantito)** | **−1,0207** | **+2,07%** |
| **backtest, 778 stop** | **−1,0225** | **+2,25%** |

**Lo sforo misurato dal vivo e quello del backtest coincidono entro 0,2 punti percentuali.** Il backtest rappresenta correttamente ciò che accade allo stop: i costi d'uscita **sono** dentro la serie in R, e sottrarli di nuovo sarebbe doppio conteggio. *(Sui 4 trade pre-build-P la media è più bassa (+1,11% su n=7) proprio perché senza riancoraggio la distanza di stop era falsata: un'ulteriore conferma indiretta della trappola 5.14.)*
**Resta valido**: da sottrarre solo l'ingresso, −0,0233 R/trade → **edge ORB netto +0,1551**.

### 13.2 Punto 2 (500 $/R sul funded = già la nostra config) — **CONFERMATO a livello di sorgente**
Letto il codice della build P, riga 626-633:
```
double buf = eq - InpFloorEquity;      // equity - 90.000
double r   = buf*InpBufferPct/100.0;   // x 5%
if(InpBufferCapUSD>0 && r>InpBufferCapUSD) r = InpBufferCapUSD;   // cap 1.500
```
A equity 100.000 → **r = 500,00 $**. La formula della chat esterna (`orisk = 500 × (10000+eq)/10000 = 500 + 0,05·eq`) è **algebricamente identica alla nostra**. La loro riga "1.000 $/R (vostra scelta)" corrisponde a `InpBufferPct = 10%`, che non abbiamo mai usato. **Nessuna riapertura. La decisione chiusa resta chiusa.**

### 13.3 Punto 3 (perché il gate VIX è archiviato) — **DUE MIE SOVRA-AFFERMAZIONI, LE RITIRO**

**Ritiro n.1 — «si inverte nel regime di stress».** Non è supportato:

| VIX > 30 | n aperto | n chiuso | differenza | t | IC95% |
|---|---|---|---|---|---|
| tutti i trade | 19 | 40 | −1,186 | **−0,82** | [−4,03 ; +1,66] |
| **senza il solo trade da +54,23R** | 18 | 40 | **+0,187** | **+0,39** | — |

t = −0,82 **non è significativo**, e togliendo **un solo trade** l'inversione sparisce e cambia segno. Avevo presentato come struttura quello che è rumore su un campione di 19 osservazioni.

**Ritiro n.2 — «non regge fuori campione».** Troppo forte:

| OOS da | n | differenza | IC95% |
|---|---|---|---|
| 2023 | 526 | −0,044 | [−0,543 ; +0,455] |
| 2024 | 387 | +0,120 | [−0,507 ; +0,747] |
| 2025 | 242 | +0,005 | [−0,905 ; +0,915] |

**Nessuno dei tre intervalli esclude lo zero — ma nessuno esclude nemmeno +0,21.** La formulazione corretta è: *l'effetto non è stabile nel tempo*, non *è smentito fuori campione*.

**Cosa resta, in ordine di solidità** (l'archiviazione REGGE, ma per **accumulo di indizi deboli**, non per una prova decisiva):
1. **t = 1,08** sul campione intero, IC95% [−0,20 ; +0,57]: sotto ogni soglia di evidenza, e **le soglie erano pre-registrate** (verde ≥ +0,10 **e** t ≥ 2,0).
2. **Altopiano che collassa a k=4** (+0,212 → +0,004 → −0,060 a k=5): un effetto reale non sparisce per un giorno di lookback.
3. **Segno invertito in 2 anni su 6.**
4. Instabilità temporale (sopra).
5. Costo operativo: dimezza le occasioni del cancello 1(a), da 88% a 45% con l'uptime reale.

> **Il gate resta archiviato**, ma la motivazione è *«il test pre-registrato ha dato GIALLO e nessuna verifica successiva lo ha promosso»*, non *«è dimostrato inutile»*. La differenza conta se un giorno lo si riprendesse.

### 13.4 Punto 4 (il veto vale 1,3 : 1) — **CONFERMATO e reso simmetrico**

| Esito del veto | P(edge intatto) | P(edge nullo) | Verosimiglianza |
|---|---|---|---|
| **ROSSO** | 36,6% | 47,1% | **1,29 : 1** a favore di «edge nullo» |
| **VERDE** | 63,4% | 52,9% | **1,20 : 1** a favore di «edge intatto» |

**Nessuno dei due esiti informa sull'edge.** Il veto è una protezione dalla rovina, e va letto solo così — in verde come in rosso.

**Controllo del simulatore**: ho rimodellato le guardie con le costanti esatte del sorgente (kill IM a 3 perdite chiuse **oppure** −3R = −1.500 $; guardia equity a min(9R, 2.000) = 2.000 $) invece della mia approssimazione a −2.500 $. **P(veto) 36,7% contro 36,6%.** Il numero non dipende dall'approssimazione.

### 13.5 Punto 5 (la regola del verdetto rosso) — **CONFERMATO, ma con una rivelazione che avevo OMESSO**

La soglia **−6.437 $** è calibrata al 13,0% di falso positivo **da conto pulito su 30 sedute**. Ma applicata alla struttura **reale** — 6 sedute già fatte e fisse a −3.384,54, più 24 aleatorie — il quadro è questo:

| | valore |
|---|---|
| P(secondo verdetto rosso a −6.437 \| **sistema sano**, da dove siamo) | **30,2%** |
| P(secondo verdetto rosso a −6.437 \| edge nullo) | 46,8% |
| **P(ROSSO due volte \| sistema sano)** | **19,5%** |
| P(ROSSO due volte \| edge nullo) | 31,6% |
| **Verosimiglianza di «rosso due volte»** | **1,62 : 1** |

> **Questo l'avevo taciuto e va detto**: il secondo cancello **non** ha il 13% di falso positivo *da dove siamo* — ne ha il **30,2%**. La regola ferma un sistema sano nel **19,5%** dei casi, e quando ferma vale 1,62 : 1. È **meglio** del singolo verdetto (1,29 : 1 fermando il 36,6%), ma resta **evidenza debole**.

**Un'alternativa esiste e l'ho scartata di proposito.** Calibrando la soglia in modo **condizionato** (13% di falso positivo *da dove siamo*) si otterrebbe **−9.404 $**, con LR **1,92 : 1** e solo l'**11,6%** di sistemi sani fermati: migliore su entrambe le metriche che ci stanno a cuore.
> **Non la adotto, e la ragione è di metodo, non di numeri.** −9.404 è per costruzione una soglia che **assorbe la nostra sfortuna passata**: la si sceglierebbe *perché* siamo a −3.384. È esattamente l'errore 8.5 — cambiare la calibrazione dopo aver visto i numeri — travestito da argomento tecnico. Il criterio originale fu calibrato in modo **non condizionato** (13% da conto pulito su 15 sedute) e la sua estensione dev'essere calibrata allo stesso modo. **La stessa asimmetria esiste già oggi** (13% dichiarato, 36,4% effettivo da qui) ed è accettata: sarebbe incoerente correggerla solo ora che ci penalizza.
> **Quando un argomento tecnico e il nostro interesse puntano nella stessa direzione, la disciplina è sospettare dell'argomento.** La regola resta **−6.437**, con il 30,2% e il 19,5% dichiarati a verbale.

### 13.6 Punto 6 (la trappola dei default) — **CONFERMATO, ed è PEGGIO di come l'avevo descritto**
Verificato nel sorgente, righe 827-836:
```cpp
if(InpUseProfitTarget && !g_targetReached && g_baseline>0 &&
   eq >= g_baseline + InpProfitTargetUSD + InpTargetBufferUSD)
  { if(HasPosition()) CloseAll("TARGET DI FASE RAGGIUNTO"); ... }
```
Il confronto è **sull'EQUITY**, non sul bilancio. Con `InpTargetBufferUSD = 0` (il default) l'EA scatta appena l'**equity flottante** tocca baseline + 10.000 e **chiude a mercato**: fra il controllo e il riempimento il prezzo può muoversi, e **il bilancio realizzato può atterrare SOTTO il target**. Non è solo «si ferma al tocco esatto»: è **si ferma sul flottante e realizza dove capita**. È esattamente il fallimento-al-tocco che il margine di 500 $ elimina.

### 13.7 Esito della ri-validazione
**Confermati**: punti 1, 2, 4, 6 (i primi due con prove nuove, il sesto aggravato). **Punto 5 confermato con la disclosure mancante.** **Punto 3 corretto**: due sovra-affermazioni ritirate, conclusione invariata ma su basi dichiaratamente più deboli.
**Nessuna conclusione operativa cambia. Nessuna modifica agli EA, ai parametri o al criterio. Il forward riparte lunedì come previsto.**

---

## 14. SEDUTE 7→12 — dal 31/08 all'08/09/2026 — **CERTIFICATE (12/15)** — conto 2

Custodia: `20260901_experts` `fe97f5650c5d49f93b45fe9c6c0c3082` · `20260902_experts` `74066f1b02b03ef504ff866e1d046582` · `20260903_experts` `dd059ef372cfd92b2972c0010d75ca11` · `20260904_experts` `a15e01428d71957b7e04609be8440b61` · `20260908_experts` `0f83256b96ab3c26c654fe9a2f0932ac` · `20260831_journal` `dc04ef6ce3bf66f242d7175ba4412fe0` · `20260901_journal` `4bbba78f020be67066f322e37a45c4e0` · `20260902_journal` `08bea45601ea764438db48c38a9b375d` · `20260903_journal` `9c4e98e8a31b59bc5a15d4dd901abc6e` · `20260904_journal` `41ed8140ed3b8f3e783b498dc7da6519` · `20260908_journal` `7ad4ec74bdab82ef890f96ea73f2a99f` · `CronoStoria_20260908.xlsx` `f615aa54b30bc9c94e34fbe65a0badaf`.
**Experts del 31/08 non reperibile** (MT5 ruota i log a inizio mese): la seduta è certificata dal journal + CronoStoria, e l'ATR(D1) di quel giorno è stato **ricavato dai dati** (389,825, dal TP riancorato).
Conto 2: **1514463987**, aperto 30/08 con 100.000,00.

### 14.1 I sei trade, al centesimo — tutti gli assert superati

| Trade | dist | lotti (buffer→calc) | slip ingresso | slip stop | rischio | R |
|---|---|---|---|---|---|---|
| 31/08 ORB LONG | 38,9825 | 12,82 ✓ | **+0,30** | +0,68 (**+1,74%**) | 499,76 | **−1,0174** |
| 01/09 ORB SHORT | 38,3438 | 12,37 ✓ | **+3,81** | +0,62 (+1,62%) | 474,31 | −1,0161 |
| 02/09 ORB SHORT | 39,7238 | 11,34 ✓ | **−0,19** | +0,74 (+1,86%) | 450,47 | −1,0185 |
| 03/09 | — | — | **SKIP doji** (corpo 4,2% del range) | — | — | — |
| 04/09 ORB LONG | 40,0938 | 10,66 ✓ | +0,40 | +1,17 (**+2,92%**) | 427,40 | −1,0291 |
| **04/09 IM LONG** | 30,160 | **13,49 (cap notional)** | **0,00** | +0,44 | **406,86** | **−2,0146** |
| 08/09 ORB SHORT | 36,4425 | 10,00 ✓ | +0,50 | +0,71 (+1,95%) | 364,43 | −1,0194 |

Verificati per ciascun trade, con assert: lotti dal buffer `5%×(bilancio−90.000)` · SL riancorato = `fill ∓ dist` · TP riancorato = `fill ± 8·dist` · perdita = `lotti × (uscita − fill)`. **Bilancio finale ricostruito 96.919,82 = CronoStoria, al centesimo.**

### 14.2 **RIANCORAGGIO 5 SU 5 — la build P è ora a 8 SU 8**
Ordine vs Posizione nella CronoStoria: 31/08 `29372.00→29372.30` · 01/09 `29083.67→29079.86` · 02/09 `29074.75→29074.94` · 04/09 `29545.09→29545.49` · 08/09 `29579.07→29578.57`. **Tutti diversi ⇒ `PositionModify` eseguita ogni volta.** Commento d'ordine `ORB 08-22-P` su tutti (regola 5.9) ✓.

**Il caso dell'IM del 04/09 è la prova che il cancello 1(e) riformulato era giusto.** Ordine SL `29579.66` = Posizione SL `29579.66`, e il journal stampa `skipped as it changes nothing`. **Non è un fallimento**: il prezzo richiesto era `29579.66 + 2×30,16 = 29639,98` ed è **esattamente il fill**. Slippage **zero**, quindi il riancoraggio non doveva spostare nulla. Con la formulazione originale del cancello (*«la riga deve comparire a ogni ingresso»*) questo sarebbe stato un **falso rosso**. **La correzione del 25/08 ha appena pagato il suo primo dividendo.**

### 14.3 **N2 OSSERVATO DAL VIVO: il cap notional dell'IM ha morso, a nostro favore**
Sizing nominale `500 / 30,16 = 16,58 lotti`; cap `4 × 100.000 / 29.639,98 = 13,495` → **13,49 lotti**. Rischio effettivo **406,86 $ invece di 500**. È il rilievo N2 (*«il cap morde spesso, a favore nostro»*) osservato per la prima volta su un ordine reale. **La perdita a −2R è stata 819,65 $ invece di ~1.000.**

### 14.4 Serie di esecuzione — l'esecuzione FTMO resta migliore del modello
- **Slippage d'ingresso ORB (n=14)**: +2,10 / +2,84 / −0,50 / +3,80 / +0,30 / −0,50 / −4,60 / −0,70 / −0,30 / **+0,30 / +3,81 / −0,19 / +0,40 / +0,50** → media **+0,517 pt**.
- **Slippage sullo stop (n=14)**: media **+0,560 pt = 1,39% della distanza**, contro il **2,25%** atteso dal backtest. Peggiore osservato: +4,02% (27/08).
- **Commissioni 0,00 su tutti e 14 i trade. Swap 0,00** (nessuna posizione overnight sul conto 2).

### 14.5 CONTABILITÀ — **il veto di regime è sforato**

| Seduta | Data | Risultato | Bilancio conto 2 |
|---|---|---|---|
| 7 | 31/08 | −508,44 | 99.491,56 |
| 8 | 01/09 | −481,94 | 99.009,62 |
| 9 | 02/09 | −458,82 | 98.550,80 |
| 10 | 03/09 | **0,00** (SKIP doji) | 98.550,80 |
| 11 | 04/09 | −1.259,48 (ORB −439,83 + IM −819,65) | 97.291,32 |
| — | 07/09 | Labor Day, chiuso | — |
| 12 | 08/09 | −371,50 | **96.919,82** |

> **RISULTATO FORWARD (regola §8.2)** = (96.113,02 − 99.497,56) + (96.919,82 − 100.000,00)
> = −3.384,54 + (−3.080,18) = **−6.464,72 $**
> **Veto di regime ≥ −5.000 $: SFORATO di 1.464,72 $, alla seduta 12 di 15.**
> Per rientrare servono **+1.464,72 $** in 3 sedute (≈ 4,2 R al rischio corrente di ~350 $/R): **P ≈ 24%**. Mediana attesa al 15/15: **−6.807 $**.

**Tredici trade, tredici perdite** (11 ORB + 2 IM). Somma **−15,278 R**.

### 14.6 **QUANTO È ANOMALA QUESTA SERIE — e un mio errore di metodo, corretto prima di consegnare**

Il primo calcolo che ho fatto campionava i **13 trade uno a uno**, in modo indipendente: dava P = **0,17%** e verosimiglianza **14,7 : 1** a favore di «edge nullo» — cioè *evidenza forte che il sistema è rotto*. **È sbagliato**, e me ne sono accorto rifacendolo: ignora la correlazione infragiornaliera (**0,223**) e la dipendenza seriale fra sedute consecutive. Il metodo prescritto dal progetto è il **bootstrap per giornata intera**.

| Metodo | P(risultato ≤ −6.464,72 con edge intatto) |
|---|---|
| Trade per trade, indipendenti *(SBAGLIATO)* | 0,17% |
| **Giornate intere indipendenti** *(metodo del progetto)* | **4,84%** |
| **Blocchi di 6 giornate consecutive** *(preserva anche la dipendenza seriale)* | **11,94%** |

**Verosimiglianza, ricalcolata a giornate intere:**

| Ipotesi | P(≤ osservato) | LR contro «edge intatto» |
|---|---|---|
| Edge **intatto** | 4,84% | — |
| Edge **dimezzato** | 7,44% | **1,54 : 1** |
| Edge **nullo** | 10,59% | **2,19 : 1** |
| Edge **negativo** | 18,50% | 3,82 : 1 |

> **Conclusione: siamo fra il 5° e il 12° percentile. Sfortuna, non rottura.** La verosimiglianza contro «edge nullo» è **2,19 : 1** — sotto la soglia di 3:1 della scala di Jeffreys, quindi **evidenza trascurabile**. Coerente con quanto già a verbale al §12.4: il veto **non è un test dell'edge**, e il fatto che sia rosso **non dice che il sistema è rotto**.
> *(Errore mio a verbale, il settimo: il bootstrap trade-per-trade. Trovato e corretto prima della consegna, ma va dichiarato perché per qualche minuto ho creduto a un LR di 14,7:1.)*

### 14.7 Rilievi nuovi

**(a) 04/09 — `*** WARNING: volume candela apertura NON anomalo … possibile ORARIO SESSIONE ERRATO ***`. Falso positivo, spiegato.**
Il 04/09 era il **primo venerdì di settembre = giorno dei Non-Farm Payrolls**, pubblicati alle 8:30 ET = **14:30 server**, un'ora prima dell'apertura cassa. L'ora precedente era già gonfia di volume da NFP, quindi la candela delle 16:30 non è apparsa anomala e la guardia ha parlato. **L'orario è corretto**: la CronoStoria data l'ordine alle 16:35:00 server come sempre. → **Il controllo di volume dà falso positivo strutturale sui venerdì NFP e sui giorni con dato macro pre-apertura. A verbale per non spaventarsi.**

**(b) 03/09 — cambio di timeframe del grafico IN SEDUTA. Violazione del §13.**
Alle 15:52:43 l'ORB si reinizializza con `(US100.cash, H1)`, alle 15:53:02 di nuovo con `(US100.cash, M5)`. **Non è un doppio EA** (trappola 5.15): è lo **stesso** EA che si reinizializza perché è cambiato il periodo del grafico — e infatti stampa `PERIOD_M5` in entrambi i casi, perché legge M5 a prescindere dal grafico su cui sta. Il journal registra anche `one click trading has been disabled` il 02/09 alle 15:52:43.
**Ma la reinizializzazione azzera `g_dailyRefEq` (rilievo R1) e `g_doneToday` (trappola 5.7).** Quel giorno innocuo (SKIP doji, finestra d'ingresso già chiusa). **Se fosse successo fra le 15:35 e le 15:40 con il trade già aperto e chiuso, avrebbe potuto produrre un SECONDO trade nella stessa giornata.** È esattamente lo scenario per cui esiste la regola «mani giù 15:35–15:40». **Da non ripetere.**

**(c) 08/09 — partenza tardiva: ingresso con 2 minuti e 14 secondi di ritardo.**
Terminale acceso alle **15:37:11**; l'ORB è entrato alle **15:37:13** (CronoStoria: 16:37:14 server). La finestra d'ingresso è 16:35→16:40 server, quindi il comportamento è **corretto per disegno** — l'EA recupera una partenza tardiva. **Ma il prezzo d'ingresso non è quello che il backtest avrebbe avuto**: il backtest entra sempre all'apertura della candela delle 16:35. **È la seconda osservazione degradata dall'uptime dopo il 24/08.** Il trade resta valido per la somma del veto (regola: dollari grezzi, nessuno scorporo), ma come osservazione della strategia vale meno.

**(d) MT5 si è auto-aggiornato a build 6182** (da 6140), scaricato l'08/09 alle 15:38 e applicato alle 18:31. **Terzo aggiornamento del progetto** (6090 → 6140 → 6182). Vale la stessa nota di sempre: nel tester l'aggiornamento è provato innocuo, nel live il percorso invio-ordine/cache è quello della trappola 5.14. Da qui in poi si gira su **6182**.

**(e) 01/09 alle 17:44:02 — `terminal stopped due to system shutdown`**: spegnimento del PC, non chiusura di MT5.

### 14.8 **UPTIME — è peggiorato, ed è ora l'unica cosa che decide il verdetto**

| Seduta | Terminale | Check IM eseguiti | Acceso alle 21:55? |
|---|---|---|---|
| 7 (31/08) | 13:20→17:34 · 18:20→**21:44:56** | 11/12 | **NO — mancati 11 minuti** |
| 8 (01/09) | 13:18→**17:44 (shutdown del PC)** · 18:44→21:26 | 9/12 | **NO** |
| 9 (02/09) | 15:27→17:24 | 3/12 | **NO** |
| 10 (03/09) | 14:47→15:53 | 0/12 | **NO** |
| 11 (04/09) | 14:36→16:33 | 2/12 | **NO** |
| 12 (08/09) | 15:37→17:38 · 18:31→… | ~9/12 | non documentato |
| | | **conto 2: 34/72 = 47%** | |
| | | **totale forward: 80/144 = 56%** | **0 su 12** |

**Conseguenza misurata, non stimata:**

| | Ingressi IM in 12 sedute |
|---|---|
| Attesi con **uptime pieno** | **8,3** |
| Attesi con **l'uptime realmente tenuto (56%)** | **4,6** |
| **Osservati** | **2** |

P(≤2 ingressi con l'uptime reale) = **12,5%**. **L'uptime è costato circa 3,7 ingressi del momentum**, ed è la ragione per cui il cancello 1(a) è fermo a **2 su 3** alla dodicesima seduta.

> **E il cancello 1(b) è a ZERO su DODICI.** Il terminale non è mai stato acceso alle 21:55 italiane. Il **31/08 è stato spento alle 21:44:56: undici minuti prima.**

### 14.9 Stato dei cancelli e cosa succede adesso

| Cancello | Stato al 08/09 | Sulle 3 sedute rimaste |
|---|---|---|
| **1(a)** ≥3 ordini IM dal vivo | **2 su 3** (24/08 e 04/09) | P = **92,1%** con uptime pieno |
| **1(b)** ≥1 chiusura EoD 22:55 osservata | **0** | P = **77,5%** con uptime pieno · **ZERO** con l'uptime tenuto finora |
| **1(c)** nessuna guardia per errore, nessun ordine fallito, nessun doppio trade | ✅ verde (nota §14.7b) | — |
| **1(d)** osservazioni da terminale acceso | in corso | — |
| **1(e)** riancoraggi | ✅ **8 su 8** con la build P, nessuna riga di ATTENZIONE | — |
| **2 — veto di regime ≥ −5.000** | **−6.464,72: ROSSO** | P(rientro) = 24% |

> **La regola pre-registrata del §12.4 (fissata il 30/08, con 9 sedute ancora da giocare) diventa operativa.**
> Meccanica verde + veto rosso → **non si compra**; il forward **prosegue per altre 15 sedute** con la **stessa identica configurazione**; il criterio si applica **una seconda e ultima volta** sulla somma cumulativa delle **30 sedute** con soglia **−6.437 $**; se ancora rosso, **il progetto si ferma**.
> **P(secondo verdetto verde | edge storico intatto), da dove siamo: ≈ 50%.** Mediana della somma a 30 sedute: −6.382 $.
> Si applica **comunque** anche il cancello 1(d) riformulato: se 1(a) e 1(b) non sono soddisfatti all'11/09, il forward si prolunga finché non lo sono. **Le due regole convergono sulla stessa azione.**

### 14.10 Esito
**Sedute 7-12 CERTIFICATE. Nessuna anomalia meccanica**: quadratura al centesimo su tutti e sei i trade, riancoraggio 5/5 (8/8 con la build P), build corretta provata dal commento d'ordine, nessuna guardia scattata, nessun ordine fallito, nessun doppio trade, esecuzione migliore dell'atteso.
**Il veto è sforato, ma la serie non è statisticamente anomala** (5°-12° percentile, LR 2,19:1).
**Le tre sedute rimaste servono solo ai cancelli meccanici, non al veto.** L'unica cosa che le rende utili è tenere il terminale acceso fino alle 22:15.

---

## 15. SEDUTE 13→15 — dal 09 all'11/09/2026 — **CERTIFICATE (15/15)** — FORWARD CHIUSO

Custodia: `20260909_experts` `0edb5e0b0e44b58f4987860b6812c8c1` · `20260909_journal` `c9bd31787e74c5ce913e5d81db0c9eaf` · `20260910_experts` `937b7e4118474d2cd68cc43792771a77` · `20260910_journal` `05488ab8b4c3dd7288108f1305674821` · `20260911_experts` `ed19eeb57287a949dd15a47a0822207f` · `20260911_journal` `c2bb199d214a71e8ecd5b689ab1135ae` · `CronoStoria_20260911.xlsx` `8cd7f9d95ec67b49e01d0e514a30ceab`.
**Controllo di custodia superato**: l'experts del 08/09 riconsegnato ha md5 `0f83256b96ab3c26c654fe9a2f0932ac`, **identico** a quello già agli atti. Il journal del 08/09 è invece **più lungo** (`aead52b37215d751e17032c484d432eb` contro `7ad4ec74…`): il primo export era stato fatto a giornata in corso. Il nuovo è un **sovrainsieme** e corregge il §14.8 (vedi 15.6).

### 15.1 I due trade, al centesimo — **36 assert su 36 superati**

| Trade | dist | lotti | slip ingresso | uscita | rischio | R |
|---|---|---|---|---|---|---|
| 09/09 ORB LONG | 36,1510 | 9,57 ✓ | **−1,20** *(favorevole)* | STOP 18:09:32 srv | 345,97 | **−1,0207** |
| 10/09 ORB LONG | 34,8320 | 9,42 ✓ | **−6,50** *(favorevole, il più grande del forward)* | **EoD 22:55:00 srv** | 328,12 | **+1,3780** |
| 11/09 | — | — | — | **SKIP doji** (corpo 3,3% del range) | — | — |

Assert verificati su **tutti e 8** i trade del conto 2, non solo sui nuovi:
- **lotti = `floor₂( 5%×(bilancio−90.000) / dist )` → 8 su 8.** *La convenzione è il TRONCAMENTO a 2 decimali, non l'arrotondamento: dimostrato dal 31/08 (500/38,9825 = 12,8262 → **12,82**, non 12,83) e dall'01/09 (12,3769 → **12,37**). Prima non era mai stata isolata.*
- **SL riancorato = `fill ∓ dist`** e **TP riancorato = `fill ± 8·dist`**, al centesimo → 2 su 2.
- **TP dell'ordine = `prezzo richiesto ± 8·dist`**, al centesimo → conferma che il prezzo richiesto ricostruito dallo SL dell'ordine è quello vero.
- **P&L = `lotti × (uscita − fill)`** → 8 su 8.
- **Bilancio ricostruito 97.018,85 = CronoStoria, al centesimo.**

### 15.2 ⭐ **IL CANCELLO 1(b) È VERDE — PRIMA CHIUSURA EoD OSSERVATA DAL VIVO**

> `2026.09.10 21:55:00.182  [ORB] Posizione chiusa (EoD close)`
> Journal: `21:54:59.985 market sell 9.42 close #539501983` → `21:55:00.179 deal #517383795 sell 9.42 at 29114.48 done`, ordine eseguito in **195,140 ms**. CronoStoria: uscita `2026.09.10 22:55:00` ora server.

**È l'unico meccanismo del progetto che non era mai stato verificato sul campo**, aperto dal 03/08/2026. Alla **quattordicesima seduta su quindici**, con il terminale acceso e una posizione aperta, l'`OnTimer` ha chiuso alle 22:55:00 server **al secondo**. Cancello **1(b): VERDE**. Cancello **1(d)**: l'osservazione proviene da terminale acceso al momento dell'evento → soddisfatto per 1(b).

**E ha fruttato**: uscita a 29.114,48 contro un fill di 29.066,48 = **+48,00 punti = +452,16 $ = +1,3780 R**. È il **primo trade in profitto dell'intero forward** e ha interrotto una serie di **14 perdite consecutive**.

> **Nota non secondaria**: alle 17:48:31 il terminale era stato spento **con la posizione aperta**; è stato riacceso alle 19:24:10, cioè **3 ore e 31 minuti prima della chiusura EoD**. Se non fosse stato riacceso, l'EoD non sarebbe scattata e il trade sarebbe rimasto aperto tutta la notte, fuori dal modello (§9.4). **Il +452,16 è stato messo in banca da una riaccensione fortuita, non da una procedura.**

### 15.3 **IL RIANCORAGGIO HA GIOCATO IN DIFESA — e questa volta poteva valere 719 $**
Il 10/09 lo slippage d'ingresso è stato **favorevole di 6,50 punti** (fill 29.066,48 contro un richiesto di 29.072,98). Conseguenza: lo SL allegato all'ordine (29.038,15) si trovava a soli **28,33 punti** dal fill invece che a 34,832 — cioè **uno stop più stretto dell'86,4%** del voluto, con rischio effettivo 266,87 $ invece di 328,12. Il riancoraggio lo ha **allontanato** a 29.031,65, riportando il rischio a 1,00 R esatto.
**Se in giornata il minimo fosse sceso fra 29.031,65 e 29.038,15, la versione non riancorata sarebbe stata fermata a −266,87 $ invece di chiudere a +452,16: una differenza di 719,03 $ su un solo trade.** *Non verificabile senza i dati M1 del 10/09 — resta un controllo eseguibile.* È l'immagine speculare del 26/08, quando lo stesso meccanismo costò 45 $: **metà delle volte fa risparmiare, metà costa. Il valore è nella varianza tolta, non nella media** (§7.3, confermato).

### 15.4 **RIANCORAGGIO 10 SU 10 con la build P**
Ordine vs Posizione nella CronoStoria: 09/09 `29419.93→29418.73` · 10/09 `29038.15→29031.65`. Entrambi diversi ⇒ `PositionModify` eseguita. Commento d'ordine `ORB 08-22-P` su entrambi ✓.
**Nessuna riga `*** ATTENZIONE: posizione NON leggibile dopo l'invio ***` in tutto il forward.** **Cancello 1(e): VERDE, 10 su 10.**
La riga `[ORB] posizione visibile dopo attesa` — prova diretta che la correzione 5.14 ha lavorato — è comparsa **3 volte** (27/08 ×2, **08/09**), l'ultima risolta in ~57 ms. Sulle build O quei tre riancoraggi sarebbero stati persi in silenzio.

### 15.5 CONTABILITÀ FINALE — **il veto di regime è ROSSO**

| Seduta | Data | Risultato | Bilancio conto 2 |
|---|---|---|---|
| 7-12 | 31/08 → 08/09 | −3.080,18 | 96.919,82 |
| **13** | **09/09** | **−353,13** | **96.566,69** |
| **14** | **10/09** | **+452,16** | **97.018,85** |
| **15** | **11/09** | **0,00** (SKIP doji) | **97.018,85** |

> **RISULTATO FORWARD (regola contabile §8.2)**
> = (96.113,02 − 99.497,56) + (97.018,85 − 100.000,00) = **−3.384,54 + (−2.981,15) = −6.365,69 $**
> **Veto di regime (≥ −5.000 $): ROSSO, sforato di 1.365,69 $.**

15 sedute · 13 segnali ORB (2 SKIP doji) + 2 ingressi IM = **15 trade: 14 perdite e 1 vincita**. Conto 2: profit factor 0,132, DD massimo di bilancio 3.433,31 (3,43%), 7 perdite consecutive.

### 15.6 **QUANTO È ANOMALO IL RISULTATO FINALE** — e perché non cambia la lettura

Bootstrap **per giornata intera** sulla sequenza congiunta (calendario cronologico ricostruito, 1.256 giornate, IM diradato al **58,3%** dell'uptime realmente tenuto — l'uptime appartiene alla nostra realtà, non all'ipotesi sotto test). 20.000 simulazioni, seed 7, seed-check 101.

| Blocco | P(risultato ≤ −6.365,69 con **edge intatto**) |
|---|---|
| giornate indipendenti | **3,33%** *(seed-check 3,75%)* |
| blocchi di 5 giornate | 3,08% |
| blocchi di 10 giornate | 2,65% |

| Ipotesi | P(≤ osservato) | LR contro «edge intatto» |
|---|---|---|
| Edge **intatto** | 3,33% | — |
| Edge **dimezzato** | 5,56% | **1,67 : 1** |
| Edge **nullo** | 7,99% | **2,39 : 1** |
| Edge **negativo** | 11,39% | 3,41 : 1 |

> **Siamo al 3° percentile: più in coda di quanto fossimo alla seduta 12 (4,84%), perché tre sedute in più spostano in alto la distribuzione di riferimento — non perché il risultato sia peggiorato (è migliorato di 99 $).**
> **Ma la verosimiglianza contro «edge nullo» resta 2,39 : 1, sotto la soglia di 3:1 della scala di Jeffreys: evidenza trascurabile.** Un risultato in coda è quasi altrettanto improbabile *anche* con edge nullo — ed è esattamente il motivo per cui il §12.4 dice che **il veto non è un test dell'edge**. La lettura non cambia: **sfortuna, non rottura dimostrata.**

### 15.7 IL SILENZIO DEL MOMENTUM — misurato, non ipotizzato
Frequenza storica: **742 ingressi su 1.256 giornate = 0,5908 per seduta** con uptime pieno (lo slot delle 17:00 server da solo vale 222 ingressi = il 29,9% del totale).

| | Ingressi IM su 15 sedute |
|---|---|
| Attesi con **uptime pieno** | **8,86** |
| Attesi con **l'uptime realmente tenuto (58,3%)** | **5,17** |
| **Osservati** | **2** |

P(≤2 ingressi con l'uptime reale, edge intatto) = **9,31%** *(bootstrap per giornata, 200.000 sim)*. **Basso ma non anomalo.** L'uptime spiega la maggior parte del silenzio (da 8,86 attesi a 5,17); il resto è varianza. **Ma il cancello 1(a) resta a 2 su 3.**

### 15.8 UPTIME — il quadro finale, con una correzione al §14.8

| Seduta | Terminale (ora locale) | Check IM | Acceso alle 21:55? |
|---|---|---|---|
| **12 (08/09)** | 15:37→17:38 · 18:31:54→**21:56:09** | **10/12** *(corretto da ~9)* | **SÌ** — ma nessuna posizione aperta |
| 13 (09/09) | 12:39→12:40 · 14:49→15:17 · 15:17→15:21 · 15:22→17:48 · 18:23→**23:14** | **11/12** | **SÌ** — ma posizione già chiusa allo stop alle 17:09 |
| 14 (10/09) | 14:54→17:48 · **19:24→22:07** | **9/12** | **SÌ, CON POSIZIONE APERTA → EoD OSSERVATA** |
| 15 (11/09) | 15:26→16:45 · 16:45→17:35 | **4/12** | NO — ma SKIP doji, nessuna posizione |

**Totale forward: 105 check su 180 = 58,3%.** *(Conto 1: 46/72. Conto 2: 59/108.)*
**Correzione a verbale del §14.8**: la seduta 12 risultava "~9/12, non documentato". Il journal completo del 08/09 prova che il terminale era acceso fino alle **21:56:09** e che i check eseguiti erano **10**. Il totale al 08/09 passa da 80/144 a **81/144**.
**Terminale acceso alle 21:55: 4 sedute su 15** (08, 09, 10/09 documentate + 28/08 probabile). **Tutte e quattro nelle ultime quattro settimane**: la disciplina è migliorata proprio alla fine — ed è bastata.

### 15.9 RILIEVI NUOVI

**(a) 10/09 — ⚠️ RILIEVO R1 OSSERVATO DAL VIVO CON UN NUMERO, per la prima volta.**
Riavvio alle 19:24:12 **con posizione aperta in profitto**. Il log stampa `EqRef: 97685.32` contro il bilancio d'inizio giornata di **96.566,69**: il riferimento del freno giornaliero si è spostato di **+1.118,63 $**, cioè esattamente il flottante del momento.
**Il verso del danno dipende dal segno del flottante al riavvio** — distinzione che R1 non conteneva:
- riavvio **in profitto** → riferimento più alto → freno **più severo** (innocuo, è il caso del 10/09);
- riavvio **in perdita** → riferimento più basso → freno **più permissivo**, che è la modalità di fallimento temuta.
R1 resta aperto, ma ora è **quantificato su un caso reale** e la mitigazione operativa («nessun riavvio volontario in seduta») ha una ragione misurata.

**(b) 09/09 — script `CalendarDump` in esecuzione sul grafico dell'ORB durante la finestra d'ingresso. Violazione del §13.**
Journal: `15:34:24.987 script CalendarDump (US100.cash, M5) loaded successfully`; l'ORB entra alle `15:34:59.724`. **Lo script stava girando sullo stesso grafico dell'EA al momento dell'invio dell'ordine.** Nessun danno (EA non scaricato, ingresso al secondo giusto, ordine eseguito in 215,096 ms), ma è precisamente la classe di azione che la regola «mani giù 15:35–15:40» vieta. Aggravante: quel giorno il terminale era stato chiuso e riaperto **quattro volte** fra le 12:39 e le 15:22. **Da non ripetere: nessuno script, nessun tester, nessun riavvio dalle 15:25 in poi.**

**(c) Il `WARNING: volume candela apertura NON anomalo` è ormai un rumore: 3 falsi positivi su 5 sedute** (04/09 NFP, 10/09, 11/09). Tutti e tre smentiti dalla CronoStoria, che data l'ordine alle 16:35:00 server. La guardia rileva «dato macro pre-apertura», non «orario sessione errato». **A verbale: il controllo, nella forma attuale, non è informativo.** Nessuna modifica al codice — l'orario è verificato in modo indipendente e più forte (ora d'ingresso nella CronoStoria).

**(d) 09/09 — uscita allo stop alle 18:09:32 server, 1h34' dopo l'ingresso**, con slippage **+0,75 pt = +2,07%** della distanza. Dentro la norma.

**(e) Terminale stabile su build 6182** per tutte e tre le sedute, nessun aggiornamento nuovo. Una caduta di rete il 09/09 alle 23:01:05, riparata in 53 secondi, **fuori sessione e senza posizioni**.

### 15.10 SERIE DI ESECUZIONE — FINALI

| Grandezza | Backtest | Misurato (forward completo) |
|---|---|---|
| **Slippage d'ingresso ORB (n=16)** | — | media **−0,03 pt**. Serie: +2,10 / +2,84 / −0,50 / +3,80 / +0,30 / −0,50 / −4,60 / −0,70 / −0,30 / +0,30 / +3,81 / −0,19 / +0,40 / +0,50 / **−1,20 / −6,50** |
| **Slippage sullo stop (n=15)** | media **2,25%** della distanza | media **+0,573 pt = 1,44%**. Peggiore **+4,02%** (27/08) |
| Commissioni | — | **0,00 su 16 trade su 16** |
| Swap | — | +1,24 in tutto il forward (una sola notte, 24/08) |
| Tempi di esecuzione ingresso (n=9) | — | media **223,2 ms** (215,1 e 251,8 i due nuovi) · chiusura EoD **195,1 ms** · modify di riancoraggio 77,1 e 241,9 ms |
| Spread all'ingresso | mediana storica 1,45 | **1,45** su tutti e 16 |

> **L'aperto n.6 si CHIUDE**: lo slippage d'ingresso è **casuale e centrato su zero** (media −0,03 pt su 16 osservazioni), non sistematico. Resta la **dispersione**, che è esattamente ciò che il riancoraggio elimina.
> **L'aperto n.7 resta aperto sulla CODA**: la media (1,44%) è metà dell'attesa, ma con n=15 il 9,4% di casi oltre il 5% e i 3 su 778 oltre il 20% restano non campionati.

### 15.11 ESITO DEL FORWARD — I CANCELLI

| Cancello | Esito | Prova |
|---|---|---|
| **1(a)** ≥3 ordini IM dal vivo | ❌ **2 su 3** | 24/08 e 04/09. Attesi 5,17 con l'uptime tenuto; P(≤2) = 9,31% |
| **1(b)** ≥1 chiusura EoD 22:55 osservata | ✅ **VERDE** | 10/09 21:55:00.182, terminale acceso, +452,16 $ |
| **1(c)** nessuna guardia per errore, nessun ordine fallito, nessun doppio trade | ✅ **VERDE** | zero guardie scattate, zero ordini rifiutati, zero doppi trade in 15 sedute |
| **1(d)** osservazioni da terminale acceso | ✅ per 1(b) · ❌ per 1(a) | — |
| **1(e)** riancoraggi | ✅ **VERDE, 10 su 10** | nessuna riga di ATTENZIONE in tutto il forward |
| **2 — veto di regime ≥ −5.000 $** | ❌ **ROSSO: −6.365,69** | sforato di 1.365,69 |

### 15.12 COSA SCATTA ADESSO — due regole, **una sola azione**

1. **Cancello 1(a) non soddisfatto** → riformulazione 1(d), pre-registrata il 27/08: *«se all'11/09 quei due cancelli non sono soddisfatti, il forward si prolunga finché non lo sono. Non si abbassa l'asticella: si continua a misurare.»*
2. **Veto ROSSO con meccanica per il resto verde** → regola pre-registrata del **30/08**: non si compra; il forward **prosegue per altre 15 sedute**, **stessa identica configurazione, nessun filtro nuovo**; il criterio si applica **una seconda e ultima volta** sulla somma cumulativa delle **30 sedute** con soglia **−6.437 $**; se ancora rosso, **il progetto si ferma** e il regime diventa ricerca. **Nessun terzo tentativo.**

> **Le due regole convergono: SI CONTINUA. Non si compra la challenge questa settimana.**
> **Il numero operativo**: `−6.437 − (−6.365,69)` = **le prossime 15 sedute devono dare almeno −71,31 $.**
> **P(secondo verdetto VERDE | edge storico intatto) = 49,4%** *(seed-check 49,1%)*; mediana delle prossime 15 sedute **−145 $**, p25 −2.858, p75 +3.867. Se l'edge fosse **dimezzato**: 44,0%. Se fosse **nullo**: 38,5%.
> *Il criterio discrimina poco — era noto e messo a verbale il 30/08: «il veto è simmetricamente non informativo». Si applica perché è pre-registrato, non perché sia potente.*

### 15.13 REGIME 2026 — l'aperto n.10, aggiornato coi 15 trade del forward

| | Backtest 2026 | **Con i trade del forward** |
|---|---|---|
| ORB | +9,26R su 129 (+0,0718/trade) | **−1,56R su 142 (−0,0110/trade)** |
| IM | −7,45R su 97 (−0,0768/trade) | −11,48R su 99 |

**IC95% dell'ORB 2026+forward: [−0,4075 ; +0,3855]** — contiene lo zero **e** contiene +0,1784. **Con 142 trade non si distingue nulla**: servono 890 trade per separare l'edge da zero al 95%. L'aperto n.10 resta **apertissimo in entrambe le direzioni**, esattamente come prima. *Il forward non ha aggiunto informazione sull'edge: non poteva, per costruzione.*

### 15.14 Esito
**Sedute 13-15 CERTIFICATE. FORWARD CHIUSO A 15 SU 15.**
**Meccanica: 4 cancelli su 5 verdi**, incluso il 1(b) che era aperto dall'inizio del progetto. Quadratura al centesimo su 8 trade su 8, riancoraggio 10/10, zero anomalie di esecuzione, esecuzione FTMO migliore del modello su ogni metrica misurata.
**Veto: ROSSO a −6.365,69 $**, statisticamente non anomalo (3° percentile, LR 2,39:1 = evidenza trascurabile).
**Azione: il forward si estende di 15 sedute. Non si compra.**

---

## 16. SEDUTE 16→20 — dal 14 al 18/09/2026 — **CERTIFICATE (20/30)** — conto 3 · ⭐ **CANCELLO 1(a) CHIUSO**

Custodia: `CronoStoria_20260918.xlsx` `512a396572a13ebc15f4f37c95bae563`. Conto 3: **1514618793**, aperto il 14/09 alle 12:05:05 server con **100.000,00** (confermato dal deal `Initial account balance`).

### 16.1 ⭐ IL CANCELLO 1(a) È VERDE — terzo e quarto ordine dell'IM dal vivo

> `2026.09.15 17:00:02  [IM] entry SHORT lots=5.45 dist=91.6`   → **18:00:01 ora server** (3° check)
> `2026.09.16 16:00:02  [IM] entry LONG  lots=13.71 dist=31.7`  → **17:00:01 ora server** (1° check)
>
> ⚠️ *I log Experts/Journal timbrano in **ora locale**, la CronoStoria in **ora server** (locale +1h). Le due righe qui sopra sono del log, quindi locali; i riferimenti orari nel resto di questo paragrafo sono server.*

Erano fermi a **2 su 3 dal 4 settembre**. **Con questi due, TUTTI E CINQUE I CANCELLI MECCANICI SONO VERDI** per la prima volta da quando esiste il criterio D. Il forward ha finito il lavoro per cui era nato: misurare il rischio **meccanico** di far girare dal vivo due EA che non erano mai stati in produzione.

### 16.2 I quattro trade, al centesimo

⚠️ **Nota metodologica**: l'ATR stampato nel log è arrotondato a 2 decimali, quindi la distanza non è ricostruibile esattamente da lì. Ho risolto `dist` e il **prezzo richiesto** come incognite dal sistema di quattro equazioni date da SL e TP dell'**ordine** e della **posizione**. Soluzione unica in entrambi i casi ORB, e coincide con lo slippage stampato dall'EA al centesimo.

| Trade | dist | lotti | slip ingresso | uscita | rischio | R |
|---|---|---|---|---|---|---|
| **15/09 ORB SHORT** | 36,5161 | 13,69 ✓ | **−1,49** *(favorevole)* | STOP 16:38:46 srv | 499,91 | **−0,9985** |
| **15/09 IM SHORT** | 91,635 | 5,45 ✓ | **−1,70** *(favorevole)* | **chiusa il 16/09 alle 11:31:33 srv** | 998,82 *(2×dist)* | **−1,3052** |
| **16/09 IM LONG** | 31,700 | **13,71 (cap notional)** | **−1,75** *(favorevole)* | **RIENTRO IN BANDA 17:30:00 srv** | 869,21 *(2×dist)* | **−0,8347** |
| **17/09 ORB SHORT** | 37,6753 | 11,26 ✓ | **+0,01** | STOP 16:54:14 srv | 424,22 | **−1,0686** |

Assert superati: lotti da `floor₂(5%×(bilancio−90.000)/dist)` · SL e TP riancorati al fill · SL e TP dell'ordine dal prezzo richiesto · P&L `= lotti × (uscita − fill)` · **bilancio ricostruito 98.032,57 = CronoStoria, al centesimo.**

**Sedute senza trade**: 14/09 `SKIP: doji (body 0.4% del range)` · 16/09 e 18/09 `SKIP: ampiezza candela1 10.6% / 10.2% ATR`. Tre SKIP su cinque sedute.

### 16.3 ⭐ PRIMA USCITA "RIENTRO IN BANDA" DELL'IM OSSERVATA DAL VIVO
Il 16/09 l'IM è entrato LONG alle 17:00 server ed è uscito **al check successivo delle 17:30** perché il prezzo era rientrato sotto la banda alta: `market sell 13.71 close #543646463`, eseguito in 199 ms.
**È l'uscita più frequente del sistema — 282 su 742 nel backtest (38%) — e non era mai stata vista dal vivo.** Prima di oggi avevamo osservato solo stop protettivi. **Il meccanismo semi-orario funziona come progettato.**

### 16.4 IL CAP NOTIONAL MORDE PER LA SECONDA VOLTA
16/09: sizing nominale `500 / 31,70 = 15,77 lotti`; cap `4 × 100.000 / p`. Risultato **13,71 lotti**, rischio effettivo **434,61 $ invece di 500**.
*(Il cap usa `p = iClose(M1,1)`, il prezzo del segnale, non l'ask: ricostruendolo dall'ask si ottiene 13,70 e non 13,71. Dettaglio verificato, non un'anomalia.)*
Il 15/09 invece il cap era **inattivo** (13,83 disponibili contro 5,46 richiesti): con `dist` di 91,6 punti il sizing è naturalmente piccolo. **Il rilievo N2 è confermato: morde sulle distanze corte, sempre a nostro favore.**

### 16.5 ⚠️ IL PC SPENTO CON LA POSIZIONE IM APERTA — e la rete di sicurezza che ha funzionato

`2026.09.15 18:01:11  System  terminal stopped due to system shutdown`

La posizione IM short da 5,45 lotti, aperta alle 17:00 server, è rimasta aperta tutta la notte. Alla riaccensione:

```
2026.09.16 10:31:19  terminal synchronized ...: 1 positions
2026.09.16 10:31:34  market buy 5.45 US100.cash, close #542798431   -> eseguito in 203,981 ms
```

**È il FIX1 dell'IM osservato dal vivo per la prima volta**: `OnTimer` legge `POSITION_TIME` dal server, vede che la posizione è di un giorno precedente e la chiude (`posizione di un giorno precedente`). **Comportamento corretto, immediato, senza intervento manuale.** Il meccanismo che esiste proprio perché le variabili in memoria si azzerano a ogni riavvio ha fatto esattamente il suo mestiere.

**Il costo**: uscita a 29.052,18 contro un ingresso a 28.932,58 → **−651,82 $ = −1,3052 R**, contro un massimo teorico di −2R.
**Lo stop protettivo a 29.115,85 non è mai stato toccato durante la notte** — se lo fosse stato, il server avrebbe chiuso e non avremmo trovato la posizione aperta la mattina.
⚠️ **Quanto sia costato davvero NON è determinabile con i dati che abbiamo**: l'EoD delle 22:55 avrebbe chiuso a un prezzo che non conosciamo. **Controllo eseguibile**: basta esportare le barre M1 di US100.cash dal 15/09 22:00 al 16/09 11:00 e si chiude la domanda. *A differenza del 24/08, questa volta non possiamo nemmeno stabilire il segno.*

### 16.6 ⚠️ LO SWAP HA SEGNO OPPOSTO ALL'UNICA MISURA PRECEDENTE
| Data | Direzione | Lotti | Swap | Per lotto |
|---|---|---|---|---|
| 24/08 | short | 3,64 | **+1,24** *(a credito)* | **+0,34 $** |
| **15/09** | **short** | **5,45** | **−0,37** *(a debito)* | **−0,068 $** |

**Stesso strumento, stessa direzione, segno opposto.** Due osservazioni in due mesi non fanno una stima: lo swap su US100.cash **non è una costante** e va trattato come ignoto finché non se ne raccolgono abbastanza. *Il documento dei costi d'esecuzione già avvertiva che una sola osservazione non basta: ora è dimostrato.*

### 16.7 ⚠️ SLIPPAGE SULLO STOP +6,85% — IL PEGGIORE MAI OSSERVATO, E LA CODA COMINCIA A VEDERSI
Il 17/09 lo stop è stato eseguito a **29.376,38** contro un livello di **29.373,80**: **+2,58 punti = +6,85% della distanza**. Il precedente record era +4,02% (27/08).

| | Prima | **Ora** |
|---|---|---|
| n | 14 | **16** |
| media | +1,44% | **+1,67%** |
| peggiore | +4,02% | **+6,85%** |
| oltre il 5% | **0 su 14** | **1 su 16 = 6,2%** |

**Il backtest attende il 9,4% dei casi oltre il 5%.** Con 1 su 16 siamo dentro. **Il modello di costo regge**: non è un'anomalia, è la coda che finalmente si campiona. *Resta non campionata la coda estrema — 3 casi su 778 oltre il 20% nel backtest.*

**E nella stessa settimana il primo stop FAVOREVOLE della storia del forward**: il 15/09 uscita a 29.107,58 contro SL 29.107,64 → **−0,06 pt = −0,16%**, eseguito **meglio** del livello.

### 16.8 SERIE DI ESECUZIONE AGGIORNATE
- **Slippage d'ingresso, n = 20**: media **−0,27 pt**, dev.st 2,46, 9 sfavorevoli su 20. **Le quattro misure di questa settimana sono tutte favorevoli o nulle** (−1,49 / −1,70 / −1,75 / +0,01). *L'aperto n.6 resta chiuso: è rumore centrato su zero.*
- **Riancoraggio: 14 su 14.** Il 15/09 è comparsa di nuovo la riga `posizione visibile dopo attesa: riancoraggio possibile (fill 29071.12)` — **quarta volta su 20 ingressi**: la condizione di gara della trappola 5.14 si ripresenta nel 20% dei casi, e l'attesa la risolve ogni volta. **Con le build O/D sarebbero quattro riancoraggi persi in silenzio.**
- **Nessuna riga di ATTENZIONE** in 20 sedute. Commissioni **0,00 su 20 trade su 20**.
- Tempi di esecuzione: ordini a mercato 281,958 / 306,333 / 283,934 / 247,841 / 203,981 / 199,090 ms; `PositionModify` 83,458 / 109,167 / 239,365 / 119,079 ms.

### 16.9 CONTABILITÀ — la somma a 20 sedute

| Seduta | Data | Risultato | Bilancio conto 3 |
|---|---|---|---|
| 16 | 14/09 | **0,00** (SKIP doji) | 100.000,00 |
| 17 | 15/09 | **−1.151,33** (ORB −499,14 · IM −651,82 · swap −0,37) | 98.848,67 * |
| 18 | 16/09 | **−362,77** (IM, rientro in banda) | 98.485,90 |
| 19 | 17/09 | **−453,33** (ORB) | 98.032,57 |
| 20 | 18/09 | **0,00** (SKIP ampiezza) | **98.032,57** |

\* *Convenzione già usata per il 24/08: il trade IM aperto il 15/09 è stato chiuso il 16/09 alle 11:31:33 server, quindi a fine giornata 15/09 il bilancio era ancora **99.500,86** con la posizione aperta. L'attribuzione alla seduta d'apertura è una convenzione di lettura: **non incide sulla somma cumulativa**, che è calcolata sui bilanci di conto e non per seduta.*

> **REGOLA CONTABILE A N CONTI** *(pre-registrata il 14/09, prima che il conto 3 producesse un numero)*
> `(96.113,02 − 99.497,56) + (97.018,85 − 100.000,00) + (98.032,57 − 100.000,00)`
> = −3.384,54 + (−2.981,15) + (−1.967,43) = **−8.333,12 $** su 20 sedute.
>
> **Soglia pre-registrata sulle 30 sedute: −6.437 $.**
> **Le ultime 10 sedute devono dare almeno `−6.437 − (−8.333,12)` = +1.896,12 $.**

**P(secondo verdetto VERDE | edge storico intatto) = 29,9%** *(seed-check 29,6%)*; **33,3%** se a metà percorso si riparte da un conto nuovo a 100.000, perché il buffer torna a 500 $/trade e aumenta la varianza. Mediana delle prossime 10 sedute: **−188 $** · p25 −2.186 · p75 +2.604 · p90 +6.226.
Se l'edge fosse **dimezzato**: 26,4%. Se fosse **nullo**: 23,3%.

*Al 14/09 la stessa probabilità era 49,4%. È scesa di venti punti in una settimana.*

### 16.9-bis CHI STA PERDENDO — scomposizione per EA su tutte e 20 le sedute

| | Trade | Somma | Vincenti | Media in R | Backtest |
|---|---|---|---|---|---|
| **ORB** | 15 | **−5.492,42 $** | **1 su 15** | **−0,757** *(sui 9 con R verificato al centesimo)* | +0,1784 |
| **IM** | 4 | **−2.840,33 $** | **0 su 4** | **−1,542** | +0,1437 |
| swap | — | −0,37 $ | — | — | — |
| **TOTALE** | **19** | **−8.333,12 $** | **1 su 19** | — | — |

> **Il calo NON è concentrato su un solo sistema: perdono entrambi, e l'IM di più per trade.** Questo esclude la spiegazione più comoda — «è colpa del momentum, basta spegnerlo» — e insieme la sua speculare. *Con 4 trade l'IM non dice nulla di statisticamente leggibile; l'ORB con 15 nemmeno (ne servono 890).*

### 16.10 QUANTO È ANOMALA LA SOMMA A 20 SEDUTE

| Ipotesi | P(≤ −8.333,12) | LR contro «edge intatto» |
|---|---|---|
| Edge **intatto** | **2,04%** *(seed-check 2,27%)* | — |
| Edge **dimezzato** | 3,75% | 1,83 : 1 |
| Edge **nullo** | 6,04% | **2,95 : 1** *(5 semi indipendenti: 2,69 / 2,72 / 2,94 / 2,99 / 3,01 — media **2,87**, range [2,69 ; 3,01])* |
| Edge **negativo** | 9,02% | 4,41 : 1 |

> **Siamo al 2° percentile.** La verosimiglianza contro «edge nullo» è salita da **2,39 : 1** (15 sedute) a **≈ 2,9 : 1** — **esattamente sulla soglia di 3:1 della scala di Jeffreys**, il confine fra «evidenza trascurabile» e «evidenza debole». *Verificata su 5 semi indipendenti (range 2,69-3,01) e su tre ipotesi di uptime nel modello nullo (2,70-2,97): il numero è robusto, e il fatto che stia sul confine non è un artefatto del seme.*
> **Non è ancora una prova che l'edge sia rotto, ma non è più solo sfortuna neutra.** Va detto chiaramente: se la prossima settimana somiglia a questa, l'LR supera il 3:1 e il quadro cambia qualitativamente. **Il criterio non si tocca comunque**: il numero va conosciuto, non usato per spostare l'asticella.

### 16.11 UPTIME — migliorato, e per la prima volta il momentum è allineato all'atteso

| Seduta | Terminale (ora locale) | Check IM | Acceso alle 21:55? |
|---|---|---|---|
| 16 (14/09) | 11:16→17:41 · 17:42→18:00 · 18:49→**21:52:11** | 11/12 | **NO — mancati 3 minuti** |
| 17 (15/09) | 14:26→**18:01 (shutdown del PC, con posizione aperta)** | 5/12 | NO |
| 18 (16/09) | 10:31→11:10 · 12:25→18:04 · 18:45→21:14 · 21:44→**21:48:55** | 10/12 | **NO — mancati 6 minuti** |
| 19 (17/09) | 14:35→17:58 | 4/12 | NO |
| 20 (18/09) | 12:10→oltre le 23:01 | **12/12** | **SÌ** *(nessuna posizione aperta)* |
| | | **42/60 = 70%** | 1 su 5 |

**Cumulativo 20 sedute: 147/240 = 61,3%** (era 58,3%).

| | Ingressi IM in queste 5 sedute |
|---|---|
| Attesi con uptime pieno | 2,95 |
| Attesi con l'uptime tenuto (70%) | **2,07** |
| **Osservati** | **2** |

**Per la prima volta l'IM è esattamente dove doveva essere.** Il "silenzio del momentum" delle settimane scorse era uptime, non l'EA: adesso che l'uptime è salito, gli ingressi sono arrivati. **Questione chiusa.**

⚠️ **Ma due sere su cinque il terminale è stato spento a 3 e 6 minuti dalle 21:55.** Il cancello 1(b) è già verde, quindi non costa più nulla — ma è la stessa abitudine che lo ha tenuto a zero per tredici sedute.

### 16.12 RILIEVI MINORI
**(a) Cambio conto gestito correttamente.** 14/09 11:17:30 `automated trading is disabled because the account has been changed` → **11:17:53 `automated trading is enabled`**, riabilitato a mano in 23 secondi. **Trappola 5.10 neutralizzata.** Il conto 2 risultava `trading has been disabled - disabled on server`: free trial scaduto.
**(b)** `MCP bind error on 127.0.0.1:22346 [(10048)]` il 15/09 alle 14:26: la porta era ancora occupata dall'istanza chiusa alle 11:55. Innocuo, nessun effetto sul trading. A verbale.
**(c)** Quattro cadute di rete (14/09 ×3, 16/09 ×2, 18/09 ×1), tutte riparate automaticamente in pochi secondi, **nessuna con posizione aperta in momenti critici**. Una il 16/09 alle 16:21:50, con la posizione IM aperta: alla riconnessione `1 positions`, nessun effetto.
**(d)** Il 16/09 l'EqRef è stato letto tre volte diverso nella stessa giornata (98.852,48 → 98.848,67 → 98.485,90): sono i riavvii che riagganciano `g_dailyRefEq` all'equity del momento — **rilievo R1, nella sua forma benigna**.

### 16.13 IL MIO ERRORE — il decimo a verbale
Il primo verificatore automatico che ho scritto per queste sedute ha segnalato **4 assert falliti**, tutti da 0,01. Non erano errori degli EA: avevo **invertito il segno** nella ricostruzione del prezzo richiesto (`entry = SL + s·dist` invece di `SL − s·dist` con la convenzione del sorgente), e in più usavo l'arrotondamento bancario di Python invece di quello di `NormalizeDouble`. Rifatto risolvendo `dist` e il prezzo richiesto **come incognite** dal sistema dato da SL e TP di ordine e posizione: **soluzione unica, e coincide con lo slippage stampato dall'EA al centesimo su entrambi i trade ORB**.
**Trovato e corretto prima della consegna, ma va dichiarato**: per qualche minuto ho creduto a quattro discrepanze che non esistevano. *Lezione: quando un verificatore segnala errori tutti della stessa identica grandezza, il sospettato numero uno è il verificatore.*

### 16.14 ESITO
**Sedute 16-20 CERTIFICATE. Forward a 20 su 30.**
⭐ **MECCANICA: TUTTI E CINQUE I CANCELLI VERDI.** Cancello 1(a) chiuso con il terzo e quarto ordine IM; prima uscita "rientro in banda" osservata; prima esecuzione della rete di sicurezza al riavvio; riancoraggio 14/14; zero righe di ATTENZIONE in 20 sedute.
**Veto: −8.333,12 $.** Servono **+1.896,12** dalle ultime 10 sedute: **P ≈ 30%**.
**Non si tocca niente. Si continua fino alla seduta 30.**

---

## 17. SEDUTE 21→25 — dal 21 al 25/09/2026 — **CERTIFICATE (25/30)** — conto 3 chiuso · ⭐ **il Free Trial si è concluso per obiettivi raggiunti**

Custodia: `Cronistoria.xlsx` (report del 2026.09.26 12:49, conto 1514618793, 18 trade dal 15/09) md5 `296de624542d1bd3d161aee9bd97c209`. Log Experts e Journal dal 21 al 26/09 e `metaeditor.log`: **incollati in chat, non consegnati come file** → nessun md5. *Lacuna di custodia a verbale: vanno archiviati come file con la rinomina `AAAAMMGG_experts.log` / `AAAAMMGG_journal.log`.*
Build in esecuzione: `metaeditor.log` data l'ultima compilazione di `ORB_US100_-_step16_P` al **2026.08.25 17:20:01** e di `IntradayMomentum_NAS100_E` al **17:19:08**, nessuna ricompilazione da allora. Commenti d'ordine `ORB 08-22-P` e `IM 08-22-E` su tutti e sette gli ingressi (regola 5.9) ✓.

### 17.1 I sette trade, al centesimo — **tutti gli assert superati**

| Trade | dist | lotti | slip ingresso | uscita | rischio (lotti × dist) | R |
|---|---|---|---|---|---|---|
| 21/09 IM LONG | 136,77 | 3,65 ✓ | **−0,40** | **EoD** 22:55:15 srv @ 30.490,68 | 499,21 | **+2,6808** |
| 22/09 ORB LONG | 42,0300 | 11,14 ✓ | +0,70 | **EoD** 22:55:00 @ 30.725,42 | 468,21 | **+3,7935** |
| 22/09 IM LONG n.1 | 74,72 | 6,69 ✓ | +0,20 | **banda** 19:00:00 @ 30.609,43 | 499,88 | −0,2563 |
| 22/09 IM LONG n.2 *(check delle 20:30)* | 42,25 | 11,83 ✓ | −0,50 | **EoD** 22:55:12 @ 30.724,72 | 499,82 | **+1,7027** |
| 23/09 ORB SHORT | 42,8167 | 13,86 ✓ | −0,99 | **catch-all** 24/09 01:05:01 @ 30.496,07 | 593,44 | **+3,1051** |
| 23/09 IM SHORT | 73,595 | 6,79 ✓ | +0,50 | **catch-all** 24/09 01:05:09 @ 30.492,67 | 499,71 | +0,7359 |
| 24/09 ORB LONG | 42,4067 | 16,60 ✓ | −1,30 | **EoD** 22:55:00 @ 30.484,32 | 703,95 | **+5,6180** |

Assert verificati:
- **Lotti ORB** = `floor₂(5% × (equity − 90.000) / dist)` → 3 su 3 (equity all'ingresso 99.370,84 · 101.869,22 · 104.082,28).
- **Lotti IM** = `floor₂(min(500/dist ; 400.000/p))` → 4 su 4; cap notional **mai attivo** questa settimana.
- **Riancoraggio**: SL ORB = `fill ∓ dist`, TP = `fill ± 8·dist`; SL IM = `fill ∓ 2·dist`, al centesimo.
- **P&L** = `lotti × (uscita − fill)` → 7 su 7.
- **Bilancio ricostruito 108.018,50 = CronoStoria, al centesimo** (inclusi swap e trade manuali, §17.6).

Metodo come al §16.2: per l'ORB `dist` e prezzo richiesto risolti come incognite da SL e TP dell'ordine (TP − SL = 9R); per l'IM lo slippage è la differenza fra SL della posizione e SL dell'ordine, e coincide al centesimo col `delta` stampato dall'EA (che però **non è corretto per la direzione**: sullo short del 23/09 il delta −0,50 è uno slippage **sfavorevole** di 0,50).

**Sedute senza trade dell'ORB**: 21/09 `SKIP: ampiezza candela1 10.7% ATR` (sotto il 12%). Ampiezza della candela 1 negli altri giorni: 24,7% · 20,1% · **13,5%** (il 24/09, a 1,5 punti dalla soglia). **IM**: nessun ingresso il 24/09 (apertura 30.225,1 contro chiusura precedente 30.476,0: gap di −0,82%, prezzo mai fuori banda ai check).

### 17.2 Riancoraggio **7 su 7** — con le build P/E ora **21 su 21**

| Trade | SL ordine → SL posizione |
|---|---|
| 21/09 IM | 29850.89 → **29850.49** |
| 22/09 ORB | 30523.25 → **30523.95** (TP 30901.52 → 30902.22) |
| 22/09 IM n.1 | 30478.94 → **30479.14** |
| 22/09 IM n.2 | 30568.78 → **30568.28** |
| 23/09 ORB | 30670.85 → **30671.84** (TP 30285.50 → 30286.49) |
| 23/09 IM | 30694.52 → **30694.02** |
| 24/09 ORB | 30204.97 → **30203.67** (TP 30586.63 → 30585.33) |

Tutti diversi ⇒ `PositionModify` eseguita ogni volta, in 55–215 ms. **Il fill stampato nel log coincide con la CronoStoria 7 volte su 7**: la correzione 5.3/5.14 funziona anche come strumento di misura. Nei log consegnati **nessuna riga `*** ATTENZIONE: posizione NON leggibile dopo l'invio ***`**.

### 17.3 ⭐ Tre meccanismi osservati dal vivo per la prima volta

1. **Prima chiusura EoD del MOMENTUM** — 21/09, 22:55:14 server, `market sell 3.65`, eseguita in 219,68 ms, **+1.338,27 $**. Fino a oggi l'EoD dal vivo era stata vista solo sull'ORB (10/09). Nella settimana le chiusure EoD osservate sono **quattro** (IM 21/09, ORB 22/09, IM 22/09, ORB 24/09), tutte fra 214 e 229 ms.
2. **Primo catch-all corretto dell'ORB** su una posizione del giorno precedente — 24/09 alle 01:05:00 server, al primo tick dopo la pausa notturna (§17.4). *Il catch-all del 06/08 era la versione difettosa (trappola 5.2); questo è il comportamento giusto, ancorato a `POSITION_TIME`.*
3. **Prima uscita a riapertura di mercato**: l'IM ha chiuso la sua posizione del giorno prima (FIX1) nello stesso minuto, dopo una serie di rifiuti `[Market closed]` durante la pausa.

Anche l'uscita **su banda** dell'IM si è ripetuta (22/09, check delle 19:00 server, 213 ms).

### 17.4 ⚠️ LA NOTTE DEL 23→24/09 — PC spento un'ora prima dell'EoD, con due posizioni aperte

`2026.09.23 20:55:28  terminal stopped due to system shutdown` *(ora locale = 21:55 server)*. Erano aperti **ORB short 13,86 lotti** e **IM short 6,79 lotti**. Nessuna delle due chiusure di fine giornata poteva avvenire.

| Ora (server) | Fatto |
|---|---|
| 24/09 00:37 | terminale acceso e richiuso in 17 secondi |
| 01:01:38 | terminale acceso, `2 positions` |
| **01:01:54 → 01:04:57** | l'IM riconosce la posizione del giorno prima e tenta di chiuderla: **~65 richieste, tutte `[Market closed]`** — raffiche di 5 tentativi ogni 15 s |
| **01:05:00** | primo tick dopo la pausa: catch-all dell'ORB, `buy 13.86` accettato dopo 1,1 s, **eseguito in 1.296 ms** @ 30.496,07 → **+1.842,69 $ (+3,1051 R)** |
| 01:05:09 | l'IM chiude `buy 6.79` in 189 ms @ 30.492,67 → **+367,75 $ (+0,7359 R)** |

Swap del rollover mercoledì→giovedì: **+1,76** e **+0,86** = **+0,127 $ per lotto** su entrambe, a credito.

**Terza notte overnight del forward, terza per PC spento** (24/08, 15/09, 23/09). Questa volta è andata bene, ma resta **fuori dal modello**: il backtest chiude sempre alle 22:55. Il prezzo alle 22:55 del 23/09 non è noto, quindi **non si può stabilire quanto l'EoD mancata sia costata o abbia reso** *(controllo eseguibile: barre M1 del 23/09 fra le 22:50 e le 23:00 server)*.
**Rischio corso, misurato**: con 20,65 lotti short (prezzo medio d'ingresso 30.602,00) e il riferimento giornaliero FTMO del 24/09 a 101.869,22, un gap di circa **+1,1%** alla riapertura avrebbe consumato **da solo** l'intero limite di perdita giornaliera di 5.000 $.
**R1 nel verso «severo»**: al riavvio delle 18:41 del 23/09 l'ORB ha stampato `EqRef 105.669,12`, cioè il bilancio più **+3.799,90** di flottante. Il suo freno giornaliero (1.500 $ da quel riferimento) avrebbe chiuso **entrambe** le posizioni su un semplice ritracciamento del profitto, con la giornata ancora in utile di ~2.300 $. Non è successo. **Anche il verso «benigno» di R1 ha un costo: può tagliare i vincitori.**

### 17.5 ⭐ 25/09 — IL CONTO È STATO DISABILITATO: il Free Trial si è concluso per obiettivi raggiunti

`2026.09.25 15:30:26` (primo collegamento dopo la sera del 24): `'1514618793': trading has been disabled - disabled on server` e `balance management has been disabled - disabled on server`. È lo stesso messaggio che il conto 2 mostrava il 14/09, quando era scaduto.

**Perché — ricostruzione.** Il Free Trial FTMO 2-Step **non ha gli obiettivi della challenge**: fonte ufficiale FTMO, *«The Profit Target is reduced from 10% to 5%. The Minimum Trading Days requirement is reduced from 4 to 2»*, durata 14 giorni. Il conto 3:
- ha raggiunto il **target del 5% (105.000) con tutte le posizioni chiuse il 24/09 alle 22:55:00 server**, alla chiusura EoD dell'ORB (bilancio 108.018,50);
- aveva **7 giorni di trading** su 2 richiesti;
- **non ha violato alcuna regola** (perdita giornaliera massima e perdita massima mai avvicinate);
- **sarebbe scaduto il 28/09** (aperto il 14/09): il blocco è arrivato **tre giorni prima** della scadenza.

> **Conclusione: il conto è stato chiuso da FTMO per obiettivi del Free Trial raggiunti.** L'intuizione di Manu era giusta sui tempi (giovedì sera, 21:55 italiane) e sul motivo; **ma è il Free Trial, non la challenge**: con il target del 10% della challenge vera il conto sarebbe a **+8,02%**, 1.981,50 $ sotto. *(FTMO non scrive esplicitamente che il conto si blocca al raggiungimento degli obiettivi: la conclusione è un'inferenza forte, da confermare su Account MetriX.)*

**Il segnale perso**: alle 16:35 server del 25/09 l'ORB aveva un **LONG da 20,40 lotti** (rischio 901 $ = 5% × 18.018,50 ✓), SL 30.525,22, TP 30.922,62. Rifiutato `[Trade disabled]` (10017). L'EA ha **ritentato a ogni tick per cinque minuti** (~3.000 richieste, una ogni 60-130 ms), **ricalcolando SL e TP a ogni tentativo** (SL fra 30.520 e 30.553): stava **inseguendo il prezzo** fino a ~+28 punti (~+0,6 R) dal segnale. Difetto D1 (§17.8). Se l'IM abbia tentato ingressi dopo le 17:00 non è documentato (l'estratto finisce prima).

**Seduta 25 = 0,00 $**, per la definizione pre-registrata (*«una seduta conta anche se gli EA non hanno operato»*, pre-registrazione §2). Il LONG mancato **non entra nella somma** in nessuna forma: niente «what if».

### 17.6 Trade manuali e terzo EA sul conto del forward — **deviazione di protocollo dichiarata, effetto nullo sugli EA**

Manu ha eseguito operazioni manuali di prova per uno studio parallelo sulle commissioni:

| Quando (server) | Operazioni | Risultato |
|---|---|---|
| 23/09 11:25 → 12:32 | 3 × XAUUSD 0,01 lotti | −0,54 lordo, commissioni −0,18 → **−0,72** |
| 24/09 20:10 → 20:13 | EURUSD 0,1 e 1 lotto · USDJPY 1 e 0,1 lotti | −7,56 lordo, commissioni −11,00 → **−18,56** |
| | | **totale −19,28 $** |

Commissioni misurate, utili fuori dal progetto: **FX 2,50 $ per lotto per lato**; **XAUUSD 0,03 $ per 0,01 lotti per lato**. *Su US100.cash restano 0,00 su tutti i trade.*
**Effetto sugli EA: nessuno.** Lotti ORB del 23/09 identici con e senza il −0,72 (13,86 in entrambi i casi); i trade FX del 24/09 sono successivi all'ingresso ORB; l'IM ha rischio fisso e il suo `DayStats` conta solo il proprio magic.
**Violano però la condizione di validità §5.2 della pre-registrazione («nessun trade manuale»).** Dichiarato, non nascosto: per la regola contabile (dollari grezzi, nessuno scorporo) **i −19,28 $ restano nella somma**. La somma dei soli EA si riporta **come informazione**.
Dal 23/09 alle 14:25 gira sullo stesso terminale anche **`RoundLevels_XAUUSD` in dry run**: nessun ordine, nessuna interferenza osservata. **Per le sedute 26-30: nessun trade manuale e nessun altro EA sul conto del forward.**

### 17.7 CONTABILITÀ — conto 3 chiuso, addendo definitivo

| Seduta | Data | Risultato | Bilancio conto 3 |
|---|---|---|---|
| 16-20 | 14 → 18/09 | −1.967,43 | 98.032,57 |
| **21** | **21/09** | **+1.338,27** (IM) | 99.370,84 |
| **22** | **22/09** | **+2.499,10** (ORB +1.776,16 · IM −128,11 e +851,05) | 101.869,94 |
| **23** | **23/09** | **+2.212,34** (ORB +1.842,69 · IM +367,75 · swap +2,62 · manuali −0,72) \* | 104.082,28 |
| **24** | **24/09** | **+3.936,22** (ORB +3.954,78 · manuali −18,56) | **108.018,50** |
| **25** | **25/09** | **0,00** (conto disabilitato da FTMO) | 108.018,50 |

\* *Convenzione già usata per il 24/08 e il 15/09: i trade chiusi dopo la mezzanotte si attribuiscono alla seduta d'apertura. Non incide sulla somma, calcolata sui bilanci di conto.*

**Settimana**: EA **+10.005,21 $** (ORB +7.573,63 = **+12,52 R** su 3 trade · IM +2.428,96 = +4,86 R su 4 · swap +2,62) · manuali −19,28 · netto **+9.985,93 $**.

> **REGOLA CONTABILE A N CONTI** *(pre-registrata il 14/09)*
> `(96.113,02 − 99.497,56) + (97.018,85 − 100.000,00) + (108.018,50 − 100.000,00)`
> = −3.384,54 + (−2.981,15) + **8.018,50** = **+1.652,81 $** su 25 sedute *(solo EA, come informazione: +1.672,09)*.
> **Terzo addendo DEFINITIVO**: il conto è disabilitato e non può più cambiare.
>
> **Soglia pre-registrata sulle 30 sedute: −6.437 $. Margine: 8.089,81 $.** Le sedute 26-30 dovrebbero perdere più di 8.089,81 $ per far scattare il rosso: con il conto 4 a 500 $/trade per l'ORB e 500 $ nominali per l'IM, **P(rosso) < 0,1%** *(bootstrap per giornata intera: 0,0005% a giornate indipendenti, 0,075% a blocchi di 5, 0,000% con l'uptime al 65%; 200.000 simulazioni per variante)*. **Il criterio monetario del secondo verdetto è, in pratica, già deciso — salvo un evento estremo.**

### 17.8 DIFETTI EMERSI — nessuno tocca la strategia, tutti vanno corretti prima di pagare

| # | EA | Difetto | Visto il | Rimedio |
|---|---|---|---|---|
| **D1** | ORB | Su **qualunque** rifiuto ritenta **a ogni tick** per tutta la finestra d'ingresso, **senza leggere il codice d'errore** e **ricalcolando prezzo, SL e TP** a ogni tentativo (insegue il prezzo) | 25/09: ~3.000 richieste in 5 minuti | classificare i codici di ritorno (10017, 10018, 10026, 10027 non si ritentano); tetto ai tentativi con attesa; tetto all'inseguimento rispetto al prezzo del primo tentativo; loggare il prezzo del primo tentativo |
| **D2** | IM | La chiusura della posizione del giorno prima (FIX1) ritenta **ogni 15 s in raffiche da 5 senza controllare se il mercato è aperto** | 24/09: ~65 richieste `[Market closed]` in 3 minuti | controllare la sessione (`SymbolInfoSessionTrade`, `SYMBOL_TRADE_MODE`) e il codice 10018: attendere la riapertura invece di insistere |
| **D3** | ORB | `TradingIsLive()` non controlla **`ACCOUNT_TRADE_ALLOWED`** (né `TERMINAL_TRADE_ALLOWED`): non si accorge del conto disabilitato | 25/09 | aggiungere i due controlli (il pre-flight di RoundLevels li ha già: `terminale / EA / conto`) |
| **D4** | ORB | Il catch-all del giorno precedente fa **un solo tentativo**: se fallisce, la posizione vecchia resta aperta fino all'EoD del giorno nuovo | letto nel sorgente; il 24/09 è riuscito al primo colpo | ritentare con tetto finché `posDay < oggi` |

**Perché contano**: FTMO vieta come iperattività gli EA che causano **più di 2.000 richieste al server al giorno**. D1 supererebbe il limite in circa tre minuti; D2, con il terminale acceso per un weekend e una posizione rimasta aperta, in meno di due ore. Sul conto demo già disabilitato non ci sono state conseguenze; **su un conto a pagamento sarebbe stato un rischio vero.**

**Cancello 1(c) — decisione a verbale.** Il cancello dice *«nessun ordine fallito»*. **Per la lettera, questa settimana ordini falliti ci sono stati**, entrambi per cause amministrative (mercato chiuso dopo lo spegnimento del PC; conto disabilitato da FTMO), non per un guasto d'esecuzione del broker. Ma hanno rivelato difetti reali. **Si applica la regola pre-registrata del cancello rosso nella sua parte operativa: si corregge quel punto e si rifà solo quello.**
- **Durante le sedute 26-30 non si tocca nulla**: la pre-registrazione §5.1 vieta di cambiare build.
- **Dopo la seduta 30 e prima dell'acquisto**: build **Q** (ORB) ed **F** (IM) con le correzioni D1-D4, acceptance cella per cella contro P/E nel tester (devono risultare identiche, come P≡O ed E≡D), e un collaudo dal vivo a costo zero: **agganciare le build nuove al conto 3, che è disabilitato** — devono scrivere un solo messaggio e fermarsi, non ritentare.
*(Nota di nomenclatura: la sigla F era stata riservata a un eventuale gate VIX, archiviato. Se quel gate tornasse, prenderebbe la sigla successiva.)*

### 17.9 UPTIME — il migliore del forward, e comunque un'EoD persa

| Seduta | Terminale (ora locale) | Check IM *(stima dagli spegnimenti nei log)* | Acceso alle 21:55? |
|---|---|---|---|
| 21 (21/09) | 14:13→17:46 · 18:32→oltre le 21:55 | ~10/12 | **SÌ — EoD dell'IM osservata** |
| 22 (22/09) | ~13:14→18:40 · 19:23→oltre le 21:55 | ~11/12 | **SÌ — due EoD osservate** |
| 23 (23/09) | mattina→18:14 *(riavvio 14:46)* · 18:41→**20:55 (spegnimento del PC con 2 posizioni aperte)** | ~9/12 | **NO** |
| 24 (24/09) | 00:01→… · 11:04→17:43 · 18:26→22:14 | ~11/12 | **SÌ — EoD dell'ORB osservata** |
| 25 (25/09) | 15:30→26/09 01:51 | 12/12 *(conto già disabilitato)* | sì, ma nessun ordine possibile |

**Sedute 21-24: ~41/48 = 85%. Cumulativo 24 sedute: ~188/288 = 65,3%** (era 61,3%).
Ingressi IM attesi con quell'uptime: **~2,1**; osservati **4** (P(≥4) = 13,4%): sopra l'atteso, dentro la varianza.
**Ma una sera su quattro il PC è stato spento prima delle 21:55 con posizioni aperte**, ed è la sera che ha prodotto l'overnight del §17.4. È il terzo caso del forward, sempre per la stessa causa.

### 17.10 SERIE DI ESECUZIONE AGGIORNATE *(dettaglio in `COSTI_ESECUZIONE_REALI_FTMO_US100` rev 4.1, md5 `4cd78254b846f1c5377a11652b4f98c3`, che sostituisce la rev 4 dopo il doppio controllo del §17.15)*

- **Slippage d'ingresso, n = 29**: media **−0,20 pt**, dev.st 2,07, IC95% [−0,99 ; +0,58]. Le sette misure della settimana sono le più strette mai viste: tutte entro ±1,30 (dev.st 0,75).
- **Slippage sullo stop**: nessuno stop nella settimana; **n = 15 stop ORB, media +1,77%** della distanza, cioè **+0,68 punti** *(ricalcolata togliendo un doppio conteggio della rev 3: vedi errore n.11)*. Dal vivo, sugli 11 stop con riancoraggio: **−1,0228 R** contro −1,0225 R del backtest.
- **Uscite a mercato, n = 10**: 9 fra 189 e 229 ms; **1.296 ms** sul primo ordine dopo la riapertura delle 01:05.
- **Ingressi**: mediana 234 ms su 20 documentati; **un valore a 825 ms** (IM, 23/09, check delle 17:00 server) con slippage di appena +0,50.
- **Commissioni US100.cash 0,00** su tutti i trade. **Swap**: terza notte osservata (+0,127 $/lotto): due a credito, una a debito, sempre su short.
- **Zero rifiuti sul prezzo** (requote, off quotes) su 29 ingressi e 10 uscite a mercato. I rifiuti della settimana sono solo amministrativi (§17.8).

### 17.11 REGIME 2026 — aperto n.10, aggiornato

| | Backtest 2026 | **Con i trade del forward (21/08 → 24/09)** |
|---|---|---|
| ORB | +9,26 R su 129 | **+8,82 R su 147** (+0,060/trade), IC95% [−0,34 ; +0,46] |
| IM | −7,45 R su 97 | **−8,76 R su 105** (−0,083/trade), IC95% [−0,44 ; +0,28] |

Il forward dell'ORB da solo: **18 trade, −0,44 R, 4 vincenti (22,2%** contro il 19,3% storico). La serie di 14 perdite di agosto-settembre e le 3 vincite di fila di questa settimana (probabilità 0,7% prese da sole) sono **la stessa distribuzione vista da due lati**. Entrambi gli intervalli contengono lo zero **e** la media storica: l'aperto n.10 resta **apertissimo in entrambe le direzioni**.

### 17.12 QUANTO È ANOMALA LA SOMMA A 24 SEDUTE — e la lezione che dà

Bootstrap per giornata intera con la struttura reale dei tre conti (6 + 9 + 9 sedute, buffer ORB ricalcolato su ogni conto, IM a 500 $ diradato al 65% di uptime), 40.000 simulazioni, seed 7. Osservato (solo EA): **+1.672,09 $**.

| Ipotesi | P(≤ osservato) | Mediana | Verosimiglianza «edge intatto» contro l'ipotesi |
|---|---|---|---|
| Edge **intatto** | **53,3%** *(seed-check 53,7%; blocchi di 5 giornate 53,6%)* | +1.045 | — |
| Edge **dimezzato** | 60,0% | −125 | **1,05 : 1** |
| Edge **nullo** | 66,2% | −1.270 | **1,11 : 1** |
| Edge **negativo** | 76,5% | −3.485 | 1,44 : 1 |

*Metodo dichiarato: con l'osservato nella coda sinistra (sedute 12, 15, 20) la verosimiglianza era stimata con la probabilità di coda; ora che l'osservato sta al centro della distribuzione si usa la densità in una finestra di ±500 $ (±1.000 $ dà gli stessi rapporti: 1,01 / 1,12 / 1,44).*

> **In quattro sedute la somma è passata dal 2° percentile (LR 2,95 : 1 CONTRO l'edge, §16.10) al 53° percentile (LR 1,1 : 1).** È la dimostrazione dal vivo del presidio anti-bias: **il P&L di poche settimane non misura l'edge, in nessuna delle due direzioni.** Il 19/09 i numeri sembravano dire «forse è rotto», oggi sembrano dire «funziona»: non dicevano niente allora e non dicono niente adesso. **Il criterio non si tocca, e non si festeggia.**

### 17.13 ERRORE A VERBALE — l'undicesimo

**Il documento `COSTI_ESECUZIONE_REALI_FTMO_US100` rev 3 (19/09) conteneva cinque errori materiali e un confronto non aggiornato**, trovati rileggendolo per aggiornarlo e corretti nella rev 4:
(a) la serie dello slippage d'ingresso era dichiarata «n = 16» in un punto e «n = 20» in un altro, conteneva due misure pre-forward e **ometteva due ingressi dell'IM** (24/08 +1,25; 04/09 0,00);
(b) lo stop IM del 24/08 era **contato due volte**: nella serie dei 16 stop (+0,18%) e di nuovo come stop protettivo con un valore errato (+1,37 pt = +0,62%). La serie corretta è di 15 stop ORB, media +1,77% invece di +1,67%;
(c) lo swap del 24/08 era riportato su **3,64 lotti a +0,34 $/lotto**: i lotti erano 4,48, il tasso **+0,28** *(il +0,34 veniva dall'ipotesi del §5.4, poi smentita dalla CronoStoria, che nessuno aveva ricalcolato)*;
(d) la tabella dei costi contava **lo spread due volte** sulle uscite a mercato;
(e) *(non un errore, un dato vecchio)* il confronto dal vivo del §4.4 era fermo a 3 stop del 30/08;
(f) un orario del 17/09 era descritto al contrario (16:54 «dopo» le 17:00).
**Nessuno cambia le conclusioni**, ma il documento dichiara che *«nessun numero è stimato»* e va dato ad altre chat: gli errori contano più che altrove. *Lezione: un documento aggiornato per aggiunte successive accumula incoerenze; ogni revisione va ricalcolata da zero sulle fonti, non estesa.*

### 17.14 ESITO

**Sedute 21-25 CERTIFICATE. Forward a 25 su 30.** Quadratura al centesimo su 7 trade su 7, riancoraggio 7/7 (21/21 con le build P/E), quattro EoD, primo catch-all corretto dell'ORB, prima EoD del momentum.
**Conto 3 chiuso da FTMO a 108.018,50 per obiettivi del Free Trial raggiunti** (target 5%, non 10%). **Somma a 25 sedute: +1.652,81 $** contro una soglia di −6.437: **P(rosso) < 0,1%**.
**Cancello 1(c)**: difetti di gestione dei rifiuti D1-D4 → **correzione e acceptance dopo la seduta 30, prima dell'acquisto** (§17.8).
**Prossima azione: aprire il conto 4 (nuovo Free Trial) prima di lunedì 28/09 alle 15:00**, con Algo Trading riabilitato a mano e baseline 100000 verificata nella finestra Proprietà. **Se il conto 4 arriva al +5% prima della seduta 30 (~10% di probabilità), FTMO lo chiuderà di nuovo: si apre subito il conto 5 e si prosegue** — la regola a N conti lo assorbe, le sedute perse valgono 0,00.
**Secondo e ultimo verdetto: weekend 3-4 ottobre.**

### 17.15 DOPPIO CONTROLLO DEI DOCUMENTI PER LE ALTRE CHAT — errore a verbale n.12

Il 26/09, su richiesta di Manu, `COSTI_ESECUZIONE_REALI_FTMO_US100` rev 4 e `DOSSIER_FTMO_PER_NUOVE_STRATEGIE` rev 1 sono stati ricontrollati numero per numero sulle fonti primarie (serie CSV, Report Cronistorico, sorgenti degli EA, MEMORIA, studio esterno, pagine ufficiali FTMO), poi sottoposti a due passate di verifica indipendente (circa 280 affermazioni controllate). **Trovati e corretti** (COSTI → **rev 4.1**, dossier → **rev 2**):
- ⚠️ **il più grave, rischio di doppio conteggio**: COSTI §1.3 e la ricetta del dossier facevano aggiungere lo slippage sugli stop anche a un backtest MT5 su tick reali, che lo contiene già (−1,0225 R nel backtest, −1,0228 R dal vivo). Ora la ricetta distingue i tipi di backtest e indica il controllo da fare: la perdita media agli stop in R;
- lo slippage sugli stop era espresso in percentuale della distanza, che lo sottostima per gli stop stretti: ora **in punti (≈0,7 su `US100.cash`)**, stress × 2,5;
- «lo spread medio storico sottostima il costo attuale di oltre il doppio»: vero rispetto al 2021 (2,4 volte), non rispetto alla media (1,4 volte, circa il 30%);
- coda dello slippage sugli stop «fino a 0,20 R»: nel backtest 3 stop su 778 la superano, il peggiore a 0,63 R;
- la misura «su SL/TP» riguardava solo gli stop: sui take profit non c'è misura (uno solo colpito dal vivo, il 04/08, senza rilevare lo slippage);
- la serie dell'IM in custodia (742 trade) è il backtest in Python su barre M1, non il tester MT5 (633 trade): i suoi stop protettivi valgono almeno +4% oltre il livello, contro +0,18% e +0,73% dal vivo, cioè sovrastimano il costo;
- la finestra senza quotazioni è stata attraversata in tutte e tre le notti overnight, non una volta sola; il gap alla riapertura è stato osservato solo il 24/09;
- sul netto dei soli dati FTMO le nostre strategie hanno t 1,78 (ORB) e ~0,9 (IM): il cancello G2 del dossier ora lo dichiara;
- minori: Kelly calcolato sull'edge netto; fortuna di calendario e confronto con la 1-Step attribuiti allo studio esterno con le sue metriche; verifica del fuso su un altro broker limitata alle settimane 2024-25 (non «9 anni»); lo slippage delle uscite a mercato è assunto, non misurato; «27 trade del forward» → «dal 17/08»; tempi di `PositionModify`; ping domestico 29-76 ms; quota della challenge in euro e quote attese 2,7-2,8; inferenze dichiarate come tali (chiusura del Free Trial, deviation); riferimenti di riga.

**Nessuna correzione tocca le conclusioni del forward né i valori misurati**: cambia il modo in cui un'altra chat li applica. *Lezione, che conferma la n.11: un documento destinato ad altre chat si verifica contro le fonti, e con una verifica indipendente, prima della consegna, non dopo.*
**Da consegnare alle chat parallele**: `DOSSIER_FTMO_PER_NUOVE_STRATEGIE` rev 2 (md5 `a19e26e925fa3d1f1417a227146eee89`) e `COSTI_ESECUZIONE_REALI_FTMO_US100` rev 4.1 (md5 `4cd78254b846f1c5377a11652b4f98c3`). Le versioni precedenti non vanno più usate. *(Superati il 06/10 da DOSSIER rev 3.1 e COSTI rev 5.1: vedi §18.18.)*

---

## 18. SEDUTE 26→30 — dal 28/09 al 02/10/2026 — **CERTIFICATE (30/30)** — conto 4 (Free Trial **Swing**) · ⭐ **SECONDO E ULTIMO VERDETTO: VERDE**

**Custodia** (file consegnati il 05-06/10; i nomi «(n)» sono quelli dati da Manu, i contenuti sono UTF-16 come sempre):

| Giorno | Experts | Journal |
|---|---|---|
| 28/09 (seduta 26) | **incollato in chat** («non trovato sul terminale») → nessun md5 | `Journal (9).log` `81d9a82ba2105bdc09e18f7dde2a7626` |
| 29/09 (seduta 27) | `Experts (5).log` `9100262e2231854a0ae9c3d03dbfcd7c` | `Journal (8).log` `ae21293c3fa7a67352f7ce502833fb77` |
| 30/09 (seduta 28) | `Experts (6).log` `f9506907fee55901f256c02ec9fa847e` *(identico al testo incollato in chat; si ferma alle 16:00:07 locali)* | `Journal (7).log` `9f8539753425097c584c41fcbb7ba4b6` |
| 01/10 (seduta 29) | `Experts (7).log` `25407918cb49979f162d42a82c45e162` | `Journal (6).log` `21d15a8f7490a0ec0cf41ace6b9b8985` |
| 02/10 (seduta 30) | `Experts (1).log` `e72bb31149a22f0d287cd2493fa812d0` | `Journal (5).log` `c1d4726ccc4fe488e555438184bf6a99` |
| 03-06/10 (dopo il forward) | `Experts (2)` `ce95a32d4121c5096121007c3d5888e4` · `(3)` `8dbf734c136b2bcc4f7476dd42140572` · `(4)` `9e7652a17da691a805e3921f34ad37bd` · `20261006.log` `ae1612362b4ee403d4eb4f572c73c78a` | `Journal (4)` `dec662d1c24a9a2892f6a4ddf55c679e` · `(2)` `71cf32293fa35933d5e3febfb1ac3fb8` · `(1)` `8d71b09e65504b3c5880c2c019b1b95f` · `20261006.log` `6e42b273a7ae607eb61ad0e21c8bfa47` |

- `Cronistoria.xlsx` — report del **2026.10.05 17:27**, conto `1514768646`, 6 trade, md5 **`d28f10a862a2a4990961ec0cd87a0a4b`**.
- `Journal (3).log` — **non è un journal del terminale: è il log di MetaEditor** (compilazioni dal 20/07), md5 `c74e15c256b7e047cfbbdb6c55bbe639`. Usato per la verifica di build qui sotto.
- `calendario_eventi_2021_2026.csv` — export del calendario economico MQL5 fatto il 30/09 dal terminale (§18.6c), md5 `df2d8224788e410279828b6d62680693`. Usato per il confronto stop/notizie (§18.7).
- **Fonti primarie riaperte per la ricostruzione da zero di tutto il forward** (§18.12): `ReportHistory_20260821.xlsx` `c8e747ae175ad282bd825724227622fa`, `CronoStoria_20260828.xlsx` `06951162d823d43ab115b25fd3a07bd9`, `CronoStoria_20260908.xlsx` `f615aa54b30bc9c94e34fbe65a0badaf` — **impronte identiche a quelle agli atti** — e **`ReportHistory-1514618793.xlsx`** (conto 3, report del 24/09 19:25 server, nuovo in custodia) `e5e52dbcb565b72d3bf6a9b7e6ad0d99`; serie `ORB_trades_R_20212026.csv` e `MOMENTUM_trades_R_20212026_FTMO.csv` con impronte identiche.

**Build in esecuzione.** Il log di MetaEditor data l'ultima compilazione di `ORB_US100_-_step16_P` al **2026.08.25 17:20:01** e di `IntradayMomentum_NAS100_E` al **17:19:08**: nessuna ricompilazione da allora. Init stampate `ORB 08-22-P` e `IM 08-22-E`; commenti d'ordine `ORB 08-22-P` ×4 e `IM 08-22-E` ×2 nella cronistoria (regola 5.9) ✓. Il 29/09 risultano compilate, prima in una cartella di progetto (15:55 locali) e poi nella cartella `Experts` del terminale (16:47), **`IntradayMomentum_NAS100_F_senzaHalt`** e **`_G_senzaHalt`**: secondo i journal **non sono mai state agganciate** a un grafico nelle sedute 26-30 (caricati sempre e solo ORB step16_P, IM_E e RoundLevels_XAUUSD). Vedi la nota sulla sigla F al §18.15.

### 18.1 I sei trade, al centesimo — **tutti gli assert superati**

| Trade | dist | lotti | slip ingresso | uscita | rischio (lotti × dist) | R |
|---|---|---|---|---|---|---|
| 28/09 ORB SHORT | 45,2656 | 11,04 ✓ | **+5,71** | STOP 19:27:19 srv @ 30.438,28 (SL 30.437,69: **+0,59 = +1,30%**) | 499,73 | **−1,0131** |
| 28/09 IM SHORT *(check delle 17:30)* | 44,825 | 11,15 ✓ | +0,81 | STOP 19:24:38 srv @ 30.362,38 (SL 30.356,87: **+5,51 = +6,15%**) | 499,80 *(stop a 2×dist: 999,60)* | **−2,1229** |
| 29/09 ORB SHORT | 46,8578 | 8,99 ✓ | +0,80 | STOP 16:56:28 @ 30.377,43 (SL 30.376,89: +0,54 = +1,15%) | 421,25 | −1,0116 |
| 30/09 ORB LONG | 47,2311 | 8,47 ✓ | **−1,70** | STOP 16:35:51 @ 30.447,03 (SL 30.446,25: **−0,78 = −1,65%, a favore**) | 400,05 | −0,9835 |
| 30/09 IM LONG *(check delle 17:00)* | 57,505 | 8,69 ✓ | +1,90 | **BANDA** 19:30:00 @ 30.572,93 (249,95 ms) | 499,72 | −0,0643 |
| 01/10 ORB LONG | 46,7189 | 8,11 ✓ | **−2,20** | STOP 16:35:45 @ 30.490,43 (SL 30.491,06: +0,63 = +1,35%) | 378,89 | −1,0135 |

Assert verificati:
- **Lotti ORB** = `floor₂(5% × (equity − 90.000) / dist)` → 4 su 4 (equity all'ingresso 100.000,00 · 98.432,68 · 98.006,55 · 97.580,97 → rischio 500,00 · 421,63 · 400,33 · 379,05; il log stampa `R$ 500 / 421 / 400 / 379`). `dist` = 10% dell'ATR(D1) stampato (452,65 · 468,57 · 472,32 · 467,19) ✓.
- **Lotti IM** = `floor₂(min(500/dist ; 4 × 100.000/p))` → 2 su 2 (11,1545 → 11,15; 8,6949 → 8,69); cap notional **inattivo** (~13,2 e ~13,1 lotti disponibili).
- **Riancoraggio**: SL ORB = `fill ∓ dist`, TP = `fill ± 8·dist`; SL IM = `fill ∓ 2·dist`; TP dell'ordine ORB = `prezzo richiesto ± 8·dist` → tutti al centesimo.
- **P&L** = `lotti × (uscita − fill)` → 6 su 6. Commissioni **0,00**, swap **0,00** su tutti.
- **Bilancio ricostruito 97.196,96 = Cronistoria, al centesimo.**

Metodo come al §16.2 e §17.1: per l'ORB `dist` e prezzo richiesto risolti da SL e TP dell'ordine (TP − SL = 9·dist); per l'IM lo slippage è la differenza fra SL della posizione e SL dell'ordine, e coincide col `delta` stampato dall'EA **corretto per la direzione** (28/09, short: `delta −0,81` = **+0,81 sfavorevole**).

**Tempo in posizione**: 28/09 ORB 2h52'19" e IM 1h54'37" · 29/09 21'28" · **30/09 ORB 51 secondi** · 30/09 IM 2h29'59" · **01/10 ORB 45 secondi**. Sei trade, sei perdite; l'IM del 30/09 è uscito sul rientro in banda quasi a pareggio (−0,06 R).

### 18.2 Riancoraggio **6 su 6** — con le build P/E ora **27 su 27**

| Trade | SL ordine → SL posizione | TP ordine → TP posizione |
|---|---|---|
| 28/09 ORB | 30443.40 → **30437.69** | 30036.01 → 30030.30 |
| 28/09 IM | 30357.68 → **30356.87** | — |
| 29/09 ORB | 30377.69 → **30376.89** | 29955.97 → 29955.17 |
| 30/09 ORB | 30447.95 → **30446.25** | 30873.03 → 30871.33 |
| 30/09 IM | 30459.72 → **30461.62** | — |
| 01/10 ORB | 30493.26 → **30491.06** | 30913.73 → 30911.53 |

Tutti diversi ⇒ `PositionModify` eseguita ogni volta (69-200 ms). *Il conteggio «27 su 27» segue la convenzione del §17.2: gli ingressi con le build P/E sono 28 (19 ORB, 9 IM), ma in uno — IM del 04/09 — lo slippage era zero e non c'era nulla da spostare (§14.2); i 27 con slippage non nullo sono stati riancorati tutti.* La riga **`[ORB] posizione visibile dopo attesa`** è comparsa **due volte su quattro ingressi del breakout**: 30/09 (fill 30493.48, posizione visibile ~60 ms dopo il deal) e 01/10 (fill 30537.78, ~66 ms). Con la build O sarebbero stati due riancoraggi persi in silenzio. **Nessuna riga `*** ATTENZIONE: posizione NON leggibile dopo l'invio ***`.** Il fill stampato dagli EA coincide con la cronistoria 6 volte su 6 (l'IM lo stampa con un decimale).

### 18.3 ⚠️ Il conto 4 è un Free Trial **Swing**, con leva **1:30** — deviazione di configurazione dichiarata, effetto nullo sulla misura

L'intestazione della cronistoria dice **`$100k FTMO Free Trial Swing 2-Step`**; i report dei conti 1, 2 e 3 dicevano `$100k FTMO Free Trial 2-Step`. Il rapporto di avvio dell'EA sull'oro stampa **`leva 1:100`** sul conto 3 alle 09:57 del 28/09 e **`leva 1:30`** sul conto 4 un minuto dopo. Conto aperto il **28/09 alle 10:45:46 server** con 100.000,00 (deal `Initial account balance`).
La pre-registrazione del §12.4 chiedeva la **«stessa identica configurazione»** per le sedute 16-30. **La configurazione degli EA è identica** (stesse build e stessi parametri nelle righe di Init: buffer 5%, cap 1.500, stop 10% ATR, baseline 100000.00 esplicita; cambia solo il rischio del giorno, che dipende dall'equity); **il tipo di conto no**. Effetti:
- **costi**: identici — spread 1,45 su 4 ingressi del breakout su 4, commissioni 0,00 su 6 trade;
- **margine**: sul conto Standard il report del 24/09 mostra per 16,60 lotti un margine di **10.041,70 $ = 2,00% esatto del nozionale al prezzo d'apertura (1:50)**; sul conto Swing il margine degli indici non è misurato. Con l'esposizione massima della settimana (22,19 lotti il 28/09) anche una leva di 1:30 sugli indici avrebbe impegnato ~22.400 $ su ~100.000 *[STIMA]*: **non vincolante**;
- **regole**: le differenze Swing/Standard (news e weekend sul conto finanziato) non toccano il Free Trial.
> **Conclusione: nessun effetto sulla misura.** Ma il dato va a verbale per due motivi: (1) è una misura in più per le chat parallele (costi identici su Swing); (2) la challenge del progetto era pensata su **Standard**: il tipo di conto va scelto consapevolmente al momento dell'acquisto (§18.15).

### 18.4 ⚠️ 28/09 — il movimento rapido, lo stop con lo slittamento peggiore del forward, e R1 nel verso pericoloso

| Ora (server) | Fatto |
|---|---|
| 10:57 | conto 3 ancora collegato: il pre-flight dell'EA sull'oro stampa `trading permesso: … conto NO` (il conto disabilitato è visto subito: è il rimedio al difetto D3). L'ORB aveva già preparato la giornata a **901 $/trade** sul conto 3: senza il cambio conto, alle 16:35 avrebbe ripetuto la raffica di rifiuti del 25/09 (difetti D3 e D1: non vede il conto disabilitato e ritenta a ogni tick) |
| 10:58:44 | cambio conto → `automated trading is disabled because the account has been changed` → **10:59:01 `enabled`** (17 s, a mano). Trappola 5.10 neutralizzata. L'EA sull'oro trova il riferimento giornaliero mancante e lo ricostruisce a 100.000; l'ORB parte a **500 $/trade** con baseline 100000.00 esplicita (§8.5) ✓ |
| 11:58 → 12:21 | aggiornamento automatico del terminale a **build 6230** (scaricato alle 11:58, applicato alle 12:21 con riavvio) — **quarta build del progetto** (6090 → 6140 → 6182 → 6230), prima della seduta |
| 16:35:00 | ORB short 11,04 @ 30.392,42 · **slippage +5,71, il peggiore sfavorevole del forward** · ordine eseguito in **420,3 ms**, il più lento di tutti gli ingressi del breakout |
| 16:58:51 | cambio di access point, riconnessione in 1 s con la posizione aperta (`1 positions`): nessun effetto |
| 17:30:01 | IM short 11,15 @ 30.267,22 (slippage +0,81, 228,5 ms) |
| **18:42:51 → 19:23:59** | **terminale spento con due posizioni aperte.** Nel journal mancano le righe di arresto regolare (`exit with code`, `stopped`, `shutdown`): terminazione non pulita, causa non determinabile dai log. **Il check delle 19:00 dell'IM cade nel buco, con la posizione aperta** |
| 19:24:00 | riavvio, `2 positions`. ORB: `Riavvio con posizione aperta di oggi: lasciata correre`, **`EqRef 99.739,93`** = bilancio 100.000 − 260,07 di flottante |
| **19:24:38** | **stop dell'IM a 30.362,38 contro 30.356,87: +5,51 punti (+6,15%)** → −1.061,03 $ invece di −999,60 al livello |
| 19:27:19 | stop dell'ORB a 30.438,28 contro 30.437,69: +0,59 (+1,30%) → −506,29 $ |

**Il movimento**: ~+81 punti in 2'41", fra i due stop. **Calendario MQL5: nessun dato USD di importanza alta o media** fra le 18:30 e le 20:25 (solo aste di T-bill a 3 e 6 mesi alle 18:30, importanza bassa; discorso del governatore Fed Cook, importanza media, alle 20:25). **È la coda dello slippage sullo stop vista per la prima volta in punti — e senza notizie.**

**Il check perso delle 19:00.** Se a quell'ora il prezzo era rientrato nella banda, l'IM sarebbe uscito a mercato, senza attraversamento e probabilmente con una perdita minore; se no, nulla cambia. **Non determinabile con i dati in custodia** — *controllo eseguibile: barre M1 di US100.cash del 28/09 fra le 18:55 e le 19:05 server*. È la quarta osservazione degradata dall'uptime con posizione aperta (dopo 24/08, 15/09, 23/09).

**⚠️ Rilievo R1 osservato per la prima volta nel verso PERMISSIVO** — quello temuto. Il riavvio in perdita ha spostato il riferimento del freno giornaliero dell'ORB da 100.000,00 a 99.739,93, cioè il livello di blocco da **98.500,00 a 98.239,93: 260,07 $ di margine in più**. Effetto quel giorno: con il riferimento giusto il freno sarebbe stato a portata negli ultimi secondi prima dello stop dell'ORB (equity sotto 98.500 per prezzi oltre 30.432,18; stop a 30.437,69): differenza teorica massima ~67 $ (6,10 punti × 11,04 lotti: dalla soglia di 30.432,18 al prezzo eseguito dello stop, 30.438,28), **non verificabile senza i tick**. Con il riferimento spostato il freno non poteva scattare (bilancio finale 98.432,68 > 98.239,93). Insieme al §15.9a (verso severo, +1.118,63) e al §17.4 (verso severo, +3.799,90), **R1 è ora osservato in entrambe le direzioni**: la correzione «freni ricalcolati dallo storico del server» resta da fare prima di pagare.

### 18.5 ⚠️ 02/10 — la seduta 30 è persa per uptime: **prima finestra d'ingresso del breakout saltata in tutto il forward**

Terminale acceso solo **13:14→13:15, 13:38→13:43, 14:33→14:33 e 17:51→17:53** (ora locale). La finestra d'ingresso del breakout (16:35-16:40 server) è caduta a terminale spento: **è la prima volta in 30 sedute** (l'08/09 il terminale era stato acceso con 2 minuti di ritardo, ma dentro la finestra). L'IM ha preparato la giornata solo alle 18:51 server e si è spento due minuti dopo: **0 check su 12**. Era il giorno dei **Non-Farm Payrolls** (15:30 server). Alle 13:14 `MCP bind error on 127.0.0.1:22346` (porta occupata, innocuo come il 15/09).

**Seduta 30 = 0,00 $**, per la definizione pre-registrata (*«una seduta conta anche se gli EA non hanno operato»*). Nessun «what if»: non si sa se ci sarebbe stato un segnale. **Effetto sul verdetto: nullo** — il margine dalla soglia è di 5.286,77 $ e nessuna seduta singola può perdere tanto, nemmeno nel peggior caso dei freni (~3.600 $, rilievo R1).

### 18.6 Altri rilievi

**(a) Latenze d'ingresso più alte dopo la build 6230.** 420,3 · 228,5 · 295,8 · 224,7 · 364,0 · 326,5 ms → **mediana 311 ms**, contro **232 ms** sui 27 ingressi fino al 24/09 (letti dai journal: §18.12). Ping invariato (38,5-66,9 ms). Il caso da 420 ms è anche quello con lo slippage peggiore, ma un caso solo non fa un legame (il più lento in assoluto, 825 ms del 23/09, aveva +0,50). **Da sorvegliare, non una conclusione.** Il terminale ha offerto il VPS a 1,44 ms (28/09) e 1,61 ms (29/09).

**(b) 29/09 — compilazione di EA nuovi e riavvio del terminale a seduta in corso.** Alle 16:47 locali (17:47 server) sono state compilate le build F/G `senzaHalt` nella cartella `Experts`, e alle 16:48 il terminale è stato chiuso e riaperto. **Violazione della regola «nessun riavvio dalle 15:25»** (§15.9b). Nessun effetto: conto piatto, R1 nella forma benigna (`EqRef` = bilancio). **Da non ripetere**: lo sviluppo va fatto su un'installazione separata di MT5.

**(c) 30/09 — il calendario economico MQL5 è popolato sul terminale FTMO.** Alle 12:31 locali (prima delle 15:25: ammesso) lo script `EsportaCalendarioEventi_v1`, su un grafico US100.cash M30 diverso da quelli degli EA, ha esportato **64.986 eventi 2021-2026** (22.171 USD, 19.131 EUR, …), in ora server. **Si chiude la metà «calendario disponibile» dell'aperto sul filtro news dell'IM** (trappola T21 del dossier): il filtro ha i dati. Resta aperta l'altra metà — che l'EA li legga correttamente al check: la riga `entry bloccata da news filter` non è mai comparsa nei log disponibili. Il 01/10 il check delle 17:00 coincideva con l'ISM manifatturiero (alto impatto): nessun ingresso e nessuna riga di blocco, quindi a quel check non c'era segnale — o il filtro non ha parlato; i log non lo distinguono.

**(d) `WARNING: volume candela apertura NON anomalo` il 30/09 e il 01/10 — falsi positivi, e ora la spiegazione è verificata.** Con il calendario in mano: **tutti e cinque i falsi allarmi registrati nel verbale** (04/09, 10/09, 11/09, 30/09, 01/10) cadono in giorni con dati USA ad alto impatto alle **15:30 server** — Non-Farm Payrolls; prezzi alla produzione e sussidi; inflazione CPI; PCE e PIL; sussidi. La guardia misura «c'è stato un dato pre-apertura», non «l'orario è sbagliato» (§14.7a, §15.9c: confermato).

**(e) Rete**: riconnessioni il 28/09 alle 15:58:51 locali (1 s, con posizione aperta), il 29/09 alle 12:46:33 (1 s), 23:01:05 (34 s) e 23:01:43 (2 s), il 30/09 alle 11:19:59 (5 s) e 21:29:12 (5 s). Tutte riparate da sole, nessuna su un ordine.

**(f) `RoundLevels_XAUUSD` in dry run è rimasto agganciato** per tutte e cinque le sedute: **deviazione formale** dall'indicazione del §17.6 («nessun altro EA sul conto del forward»), **effetto nullo** (nessun ordine; la cronistoria contiene solo i 6 trade degli EA). **Nessun trade manuale** ✓. I suoi due segnali simulati (30/09 LONG a 4.200, 01/10 SHORT a 4.150) restano nel suo log; il suo rapporto di avvio ha fornito i dati sull'oro del documento dei costi (rev 5.1, §2.10).

**(g) Dopo la seduta 30** (fuori dal forward): il 03/10 alle 11:34 locali l'IM è stato tolto dal terminale; l'ORB è rimasto agganciato al conto 4 (05/10 e 06/10: nessun trade nei log consegnati). Il 03-04/10 sono stati compilati nella cartella `Experts` `GotobiFix_USDJPY` e `RoundLevels_XAUUSD_R8` / `R8D`.

### 18.7 Stop e notizie — confronto con il calendario MQL5 *(nuovo)*

Su **tutti i 22 stop eseguiti dal server** dal 17/08 (19 del breakout, 3 del momentum), cercando gli eventi USD ad alto impatto entro 30 minuti:

| Stop | Evento ad alto impatto più vicino |
|---|---|
| 29/09 16:56:28 | **3,5 minuti PRIMA** di JOLTS e Fiducia dei consumatori (17:00) — il più vicino in assoluto |
| 31/08 16:35:14 · 30/09 16:35:51 | ~9 minuti prima del Chicago PMI (16:45) |
| 01/09 16:35:21 · 01/10 16:35:45 | ~9 minuti prima del PMI S&P Global (16:45), ~24 prima dell'ISM (17:00) |
| 02/09 17:14:03 | 16 minuti prima delle scorte di greggio EIA (17:30) |
| 25/08 16:36:26 | 24 minuti prima di vendite di case nuove e Fiducia dei consumatori |
| gli altri 15 | nessun evento ad alto impatto entro 30 minuti (compreso il +5,51 del 28/09) |

> **Nessuno stop è stato eseguito entro ±2 minuti da un dato ad alto impatto, e nessuno DOPO un dato entro mezz'ora.** In compenso **due posizioni del breakout hanno attraversato un dato delle 10:00 ET senza toccare lo stop**: 10/09 (vendite di case esistenti alle 17:00, EIA alle 19:00, asta a 30 anni alle 20:00 → EoD +1,38 R) e 24/09 (vendite di case nuove alle 17:00 → EoD +5,62 R); e tre hanno attraversato le scorte EIA delle 17:30 (23/09 ORB e IM, 30/09 IM).
> **Il limite n.5 del documento dei costi resta aperto**: lo slippage sullo stop nei minuti di un dato non è mai stato misurato. Per il conto finanziato Standard (regola ±2 minuti su stop e target) il dato utile è che in 30 sedute il caso non si è presentato — ma il calendario di FTMO non coincide necessariamente con gli eventi «alti» di MQL5.

### 18.8 Gli stop rapidissimi: più frequenti dal vivo, ma in linea con il 2026 *(aggiorna il §11.4)*

Stop del breakout entro **60 secondi** dall'ingresso: **5 su 19** dal vivo (26/08 25 s, 31/08 14 s, 01/09 21 s, **30/09 51 s, 01/10 45 s**) = 26%. Nel backtest: **8,1%** su tutto lo storico (P di vederne ≥5 su 19 = **1,5%**), ma **13,5% nel solo 2026** (P = **10,2%**). Mediana del tempo allo stop: **5,1 minuti** dal vivo, 6,3 nel backtest 2026, 7,3 su tutto lo storico.
> **Dentro il regime 2026, non un'anomalia d'esecuzione.** È però un indizio in più, coerente con il §17.11, che il 2026 è un anno diverso per questo breakout: gli stop arrivano più in fretta.

### 18.9 UPTIME — sedute 26-30

| Seduta | Terminale (ora locale) | Check IM | Acceso alle 21:55? |
|---|---|---|---|
| 26 (28/09) | 09:57→11:21 · 11:21→**17:42 (con 2 posizioni aperte)** · 18:23→21:47 | 11/12 *(perso quello delle 19:00 server, **con posizione IM aperta**)* | NO — spento 8 minuti prima *(nessuna posizione)* |
| 27 (29/09) | 12:46→16:48 · 16:48→18:00 · 18:40→21:45 · 22:12→notte | 11/12 | NO — spento 10 minuti prima *(nessuna posizione)* |
| 28 (30/09) | notte→10:42 · 10:56→11:28 · 12:29→12:40 · 15:11→21:37 | **12/12** | NO — spento 17 minuti prima *(nessuna posizione)* |
| 29 (01/10) | 14:29→17:39 | 4/12 | NO |
| 30 (02/10) | 13:14→13:15 · 13:38→13:43 · 14:33→14:33 · 17:51→17:53 | **0/12** · **finestra ORB persa** | NO |
| | | **38/60 = 63%** | 0 su 5 |

**Cumulativo, 29 sedute valutabili (esclusa la 25): ~226/348 = 64,9%** (era 65,3% a 24 sedute).
Ingressi IM attesi con quell'uptime: 5 × 0,5908 × 0,633 = **1,87**; osservati **2**. Allineati.
**Terminale acceso all'ora dell'EoD: 0 sere su 5** — tre volte spento fra 8 e 17 minuti prima delle 21:55. Questa settimana non è costato nulla (nessuna posizione aperta a quell'ora), ma è la stessa abitudine dei §14.8, §16.11, §17.9. **Sul forward intero, il terminale è stato acceso all'ora dell'EoD in circa 8 sedute su 29.**

### 18.10 SERIE DI ESECUZIONE AGGIORNATE *(dettaglio in `COSTI_ESECUZIONE_REALI_FTMO_US100` rev 5.1 e nella tabella `ESECUZIONI_REALI_FTMO_US100_TRADE.csv`)*

- **Slippage d'ingresso, n = 35**: media **−0,02 pt**, dev. st. 2,22, IC95% [−0,78 ; +0,74], 17 sfavorevoli, 17 favorevoli, 1 nullo. Settimana: +5,71 · +0,81 · +0,80 · −1,70 · +1,90 · −2,20 (media +0,89, la più sfavorevole del forward). *L'aperto n.6 resta chiuso: rumore centrato su zero.*
- **Slippage sullo stop del breakout, n = 19**: media **+1,51%** (+0,59 pt), contro il 2,25% atteso dal backtest; i 4 nuovi +1,30 · +1,15 · **−1,65** · +1,35. Sui **15 stop con riancoraggio: −1,0181 R** contro −1,0225 del backtest.
- **Stop protettivi dell'IM, n = 3**: +0,18% · +0,73% · **+6,15% (5,51 pt)** → media −2,051 R contro −2,0549 del backtest a barre. *L'affermazione dei documenti precedenti che il backtest a barre «gonfi» l'attraversamento è ritirata (§18.16).*
- **Tutti i 22 stop in punti**: media **+0,80**, mediana +0,61, peggiore +5,51. *L'aperto n.7 resta aperto sulla coda estrema (oltre il 20%).*
- **Uscite a mercato, n = 11** (nuova: banda dell'IM del 30/09, 249,95 ms): 10 su 11 fra 189 e 250 ms.
- **Spread all'ingresso del breakout: 1,45 su 23 su 23.** Fuori orario USA nuovi estremi: **1,25** (30/09 13:29 server) e **2,19** (01/10 15:29, l'ora prima dell'apertura cassa).
- **Commissioni 0,00 su 33 trade su 33** dal 17/08. **Swap**: nessuna notte nuova.
- **Zero rifiuti** di qualunque tipo. **Deviation ignorata anche su un fill contrario**: +5,71 oltre i 5,0 impostati, senza requote (dopo il −6,50 a favore del 10/09).

### 18.11 CONTABILITÀ — conto 4 e somma finale

| Seduta | Data | Risultato | Bilancio conto 4 |
|---|---|---|---|
| — | 28/09 10:45 | apertura | 100.000,00 |
| **26** | **28/09** | **−1.567,32** (ORB −506,29 · IM −1.061,03) | 98.432,68 |
| **27** | **29/09** | **−426,13** (ORB) | 98.006,55 |
| **28** | **30/09** | **−425,58** (ORB −393,43 · IM −32,15) | 97.580,97 |
| **29** | **01/10** | **−384,01** (ORB) | 97.196,96 |
| **30** | **02/10** | **0,00** (terminale spento, §18.5) | **97.196,96** |

**Settimana**: ORB −1.709,86 $ (−4,02 R su 4) · IM −1.093,18 $ (−2,19 R su 2) → **−2.803,04 $**. Sei trade, sei perdite.

> **REGOLA CONTABILE A N CONTI** *(pre-registrata il 14/09)*
> `(96.113,02 − 99.497,56) + (97.018,85 − 100.000,00) + (108.018,50 − 100.000,00) + (97.196,96 − 100.000,00)`
> = −3.384,54 + (−2.981,15) + 8.018,50 + (−2.803,04) = **−1.150,23 $** su 30 sedute *(solo EA, come informazione: −1.130,95)*.
> **Quarto addendo DEFINITIVO**: il forward finisce con la seduta 30; quello che il conto 4 farà dopo non entra nella somma.
>
> **Soglia pre-registrata sulle 30 sedute: −6.437 $. Risultato: −1.150,23 → VERDE, con 5.286,77 $ di margine.**

**Il forward per EA** (21/08 → 01/10, 32 trade):

| | Trade | Vincenti | Somma in R | Somma in $ |
|---|---|---|---|---|
| **ORB** | 22 | 4 (18,2%, storico 19,3%) | **−4,46 R** | **+371,35 $** |
| **IM** | 10 | 3 | **−3,49 R** | **−1.505,79 $** |
| swap | | | | +3,49 $ |
| trade manuali (23-24/09) | | | | −19,28 $ |
| **Totale** | **32** | **7** | | **−1.150,23 $** |

> *L'ORB è negativo in R e positivo in dollari*: il dimensionamento a buffer ha dato più peso ai vincitori di settembre, arrivati con il conto 3 in crescita (fino a 704 $/R), che alle perdite, arrivate a 320-500 $/R. È il comportamento voluto del buffer, e un promemoria che **il P&L in dollari di un forward dipende dalla sequenza**, non solo dall'edge.

### 18.12 RICOSTRUZIONE DA ZERO DI TUTTO IL FORWARD — e una tabella per le altre chat *(nuovo)*

Per aggiornare i documenti destinati alle altre chat **senza estenderli per aggiunte** (lezione degli errori n.11 e n.12), tutti i **33 trade dal 17/08** sono stati ricostruiti da zero con uno script, leggendo i Report Cronistorici dei quattro conti e, per i tempi d'esecuzione, i journal giornalieri del terminale. Per i tre dati non coperti dai report oggi disponibili (trade del 09/09 e del 10/09, chiusura EoD del 24/09) si è usato il verbale (§15.1, §17.1), le cui cifre provengono dalle cronistorie dell'11/09 e del 26/09.
**Controlli automatici, tutti superati**: P&L di ogni trade = `lotti × (uscita − fill) × side` al centesimo (33 su 33) · **saldo finale di ciascuno dei quattro conti al centesimo** (96.113,02 · 97.018,85 · 108.018,50 · 97.196,96, compresi swap e trade manuali) · slippage d'ingresso dei riancorati = spostamento dello SL fra ordine e posizione · e soprattutto **la ricostruzione riproduce esattamente le statistiche della rev 4.1 dei costi**: n=29 media −0,204, dev. st. 2,073, IC95% [−0,99 ; +0,58]; 15 stop +1,773%; 11 stop riancorati −1,0228 R; distanza di riferimento 38,8629.
Il risultato è il file **`ESECUZIONI_REALI_FTMO_US100_TRADE.csv`** (md5 `24346a19fb9a7a8d0ad0b185150d772a`), una riga per trade, che accompagna da oggi i documenti per le altre chat. La tabella è stata poi **riverificata con un secondo script indipendente** (§18.19): 0 differenze.
Cinque incongruenze minori trovate nei documenti precedenti: vedi §18.16.

### 18.13 QUANTO È ANOMALA LA SOMMA A 30 SEDUTE

Bootstrap per giornata intera come al §17.12: struttura reale dei quattro conti (6 + 9 + 9 + 4 sedute attive; **le sedute 25 e 30, a zero per cause non di mercato, sono escluse dalla simulazione**, come la 25 lo era a 24 sedute), buffer ORB ricalcolato su ogni conto, IM a 500 $ diradato al 65% di uptime, 40.000 simulazioni, seed 7. Osservato (solo EA): **−1.130,95 $**.
*Controllo di replica*: rifatto a 24 sedute, lo stesso codice dà **54,0%** contro il **53,3%** del §17.12 (calendario ricostruito di 1.226 giornate contro 1.256): accordo entro un punto.

| Ipotesi | P(≤ osservato) | Mediana | Verosimiglianza «edge intatto» contro l'ipotesi *(densità a ±500 $)* |
|---|---|---|---|
| Edge **intatto** | **36,5%** *(seed-check 37,1%; blocchi di 5 giornate 35,1%)* | +1.364 | — |
| Edge **dimezzato** | 43,9% | −13 | 0,95 : 1 |
| Edge **nullo** | 51,2% | −1.361 | **1,00 : 1** *(seed-check 1,03)* |
| Edge **negativo** | 64,9% | −3.951 | 1,13 : 1 |

> **Il forward chiude al 36° percentile con l'edge intatto, e il risultato è esattamente altrettanto probabile con edge intatto e con edge nullo (1,0 : 1).** Traiettoria della somma: **2° percentile a 20 sedute → 53° a 24 → 36° a 30.** Il forward finisce come doveva finire per costruzione: **senza dire nulla sull'edge** — e lo si era scritto il 30/08, prima di vederlo.
> *Calibrazione, per completezza*: con la struttura reale dei quattro conti, P(somma < −6.437 | edge intatto) = **11,1%**, in linea con il 13% di falso positivo dichiarato quando la soglia fu fissata.

### 18.14 REGIME 2026 — aperto n.10, aggiornato

| | Backtest 2026 | **Con i trade del forward (21/08 → 01/10)** |
|---|---|---|
| ORB | +9,26 R su 129 | **+4,80 R su 151** (+0,032/trade), IC95% [−0,36 ; +0,42] |
| IM | −7,45 R su 97 | **−10,94 R su 107** (−0,102/trade), IC95% [−0,46 ; +0,25] |

Il forward dell'ORB da solo: **22 trade, −4,46 R, 4 vincenti (18,2%** contro il 19,3% storico). Entrambi gli intervalli contengono lo zero **e** la media storica (+0,178 e +0,144): **l'aperto n.10 resta apertissimo in entrambe le direzioni.** Unico indizio nuovo: gli stop rapidissimi (§18.8).

### 18.15 ⭐ ESITO DEL CRITERIO D — SECONDO E ULTIMO VERDETTO

| Cancello | Esito | Prova |
|---|---|---|
| **1(a)** ≥3 ordini IM dal vivo | ✅ **VERDE** — 10 | dal 24/08 al 30/09 |
| **1(b)** ≥1 chiusura EoD 22:55 osservata | ✅ **VERDE** — 5 | ORB 10/09, 22/09, 24/09 · IM 21/09, 22/09 |
| **1(c)** nessuna guardia per errore, nessun ordine fallito, nessun doppio trade | ✅ **VERDE nelle sedute 26-30** (zero rifiuti, zero guardie, zero doppi trade) · i difetti **D1-D4** emersi il 24-25/09 restano **da correggere prima dell'acquisto** | §17.8 |
| **1(d)** osservazioni da terminale acceso | ✅ **VERDE** | — |
| **1(e)** riancoraggi | ✅ **VERDE — 27 su 27** con le build P/E, nessuna riga di ATTENZIONE | §18.2 |
| **2 — somma a 30 sedute ≥ −6.437 $** | ✅ **VERDE — −1.150,23 $** | margine 5.286,77 $ (§18.11) |

> **Il criterio D, applicato per la seconda e ultima volta come pre-registrato il 30/08, dà VERDE.** Ne segue, **per regole già scritte e non per decisioni nuove**:
> 1. **Il progetto non si ferma** (il punto 4 del §12.4 non scatta) e **il criterio autorizza l'acquisto della challenge**, alle condizioni già fissate al §17.8.
> 2. **Prima di qualunque acquisto**: build **Q** (ORB) ed **F** (IM) con le correzioni **D1-D4**; acceptance cella per cella contro P/E nel tester (devono risultare identiche, come P≡O ed E≡D); collaudo dal vivo a costo zero agganciandole al **conto 3, disabilitato** (devono scrivere un messaggio e fermarsi, non ritentare). ⚠️ **Sigla F**: nella cartella `Experts` esistono già `IntradayMomentum_NAS100_F_senzaHalt` e `_G_senzaHalt` (compilate il 29/09), prodotte da un lavoro parallelo e **non verificate da questo verbale**: prima dell'acceptance va stabilito quale file è la build F pre-registrata e che cosa contiene di diverso da E oltre a D1-D4.
> 3. **Verifica voce per voce dei parametri** prima dell'acquisto (trappola dei default, §12.5 e §13.6), con baseline esplicita.
>
> **Il verdetto verde non dice che l'edge c'è** (verosimiglianza 1,0 : 1, §18.13). Dice che il forward ha fatto il lavoro per cui era nato — misurare **meccanica e costi reali** dal vivo, che si sono rivelati in linea con il modello o migliori — e che il criterio monetario di protezione non ha trovato motivi per fermarsi.
>
> **Raccomandazioni non vincolanti emerse da queste cinque sedute** (la decisione resta di Manu):
> - **VPS dal primo giorno della challenge.** In 30 sedute l'uptime del PC ha fatto perdere una seduta intera, ~35% dei check del momentum, un check con posizione aperta seguito dallo stop peggiore del forward, circa tre chiusure di fine giornata su quattro (terminale acceso all'ora dell'EoD in circa 8 sedute su 29) e tre notti fuori modello. Nessuno di questi costi è nel backtest.
> - **Scegliere consapevolmente Standard o Swing.** La configurazione del progetto (freni, piano di passaggio al funded) è stata pensata su Standard (leva 1:100); il conto 4 era Swing (1:30). Per il margine dei nostri EA non cambia nulla; per il conto finanziato cambiano le regole su news e weekend (Swing non le ha) e la leva.

### 18.16 ERRORE A VERBALE — il tredicesimo

Ricalcolando tutto da zero (§18.12) sono emerse cinque incongruenze nei documenti precedenti, **nessuna delle quali tocca il forward o le sue conclusioni**:
(a) `COSTI` rev 4.1 e `DOSSIER` rev 2 davano il rischio effettivo senza riancoraggio nei casi estremi «da **0,83×** a 1,10×»: il minimo corretto è **0,81×** (10/09: 28,33 punti di distanza reale contro 34,83 voluti — il valore era già giusto al §15.3, in dollari). Con il 28/09 il massimo sale a 1,13×;
(b) gli stessi documenti affermavano che il backtest a barre del momentum **«gonfia»** l'attraversamento degli stop, sulla base di **due** casi dal vivo (+0,18%, +0,73%): il terzo (+6,15%) porta la media dal vivo vicino a quella del backtest. **Ritirata**: con tre casi non si distingue nulla;
(c) i tempi d'esecuzione degli ingressi erano su «20 documentati» (mediana 234 ms): letti ora dai journal per tutti e 27 gli ingressi fino al 24/09, la mediana è **232 ms**. Immateriale;
(d) il §15.4 attribuiva le righe `posizione visibile dopo attesa` a «27/08 ×2, 08/09»: le date giuste sono **26/08, 27/08 e 08/09** (il §7.1 cita la riga del 26/08, il §11.2 la tabella 26/08-27/08);
(e) il dossier rev 2 contava «due aggiornamenti» del terminale fino alla 6182: è corretto, e con la 6230 sono **tre aggiornamenti, quattro build** — ma il §14.7(d) di questo verbale chiamava la 6182 «terzo aggiornamento»: era la terza **build**, il secondo aggiornamento.
*Lezione: un'affermazione generale costruita su due casi va scritta come tale («con due casi…»), non come proprietà del sistema.*

### 18.17 ESITO

**Sedute 26-30 CERTIFICATE. FORWARD CHIUSO A 30 SU 30.**
Quadratura al centesimo su 6 trade su 6 e — con la ricostruzione da zero — su tutti i 33 trade dal 17/08 e sui saldi dei quattro conti. Riancoraggio 6/6 (**27/27** con le build P/E). Conto 4 = **Free Trial Swing, leva 1:30**, costi identici. Uno stop con **+5,51 punti** di slittamento in un movimento rapido senza notizie; **R1 osservato nel verso permissivo**; **seduta 30 persa per uptime**.
**Somma a 30 sedute: −1.150,23 $ contro una soglia di −6.437 $ → SECONDO VERDETTO VERDE.** 36° percentile con l'edge intatto, verosimiglianza 1,0 : 1: nessuna informazione sull'edge, come previsto.
**Prossime azioni**: (1) consegnare alle chat parallele il pacchetto del §18.18; (2) build Q/F, acceptance e collaudo sul conto 3 (§17.8, §18.15); (3) decisione d'acquisto — tipo di conto e VPS — di Manu.

### 18.18 DOCUMENTI PER LE CHAT PARALLELE — pacchetto del 06/10/2026

Nella cartella `COSTI gestione reali FTMO` (le versioni precedenti restano in `Old`, intatte):
- `00_LEGGIMI_PACCHETTO_FTMO.md` — indice del pacchetto, ordine di lettura e impronte;
- `DOSSIER_FTMO_PER_NUOVE_STRATEGIE` **rev 3.1** (md5 `bbb4deaafc4a46e33dd1ba7e3fe95491`);
- `COSTI_ESECUZIONE_REALI_FTMO_US100` **rev 5.1** (md5 `6e361905d7fe8d1bf4de4f53506b16cd`);
- `ESECUZIONI_REALI_FTMO_US100_TRADE.csv` (33 trade, md5 `24346a19fb9a7a8d0ad0b185150d772a`);
- questo verbale, sedute 1-30.

**`COSTI` rev 4.1 e 5, `DOSSIER` rev 2 e 3 non vanno più usati** (le rev 5 e 3, consegnate a Manu il 06/10 mattina, sono superate dalle 5.1 e 3.1 dopo il doppio controllo del §18.19; i valori misurati sono gli stessi).

### 18.19 DOPPIO CONTROLLO DEL PACCHETTO — 06/10/2026, su richiesta di Manu · errore a verbale n.14

Prima della consegna alle chat parallele, il pacchetto è stato ricontrollato **con strumenti nuovi, non con quelli che lo avevano prodotto**:

| Verifica | Metodo | Esito |
|---|---|---|
| **Tabella dei 33 trade** | secondo script, scritto da zero: ogni campo confrontato con le cinque cronistorie disponibili (posizioni, ordini, posizioni aperte) e con le righe d'ordine, di deal e di modifica dei journal; coerenze interne (P&L, slippage, distanze, TP = 8·dist, R) | **0 differenze su 33 trade.** I tre dati presi dal verbale (09/09, 10/09, chiusura EoD del 24/09) sono confermati dalle righe di deal dei journal originali (`buy 9.57 at 29454.88` / `sell 9.57 at 29417.98`; `buy 9.42 at 29066.48` / `sell 9.42 at 29114.48`; `sell 16.6 at 30484.32`) |
| **Statistiche citate** | 108 controlli: valori citati ricalcolati dal CSV con codice nuovo e confrontati automaticamente col testo | **tutti coincidono**; l'unica differenza è di 1 sull'ultima cifra della media dei 15 stop riancorati (−1,0182 ricalcolata dal CSV, che arrotonda `R` a 4 decimali, contro −1,0181 a precisione piena): aggiunta una nota nei documenti |
| **Fatti tratti dai log** | uptime e check ricostruiti in automatico dai journal; ping, riconnessioni, istantanee di spread di US100.cash e dell'oro rilette | tutto coincide (check 11/11/12/4/0; ping 38,53-66,94 ms; sei riconnessioni) |
| **Rilettura integrale** | DOSSIER, §18 del verbale, LEGGIMI, COSTI | correzioni di forma qui sotto |

**Il verificatore ha sbagliato per primo**: alla prima esecuzione ha segnalato 6 errori, tutti su tre trade in cui l'ordine è datato un secondo prima della posizione (17:00:00 contro 17:00:01; 16:37:13 contro 16:37:14). Abbinando ordine e posizione per ticket invece che per orario, gli errori sono spariti. *Conferma della lezione del §16.13: quando gli errori sono tutti dello stesso tipo, il primo sospettato è il verificatore.*

**Correzioni ai documenti consegnati il 06/10 mattina** — tutte di forma, **nessun valore misurato né alcuna conclusione cambia**:
(a) «riancoraggio 27 su 27»: precisato che gli ingressi con le build P/E sono 28 e che il 28° (04/09) aveva slippage zero (§18.2, COSTI §1.2);
(b) mediana delle istantanee di spread dell'oro **0,405** (media 0,40), non 0,40 (COSTI §2.10, DOSSIER §2.4);
(c) DOSSIER §2.4: «33 trade **del forward**» → «dal 17/08», lo stesso errore già corretto nella rev 4.1 (punto s);
(d) §18.3: le Init non sono «uguali carattere per carattere» (cambia il rischio del giorno): sono uguali i parametri;
(e) §18.4: la differenza teorica massima del freno di R1 è ~67 $, non ~60 $ (va contata fino al prezzo eseguito dello stop, non fino al livello);
(f) §18.12 diceva «tre incongruenze», il §18.16 ne elencava quattro e in realtà sono cinque; corretto anche il §18.16(e), che attribuiva al dossier rev 2 un errore che non c'era;
(g) §18.15: «quasi tutte le chiusure di fine giornata» perse → «circa tre su quattro»;
(h) LEGGIMI: il P&L del CSV era descritto come «lordo di swap», formula ambigua: è il P&L sul prezzo, **swap escluso** (colonna a parte); aggiunte la descrizione di `MKT-riavvio` e le note sull'arrotondamento e sull'ingresso a slippage zero;
(i) il conto pre-forward `1514172196` registrò tre ingressi (04, 06 e 07/08), non due: lo slippage è documentato per due (COSTI, piè di pagina).
*Lezione: anche un documento ricalcolato da zero contiene errori di formulazione che nessun ricalcolo trova; servono entrambe le verifiche, quella dei numeri e la rilettura riga per riga.*
