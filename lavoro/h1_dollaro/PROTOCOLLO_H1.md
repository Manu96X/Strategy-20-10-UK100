# PROTOCOLLO PRE-REGISTRATO — H1 «il dollaro segue i metalli con un giorno di ritardo»
*Scritto il 20/10/2026 **prima di qualunque risultato su forex e 2024**: lo certifica l'orario del commit. Manu ha scelto H1 («Parti da H1») sulla base di `f4_event_study/ROSA_IPOTESI_F1.md`. Correzioni successive solo come addendum datati «prima/dopo i numeri».*

## 0. Cosa è già stato visto (trasparenza)
- **Scoperta** (event study F1, dati < 2024): XAU oggi → USDX domani, pendenza **−0,107 z**, t −3,8, permutazioni p 0,00059 (soglia BH 0,00041: non superata); XAG → USDX t −3,1. Periodo: **22/04/2019 → 29/12/2023** (USDX Pepperstone). Un revisore ha visto, sugli stessi dati, che l'effetto sta nella sessione **08:20-16:00 NY** del giorno dopo.
- **Mai visti**: le 6 coppie forex FTMO (rendimenti), l'USDX prima del 22/04/2019, tutto il 2024 e il 2025-2026.
- Visti **solo come qualità o costo** (nessun rendimento): audit dei file forex su tutto il periodo (`f0/risultati_nuovi`), colonna SPREAD forex 10/10/2025 → 09/10/2026 (`risultati/SPREAD_FX_FTMO_per_ora.csv`), swap dalla specifica FTMO.

## 1. Dati (sigillati il 20/10/2026, `/home/user/dati_h1/SIGILLO.txt`)
| Uso | Strumenti | Periodo |
|---|---|---|
| Segnale | XAU e XAG **Pepperstone** (feed della scoperta); fuso NY+7 | barre H1 fino al 09/06/2017, poi M1 |
| Bersaglio | EURUSD, GBPUSD, AUDUSD, USDJPY, USDCHF, USDCAD **FTMO** | M1 dal 2015 (GBPUSD: alcune barre H1 a inizio 2019) |
| Concordanza | USDX Pepperstone (prima del 22/04/2019: mai visto) | |
| **Hold-out** | tutto il 2025-2026 | **non copiato, resta sigillato** |

**Fuso del forex FTMO** (F0-bis, `fuso_per_anno_generico.py`): fino al 2019 l'ora server segue l'**ora legale europea** (server = ora di Atene: nelle settimane di disallineamento è New York + 6); dal 2021 è New York + 7; il 2020 è incerto nelle settimane di disallineamento. Ogni istante si fissa in **ora di New York** e si converte nell'ora server con la regola del periodo.

## 2. Definizioni (identiche alla scoperta, `famiglia_F.py`)
- **Prezzo alle 16:00 NY** = close dell'ultima barra che inizia prima delle 16:00 NY: entro 15 minuti per i giorni M1; entro 60 minuti nei giorni in cui il passo modale delle barre è di 60 minuti (barre H1: la barra delle 15:00 chiude alle 16:00).
- d = giorni feriali di New York con prezzo; rendimento r(d) = ln(P(d)/P(d−1)), con d−1 la riga valida precedente entro 4 giorni di calendario.
- σ(d) = deviazione standard degli ultimi 20 rendimenti validi **fino a d incluso**; z(d) = r(d)/σ(d).
- **Segnale** S(d) = [z_XAU(d) + z_XAG(d)] / 2.
- **Paniere del dollaro** (pesi uguali, verso «dollaro forte»): R_B = media di [−r_EURUSD, −r_GBPUSD, −r_AUDUSD, +r_USDJPY, +r_USDCHF, +r_USDCAD]; σ_B(d) come sopra sui rendimenti del paniere; giorni con tutte e 6 le coppie valide.
- **Finestre** sul giorno d+1 (riga valida successiva entro 4 giorni):
  - **W1** (replica della scoperta): 16:00 NY di d → 16:00 NY di d+1; y = R_B(W1)/σ_B(d).
  - **W2** (versione negoziabile, senza swap): ingresso all'open del primo M1 che inizia alle 08:20 NY di d+1 o dopo (entro 15 minuti), uscita al prezzo delle 16:00 NY di d+1; y = R_B(W2)/σ_B(d).
- **Strategia**: ogni giorno posizione sul dollaro = **−segno(S(d))** (metalli su → dollaro short), stesso peso su tutte e 6 le coppie.

## 3. Costi FTMO (di oggi) [SPECIFICA] [MISURATO] [STIMA]
- **Spread**: p75 della colonna SPREAD (minimo del minuto) degli ultimi 12 mesi per ora server, **minimo 0,1 pip**; ora dell'ingresso per i long, dell'uscita per gli short (prezzi bid, acquisto all'ask). Ore usate: 08:20 NY → ora server 15; 15:59 NY → ora server 22.
- **Commissione**: 2,50 $ per lotto per lato (dossier FTMO, misurata su EURUSD e USDJPY) → 5 $ per 100.000 unità di valuta base a round-trip.
- **Swap** (solo W1, una notte; ×3 se la notte è mercoledì → giovedì): valori della specifica FTMO (`specifiche_simboli.csv`), in $ per lotto: EURUSD −9,41/+0,10 · GBPUSD −8,40/−5,55 · AUDUSD −3,07/−8,35 · USDJPY +1,64/−11,10 · USDCHF +0,71/−19,63 · USDCAD +0,67/−8,95 (long/short).
- **Stress**: spread ×1,5, più 0,1 pip di slittamento per ogni ordine a mercato (2 per trade), swap ×1,5.
- Costo del paniere = media dei costi delle 6 coppie (in frazione del prezzo), in z dividendo per σ_B(d).

## 4. Test e cancelli
### Stadio A — indipendente: giorni d+1 dall'inizio dei dati al **19/04/2019** (prima della scoperta)
- **A1 (PRIMARIO)**: pendenza OLS b di y(W1) su S(d); p **unilaterale** (b < 0) con 100.000 permutazioni di S. **VERDE** p < 0,05 · **GIALLO** b < 0 e p < 0,20 · **ROSSO** altrimenti.
- A2: media netta (base e stress) della strategia su W2, con t.
- **Regola di arresto**: A1 ROSSO → **H1 BOCCIATA**; il 2024 resta sigillato (servirà ad altre ipotesi).

### Stadio B — validazione: giorni d+1 nel **2024** (aperto una sola volta, solo se A1 non è ROSSO)
- B1: pendenza b su W1 nel 2024 (p unilaterale); **A+B insieme**: pendenza e p unilaterale (100.000 permutazioni).
- B2: media netta della strategia su W2 nel 2024.

### Verdetto (deciso ora)
- **PROMOSSA alla F4** (progetto, Monte Carlo FTMO, indipendenza; hold-out ancora sigillato) se **tutte**: p(A+B) < 0,05 unilaterale · b < 0 sia in A sia in B · W2 netto base > 0 sia in A sia in B · W2 netto stress (A+B) > 0 · t del W2 netto base (A+B) ≥ 1,645.
- **EFFETTO REALE MA NON SFRUTTABILE** se p(A+B) < 0,05 e b < 0 in A e in B, ma le condizioni sul netto falliscono.
- **BOCCIATA** in tutti gli altri casi.

## 5. Analisi descrittive (non entrano nel verdetto)
- **A0, diagnostico sul periodo della scoperta** (22/04/2019 → 2023, esclusi i giorni del 2020 nelle settimane di disallineamento): pendenza del paniere forex contro quella dell'USDX sugli stessi giorni. Se il forex non mostra l'effetto mentre l'USDX sì, la scoperta è sospetta di **artefatto del CFD USDX**.
- **C1**: USDX Pepperstone come bersaglio nello stadio A (stesso strumento della scoperta, periodo mai visto).
- Per coppia; segnale solo XAU e solo XAG; strategia lineare (posizione ∝ −S); W1 netto con swap; per anno; senza il 2% dei giorni più influenti; prezzo robusto (mediana degli ultimi 5 close) per i file forex 2019 con barre anomale; segnale dai metalli FTMO.

## 6. Doppio controllo prima di comunicare
Replica cieca (codice scritto da zero solo da questo protocollo) e revisore avversario (fuso, anticipo dei dati, costi, segni), come in F3 e nell'event study. I numeri si comunicano solo se replica e originale coincidono.
