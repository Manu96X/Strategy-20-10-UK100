# Storici MT5 compressi

Ogni storico e' un archivio `tar.gz`. Gli archivi troppo grandi per GitHub
sono spezzati in parti numerate (`.part01`, `.part02`, ...).

## Come aprirli

Archivio in un pezzo solo:

```bash
tar -xzf NOME.tar.gz
```

Archivio spezzato in parti:

```bash
cat NOME.tar.gz.part* > NOME.tar.gz && tar -xzf NOME.tar.gz
```

Le parti sono numerate con due cifre, quindi `part*` in bash le espande gia'
nell'ordine giusto.

## Verificare che i dati siano intatti

`SHA256.txt` contiene l'impronta di ogni CSV originale, calcolata su Windows
prima della compressione. Dopo aver estratto:

```bash
sha256sum -c SHA256.txt
```

Deve rispondere `OK` per ogni file. Se risponde `FAILED`, il file e'
corrotto e non va usato per i backtest.

## Formato dei CSV

Export standard MT5, separatore TAB:

```
<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>
```

`<VOL>` e' 0 su tutte le righe sui CFD. `<SPREAD>` e' in punti indice.
Gli orari sono ora del server del broker, non ora locale.

## Caricare in pandas

```python
import pandas as pd
df = pd.read_csv("NOME.csv", sep="\t")
df.columns = [c.strip("<>").lower() for c in df.columns]
df["ts"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M:%S")
```

Un anno di barre M1 sono circa 350.000 righe; un file da 8 anni chiede circa
2,5 GB di RAM se caricato tutto insieme. Con poca memoria usa `chunksize`
oppure filtra in lettura.