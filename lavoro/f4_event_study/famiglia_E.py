# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA E: lunedi' in calo -> recupero
(French 1980; Connors "Turnaround Tuesday"). 24 test esatti. Solo dati di scoperta sigillati (< 01/01/2024)
tramite eventi_comune.

E1 (10 strumenti): lunedi' di trading (dow 0) con r_lunedi' < 0 (chiusura sotto la chiusura della riga di trading
    precedente); finestra chiusura del lunedi' -> chiusura del giorno di trading successivo, che deve essere il
    martedi' di calendario (lunedi' + 1), altrimenti l'evento salta. Pool placebo: tutte le finestre di 1 giorno
    di trading (riga j -> riga j+1) dello stesso strumento/feed, stessi anni degli eventi.
E2 (10 strumenti): stessa condizione; uscita alla chiusura del secondo giorno di trading successivo, che deve
    essere il mercoledi' (piano: "martedi' + mercoledi'": riga +1 = lunedi'+1 e riga +2 = lunedi'+2).
    Pool placebo: tutte le finestre di 2 giorni di trading (riga j -> riga j+2).
E3 (4 indici, test GIA' VISTO, nota §4 del piano): tutti i lunedi' di trading il cui giorno di trading successivo e'
    il martedi'; finestra chiusura cash del lunedi' (C) -> apertura cash del martedi' (O della riga dopo).
    Pool placebo: tutte le notti C_j -> O_{j+1} (qualunque giorno). z con sigma giornaliera.

Convenzioni (piano + istruzioni):
- sigma_ingresso = dev.std dei 20 rendimenti giornalieri FINO al giorno d'ingresso INCLUSO (sig_in);
- z = ln(P_uscita/P_ingresso)/sig_in; benchmark = media z di TUTTE le finestre della stessa lunghezza
  (tutti gli anni del feed); media anomala = media z eventi - benchmark;
- t = EC.t_cluster(z eventi, date eventi) (sugli z grezzi, come da istruzioni); in CSV anche t_anomala;
- p primario = EC.p_placebo(media z eventi, pool stessa lunghezza ristretto agli anni con eventi, n, 2000, seed);
- quota anni: anni con >= 2 eventi, media anomala dell'anno, quota con lo stesso segno della media anomala totale;
- netto (unita' z): verso = segno della media anomala; (verso*(Pu-Pe) - EC.costo_trade(s, Pe, ora server
  dell'M1 d'ingresso, notti di calendario, scenario)) / (sig_in*Pe), media sugli eventi; VIX -> null;
- concordanza: stessi calcoli sul feed FTMO (se esiste e non e' gia' il feed d'inferenza).
E4 DESCRITTIVO (fuori dai 24 test) -> risultati/famiglia_E_descrittivo.csv.
Esecuzione: python3 -I famiglia_E.py
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study')
import eventi_comune as EC

QUI = '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study'
OUT = os.path.join(QUI, 'risultati', 'famiglia_E.csv')
OUT_D = os.path.join(QUI, 'risultati', 'famiglia_E_descrittivo.csv')
ORDINE = ["US500", "US100", "GER40", "UK100", "XAU", "XAG", "BRENT", "USOIL", "VIX", "USDX"]
INDICI = ["US500", "US100", "GER40", "UK100"]
NREP = 2000
GIORNI = ["lun", "mar", "mer", "gio", "ven"]


def tabella(s, f):
    d = EC.giornaliero(s, f).copy().reset_index(drop=True)
    assert pd.to_datetime(d.data).max() < pd.Timestamp("2024-01-01"), "dati oltre il 2023!"
    d["sig_in"] = d.r.rolling(20, min_periods=20).std()          # 20 rendimenti FINO al giorno incluso
    d["ora_C"] = pd.to_datetime(d.ts_C).dt.hour                   # ora server dell'M1 di chiusura
    d["dt"] = pd.to_datetime(d.data)
    return d


# ----------------------------------------------------------------------------------------------- eventi
def eventi(d, quale):
    """Ritorna (ie, iu, pe, pu) = righe e prezzi d'ingresso/uscita degli eventi del test."""
    dt = d.dt.values; n = len(d); ie = []; iu = []
    dow = d.dow.values; r = d.r.values; sg = d.sig_in.values
    for i in range(n):
        if dow[i] != 0 or not np.isfinite(sg[i]): continue
        if i + 1 >= n or (dt[i + 1] - dt[i]) != np.timedelta64(1, "D"): continue      # riga dopo = martedi'
        if quale in ("E1", "E2"):
            if not (np.isfinite(r[i]) and r[i] < 0): continue                          # lunedi' in calo
        if quale == "E1":
            ie.append(i); iu.append(i + 1)
        elif quale == "E2":
            if i + 2 >= n or (dt[i + 2] - dt[i]) != np.timedelta64(2, "D"): continue  # riga +2 = mercoledi'
            ie.append(i); iu.append(i + 2)
        elif quale == "E3":
            if not np.isfinite(d.O.values[i + 1]): continue
            ie.append(i); iu.append(i + 1)
    ie = np.array(ie, int); iu = np.array(iu, int)
    pe = d.C.values[ie]
    pu = d.O.values[iu] if quale == "E3" else d.C.values[iu]
    return ie, iu, pe, pu


def pool(d, quale):
    """z di tutte le finestre della stessa lunghezza (riga d'ingresso j), con anno della riga d'ingresso."""
    C = d.C.values; sg = d.sig_in.values; n = len(d)
    if quale == "E3":
        j = np.arange(n - 1); z = np.log(d.O.values[j + 1] / C[j]) / sg[j]
    else:
        L = 1 if quale == "E1" else 2
        j = np.arange(n - L); z = np.log(C[j + L] / C[j]) / sg[j]
    ok = np.isfinite(z)
    return z[ok], d.anno.values[j][ok], j[ok]


def netto(s, d, ie, iu, pe, pu, verso, scen):
    if EC.tabella_spread(s) is None: return np.nan
    notti = (d.dt.values[iu] - d.dt.values[ie]) / np.timedelta64(1, "D")
    out = [(verso * (pu[k] - pe[k]) - EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]], notti[k], scen))
           / (d.sig_in.values[ie[k]] * pe[k]) for k in range(len(ie))]
    return float(np.mean(out)) if out else np.nan


def analisi(s, f, quale, seed):
    d = tabella(s, f)
    ie, iu, pe, pu = eventi(d, quale)
    if len(ie) < 2: return None
    W = np.log(pu / pe); z = W / d.sig_in.values[ie]
    anni = d.anno.values[ie]
    zp, ap, jp = pool(d, quale)
    bench = float(zp.mean())
    anom = float(z.mean() - bench)
    pool_anni = zp[np.isin(ap, np.unique(anni))]
    p = EC.p_placebo(z.mean(), pool_anni, len(z), NREP, seed)
    t = EC.t_cluster(z, d.data.values[ie]); t_an = EC.t_cluster(z - bench, d.data.values[ie])
    ya = pd.Series(z - bench).groupby(anni).agg(["mean", "size"]); ya = ya[ya["size"] >= 2]
    quota = float((np.sign(ya["mean"]) == np.sign(anom)).mean()) if len(ya) else np.nan
    verso = 1.0 if anom > 0 else -1.0
    nb = netto(s, d, ie, iu, pe, pu, verso, "base"); ns = netto(s, d, ie, iu, pe, pu, verso, "stress")
    costo_z = (float(np.mean([EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]],
                                             (d.dt.values[iu[k]] - d.dt.values[ie[k]]) / np.timedelta64(1, "D"), "base")
                              / (d.sig_in.values[ie[k]] * pe[k]) for k in range(len(ie))]))
               if EC.tabella_spread(s) is not None else np.nan)
    # quanti lunedi' validi sono stati saltati perche' la riga dopo non e' martedi' (o +2 non e' mercoledi')
    lun = (d.dow.values == 0) & np.isfinite(d.sig_in.values)
    if quale != "E3": lun &= (d.r.values < 0)
    return dict(n=len(z), media_z=float(z.mean()), media_anomala=anom, bps=float(W.mean() * 1e4), bench=bench,
                t=t, t_an=t_an, p=p, quota=quota, anni_validi=len(ya), eventi_anno=len(z) / len(np.unique(anni)),
                netto_base=nb, netto_stress=ns, costo_z=costo_z, per_anno=ya["mean"].round(3).to_dict(),
                pool_n=len(zp), pool_anni_n=len(pool_anni), saltati=int(lun.sum()) - len(z), verso=verso,
                primo=str(d.data.values[ie[0]]), ultimo=str(d.data.values[iu[-1]]),
                hit=float(np.mean(np.sign(W) == verso)), z=z, ie=ie, d=d, mediana_z=float(np.median(z)),
                senza2020=float(z[anni != 2020].mean() - zp[ap != 2020].mean()) if (anni != 2020).any() else np.nan)


# ----------------------------------------------------------------------------------------------- E4 descrittivo
def descrittivo():
    righe = []
    for s in ORDINE:
        f = EC.FEED_INFERENZA[s]; d = tabella(s, f)
        # chiusura -> chiusura del giorno d (rendimento r_d) / sig_in_{d-1}; raggruppato per giorno della settimana di d
        zcc = d.r.values / d.sig_in.shift(1).values
        ok = np.isfinite(zcc)
        bench_cc = zcc[ok].mean()
        for g in range(5):
            m = ok & (d.dow.values == g)
            x = zcc[m]
            righe.append(dict(strumento=s, feed=f, misura="chiusura->chiusura", gruppo=GIORNI[g], n=int(m.sum()),
                              media_z=x.mean(), anomala=x.mean() - bench_cc, t=x.mean() / (x.std(ddof=1) / np.sqrt(len(x))),
                              bps=float(np.nanmean(d.r.values[m]) * 1e4)))
        if s in INDICI:
            C = d.C.values; O = d.O.values; sgp = d.sig_in.shift(1).values
            wn = np.log(O / np.roll(C, 1)); wn[0] = np.nan          # notte che finisce il giorno d: C_{d-1} -> O_d
            wd = np.log(C / O)                                       # giornata: O_d -> C_d
            for nome, w in [("notte C(d-1)->O(d)", wn), ("giornata O(d)->C(d)", wd)]:
                zz = w / sgp; okk = np.isfinite(zz); b = zz[okk].mean()
                for g in range(5):
                    m = okk & (d.dow.values == g); x = zz[m]
                    righe.append(dict(strumento=s, feed=f, misura=nome, gruppo=GIORNI[g], n=int(m.sum()),
                                      media_z=x.mean(), anomala=x.mean() - b,
                                      t=x.mean() / (x.std(ddof=1) / np.sqrt(len(x))), bps=float(np.nanmean(w[m]) * 1e4)))
        # giorno dopo un giorno in calo, per giorno della settimana del giorno in calo (lun = condizione di E1)
        dt = d.dt.values; n = len(d)
        z1 = np.full(n, np.nan); z1[:-1] = np.log(d.C.values[1:] / d.C.values[:-1]) / d.sig_in.values[:-1]
        b1 = np.nanmean(z1)
        for g in range(5):
            passo = 3 if g == 4 else 1                               # venerdi' -> lunedi'
            idx = [i for i in range(n - 1) if d.dow.values[i] == g and d.r.values[i] < 0 and np.isfinite(z1[i])
                   and (dt[i + 1] - dt[i]) == np.timedelta64(passo, "D")]
            x = z1[idx]
            righe.append(dict(strumento=s, feed=f, misura="giorno dopo un giorno in calo (C->C)", gruppo=GIORNI[g],
                              n=len(x), media_z=x.mean(), anomala=x.mean() - b1,
                              t=x.mean() / (x.std(ddof=1) / np.sqrt(len(x))),
                              bps=float(np.mean(np.log(d.C.values[np.array(idx) + 1] / d.C.values[idx])) * 1e4)))
    return pd.DataFrame(righe)


# ----------------------------------------------------------------------------------------------- main
def main():
    righe = []; seed = 5000
    for quale in ["E1", "E2", "E3"]:
        lista = INDICI if quale == "E3" else ORDINE
        for s in lista:
            f = EC.FEED_INFERENZA[s]; seed += 1
            r = analisi(s, f, quale, seed)
            c = (analisi(s, "FTMO", quale, seed + 500)
                 if (f != "FTMO" and "FTMO" in EC.STRUMENTI[s]["feed"]) else None)
            fin = {"E1": "lun in calo: C lun -> C mar", "E2": "lun in calo: C lun -> C mer",
                   "E3": "tutti i lun: C cash lun -> O cash mar (GIA' VISTO)"}[quale]
            righe.append(dict(
                test_id=f"{quale}_{s}", famiglia="E", strumento=s, feed=f, n=r["n"], media_z=r["media_z"],
                media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"], t_anomala=r["t_an"], p_primario=r["p"],
                quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"], eventi_anno=r["eventi_anno"],
                netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                conc_ftmo_media=(c["media_anomala"] if c else np.nan), conc_ftmo_n=(c["n"] if c else np.nan),
                benchmark_z=r["bench"], seed=seed, periodo=f"{r['primo']}..{r['ultimo']}",
                note=(f"{fin}; bench={r['bench']:.4f} su {r['pool_n']} finestre (pool anni eventi {r['pool_anni_n']}); "
                      f"verso {'long' if r['verso'] > 0 else 'short'}; hit={r['hit']:.3f}; mediana z={r['mediana_z']:.3f}; "
                      f"costo base medio={r['costo_z']:.4f} z; saltati (riga dopo non mar/mer o O mancante)={r['saltati']}; "
                      f"anomala senza 2020={r['senza2020']:.3f}; anomala per anno={r['per_anno']}"
                      + (f"; FTMO: z={c['media_z']:.3f}, p={c['p']:.3f}, periodo {c['primo']}..{c['ultimo']}" if c else ""))))
            print(righe[-1]["test_id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in righe[-1].items()
                                         if k in ["n", "media_z", "media_anomala", "bps", "t", "p_primario",
                                                  "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z",
                                                  "conc_ftmo_media", "conc_ftmo_n"]})
    out = pd.DataFrame(righe)
    assert len(out) == 24, len(out)
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("scritto", OUT, len(out))
    de = descrittivo()
    de.to_csv(OUT_D, sep=";", decimal=",", index=False)
    print("scritto", OUT_D, len(de))


if __name__ == "__main__":
    main()
