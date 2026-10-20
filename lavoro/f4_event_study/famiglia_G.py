# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA G: flussi intraday a orario noto sulle materie prime.
12 test esatti. Solo dati di scoperta sigillati (< 01/01/2024) tramite eventi_comune.

G1 (4 test; BRENT su Pepperstone, USOIL su FTMO). Report EIA = ogni mercoledi' alle 10:30 NY, escluse le settimane con un
   festivo NYSE da lunedi' a mercoledi' (EC.festivi('NYSE')).
   r0 = ln(P(10:35)/P(10:30)), y = ln(P(12:00)/P(10:35)); P(hh:mm) = close dell'ultimo M1 iniziato prima di hh:mm (EC.prezzo_alle).
   G1a: y_z = a + b*r0_z (z con la sigma giornaliera d'ingresso); media_z = media_anomala = b (convenzione di A2);
        t = t HC1 di b; p_primario = permutazione di r0 fra gli eventi (2000); netto con posizione segno(b*r0) 10:35 -> 12:00;
        bps = media lorda del trade segno(b*r0); quota anni = pendenza annuale (anni con >= 6 eventi, come A2) con il segno di b.
   G1b: media di y_z sui mercoledi' EIA; media anomala = media - media di tutte le finestre 10:35 -> 12:00 (tutti i giorni,
        stessi anni); t cluster; p_primario = EC.p_placebo con pool = finestre 10:35 -> 12:00 di martedi' e giovedi'
        (stesse settimane valide, cioe' senza festivo NYSE lun-mer, stessi anni).
   Controllo della reazione: |r0| medio nei mercoledi' EIA contro martedi'/giovedi' alla stessa ora.
G2 (8 test; XAU, XAG, BRENT, USOIL sul feed d'inferenza).
   notte    = ln(P(08:20 NY, d) / P(16:00 NY, giorno di trading precedente)), sigma = sigma_ingresso del giorno precedente;
   giornata = ln(P(16:00 NY, d) / P(08:20 NY, d)), sigma = sigma_ingresso del giorno d.
   media z; p_primario = t (cluster per data = iid) bilaterale con approssimazione normale. Non esiste un benchmark
   incondizionato distinto (gli eventi SONO tutte le finestre di quel tipo): media_anomala = media_z (benchmark 0).
   Netto: notte = ingresso alle 16:00 NY (ora server 23, notti di calendario: 1, 3 il venerdi'); giornata = ingresso alle
   08:20 NY (ora server 15, 0 notti). Concordanza FTMO per XAU e XAG.
sigma_ingresso = dev.std dei 20 rendimenti giornalieri FINO al giorno d'ingresso INCLUSO (riga del giorno d'ingresso).
Esecuzione: python3 -I famiglia_G.py
"""
import os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from math import erf, sqrt
import numpy as np
import pandas as pd

sys.path.insert(0, '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study')
import eventi_comune as EC

QUI = '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study'
OUT = os.path.join(QUI, 'risultati', 'famiglia_G.csv')
NREP = 2000
FEST_NYSE = EC.festivi('NYSE')


def istanti_locali(date, hh, mm, tz):
    z = ZoneInfo(tz)
    return pd.Series([datetime(d.year, d.month, d.day, hh, mm, tzinfo=EC.NY).astimezone(z).replace(tzinfo=None)
                      for d in date])


def tabella(s, f, orari):
    d = EC.giornaliero(s, f).copy().reset_index(drop=True)
    d["sig_in"] = d.r.rolling(20, min_periods=20).std()          # 20 rendimenti FINO al giorno incluso
    m1 = EC.carica(s, f); tz = EC.STRUMENTI[s]["tz"]
    for hh, mm in orari:
        px, ts = EC.prezzo_alle(m1, istanti_locali(d.data, hh, mm, tz))
        d[f"P{hh:02d}{mm:02d}"] = px; d[f"T{hh:02d}{mm:02d}"] = pd.to_datetime(ts)
    dt = pd.to_datetime(d.data)
    iso = dt.dt.isocalendar()
    d["sett"] = iso.year.astype(int) * 100 + iso.week.astype(int)
    lunedi = (dt - pd.to_timedelta(dt.dt.weekday, unit="D")).dt.date
    d["sett_festiva"] = [any((l + pd.Timedelta(days=k)) in FEST_NYSE for k in range(3)) for l in lunedi]
    return d


def span_anni(d):
    return (pd.Timestamp(d.data.iloc[-1]) - pd.Timestamp(d.data.iloc[20])).days / 365.25


def ols_hc1(x, y):
    X = np.column_stack([np.ones(len(x)), x]); n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X); beta = XtXi @ X.T @ y; u = y - X @ beta
    V = XtXi @ (X.T * u ** 2) @ X @ XtXi * n / (n - k)
    return beta, np.sqrt(np.diag(V))


def slope(x, y):
    xc = x - x.mean(); return (xc @ (y - y.mean())) / (xc @ xc)


def netto(s, Pi, Pu, verso, ore, notti, sig):
    out = {}
    if EC.STRUMENTI[s]["ftmo_spread"] is None: return dict(base=np.nan, stress=np.nan, costo=np.nan)
    lordo = verso * (Pu - Pi); den = sig * Pi
    for sc in ("base", "stress"):
        c = np.array([EC.costo_trade(s, p, h, nt, sc) for p, h, nt in zip(Pi, ore, notti)])
        out[sc] = float(np.mean((lordo - c) / den))
        if sc == "base": out["costo"] = float(np.mean(c / den))
    return out


# ------------------------------------------------------------------------------------------------------------- G1
def finestre_G1(s, f):
    d = tabella(s, f, [(10, 30), (10, 35), (12, 0), (11, 0), (11, 5)])
    d["r0"] = np.log(d.P1035 / d.P1030); d["W"] = np.log(d.P1200 / d.P1035)
    d["r0z"] = d.r0 / d.sig_in; d["yz"] = d.W / d.sig_in
    d["r11"] = np.log(d.P1105 / d.P1100)
    d["ok"] = np.isfinite(d.r0z) & np.isfinite(d.yz)
    d["eia"] = (d.dow == 2) & ~d.sett_festiva
    return d


def analisi_G1(s, f, seed):
    d = finestre_G1(s, f)
    ev = d[d.eia & d.ok].reset_index(drop=True)
    anni = set(ev.anno)
    tutte = d[d.ok & d.anno.isin(anni)]
    # --- G1a: pendenza
    x = ev.r0z.values; y = ev.yz.values
    beta, se = ols_hc1(x, y); b = beta[1]
    rng = np.random.default_rng(seed)
    bp = np.array([slope(rng.permutation(x), y) for _ in range(NREP)])
    pa = float((1 + (np.abs(bp) >= abs(b)).sum()) / (1 + NREP))
    per_anno = {}
    for yy, g in ev.groupby("anno"):
        if len(g) >= 6 and g.r0z.std() > 0: per_anno[int(yy)] = float(slope(g.r0z.values, g.yz.values))
    quota_a = float(np.mean([np.sign(v) == np.sign(b) for v in per_anno.values()])) if per_anno else np.nan
    verso_a = np.sign(b * x); n_zero = int((verso_a == 0).sum()); verso_a[verso_a == 0] = 1.0
    ore = ev.T1035.dt.hour.values; notti = np.zeros(len(ev))
    na = netto(s, ev.P1035.values, ev.P1200.values, verso_a, ore, notti, ev.sig_in.values)
    sp = span_anni(d)
    G1a = dict(n=len(ev), media_z=b, media_anomala=b, bps=float(np.mean(verso_a * ev.W.values) * 1e4), t=b / se[1], p=pa,
               quota=quota_a, eventi_anno=len(ev) / sp, netto_base=na["base"], netto_stress=na["stress"],
               note=(f"y_z = a + b*r0_z, eventi EIA {len(ev)}; a={beta[0]:.4f}; corr={np.corrcoef(x, y)[0, 1]:.3f}; "
                     f"lordo_z segno(b*r0)={np.mean(verso_a * y):.4f}; costo medio {na['costo']:.4f} z; ore server ingresso "
                     f"{sorted(set(int(h) for h in ore))}; r0 nulli {n_zero}; b per anno={ {k: round(v, 3) for k, v in per_anno.items()} }; "
                     f"bps = media lorda del trade segno(b*r0); p = permutazione di r0 ({NREP})"))
    # --- G1b: media della deriva
    pool = tutte[tutte.dow.isin([1, 3]) & ~tutte.sett_festiva]
    bench = tutte.yz.mean(); mz = ev.yz.mean(); anom = mz - bench
    t_b = EC.t_cluster(ev.yz.values, ev.data.values)
    p_b = EC.p_placebo(mz, pool.yz.values, len(ev), NREP, seed + 1)
    segni = []
    for yy, g in ev.groupby("anno"):
        if len(g) >= 2: segni.append(np.sign(g.yz.mean() - tutte[tutte.anno == yy].yz.mean()))
    quota_b = float(np.mean(np.array(segni) == np.sign(anom))) if segni else np.nan
    verso_b = 1.0 if anom > 0 else -1.0
    nb = netto(s, ev.P1035.values, ev.P1200.values, np.full(len(ev), verso_b), ore, notti, ev.sig_in.values)
    G1b = dict(n=len(ev), media_z=mz, media_anomala=anom, bps=float(ev.W.mean() * 1e4), t=t_b, p=p_b, quota=quota_b,
               eventi_anno=len(ev) / sp, netto_base=nb["base"], netto_stress=nb["stress"],
               note=(f"10:35->12:00 mercoledi' EIA; bench {bench:.4f} su {len(tutte)} finestre (tutti i giorni, stessi anni); "
                     f"pool mar/gio {len(pool)} (media {pool.yz.mean():.4f}); verso trade {'long' if verso_b > 0 else 'short'}; "
                     f"anni per la quota {len(segni)}; costo medio {nb['costo']:.4f} z; t sugli anomali "
                     f"{EC.t_cluster(ev.yz.values - bench, ev.data.values):.3f}"))
    # --- controlli
    tt = d[d.ok & d.dow.isin([1, 3]) & ~d.sett_festiva & d.anno.isin(anni)]
    esclusi = d[d.ok & (d.dow == 2) & d.sett_festiva]
    gio_fest = d[(d.dow == 3) & d.sett_festiva & np.isfinite(d.r11)]
    gio_norm = d[(d.dow == 3) & ~d.sett_festiva & np.isfinite(d.r11)]
    col_vet = d[d.ok & (d.dow == 2) & d.data.apply(lambda x: _settimana_federale(x))]
    ctrl = dict(abs_r0_eia_bps=float(ev.r0.abs().mean() * 1e4), abs_r0_martgio_bps=float(tt.r0.abs().mean() * 1e4),
                med_r0_eia_bps=float(ev.r0.abs().median() * 1e4), med_r0_martgio_bps=float(tt.r0.abs().median() * 1e4),
                abs_r0z_eia=float(ev.r0z.abs().mean()), abs_r0z_martgio=float(tt.r0z.abs().mean()),
                n_eia=len(ev), n_martgio=len(tt), n_mer_esclusi=len(esclusi),
                abs_r0_mer_esclusi_bps=float(esclusi.r0.abs().mean() * 1e4) if len(esclusi) else np.nan,
                abs_r11_gio_fest_bps=float(gio_fest.r11.abs().mean() * 1e4) if len(gio_fest) else np.nan,
                abs_r11_gio_norm_bps=float(gio_norm.r11.abs().mean() * 1e4), n_gio_fest=len(gio_fest),
                abs_r0_mer_colvet_bps=float(col_vet.r0.abs().mean() * 1e4) if len(col_vet) else np.nan,
                n_mer_colvet=len(col_vet), frac_eia_ratio3=float((ev.r0.abs() >= 3 * tt.r0.abs().median()).mean()),
                primo=str(ev.data.iloc[0]), ultimo=str(ev.data.iloc[-1]),
                mer_nel_periodo=int(((d.dow == 2) & d.anno.isin(anni)).sum()),
                mer_senza_prezzi=int(((d.dow == 2) & ~d.sett_festiva & ~d.ok).sum()))
    return G1a, G1b, ctrl


def _settimana_federale(x):
    """Mercoledi' di settimane con Columbus Day o Veterans Day (festivi federali NON NYSE) da lunedi' a mercoledi'."""
    import holidays
    fed = holidays.US(years=x.year)
    lun = x - pd.Timedelta(days=x.weekday()).to_pytimedelta()
    for k in range(3):
        g = lun + pd.Timedelta(days=k).to_pytimedelta()
        n = fed.get(g)
        if n and ("Columbus" in n or "Veterans" in n): return True
    return False


# ------------------------------------------------------------------------------------------------------------- G2
def finestre_G2(s, f):
    d = tabella(s, f, [(8, 20)])
    a = d.iloc[:-1].reset_index(drop=True); b = d.iloc[1:].reset_index(drop=True)
    w = pd.DataFrame({"d0": a.data, "d": b.data, "anno_d": b.anno, "gap": (pd.to_datetime(b.data) - pd.to_datetime(a.data)).dt.days})
    w["C0"], w["T0"], w["sig0"] = a.C.values, pd.to_datetime(a.ts_C.values), a.sig_in.values
    w["P0820"], w["T0820"], w["C1"], w["sig1"] = b.P0820.values, b.T0820.values, b.C.values, b.sig_in.values
    w["r_d"] = b.r.values
    w["Wn"] = np.log(w.P0820 / w.C0); w["Wg"] = np.log(w.C1 / w.P0820)
    w["zn"] = w.Wn / w.sig0; w["zg"] = w.Wg / w.sig1
    w["ok"] = np.isfinite(w.zn) & np.isfinite(w.zg) & (w.gap <= 4)
    return w[w.ok].reset_index(drop=True), d


def p_normale(t):
    return float(2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))) if np.isfinite(t) else np.nan


def analisi_G2(s, f, quale):
    w, d = finestre_G2(s, f)
    z = w.zn.values if quale == "notte" else w.zg.values
    W = w.Wn.values if quale == "notte" else w.Wg.values
    mz = float(np.mean(z)); t = EC.t_cluster(z, w.d.values)
    segni = []
    for yy, g in w.groupby("anno_d"):
        if len(g) >= 2:
            segni.append(np.sign((g.zn if quale == "notte" else g.zg).mean()))
    quota = float(np.mean(np.array(segni) == np.sign(mz))) if segni else np.nan
    verso = 1.0 if mz > 0 else -1.0
    if quale == "notte":
        Pi, Pu, sig = w.C0.values, w.P0820.values, w.sig0.values
        notti = w.gap.values.astype(float); ore = np.full(len(w), 23)
        ore_alt = w.T0.dt.hour.values
    else:
        Pi, Pu, sig = w.P0820.values, w.C1.values, w.sig1.values
        notti = np.zeros(len(w)); ore = pd.to_datetime(w.T0820).dt.hour.values; ore_alt = ore
    nt = netto(s, Pi, Pu, np.full(len(w), verso), ore, notti, sig)
    nt_alt = netto(s, Pi, Pu, np.full(len(w), verso), ore_alt, notti, sig)
    sp = (pd.Timestamp(w.d.iloc[-1]) - pd.Timestamp(w.d.iloc[0])).days / 365.25
    per_anno = {int(yy): round(float((g.zn if quale == "notte" else g.zg).mean()), 4) for yy, g in w.groupby("anno_d")}
    # descrittivo: bench close-to-close (z del giorno con la sigma d'ingresso del giorno precedente)
    zcc = (w.r_d / w.sig0).mean()
    return dict(n=len(w), media_z=mz, media_anomala=mz, bps=float(np.mean(W) * 1e4), t=t, p=p_normale(t), quota=quota,
                eventi_anno=len(w) / sp, netto_base=nt["base"], netto_stress=nt["stress"], costo=nt["costo"],
                netto_base_alt=nt_alt["base"], verso=verso, per_anno=per_anno, zcc=zcc,
                notti_medie=float(np.mean(notti)), ore=sorted(set(int(h) for h in ore)), ore_alt=sorted(set(int(h) for h in ore_alt)),
                n_anni=len(segni), periodo=f"{w.d.iloc[0]}..{w.d.iloc[-1]}",
                somma_ok=float(np.nanmax(np.abs(w.Wn + w.Wg - w.r_d))), t_iid=float(mz / (np.std(z, ddof=1) / np.sqrt(len(z)))))


# ------------------------------------------------------------------------------------------------------------- main
def riga(test_id, s, f, r, conc_m=np.nan, conc_n=np.nan, note=""):
    return dict(test_id=test_id, famiglia="G", strumento=s, feed=f, n=r["n"], media_z=r["media_z"],
                media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"], p_primario=r["p"],
                quota_anni_stesso_segno=r["quota"], eventi_anno=r["eventi_anno"], netto_base_z=r["netto_base"],
                netto_stress_z=r["netto_stress"], conc_ftmo_media=conc_m, conc_ftmo_n=conc_n, note=note)


def main():
    righe = []; controlli = []; seed = 700
    for s in ("BRENT", "USOIL"):
        f = EC.FEED_INFERENZA[s]; seed += 10
        G1a, G1b, ctrl = analisi_G1(s, f, seed)
        righe.append(riga(f"G1a_{s}", s, f, G1a, note=G1a["note"] + f"; seed {seed}"))
        righe.append(riga(f"G1b_{s}", s, f, G1b, note=G1b["note"] + f"; seed {seed + 1}"))
        controlli.append((s, f, ctrl))
    for s in ("XAU", "XAG", "BRENT", "USOIL"):
        f = EC.FEED_INFERENZA[s]
        for quale in ("notte", "giornata"):
            r = analisi_G2(s, f, quale)
            cm = cn = np.nan; cnote = ""
            if f != "FTMO" and "FTMO" in EC.STRUMENTI[s]["feed"]:
                c = analisi_G2(s, "FTMO", quale); cm, cn = c["media_anomala"], c["n"]
                cnote = f"; FTMO t {c['t']:.3f} periodo {c['periodo']}"
            fin = ("16:00 NY giorno prec. -> 08:20 NY" if quale == "notte" else "08:20 NY -> 16:00 NY")
            note = (f"{fin}; periodo {r['periodo']}; media_anomala = media_z (benchmark 0: gli eventi sono tutte le finestre "
                    f"del tipo); p = t normale bilaterale; t iid {r['t_iid']:.3f}; verso trade {'long' if r['verso'] > 0 else 'short'}; "
                    f"costo medio {r['costo']:.4f} z, notti medie {r['notti_medie']:.2f}, ore server costo {r['ore']} "
                    f"(con l'ora dell'M1 usato {r['ore_alt']}: netto base {r['netto_base_alt']:.4f}); anni per la quota {r['n_anni']}; "
                    f"media z per anno {r['per_anno']}; z medio close-to-close (descrittivo) {r['zcc']:.4f}; "
                    f"max |Wn+Wg-r_d| {r['somma_ok']:.1e}" + cnote)
            righe.append(riga(f"G2_{s}_{quale}", s, f, r, cm, cn, note))
    for rr in righe:
        print(rr["test_id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rr.items() if k not in ("note", "famiglia")})
        print("    ", rr["note"])
    print("\nCONTROLLI G1 (reazione EIA)")
    for s, f, c in controlli:
        print(" ", s, f, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()})
    out = pd.DataFrame(righe)
    assert len(out) == 12
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("\nscritto", OUT, len(out), "test")


if __name__ == "__main__":
    main()
