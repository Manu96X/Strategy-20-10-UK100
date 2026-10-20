# PACCHETTO FTMO — COSTI REALI DI ESECUZIONE E LEZIONI DAL FORWARD
### Indice per la chat che riceve questi file · aggiornato al **06/10/2026** (forward chiuso: 30 sedute, 21/08 → 02/10/2026)

> **Che cos'è.** L'unica misura diretta che il progetto possiede dei **costi reali di esecuzione** su MetaTrader 5 / FTMO (`US100.cash`, server `FTMO-Demo`), ricavata da un forward test di due Expert Advisor — un breakout d'apertura (*ORB*) e un intraday momentum (*IM*) — su quattro conti demo Free Trial, più tutto ciò che quel forward ha insegnato su regole FTMO, trappole della piattaforma, infrastruttura e metodo.
> **A cosa serve.** A stimare se una strategia nuova sopravvive **al netto dei costi reali e delle dinamiche FTMO**, e a validarla o scartarla con una checklist esplicita.

---

## 1. ORDINE DI LETTURA

| # | File | Leggilo per… | Tempo |
|---|---|---|---|
| 1 | **`DOSSIER_FTMO_PER_NUOVE_STRATEGIE.md`** (rev 3.1) | il quadro completo: **17 regole d'oro** (§1), costi riassunti, regole FTMO reali, trappole di MT5, infrastruttura, metodo, **idee già scartate** (§8) e la **checklist di validazione o scarto** (§11) | 20-30 min · *se hai 5 minuti: §1 e §11* |
| 2 | **`COSTI_ESECUZIONE_REALI_FTMO_US100.md`** (rev 5.1) | i **numeri dei costi** nel dettaglio: le sei trappole di misura (§1), spread, slippage, commissioni, swap, latenze (§2), oro (§2.10), **come trasformarli in costo per trade senza contarli due volte** (§4), limiti del campione (§5) | 20 min · *se hai fretta: §7* |
| 3 | **`ESECUZIONI_REALI_FTMO_US100_TRADE.csv`** | i **dati grezzi**: 33 trade, uno per riga, riconciliati al centesimo. Serve se devi ricalcolare una statistica che nei documenti non c'è | — |
| 4 | `VERBALE_FORWARD_SEDUTE.md` (sedute 1-30) | solo per la **tracciabilità**: seduta per seduta, ogni trade, ogni anomalia, ogni decisione e ogni errore commesso, con le impronte dei file sorgente | consultazione |

La cartella `Old` contiene le versioni precedenti (`COSTI` rev 4.1, `DOSSIER` rev 2, verbale sedute 1-25): **non vanno più usate**, come le rev 5 e 3 circolate la mattina del 06/10 prima del doppio controllo (stessi valori misurati, alcune formulazioni corrette).

---

## 2. IMPRONTE DEI FILE (md5)

| File | Revisione | md5 |
|---|---|---|
| `DOSSIER_FTMO_PER_NUOVE_STRATEGIE.md` | rev 3.1 del 06/10/2026 | `bbb4deaafc4a46e33dd1ba7e3fe95491` |
| `COSTI_ESECUZIONE_REALI_FTMO_US100.md` | rev 5.1 del 06/10/2026 | `6e361905d7fe8d1bf4de4f53506b16cd` |
| `ESECUZIONI_REALI_FTMO_US100_TRADE.csv` | 06/10/2026, 33 trade | `24346a19fb9a7a8d0ad0b185150d772a` |
| `VERBALE_FORWARD_SEDUTE.md` | sedute 1-30, §18 del 06/10/2026 | `5830dc0804ef4c110931603c6d2e6bfd` |

*Le impronte permettono a chi riceve i file di verificare di avere esattamente queste versioni (in PowerShell: `Get-FileHash -Algorithm MD5 <file>`).*

---

## 3. I DIECI NUMERI DA NON SBAGLIARE *(US100.cash su FTMO-Demo, 2026)*

1. **Commissioni: 0,00** su US100.cash (33 trade su 33). Ma **FX 2,50 $** e **oro 3,00 $ per lotto per lato**: lo zero vale solo per questo simbolo.
2. **Spread: 1,45 punti indice** alle 16:35 server (23 ingressi su 23) e in tutte le letture dal vivo in orario USA; **1,25-1,95** la mattina europea; **fino a 2,19** nell'ora prima dell'apertura cassa. **Una volta per round-trip.** Lo spread del 2026 è 2,4 volte quello del 2021: un backtest pluriennale lo sottostima.
3. **Slippage d'ingresso a mercato: media −0,02 punti su 35 ordini** (dev. st. 2,22): rumore, non costo — ma rumore sul rischio, da neutralizzare **riancorando stop e target al fill**.
4. **Slippage sugli stop del server: ≈0,8 punti di media** (22 stop; +0,59 sui 19 del breakout = +1,5% della distanza), peggiore **5,51 punti**. **Solo le uscite a livello lo pagano**: il costo dipende dal **mix di uscite** della strategia, contato sul backtest.
5. **Costo in R = punti ÷ distanza dello stop**: 1,45 di spread sono 0,036 R su 40 punti e **0,097 R su 15**.
6. **Non contare i costi due volte**: in un backtest MT5 su tick reali l'attraversamento degli stop è già dentro (backtest −1,0225 R agli stop, dal vivo −1,0181 R).
7. **`CTrade::ResultPrice()` su FTMO restituisce il prezzo richiesto**: lo slippage si misura con `POSITION_PRICE_OPEN` o con il Report Cronistorico.
8. **Limite FTMO di 2.000 richieste al server al giorno**: un EA che ritenta senza leggere il codice d'errore lo supera in minuti (visti ~3.000 rifiuti in 5 minuti).
9. **Leva per tipo di conto**: Standard 1:100 (US100.cash a margine 2,00% = 1:50), **Swing 1:30**; costi d'esecuzione identici sui due tipi (6 trade sullo Swing).
10. **Il P&L di poche settimane non misura l'edge**: il nostro forward è passato dal 2° al 53° percentile in quattro sedute e ha chiuso al 36°, con verosimiglianza 1:1 fra edge intatto ed edge nullo.

---

## 4. ISTRUZIONI PER LA CHAT CHE RICEVE IL PACCHETTO

- **I numeri di costo valgono per `US100.cash` su `FTMO-Demo`.** Regole, trappole e metodo valgono ovunque; spread e slippage vanno ri-misurati su ogni simbolo nuovo (per l'oro ci sono commissioni, istantanee di spread e specifica dello swap, non lo slippage).
- **Ogni dato è etichettato** [MISURATO], [BACKTEST], [REGOLA FTMO], [STUDIO ESTERNO] o [STIMA]: non promuovere una stima a misura.
- **Applica la checklist G1-G8** del dossier (§11), con le soglie scritte **prima** di guardare i risultati, e dichiara quali cancelli passano.
- **Conto demo**: nessuna misura è stata confermata su denaro vero. È il limite più serio (COSTI §5.1).
- **Strategie parallele**: se la tua strategia deve girare accanto all'ORB e all'IM, leggi il dossier §9 (magic number, freni condivisi, correlazione) e **non usare il conto di un forward in corso**.

---

## 5. IL FILE CSV — legenda delle colonne

Separatore `;`, decimali col punto, orari in **ora server FTMO** (New York + 7), una riga per trade dal 17/08/2026. Convenzione di segno: **`+` = sfavorevole**.

| Colonna | Significato |
|---|---|
| `n`, `conto`, `tipo_conto` | progressivo; numero del conto; `FreeTrial2Step` (Standard) o `FreeTrialSwing2Step` |
| `ea`, `build` | `ORB` (breakout, stop e target sul server) o `IM` (momentum, stop protettivo sul server a 2×dist, uscite a mercato); build letta dal commento d'ordine |
| `apertura_srv`, `chiusura_srv`, `direzione`, `lotti` | dal Report Cronistorico |
| `dist_prog_pt` | distanza di stop progettata in punti indice (ORB: stop a 1×dist; IM: stop a 2×dist) |
| `prezzo_richiesto` | prezzo del segnale: **letto dal log** per i 4 trade non riancorati, **derivato** dallo stop dell'ordine per gli altri |
| `fill`, `slip_ingresso_pt` | prezzo eseguito; slippage d'ingresso |
| `spread_ingresso_pt` | spread all'ingresso stampato dall'EA (solo ORB) |
| `riancorato`, `sl_ordine`, `sl_posizione`, `tp_posizione` | se stop e target sono stati riportati al fill (`si`/`no`; i 4 `no` sono gli ingressi delle build O e D, 21-25/08); livelli inviati e livelli in vigore. Il 04/09 (IM) `si` con slippage 0,00: non c'era nulla da spostare |
| `uscita_tipo`, `prezzo_uscita` | `SL` (stop del server), `MKT-EoD` (chiusura di fine giornata alle 22:55), `MKT-banda` (rientro in banda dell'IM al check semi-orario), `MKT-riavvio` (posizione del giorno prima chiusa dall'EA alla riaccensione del terminale), `MKT-riapertura` (posizione del giorno prima chiusa alle 01:05, alla riapertura delle quotazioni) |
| `slip_uscita_livello_pt`, `slip_uscita_pct_dist` | slittamento oltre lo stop, in punti e in % della distanza fill→stop (solo uscite `SL`) |
| `pnl_usd`, `swap_usd`, `commissioni_usd` | dal Report Cronistorico: `pnl_usd` è il P&L sul prezzo, **swap escluso** (lo swap è nella sua colonna) |
| `R` | P&L ÷ (lotti × `dist_prog_pt`); per l'IM lo stop protettivo vale −2R |
| `ms_ingresso`, `ms_modify`, `ms_uscita_mercato` | tempi d'esecuzione dal journal del terminale |
| `fonte` | `cronistoria` o, per tre dati, il verbale con la cronistoria d'origine (tutti e tre confermati anche dalle righe di deal dei journal) |

**Arrotondamenti**: `R` ha 4 decimali, le percentuali 2. Le statistiche dei documenti sono calcolate a precisione piena: ricalcolando una media dal CSV si può trovare una differenza di 1 sull'ultima cifra (es. −1,0182 invece di −1,0181 sui 15 stop riancorati).

Oltre ai 33 trade, le statistiche d'ingresso dei documenti includono due ingressi pre-forward (agosto, conto `1514172196`) di cui si conosce solo lo slippage: +2,10 e +2,84 punti.

---

*Pacchetto preparato il 06/10/2026 dal progetto ORB US100 + Intraday Momentum NAS100 su FTMO. Tutti i trade sono stati ricostruiti da zero dai Report Cronistorici dei quattro conti e dai journal del terminale, con verifica automatica del P&L di ogni trade e del saldo di ogni conto al centesimo; la tabella e le statistiche sono state poi riverificate con un secondo controllo indipendente (verbale §18.19).*
