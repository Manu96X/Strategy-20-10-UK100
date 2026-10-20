import pandas as pd, numpy as np
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 200)
X = pd.read_pickle("confronto.pkl")
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
NS = 60_000_000_000
# 1) formula SL in gap: codice min(open, SL-slip) vs protocollo min(open,SL)-slip
X["dR_prot"] = X.R_protocollo - X.R
sl = X[X.tipo == "SL"]
print("== SL: trade con apertura oltre lo stop (gap):", sl.gap_open.sum(), "su", len(sl))
g = sl[sl.gap_open & (X.scenario != "lordo")]
print(g.groupby(["cella", "feed", "scenario"]).agg(n=("R", "size"), dR_medio=("dR_prot", "mean"), dR_min=("dR_prot", "min")).round(4))
for (c, f, s), gg in X[X.scenario != "lordo"].groupby(["cella", "feed", "scenario"]):
    d = gg.R_protocollo.mean() - gg.R.mean()
    if abs(d) > 1e-4: print(f"  effetto sulla media {c} {f} {s}: {gg.R.mean():.5f} -> {gg.R_protocollo.mean():.5f}  (diff {d:+.5f} R)")
# 2) buchi >= 120 minuti dentro la tenuta
b = X[X.buco_max_min >= 120]
print("\n== trade con un buco M1 >= 120 min fra ingresso e uscita:", len(b))
print(b.groupby(["cella", "feed", "scenario"]).size())
print(b[b.scenario == "base"][["cella", "feed", "data_loc", "tipo", "ts_in", "ts_out", "buco_max_min", "R"]].assign(
    ts_in=lambda x: pd.to_datetime(x.ts_in), ts_out=lambda x: pd.to_datetime(x.ts_out)).to_string())
# 3) R1: un trade per lunedi', solo lunedi'
for c in ["A1", "A2", "A3", "A9", "B1", "B2", "B3"]:
    for (f, s), gg in T[T.cella == c].groupby(["feed", "scenario"]):
        dup = gg.data_loc.duplicated().sum(); nonlun = (gg.dow != 0).sum()
        wd = pd.to_datetime(gg.data_loc).dt.weekday.ne(0).sum()
        if dup or nonlun or wd: print("R1 VIOLAZIONE", c, f, s, dup, nonlun, wd)
print("\n== R1: duplicati per lunedi' e giorni non lunedi' controllati (nessuna riga sopra = ok)")
# R1: stessi segnali in tutti gli scenari
for c in ["A1", "A2", "A3", "A9", "B1", "B2", "B3"]:
    for f in ["PEP", "FTMO"]:
        sets = [tuple(T[(T.cella == c) & (T.feed == f) & (T.scenario == s)].ts_in) for s in ["lordo", "base", "stress"]]
        if not (sets[0] == sets[1] == sets[2]): print("R1 ingressi diversi fra scenari", c, f, [len(x) for x in sets])
# 4) R2: una posizione alla volta
for c in ["A4", "A5", "A6", "A7", "A10"]:
    for (f, s), gg in T[T.cella == c].groupby(["feed", "scenario"]):
        gg = gg.sort_values("ts_in"); ov = (gg.ts_in.values[1:] < gg.ts_out.values[:-1]).sum()
        same = (gg.ts_in.values[1:] == gg.ts_out.values[:-1]).sum()
        if ov: print("R2 SOVRAPPOSIZIONE", c, f, s, ov)
        if same and s == "base": print(f"  R2 {c} {f} {s}: rientri nello stesso minuto dell'uscita: {same}")
print("== R2 controllato")
# 5) A8 = A1 + A5
for f in ["PEP", "FTMO"]:
    for s in ["lordo", "base", "stress"]:
        a8 = T[(T.cella == "A8") & (T.feed == f) & (T.scenario == s)].drop(columns="cella").sort_values(["ts_in", "R"]).reset_index(drop=True)
        u = T[T.cella.isin(["A1", "A5"]) & (T.feed == f) & (T.scenario == s)].drop(columns="cella").sort_values(["ts_in", "R"]).reset_index(drop=True)
        print("A8", f, s, len(a8), "=", len(u), "uguali:", a8.equals(u))
# 6) lordo: costi zero
L = T[T.scenario == "lordo"]; print("lordo: max costo_R", L.costo_R.abs().max(), "max swap", L.swap.abs().max(), "max spread", L.spread.abs().max())
# 7) scadenze: uscite TEMPO dopo la scadenza di quanto?
X["ritardo_uscita_min"] = (X.ts_out - X.scad) / NS
t = X[X.tipo == "TEMPO"]
print("TEMPO: ritardo uscita rispetto alla scadenza (min): max", t.ritardo_uscita_min.max(), " >5 min:", (t.ritardo_uscita_min > 5).sum())
print(t[t.ritardo_uscita_min > 5][["cella", "feed", "scenario", "data_loc", "ritardo_uscita_min"]].head(20).to_string())
# 8) uscite CHIUSURA: ultima quotazione e giorno
c = X[X.tipo == "CHIUSURA"]
print("CHIUSURA: giorni della settimana dell'uscita:", pd.to_datetime(c.ts_out).dt.weekday.value_counts().to_dict())
