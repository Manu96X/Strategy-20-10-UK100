# PIANO PRE-REGISTRATO — EVENT STUDY MULTI-STRUMENTO (F1-bis)
*Scritto il 20/10/2026 **prima di qualunque risultato**: lo certifica l'orario del commit, precedente ai risultati. Scopo: trovare effetti con meccanismo dichiarato, da cui scegliere la nuova rosa di ipotesi (F1). Dati: solo copie sigillate < 01/01/2024 (`/home/user/dati_scoperta_tutti`). **2024 (validazione) e 2025-2026 (hold-out) restano sigillati**: saranno l'unico campione di conferma per le ipotesi scelte, perché 2017-2023 diventa campione di esplorazione.*

## 0. Regole comuni
- **Strumenti** (feed d'inferenza → concordanza): US500 (Pepperstone dal 13/07/2020 → FTMO), US100 (NAS100 Pepperstone dal 09/06/2017 → FTMO), GER40 (Pepperstone dall'11/06/2020 → FTMO), UK100 (Pepperstone dal 06/06/2017 → FTMO), XAU e XAG (Pepperstone dal 12/06/2017 → FTMO dal 04/01/2021), BRENT (Pepperstone dal 02/04/2018), USOIL (solo FTMO dal 05/04/2021), VIX (Pepperstone, future, **non negoziabile su FTMO**: solo come segnale), USDX (Pepperstone dal 22/04/2019; su FTMO c'è DXY.cash).
- **Chiusura giornaliera**: indici alla chiusura cash locale (16:00 New York, 17:30 Francoforte, 16:30 Londra; mezze sedute anticipate); gli altri strumenti alle 16:00 di New York. Prezzo = close dell'ultimo M1 che inizia prima dell'orario (entro 15 minuti). Modulo `eventi_comune.py`.
- **Unità**: rendimento della finestra W = ln(P_uscita/P_ingresso); **z** = W / σ_ingresso, con σ_ingresso = deviazione standard dei 20 rendimenti giornalieri fino al giorno d'ingresso **incluso** (nota all'ingresso).
- **Anomalo** = z della finestra − media degli z di tutte le finestre della stessa lunghezza dello stesso strumento (benchmark incondizionato, stesso periodo).
- **Per ogni test**:
  - n eventi, media z, media anomala, bps medi;
  - t con errore raggruppato per data dell'evento (CR1);
  - **p del placebo** bilaterale: 2.000 estrazioni di finestre della stessa lunghezza prese a caso negli stessi anni. È il p che entra in Benjamini-Hochberg;
  - quota degli anni con lo stesso segno;
  - eventi per anno;
  - concordanza: media anomala sul feed FTMO nel periodo comune;
  - **netto dei costi** in unità z, scenari base e stress: ingresso all'ask, uscita al bid, `costo_trade` con spread FTMO 2026 per ora, commissione e swap per notte di calendario. Se l'effetto è negativo il trade è short.
- **Correzione per test multipli**: Benjamini-Hochberg q = 0,10 su **tutti i 242 test** del piano.
- **Classificazione** (esplorativa, serve solo a scegliere le ipotesi):
  - **PROMETTENTE** se supera BH, ha lo stesso segno su FTMO (se esiste il feed), ha ≥ 60% degli anni con lo stesso segno, ha media netta (base) > 0 nel verso dell'effetto e un meccanismo dichiarato;
  - **INDIZIO** se p del placebo < 0,05 senza BH, con concordanza e anni ok;
  - **NULLO** altrimenti.

## 1. Famiglie (meccanismo → test)
| Fam. | Effetto e fonte | Meccanismo | Test |
|---|---|---|---|
| **A** | **Turn of the month** (Lakonishok-Smidt 1988; McConnell-Xu 2008) e **ribilanciamento di fine mese** (Harvey-Mazzoleni-Melone 2025) | flussi di stipendi e pensioni a inizio mese; i fondi bilanciati vendono azioni a fine mese dopo un mese forte e le ricomprano dopo | A1: finestra [ultimo giorno del mese TD−1 → TD+3] (ingresso alla chiusura di TD−2), **10 strumenti**. A2 (4 indici): pendenza del rendimento [TD−3, TD−1] e [TD+1, TD+2] sul rendimento del mese fino a TD−4 (z), attese < 0 e > 0 → **8**. Totale **18** |
| **B** | **Drift pre-FOMC** (Lucca-Moench 2015) | premio per l'incertezza che si scioglie all'annuncio | B1: dalle 14:00 NY del giorno prima alle 13:55 NY del giorno FOMC; B2: dalle 14:05 NY del giorno FOMC alle 16:00 NY del giorno dopo; **10 strumenti × 2 = 20**. Placebo: le stesse finestre orarie nei giorni senza FOMC |
| **C** | **Scadenza delle opzioni** (Stivers-Sun 2013) e **pre-festivi** (Ariel 1990; Kim-Park 1994) | coperture dei dealer in scadenza; chiusura degli short e liquidità prima dei festivi | C1 settimana OPEX (chiusura del venerdì prima → chiusura del terzo venerdì); C2 settimana dopo; C3 solo OPEX trimestrali; C4 giorno pre-festivo (calendario della borsa dell'indice); C5 giorno post-festivo; **4 indici × 5 = 20** |
| **E** | **Lunedì in calo → recupero** (French 1980; Connors «Turnaround Tuesday»; nostra A2) | pressione di vendita del lunedì (notizie del weekend) riassorbita | E1: lunedì chiuso sotto la chiusura precedente → rendimento martedì; E2: martedì + mercoledì; **10 strumenti × 2 = 20**; E3: notte lunedì → martedì (chiusura cash → apertura cash), **4 indici**. Totale **24**. E4 descrittivo (fuori dalla correzione): rendimento per giorno della settimana |
| **F** | **Correlazioni e anticipi fra strumenti** (Hanna 2024) | informazione che si diffonde con ritardo fra mercati; ritorno dopo i picchi di paura | F1: rendimento giornaliero di ogni strumento alle 16:00 NY (z) → rendimento del giorno dopo di ogni strumento, **10 × 10 = 100** regressioni (p per permutazione). F2: VIX alla chiusura sul massimo di 10 giorni → rendimento degli indici a 1 e 3 giorni, **4 × 2 = 8**. Totale **108** |
| **G** | **Flussi intraday a orario noto sulle materie prime** | report EIA del mercoledì alle 10:30 NY; sessione notturna contro sessione COMEX per metalli ed energia | G1: reazione ai primi 5 minuti dopo l'EIA (10:30 → 10:35) → deriva 10:35 → 12:00 (pendenza) e media della deriva, **BRENT e USOIL × 2 = 4**. G2: notte (16:00 → 08:20 NY) e giorno (08:20 → 16:00 NY) per XAU, XAG, BRENT, USOIL, **8**. Totale **12** |
| **I** | **Momentum di serie storica** (Moskowitz-Ooi-Pedersen 2012; Hurst-Ooi-Pedersen 2017; Hill 2019; SigTech 2022) | sotto-reazione e poi sovra-reazione degli investitori, coperture | a ogni fine mese, segno del rendimento degli ultimi L mesi (L = 1, 3, 6, 12) → rendimento del mese dopo nel verso del segnale; **10 strumenti × 4 = 40** |

**Totale: 18 + 20 + 20 + 24 + 108 + 12 + 40 = 242 test.** Nessun test aggiunto dopo i numeri; eventuali analisi in più saranno marcate «dopo i numeri».

## 2. Controlli sui risultati
I PROMETTENTI (o, se sono meno di 4, i primi per p) vengono **ricalcolati da zero** da revisori indipendenti, che cercano attivamente di smontarli:
- anticipo e calendario, cioè date e orari;
- effetto di pochi eventi estremi, togliendo il 2020;
- stabilità anno per anno;
- confronto fra i due feed.

## 3. Dopo
Dai PROMETTENTI e dagli INDIZI con meccanismo forte si scrive la **rosa di 3-6 ipotesi** (§8 del prompt) per la scelta di Manu. Per ognuna:
- meccanismo;
- strumenti e frequenza;
- costo in R;
- indipendenza dai suoi EA;
- perché non è una variante del già bocciato;
- **potenza attesa sul campione di conferma 2024-2026**.
