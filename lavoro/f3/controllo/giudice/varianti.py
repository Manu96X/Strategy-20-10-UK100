# Varianti del motore (copie locali di simula / esiti_tutte_le_barre; il motore originale NON e' modificato)
import numpy as np, pandas as pd
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import motore_f3 as M
MIN, ORA = M.MIN, M.ORA

def prepara_buchi(feed, soglia_min):
    """per ogni M1 i: ts dell'ultima quotazione prima del primo buco > soglia che inizia in j >= i (inf se nessuno)"""
    ts = feed.ts; d = np.diff(ts)
    g = np.flatnonzero(d > soglia_min * MIN)            # buco fra g e g+1
    nxt = np.full(len(ts), np.iinfo(np.int64).max, np.int64)
    pos = np.searchsorted(g, np.arange(len(ts)), "left")
    ok = pos < len(g)
    nxt[ok] = ts[g[pos[ok]]]
    feed._buco_next = nxt
    return g

def simula_var(feed, i0, t_regola, d, tab_spread, sc, sl_prima=True, buchi=False, sl_protocollo=False):
    ts = feed.ts
    k = feed.info_giorno(i0)
    if k is None: return None
    chius = feed.prossima_chiusura[k]
    if feed.chiusura_dopo[k] and ts[i0] >= feed.ultima[k] - 2 * ORA: return None
    if buchi:
        gb = feed._buco_next[i0]
        if gb < chius:                                          # il buco viene prima della chiusura di calendario
            if ts[i0] >= gb - 2 * ORA: return None              # regola delle 2 ore anche prima del buco
            chius = gb
    t_forz = chius - 15 * MIN
    t_exit = min(t_regola, t_forz)
    if t_exit <= ts[i0]: return None
    ie = int(np.searchsorted(ts, t_exit, "left"))
    if ie >= len(ts): return None
    sp = tab_spread[feed.ora[i0]] * sc["spread"]
    fill = feed.o[i0] + sp + sc["mkt"]
    SL, TP = fill - d, fill + 2 * d
    seg_l, seg_h = feed.l[i0:ie], feed.h[i0:ie]
    a = np.flatnonzero(seg_l <= SL); b_ = np.flatnonzero(seg_h >= TP)
    jsl = a[0] if len(a) else np.inf; jtp = b_[0] if len(b_) else np.inf
    slip = 0.0
    if jsl < np.inf and (jsl < jtp or (jsl == jtp and sl_prima)):
        j = i0 + int(jsl)
        if sl_protocollo: px = min(feed.o[j], SL) - sc["slip"]; slip = sc["slip"]
        else: px = min(feed.o[j], SL - sc["slip"]); slip = min(SL - px, sc["slip"])
        tipo = "SL"
    elif jtp < np.inf:
        j = i0 + int(jtp); px = TP; tipo = "TP"
    else:
        j = ie; px = feed.o[ie] - sc["mkt"]; tipo = "TEMPO" if t_exit == t_regola else "CHIUSURA"
    de, du = feed.giorno_int[i0], feed.giorno_int[j]
    notti = 0
    for x in range(de, du):
        notti += 3 if (x + 3) % 7 == 2 else 1
    swap = notti * sc["swap"]
    R = (px - fill - swap) / d
    n_mkt = 2 if tipo in ("TEMPO", "CHIUSURA") else 1
    return dict(i0=i0, ts_in=ts[i0], ts_out=ts[j], fill=fill, sl=SL, tp=TP, px_out=px, d=d, tipo=tipo,
                spread=sp, slip=slip, notti=notti, swap=swap, R=R,
                costo_R=(sp + sc["mkt"] * n_mkt + slip + swap) / d)

def fabbrica_esiti(**kw):
    def esiti(feed, b, m, regola_t, tab, sc, sl_prima=True):
        fine = b.fine_srv.values.astype("datetime64[ns]").astype(np.int64)
        i0s = np.searchsorted(feed.ts, fine, "left")
        out = [None] * len(b)
        atr = b.atr.to_numpy(); val = b.valida.to_numpy()
        for s in range(len(b)):
            if not val[s]: continue
            i0 = i0s[s]
            if i0 >= len(feed.ts) or feed.ts[i0] - fine[s] > 15 * MIN: continue
            t_r = M.scadenza(regola_t, b, s, i0, feed)
            if t_r is None: continue
            r = simula_var(feed, i0, t_r, m * atr[s], tab, sc, sl_prima, **kw)
            if r is not None:
                r["s"] = s; out[s] = r
        return out
    return esiti
