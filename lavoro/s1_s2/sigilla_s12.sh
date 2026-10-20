#!/bin/bash
# Sigillo dei dati per S1/S2 (20/10/2026, prima dei risultati). scoperta: data < 2024.01.01 (solo i file non gia' sigillati);
# validazione_2024: 2023.11.01 <= data < 2025.01.01 per tutti gli indici di S1/S2. Il 2025-2026 NON viene copiato.
set -e
N=/home/user/dati_m1_nuovi; O=/home/user/dati_m1; OUT=/home/user/dati_s12
mkdir -p $OUT/scoperta $OUT/validazione_2024
for n in "US30 Pepperstone m1" "US2000 m1 Pepperstone" "US2000 m1 FTMO" "FRA40 m1 FTMO"; do
  awk -F'\t' 'NR==1 || $1 < "2024.01.01"' "$N/$n.csv" > "$OUT/scoperta/$n.csv"
  awk -F'\t' 'NR==1 || ($1 >= "2023.11.01" && $1 < "2025.01.01")' "$N/$n.csv" > "$OUT/validazione_2024/$n.csv"
done
for n in "US500 m1 - Pepperstone" "US500 m1 - FTMO" "NAS100 m1 - FTPepperstone" "US100 m1 - FTMO" "GER40 Pepperstone m1" "GER40 FTMO m1" "UK100 Pepperstone m1" "UK100 FTMO m1"; do
  awk -F'\t' 'NR==1 || ($1 >= "2023.11.01" && $1 < "2025.01.01")' "$O/$n.csv" > "$OUT/validazione_2024/$n.csv"
done
chmod 444 $OUT/scoperta/*.csv $OUT/validazione_2024/*.csv
{ echo "SIGILLO S1/S2 - creato $(date -u '+%Y-%m-%d %H:%M:%S UTC')"; cd $OUT; sha256sum scoperta/*.csv validazione_2024/*.csv;
  for f in scoperta/*.csv validazione_2024/*.csv; do echo "$f: $(sed -n 2p "$f" | cut -f1) -> $(tail -1 "$f" | cut -f1)"; done; } > $OUT/SIGILLO.txt
chmod 444 $OUT/SIGILLO.txt; cat $OUT/SIGILLO.txt
