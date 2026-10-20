# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA I: momentum di serie storica (time-series momentum,
Moskowitz-Ooi-Pedersen 2012; Hurst-Ooi-Pedersen 2017). 40 test esatti: 10 strumenti x L = 1, 3, 6, 12 mesi.

Definizioni (vincolanti, dal piano e dalle istruzioni della famiglia):
- TD-1(m) = ultimo giorno di trading del mese m nella tabella giornaliera EC.giornaliero (chiusura cash per gli indici,
  16:00 NY per gli altri). Dicembre 2023: l'ultima riga della tabella vale come TD-1 (il sigillo e' al 31/12/2023,
  quindi il mese e' completo; per BRENT e' il 28/12 perche' il 29/12 il feed chiude alle 15:00 NY, vedi 'problemi').
- segnale(m, L) = segno di ln(C(TD-1 m) / C(TD-1 m-L)); richiede che il TD-1 del mese m-L esista in tabella.
- mese di detenzione m+1: W = ln(C(TD-1 m+1) / C(TD-1 m)); z = W / (sig_in * sqrt(N)), con sig_in = dev.std dei 20
  rendimenti giornalieri FINO a TD-1(m) incluso e N = numero di giorni di trading del mese m+1 nella tabella.
- risultato = segnale * z. media_z = media dei risultati.
- media_anomala = media_z - benchmark, benchmark = (2q - 1) * media(z dei mesi di detenzione), q = quota di segnali +1:
  e' la media attesa di una strategia a segni casuali con la stessa quota di +1 sugli STESSI mesi (= il centro della
  distribuzione di randomizzazione), cioe' l'analogo per il TSMOM del "benchmark incondizionato stesso periodo".
- t = EC.t_cluster(risultati, gruppi = mese di detenzione).
- p_primario = randomizzazione del segno: 2000 permutazioni del vettore dei segnali (stessa quota di +1), media di
  segnale_perm * z; bilaterale attorno al benchmark: p = (1 + #|m_perm - b| >= |m_oss - b|) / (1 + 2000).
- quota anni = per ogni anno (del mese di detenzione) con >= 2 eventi, media di (risultato - benchmark); quota degli
  anni con lo stesso segno della media anomala complessiva.
- netto: trade nel verso dell'effetto = segnale * segno(media_anomala) (seguire il segnale se > 0, contrario se < 0),
  ingresso alla chiusura TD-1(m), uscita alla chiusura TD-1(m+1), costo EC.costo_trade con notti di calendario fra le
  due date; netto in unita' z del test = (verso*(Pu-Pe) - costo) / (sig_in * sqrt(N) * Pe). Costo scomposto in
  spread(+commissione) e swap; swap riportato anche in % del rendimento lordo nel verso del trade.
- concordanza: stessi calcoli sul feed FTMO dove esiste (US500, US100, GER40, UK100, XAU, XAG).
Solo dati di scoperta sigillati (< 01/01/2024) tramite eventi_comune.
"""
import sys
sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f4_event_study")
import numpy as np
import pandas as pd
import eventi_comune as EC

OUT = "/home/user/Strategy-20-10-UK100/lavoro/f4_event_study/risultati/famiglia_I.csv"
NREP = 2000
LAGS = [1, 3, 6, 12]
CONTROLLI = {}


def tabella(s, f):
    d = EC.giornaliero(s, f).copy().reset_index(drop=True)
    d["sig_in"] = d.r.rolling(20, min_periods=20).std()       # 20 rendimenti FINO al giorno incluso
    d["ora_C"] = pd.to_datetime(d.ts_C).dt.hour
    d["per"] = pd.to_datetime(d.data).dt.to_period("M")
    return d


def fine_mese(d):
    """Righe dei TD-1: ultima riga di ogni mese presente in tabella. L'ultima riga della tabella conta solo se e' di
    dicembre 2023 (mese completo: il sigillo e' al 31/12/2023)."""
    per = d.per.values
    idx = [i for i in range(len(d) - 1) if per[i + 1] != per[i]]
    if per[-1] == pd.Period("2023-12", "M"):
        idx.append(len(d) - 1)
    return np.array(idx, int)


def controllo_td1(s, f, d, fm):
    """Quanti TD-1 cadono prima dell'ultimo giorno feriale non festivo del mese (giorni di calendario di scarto)."""
    fest = EC.festivi(EC.STRUMENTI[s]["cal"]) if EC.STRUMENTI[s]["cal"] else set()
    scarti = []
    for i in fm:
        p = d.per.values[i]
        x = p.to_timestamp(how="end").normalize()
        while x.weekday() >= 5 or x.date() in fest:
            x -= pd.Timedelta(days=1)
        scarti.append((x.date() - d.data.values[i]).days)
    scarti = np.array(scarti)
    mesi_consec = np.all(np.diff(np.array([d.per.values[i].ordinal for i in fm])) == 1)
    CONTROLLI[(s, f)] = dict(n_td1=len(fm), td1_non_ultimo=int((scarti > 0).sum()), scarto_max=int(scarti.max()),
                             mesi_consecutivi=bool(mesi_consec),
                             esempi=[str(d.data.values[i]) for i, sc in zip(fm, scarti) if sc > 0][:6])


def eventi(d, L):
    """(riga ingresso TD-1 m, riga uscita TD-1 m+1, riga TD-1 m-L)."""
    fm = fine_mese(d)
    pos = {d.per.values[i].ordinal: i for i in fm}
    ev = []
    for i in fm:
        o = d.per.values[i].ordinal
        if (o + 1) not in pos or (o - L) not in pos:
            continue
        if not np.isfinite(d.sig_in.values[i]):
            continue
        ev.append((i, pos[o + 1], pos[o - L]))
    return ev


def analisi(s, f, L, seed, controlla=False):
    d = tabella(s, f)
    if controlla:
        controllo_td1(s, f, d, fine_mese(d))
    ev = eventi(d, L)
    if len(ev) < 5:
        return None
    C = d.C.values
    ie = np.array([e[0] for e in ev]); iu = np.array([e[1] for e in ev]); il = np.array([e[2] for e in ev])
    sig = np.sign(np.log(C[ie] / C[il]))
    n0 = int((sig == 0).sum())
    keep = sig != 0
    ie, iu, il, sig = ie[keep], iu[keep], il[keep], sig[keep]
    N = (iu - ie).astype(float)                              # giorni di trading del mese di detenzione
    W = np.log(C[iu] / C[ie])
    z = W / (d.sig_in.values[ie] * np.sqrt(N))
    res = sig * z
    n = len(res)
    q = float((sig > 0).mean())
    zbar = float(z.mean())
    bench = (2 * q - 1) * zbar
    mz = float(res.mean())
    anom = mz - bench
    mesi = np.array([str(d.per.values[i]) for i in iu])
    anni = np.array([d.per.values[i].year for i in iu])
    t = EC.t_cluster(res, mesi)
    # randomizzazione del segno: permutazioni del vettore dei segnali (stessa quota di +1)
    rng = np.random.default_rng(seed)
    mp = np.array([(rng.permutation(sig) * z).mean() for _ in range(NREP)])
    p = float((1 + (np.abs(mp - bench) >= abs(mz - bench) - 1e-12).sum()) / (1 + NREP))
    # quota anni
    ya = pd.Series(res - bench).groupby(anni).agg(["mean", "size"])
    ya = ya[ya["size"] >= 2]
    quota = float((np.sign(ya["mean"]) == np.sign(anom)).mean()) if len(ya) else np.nan
    ya_raw = pd.Series(res).groupby(anni).mean()
    # netto
    verso = sig * (1.0 if anom > 0 else -1.0)
    pe, pu = C[ie], C[iu]
    notti = np.array([(d.data.values[b] - d.data.values[a]).days for a, b in zip(ie, iu)], float)
    den = d.sig_in.values[ie] * np.sqrt(N) * pe
    lordo_v = verso * (pu - pe) / den
    has_cost = EC.tabella_spread(s) is not None
    out = dict(n=n, n_segnale_zero=n0, quota_long=q, media_z=mz, media_anomala=anom, bench=bench, zbar=zbar,
               bps=float((sig * W).mean() * 1e4), t=t, p=p, quota=quota, anni_validi=len(ya),
               eventi_anno=n / len(np.unique(anni)), per_anno=ya["mean"].round(3).to_dict(),
               per_anno_raw=ya_raw.round(3).to_dict(), lordo_verso_z=float(lordo_v.mean()),
               bps_verso=float((verso * W).mean() * 1e4), N_medio=float(N.mean()), notti_medie=float(notti.mean()),
               primo=str(d.data.values[ie[0]]), ultimo=str(d.data.values[iu[-1]]),
               hit=float((res > 0).mean()))
    if has_cost:
        for scen in ("base", "stress"):
            ctot = np.array([EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]], notti[k], scen) for k in range(n)])
            c0 = np.array([EC.costo_trade(s, pe[k], d.ora_C.values[ie[k]], 0, scen) for k in range(n)])
            sw = ctot - c0
            out[f"netto_{scen}"] = float(((verso * (pu - pe) - ctot) / den).mean())
            out[f"costo_spread_{scen}_z"] = float((c0 / den).mean())
            out[f"swap_{scen}_z"] = float((sw / den).mean())
            out[f"swap_{scen}_bps"] = float((sw / pe).mean() * 1e4)
            out[f"spread_{scen}_bps"] = float((c0 / pe).mean() * 1e4)
            lv = float(lordo_v.mean())
            out[f"swap_{scen}_pct_lordo"] = float(out[f"swap_{scen}_z"] / lv * 100) if lv > 0 else np.nan
    else:
        for scen in ("base", "stress"):
            out[f"netto_{scen}"] = np.nan
            out[f"costo_spread_{scen}_z"] = np.nan
            out[f"swap_{scen}_z"] = np.nan
            out[f"swap_{scen}_bps"] = np.nan
            out[f"spread_{scen}_bps"] = np.nan
            out[f"swap_{scen}_pct_lordo"] = np.nan
    # verifica indipendente del benchmark: media esatta della distribuzione di randomizzazione
    out["media_perm"] = float(mp.mean())
    return out


def main():
    righe = []
    seed = 9000
    for s in EC.STRUMENTI:
        f = EC.FEED_INFERENZA[s]
        ha_ftmo = f != "FTMO" and "FTMO" in EC.STRUMENTI[s]["feed"]
        for L in LAGS:
            seed += 1
            r = analisi(s, f, L, seed, controlla=(L == 1))
            c = analisi(s, "FTMO", L, seed + 500, controlla=(L == 1)) if ha_ftmo else None
            nota = (f"TSMOM L={L}m: segno ln(C TD-1 m / C TD-1 m-{L}) -> mese m+1, z=W/(sig_in*sqrt(N)); "
                    f"quota segnali long={r['quota_long']:.3f}; media z mesi (long-only)={r['zbar']:.4f}; "
                    f"bench=(2q-1)*zbar={r['bench']:.4f} (media perm={r['media_perm']:.4f}); hit={r['hit']:.3f}; "
                    f"N medio={r['N_medio']:.1f}; notti medie={r['notti_medie']:.1f}; "
                    f"lordo nel verso={r['lordo_verso_z']:.4f} z ({r['bps_verso']:.1f} bps); "
                    f"spread base={r['spread_base_bps']:.2f} bps ({r['costo_spread_base_z']:.4f} z); "
                    f"swap base={r['swap_base_bps']:.1f} bps ({r['swap_base_z']:.4f} z, {r['swap_base_pct_lordo']:.0f}% del lordo); "
                    f"swap stress={r['swap_stress_bps']:.1f} bps ({r['swap_stress_z']:.4f} z, {r['swap_stress_pct_lordo']:.0f}% del lordo); "
                    f"anomala per anno={r['per_anno']}; risultato grezzo per anno={r['per_anno_raw']}")
            if r["n_segnale_zero"]:
                nota += f"; segnali nulli esclusi={r['n_segnale_zero']}"
            if c:
                nota += f"; FTMO: media_z={c['media_z']:.4f}, t={c['t']:.2f}, p={c['p']:.3f}, periodo {c['primo']}..{c['ultimo']}"
            righe.append(dict(
                test_id=f"I_{s}_L{L}", strumento=s, feed=f, L_mesi=L, n=r["n"], media_z=r["media_z"],
                media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"], p_primario=r["p"],
                quota_anni_stesso_segno=r["quota"], anni_validi=r["anni_validi"], eventi_anno=r["eventi_anno"],
                netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                conc_ftmo_media=(c["media_anomala"] if c else np.nan), conc_ftmo_n=(c["n"] if c else np.nan),
                benchmark_z=r["bench"], quota_long=r["quota_long"], hit_rate=r["hit"],
                lordo_verso_z=r["lordo_verso_z"], costo_spread_base_z=r["costo_spread_base_z"],
                swap_base_z=r["swap_base_z"], swap_stress_z=r["swap_stress_z"], swap_base_bps=r["swap_base_bps"],
                swap_stress_bps=r["swap_stress_bps"], swap_base_pct_lordo=r["swap_base_pct_lordo"],
                swap_stress_pct_lordo=r["swap_stress_pct_lordo"], periodo=f"{r['primo']}..{r['ultimo']}", note=nota))
            print(righe[-1]["test_id"], {k: (round(righe[-1][k], 4) if isinstance(righe[-1][k], float) else righe[-1][k])
                                         for k in ["n", "media_z", "media_anomala", "t", "p_primario",
                                                   "quota_anni_stesso_segno", "netto_base_z", "netto_stress_z",
                                                   "conc_ftmo_media", "conc_ftmo_n", "swap_base_pct_lordo"]})
    out = pd.DataFrame(righe)
    assert len(out) == 40, len(out)
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("scritto", OUT, len(out))
    print("CONTROLLI TD-1:")
    for k, v in CONTROLLI.items():
        print(k, v)


if __name__ == "__main__":
    main()
