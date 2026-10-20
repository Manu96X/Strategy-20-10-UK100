# RAPPORTO H1 — «il dollaro segue i metalli con un giorno di ritardo»
*20/10/2026. Protocollo `PROTOCOLLO_H1.md` (commit 854fac8, 15:24 UTC) e codice (commit 684e4d8) pubblicati **prima** dei risultati. Etichette: [BACKTEST] numeri sui dati · [STIMA] derivati.*

## Verdetto: **H1 BOCCIATA**
Il test primario A1 sul campione indipendente è **ROSSO**: la pendenza ha il segno **opposto** a quello previsto. Per la regola di arresto pre-registrata la ricerca su H1 si ferma qui. **Il 2024 resta sigillato** e il 2025-2026 non è mai stato toccato.

## 1. Stadio A — campione indipendente (forex FTMO, mai visto) [BACKTEST]
Giorni d dal 01/02/2017, giorni d+1 fino al 18/04/2019: **535 giorni**.

| Misura | Valore | Atteso se H1 fosse vera |
|---|---|---|
| **A1** pendenza del paniere del dollaro (W1) sul segnale dei metalli | **+0,053 z**, t +1,19, p unilaterale **0,87** | −0,107 (t ≈ −2,4) |
| Strategia W2 (08:20 → 16:00 NY), netto base | **−0,064 z** per trade (t −1,87); lordo −0,037, costi 0,027 | > 0 |
| Strategia W2, netto stress | −0,075 z (t −2,21) | > 0 |
| Strategia W1 (giorno intero, con swap), netto base | −0,078 z (t −1,70); lordo −0,024, costi 0,054 | > 0 |

- **Per coppia**: EURUSD +0,047 · GBPUSD −0,012 · AUDUSD +0,045 · USDJPY −0,005 · USDCHF +0,038 · USDCAD +0,074. Nessuna conferma.
- **Controlli di robustezza**: solo oro +0,042; solo argento +0,056; senza il 2% dei giorni più influenti +0,006; prezzo robusto +0,053; segnale dai metalli FTMO invece che Pepperstone +0,053 (i due segnali hanno correlazione 0,996).
- **Un altro feed lo conferma**: con l'USDX Pepperstone come bersaglio (periodo mai visto, n 529) la pendenza è +0,038 (t +0,82).
- **Potenza** [STIMA]: l'errore standard è ≈ 0,045. La pendenza della scoperta (−0,107) dista 3,6 errori standard dal valore osservato (p ≈ 0,0002). Anche un effetto dimezzato (−0,05) è escluso al livello dell'1%.

## 2. Perché non è un errore di calcolo
1. **Replica cieca** (codice scritto da zero dal solo protocollo, `controllo/`):
   - numeri identici su **535 giorni su 535**: differenza massima 5·10⁻¹⁰ su ogni colonna;
   - stesso verdetto ROSSO (b +0,053, p 0,867).
   - Il replicatore ha anche verificato **in modo indipendente il fuso del forex FTMO**, correlando i rendimenti al minuto di EURUSD con l'USDX a ±1 ora: nel 2018-2019 il server segue l'ora legale europea, come assunto.
2. **Il sistema riproduce la scoperta** (diagnostico A0, sul periodo della scoperta 22/04/2019 → 2023, 1.102 giorni):
   - paniere forex −0,095 z (t −2,77);
   - USDX −0,107 (t −3,13), lo **stesso valore** della scoperta;
   - correlazione fra paniere e USDX 0,92.
   - Quindi definizioni e dati sono giusti, e l'effetto 2019-2023 c'era anche sul forex: **non era un artefatto del CFD USDX**. È **sparito fuori dal periodo in cui era stato trovato**.

## 3. Lettura da quant (addendum «dopo i numeri», descrittivo) [BACKTEST]
Pendenza del paniere forex anno per anno: **2017 +0,03 · 2018 +0,08 · 2019 −0,15 · 2020 −0,01 · 2021 −0,10 · 2022 +0,01 · 2023 −0,18.**
- Il «5 anni su 5» della scoperta (sull'USDX) diventa, sul forex, **3 anni negativi, 2 nulli e 2 positivi**.
- È la firma tipica di un effetto **non stabile**:
  - scelto come il migliore fra 100 regressioni, con il suo «premio del vincitore»;
  - vissuto in un regime (2019-2023), non come una regola del mercato.
- Ripescarlo come «H1 solo dopo il 2019» sarebbe data mining puro: **escluso**.

## 4. Nuove trappole dei dati trovate in F0-bis (valgono per ogni ricerca futura)
| Trappola | Dettaglio |
|---|---|
| **Fuso del forex FTMO** | fino al 2019 l'ora server segue l'ora legale **europea** (ora di Atene): nelle settimane di disallineamento il dato USA delle 08:30 NY cade alle 14:30 server, non alle 15:30. Dal 2021 è NY+7. Il replicatore vede NY+7 già il 9-20/03/2020, quindi il cambio avviene fra novembre 2019 e marzo 2020 |
| **Fuso dell'oro e dell'argento FTMO** | fino al 2019 come il forex (ora europea); i file Pepperstone e l'USDX sono sempre NY+7 |
| Forex FTMO 2019 | ~256 barre con tick volume anomalo e 240-360 con range anomalo per coppia: non spostano i prezzi giornalieri (il prezzo robusto dà lo stesso risultato) |
| Spread del forex FTMO | il campo è il minimo del minuto: EURUSD ha mediana **0,0 pip**. Usati il p75 per ora e un minimo di 0,1 pip; spread più alti dopo le 16:00 NY (ora server 23: p75 0,6-1,3 pip) |
| Calendario economico | **CORRETTO il 20/10/2026 (addendum)**: la colonna `ora_server` è **UTC + 3 ore fisse in tutti gli anni** (l'offset del giorno dell'export), non NY+7. Da ottobre a marzo è sfasata di un'ora rispetto al server FTMO (NFP alle 16:30 invece che alle 15:30). Verificato su NFP, sussidi, ISM e FOMC (`s1_s2/PROTOCOLLO_S1_S2.md` §0). La frase precedente («NY+7 anche prima del 2020») era sbagliata; H1 non usa il calendario, quindi i suoi risultati non cambiano |
| **Fusi anomali (addendum del 20/10/2026, trovati in S1/S2)** | Pepperstone (XAU, XAG, NAS100, US2000, US30, UK100) in NY+8 da novembre 2017 a febbraio 2018; GBPUSD FTMO in UTC+1 dall'08/02 al 20/09/2019; forex FTMO in NY+7 dal 30/10 al 02/11/2017. **Effetto su H1**: senza quei giorni la pendenza A1 passa da +0,053 a +0,118 (n 407): il verdetto non cambia (`s1_s2/addendum2_fusi_anomali.py`) |
