# RAPPORTO S1 + S2 — prosecuzione dopo i dati macro e reversione dopo le aste di chiusura
*20/10/2026. Protocollo `PROTOCOLLO_S1_S2.md`: commit 744c88c (16:44 UTC) e addendum 1 (e72fb4b), **prima** dei risultati; bozza rivista da tre revisori avversari. Etichette: [BACKTEST] dati di scoperta 2016/2017-2023 · [STIMA].*

## Verdetto: **S1 NON VALIDA · S2 NON VALIDA** → si passa a S3, come chiesto
Nessuno dei 14 test primari supera la correzione. **Il netto è negativo in tutte le 14 configurazioni**, anche prima dello stress.
Due repliche cieche indipendenti, scritte solo dal protocollo, danno gli stessi numeri e lo stesso verdetto (§3).

## 1. S1 — prosecuzione dopo i dati macro USA [BACKTEST]
1.955 orari di dati USA ad alto impatto 2016-2023 (circa 245 l'anno); 6 strumenti (EURUSD, GBPUSD, USDJPY, oro, US100, US500); ingresso 3 minuti dopo il dato nel verso della prima reazione.

| Configurazione | Eventi | Lordo (z) | Netto base (z) | t | Netto (bps) |
|---|---|---|---|---|---|
| c 0,10 · H 30' | 1.411 | −0,009 | −0,029 | −4,59 | −1,7 |
| c 0,10 · H 60' | 1.411 | −0,005 | −0,025 | −2,90 | −1,4 |
| c 0,10 · H 120' | 1.412 | −0,000 | −0,021 | −1,81 | −1,3 |
| c 0,25 · H 30' | 562 | +0,001 | −0,021 | −1,61 | −1,2 |
| c 0,25 · H 60' | 562 | +0,012 | −0,010 | −0,60 | −0,4 |
| c 0,25 · H 120' | 562 | +0,014 | −0,008 | −0,39 | −0,7 |

- **Dopo 3 minuti il prezzo non prosegue**: il dato è già nei prezzi (coerente con Andersen et al. 2003: l'aggiustamento avviene nei primissimi minuti). Solo le reazioni grandi (c = 0,25) lasciano un lordo di +0,01 z, cioè meno di un terzo dei costi.
- Nessuno strumento si salva da solo. Il migliore (US100, c 0,25, H 60') ha +0,04 z con t 1,27 su 140 trade: compatibile col caso.
- **Gli orari sono giusti**: il 72% degli eventi supera la soglia di reazione; il replicatore ha verificato che il picco di movimento cade esattamente al minuto T su tutti i feed, sia con l'ora legale sia senza.

## 2. S2 — reversione dopo le aste di chiusura [BACKTEST]
| Configurazione | Giorni | Lordo (z) | Netto base (z) | t |
|---|---|---|---|---|
| USA c 0 · X1 | 1.615 | −0,006 | −0,025 | −7,58 |
| USA c 0 · X2 | 1.267 | +0,007 | −0,025 | −1,76 |
| USA c 0,10 · X1 | 1.223 | −0,006 | −0,027 | −5,50 |
| USA c 0,10 · X2 | 971 | +0,019 | −0,015 | −0,80 |
| Europa c 0 · X1 | 1.631 | −0,006 | −0,029 | −6,50 |
| Europa c 0 · X2 | 1.286 | −0,025 | −0,060 | −3,95 |
| Europa c 0,10 · X1 | 784 | −0,008 | −0,032 | −4,26 |
| Europa c 0,10 · X2 | 600 | −0,010 | −0,049 | −1,87 |

- **Nessuna reversione dopo l'asta**: il lordo è nullo o leggermente nel verso della prosecuzione, coerente con il dossier («gli estremi intraday continuano»).
- Il **placebo** un'ora prima dell'asta dà lo stesso valore (USA −0,004 z, Europa −0,002 z): non c'è nulla di specifico dell'asta.
- Nei giorni di asta pesante (scadenze trimestrali) l'Europa ha un lordo di +0,024/+0,036 z (23-32 giorni), gli USA −0,054/−0,076: nessun meccanismo confermato.
- Costi: sui CFD europei e su US2000 lo spread dopo la chiusura è di 2-4 bps, un multiplo di qualunque effetto plausibile.

## 3. Doppio controllo
- **Repliche cieche** (codice scritto da zero dal solo protocollo e dalla tabella dei costi congelata):

  | Test | Netto z (mio / replica) | t (mio / replica) |
  |---|---|---|
  | S1 c 0,10 H 60 | −0,0253 / −0,0247 | −2,90 / −2,84 |
  | S2 USA c 0 X1 | −0,0253 / −0,0254 | −7,58 / −7,61 |

  - Stesso verdetto su tutti i 14 test.
  - Le piccole differenze di n (da 0 a 11 eventi o giorni) vengono dai casi limite dell'addendum 1 e dai calendari.
- **Revisione avversaria del codice**: fusi, calendario, prezzi, segni, regole d'ingresso e d'uscita, costi, aggregazione e statistiche sono corretti. Solo difetti minori, che toccano meno dell'1-2% delle osservazioni e non possono nascondere un effetto.
  - Anche **a costi zero** il t lordo massimo è +0,72 (S1) e +1,00 (S2), contro soglie BH di t ≈ 2,1-2,2.
  - Con il segno invertito nessun test supera la soglia.
- **Controllo a mano su righe grezze**: 30 casi (16 trade S1, 13 trade S2, 2 sigma e diversi non-trade) ricostruiti con grep/awk. Tutti esatti.

## 3-bis. Addendum 2 «dopo i numeri»: tre anomalie di fuso nei dati sigillati
Il controllo a mano ha trovato tre periodi in cui l'ora server non è quella dichiarata (`addendum2_fusi_anomali.py`, `risultati/ADDENDUM2_SENSIBILITA_FUSI.csv`):
1. **Pepperstone** (XAU, NAS100, US2000, US30, UK100) in **NY+8 da novembre 2017 a febbraio 2018**. L'ho verificato in modo indipendente sul picco del tick volume all'apertura USA: 19-22 giorni al mese in NY+8, nessuno dopo il marzo 2018. I feed FTMO e i Pepperstone dal 2020 sono puliti.
2. **GBPUSD FTMO in UTC+1** dall'08/02 al 20/09/2019.
3. **Forex FTMO in NY+7** dal 30/10 al 02/11/2017 (invece che nell'ora di Atene).

Senza i trade colpiti **tutti i 14 test restano NULLI**: la variazione maggiore è USA c 0,10 X2, da −0,015 a −0,004 z (t −0,22). Anche **H1** resta bocciata: la pendenza A1 senza quei giorni passa da +0,053 a +0,118, ancora più lontana dall'ipotesi.

Queste finestre valgono come **trappole permanenti**: S3 le esclude prima dei numeri. Il FTSE (F3) e l'event study usavano Pepperstone nel 2017-2018: l'inverno 2017-18 è circa il 5% del loro campione e nessun verdetto era al limite.

## 4. Cosa insegna
1. I **dati macro** sono già nei prezzi dopo 3 minuti; ciò che resta non paga gli spread FTMO.
2. Sulle **aste di chiusura** i CFD seguono i futures, e intorno all'asta non c'è pressione che rientri.
3. **Nuova trappola** (valida anche per i backtest con il calendario MQL5): il calendario esportato è in **UTC+3 fisso**. In inverno ogni evento risulta un'ora dopo il vero. Senza la correzione S1 avrebbe misurato, per un terzo degli eventi, l'apertura cassa delle 09:30.
