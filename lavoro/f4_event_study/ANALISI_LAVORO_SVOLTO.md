# ANALISI DEL LAVORO SVOLTO (F0 → F3) — cosa abbiamo imparato
*20/10/2026. Tutti i numeri vengono dai rapporti F0 e F3, controllati due volte.*

## 1. Sulla strategia del video
1. **La Regola 2** (prezzo ≥ k ATR sotto la media a 40 ore con RSI < 35) **non ha edge nemmeno lordo**: A5 dà −0,010 R lordo e −0,034 R netto su 359 trade; su FTMO −0,074 R. Nessuna variante (k = 2/3/4, uscita a 24 ore o a 24 barre, barre cash o CFD) supera lo zero netto.
2. **I 1.908 trade dichiarati si spiegano** entrando a **ogni** barra che soddisfa la Regola 2, con posizioni sovrapposte: 215-259 trade l'anno contro ~218 del video. Anche così la media è **−0,06 R** (Pepperstone) e **−0,10 R** (FTMO). Il +312,9% del video non è riproducibile con dati reali e costi.
3. **La Regola 1** (lunedì sotto l'apertura, RSI < 40) è l'unica con segno positivo:
   - +0,11 R con uscita a 24 ore, +0,26 R con uscita a 24 barre;
   - è rara: 12,7 trade l'anno;
   - non supera la correzione per test multipli.
   - Il confronto lunedì contro martedì-venerdì (+0,33 R, t 2,26) è un **indizio** di struttura settimanale, non una strategia. L'event study lo verifica in modo generale (famiglia E).
4. **Il «Monday dip» su DAX, S&P 500 e Nasdaq non si conferma**: GER40 −0,07 R, US500 +0,15 R, US100 +0,07 R, tutti con t < 1,1.

## 2. Sui dati (trappole trovate, da ricordare in ogni ricerca futura)
| Trappola | Numeri | Conseguenza |
|---|---|---|
| Storici FTMO degli indici M1 veri solo dal 14/09/2021 (GER40 dal 28/12/2021): prima ci sono D1 e H1 travestiti | F0 §2 | su FTMO bastano ~2,3 anni; per l'inferenza serve Pepperstone (dal 2017) |
| GER40 e US500 Pepperstone sono **M5 travestito** fino al 10/06/2020 e al 10/07/2020 | 288 barre al giorno | il mio primo audit non l'aveva visto: il criterio corretto è il passo modale fra barre |
| Il campo SPREAD è il **minimo** del minuto | F0 §5 | lo spread vero è più alto: stress +50% obbligatorio |
| **Stacco dei dividendi del FTSE 100 di giovedì** | apertura del giovedì −0,136% in media contro ~0 negli altri giorni (t −4,0); il DAX, total return, non ce l'ha | ogni strategia long multi-giorno su UK100 va simulata con l'**accredito del dividendo** del broker (se FTMO lo applica) e con lo **swap**. Sulle celle F3 l'effetto è piccolo (+0,01/+0,03 R) e nessun verdetto cambia |
| Fuso NY+7 confermato su **tutti** i 16 file (indici, oro, argento, petrolio, VIX, dollaro) | F0 §4 e `fuso_spread_altri.py` | orari derivati sempre dall'ora locale della borsa |
| Mezze sedute LSE (ultimo giorno lavorativo prima di Natale e di Capodanno, alle 12:30) e NYSE (alle 13:00) | — | gestite nelle chiusure giornaliere |

## 3. Sul metodo
1. **La potenza statistica è il vero collo di bottiglia**, non i costi:
   - su UK100 con stop di 2-2,5 ATR H1 i costi valgono il 3-4% di R (stress 8-11%);
   - una regola da 13 trade l'anno non si può confermare in 1-3 anni di dati nuovi.
   - **Le prossime ipotesi devono avere ≥ 100 trade l'anno**, oppure essere panieri di strumenti, oppure effetti grandi per evento.
2. **La replica cieca e la revisione avversaria funzionano**:
   - hanno confermato i numeri (trade per trade);
   - hanno trovato 12 imperfezioni piccole, senza nessuna conseguenza sui verdetti;
   - le teniamo come standard.
3. **2017-2023 è ormai «visto»**: chi esplora oggi su quei dati (event study) può confermare **solo** su 2024 (validazione) + 2025-2026 (hold-out), cioè circa 2,8 anni. Per questo il piano dell'event study chiede effetti frequenti o in paniere.
4. **Coerenza con la tua lezione** («robusti solo la prosecuzione dopo flussi/livelli strutturali e la reversione dopo un flusso a orario noto»): la strategia del video era reversione **senza** flusso identificato e il risultato è nullo. La ricerca va spostata su **flussi a data/ora nota** (fine mese, FOMC, scadenze, festivi, report EIA) e su effetti **multi-giorno** documentati in letteratura.
