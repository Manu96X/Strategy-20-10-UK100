# ADDENDUM AL PROTOCOLLO F2 — 20/10/2026, **DOPO I NUMERI** della scoperta

Il protocollo `PROTOCOLLO_F2_BOZZA.md` resta valido. Queste modifiche sono state scritte **dopo** aver visto i risultati della scoperta, e lo dichiaro. Nascono tutte dal doppio controllo (`lavoro/f3/controllo/ESITO_REVISIONE.md`), non dalla ricerca di un risultato migliore. Ognuna è neutra o più prudente, e nessuna cambia di colore una cella.

| # | Modifica | Perché | Effetto |
|---|---|---|---|
| 1 | Stop in gap: prezzo = `min(open, SL) − slippage` | allinea il codice al testo del §3 (prima `min(open, SL − slippage)`, più ottimista) | ≤ 0,0007 R sulle medie |
| 2 | Sessione cash troncata nei giorni di chiusura anticipata: LSE 24 e 31/12 alle 12:30; NYSE alle 13:00 (elenco ufficiale 2017-2025) | la sessione cash quel giorno finisce davvero prima | da −0,0025 a +0,0043 R, segno misto |
| 3 | t raggruppato per giorno FTMO con correzione **CR1**: × √(G/(G−1)), con G = numero di giorni | stimatore standard e più prudente | t −0,6% |
| 4 | Bootstrap per giorno con **100.000** repliche, e quota delle repliche ≤ 0 riportata | toglie la dipendenza dal seme | solo l'intervallo di confidenza |
| 5 | Placebo P2 per **tutte** le celle R1 di sessione (A1, A2, A3, B1-B3) | il §6 lo chiede («solo R1 e B1-B3») | informativo, non entra nel §7 |
| 6 | Fascia gialla di A3: 1,0 ≤ t < 2,5 (la soglia verde di A3 è 2,5) | colma un vuoto del testo | nessuno (A3 ha t 0,44) |
| 7 | Gli anni parziali contano nella quota di anni positivi se hanno almeno 6 mesi di dati (il 2017 ne ha 7) | colma un vuoto del testo | nessuno |
| 8 | **Lettura della soglia GIALLO, aperta** — L1: una deroga alla volta (t fra 1 e 2, **oppure** placebo superato solo prima di Benjamini-Hochberg); L2: le due deroghe possono valere insieme | il testo del §7 non copre il caso di una cella con entrambe le deroghe | cambia solo A2 (L1 rossa, L2 gialla). **Decide Manu**; in entrambi i casi A2 va avanti solo con il suo via esplicito |

Non modificato, deliberatamente: i buchi di dati di 2 ore o più dentro una tenuta **non** sono trattati come chiusure, perché non sono noti in anticipo (verificato dal giudice).
