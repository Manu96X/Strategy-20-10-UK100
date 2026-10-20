# PROTOCOLLO PRE-REGISTRATO — S1 (prosecuzione dopo i dati macro USA) e S2 (reversione dopo le aste di chiusura)
*Versione definitiva del 20/10/2026, scritta **prima di qualunque risultato** su queste ipotesi: lo certifica l'orario del commit. Manu: «Procedi con S1 e S2. Solo se nessuna delle 2 risulta valida procedi con S3». La bozza è stata rivista da tre revisori avversari indipendenti (statistica; dati e fusi; costi e FTMO) **senza guardare rendimenti**: tutte le correzioni sono state integrate qui prima dei numeri. Correzioni successive solo come addendum datati «prima/dopo i numeri».*

## 0. Cosa è già stato visto e cosa è cambiato rispetto alla bozza
- **Già visto (nessun rendimento intorno agli eventi o alle aste)**:
  - calendario: conteggi, campi, orari;
  - per i costi, dal 2025-2026: colonna SPREAD FTMO, livello di prezzo per convertire in bps, file M1BA;
  - tick volume e presenza delle barre (revisori).
- **Event study precedente** (< 2024), test vicini, tutti nulli o deboli: G1 (prosecuzione dopo l'EIA sul petrolio), B2 (deriva dopo il FOMC fino al giorno dopo).
- **Dossier FTMO §8**:
  - mean reversion intraday morta su NAS100, US500, GER40 e oro, compreso il «fade di fine sessione»;
  - «gli estremi intraday continuano».
  - È un indizio a favore di S1 e un precedente contrario a S2. **Prior su S2 basso.**
- **Trappola scoperta in revisione: il calendario è in UTC+3 fisso.** La colonna `ora_server` di `calendario_economico.csv` vale **UTC + 3 ore in tutti gli anni**: è l'offset del giorno dell'export.
  - Verificato su NFP 08:30 (129 su 130), sussidi 08:30, ISM 10:00 e FOMC 14:00 di New York, CPI dell'Eurozona e Tokyo CPI, e sul picco del tick volume.
  - La bozza (e il RAPPORTO_H1 §4) diceva «NY+7»: era sbagliato per i mesi di ora solare USA, cioè un terzo degli eventi.
- **Correzioni rispetto alla bozza**:
  - **S1**: tolta la famiglia «sorpresa». Il campo `previsto` del calendario MQL5 è la previsione del modello di MetaQuotes, non il consenso di mercato (es. NFP 03/02/2023: previsto 16, consenso ≈ 188).
  - **Test primari aggregati** per paniere, con BH separata per ipotesi (potenza molto più alta).
  - **Uscite S1** limitate prima della notizia successiva (regola FTMO e niente contaminazione).
  - **Costi**: per fascia oraria e minuto esatto, forex ×2.
  - **S2**: meccanismo riscritto, L = 15 minuti negli USA, FRA40 escluso dall'uscita notturna, placebo d'orario, diagnostica dei giorni di asta pesante.

## 1. Dati, sigilli, campioni
- **Scoperta**: eventi e giorni **< 01/01/2024**, solo copie sigillate:
  - `/home/user/dati_h1/scoperta` (SIGILLO.txt del 20/10/2026 15:23 UTC: forex, metalli);
  - `/home/user/dati_scoperta_tutti` (SIGILLO.txt: indici, metalli);
  - `/home/user/dati_s12/scoperta` (`/home/user/dati_s12/SIGILLO.txt` del 20/10/2026 16:15 UTC):
    - US30 Pep `4557c62e…`;
    - US2000 Pep `da9154de…`;
    - US2000 FTMO `fa9f20c5…`;
    - FRA40 FTMO `2dfa2233…`.
- **Validazione**: il 2024, copie sigillate in `…/validazione_2024`, aperte **una volta** e solo per le strategie promosse.
- **Hold-out**: 2025-2026, mai toccato per i rendimenti.

| Strumento | Feed d'inferenza (inizio) | Concordanza | Regola del fuso |
|---|---|---|---|
| EURUSD, USDJPY | FTMO (04/01/2016) | — | ora di Atene fino al 31/12/2019, NY+7 dal 2020 |
| GBPUSD | FTMO (04/01/2016; escluse le giornate non M1 dal 01/01 al 07/02/2019) | — | come sopra |
| XAU | Pepperstone (12/06/2017) | FTMO (04/01/2021) | NY+7 |
| US100 | Pepperstone NAS100 (09/06/2017) | FTMO (14/09/2021) | NY+7 |
| US500 | Pepperstone (13/07/2020) | FTMO (14/09/2021) | NY+7 |
| US30 | Pepperstone (02/01/2018) | — | NY+7 |
| US2000 | Pepperstone (05/06/2017) | FTMO (09/04/2018) | NY+7 |
| GER40 | Pepperstone (11/06/2020) | FTMO (28/12/2021) | NY+7 |
| UK100 | Pepperstone (06/06/2017) | FTMO (14/09/2021) | NY+7 |
| FRA40 | FTMO (14/09/2021) | — | NY+7 |

NY+7 = ora di New York (con l'ora legale USA) + 7 ore.

## 2. Definizioni operative comuni (univoche, per le repliche cieche)
- **Istanti**: ogni istante è fissato in ora locale (New York o la borsa), convertito in UTC con `zoneinfo`, poi nell'ora server con la regola del feed.
  - **Calendario**: UTC = `ora_server` − 3 ore, per tutti gli eventi e tutti gli anni.
- **Barre valide**: una barra è utilizzabile solo se il suo giorno server ha passo modale fra barre consecutive = 1 minuto.
- **Prezzo «a t»** = open della prima barra che inizia in [t, t+5 min]; valido solo se esiste anche una barra che inizia in [t−5 min, t) (continuità: niente prezzi di riapertura dopo una pausa).
- **Prezzo «prima di t»** = close dell'ultima barra che inizia in [t−5 min, t).
- Un prezzo mancante esclude il trade (non si cercano sostituti).
- **σ_d** del giorno d:
  - prezzi «prima di» 16:00 New York (S1; S2 USA) o «prima dell'asta» locale (S2 Europa), con tolleranza di 15 minuti;
  - rendimenti logaritmici fra chiusure valide consecutive distanti ≤ 4 giorni di calendario;
  - σ_d = deviazione standard (ddof = 1) degli ultimi 20 rendimenti validi fino a d−1. È nota prima del giorno d.
- **Unità**: z = rendimento netto / σ_d; bps = rendimento netto × 10⁴.
- **Notizie vietate** (per uscite e ingressi): eventi ad alto impatto (`importanza` = 3, ORARIO_ESATTO) delle valute pertinenti, più «Dichiarazione del FOMC», «Verbali FOMC» e «Proiezioni Economiche del FOMC». Valute pertinenti:
  - EURUSD: USD, EUR; GBPUSD: USD, GBP; USDJPY: USD, JPY;
  - oro e indici USA: USD;
  - GER40 e FRA40: EUR e USD; UK100: GBP e USD.
- **Statistica di ogni test**:
  - t con errori raggruppati per data di New York (CR1), distribuzione di Student con G−1 gradi di libertà;
  - **p primario unilaterale** sulla media netta base > 0;
  - meno di 30 osservazioni → p = 1;
  - bootstrap per giorno (10.000, seme 20261020, ricentrato) solo descrittivo: in caso di disaccordo prevale il t.

## 3. S1 — prosecuzione dopo i dati macro USA (famiglia S1-R)
- **Eventi** (elenco chiuso, 31 voci): valuta USD, importanza 3, ORARIO_ESATTO, con `attuale` presente, giorni feriali di New York.
  - Voci: elenco chiuso per `event_id` in `EVENTI_S1_ELENCO_CHIUSO.csv` (31 righe: dati numerici e decisione del FOMC).
  - **Esclusi**: EIA, aste, discorsi, testimonianze, conferenze stampa.
  - Più dati allo stesso minuto = un evento T.
  - Per US100 e US500 sono esclusi i giorni di chiusura NYSE.
- **Prezzi**:
  - P_pre = prezzo prima di T;
  - P_in = prezzo a T+3 minuti (ingresso);
  - reazione r0 = ln(P_in / P_pre).
- **Ingresso escluso** se una notizia vietata cade in [T+1, T+5] minuti.
- **Uscita** = prezzo a min(T+H, E − 3 minuti), con E la prima notizia vietata dopo T (minuto diverso da T); H ∈ {30, 60, 120} minuti. Se l'uscita cade prima di T+4 minuti, nessun trade.
  - Questa regola rende impossibili le posizioni sovrapposte sullo stesso strumento, rispetta la regola FTMO ±2 minuti ed evita che l'evento successivo contamini la deriva.
- **Segnale**: verso q = segno(r0); si entra solo se |r0| ≥ c·σ_d, c ∈ {0,10; 0,25}.
- **Strumenti**: EURUSD, GBPUSD, USDJPY, XAU, US100, US500.
- **Test primari: 6 aggregati**, uno per (c, H). Per ogni evento, valore = media dei z netti base degli strumenti che fanno il trade su quell'evento. **BH q = 0,10 sui 6.**
- **Test secondari** (gerarchici, solo descrittivi della composizione): i 36 test per strumento, con BH solo dentro le configurazioni promosse. **La strategia negozia tutti e 6 gli strumenti, senza selezione.**

## 4. S2 — reversione dopo le aste di chiusura (sul prezzo del CFD)
- **Meccanismo dichiarato e limiti**:
  - i CFD seguono i futures e quotano durante le aste: il test misura il movimento del **future** intorno all'asta cassa. È una «pressione di fine giornata sul future»; l'effetto documentato (Bogousslavsky-Muravyev 2023) riguarda la stampa di chiusura cassa.
  - Nei futures la letteratura trova anzi momento nell'ultima mezz'ora (Baltussen et al. 2021).
  - **Un esito nullo non dice nulla sull'asta cassa. Prior basso.**
- **Panieri**: USA (US500, US100, US30, US2000; borsa NYSE) ed Europa (GER40 su Xetra, UK100 su LSE, FRA40 su Euronext Parigi).
  - Giorni di borsa interi: esclusi festivi e mezze sedute (NYSE alle 13:00; LSE alle 12:30, cioè l'ultimo giorno lavorativo prima di Natale e di Capodanno; Xetra/Euronext 24 e 31/12).
- **Asta** A (ora locale): 16:00 New York; 17:30 Francoforte e Parigi; 16:30 Londra.
- **Movimento prima dell'asta** m = ln(P(prima di A) / P(prima di A − 15 min)): **L = 15 minuti ovunque**, perché copre la pubblicazione degli squilibri NYSE delle 15:45 e delle 15:50.
- **Ingresso**: prezzo a A+1 minuto negli USA, a A+6 minuti in Europa. Verso q = −segno(m); si entra solo se m ≠ 0 e |m| ≥ c·σ_d, c ∈ {0; 0,10}.
- **Uscite**:
  - **X1** = prezzo a A+45 minuti (16:45 NY, prima della pausa delle 16:50 di US100.cash; 18:15 Francoforte e Parigi; 17:15 Londra);
  - **X2** = prezzo alla pre-apertura del giorno di borsa successivo (09:25 NY; 08:55 Francoforte; 07:55 Londra):
    - solo se quel giorno è il giorno di calendario seguente;
    - **FRA40 escluso da X2**: la pausa notturna FTMO supera le 2 ore, quindi non è detenibile sul conto Standard;
    - se una notizia vietata cade prima della pre-apertura, l'uscita va a E − 3 minuti.
- **Test primari: 8 aggregati** (paniere × c × uscita). Per ogni giorno, valore = media dei z netti base degli indici del paniere che fanno il trade. **BH q = 0,10 sugli 8.** I test per indice sono secondari, come in S1.
- **Diagnostiche** (non cancelli, riportate per ogni test promosso):
  - **placebo d'orario**: stessa costruzione con A' = A − 60 minuti e uscita a A' + 45. Se il placebo è grande quanto l'effetto, è una generica reversione intraday;
  - **giorni di asta pesante**: terzo venerdì di marzo, giugno, settembre e dicembre; ultimo venerdì di giugno. Se l'effetto non è più forte lì, va dichiarato «meccanismo non confermato» prima della validazione;
  - X2 su UK100 senza gli ingressi del mercoledì (stacco dei dividendi del giovedì).

## 5. Costi FTMO (di oggi) — formula unica
**Tabella congelata** `risultati/COSTI_TABELLA_CONGELATA.csv` (sha256 `dc21e2bb60ab667c…`, prodotta da `costi_s12.py` prima dei numeri). Spread in bps, p75 della colonna SPREAD FTMO (minimo del minuto) dal 10/10/2025 al 09/10/2026, per contesto:
- `S1_evento|fascia`: minuti T+3..T+5 dopo i dati USD, per fascia oraria NY dell'evento (08:00-08:59; 09:00-09:59; 10:00-11:59; 12:00-16:59);
- `NY|hh:mm`: mezz'ora di New York, per le uscite di S1;
- `S2|…`: minuto locale esatto ±2 di ingresso, X1, X2 e placebo.

Regole per strumento:
- **US100 e oro**: massimo con lo spread reale all'apertura del minuto dei file M1BA 2025-2026, nello stesso contesto.
- **Forex** (il minimo del minuto sottostima uno spread variabile): base = max(2 × p75; 0,2 pip); stress = max(3 × p75; 0,3 pip).
- **Indici e oro**: stress = 1,5 × base.
- **US30** (nessun file FTMO): massimo fra lo spread della specifica riscalato col rapporto contesto/quotazione congelata di US100 e quello di US100 e US500 nello stesso contesto.

Costo in frazione del prezzo:
- **spread**: i long pagano lo spread del contesto d'ingresso, gli short quello del contesto d'uscita (prezzi bid);
- **commissioni** [MISURATO]: forex 5 $ / (100.000 × prezzo in $ della valuta base) a round-trip; oro 6 $ / (100 × prezzo); indici 0;
- **stress**: più 2 × 0,3 bps di slittamento (tutti gli strumenti);
- **swap** (solo X2, una notte da lunedì a giovedì) [SPECIFICA]:
  - indici USA: long −0,0227%, short +0,0011%;
  - GER40: −0,0178% / −0,0002%;
  - UK100: −0,0236% / +0,0011% (punti della specifica convertiti col prezzo mediano 2025-26);
  - in stress gli swap a debito × 1,5.

## 6. Cancelli di PROMOZIONE (per configurazione aggregata; tutti insieme)
1. **BH** superata nella propria ipotesi (S1: m = 6; S2: m = 8).
2. **Netto stress** medio z > 0.
3. **Netto base** medio in **bps** > 0.
4. **Metà del campione**: netto base z > 0 sia prima sia dopo il **01/01/2020**.
5. **Anni**: ≥ 3 anni con ≥ 10 osservazioni e ≥ 60% di essi con netto base > 0.
6. **Coerenza**:
   - stesso c, lordo aggregato > 0 su almeno 2 delle 3 H (S1) o su entrambe le uscite (S2);
   - almeno metà degli strumenti del paniere con netto base > 0 nella configurazione.
7. **Influenza**: netto base z > 0 anche togliendo l'1% delle date con il maggior |contributo| alla media.
8. **Feed**: stesso segno del lordo aggregato ricalcolato in modo indipendente sui feed di concordanza (S1: XAU, US100, US500; S2-USA: US500, US100, US2000; S2-Europa: GER40, UK100), sugli stessi eventi o giorni del periodo comune.
   - Con meno di 100 osservazioni comuni il cancello non si applica.

**INDIZIO** = p < 0,05 e netto base > 0 senza tutti i cancelli. **NULLO** altrimenti.

**Verdetto**:
- S1 è valida se almeno una configurazione S1 è PROMOSSA;
- S2 è valida se lo è almeno una configurazione S2;
- se nessuna delle due → **S3**.

Si riportano anche, per test e anno, la quota di eventi persi per prezzo mancante. Oltre il 10% in un anno → ripetizione senza quell'anno, solo descrittiva.

## 7. Potenza dichiarata [STIMA, solo dal calendario]
- **S1**: ~1.955 orari di evento 2016-2023 (~245 l'anno; XAU e US100 dal 06/2017, US500 dal 07/2020). Con un filtro c che tiene il 40-70% degli eventi, n ≈ 800-1.400.
  - Soglia BH del primo rango 0,10/6 → t ≈ 2,13.
  - Sharpe per evento rilevabile: ≈ 0,060-0,075 al 50% di potenza, ≈ 0,08-0,105 all'80%.
- **S2**: ~1.600 giorni per paniere (X2 ≈ 1.150).
  - Soglia 0,10/8 → t ≈ 2,24.
  - Sharpe rilevabile ≈ 0,056 (50%) e 0,075 (80%) con n = 1.600.
- **Conferma** (validazione 2024 + hold-out 2025-2026, ~2,8 anni): può confermare solo effetti con Sharpe per evento ≥ ~0,08-0,10. Si assume fuori campione la metà dell'effetto della scoperta: se la potenza risultasse < 50%, va detto prima della validazione.

## 8. Dopo i numeri (fissato ora)
1. **Configurazione da portare avanti**, nell'ordine (non per t massimo):
   - S1: (0,10; 60) > (0,10; 30) > (0,10; 120) > (0,25; 60) > (0,25; 30) > (0,25; 120);
   - S2, per paniere: (0,10; X1) > (0; X1) > (0,10; X2) > (0; X2).
   - Si prende la prima promossa.
2. **Strategia**:
   - tutti gli strumenti del paniere, rischio uguale in z (lotti ∝ 1/σ_d);
   - stop di protezione sul server a 3 × la deviazione standard dei rendimenti della stessa finestra sugli ultimi 250 eventi o giorni (solo passato);
   - se lo stop cambia il segno o dimezza il netto, la strategia non va in validazione.
   - VPS obbligatoria.
3. **Validazione 2024**, una volta, un test per strategia: p unilaterale < 0,10 e netto stress ≥ 0.
4. **F4**:
   - Monte Carlo FTMO per giornata intera sull'equity intraday (la perdita fluttuante di X2 va attribuita al giorno FTMO successivo);
   - frequenza totale (obiettivo ≥ 0,7 trade al giorno);
   - **indipendenza** dalle liste del tester ORB e IM: quota di trade S1 su US100/US500 contemporanei e nello stesso verso di ORB o IM, e correlazione giornaliera in R. Oltre il 50% o oltre 0,3 la strategia non conta come nuova e il rischio si somma.
5. **Hold-out 2025-2026**, una volta, a regole congelate: p unilaterale < 0,05.

## 9. Doppio controllo prima di comunicare
- Repliche cieche di S1 e S2 dal solo protocollo e dalla tabella dei costi congelata.
- Revisore avversario del codice.
- Controllo a mano di eventi e giorni campione sulle righe grezze.
- I numeri si comunicano solo se originale e repliche coincidono.

## Addendum 1 — 20/10/2026, PRIMA dei numeri
La prima esecuzione (16:50 UTC) si è interrotta con un errore **prima di produrre qualunque risultato**: nessun numero è stato salvato o letto.
- **Causa**: un'uscita X2 anticipata prima di una notizia vietata (es. un discorso del presidente Fed alle 17:30 NY) cadeva nella pausa giornaliera del simbolo FTMO (16:50 → 18:05 NY), dove la tabella dei costi non ha contesto, perché FTMO non quota.
- **Regola aggiunta, per S1 e S2**: se l'ingresso o l'uscita cadono in un orario in cui il simbolo FTMO non quota (nessun contesto nella tabella congelata), il trade è **escluso**: su FTMO non sarebbe eseguibile.
- Le repliche cieche, già avviate, potrebbero aver trattato questi pochi casi in un altro modo: le differenze vanno riconciliate caso per caso.
