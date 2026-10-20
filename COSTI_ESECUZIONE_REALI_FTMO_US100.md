# COSTI REALI DI ESECUZIONE — MISURATI DAL VIVO SU FTMO / MetaTrader 5
### Strumento **US100.cash** (NASDAQ 100, spot CFD) · broker **FTMO Global Markets Ltd**, server `FTMO-Demo` · misure raccolte dal **04/08 al 01/10/2026**
### Documento autosufficiente per una chat Claude che deve stimare i costi di una strategia diversa. I numeri misurati sono letti da log ed estratti conto reali; quelli presi dal backtest o stimati sono dichiarati come tali.

> ### COSA TROVI QUI
> I costi di esecuzione **realmente pagati** su `US100.cash` di FTMO, misurati durante un **forward test di 30 sedute** (21/08 → 02/10/2026) di due Expert Advisor su conto demo — uno di **breakout** con stop e take profit sul server, uno di **momentum** con uscite a orario — più tre ingressi dal vivo precedenti (04/08 → 17/08).
> **Campione**: **35 ingressi a mercato** · uscite tracciate su 33 trade (dal 17/08): **19 stop loss server-side del breakout**, **3 stop protettivi del momentum**, **11 uscite a mercato** · **3 notti overnight** · 4 conti demo in sequenza (più un conto precedente per i primi due ingressi), l'ultimo dei quali di tipo **Swing**.
> **Ogni trade del forward è stato riconciliato al centesimo** contro il Report Cronistorico del broker, e i saldi di tutti e quattro i conti tornano al centesimo. La tabella trade per trade è nel file gemello **`ESECUZIONI_REALI_FTMO_US100_TRADE.csv`**: ogni numero di questo documento si può ricalcolare da lì. Dove un dato è derivato e non letto, è detto esplicitamente.
>
> **Se hai fretta, il §7 sono dieci righe.** Se devi usare questi numeri per davvero, leggi prima il **§1** (le trappole di misura) e poi il **§5** (cosa questo campione non può dirti).

> ### NOVITÀ DELLA REV 5 — settimana 28/09 → 02/10/2026 (6 trade, conto 4)
> - **Commissioni ancora 0,00** su tutti e 33 i trade dal 17/08, anche sul nuovo conto **Swing**.
> - **Spread all'apertura USA ancora 1,45** (23 ingressi su 23). Nuovi estremi fuori orario USA: **1,25** (30/09, 13:29 server) e **2,19** (01/10, 15:29 server, nell'ora che precede l'apertura cassa).
> - **Slippage d'ingresso**: settimana sfavorevole (media **+0,89** su 6) con il **peggior caso contrario mai visto, +5,71 punti** — ma sull'intero campione la media è **−0,02 su 35**: resta rumore centrato su zero, con più dispersione (dev. st. 2,22).
> - **Slippage sugli stop del breakout**: 4 stop nuovi, media +0,54% → su 19 stop la media scende a **+1,51%** (+0,59 punti).
> - ⚠️ **Il peggior slittamento sullo stop in punti di tutto il forward: +5,51 punti** (stop protettivo del momentum, 28/09), in un movimento rapido **senza dati macro in calendario**. Sui 22 stop la media in punti sale a **+0,80**.
> - **Latenze d'ingresso più alte** dopo l'aggiornamento del terminale a build 6230: mediana **311 ms** (n=6) contro 232 ms prima.
> - **La deviation è ignorata in entrambe le direzioni**: dopo il fill a −6,50 (a favore) del 10/09, il 28/09 è passato un fill a **+5,71 contro**, oltre la deviation di 5,0, senza requote.
> - Nuovi dati di **margine** (conto Standard: 2,00% del nozionale = 1:50) e **leva** (conto Swing: 1:30), e un primo profilo di costo dell'**oro** (§2.10).
> - **Correzioni** a numeri della rev 4.1: vedi lo storico delle revisioni in fondo.
> - **Rev 5.1** (stesso giorno): doppio controllo indipendente del CSV e di tutte le statistiche, con quattro precisazioni di forma; **nessun valore misurato cambia**.

---

## 0. COME USARE QUESTO DOCUMENTO

Leggi il **§1 prima dei numeri**. Contiene **sei trappole di misura** di MetaTrader 5 e di FTMO: se le ignori, i numeri che ricaverai dal tuo terminale saranno sbagliati in modo *silenzioso* — non otterrai un errore, otterrai valori plausibili e falsi. Noi ci siamo cascati, e la prima ci è costata settimane di slippage loggato a zero mentre lo slippage reale c'era.

Poi il **§4** ti dice come trasformare questi numeri in un costo per trade, e il **§5** ti dice cosa questo campione **non** può dirti.

**Convenzione di segno usata ovunque: `+` = sfavorevole (costo), `−` = favorevole (guadagno).**

**Il file `ESECUZIONI_REALI_FTMO_US100_TRADE.csv`** (separatore `;`, decimali col punto, una riga per trade dal 17/08) contiene per ogni trade: conto e tipo di conto, EA e build, orari server di apertura e chiusura, lotti, distanza di stop progettata, prezzo richiesto, fill, slippage d'ingresso, spread all'ingresso (dove loggato), stop e target dell'ordine e della posizione, tipo e prezzo d'uscita, slippage sull'uscita a livello (in punti e in % della distanza), P&L, swap, commissioni, R, tempi d'esecuzione dell'ingresso, della modifica e dell'uscita a mercato. Il prezzo richiesto dei trade riancorati è **derivato** (stop dell'ordine ± distanza); `R` = P&L ÷ (lotti × distanza progettata), con 1R = lotti × distanza anche per il momentum (il suo stop protettivo sta a −2R). Ai 33 trade del CSV si aggiungono, nelle statistiche d'ingresso, due ingressi pre-forward (agosto, conto `1514172196`) di cui conosciamo solo lo slippage. *Nel CSV `R` e le percentuali sono arrotondati a 4 e 2 decimali, mentre le statistiche di questo documento sono calcolate a precisione piena: ricalcolando una media dal CSV si può trovare una differenza di 1 sull'ultima cifra (per esempio −1,0182 invece di −1,0181 sui 15 stop riancorati).*

---

## 1. LE SEI TRAPPOLE DI MISURA — leggere prima dei numeri

### 1.1 `CTrade::ResultPrice()` su FTMO restituisce il prezzo **RICHIESTO**, non quello **ESEGUITO**
Verificato il 04/08/2026 e riverificato decine di volte. Conseguenza diretta: **qualunque EA che calcoli lo slippage come `ResultPrice() − prezzo_richiesto` loggherà sempre 0,00**, su ogni trade, per sempre. Il nostro EA lo ha fatto per settimane e riportava slippage nullo mentre lo slippage reale c'era.

**Come si misura davvero lo slippage.** Due strade, entrambe valide:
- da dentro l'EA: leggere **`POSITION_PRICE_OPEN`** dopo l'apertura (non `ResultPrice()`), oppure `HistoryDealSelect(ResultDeal())` → `DEAL_PRICE`;
- a posteriori: incrociare il log dell'EA con il **Report Cronistorico dei Trade** (menu *Visualizza → Cronologia*, tasto destro → *Report*), che riporta i prezzi realmente eseguiti.

**Corollario operativo.** Un EA che legge `POSITION_PRICE_OPEN` logga il fill vero: le nostre build attuali lo fanno, e **dal 21/09 13 fill su 13 del log coincidono con la cronistoria** (al centesimo per il breakout; il momentum li stampa con un decimale). Ma la cronistoria resta indispensabile: lo **slippage** non è ricostruibile dal solo log se l'EA non stampa anche il prezzo del *primo* tentativo (trappola 1.6), e **swap e commissioni** stanno solo lì.

### 1.2 Una seconda condizione di gara: dopo `OrderSend` la posizione può non essere ancora in cache
Subito dopo l'invio, `PositionSelect`/`PositionGetDouble` possono restituire `false` perché la posizione non è ancora comparsa nella cache locale del terminale. Un EA che legge il prezzo eseguito in quel momento **ricade silenziosamente sul valore sbagliato** (trappola 1.1) e salta ogni logica basata sul fill.
**Soluzione adottata e validata dal vivo**: attesa attiva con `Sleep(50)` fino a 1 secondo finché la posizione non è leggibile. **Riancoraggio riuscito 27 volte su 27** (verificato confrontando i livelli dell'*ordine* con quelli della *posizione* nella cronistoria; gli ingressi delle build attuali sono 28, ma nel 28° — momentum, 04/09 — lo slippage era zero e non c'era nulla da spostare). L'attesa è servita **almeno 6 volte** — 4 fino al 18/09, e **2 sui 4 ingressi del breakout della settimana 28/09-01/10** — e la posizione è comparsa in **57-66 ms**. Durante l'attesa **la posizione non è mai scoperta**: stop e take profit viaggiano allegati all'ordine a mercato e sono già sul server dal primo millisecondo.

### 1.3 Il tester di MetaTrader 5 **non modella lo slippage degli ordini a mercato** — ma l'attraversamento degli stop sì
Con Ritardi = *"Latenza zero, esecuzione ideale"* (l'unica impostazione che rende il tester deterministico e quindi confrontabile) lo slippage degli **ordini a mercato** è **0,00 su tutti gli ordini** — verificato su 39 ordini in una nostra acceptance. Il tester modella lo **spread** (se usi tick reali).
**Sulle uscite a livello è diverso**: con i tick reali il tester esegue stop e target al tick che attraversa il livello, quindi l'attraversamento è **già dentro**. Nel nostro backtest gli stop valgono in media **−1,0225 R** (+2,25% oltre il livello), e dal vivo, sui 15 stop con riancoraggio, abbiamo misurato **−1,0181 R**.
→ **Va aggiunto a mano lo slippage degli ordini a mercato** (ingressi e chiusure a orario: media ≈0, ma con la sua varianza), e **quello a livello solo se il backtest esegue gli stop esattamente al livello**. Il controllo è al §4.4: guarda la perdita media degli stop in R.

### 1.4 Errori di segno da non ripetere
Ricostruendo il prezzo richiesto dallo stop allegato all'ordine, la formula corretta è
`prezzo_richiesto = SL_ordine + side × dist` con `side = +1` per long e `−1` per short.
Usando `−` invece di `+` si ottengono slippage assurdi (nel nostro caso −78 punti). Ci siamo cascati.
**Seconda insidia**: il nostro EA di momentum logga `delta = fill − prezzo richiesto` **senza correggere per la direzione**. Su uno short un delta **negativo** è **sfavorevole** (hai venduto più in basso): il 28/09 il log stampava `delta −0,81` su uno short, cioè **+0,81 sfavorevole**. Converti sempre alla convenzione `+ = sfavorevole` prima di fare medie.

### 1.5 `PositionModify` con TP = 0.0 **cancella** il take profit
Ogni chiamata di modifica deve ripassare il TP corrente, anche se non lo si sta cambiando.

### 1.6 Lo slippage loggato è misurato contro l'**ultimo tentativo**, non contro il segnale
Se l'ordine fallisce e l'EA ritenta ricalcolando prezzo, stop e target a ogni tick (come fa il nostro EA di breakout), lo slippage stampato al momento del fill misura **solo l'ultimo salto**. Il costo vero rispetto al segnale include tutto l'**inseguimento**, e il log non lo vede.
Nel nostro campione **tutti i 35 ingressi sono riusciti al primo tentativo**, quindi le due misure coincidono. Ma il 25/09, con il conto disabilitato, l'EA ha ritentato per cinque minuti spostando il prezzo di riferimento **fino a ~+28 punti (~+0,6 R)** dal segnale: se l'ordine fosse passato a metà, il log avrebbe mostrato uno slippage vicino a zero.
**Rimedio**: loggare il prezzo del primo tentativo e mettere un tetto all'inseguimento (vedi anche §2.9).

---

## 2. I NUMERI — quello che abbiamo effettivamente misurato

**Campione**: **35 ingressi a mercato eseguiti** (25 dalla strategia di breakout, 10 da quella di momentum), 04/08 → 01/10/2026. Uscite tracciate sui 33 trade dal 17/08: **19 stop loss server-side** (breakout), **3 stop protettivi** (momentum), **11 uscite a mercato** (5 chiusure programmate di fine giornata, 3 uscite su segnale a orario, 1 chiusura dopo riavvio, 2 chiusure alla riapertura notturna), **3 notti overnight**. Forward: **30 sedute, 21/08 → 02/10/2026**.
*In due sedute non è stato eseguito nessun ordine, per cause che non riguardano l'esecuzione: il 25/09 il conto era stato disabilitato da FTMO dopo il raggiungimento degli obiettivi del Free Trial; il 02/10 il terminale è rimasto spento per tutta la seduta. Non fanno parte del campione dei costi.*

### 2.1 Commissioni — **ZERO su US100.cash**

> **0,00 $ su tutti i 33 trade dal 17/08.** Nessuna commissione di apertura, nessuna di chiusura — anche sul conto **Swing** aperto il 28/09 (6 trade).

Non è un arrotondamento: il report cronistorico riporta letteralmente `0.0` nella colonna Commissioni per ogni singolo affare. **Su US100.cash di FTMO il costo è interamente nello spread.** Se stai modellando una strategia su questo strumento e questo broker, la voce commissioni va messa a zero, non stimata.

> ⚠️ **È una proprietà del simbolo, non del broker.** Sullo stesso conto, alcune operazioni manuali di prova hanno pagato: **EURUSD e USDJPY 2,50 $ per lotto per lato** (5,00 $ a round-trip; misurato su 1 e 0,1 lotti) e **XAUUSD 0,03 $ per 0,01 lotti per lato** (≈3 $ per lotto per lato; confermato dal calcolo automatico di un nostro EA sull'oro: **6 affari, 0,06 lotti, −0,18 $ → −3,00 $ per lotto per lato**). **Su un altro simbolo non usare lo zero.** Per l'oro c'è un profilo di costo più completo al §2.10.

### 2.2 ⚠️ Swap — piccolo, e **di segno non prevedibile**

| Notte (rollover) | Direzione | Lotti | Swap | $ per lotto per notte |
|---|---|---|---|---|
| 24→25/08 (lun→mar) | short | 4,48 | +1,24 | **+0,28** · a credito |
| 15→16/09 (mar→mer) | short | 5,45 | −0,37 | **−0,07** · a debito |
| 23→24/09 (mer→gio) | short | 13,86 | +1,76 | **+0,127** · a credito |
| 23→24/09 (mer→gio) | short | 6,79 | +0,86 | **+0,127** · a credito |

> **Stesso strumento, stessa direzione: due notti a credito, una a debito.** Nella stessa notte due posizioni diverse hanno avuto **lo stesso tasso per lotto** (+0,127, entro l'arrotondamento al centesimo): lo swap è proporzionale ai lotti e coerente dentro la notte, ma **cambia da una notte all'altra, anche di segno**.

In valore assoluto è **trascurabile** (≤ 0,28 $ per lotto per notte: su 13,86 lotti fa 1,76 $). Se la tua strategia è intraday non ti interessa. Se tieni posizioni overnight, **non dedurre il segno dalla direzione**: leggi i valori correnti nella *Specifica* del simbolo in MT5 (swap long/short e giorno del triplo).
*Da verificare*: se per questo simbolo il **mercoledì** è il giorno dello swap triplo, la notte del 23/09 vale +0,042 $ per lotto a notte singola. Nessuna misura su posizioni long, su nottate multiple o sul weekend. *Nella settimana 28/09-01/10 nessuna posizione è rimasta aperta di notte: nessun dato nuovo.*

### 2.3 Spread — l'unico costo vero, e dipende dall'ora

| Momento (ora server) | Spread (punti indice) | Fonte |
|---|---|---|
| **16:35** *(5 minuti dopo l'apertura cassa USA)* | **1,45** su **23 ingressi su 23** | misurato dal vivo, 17/08 → 01/10 |
| Orario USA dopo l'apertura (17:00 → 22:30) | **1,45 in tutte le letture dal vivo** (fra cui 5 nella settimana 28/09-05/10, alle 17:48, 18:25, 18:51, 19:24, 19:40) · **storico 2021-26: mediana 0,80, p95 1,45** | dal vivo: istantanee al riavvio degli EA · storico: tick FTMO |
| Mattina e primo pomeriggio europeo (10:50 → 15:15) | **1,25 – 1,95** | dal vivo: fino al 18/09 1,95 · 1,95 · 1,85 · 1,75 ×3 · 1,55 · 1,45 ×6; 21-24/09 1,85-1,95 fra le 12:04 e le 14:14, 1,45 alle 11:21 e alle 15:13; 28/09-06/10 1,65 · 1,85 · 1,45 ×4 · **1,25** (30/09 13:29) · 1,95 · 1,65 |
| **Ora che precede l'apertura cassa** (15:29 → 16:11) | **1,95 – 2,19** | dal vivo, 3 letture: 2,19 (01/10 15:29), 1,95 (02/10 15:33, tre minuti dopo i Non-Farm Payrolls), 1,95 (30/09 16:11) |
| Ultima ora di quotazione (dopo la chiusura cassa) | **1,53** | dal vivo, 29/09 alle 23:12 |

**Profilo storico alle 16:35 server, verificato cifra per cifra sui tick FTMO 2021-2026**: mediana **1,00** · media **1,02** · massimo **1,79** · **zero osservazioni sopra 2,0**.

> ⚠️ **Lo spread si è allargato nel tempo, e di parecchio.** Mediana per anno alle 16:35 server:
> **2021: 0,60 · 2022: 0,60 · 2023: 1,00 · 2024: 1,10 · 2025: 1,20 · 2026: 1,45**
> Lo spread di oggi è **1,4 volte la media storica** (1,02) e **2,4 volte quello del 2021**: un backtest pluriennale che usa lo spread medio sottostima il costo attuale di circa il **30%**, uno tarato sul 2021 di circa il **60%**. Usa 1,45 per il presente, non 1,02.

> ⚠️ **Anche in orario USA usa 1,45, non lo 0,80 storico.** La mediana 0,80 dei confini semi-orari 17:00-22:30 è calcolata su 2021-2026, cioè in gran parte su anni con spread molto più stretti; tutte le letture dal vivo in orario USA danno 1,45. Sono istantanee prese al riavvio degli EA, non una misura continua — ma nessuna è sotto 1,45. *[STIMA prudente per una strategia che entra fra le 17:00 e le 22:30]*

**Tre avvertenze pratiche:**
- **Lo spread si paga UNA volta per round-trip.** Rispetto a un grafico bid, un long lo paga all'ingresso (compra all'ask), uno short all'uscita (ricompra all'ask). Non sommarlo due volte (vedi §4.2).
- **L'ora prima dell'apertura cassa è la più cara** (fino a 2,19): è anche l'ora dei dati macro delle 8:30 di New York (15:30 server). Una strategia che entra fra le 15:30 e le 16:30 server paga dal 35 al 50% di spread in più di una che entra alle 16:35 (3 letture: è un'indicazione, non una stima).
- A mercato chiuso (notte, weekend) il terminale mostra **1,53**: è l'ultima quotazione congelata — e coincide con lo spread dell'ultima ora di quotazione (29/09, 23:12 server: 1,53 a mercato aperto). **Non è uno spread negoziabile nella pausa.** Non usarla come stima dello spread durante la sessione.

### 2.4 Slippage d'ingresso (ordine a mercato) — **centrato su zero**

Serie completa, **n = 35**, in punti indice (`+` = sfavorevole):

```
pre-forward 04/08 → 17/08 :  +2,10  +2,84  −0,50
breakout 21/08 → 17/09    :  +3,80  +0,30  −0,50  −4,60  −0,70  −0,30  +0,30  +3,81
                             −0,19  +0,40  +0,50  −1,20  −6,50  −1,49  +0,01
momentum 24/08 → 16/09    :  +1,25   0,00  −1,70  −1,75
settimana 21 → 24/09      :  breakout +0,70  −0,99  −1,30  ·  momentum −0,40  +0,20  −0,50  +0,50
settimana 28/09 → 01/10   :  breakout +5,71  +0,80  −1,70  −2,20  ·  momentum +0,81  +1,90
```

| | **Tutti (n=35)** | Breakout (n=25) | Momentum (n=10) |
|---|---|---|---|
| Media | **−0,02 punti** | −0,04 | +0,03 |
| Mediana | 0,00 | −0,19 | +0,10 |
| Deviazione standard | **2,22 punti** | 2,54 | 1,18 |
| Range | −6,50 … +5,71 | −6,50 … +5,71 | −1,75 … +1,90 |
| Sfavorevoli / favorevoli / nulli | **17 / 17 / 1** | 12 / 13 / 0 | 5 / 4 / 1 |
| IC95% della media | **[−0,78 ; +0,74]** → **indistinguibile da zero** | [−1,08 ; +1,01] | [−0,81 ; +0,87] |
| p10 / p25 / p75 / p90 | −1,73 / −1,09 / +0,75 / +2,54 | | |

*Come si è mosso il campione: fino al 24/09 (n=29) media −0,20, dev. st. 2,07; settimana 28/09-01/10 (n=6) media +0,89, dev. st. 2,85.*

> **Conclusione: sull'ingresso a mercato lo slippage è RUMORE, non un costo.** Con 35 osservazioni la media è **−0,02 punti** (−0,006 R sui 33 trade con distanza nota), con perfetto equilibrio fra casi sfavorevoli e favorevoli (17 a 17), e l'intervallo di confidenza contiene abbondantemente lo zero. Quello che aggiunge è **dispersione**: ±2,22 punti di deviazione standard su uno stop medio di 40,5 punti. Senza correzioni, nei casi estremi osservati il rischio effettivo per trade sarebbe andato da **0,81× a 1,13×** di quello deciso (circa ±6% a una deviazione standard sul breakout).
>
> **Implicazione pratica per la tua strategia**: se dimensioni la posizione su una distanza fissa e piazzi lo stop *prima* di conoscere il prezzo eseguito, non stai rischiando quello che credi. La correzione è **riancorare stop e target al prezzo realmente eseguito** subito dopo il fill. Non serve a guadagnare — metà delle volte fa risparmiare e metà costa — **serve a togliere varianza dal rischio**.

**La settimana 28/09-01/10 è stata la più sfavorevole**, e contiene il **peggior caso contrario mai visto: +5,71 punti** (28/09, breakout, 11,04 lotti, = +0,126 R). È arrivato con il **tempo d'esecuzione più lento di tutti gli ingressi del breakout (420 ms)**, sul **primo ordine del conto nuovo** e il giorno dell'aggiornamento automatico del terminale. Un caso solo non dimostra un legame fra latenza e slippage (il più lento in assoluto, 825 ms del 23/09, aveva +0,50) — ma è il motivo per cui la deviazione standard è salita da 2,07 a 2,22. **Il riancoraggio ha riportato il rischio esattamente al valore deciso.**

### 2.5 Slippage sulle uscite **a livello** (stop loss sul server) — **1,51% della distanza, ≈0,6-0,8 punti**

n = 19 stop loss della strategia di breakout, espresso in % della distanza entry→stop:

```
fino al 17/09 :  +0,56   0,00  −1,21  +2,17  +1,03  +4,02  +1,18  +1,74
                 +1,62  +1,86  +2,92  +1,95  +2,07  −0,16  +6,85
28/09 → 01/10 :  +1,30  +1,15  −1,65  +1,35
```
*(nessuno stop nella settimana 21-24/09)*

| | |
|---|---|
| Media | **+1,51% della distanza** *(era +1,77% su 15)* |
| Mediana | +1,35% |
| Deviazione standard | 1,85 punti percentuali |
| Range | **−1,65%** … **+6,85%** |
| Sfavorevoli | **15 su 19** (3 favorevoli, 1 esattamente al livello) |
| IC95% della media | **[0,62% ; 2,41%]** |
| In punti indice | media **+0,59 pt**, mediana +0,62, IC95% [+0,24 ; +0,94], p90 +1,25 · su distanze da 36 a 59 pt |

**Stop protettivo della strategia di momentum** (n = 3, distanze entry→stop molto più ampie):

| Data | Slittamento | Distanza entry→stop | % |
|---|---|---|---|
| 24/08 | +0,40 pt | 224,45 | +0,18% |
| 04/09 | +0,44 pt | 60,32 | +0,73% |
| ⚠️ **28/09** | **+5,51 pt** | 89,65 | **+6,15%** |

> ### ⚠️ Il 28/09: il peggior slittamento in punti di tutto il forward
> Lo stop protettivo di uno short da 11,15 lotti (livello 30.356,87) è stato eseguito a **30.362,38: +5,51 punti** (−1.061,03 $ invece di ~−999,60 $ al livello: **61 $ di attraversamento**). Era un **movimento rapido**: il prezzo è salito di ~80 punti in meno di tre minuti, e lo stop del breakout, più in alto, è stato colpito 2'41" dopo con +0,59. **Nel calendario economico MQL5 non c'era nessun dato USD di rilievo** in quella finestra (19:24 server = 12:24 di New York; l'evento più vicino era il discorso di un governatore Fed, importanza media, un'ora dopo).
> **Due lezioni.** (1) **Ragiona in punti, non in percentuale**: lo stesso +5,51 vale +6,15% di uno stop da 90 punti, ma sarebbe il **37%** di uno stop da 15. (2) **La coda non arriva solo con le notizie**: anche un filtro news perfetto non l'avrebbe evitata.

**Tutti gli stop insieme (22, breakout + momentum), in punti**: media **+0,80**, mediana +0,61, p90 +1,52, **peggiore +5,51**; 18 sfavorevoli, 3 favorevoli, 1 al livello. **Per una strategia con stop di ampiezza diversa usa ≈0,8 punti come valore medio** (0,6 se ti fidi della mediana) e tieni presente che **un caso su ~20 arriva a 5-6 punti**.

**Take profit sul server**: **nessuna misura**. Dal vivo ne è stato colpito uno solo, il 04/08, fuori dal campione delle uscite tracciate: eseguito dal server a terminale spento, senza rilevare lo slippage. Nel backtest su tick reali i 72 target da 8R sono stati eseguiti al livello o meglio (media +8,019 R, mai peggio).

> **A differenza dell'ingresso, qui lo slippage è sistematico: 15 casi su 19 sfavorevoli** (18 su 22 contando il momentum). È atteso: uno stop sul server si attiva quando il prezzo *attraversa* il livello, quindi l'esecuzione è quasi sempre oltre.

> ### La coda si è campionata in parte, e il modello regge
> Sul breakout il caso peggiore resta il **17/09: +6,85% oltre il livello** (2,58 punti su 37,68). Il modello storico prevede il **9,4%** dei casi oltre il 5% della distanza: con **1 caso su 19 = 5,3%** siamo dentro la previsione, anzi un po' sotto.
> **Conseguenza pratica per te**: la media dell'1,5% descrive l'esecuzione *ordinaria*; **circa un caso su dieci costa 3-4 volte tanto**, e il modello storico contempla anche **3 casi su 778 oltre il 20%**, che restano non campionati. Se la tua analisi dipende dallo scenario peggiore, usa la coda del modello, non la media di questo campione.
> La distribuzione ha **entrambe le code**: tre stop sono stati eseguiti **meglio** del livello (−0,16% il 15/09, −1,21% il 24/08 e **−1,65% il 30/09**, il più favorevole).

### 2.6 Uscite **a mercato** — non subiscono slippage di attraversamento

**Undici osservazioni, di quattro tipi:**

| Tipo di uscita a mercato | n | Tempo di esecuzione |
|---|---|---|
| **Chiusura programmata di fine giornata** (22:55 server) | 5 | 195 · 214 · 215 · 220 · 229 ms |
| **Uscita su segnale a orario** *(il prezzo è rientrato nella banda al check semi-orario)* | 3 | 199 · 213 · 250 ms |
| **Chiusura dopo un riavvio** *(posizione rimasta aperta dal giorno prima)* | 1 | 204 ms |
| **Chiusura alla riapertura notturna** *(01:05 server, dopo la pausa di quotazione)* | 2 | **1.296 ms** (primo ordine dopo la pausa) · 189 ms (8 secondi dopo) |

Nessuna di queste attraversa un "livello", quindi **nessuna paga lo slippage del §2.5**: il costo è lo spread (una volta per round-trip, §2.3) più uno slippage di esecuzione che non possiamo misurare direttamente sulle chiusure, ma che ci aspettiamo simile a quello d'ingresso — rumore centrato su zero. **10 su 11 eseguite fra 189 e 250 ms**, fino a 16,6 lotti. L'unica eccezione è il **primo ordine inviato alla riapertura delle 01:05 server**: accettato dopo 1,1 s, eseguito in 1,3 s.

> ### ⭐ IL PUNTO PIÙ IMPORTANTE DI TUTTO IL DOCUMENTO
> **Lo slippage di attraversamento colpisce SOLO le uscite a livello** (stop loss e take profit sul server). **Le uscite a mercato — chiusure temporali, uscite su segnale, trailing gestito dall'EA — non lo pagano affatto.**
>
> Quindi **il costo di esecuzione di una strategia dipende dal suo MIX DI USCITE**, non dal broker. Due nostre strategie sullo stesso strumento, stesso broker, stesso periodo:
> - strategia A (breakout): **87,7%** delle uscite a livello nel backtest, di cui **80,3% allo stop** (il 7,4% al target, nel tester, è eseguito al livello o meglio) → paga quasi sempre
> - strategia B (momentum): **15,6%** delle uscite a livello → paga quasi mai
>
> **Prima di applicare lo slippage sugli stop alla tua strategia, conta che frazione delle sue uscite è a livello — e contala sul backtest, non su un periodo breve.** Dal vivo le due ultime settimane lo mostrano in modo quasi didattico: **21-24/09, 0 uscite a livello su 7; 28/09-01/10, 5 su 6.** Dal 17/08 le uscite a livello sono **19 su 23** per A (82,6%) e **3 su 10** per B (30%).

### 2.7 Qualità di esecuzione

| Grandezza | Valore |
|---|---|
| Tempo di esecuzione, ingressi a mercato (**n=33**, tutti quelli dal 17/08, letti dal journal) | mediana **236 ms**; 31 su 33 fra 195 e 364 ms; **due valori alti**: 420 ms (28/09, breakout, con lo slippage di +5,71) e 825 ms (23/09, momentum, con +0,50). **Fino al 24/09 mediana 232 ms (n=27); settimana 28/09-01/10 mediana 311 ms (n=6)**, dopo l'aggiornamento del terminale a build 6230 |
| Tempo di esecuzione, uscite a mercato (n=11) | mediana **214 ms**; 10 su 11 fra 189 e 250 ms; **1.296 ms** sul primo ordine alla riapertura delle 01:05 |
| Tempo di esecuzione, `PositionModify` (n=28) | mediana **100 ms**, range 50 – 315 |
| Ping al server FTMO-Demo | **29 – 76 ms** (PC domestico, Italia, Wi-Fi; letture sparse del journal; settimana 28/09-02/10: 38,5 – 66,9) |
| Ping via VPS MetaTrader (Londra LD4/LD6) | **1,3 – 1,8 ms** *(offerto dal terminale, non usato; 1,44 e 1,61 ms il 28-29/09)* |
| Build del terminale | **6090 → 6140 → 6182 → 6230**: tre aggiornamenti automatici fra il 20/08 e il 28/09 (l'ultimo il 28/09 alle 12:21 server, prima della seduta) |
| Rifiuti **sul prezzo** (requote, off quotes, price changed) | **0** su 35 ingressi, 11 uscite a mercato e tutte le modifiche |
| Rifiuti **amministrativi** | ~65 `[Market closed]` (24/09) e ~3.000 `[Trade disabled]` (25/09) — vedi §2.9. **Nessuno dal 28/09** |
| Deviation impostata | 5,0 punti indice. **Mai intervenuta, in nessuna delle due direzioni**: è passato senza requote sia un fill a **−6,50** (a favore, 10/09) sia uno a **+5,71** (contro, 28/09), entrambi oltre la deviation. È l'esecuzione di tipo *Market*, in cui la deviation è ignorata. **Non contarci come protezione** |

### 2.8 ⚠️ Esposizione overnight — tre osservazioni

Tre volte una posizione è rimasta aperta attraverso la notte, sempre **short**, sempre per un **PC spento** prima della chiusura di fine giornata:

| | 24/08 | 15/09 | 23/09 |
|---|---|---|---|
| Posizioni | momentum 4,48 lotti | momentum 5,45 lotti | breakout 13,86 + momentum 6,79 lotti |
| Durata | 15h 57' | ~17h 30' | 8h 30' e 8h 05' |
| Come si è chiusa | **stop protettivo sul server**, la mattina dopo | **a mercato**, dall'EA alla riaccensione | **a mercato, alla riapertura delle 01:05 server**, dagli EA (terminale riacceso alle 01:01) |
| Risultato | **−2,01 R** | **−1,31 R** | **+3,10 R** e **+0,74 R** |
| Lo stop è stato toccato? | sì | no | no |

**Lezioni utili anche a chi non usa i nostri EA:**
1. **Gli stop e i target sul server vengono eseguiti a terminale spento.** Verificato più volte. Quello che il terminale spento ti toglie non è la protezione a livello: è **tutto ciò che è a orario** (chiusure programmate) e **tutto ciò che è a segnale**. Esempio del 28/09: il terminale è rimasto spento 41 minuti con due posizioni aperte, e il check semi-orario delle 19:00 dell'EA di momentum è caduto nel buco; 24 minuti dopo la sua posizione è stata chiusa **dallo stop**, con lo slittamento di +5,51 punti del §2.5. Se a quel check il prezzo era rientrato nella banda, l'EA sarebbe uscito a mercato senza attraversamento — non lo sappiamo (servono le barre M1).
2. **Nessuna chiusura overnight ha pagato costi di esecuzione anomali.** L'unica differenza misurabile è la **latenza del primo ordine alla riapertura**: 1,3 s contro i ~200 ms abituali.
3. **Durante la pausa gli ordini vengono rifiutati** (`[Market closed]`): il 24/09 l'EA di momentum ha inviato ~65 richieste di chiusura fra le 01:01:54 e le 01:04:57 server, tutte respinte. Vedi §2.9.
4. ⚠️ **La finestra senza quotazioni (23:49 → 01:05 server) è stata attraversata in tutte e tre le notti.** La riapertura delle 01:05 è stata vista dal vivo solo il 24/09, senza gap rilevante; nelle altre due notti il gap non è misurato, ma non ha fatto scattare lo stop. Resta il rischio che questi numeri non coprono: con 20,65 lotti short aperti, un gap di circa **+1,1%** alla riapertura avrebbe consumato **da solo** l'intero limite di perdita giornaliera FTMO (5.000 $). *È rischio di prezzo, non costo di esecuzione.*

*Nella settimana 28/09-01/10 nessuna posizione è rimasta aperta di notte.*

### 2.9 ⚠️ Rifiuti amministrativi e limite FTMO sulle richieste

Nessun ordine è mai stato rifiutato **per il prezzo**. Ma due volte il server ha rifiutato **in serie**:

| Quando | EA | Rifiuto | Richieste | Perché così tante |
|---|---|---|---|---|
| 24/09, 01:01:54 → 01:04:57 server | momentum, chiusura | `[Market closed]` (10018) | ~65 | raffiche di 5 tentativi ogni 15 s, finché la posizione del giorno prima non è chiusa |
| 25/09, 16:35 → 16:40 server | breakout, ingresso | `[Trade disabled]` (10017) | **~3.000** *(stima: un tentativo ogni 60-130 ms per 5 minuti)* | ritenta **a ogni tick** per tutta la finestra d'ingresso, senza leggere il codice d'errore |

**Perché conta**: FTMO classifica come pratica vietata gli EA che causano **più di 2.000 richieste al server al giorno** (iperattività), con conseguenze fino all'esclusione dalla valutazione. Se il server conta queste richieste — il journal le registra una per una — il secondo schema supererebbe il limite in circa **tre minuti**; il primo, con il terminale acceso per un weekend intero e una posizione rimasta aperta, in meno di **due ore**. Il 25/09 il conto era già disabilitato e non ci sono state conseguenze, ma **su un conto a pagamento sarebbe un rischio vero**.
**Rimedio**: classificare i codici di ritorno (10017, 10018, 10026, 10027 non vanno ritentati), controllare prima dell'invio che conto, terminale e simbolo consentano il trading (`ACCOUNT_TRADE_ALLOWED`, `TERMINAL_TRADE_ALLOWED`, `SYMBOL_TRADE_MODE`, orari di `SymbolInfoSessionTrade`) e mettere un tetto ai tentativi.
*Nella settimana 28/09-02/10: nessun rifiuto di alcun tipo.*

### 2.10 Altri simboli sullo stesso server — **oro (XAUUSD)**: primo profilo di costo

Sullo stesso terminale gira dal 23/09 un nostro EA sull'oro **in dry run** (osserva e non opera). A ogni avvio stampa un rapporto con i dati del simbolo letti dal server: sono **istantanee**, non una misura continua, ma sono le uniche che abbiamo. *Lo slippage sull'oro non è misurato: nessun ordine reale, tranne tre manuali da 0,01 lotti.*

| Voce | Valore | Fonte |
|---|---|---|
| **Commissioni** | **3,00 $ per lotto per lato** (6,00 $ a round-trip) | [MISURATO] 6 affari da 0,01 lotti |
| **Spread** in orario di contrattazione | **0,35 – 0,51 $ per oncia**, mediana **0,405**, media 0,40 · 20 istantanee fra il 28/09 e il 06/10, dalle 10:24 alle 23:12 server · massimo 0,51 (01/10, 15:29 server, l'ora prima dell'apertura cassa USA) | [MISURATO] istantanee |
| Spread a mercato chiuso (weekend) | 0,43 — quotazione congelata, non negoziabile | [MISURATO] |
| **Costo round-trip stimato per lotto** | spread 0,40 × 100 once = **40 $** + commissioni **6 $** = **≈46 $ per lotto** (≈0,46 $ per oncia) | [STIMA] |
| **Swap** (dalla *Specifica*, modalità 1 = in punti) | **long da −64,90 a −90,35**, **short da −4,20 a −8,30** punti per lotto per notte → **≈ da −65 a −90 $ (long) e da −4 a −8 $ (short) per lotto per notte**, perché 1 punto = 0,01 $ × 100 once = 1 $. **A debito in entrambe le direzioni**, e **cambia quasi ogni giorno** (aggiornamento nel pomeriggio: −83,00 il 28/09 → −90,35 il 29/09 → −87,51 il 30/09 → −72,64 il 01/10 → −65,63 il 02/10 → −64,90 il 05/10, sui long) | [SPECIFICA DEL SIMBOLO] · conversione in $ = [STIMA], **nessuna posizione overnight reale** |
| Specifica | contract size 100 · tick 0,01 = **1,00 $ per lotto** · 1,00 di prezzo = **100 $ per lotto** · volume 0,01 – 100, passo 0,01 · stops level 0 · freeze level 0 · filling FOK e IOC | [MISURATO] |
| Volatilità di riferimento | ATR(14) su M15 fra **5,45 e 11,0 $** nelle istantanee (18,5 $ alle 18:51 server del 02/10, giorno dei Non-Farm Payrolls) → lo spread è il **4-7%** di un ATR M15 | [MISURATO] istantanee |
| Simbolo del dollaro | **`DXY.cash`** disponibile su FTMO, con storico M1 (~580.000 barre) | [MISURATO] |

> **Per una strategia sull'oro**: le commissioni **non sono zero** (al contrario di US100.cash), lo swap è **forte e a debito anche sugli short** (su un long tenuto la notte costa più dell'intero round-trip, spread più commissioni, ≈46 $ per lotto), e lo slippage va **misurato da capo** con le tecniche del §1.

---

## 3. PARAMETRI DELLO STRUMENTO — per convertire punti in dollari

| | |
|---|---|
| Simbolo | `US100.cash` (NASDAQ 100 Index, Spot CFD) |
| Digits | **2** · Point **0,01** → **1 punto indice = 100 punti simbolo** |
| Valore del punto | **1,00 $ per punto indice per lotto** |
| Tick value | 0,01 |
| Lotto minimo | 0,01 · lotti fino a **70** accettati senza problemi |
| **Margine** | **conto Standard (leva di conto 1:100): 2,00% del nozionale al prezzo d'apertura = leva effettiva 1:50** — misurato il 24/09: 16,60 lotti × 30.246,08 → **10.041,70 $** esatti. **Conto Swing (leva di conto 1:30): margine sugli indici non misurato.** Con le nostre taglie (fino a ~22 lotti aperti insieme) il margine non è mai stato vincolante |
| Modalità conto | hedging |
| Orario di quotazione | **01:05 → 23:49 ora server** in 1.200 giorni su 1.260. **Riapertura delle 01:05 confermata dal vivo** il 24/09: richieste rifiutate fino alle 01:04:57, primo fill alle 01:05:01 |
| **Finestra senza quotazioni** | **76 minuti** — 23:49 → 01:05. Stop e target sul server restano validi, ma un gap in quella finestra li attraversa |
| Mezze sedute | **34 giorni** chiudono alle 19:59 ora server (vigilie: 24/12, 3/7, giorno dopo il Ringraziamento) |

**Formula**: `P&L in $ = lotti × (prezzo_uscita − prezzo_ingresso) × side`, con i prezzi in punti indice. Nessun moltiplicatore, nessuna conversione valuta (conto in USD). *Verificata al centesimo su tutti i 33 trade del CSV.*

**Fuso del server**: **New York + 7 ore**, e **segue l'ora legale americana** (non è EET fisso). Conseguenza: l'apertura della cassa USA cade alle **16:30 ora server tutto l'anno**, incluse le settimane di disallineamento DST fra Europa e USA. Verificato sui profili di volume: 89 giorni su 89 delle settimane di disallineamento sui dati FTMO 2021-2026, e le settimane di disallineamento del 2024-25 sui dati di un altro broker (Pepperstone) con la stessa struttura. Il calendario economico MQL5 del terminale data gli eventi nello stesso orario (Non-Farm Payrolls alle 15:30 server, ISM alle 17:00).

---

## 4. COME TRASFORMARE QUESTO IN UN COSTO PER TRADE

### 4.1 L'invariante utile

> **costo in R = slippage ÷ distanza dello stop**

Il costo **in multipli di rischio è indipendente dalla taglia della posizione**: raddoppiando i lotti raddoppiano sia la perdita che il rischio nominale. Questo significa che puoi stimare il costo una volta sola, in R, e usarlo a qualunque dimensionamento.

### 4.2 Costi lordi, con i nostri numeri e una distanza di stop di 40,47 punti *(media dei 19 trade della strategia di breakout con riancoraggio, 26/08 → 01/10; era 38,86 sui primi 15)*

| Voce | Punti indice | In R | Quando si paga |
|---|---|---|---|
| Spread (**una volta** per round-trip) | 1,45 | **0,0358 R** | sempre |
| Slippage d'ingresso | −0,02 *(rumore)* | **≈ 0,000 R** | mai, in media |
| Slippage sull'uscita **a livello**, valore medio | +0,59 *(breakout)* · ≈0,8 *(tutti i 22 stop)* | **0,0146 R** *(0,020 R con 0,8)* | **solo** sulle uscite a livello |
| Slippage sull'uscita a livello, **coda** | osservati **+2,58** (breakout, +6,85%) e **+5,51** (momentum) · nel backtest p99 16,8%, peggiore 63% | sulla distanza di riferimento **0,064 R** e **0,136 R**; nel backtest di solito **0,05-0,17 R**, oltre 0,20 R in 3 casi su 778 (massimo **0,63 R**) | ~1 caso su 10 |
| Uscita **a mercato** | nessun attraversamento | **≈ 0 R** oltre allo spread già contato | sulle uscite a mercato |
| Commissioni | 0,00 | **0** | mai (solo su US100.cash, §2.1) |
| Swap | ≤ 0,28 $/lotto/notte, **segno non prevedibile** | — | solo overnight |

⚠️ Questi sono costi **lordi**: se il tuo backtest è MT5 su tick reali, lo spread storico e l'attraversamento degli stop ci sono già — leggi il §4.4 prima di sottrarre qualunque cosa.

**Scala i valori sulla TUA distanza di stop.** Con uno stop di 15 punti lo spread pesa `1,45/15 = 0,097 R`, cioè **2,7 volte** quanto pesa da noi, e uno slittamento come quello del 28/09 (+5,51) costerebbe **0,37 R** in un colpo solo. Il costo in R esplode al ridursi della distanza: è il vincolo che decide se una strategia intraday sopravvive o no.

### 4.3 Il filtro costi che usiamo, e la soglia che ne esce

Una delle due strategie rifiuta gli ingressi la cui distanza non soddisfa

```
dist ≥ 8 × (spread + 2 × slippage_stimato)
```

con `slippage_stimato = 1,0 punto`. Con spread 1,45 la soglia è **dist ≥ 27,6 punti**. Il moltiplicatore 8 non è ottimizzato: viene da un'analisi costi con altopiano largo, e fissa il costo totale di esecuzione a un tetto del **12,5% di R**.

### 4.4 ⚠️ L'errore da non commettere: sottrarre i costi due volte

> **Se la tua lista di trade è costruita dai prezzi di uscita REALI, i costi di uscita sono GIÀ dentro i numeri.** Sottrarli di nuovo è un doppio conteggio.

Come accorgersene: guarda la **media degli stop espressa in R**. Se il sistema perde esattamente 1R sugli stop, i costi non sono dentro. Se perde **più** di 1R, la differenza è il costo già incorporato.

Nel nostro caso, sul backtest: media degli stop = **−1,0225 R** → eccedenza del **2,25%**: è l'attraversamento degli stop che il tester riproduce sui tick reali (§1.3). Dal vivo, sui **15 stop con riancoraggio garantito** (26/08 → 01/10): **−1,0181 R** → **+1,81%** (sugli 11 fino al 17/09 era −1,0228). **Le due cifre coincidono entro mezzo punto percentuale**: il backtest rappresenta correttamente ciò che succede allo stop, se mai in modo leggermente prudente.
Sull'altra strategia, stop protettivo teorico a −2,0000 R → realizzato nel backtest **−2,0549 R** (+2,74%). Quella serie viene da un **backtest in Python su barre M1**: i 106 stop protettivi oltre −2R (su 116: gli altri 10 hanno taglia ridotta dal tetto al nozionale) valgono in media −2,081 R, cioè circa +4% della distanza. Dal vivo i tre stop protettivi valgono **−2,015, −2,015 e −2,123 R**, media **−2,051 R** (+2,54%). ⚠️ *La rev 4.1 affermava che il backtest a barre «gonfia» l'attraversamento, sulla base dei primi due casi (+0,18% e +0,73%): con il terzo (+6,15%, §2.5) la media dal vivo è vicina a quella del backtest. **Con tre casi non si può dire né che lo sovrastimi né che lo sottostimi.*** Il controllo sulla perdita media agli stop vale comunque anche su un backtest a barre.

**Quindi: se la serie viene dai prezzi reali, restano da sottrarre solo gli ORDINI A MERCATO**: lo slippage d'ingresso e quello delle uscite a mercato (≈0 in media, ma con varianza) e lo spread **se la serie non lo contiene già**. Un backtest MT5 su tick reali lo contiene, ma allo spread storico dell'epoca (0,60 nel 2021 contro 1,45 oggi): in quel caso sottrai solo la differenza.

---

## 5. LIMITI DEL CAMPIONE — leggili prima di fidarti

1. **È un conto DEMO.** Server `FTMO-Demo`, denaro non reale, sia sui conti Standard sia sul conto Swing. L'infrastruttura è la stessa del conto pagato, ma l'esecuzione su demo può essere più benigna di quella su un conto finanziato. **Nessuna di queste misure è stata confermata su denaro vero.** È il limite più serio.
2. **La coda è campionata solo in parte.** Con n=19 stop del breakout abbiamo **un** caso sopra il 5% (+6,85%), contro il **9,4%** atteso dal modello storico: **il modello regge nella parte bassa della coda**. In punti, il caso peggiore (+5,51) è arrivato su uno stop del momentum. Ma i **3 casi su 778 oltre il 20%** restano **non campionati**, e per vederne uno servirebbero ~250 stop. **La media e la coda moderata sono affidabili; la coda estrema no.**
3. **n = 35 ingressi.** L'IC95% della media dello slippage d'ingresso è ±0,76 punti: abbastanza per dire "è centrato su zero", non abbastanza per dire "è zero".
4. **Tutti gli ingressi cadono in due famiglie di orari**: le 16:35 server (breakout) e i confini semi-orari fra le 17:00 e le 22:30 (momentum). Lo spread fuori da quelle finestre è diverso e più largo (§2.3), e nell'ora che precede l'apertura cassa arriva a 2,19. **Se la tua strategia entra in altri orari, il profilo di spread non è questo.**
5. **⚠️ Esecuzione nei minuti dei dati macro: mai campionata su uno stop.** Confrontando i 22 stop eseguiti dal server con il calendario economico MQL5 (eventi USD ad alto impatto), **nessuno è caduto entro ±2 minuti da un dato**: il più vicino è del 29/09, **3 minuti e mezzo prima** di JOLTS e Fiducia dei consumatori delle 17:00 server. L'esposizione però esiste: la strategia di breakout entra alle **16:35 server = 9:35 di New York**, e i dati delle **10:00 ET** escono alle **17:00 server**, con la posizione aperta e nessun filtro (§6.1). **Due volte** una posizione del breakout ha attraversato un dato delle 10:00 ad alto impatto (10/09 vendite di case esistenti, 24/09 vendite di case nuove) senza toccare lo stop. Lo slippage sullo stop in quei minuti resta **non misurato** e può essere fuori scala rispetto alla media. *(Il calendario di FTMO per la regola news del conto finanziato non coincide necessariamente con gli eventi «ad alto impatto» di MQL5.)*
6. **Un solo strumento per lo slippage.** Tutto `US100.cash`. Su altri simboli dello stesso broker non abbiamo misure di slippage; le commissioni e i dati del §2.10 mostrano già che i costi cambiano per simbolo.
7. **Tre notti di swap, quattro posizioni, tutte short, con segno ±** *(§2.2)*. Nessuna misura su long, su nottate multiple, sul weekend; giorno del triplo non verificato. **Lo swap su US100.cash va trattato come ignoto.**
8. **Periodo corto**: **nove settimane**, 04/08 → 01/10/2026. Nessuna misura in condizioni di stress estremo (gap di weekend, aperture dopo weekend turbolenti); un solo movimento rapido documentato (28/09).
9. **Il mix d'uscita di un periodo breve non è quello della strategia.** Nella settimana 21-24/09 le uscite a livello sono state 0 su 7, nella settimana 28/09-01/10 5 su 6, dal 17/08 22 su 33. Per stimare il costo medio d'uscita usa il mix del backtest (§2.6), non quello realizzato di poche settimane.
10. **Conto Swing: solo 6 trade.** I costi misurati sul conto Swing (spread 1,45 su 4 ingressi del breakout su 4, commissioni 0,00) sono identici a quelli dei conti Standard, ma su un campione minimo.

---

## 6. COSA NON È MISURATO E VA CHIESTO ALTROVE

- Costo di esecuzione su **ordini pendenti** (limit/stop d'ingresso): abbiamo usato **solo ordini a mercato**.
- **Requote e rifiuti sul prezzo**: zero osservati, quindi nessuna stima della loro frequenza reale. *(I rifiuti amministrativi sono al §2.9.)*
- **Slippage diretto sulle uscite a mercato**: il prezzo richiesto di una chiusura non viene loggato, quindi lo assumiamo simile a quello d'ingresso.
- **Spread nei minuti successivi a un dato macro** e **spread continuo in orario USA**: abbiamo solo istantanee.
- **Parziali**: mai eseguite chiusure parziali.
- **Gap overnight e di weekend**: la finestra di 76 minuti senza quotazioni è stata attraversata tre volte (24→25/08, 15→16/09, 23→24/09); il gap alla riapertura è stato osservato solo il 24/09 (non significativo). Mai un weekend.
- **Margine sugli indici su un conto Swing** (leva di conto 1:30).
- **Slippage su XAUUSD e su qualunque simbolo diverso da US100.cash.**
- **Costo su conto finanziato reale** (vedi §5.1).

### 6.1 ⚠️ IL CAMPIONE NON È CENSURATO DALLE NEWS — e questo è importante

> **Domanda che ti devi porre prima di usare qualunque statistica di esecuzione altrui: quel campione esclude i momenti peggiori?** Se la strategia che li ha prodotti salta gli ingressi vicino ai dati macro, i suoi costi sono **ottimistici per costruzione** e non trasferibili.
> **Qui la risposta è no: il campione non esclude nulla.** Sotto c'è la verifica, fatta sul sorgente in esecuzione e non sulla documentazione.

**La strategia di breakout — quella da cui vengono 25 delle 35 misure di slippage d'ingresso e tutte e 19 quelle sullo stop del breakout — non ha alcun filtro news attivo.** Verificato sul sorgente effettivamente in esecuzione (`ORB_US100_-_step16_P.mq5`, md5 `30906e3e52838074c517a6ea4bb13ba5`, ultima compilazione 25/08/2026 17:20:01 secondo il log di MetaEditor, nessuna ricompilazione da allora), quattro fatti indipendenti:

| Riga | Codice | Cosa significa |
|---|---|---|
| 174-175 | `//--- filtro news: mai testato, serve solo per altri prop firm`<br>`const bool InpUseNews = false;` | **`const`, non `input`**: cablato a `false`, **non compare nemmeno** nella scheda *Dati in ingresso* di MT5. Non è disattivato per scelta di configurazione: è disattivato nel codice |
| 685 / 719 | `if(!InpUseNews) return;` · `if(!InpUseNews \|\| g_newsCount==0) return;` | `LoadNews()` e `CheckNewsClose()` escono entrambe alla prima riga. Non fanno nulla |
| 726 | `CloseAll("Chiusura pre-news")` | Anche se fosse attivo, **è una logica di USCITA**: chiude posizioni già aperte, non impedisce l'ingresso. L'EA entrerebbe comunque alle 16:35 |
| 176 / 686 | `InpNewsCloseMinBefore = 5`<br>`FileOpen(... FILE_COMMON)` | La finestra sarebbe di **5 minuti**, non ±120 secondi, con date da un **CSV compilato a mano** in `Common\Files\ORB_news.csv`. Nessun calendario automatico |

**Prova diretta dal vivo**: il pannello dell'EA stampa `news %d` con il numero di eventi caricati (righe 1274 e 1287). Sul grafico in esecuzione legge **`news 0`**.

> **Conseguenza: tutte le misure d'ingresso e tutte quelle sullo stop della strategia di breakout sono PULITE e RAPPRESENTATIVE.** Non escludono niente, non sono ottimistiche, non richiedono margini di sicurezza aggiuntivi. Usale così come sono.

**Un filtro news vero esiste, ma è nell'ALTRO EA** (`IntradayMomentum_NAS100_E.mq5`, quello di momentum, ultima compilazione 25/08/2026 17:19:08): lì `InpUseNewsFilter` è un vero `input` a `true`, usa il **calendario MQL5 nativo**, la finestra è **±120 secondi** e blocca davvero l'ingresso (`[IM] entry bloccata da news filter`).
**Ma anche lì la censura è teorica, non realizzata**: nei log disponibili (20 sedute fino al 18/09 e sedute 26-30) quella riga **non è mai comparsa**. Il 01/10 il check delle 17:00 server coincideva con l'ISM manifatturiero (alto impatto): nessun ingresso e nessuna riga di blocco, quindi a quel check non c'era segnale — o il filtro non ha parlato; dai log non si distingue.
*Verifica nuova (30/09)*: **il calendario MQL5 sul terminale FTMO restituisce dati** — un nostro script ne ha esportati **64.986 eventi 2021-2026** (22.171 in USD). Il rischio che un filtro basato su quel calendario sia «silenziosamente vuoto» per calendario non disponibile è quindi escluso su questo terminale; resta non verificato che l'EA lo legga correttamente al momento del check.

> *Nota di tracciabilità: una revisione precedente di questo documento affermava il contrario — che gli ingressi fossero filtrati e i numeri quindi ottimistici. **Era falso**: confondeva i due EA. L'errore è stato trovato leggendo il sorgente riga per riga, ed è la ragione per cui questa sezione cita numeri di riga: perché tu possa verificare invece di fidarti.*

---

## 7. RIASSUNTO IN DIECI RIGHE, SE HAI FRETTA

1. **Commissioni: zero su US100.cash** (0,00 $ su tutti i 33 trade dal 17/08, anche sul conto Swing). Ma sullo stesso conto FX paga 2,50 $/lotto/lato e l'oro 3,00 $: lo zero vale solo per questo simbolo.
2. **Spread all'apertura USA: 1,45 punti indice** su 23 ingressi su 23, in crescita di anno in anno (era 0,60 nel 2021). **1,45 anche in orario USA** nelle letture dal vivo (lo 0,80 storico non vale per il 2026); fuori orario 1,25-1,95, **fino a 2,19 nell'ora prima dell'apertura cassa**. **Si paga una volta per round-trip.**
3. **Slippage d'ingresso a mercato: media −0,02 punti su n=35**, 17 sfavorevoli e 17 favorevoli, deviazione standard 2,22, estremi −6,50 e +5,71. È **rumore, non costo** — ma è rumore *sul rischio* (0,81×-1,13× del voluto), e va neutralizzato riancorando lo stop al prezzo eseguito (riuscito 27 volte su 27).
4. **Slippage sullo stop server-side: +1,51% della distanza sul breakout** (+0,59 punti), 15 casi su 19 sfavorevoli; **≈0,8 punti di media su tutti i 22 stop**, peggiore **+5,51 punti** (28/09, movimento rapido senza notizie). Su stop di ampiezza diversa ragiona in punti.
5. **Le uscite a mercato non pagano quello slippage.** Undici osservate, quattro tipi, 10 su 11 fra 189 e 250 ms; eccezione: il primo ordine alla riapertura notturna delle 01:05 (1,3 s). **Conta il mix di uscite della tua strategia — sul backtest, non su poche settimane** (21-24/09: 0 uscite a livello su 7; 28/09-01/10: 5 su 6).
6. **Il costo in R scala con l'inverso della distanza dello stop.** 1,45 punti di spread sono 0,036 R su uno stop da 40 punti e **0,097 R** su uno da 15.
7. ⚠️ **Lo swap su US100.cash non è una costante**: tre notti, sempre short, due a credito e una a debito, ≤ 0,28 $/lotto/notte. **Sull'oro è forte e a debito in entrambe le direzioni** (≈ −65/−90 $ per lotto per notte sui long).
8. **Il tester MT5 non modella lo slippage degli ordini a mercato** (l'attraversamento degli stop sì, con i tick reali), `ResultPrice()` su FTMO non ti dà il prezzo eseguito, e lo slippage loggato da un EA che ritenta è misurato contro l'ultimo tentativo. Senza la cronistoria non stai misurando niente.
9. **Se la tua serie di trade viene dai prezzi reali, i costi delle uscite a livello ci sono già** (dal vivo −1,0181 R su 15 stop contro −1,0225 R nel backtest). Sottrai solo gli ordini a mercato: ingresso e uscite a orario, ≈0 in media.
10. **Zero rifiuti sul prezzo, la deviation è ignorata in entrambe le direzioni, e i rifiuti amministrativi arrivano in serie** (mercato chiuso, conto disabilitato): un EA che ritenta senza leggere il codice d'errore può superare in minuti il limite FTMO di 2.000 richieste al giorno.

---

### Storico delle revisioni
- **rev 1** (15/09): prima stesura, campione di 15 sedute.
- **rev 2** (16/09): ritirata un'affermazione falsa sul filtro news (§6.1); aggiunto il limite n.5.
- **rev 3** (19/09): campione esteso a **20 sedute**. Tre cambiamenti sostanziali: la **coda dello slippage sullo stop si è campionata** (+6,85%, §2.5); lo **swap ha cambiato segno** sulla seconda osservazione (§2.2); osservate **tre uscite a mercato di tipo diverso** (§2.6). Aggiunta la §2.8 sull'esposizione overnight.
- **rev 4** (26/09): campione esteso a **24 sedute** (7 trade nuovi, 21-24/09). Novità: **terza osservazione di swap** (a credito, tasso identico su due posizioni); **sette uscite a mercato**, due delle quali alla riapertura delle 01:05 (prima misura dal vivo della pausa notturna: rifiuti `[Market closed]` e latenza 1,3 s); nuova **trappola 1.6** (slippage misurato contro l'ultimo tentativo); nuova **§2.9** (rifiuti amministrativi e limite FTMO delle 2.000 richieste); **commissioni di FX e oro** come termine di paragone (§2.1); verifica del §4.4 dal vivo su 11 stop.
  **Errori della rev 3 trovati e corretti** — nessuno cambia le conclusioni:
  (a) la serie dello slippage d'ingresso era dichiarata «n = 16» nell'intestazione e «n = 20» nel testo, comprendeva due misure pre-forward e **ometteva due ingressi del momentum** (24/08 +1,25; 04/09 0,00): ora è completa;
  (b) lo stop del momentum del 24/08 era **contato due volte** — dentro la serie dei 16 stop (+0,18%) e di nuovo come stop protettivo con un valore errato (+1,37 pt = +0,62%): la serie del breakout è ora di 15 stop, media +1,77% invece di +1,67%;
  (c) lo swap del 24/08 era riportato su **3,64 lotti a +0,34 $/lotto**: i lotti reali erano **4,48**, il tasso corretto è **+0,28**;
  (d) la tabella del §4.2 contava lo spread **due volte** sulle uscite a mercato (all'ingresso e di nuovo in uscita): si paga una volta per round-trip;
  (e) il §4.4 usava ancora il confronto dal vivo su 3 stop del 30/08: aggiornato a 11;
  (f) il limite n.5 diceva che lo stop del 17/09 (16:54 server) era arrivato *dopo* la finestra delle 17:00: è arrivato prima.
- **rev 4.1** (26/09, doppio controllo sulle fonti): (g) **§1.3 riscritto**: la frase «qualunque costo di slippage va aggiunto a mano» era sbagliata per le uscite a livello — con i tick reali il tester esegue gli stop al tick che attraversa il livello, e il nostro backtest li valuta già −1,0225 R; aggiungerlo di nuovo sarebbe un doppio conteggio (nota aggiunta anche sotto la tabella del §4.2 e al punto 8 del §7); (h) tempi di `PositionModify` fino al 18/09 ricalcolati sui 7 valori documentati nel verbale: media **133 ms**, range **64-242** (la rev 3 scriveva 137 e 77-242); (i) riferimenti di riga del §6.1 precisati (1274 e 1287; testo della riga 719); (j) precisato che i primi due ingressi del campione stanno su un conto precedente e da dove viene la verifica del fuso del server; (k) il riquadro del §2.3 diceva che lo spread medio storico «sottostima il costo attuale di oltre il doppio»: è vero rispetto al 2021 (2,4 volte), non rispetto alla media (1,4 volte, circa il 30%); (l) la coda del §4.2 era data «fino a 0,20 R»: nel backtest 3 stop su 778 la superano, il peggiore a 0,63 R; (m) aggiunte al §2.5 l'indicazione di ragionare in punti per stop di ampiezza diversa e la nota sui take profit (uno solo colpito dal vivo, senza misura); (n) §4.4: il +2,25% del backtest è l'attraversamento riprodotto dal tester, non uno slippage «assunto»; la serie del momentum è un backtest a barre in Python e sovrastima l'attraversamento (almeno +4% sugli stop oltre −2R); (o) ping domestico 29-76 ms (la rev 4 scriveva 40-54, contro letture del journal a 29 ms il 21/08 e a 76 ms il 24/08); (p) il fill a −6,50 del 10/09 era a favore; (q) la finestra senza quotazioni è stata attraversata in tutte e tre le notti, non una volta sola; il gap è stato osservato solo il 24/09 (§2.8, §6); (r) la verifica del fuso sull'altro broker riguarda le settimane di disallineamento del 2024-25, non «9 anni» (§3); (s) «27 trade del forward» e «intero forward» ora dicono «dal 17/08»: il trade del 17/08 precede il forward (§2.1, §2.6, §5, §7); (t) anche lo slippage delle uscite a mercato va aggiunto, non solo quello d'ingresso (§4.4, §7); (u) il sottotitolo non dice più che nessun numero è stimato: la coda dello slippage viene dal backtest e lo slippage delle uscite a mercato è assunto.
- **rev 5** (06/10): campione esteso a **30 sedute** (6 trade nuovi, 28/09-01/10, conto 4 di tipo **Swing**). **Ricalcolata da zero**: tutti i 33 trade dal 17/08 sono stati ricostruiti dai Report Cronistorici dei quattro conti e dai journal, con verifica automatica del P&L di ogni trade e del saldo finale di ogni conto al centesimo; ogni statistica di questo documento è ora riproducibile dal file `ESECUZIONI_REALI_FTMO_US100_TRADE.csv`, che accompagna il documento. La ricostruzione riproduce esattamente tutte le statistiche della rev 4.1 (n=29: media −0,204, IC95% [−0,99 ; +0,58]; 15 stop: +1,773%; 11 stop riancorati: −1,0228 R).
  **Novità**: peggior slittamento d'ingresso contrario (+5,71) e peggior slittamento sullo stop in punti (+5,51, movimento rapido senza notizie, §2.5); deviation ignorata anche su un fill contrario (§2.7); profilo dello spread con l'ora che precede l'apertura cassa (fino a 2,19) e con le letture dal vivo in orario USA (1,45: lo 0,80 storico non vale per il 2026, §2.3); latenze complete dai journal per tutti i 33 ingressi, e loro aumento dopo la build 6230 (§2.7); margine degli indici su conto Standard (2,00% = 1:50) e leva del conto Swing (1:30, §3); nuova **§2.10 sull'oro**; confronto degli stop con il calendario economico MQL5 (§5.5); verifica che il calendario MQL5 è popolato sul terminale FTMO (§6.1); distanza di riferimento del §4.2 aggiornata a 40,47.
  **Errori della rev 4.1 trovati e corretti**: (v) il rischio effettivo senza riancoraggio nei casi estremi era dato «da 0,83×»: il valore corretto è **0,81×** (10/09: 28,33 punti di distanza reale contro 34,83 voluti); (w) l'affermazione che il backtest a barre del momentum «sovrastima» l'attraversamento degli stop è **ritirata**: con il terzo stop dal vivo (+6,15%) la media dal vivo (+2,54% in R) è vicina a quella del backtest (+2,74%), e con tre casi non si distingue (§4.4); (x) i tempi d'esecuzione degli ingressi erano su «20 documentati» (mediana 234 ms): letti ora dal journal per tutti e 27 gli ingressi fino al 24/09, la mediana è **232 ms** — differenza immateriale.
- **rev 5.1** (06/10, doppio controllo prima della consegna): (1) il CSV è stato **riverificato con un secondo script indipendente**, campo per campo contro le cinque cronistorie disponibili e i journal: **0 differenze su 33 trade**; i tre dati presi dal verbale (09/09, 10/09, chiusura del 24/09) sono confermati dalle righe di deal dei journal originali; (2) **108 controlli** sulle statistiche citate nei documenti, ricalcolate da zero dal CSV: tutte coincidono, salvo una differenza di arrotondamento sull'ultima cifra (§0); (3) uptime, check, ping, riconnessioni e istantanee di spread ricontrollati sui log. **Precisazioni**: (y) i 27 riancoraggi su 27 sono gli ingressi con slippage non nullo: il 28° ingresso delle build attuali (04/09) aveva slippage zero (§1.2); (z) la mediana delle 20 istantanee di spread dell'oro è **0,405** (media 0,40), non 0,40 (§2.10); (aa) aggiunta la nota sull'arrotondamento di `R` nel CSV (§0); (bb) il conto pre-forward `1514172196` registrò **tre** ingressi (04, 06 e 07/08), lo slippage è documentato per due (piè di pagina). Nessun valore misurato né alcuna conclusione cambia.

---

*Misure raccolte da tre ingressi dal vivo precedenti (04/08 → 17/08; i primi due su un conto Free Trial precedente, `1514172196`, che di ingressi ne registrò tre fra il 04 e il 07/08: lo slippage è documentato per due) e dal forward test di due Expert Advisor su FTMO-Demo, **21/08 → 02/10/2026, 30 sedute**, conti `1514282053`, `1514463987`, `1514618793` (Free Trial 2-Step; l'ultimo disabilitato da FTMO dopo il raggiungimento degli obiettivi del Free Trial: target del 5% raggiunto il 24/09 alle 22:55 server, trading disabilitato al collegamento successivo) e `1514768646` (Free Trial **Swing** 2-Step, leva 1:30, dal 28/09). Ogni cifra è ricostruibile dai log Experts/Journal di MetaTrader 5, dai Report Cronistorici dei Trade archiviati e dal file `ESECUZIONI_REALI_FTMO_US100_TRADE.csv`; ogni trade del forward è stato riconciliato al centesimo contro l'estratto conto. **Revisione 5.1 del 06/10/2026.***
