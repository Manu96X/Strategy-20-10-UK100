# -*- coding: utf-8 -*-
"""
EVENT STUDY pre-registrato (PIANO_EVENT_STUDY.md) - FAMIGLIA B: FOMC (Lucca-Moench 2015). 20 test.
Solo dati di scoperta sigillati (< 01/01/2024) tramite eventi_comune.

B1 (10 strumenti): ingresso al prezzo delle 14:00 NY del giorno di trading precedente il giorno FOMC,
    uscita al prezzo delle 13:55 NY del giorno FOMC (drift pre-annuncio).
    Pool placebo: stesse finestre orarie (14:00 NY giorno d -> 13:55 NY giorno di trading successivo)
    in tutti i giorni NON FOMC (escluse le finestre che toccano un giorno FOMC), stessi anni.
B2 (10 strumenti): ingresso alle 14:05 NY del giorno FOMC, uscita alle 16:00 NY del giorno di trading successivo.
    Pool placebo: stesse finestre orarie nei giorni non FOMC (escluse quelle che toccano un giorno FOMC), stessi anni.

Convenzioni:
- giorni di trading = righe di EC.giornaliero(strumento, feed) (calendario della borsa per gli indici);
  un evento esiste solo se il giorno FOMC e' un giorno di trading dello strumento;
- finestra fra righe consecutive con distanza di calendario <= 4 giorni (buchi di dati esclusi);
- orari di New York convertiti nel fuso dello strumento (colonna 'loc' di EC.carica) con zoneinfo;
- sigma_ingresso = dev.std dei 20 rendimenti giornalieri fino al giorno d'ingresso INCLUSO;
- z = ln(P_uscita/P_ingresso) / sigma_ingresso; anno della finestra = anno del giorno d'ingresso;
- media anomala = media z eventi - media z di tutte le finestre della stessa lunghezza (stessi anni degli eventi);
- t = EC.t_cluster(z eventi, date eventi); p primario = EC.p_placebo(media z eventi, pool non FOMC, n, 2000, seed);
- quota anni: anni con >= 2 eventi, media anomala dell'anno (benchmark = tutte le finestre di quell'anno);
- netto (unita' z) nel verso dell'effetto, EC.costo_trade con ora server dell'M1 d'ingresso e notti di calendario
  (differenza fra le date server di uscita e d'ingresso: una notte per ogni passaggio delle 17:00 NY).
Esecuzione: python3 -I famiglia_B.py
"""
import os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

sys.path.insert(0, '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study')
import eventi_comune as EC

QUI = '/home/user/Strategy-20-10-UK100/lavoro/f4_event_study'
OUT = os.path.join(QUI, 'risultati', 'famiglia_B.csv')
ORDINE = ["US500", "US100", "GER40", "UK100", "XAU", "XAG", "BRENT", "USOIL", "VIX", "USDX"]
FOMC = set(pd.Timestamp(x).date() for x in EC.FOMC)
NREP = 2000


def istanti_locali(date, hh, mm, tz):
    """Istante hh:mm di New York di ciascuna data -> ora locale naive nel fuso dello strumento."""
    z = ZoneInfo(tz)
    return pd.Series([datetime(d.year, d.month, d.day, hh, mm, tzinfo=EC.NY).astimezone(z).replace(tzinfo=None)
                      for d in date])


def tabella_prezzi(strumento, feed):
    """Tabella giornaliera con sigma_ingresso e i prezzi ai tempi NY che servono."""
    d = EC.giornaliero(strumento, feed).copy()
    d["sig_in"] = d.r.rolling(20, min_periods=20).std()          # 20 rendimenti fino al giorno incluso
    m1 = EC.carica(strumento, feed); tz = EC.STRUMENTI[strumento]["tz"]
    for hh, mm in [(13, 55), (14, 0), (14, 5), (16, 0)]:
        px, ts = EC.prezzo_alle(m1, istanti_locali(d.data, hh, mm, tz))
        d[f"P{hh:02d}{mm:02d}"] = px; d[f"T{hh:02d}{mm:02d}"] = pd.to_datetime(ts)
    # controllo del comunicato: prezzi a 5 minuti 13:00 .. 14:00 (solo per i giorni FOMC)
    return d, m1


def controllo_annuncio(d, m1, strumento):
    """Per ogni giorno FOMC nel calendario dello strumento: |r 14:00->14:05| >= 3 x mediana |r 5 min| dell'ora 13:00-14:00."""
    tz = EC.STRUMENTI[strumento]["tz"]
    f = d[d.data.isin(FOMC)].reset_index(drop=True)
    griglia = {}
    for k in range(13):
        mins = 13 * 60 + 5 * k
        griglia[k] = EC.prezzo_alle(m1, istanti_locali(f.data, mins // 60, mins % 60, tz))[0]
    G = np.vstack([griglia[k] for k in range(13)]).T                     # (giorni, 13 prezzi)
    r5 = np.abs(np.diff(np.log(G), axis=1))
    med = np.nanmedian(r5, axis=1)
    rann = np.abs(np.log(f.P1405.values / f.P1400.values))
    valido = np.isfinite(rann) & np.isfinite(med)
    ok = valido & (rann >= 3 * med) & (rann > 0)
    rapporto = np.where(valido & (med > 0), rann / np.where(med > 0, med, np.nan), np.nan)
    falliti = [str(x) for x, v, o in zip(f.data, valido, ok) if v and not o]
    return dict(n_fomc_cal=len(f), n_validi=int(valido.sum()), n_falliti=int((valido & ~ok).sum()),
                date_fallite=falliti, rapporto_mediano=float(np.nanmedian(rapporto)) if valido.any() else np.nan)


def finestre(d, tipo):
    """Tutte le finestre di un tipo (B1/B2) fra righe consecutive: DataFrame con z, prezzi, flag evento/pool."""
    a = d.iloc[:-1].reset_index(drop=True); b = d.iloc[1:].reset_index(drop=True)
    w = pd.DataFrame({"d0": a.data, "d1": b.data, "anno": a.anno, "sig": a.sig_in})
    if tipo == "B1":
        w["Pi"], w["Ti"], w["Pu"], w["Tu"] = a.P1400, a.T1400, b.P1355, b.T1355
        w["evento"] = w.d1.isin(FOMC)
    else:
        w["Pi"], w["Ti"], w["Pu"], w["Tu"] = a.P1405, a.T1405, b.P1600, b.T1600
        w["evento"] = w.d0.isin(FOMC)
    w["tocca"] = w.d0.isin(FOMC) | w.d1.isin(FOMC)
    w["gap"] = (pd.to_datetime(w.d1) - pd.to_datetime(w.d0)).dt.days
    w["W"] = np.log(w.Pu / w.Pi)
    w["z"] = w.W / w.sig
    w["ok"] = np.isfinite(w.z) & (w.gap <= 4)
    return w


def analizza(strumento, feed, tipo, seed):
    d, m1 = tabella_prezzi(strumento, feed)
    w = finestre(d, tipo)
    # eventi FOMC persi (non nel calendario, buco di dati o prezzi mancanti)
    if tipo == "B1":
        nel_periodo = [x for x in FOMC if d.data.iloc[21] <= x <= d.data.iloc[-1]]
        trovati = set(w.loc[w.evento & w.ok, "d1"])
    else:
        nel_periodo = [x for x in FOMC if d.data.iloc[20] <= x < d.data.iloc[-1]]
        trovati = set(w.loc[w.evento & w.ok, "d0"])
    persi = sorted(str(x) for x in nel_periodo if x not in trovati)
    ev = w[w.evento & w.ok].reset_index(drop=True)
    anni = set(ev.anno)
    tutte = w[w.ok & w.anno.isin(anni)]
    pool = tutte[~tutte.tocca]
    bench = tutte.z.mean()
    n = len(ev); mz = ev.z.mean(); anom = mz - bench
    res = dict(n=n, media_z=mz, media_anomala=anom, bps=ev.W.mean() * 1e4, bench=bench,
               n_tutte=len(tutte), n_pool=len(pool), pool_media=pool.z.mean(), persi=persi,
               n_weekend_pool=int((pool.gap > 1).sum()), ev=ev)
    res["t"] = EC.t_cluster(ev.z.values, ev.d0.values) if n >= 3 else np.nan
    res["p"] = EC.p_placebo(mz, pool.z.values, n, NREP, seed) if n >= 2 else np.nan
    # quota anni stesso segno (benchmark annuale)
    segni = []
    for y, g in ev.groupby("anno"):
        if len(g) >= 2:
            segni.append(np.sign(g.z.mean() - tutte[tutte.anno == y].z.mean()))
    res["quota_anni"] = float(np.mean(np.array(segni) == np.sign(anom))) if segni else np.nan
    res["n_anni_quota"] = len(segni)
    span = (pd.Timestamp(w.loc[w.ok, "d0"].max()) - pd.Timestamp(w.loc[w.ok, "d0"].min())).days / 365.25
    res["eventi_anno"] = n / span if span > 0 else np.nan
    # netto dei costi nel verso dell'effetto
    verso = 1.0 if anom > 0 else -1.0
    res["verso"] = verso
    if EC.STRUMENTI[strumento]["ftmo_spread"] is None or n == 0:
        res["netto_base"] = res["netto_stress"] = np.nan; res["costo_medio_z"] = np.nan
    else:
        notti = (ev.Tu.dt.normalize() - ev.Ti.dt.normalize()).dt.days.values
        ore = ev.Ti.dt.hour.values
        lordo = verso * (ev.Pu.values - ev.Pi.values)
        den = ev.sig.values * ev.Pi.values
        for sc in ("base", "stress"):
            c = np.array([EC.costo_trade(strumento, p, h, nt, sc) for p, h, nt in zip(ev.Pi.values, ore, notti)])
            res[f"netto_{sc}"] = float(np.mean((lordo - c) / den))
            if sc == "base": res["costo_medio_z"] = float(np.mean(c / den))
        res["notti_medie"] = float(np.mean(notti)); res["ore_ingresso"] = sorted(set(int(h) for h in ore))
    return res, d, m1


def main():
    righe, controlli = [], []
    seed = 200
    for tipo in ("B1", "B2"):
        for s in ORDINE:
            seed += 1
            feed = EC.FEED_INFERENZA[s]
            r, d, m1 = analizza(s, feed, tipo, seed)
            conc_m = conc_n = np.nan
            if feed != "FTMO" and "FTMO" in EC.STRUMENTI[s]["feed"]:
                rf, _, _ = analizza(s, "FTMO", tipo, seed + 1000)
                conc_m, conc_n = rf["media_anomala"], rf["n"]
            nota = (f"bench {r['bench']:.4f} su {r['n_tutte']} finestre; pool non FOMC {r['n_pool']} (media {r['pool_media']:.4f}, "
                    f"{r['n_weekend_pool']} a cavallo di weekend/festivi); verso trade {'long' if r['verso'] > 0 else 'short'}; "
                    f"anni per la quota {r['n_anni_quota']}; FOMC persi {len(r['persi'])}"
                    + (f" ({', '.join(r['persi'])})" if r['persi'] else "")
                    + (f"; costo medio {r['costo_medio_z']:.4f} z, notti medie {r['notti_medie']:.2f}, ore server ingresso {r['ore_ingresso']}"
                       if np.isfinite(r.get('costo_medio_z', np.nan)) else "; costo n.d.")
                    + (f"; t sugli anomali {EC.t_cluster(r['ev'].z.values - r['bench'], r['ev'].d0.values):.3f}" if r['n'] >= 3 else ""))
            righe.append(dict(test_id=f"{tipo}_{s}", famiglia="B", strumento=s, feed=feed, n=r["n"],
                              media_z=r["media_z"], media_anomala=r["media_anomala"], bps=r["bps"], t=r["t"],
                              p_primario=r["p"], quota_anni_stesso_segno=r["quota_anni"], eventi_anno=r["eventi_anno"],
                              netto_base_z=r["netto_base"], netto_stress_z=r["netto_stress"],
                              conc_ftmo_media=conc_m, conc_ftmo_n=conc_n, seed=seed, note=nota))
            print(righe[-1]["test_id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in righe[-1].items() if k not in ("note",)})
            print("   ", nota)
            if tipo == "B1":
                c = controllo_annuncio(d, m1, s)
                controlli.append((s, feed, c))
                print("    controllo annuncio:", c)
    out = pd.DataFrame(righe)
    out.to_csv(OUT, sep=";", decimal=",", index=False)
    print("\nscritto", OUT, len(out), "test")
    print("\nCONTROLLO ANNUNCIO 14:00->14:05 vs 3x mediana |r5| 13:00-14:00")
    for s, f, c in controlli:
        print(f"  {s} {f}: FOMC in calendario {c['n_fomc_cal']}, validi {c['n_validi']}, NON soddisfatti {c['n_falliti']} "
              f"{c['date_fallite']}, rapporto mediano {c['rapporto_mediano']:.1f}")


if __name__ == "__main__":
    main()
