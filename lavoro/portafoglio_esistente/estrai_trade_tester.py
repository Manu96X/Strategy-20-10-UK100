# -*- coding: utf-8 -*-
"""Estrae la lista dei trade dai report del tester MT5 (xlsx) di ORB e IM forniti da Manu (20/10/2026).
Tabella 'Affari': ogni ingresso ('in') e' accoppiato all'uscita ('out') successiva dello stesso volume (FIFO).
R = profitto netto (profitto + commissione + swap) / rischio nominale del report (ORB: InpRiskFixedUSD; IM: InpRiskDollars).
Uso: python3 -I estrai_trade_tester.py <xlsx> <nome> <out_csv>"""
import sys, re
import openpyxl, pandas as pd
f, nome, out = sys.argv[1:4]
rows = list(openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
testo = {str(c) for r in rows[:120] if r for c in r if c is not None}
rischio = None
for t in testo:
    m = re.match(r"(InpRiskFixedUSD|InpRiskDollars)=([\d.]+)", t)
    if m: rischio = float(m.group(2))
i0 = next(i for i, r in enumerate(rows) if r and r[0] == "Affari")
hdr = [c for c in rows[i0 + 1] if c is not None]
deals = []
for r in rows[i0 + 2:]:
    v = [c for c in r]
    if not v or v[0] is None or not re.match(r"\d{4}\.\d{2}\.\d{2}", str(v[0])): continue
    deals.append(v[:len(hdr)])
D = pd.DataFrame(deals, columns=hdr)
D.columns = ["ora", "affare", "simbolo", "tipo", "direzione", "volume", "prezzo", "ordine", "commissione", "swap", "profitto", "saldo", "commento"][:len(D.columns)]
D = D[D.direzione.isin(["in", "out"])].reset_index(drop=True)
aperti, trade = [], []
for _, d in D.iterrows():
    if d.direzione == "in":
        aperti.append(d)
    else:
        a = next(x for x in aperti if float(x.volume) == float(d.volume)); aperti.remove(a)
        netto = float(d.profitto) + float(d.commissione) + float(a.commissione) + float(d.swap)
        trade.append(dict(strategia=nome, ingresso_srv=a.ora, uscita_srv=d.ora, verso=("long" if a.tipo == "buy" else "short"),
                          lotti=float(a.volume), prezzo_in=float(a.prezzo), prezzo_out=float(d.prezzo),
                          profitto=float(d.profitto), commissioni=float(d.commissione) + float(a.commissione), swap=float(d.swap),
                          netto_usd=netto, R=netto / rischio if rischio else None, uscita=str(d.commento), commento_in=str(a.commento)))
T = pd.DataFrame(trade)
assert not aperti, "ingressi senza uscita"
T.to_csv(out, sep=";", decimal=",", index=False)
print(nome, "trade", len(T), "rischio", rischio, "dal", T.ingresso_srv.min(), "al", T.uscita_srv.max(),
      "netto $", round(T.netto_usd.sum(), 2), "R medio", round(T.R.mean(), 4))
