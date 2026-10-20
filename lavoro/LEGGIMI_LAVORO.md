# lavoro/ — cartella di lavoro (l'unica modificata)

| Cartella | Contenuto |
|---|---|
| `f0/` | **F0**: `RAPPORTO_F0.md` (inventario, impronte, audit, fuso, spread, ATR) e gli script che lo producono; `risultati/` CSV e controllo indipendente |
| `f1/` | `SPECIFICA_STRATEGIA_UK100.md`: la strategia ricavata da PDF, 31 immagini e 6 papers |
| `f2/` | `PROTOCOLLO_F2_BOZZA.md`: protocollo pre-registrato, **da confermare** |
| `comune/` | `barre.py`: caricamento M1, ora locale di borsa, barre H1 cash/CFD, RSI e ATR di Wilder, SMA |

## Riprodurre la F0
I dati non sono in git: si estraggono fuori dalla repository (vedi `LEGGIMI.md` in radice) e si verificano con `sha256sum -c SHA256.txt`.
```bash
mkdir -p ~/dati_m1 && cd ~/dati_m1   # estrarre qui gli archivi
cd <repo>/lavoro/f0
python3 -I audit_m1.py ~/dati_m1 risultati
python3 -I fuso_e_spread.py ~/dati_m1 risultati
python3 -I controllo_indipendente_f0.py ~/dati_m1 ../../SHA256.txt risultati
python3 -I genera_rapporto_f0.py <repo>
```
Il calcolo dell'ATR H1 per anno (`risultati/ATR_H1_per_anno_UK100.csv`) è in `atr_h1_uk100.py`.
