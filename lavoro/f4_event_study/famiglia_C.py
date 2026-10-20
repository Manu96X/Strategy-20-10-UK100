# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA C: scadenza delle opzioni (Stivers-Sun 2013) e festivi
(Ariel 1990; Kim-Park 1994). 20 test esatti = 5 test x 4 indici (US500, US100, GER40, UK100), feed d'inferenza
(Pepperstone) con concordanza sul feed FTMO.

Definizioni (calendario = giorni feriali meno i festivi della borsa dell'indice, EC.festivi(cal)):
  OPEX     = EC.terzo_venerdi(anno, mese); se non e' giorno di trading del calendario, il giorno di trading precedente.
  C1       ingresso: chiusura dell'ultimo giorno di trading <= terzo venerdi' - 7 giorni (il "venerdi' prima" del piano);
           uscita: chiusura del giorno OPEX. Tutti i 12 mesi.
  C2       ingresso: chiusura del giorno OPEX; uscita: chiusura dell'ultimo giorno di trading <= terzo venerdi' + 7 giorni.
  C3       come C1 ma solo marzo, giugno, settembre, dicembre.
           Pool placebo e benchmark C1-C3: tutte le finestre di 5 giorni di trading (del calendario) con entrambi gli
           estremi presenti nei dati.
  C4       pre-festivo: giorni di trading d tali che il primo giorno feriale dopo d e' un festivo della borsa;
           finestra: chiusura del giorno di trading prima di d -> chiusura di d.
  C5       post-festivo: primo giorno di trading dopo quel festivo; finestra: chiusura di d -> chiusura del post-festivo.
           Pool placebo e benchmark C4-C5: tutte le finestre di 1 giorno di trading (del calendario).
  Il "giorno di trading" e' definito dal calendario della borsa, non dalle righe presenti: se un estremo della finestra
  manca nei dati (buco del feed) l'evento e' escluso (non spostato), e le finestre del pool che scavalcano un giorno
  di trading mancante sono escluse.
  z = ln(P_uscita/P_ingresso) / sig_in, sig_in = dev.std dei 20 rendimenti fino al giorno d'ingresso INCLUSO.
  media anomala = media z eventi - media z di tutte le finestre della stessa lunghezza (stesso strumento/feed).
  p_primario = EC.p_placebo bilaterale, 2000 estrazioni dal pool di finestre della stessa lunghezza i cui anni
  d'ingresso sono fra gli anni degli eventi. t = EC.t_cluster per data dell'evento.
Solo dati di scoperta sigillati (< 01/01/2024) tramite eventi_comune.
"""
import sys
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f4_event_study")
import numpy as np
import pandas as pd
import eventi_comune as EC

OUT = "/home/user/Strategy-20-10-UK100/lavoro/f4_event_study/risultati/famiglia_C.csv"
NREP = 2000
FINE = pd.Timestamp("2023-12-29").date()
INDICI = ["US500", "US100", "GER40", "UK100"]
GG = pd.Timedelta(days=1)


class Serie:
    """Tabella giornaliera del feed + calendario di trading della borsa."""

    def __init__(self, s, f):
        self.s, self.f = s, f
        d = EC.giornaliero(s, f).copy().reset_index(drop=True)
        d["sig_in"] = d.r.rolling(20, min_periods=20).std()     # 20 rendimenti FINO al giorno incluso
        d["ora_C"] = pd.to_datetime(d.ts_C).dt.hour
        self.d = d
        self.fest = EC.festivi(EC.STRUMENTI[s]["cal"])
        cal = pd.bdate_range("2016-12-01", FINE)
        self.cal = [x.date() for x in cal if x.date() not in self.fest]
        self.pos = {x: i for i, x in enumerate(self.cal)}
        self.riga = {x: i for i, x in enumerate(d.data)}
        self.primo = d.data.iloc[0]

    def td_le(self, x):
        """ultimo giorno di trading del calendario <= x"""
        x = pd.Timestamp(x).date()
        while x.weekday() >= 5 or x in self.fest: x = (pd.Timestamp(x) - GG).date()
        return x

    def td_succ(self, x, k=1):
        p = self.pos[x] + k
        return self.cal[p] if 0 <= p < len(self.cal) else None

    def finestra(self, a, b):
        """(z, W, riga_a, riga_b) per la finestra chiusura a -> chiusura b; None se non valida."""
        if a is None or b is None or a not in self.riga or b not in self.riga: return None
        ia, ib = self.riga[a], self.riga[b]
        sg = self.d.sig_in.values[ia]
        if not np.isfinite(sg) or ib <= ia: return None
        W = np.log(self.d.C.values[ib] / self.d.C.values[ia])
        return W / sg, W, ia, ib

    def pool(self, L):
        """tutte le finestre di L giorni di trading del calendario con estremi presenti: (z, anno d'ingresso)."""
        z, an = [], []
        for i in range(len(self.cal) - L):
            r = self.finestra(self.cal[i], self.cal[i + L])
            if r is None: continue
            z.append(r[0]); an.append(self.cal[i].year)
        return np.array(z), np.array(an)


def eventi_opex(S, quale):
    """Lista di (data_ingresso, data_uscita, anno_evento, opex, terzo_venerdi)."""
    ev = []
    for y in range(2017, 2024):
        for m in range(1, 13):
            if quale == "C3" and m not in (3, 6, 9, 12): continue
            tf = EC.terzo_venerdi(y, m)
            opex = S.td_le(tf)
            if quale in ("C1", "C3"):
                a, b = S.td_le(pd.Timestamp(tf) - 7 * GG), opex
            else:
                a, b = opex, S.td_le(pd.Timestamp(tf) + 7 * GG)
            if a < S.primo or b > FINE: continue
            ev.append((a, b, y, opex, tf))
    return ev


def eventi_festivi(S, quale):
    """C4: (giorno prima di d, d); C5: (d, primo giorno di trading dopo il festivo). Con anno dell'evento e festivo."""
    ev = []
    for d in S.cal:
        nd = pd.Timestamp(d) + GG
        while nd.weekday() >= 5: nd += GG
        nd = nd.date()
        if nd not in S.fest: continue
        if quale == "C4":
            a, b = S.td_succ(d, -1), d
            anno = d.year
        else:
            a, b = d, S.td_succ(d, 1)
            if b is None: continue
            anno = b.year
        if a is None or a < S.primo or b > FINE: continue
        ev.append((a, b, anno, nd, None))
    return ev


def analisi(s, f, quale, seed):
    S = Serie(s, f)
    ev = eventi_opex(S, quale) if quale in ("C1", "C2", "C3") else eventi_festivi(S, quale)
    L = 5 if quale in ("C1", "C2", "C3") else 1
    righe, esclusi = [], []
    for a, b, y, x, tf in ev:
        r = S.finestra(a, b)
        if r is None: esclusi.append((str(a), str(b))); continue
        righe.append((r[0], r[1], r[2], r[3], y, a, b, x, S.pos[b] - S.pos[a]))
    z = np.array([q[0] for q in righe]); W = np.array([q[1] for q in righe])
    ie = np.array([q[2] for q in righe]); iu = np.array([q[3] for q in righe]); anni = np.array([q[4] for q in righe])
    lung = np.array([q[8] for q in righe])
    zp, ap = S.pool(L)
    bench = zp.mean(); anom = z.mean() - bench
    p = EC.p_placebo(z.mean(), zp[np.isin(ap, np.unique(anni))], len(z), NREP, seed)
    date_ev = S.d.data.values[iu]
    t = EC.t_cluster(z, date_ev); t_an = EC.t_cluster(z - bench, date_ev)
    ya = pd.Series(z - bench).groupby(anni).agg(["mean", "size"])
    ya2 = ya[ya["size"] >= 2]
    quota = float((np.sign(ya2["mean"]) == np.sign(anom)).mean()) if len(ya2) else np.nan
    verso = 1.0 if anom > 0 else -1.0
    d = S.d; pe, pu = d.C.values[ie], d.C.values[iu]
    notti = np.array([(d.data.values[j] - d.data.values[i]).days for i, j in zip(ie, iu)])
    net = {}
    for scen in ("base", "stress"):
        v = [(verso * (pu[k] - pe[k]) - EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]], notti[k], scen))
             / (d.sig_in.values[ie[k]] * pe[k]) for k in range(len(ie))]
        net[scen] = float(np.mean(v))
    costo_med_z = float(np.mean([EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]], notti[k], "base")
                                 / (d.sig_in.values[ie[k]] * pe[k]) for k in range(len(ie))]))
    return dict(n=len(z), media_z=float(z.mean()), media_anomala=float(anom), bps=float(W.mean() * 1e4), bench=float(bench),
                t=t, t_anomala=t_an, p=p, quota=quota, anni_validi=len(ya2),
                eventi_anno=len(z) / len(np.unique(anni)), netto_base=net["base"], netto_stress=net["stress"],
                costo_med_z=costo_med_z, per_anno=ya2["mean"].round(3).to_dict(),
                n_anno=ya["size"].to_dict(), pool_n=len(zp), esclusi=esclusi, lung=pd.Series(lung).value_counts().to_dict(),
                primo=d.data.values[ie[0]], ultimo=d.data.values[iu[-1]], righe=righe, S=S, zp=zp,
                quota_pos=float((z > 0).mean()), mediana_z=float(np.median(z)))


DESCR = {"C1": "chiusura ultimo TD <= 3o venerdi-7 -> chiusura OPEX (12 mesi); pool finestre 5 TD",
         "C2": "chiusura OPEX -> chiusura ultimo TD <= 3o venerdi+7; pool finestre 5 TD",
         "C3": "come C1 solo mar/giu/set/dic; pool finestre 5 TD",
         "C4": "pre-festivo: chiusura TD prima di d -> chiusura d (d = TD con primo feriale successivo festivo); pool finestre 1 TD",
         "C5": "post-festivo: chiusura d pre-festivo -> chiusura primo TD dopo il festivo; pool finestre 1 TD"}


def main():
    righe = []; seed = 3000; dettagli = {}
    for quale in ["C1", "C2", "C3", "C4", "C5"]:
        for s in INDICI:
            seed += 1
            f = EC.FEED_INFERENZA[s]
            r = analisi(s, f, quale, seed)
            c = analisi(s, "FTMO", quale, seed + 500)
            dettagli[(quale, s)] = (r, c)
            righe.append(dict(test_id=f"{quale}_{s}", strumento=s, feed=f, n=r["n"], media_z=r["media_z"],
                              media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"], t_anomala=r["t_anomala"],
                              p_primario=r["p"], quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"],
                              eventi_anno=r["eventi_anno"], netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                              conc_ftmo_media=c["media_anomala"], conc_ftmo_n=c["n"], conc_ftmo_p=c["p"],
                              benchmark_z=r["bench"], costo_medio_base_z=r["costo_med_z"],
                              periodo=f"{r['primo']}..{r['ultimo']}",
                              note=(f"{DESCR[quale]}; bench={r['bench']:.4f}; pool={r['pool_n']}; lunghezze TD={r['lung']}; "
                                    f"quota z>0={r['quota_pos']:.3f}; mediana z={r['mediana_z']:.3f}; "
                                    f"esclusi={r['esclusi']}; anomala per anno={r['per_anno']}; "
                                    f"FTMO p={c['p']:.3f} t={c['t']:.2f}")))
            print(righe[-1]["test_id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in righe[-1].items()
                                         if k in ["n", "media_z", "media_anomala", "bps", "t", "p_primario",
                                                  "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z",
                                                  "conc_ftmo_media", "conc_ftmo_n", "costo_medio_base_z"]})
            print("    per anno", r["per_anno"], "n/anno", r["n_anno"], "esclusi", r["esclusi"], "lung", r["lung"])
    out = pd.DataFrame(righe)
    assert len(out) == 20 and out.test_id.is_unique
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("scritto", OUT, len(out))
    return dettagli


if __name__ == "__main__":
    main()
