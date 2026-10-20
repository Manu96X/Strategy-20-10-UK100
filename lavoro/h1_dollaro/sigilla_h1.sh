#!/bin/bash
# Sigillo dei dati per H1 (20/10/2026, prima di qualunque risultato su forex e 2024).
# scoperta: righe con data < 2024.01.01 ; validazione_2024: 2023.11.01 <= data < 2025.01.01 (con riscaldamento).
# Il 2025-2026 (hold-out) NON viene copiato. Gli originali non vengono toccati.
set -e
SRC_FX=/home/user/dati_m1_nuovi; SRC_OLD=/home/user/dati_m1; OUT=/home/user/dati_h1
mkdir -p $OUT/scoperta $OUT/validazione_2024
for p in EURUSD GBPUSD AUDUSD USDJPY USDCHF USDCAD; do
  f="$SRC_FX/$p m1 FTMO.csv"
  awk -F'\t' 'NR==1 || $1 < "2024.01.01"' "$f" > "$OUT/scoperta/$p m1 FTMO.csv"
  awk -F'\t' 'NR==1 || ($1 >= "2023.11.01" && $1 < "2025.01.01")' "$f" > "$OUT/validazione_2024/$p m1 FTMO.csv"
done
for n in "XAU-USD Pepperstone m1" "XAG-USD Pepperstone m1" "USDX pepperstone m1" "XAU-USD FTMO m1" "XAG-USD FTMO m1"; do
  awk -F'\t' 'NR==1 || $1 < "2024.01.01"' "$SRC_OLD/$n.csv" > "$OUT/scoperta/$n.csv"
  awk -F'\t' 'NR==1 || ($1 >= "2023.11.01" && $1 < "2025.01.01")' "$SRC_OLD/$n.csv" > "$OUT/validazione_2024/$n.csv"
done
chmod 444 $OUT/scoperta/*.csv $OUT/validazione_2024/*.csv
{ echo "SIGILLO H1 - creato $(date -u '+%Y-%m-%d %H:%M:%S UTC')"; cd $OUT; sha256sum scoperta/*.csv validazione_2024/*.csv;
  for f in scoperta/*.csv validazione_2024/*.csv; do echo "$f: $(sed -n 2p "$f" | cut -f1) -> $(tail -1 "$f" | cut -f1)"; done; } > $OUT/SIGILLO.txt
chmod 444 $OUT/SIGILLO.txt
cat $OUT/SIGILLO.txt
