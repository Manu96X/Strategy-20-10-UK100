# -*- coding: utf-8 -*-
"""Copia sigillata (< 2024-01-01) di DXY FTMO m1, letta in streaming dall'archivio: le righe >= taglio non vengono mai scritte
(stessa logica di sigilla_tutti.py). Uso: tar -xzOf archivio | python3 -I sigilla_dxy.py <file_uscita>"""
import sys, hashlib
out = sys.argv[1]; taglio = "2024.01.01"; n = 0; ultima = ""
with open(out, "w", encoding="utf-8", newline="") as fo:
    fo.write(sys.stdin.readline())
    for riga in sys.stdin:
        if riga[:10] >= taglio: break
        fo.write(riga); n += 1; ultima = riga[:16]
print(hashlib.sha256(open(out, "rb").read()).hexdigest(), n, ultima)
