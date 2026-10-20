# -*- coding: utf-8 -*-
"""Crea copie TRONCATE degli storici per una fase (scoperta: righe < 2024-01-01; validazione: < 2025-01-01).
Nessuna posizione resta aperta a fine anno (chiusura prima dei weekend e dei festivi), quindi il taglio
netto all'1/1 non perde uscite. Sola lettura sugli originali. Scrive SHA256 e righe di ogni copia.
Uso: python3 -I sigilla_dati.py <cartella_originali> <cartella_destinazione> <data_taglio AAAA.MM.GG>"""
import sys, os, hashlib
FILES = ["UK100 FTMO m1", "UK100 Pepperstone m1", "GER40 FTMO m1", "GER40 Pepperstone m1",
         "US500 m1 - FTMO", "US500 m1 - Pepperstone", "US100 m1 - FTMO", "NAS100 m1 - FTPepperstone"]
src, dst, taglio = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(dst, exist_ok=True)
log = []
for f in FILES:
    n = 0; ultima = ""
    with open(os.path.join(src, f + ".csv"), encoding="utf-8", newline="") as fi, \
         open(os.path.join(dst, f + ".csv"), "w", encoding="utf-8", newline="") as fo:
        fo.write(fi.readline())
        for riga in fi:
            if riga[:10] >= taglio: break
            fo.write(riga); n += 1; ultima = riga[:16]
    h = hashlib.sha256(open(os.path.join(dst, f + ".csv"), "rb").read()).hexdigest()
    os.chmod(os.path.join(dst, f + ".csv"), 0o444)
    log.append(f"{h}  {f}.csv  righe={n}  ultima={ultima}")
open(os.path.join(dst, "SIGILLO.txt"), "w").write(f"taglio < {taglio}\n" + "\n".join(log) + "\n")
print("\n".join(log))
