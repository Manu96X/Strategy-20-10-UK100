#!/usr/bin/env python3
"""Replica cieca indipendente di S1 (famiglia S1-R), protocollo PROTOCOLLO_S1_S2.md §2, §3, §5, §6.
Esecuzione: python3 -I replica_s1.py
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from scipy import stats

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = '/home/user/Strategy-20-10-UK100'
CAL = f'{BASE}/calendario_economico.csv'
EVL = f'{BASE}/lavoro/s1_s2/EVENTI_S1_ELENCO_CHIUSO.csv'
COST = f'{BASE}/lavoro/s1_s2/risultati/COSTI_TABELLA_CONGELATA.csv'
END_UTC = pd.Timestamp('2024-01-01 00:00')  # scoperta < 01/01/2024

H1 = '/home/user/dati_h1/scoperta'
ST = '/home/user/dati_scoperta_tutti'
# strumento: (file, inizio feed (data server), regola fuso, valute pertinenti)
FEEDS = {
    'EURUSD': (f'{H1}/EURUSD m1 FTMO.csv', '2016-01-04', 'ATH2019', ['USD', 'EUR']),
    'GBPUSD': (f'{H1}/GBPUSD m1 FTMO.csv', '2016-01-04', 'ATH2019', ['USD', 'GBP']),
    'USDJPY': (f'{H1}/USDJPY m1 FTMO.csv', '2016-01-04', 'ATH2019', ['USD', 'JPY']),
    'XAU':    (f'{H1}/XAU-USD Pepperstone m1.csv', '2017-06-12', 'NY7', ['USD']),
    'US100':  (f'{ST}/NAS100 m1 - FTPepperstone.csv', '2017-06-09', 'NY7', ['USD']),
    'US500':  (f'{ST}/US500 m1 - Pepperstone.csv', '2020-07-13', 'NY7', ['USD']),
}
CONC = {  # feed di concordanza (cancello 8)
    'XAU':   (f'{H1}/XAU-USD FTMO m1.csv', '2021-01-04', 'NY7', ['USD']),
    'US100': (f'{ST}/US100 m1 - FTMO.csv', '2021-09-14', 'NY7', ['USD']),
    'US500': (f'{ST}/US500 m1 - FTMO.csv', '2021-09-14', 'NY7', ['USD']),
}
INSTR = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAU', 'US100', 'US500']
FX = {'EURUSD', 'GBPUSD', 'USDJPY'}
HS = [30, 60, 120]
CS = [0.10, 0.25]
SLIP_STRESS = 2 * 0.3e-4

# Giorni di chiusura NYSE 2016-2023 (chiusure intere)
NYSE_CLOSED = set(pd.to_datetime([
    '2016-01-01', '2016-01-18', '2016-02-15', '2016-03-25', '2016-05-30', '2016-07-04', '2016-09-05', '2016-11-24', '2016-12-26',
    '2017-01-02', '2017-01-16', '2017-02-20', '2017-04-14', '2017-05-29', '2017-07-04', '2017-09-04', '2017-11-23', '2017-12-25',
    '2018-01-01', '2018-01-15', '2018-02-19', '2018-03-30', '2018-05-28', '2018-07-04', '2018-09-03', '2018-11-22', '2018-12-05', '2018-12-25',
    '2019-01-01', '2019-01-21', '2019-02-18', '2019-04-19', '2019-05-27', '2019-07-04', '2019-09-02', '2019-11-28', '2019-12-25',
    '2020-01-01', '2020-01-20', '2020-02-17', '2020-04-10', '2020-05-25', '2020-07-03', '2020-09-07', '2020-11-26', '2020-12-25',
    '2021-01-01', '2021-01-18', '2021-02-15', '2021-04-02', '2021-05-31', '2021-07-05', '2021-09-06', '2021-11-25', '2021-12-24',
    '2022-01-17', '2022-02-21', '2022-04-15', '2022-05-30', '2022-06-20', '2022-07-04', '2022-09-05', '2022-11-24', '2022-12-26',
    '2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04', '2023-11-23', '2023-12-25',
]).date)

EPOCH = pd.Timestamp('1970-01-01')


def to_min(ts):
    """Timestamp naive (Series/Index/DatetimeIndex) -> minuti interi dall'epoca."""
    return ((pd.DatetimeIndex(ts) - EPOCH) // pd.Timedelta(minutes=1)).to_numpy().astype(np.int64)


def utc_to_server(utc_naive, rule):
    """utc_naive: DatetimeIndex naive in UTC -> DatetimeIndex naive in ora server del feed."""
    u = pd.DatetimeIndex(utc_naive).tz_localize('UTC')
    ny7 = u.tz_convert('America/New_York').tz_localize(None) + pd.Timedelta(hours=7)
    if rule == 'NY7':
        return ny7
    ath = u.tz_convert('Europe/Athens').tz_localize(None)
    # Atene fino al 31/12/2019, NY+7 dal 2020 (al confine i due coincidono: UTC+2)
    use_ath = pd.DatetimeIndex(utc_naive) < pd.Timestamp('2020-01-01')
    return pd.DatetimeIndex(np.where(use_ath, ath.values, ny7.values))


def ny_local_to_utc(local_naive):
    return pd.DatetimeIndex(local_naive).tz_localize('America/New_York').tz_convert('UTC').tz_localize(None)


# ---------------------------------------------------------------- calendario
def load_calendar():
    c = pd.read_csv(CAL, sep=';', encoding='latin-1', skiprows=1, dtype=str)
    c['srv'] = pd.to_datetime(c['ora_server'], format='%Y.%m.%d %H:%M')
    c['utc'] = c['srv'] - pd.Timedelta(hours=3)  # calendario in UTC+3 fisso
    return c


def build_events(c):
    ids = set(pd.read_csv(EVL, sep=';', dtype=str)['event_id'])
    s = c[c.event_id.isin(ids) & (c.valuta == 'USD') & (c.importanza == '3') & (c.modo_orario == 'ORARIO_ESATTO')
          & c.attuale.notna() & (c.attuale.str.strip() != '') & (c.utc < END_UTC)].copy()
    s['ny'] = pd.DatetimeIndex(s.utc).tz_localize('UTC').tz_convert('America/New_York').tz_localize(None)
    s = s[s.ny.dt.dayofweek < 5]
    g = s.groupby('utc').agg(ny=('ny', 'first'), srv=('ora_server', 'first'), n_voci=('event_id', 'size'),
                             voci=('event_id', lambda x: '+'.join(sorted(x)))).reset_index()
    g = g.sort_values('utc').reset_index(drop=True)
    return g


def forbidden_minutes(c, currencies):
    m = ((c.importanza == '3') & (c.modo_orario == 'ORARIO_ESATTO') & c.valuta.isin(currencies)) | \
        c.evento.isin(['Dichiarazione del FOMC', 'Verbali FOMC', 'Proiezioni Economiche del FOMC'])
    return np.unique(to_min(c.loc[m, 'utc']))


# ---------------------------------------------------------------- costi
def load_costs():
    t = pd.read_csv(COST, sep=';', decimal=',', dtype={'strumento': str, 'contesto': str})
    return {(r.strumento, r.contesto): (float(r.base_bps), float(r.stress_bps)) for r in t.itertuples()}


def fascia(ny):
    hm = ny.hour * 60 + ny.minute
    if 8 * 60 <= hm < 9 * 60: return '08:00-08:59'
    if 9 * 60 <= hm < 10 * 60: return '09:00-09:59'
    if 10 * 60 <= hm < 12 * 60: return '10:00-11:59'
    if 12 * 60 <= hm < 17 * 60: return '12:00-16:59'
    raise ValueError(f'evento fuori fascia {ny}')


def ny_half(ny):
    return f'NY|{ny.hour:02d}:{(ny.minute // 30) * 30:02d}'


# ---------------------------------------------------------------- barre
class Bars:
    def __init__(self, path, start):
        df = pd.read_csv(path, sep='\t', usecols=[0, 1, 2, 5], header=0, names=['d', 't', 'o', 'c'],
                         dtype={'d': str, 't': str, 'o': np.float64, 'c': np.float64})
        sd = start.replace('-', '.')
        df = df[(df.d >= sd) & (df.d < '2024.01.01')]
        ts = pd.to_datetime(df.d + ' ' + df.t, format='%Y.%m.%d %H:%M:%S')
        m = to_min(ts)
        order = np.argsort(m, kind='stable')
        m = m[order]; o = df.o.to_numpy()[order]; cl = df.c.to_numpy()[order]
        keep = np.r_[True, np.diff(m) != 0]  # duplicati (non attesi)
        self.n_dup = int((~keep).sum())
        m, o, cl = m[keep], o[keep], cl[keep]
        day = m // 1440
        diff = np.r_[-1, np.diff(m)]
        same = np.r_[False, day[1:] == day[:-1]]
        dd = pd.DataFrame({'day': day[same], 'diff': diff[same]})
        vc = dd.groupby(['day', 'diff']).size().reset_index(name='n')
        vc = vc.sort_values(['day', 'n', 'diff'], ascending=[True, False, True])
        mode = vc.drop_duplicates('day').set_index('day')['diff']
        valid_days = set(mode.index[mode.to_numpy() == 1])
        v = np.isin(day, np.fromiter(valid_days, dtype=np.int64))
        self.n_days = len(np.unique(day)); self.n_valid_days = len(valid_days)
        self.valid_days = valid_days
        self.m, self.o, self.c = m[v], o[v], cl[v]
        self.first = pd.Timestamp(self.m[0] * 60, unit='s'); self.last = pd.Timestamp(self.m[-1] * 60, unit='s')

    def at(self, t):
        """open della prima barra in [t, t+5]; richiede una barra in [t-5, t)."""
        t = np.asarray(t, dtype=np.int64)
        i = np.searchsorted(self.m, t, side='left')
        out = np.full(t.shape, np.nan)
        ok = i < len(self.m)
        ok &= np.where(ok, self.m[np.minimum(i, len(self.m) - 1)] <= t + 5, False)
        ok &= i >= 1
        ok &= np.where(ok, self.m[np.maximum(i - 1, 0)] >= t - 5, False)
        out[ok] = self.o[i[ok]]
        return out

    def before(self, t, tol=5):
        """close dell'ultima barra in [t-tol, t)."""
        t = np.asarray(t, dtype=np.int64)
        i = np.searchsorted(self.m, t, side='left') - 1
        out = np.full(t.shape, np.nan)
        ok = i >= 0
        ok &= np.where(ok, self.m[np.maximum(i, 0)] >= t - tol, False)
        out[ok] = self.c[i[ok]]
        return out


def sigma_series(bars, rule, start, end='2023-12-31'):
    """sigma_d per data NY d: std(ddof=1) degli ultimi 20 rendimenti validi con data <= d-1."""
    dates = pd.date_range(start, end, freq='D')
    loc = dates + pd.Timedelta(hours=16)
    utc = ny_local_to_utc(loc)
    srv = utc_to_server(utc, rule)
    p = bars.before(to_min(srv), tol=15)
    ok = ~np.isnan(p)
    d_ok = dates[ok]; p_ok = p[ok]
    gap = np.r_[np.nan, (d_ok[1:] - d_ok[:-1]).days.to_numpy().astype(float)]
    r = np.r_[np.nan, np.diff(np.log(p_ok))]
    rv = (gap <= 4)
    rets = pd.Series(r[rv], index=d_ok[rv])
    # sigma per ogni data: rendimenti con data < d
    sig = {}
    rd = rets.index.to_numpy(); rr = rets.to_numpy()
    for d in dates:
        k = np.searchsorted(rd, d.to_datetime64(), side='left')  # rendimenti con data < d
        if k >= 20:
            sig[d.date()] = float(np.std(rr[k - 20:k], ddof=1))
    return sig, rets


# ---------------------------------------------------------------- calcolo per strumento
def compute_instrument(name, feed, events, cal, costs, gross_only=False):
    path, start, rule, curr = feed
    bars = Bars(path, start)
    sig, rets = sigma_series(bars, rule, start)
    forb = forbidden_minutes(cal, curr)
    start_ts = pd.Timestamp(start)
    rows = []
    T_utc = pd.DatetimeIndex(events.utc)
    T_min_utc = to_min(T_utc)
    # istanti di interesse in UTC, conversione in ora server
    def srv_min(utc_minutes):
        u = pd.to_datetime(utc_minutes * 60, unit='s')
        return to_min(utc_to_server(u, rule))
    s_T = srv_min(T_min_utc)
    s_T3 = srv_min(T_min_utc + 3)
    P_pre = bars.before(s_T)
    P_in = bars.at(s_T3)
    for k, ev in events.iterrows():
        tu = T_min_utc[k]
        ny = ev.ny
        d = ny.date()
        rec = dict(strumento=name, chiave=ny.strftime('%Y-%m-%d %H:%M'), utc=tu, ny=ny, anno=ny.year)
        # feed attivo: ora server di T >= inizio feed (data server)
        if s_T[k] < to_min(pd.DatetimeIndex([start_ts]))[0]:
            continue
        if name in ('US100', 'US500') and d in NYSE_CLOSED:
            continue
        # GBPUSD: giornate non M1 dal 01/01 al 07/02/2019 escluse dal feed per protocollo (non 'perse')
        if name == 'GBPUSD' and pd.Timestamp('2019-01-01') <= pd.Timestamp(d) <= pd.Timestamp('2019-02-07') \
                and (s_T[k] // 1440 not in bars.valid_days or s_T3[k] // 1440 not in bars.valid_days):
            continue
        # ingresso escluso se notizia vietata in [T+1, T+5]
        j = np.searchsorted(forb, tu + 1, side='left')
        if j < len(forb) and forb[j] <= tu + 5:
            rec['stato'] = 'news_ingresso'; rows.append(rec); continue
        # E = prima notizia vietata dopo T (minuto diverso da T)
        j = np.searchsorted(forb, tu, side='right')
        E = forb[j] if j < len(forb) else None
        rec['E'] = E
        sg = sig.get(d, np.nan)
        rec['sigma'] = sg
        rec['P_pre'] = P_pre[k]; rec['P_in'] = P_in[k]
        if np.isnan(sg):
            rec['stato'] = 'no_sigma'; rows.append(rec); continue
        if np.isnan(P_pre[k]) or np.isnan(P_in[k]):
            rec['stato'] = 'prezzo_mancante_in'; rows.append(rec); continue
        r0 = math.log(P_in[k] / P_pre[k])
        rec['r0'] = r0
        q = int(np.sign(r0))
        rec['q'] = q
        rec['stato'] = 'ok'
        for H in HS:
            tx = tu + H
            if E is not None:
                tx = min(tx, E - 3)
            rec[f'tx{H}'] = tx
            if tx < tu + 4:
                rec[f'Pout{H}'] = np.nan; rec[f'st{H}'] = 'uscita<T+4'; continue
            po = bars.at(srv_min(np.array([tx])))[0]
            rec[f'Pout{H}'] = po
            rec[f'st{H}'] = 'ok' if not np.isnan(po) else 'prezzo_mancante_out'
            if not gross_only:
                ny_x = pd.Timestamp(tx * 60, unit='s').tz_localize('UTC').tz_convert('America/New_York').tz_localize(None)
                rec[f'ctx_out{H}'] = ny_half(ny_x)
        if not gross_only:
            rec['ctx_in'] = 'S1_evento|' + fascia(ny)
        rows.append(rec)
    info = dict(file=os.path.basename(path), first=str(bars.first), last=str(bars.last), n_days=bars.n_days,
                n_valid_days=bars.n_valid_days, dup=bars.n_dup, n_sigma_days=len(sig))
    return pd.DataFrame(rows), info


def trades_for(df, name, c, H, costs):
    """Restituisce i trade (righe) per configurazione c,H."""
    out = []
    if df.empty:
        return out
    for r in df.itertuples():
        if r.stato != 'ok':
            continue
        if r.q == 0 or abs(r.r0) < c * r.sigma:
            continue
        if getattr(r, f'st{H}') != 'ok':
            continue
        po = getattr(r, f'Pout{H}')
        ret = r.q * math.log(po / r.P_in)
        if costs is None:
            out.append(dict(strumento=name, chiave=r.chiave, ny=r.ny, anno=r.anno, q=r.q, ret=ret, sigma=r.sigma))
            continue
        ctx = r.ctx_in if r.q > 0 else getattr(r, f'ctx_out{H}')
        b, s = costs[(name, ctx)]
        if name == 'EURUSD' or name == 'GBPUSD':
            comm = 5.0 / (100000.0 * r.P_in)
        elif name == 'USDJPY':
            comm = 5.0 / 100000.0
        elif name == 'XAU':
            comm = 6.0 / (100.0 * r.P_in)
        else:
            comm = 0.0
        cb = b / 1e4 + comm
        cs = s / 1e4 + comm + SLIP_STRESS
        out.append(dict(strumento=name, chiave=r.chiave, ny=r.ny, anno=r.anno, q=r.q, ret=ret, sigma=r.sigma,
                        costo_base=cb, costo_stress=cs, netto_base=ret - cb, netto_stress=ret - cs, ctx=ctx))
    return out


# ---------------------------------------------------------------- statistiche
def cr1_t(y, groups):
    y = np.asarray(y, float); n = len(y)
    mu = y.mean()
    e = y - mu
    g = pd.Series(e).groupby(np.asarray(groups)).sum().to_numpy()
    G = len(g)
    if G < 2:
        return mu, np.nan, np.nan, G
    V = (G / (G - 1)) * (g ** 2).sum() / n ** 2
    t = mu / math.sqrt(V)
    p = 1 - stats.t.cdf(t, G - 1)
    return mu, t, p, G


def boot_p(y, groups, B=10000, seed=20261020):
    y = np.asarray(y, float)
    mu = y.mean()
    yc = y - mu
    gid = pd.factorize(np.asarray(groups))[0]
    G = gid.max() + 1
    sums = np.bincount(gid, weights=yc, minlength=G)
    cnts = np.bincount(gid, minlength=G).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, G, size=(B, G))
    bm = sums[idx].sum(1) / cnts[idx].sum(1)
    return float((bm >= mu).mean())


def bh(pvals, q=0.10):
    p = np.asarray(pvals, float); m = len(p)
    o = np.argsort(p)
    thr = q * (np.arange(1, m + 1)) / m
    passed = p[o] <= thr
    k = np.max(np.where(passed)[0]) + 1 if passed.any() else 0
    rej = np.zeros(m, bool); rej[o[:k]] = True
    adj = np.minimum.accumulate((p[o] * m / np.arange(1, m + 1))[::-1])[::-1]
    a = np.empty(m); a[o] = np.minimum(adj, 1)
    return rej, a


def main():
    cal = load_calendar()
    events = build_events(cal)
    costs = load_costs()
    log = {}
    log['n_eventi_T'] = len(events)
    log['ny_orari'] = events.ny.dt.strftime('%H:%M').value_counts().to_dict()
    per_instr = {}; infos = {}
    for nm in INSTR:
        df, info = compute_instrument(nm, FEEDS[nm], events, cal, costs)
        per_instr[nm] = df; infos[nm] = info
        print(nm, info, df.stato.value_counts().to_dict() if not df.empty else {}, flush=True)
    conc = {}
    for nm in CONC:
        df, info = compute_instrument(nm, CONC[nm], events, cal, None, gross_only=True)
        conc[nm] = df; infos[nm + '_FTMO'] = info
        print(nm, 'FTMO', info, df.stato.value_counts().to_dict(), flush=True)
    log['feed'] = infos
    for nm, df in per_instr.items():
        df.drop(columns=[x for x in df.columns if x == 'E'], errors='ignore').to_csv(f'{OUT}/dettaglio_{nm}.csv', sep=';', index=False)

    agg_rows = []; trade_rows = []; results = []; extra = {}
    for c in CS:
        for H in HS:
            tid = f'S1|c={c:.2f}|H{H}'
            tr = []
            for nm in INSTR:
                tr += trades_for(per_instr[nm], nm, c, H, costs)
            T = pd.DataFrame(tr)
            T['zb'] = T.netto_base / T.sigma; T['zs'] = T.netto_stress / T.sigma; T['zl'] = T.ret / T.sigma
            T['bps'] = T.netto_base * 1e4
            for r in T.itertuples():
                trade_rows.append(dict(test_id=tid, strumento=r.strumento, chiave=r.chiave, q=r.q, ret=r.ret,
                                       costo_base=r.costo_base, netto_base=r.netto_base, sigma=r.sigma))
            A = T.groupby('chiave').agg(zb=('zb', 'mean'), zs=('zs', 'mean'), zl=('zl', 'mean'), bps=('bps', 'mean'),
                                        n_str=('zb', 'size'), ny=('ny', 'first')).reset_index().sort_values('chiave')
            A['data'] = A.ny.dt.date; A['anno'] = A.ny.dt.year
            for r in A.itertuples():
                agg_rows.append(dict(test_id=tid, chiave=r.chiave, zb=r.zb, zs=r.zs, zl=r.zl, bps=r.bps, n_str=r.n_str))
            mu, t, p, G = cr1_t(A.zb, A.data)
            n = len(A)
            if n < 30: p = 1.0
            pb = boot_p(A.zb.to_numpy(), A.data.to_numpy())
            # cancelli descrittivi
            pre = A[A.ny < '2020-01-01'].zb.mean(); post = A[A.ny >= '2020-01-01'].zb.mean()
            yrs = A.groupby('anno').agg(n=('zb', 'size'), zb=('zb', 'mean'), bps=('bps', 'mean'))
            yq = yrs[yrs.n >= 10]
            g5 = (len(yq) >= 3) and ((yq.zb > 0).mean() >= 0.6)
            ins = T.groupby('strumento').agg(n=('zb', 'size'), zl=('zl', 'mean'), zb=('zb', 'mean'), zs=('zs', 'mean'),
                                             lordo_bps=('ret', lambda x: x.mean() * 1e4), netto_bps=('bps', 'mean'))
            g6b = (ins.zb > 0).sum() >= len(INSTR) / 2
            # influenza: togliere l'1% delle date (ceil) con il maggior |contributo| alla media
            contrib = A.groupby('data').zb.sum() / n
            kdrop = int(math.ceil(0.01 * len(contrib)))
            drop = contrib.abs().sort_values(ascending=False).index[:kdrop]
            infl = A[~A.data.isin(drop)].zb.mean()
            # concordanza feed (cancello 8)
            ctr = []
            for nm in CONC:
                ctr += trades_for(conc[nm], nm, c, H, None)
            CT = pd.DataFrame(ctr)
            CT['zl'] = CT.ret / CT.sigma
            CA = CT.groupby('chiave').zl.mean()
            # stessi eventi, stessi 3 strumenti sul feed d'inferenza (riferimento)
            Tp = T[T.strumento.isin(CONC.keys())]
            Tp = Tp[Tp.chiave.isin(CA.index)]
            PA = Tp.groupby('chiave').zl.mean()
            common = CA.index.intersection(A.chiave)
            res = dict(test_id=tid, n=n, G=G, lordo_z=float(A.zl.mean()), netto_base_z=float(mu), t=float(t), p=float(p),
                       netto_stress_z=float(A.zs.mean()), netto_base_bps=float(A.bps.mean()), p_boot=pb,
                       pre2020_zb=float(pre), post2020_zb=float(post), anni=yrs.round(4).to_dict('index'), cancello5=bool(g5),
                       strumenti=ins.round(5).to_dict('index'), cancello6b=bool(g6b), influenza_zb=float(infl), k_date_tolte=kdrop,
                       conc_n=int(len(CA)), conc_n_comuni=int(len(common)), conc_lordo_ftmo=float(CA.mean()),
                       conc_lordo_ftmo_comuni=float(CA.loc[common].mean()) if len(common) else np.nan,
                       conc_lordo_pep_stessi_eventi_3str=float(PA.mean()) if len(PA) else np.nan,
                       n_trade=len(T))
            results.append(res)
            print(tid, {k: v for k, v in res.items() if k not in ('anni', 'strumenti')}, flush=True)
    rej, adj = bh([r['p'] for r in results], 0.10)
    for r, rj, a in zip(results, rej, adj):
        r['BH_rifiuta'] = bool(rj); r['BH_p_adj'] = float(a)
    # cancello 6a: stesso c, lordo aggregato > 0 su almeno 2 delle 3 H
    for c in CS:
        sub = [r for r in results if r['test_id'].startswith(f'S1|c={c:.2f}|')]
        npos = sum(r['lordo_z'] > 0 for r in sub)
        for r in sub: r['cancello6a'] = npos >= 2
    for r in results:
        g8 = True if r['conc_n_comuni'] < 100 else (np.sign(r['conc_lordo_ftmo_comuni']) == np.sign(r['lordo_z']))
        r['cancello8'] = bool(g8)
        gates = dict(g1=r['BH_rifiuta'], g2=r['netto_stress_z'] > 0, g3=r['netto_base_bps'] > 0,
                     g4=(r['pre2020_zb'] > 0 and r['post2020_zb'] > 0), g5=r['cancello5'],
                     g6=(r['cancello6a'] and r['cancello6b']), g7=r['influenza_zb'] > 0, g8=r['cancello8'])
        r['cancelli'] = {k: bool(v) for k, v in gates.items()}
        if all(gates.values()):
            r['verdetto'] = 'PROMOSSA'
        elif r['p'] < 0.05 and r['netto_base_z'] > 0:
            r['verdetto'] = 'INDIZIO'
        else:
            r['verdetto'] = 'NULLO'
    # quota di eventi persi per prezzo mancante, per test e anno (livello coppia evento-strumento)
    lost = {}
    for c in CS:
        for H in HS:
            tid = f'S1|c={c:.2f}|H{H}'
            rows = []
            for nm in INSTR:
                df = per_instr[nm]
                for r in df.itertuples():
                    if r.stato in ('news_ingresso', 'no_sigma'):
                        continue
                    if r.stato == 'prezzo_mancante_in':
                        rows.append((r.anno, 1)); continue
                    if r.q == 0 or abs(r.r0) < c * r.sigma:
                        continue
                    st = getattr(r, f'st{H}')
                    if st == 'uscita<T+4':
                        continue
                    rows.append((r.anno, int(st == 'prezzo_mancante_out')))
            L = pd.DataFrame(rows, columns=['anno', 'perso']).groupby('anno').perso.mean().round(4)
            lost[tid] = L.to_dict()
    log['quota_persi'] = lost
    pd.DataFrame(agg_rows).to_csv(f'{OUT}/S1_replica_aggregato.csv', sep=';', index=False)
    pd.DataFrame(trade_rows).to_csv(f'{OUT}/S1_replica_trade.csv', sep=';', index=False)
    with open(f'{OUT}/S1_replica_risultati.json', 'w') as f:
        json.dump(dict(results=results, log=log), f, indent=1, default=str)
    for r in results:
        print(r['test_id'], r['verdetto'], r['cancelli'], 'BHadj', round(r['BH_p_adj'], 4))
    print(json.dumps(lost, indent=0))


if __name__ == '__main__':
    main()
