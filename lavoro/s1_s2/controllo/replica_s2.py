#!/usr/bin/env python3
"""Replica cieca indipendente di S2 (PROTOCOLLO_S1_S2.md §2, §4, §5, §6).
Eseguire con: python3 -I replica_s2.py
Uscite nella cartella dello script: S2_REPLICA_aggregato.csv, S2_REPLICA_trade.csv,
S2_REPLICA_test.csv, S2_REPLICA_placebo.csv, S2_REPLICA_diag.txt
"""
import os, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
from scipy import stats
import holidays

OUT = os.path.dirname(os.path.abspath(__file__))
FINE = dt.date(2024, 1, 1)          # scoperta: < 01/01/2024
NYTZ = ZoneInfo('America/New_York')
UTC = ZoneInfo('UTC')
CAL = '/home/user/Strategy-20-10-UK100/calendario_economico.csv'
COSTI = '/home/user/Strategy-20-10-UK100/lavoro/s1_s2/risultati/COSTI_TABELLA_CONGELATA.csv'

# ---------------- strumenti (feed d'inferenza, §1) ----------------
INSTR = {
    'US500': ('/home/user/dati_scoperta_tutti/US500 m1 - Pepperstone.csv', dt.date(2020, 7, 13), 'USA'),
    'US100': ('/home/user/dati_scoperta_tutti/NAS100 m1 - FTPepperstone.csv', dt.date(2017, 6, 9), 'USA'),
    'US30': ('/home/user/dati_s12/scoperta/US30 Pepperstone m1.csv', dt.date(2018, 1, 2), 'USA'),
    'US2000': ('/home/user/dati_s12/scoperta/US2000 m1 Pepperstone.csv', dt.date(2017, 6, 5), 'USA'),
    'GER40': ('/home/user/dati_scoperta_tutti/GER40 Pepperstone m1.csv', dt.date(2020, 6, 11), 'EUROPA'),
    'UK100': ('/home/user/dati_scoperta_tutti/UK100 Pepperstone m1.csv', dt.date(2017, 6, 6), 'EUROPA'),
    'FRA40': ('/home/user/dati_s12/scoperta/FRA40 m1 FTMO.csv', dt.date(2021, 9, 14), 'EUROPA'),
}
# borsa: tz, asta A, offset ingresso (min), pre-apertura X2 (None = escluso da X2)
BORSA = {
    'US500': ('NYSE', 'America/New_York', (16, 0), 1, (9, 25)),
    'US100': ('NYSE', 'America/New_York', (16, 0), 1, (9, 25)),
    'US30': ('NYSE', 'America/New_York', (16, 0), 1, (9, 25)),
    'US2000': ('NYSE', 'America/New_York', (16, 0), 1, (9, 25)),
    'GER40': ('XETRA', 'Europe/Berlin', (17, 30), 6, (8, 55)),
    'UK100': ('LSE', 'Europe/London', (16, 30), 6, (7, 55)),
    'FRA40': ('EPA', 'Europe/Paris', (17, 30), 6, None),
}
VALUTE = {'US500': {'USD'}, 'US100': {'USD'}, 'US30': {'USD'}, 'US2000': {'USD'},
          'GER40': {'EUR', 'USD'}, 'FRA40': {'EUR', 'USD'}, 'UK100': {'GBP', 'USD'}}
FOMC = {'Dichiarazione del FOMC', 'Verbali FOMC', 'Proiezioni Economiche del FOMC'}
# swap (frazione del prezzo, segno = accredito(+)/addebito(-)), §5
SWAP = {'USA': (-0.000227, +0.000011), 'GER40': (-0.000178, -0.000002), 'UK100': (-0.000236, +0.000011)}
SLIP_STRESS = 2 * 0.3e-4


# ---------------- calendari di borsa (§4) ----------------
def giorni_borsa():
    anni = range(2016, 2025)
    nyse_fest = set(holidays.financial_holidays('NYSE', years=anni).keys())
    nyse_mezze = {dt.date(*x) for x in [
        (2016, 11, 25), (2017, 7, 3), (2017, 11, 24), (2018, 7, 3), (2018, 11, 23), (2018, 12, 24),
        (2019, 7, 3), (2019, 11, 29), (2019, 12, 24), (2020, 11, 27), (2020, 12, 24), (2021, 11, 26),
        (2022, 11, 25), (2023, 7, 3), (2023, 11, 24)]}
    uk_fest = set(holidays.UnitedKingdom(subdiv='ENG', years=anni).keys())
    tar_fest = set(holidays.financial_holidays('ECB', years=anni).keys())
    out = {}
    tutti = pd.date_range('2016-01-01', '2024-12-31').date
    for ex in ['NYSE', 'LSE', 'XETRA', 'EPA']:
        aperti, interi = set(), set()
        for d in tutti:
            if d.weekday() >= 5:
                continue
            if ex == 'NYSE':
                if d in nyse_fest: continue
                aperti.add(d)
                if d not in nyse_mezze: interi.add(d)
            elif ex == 'LSE':
                if d in uk_fest: continue
                aperti.add(d)
            elif ex == 'XETRA':
                if d in tar_fest or (d.month == 12 and d.day in (24, 31)): continue
                aperti.add(d); interi.add(d)
            elif ex == 'EPA':
                if d in tar_fest: continue
                aperti.add(d)
                if not (d.month == 12 and d.day in (24, 31)): interi.add(d)
        if ex == 'LSE':
            # mezze sedute: ultimo giorno lavorativo (di borsa) prima di Natale e di Capodanno
            mezze = set()
            for y in range(2016, 2025):
                for lim in (dt.date(y, 12, 25), dt.date(y + 1, 1, 1)):
                    d = lim - dt.timedelta(days=1)
                    while d not in aperti:
                        d -= dt.timedelta(days=1)
                    mezze.add(d)
            interi = aperti - mezze
        out[ex] = (aperti, interi)
    return out


# ---------------- dati M1 ----------------
def carica(path, start):
    df = pd.read_csv(path, sep='\t', usecols=['<DATE>', '<TIME>', '<OPEN>', '<CLOSE>'],
                     dtype={'<DATE>': str, '<TIME>': str, '<OPEN>': np.float64, '<CLOSE>': np.float64})
    s = start.strftime('%Y.%m.%d')
    df = df[df['<DATE>'] >= s]
    t = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'], format='%Y.%m.%d %H:%M:%S')
    tm = t.values.astype('datetime64[m]').astype(np.int64)
    o = df['<OPEN>'].values; c = df['<CLOSE>'].values
    ordn = np.argsort(tm, kind='stable'); tm, o, c = tm[ordn], o[ordn], c[ordn]
    assert (np.diff(tm) > 0).all(), 'timestamp duplicati'
    assert pd.Timestamp(tm.max(), unit='m') < pd.Timestamp('2024-01-01'), 'dati oltre il 2023'
    # barre valide: passo modale fra barre consecutive del giorno server = 1 minuto
    day = tm // 1440
    d = np.diff(tm); same = day[1:] == day[:-1]
    dd = pd.DataFrame({'day': day[1:][same], 'd': d[same]})
    mode = dd.groupby('day')['d'].agg(lambda x: x.value_counts().sort_index().idxmax())
    # moda: in caso di parita' si prende il passo piu' piccolo (value_counts ordinato per conteggio poi indice)
    okdays = set(mode.index[mode.values == 1])
    keep = np.isin(day, np.fromiter(okdays, dtype=np.int64))
    nd_all = len(np.unique(day)); nd_ok = len(okdays)
    return tm[keep], o[keep], c[keep], (nd_all, nd_ok)


class Serie:
    def __init__(self, tm, o, c):
        self.tm, self.o, self.c = tm, o, c

    def a(self, t):
        """prezzo a t: open della prima barra in [t, t+5]; richiede una barra in [t-5, t)."""
        i = np.searchsorted(self.tm, t, 'left')
        if i >= len(self.tm) or self.tm[i] > t + 5: return np.nan
        if i == 0 or self.tm[i - 1] < t - 5: return np.nan
        return self.o[i]

    def prima(self, t, tol=5):
        """prezzo prima di t: close dell'ultima barra che inizia in [t-tol, t)."""
        i = np.searchsorted(self.tm, t, 'left') - 1
        if i < 0 or self.tm[i] < t - tol: return np.nan
        return self.c[i]


def srv(d, hm, tz, plus=0):
    """istante locale (data d, ora hm, fuso tz) -> minuti epoch nell'ora server del feed (NY+7)."""
    loc = dt.datetime(d.year, d.month, d.day, hm[0], hm[1], tzinfo=ZoneInfo(tz)) + dt.timedelta(minutes=plus)
    # nota: aggiunta in wall-clock locale; nessuna asta/uscita cade vicino a un cambio d'ora (notte di domenica)
    ny = loc.astimezone(NYTZ).replace(tzinfo=None) + dt.timedelta(hours=7)
    return int((np.datetime64(ny, 'm')).astype(np.int64))


def m2str(m):
    return str(np.datetime64(int(m), 'm'))


# ---------------- calendario: notizie vietate ----------------
def notizie():
    cal = pd.read_csv(CAL, sep=';', encoding='latin-1', skiprows=1, dtype=str)
    cal['imp'] = pd.to_numeric(cal['importanza'])
    utc = pd.to_datetime(cal['ora_server'], format='%Y.%m.%d %H:%M') - pd.Timedelta(hours=3)  # UTC+3 fisso
    ny = utc.dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)
    cal['srv'] = (ny + pd.Timedelta(hours=7)).values.astype('datetime64[m]').astype(np.int64)
    cal['utc'] = utc
    cal = cal[cal['utc'] < pd.Timestamp('2024-01-10')]
    out = {}
    for k, vals in VALUTE.items():
        m = ((cal['imp'] == 3) & (cal['modo_orario'] == 'ORARIO_ESATTO') & cal['valuta'].isin(vals)) | \
            (cal['evento'].isin(FOMC) & (cal['valuta'] == 'USD') & (cal['modo_orario'] == 'ORARIO_ESATTO'))
        out[k] = np.unique(cal.loc[m, 'srv'].values)
    return out, cal


def costi():
    t = pd.read_csv(COSTI, sep=';', decimal=',', dtype={'strumento': str, 'contesto': str})
    return {(r.strumento, r.contesto): (float(r.base_bps), float(r.stress_bps)) for r in t.itertuples()}


# ---------------- costruzione per strumento ----------------
def costruisci(nome, cal_borsa, viet, C):
    path, start, paniere = INSTR[nome]
    ex, tz, A, off, pre = BORSA[nome]
    tm, o, c, (nd_all, nd_ok) = carica(path, start)
    S = Serie(tm, o, c)
    aperti, interi = cal_borsa[ex]
    giorni = pd.date_range(start, FINE - dt.timedelta(days=1)).date
    # sigma: chiusure "prima dell'asta" (tolleranza 15 min), rendimenti log fra chiusure valide
    # consecutive distanti <= 4 giorni di calendario; sigma_d = std(ddof=1) ultimi 20 fino a d-1
    chi = []
    for d in giorni:
        p = S.prima(srv(d, A, tz), tol=15)
        if np.isfinite(p): chi.append((d, p))
    rets = []  # (data, r)
    for (d0, p0), (d1, p1) in zip(chi[:-1], chi[1:]):
        if (d1 - d0).days <= 4:
            rets.append((d1, np.log(p1 / p0)))
    rd = np.array([r[0] for r in rets]); rv = np.array([r[1] for r in rets])
    sig = {}
    for d in giorni:
        k = np.searchsorted(rd, d, 'left')  # rendimenti con data <= d-1
        if k >= 20: sig[d] = float(np.std(rv[k - 20:k], ddof=1))
    trade = []
    diag = {'giorni_validi': (nd_all, nd_ok), 'mancanti': {}}
    for d in giorni:
        if d not in interi: continue
        for kind in ('main', 'placebo'):
            Ak = A if kind == 'main' else (A[0] - 1, A[1])  # A' = A - 60 minuti
            tA = srv(d, Ak, tz)
            p_a = S.prima(tA); p_a15 = S.prima(srv(d, Ak, tz, -15))
            t_in = srv(d, Ak, tz, off)
            p_in = S.a(t_in)
            uscite = [('X1', srv(d, Ak, tz, 45))]
            if kind == 'main' and pre is not None:
                d1 = d + dt.timedelta(days=1)
                if d1 in aperti:  # giorno di borsa successivo = giorno di calendario seguente
                    tp = srv(d1, pre, tz)
                    nv = viet[nome]
                    j = np.searchsorted(nv, t_in, 'right')  # prima notizia vietata dopo l'ingresso
                    tx = tp
                    if j < len(nv) and nv[j] < tp:
                        tx = nv[j] - 3
                    uscite.append(('X2', tx if tx > t_in else None))
            for ux, tx in uscite:
                rec = dict(strumento=nome, paniere=paniere, data=d, kind=kind, uscita=ux, sigma=sig.get(d, np.nan))
                ok = True
                if tx is None:
                    rec['motivo'] = 'uscita_prima_ingresso'; ok = False
                else:
                    p_out = S.a(tx)
                    if not (np.isfinite(p_a) and np.isfinite(p_a15) and np.isfinite(p_in) and np.isfinite(p_out)):
                        rec['motivo'] = 'prezzo_mancante'; ok = False
                if ok and not np.isfinite(rec['sigma']):
                    rec['motivo'] = 'sigma_mancante'; ok = False
                if ok:
                    m = np.log(p_a / p_a15)
                    q = -np.sign(m)
                    r = np.log(p_out / p_in)
                    ctx_in = 'S2|ingresso' if kind == 'main' else 'S2|placebo_ingresso'
                    ctx_out = ('S2|' + ux) if kind == 'main' else 'S2|placebo_X1'
                    sb_in, ss_in = C[(nome, ctx_in)]; sb_out, ss_out = C[(nome, ctx_out)]
                    if q > 0:
                        spb, sps = sb_in / 1e4, ss_in / 1e4
                    else:
                        spb, sps = sb_out / 1e4, ss_out / 1e4
                    swb = sws = 0.0
                    if ux == 'X2' and q != 0 and (tx // 1440) > (t_in // 1440):  # una notte (rollover server)
                        key = 'USA' if paniere == 'USA' else nome
                        lg, sh = SWAP[key]
                        sw = lg if q > 0 else sh
                        swb = sw; sws = sw * 1.5 if sw < 0 else sw
                    cb = spb - swb  # costo base (frazione; swap a credito riduce il costo)
                    cs = sps + SLIP_STRESS - sws
                    rec.update(m=m, q=q, p_pre15=p_a15, p_pre=p_a, p_in=p_in, p_out=p_out, t_in=m2str(t_in),
                               t_out=m2str(tx), ret=r, lordo=q * r, costo_base=cb, costo_stress=cs,
                               netto_base=q * r - cb, netto_stress=q * r - cs, motivo='')
                trade.append(rec)
    return pd.DataFrame(trade), diag


def t_cr1(y, g):
    y = np.asarray(y, float); n = len(y)
    if n < 2: return np.nan, 1.0, 0
    df = pd.DataFrame({'y': y, 'g': g})
    mu = y.mean(); e = y - mu
    sg = df.assign(e=e).groupby('g')['e'].sum().values
    G = len(sg)
    V = (sg ** 2).sum() / n ** 2 * (G / (G - 1)) * ((n - 1) / (n - 1))
    t = mu / np.sqrt(V)
    p = 1 - stats.t.cdf(t, G - 1)
    if n < 30: p = 1.0
    return t, p, G


def boot(y, seed=20261020, B=10000):
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float); n = len(y); mu = y.mean(); yc = y - mu
    idx = rng.integers(0, n, size=(B, n))
    bm = yc[idx].mean(1)
    return float((bm >= mu).mean())


def main():
    cal_borsa = giorni_borsa()
    viet, cal = notizie()
    C = costi()
    tutti, diag = [], {}
    for nome in INSTR:
        df, dg = costruisci(nome, cal_borsa, viet, C)
        tutti.append(df); diag[nome] = dg
        print(nome, len(df), dg['giorni_validi'], flush=True)
    T = pd.concat(tutti, ignore_index=True)
    T.to_pickle(os.path.join(OUT, 'trade_raw.pkl'))
    righe_trade, righe_agg, righe_test, righe_plac = [], [], [], []
    lines = []
    for paniere in ('USA', 'EUROPA'):
        for c in (0.0, 0.10):
            for kind, uscite in (('main', ('X1', 'X2')), ('placebo', ('X1',))):
                for ux in uscite:
                    tid = f'S2|{paniere}|c={c:.2f}|{ux}' + ('|placebo_A-60' if kind == 'placebo' else '')
                    sub = T[(T.paniere == paniere) & (T.kind == kind) & (T.uscita == ux)]
                    elig = sub
                    ok = sub[sub.motivo == ''].copy()
                    ok = ok[(ok.m != 0) & (ok.m.abs() >= c * ok.sigma)]
                    ok['zb'] = ok.netto_base / ok.sigma; ok['zs'] = ok.netto_stress / ok.sigma
                    ok['zl'] = ok.lordo / ok.sigma; ok['bps'] = ok.netto_base * 1e4
                    for r in ok.itertuples():
                        righe_trade.append((tid, r.strumento, r.data.isoformat(), int(r.q), r.ret, r.costo_base,
                                            r.netto_base, r.sigma, r.m, r.t_in, r.t_out, r.p_in, r.p_out,
                                            r.costo_stress, r.netto_stress))
                    ag = ok.groupby('data').agg(zb=('zb', 'mean'), zs=('zs', 'mean'), zl=('zl', 'mean'),
                                                bps=('bps', 'mean'), n_str=('zb', 'size')).reset_index()
                    for r in ag.itertuples():
                        righe_agg.append((tid, r.data.isoformat(), r.zb, r.zs, r.zl, r.bps, r.n_str))
                    t, p, G = t_cr1(ag.zb.values, ag.data.values)
                    pre = ag[ag.data < dt.date(2020, 1, 1)].zb; post = ag[ag.data >= dt.date(2020, 1, 1)].zb
                    ag['y'] = [d.year for d in ag.data]
                    anni = ag.groupby('y').agg(n=('zb', 'size'), mb=('zb', 'mean'), bps=('bps', 'mean'))
                    per_str = ok.groupby('strumento').agg(n=('zb', 'size'), zb=('zb', 'mean'), zl=('zl', 'mean'),
                                                          bps=('bps', 'mean'))
                    # influenza: togli 1% delle date con |contributo| massimo
                    k = int(np.floor(0.01 * len(ag)))
                    infl = ag.loc[ag.zb.abs().sort_values(ascending=False).index[k:], 'zb'].mean() if len(ag) else np.nan
                    res = dict(test_id=tid, n=len(ag), n_trade=len(ok), lordo_z=ag.zl.mean(), netto_base_z=ag.zb.mean(),
                               t=t, p=p, G=G, netto_stress_z=ag.zs.mean(), netto_base_bps=ag.bps.mean(),
                               meta1=pre.mean(), meta2=post.mean(), n_meta1=len(pre), n_meta2=len(post),
                               p_boot=boot(ag.zb.values) if len(ag) > 1 else np.nan, infl1pct=infl)
                    (righe_plac if kind == 'placebo' else righe_test).append(res)
                    # mancanti per anno (sugli eleggibili: giorni interi di borsa x strumento)
                    el = elig.copy(); el['y'] = [d.year for d in el.data]
                    mm = el.groupby('y').apply(lambda x: (x.motivo == 'prezzo_mancante').mean(), include_groups=False)
                    lines.append(f'== {tid}: ' + ', '.join(f'{k_}={v_}' for k_, v_ in res.items()
                                                              if k_ != 'test_id'))
                    lines.append('  per anno:\n' + anni.to_string())
                    lines.append('  per strumento:\n' + per_str.to_string())
                    lines.append('  quota prezzo mancante per anno: ' + ', '.join(f'{y}:{v:.3f}' for y, v in mm.items()))
                    lines.append('  motivi esclusione: ' + str(elig.motivo.value_counts().to_dict()))
    pd.DataFrame(righe_agg, columns=['test_id', 'chiave', 'zb', 'zs', 'zl', 'bps', 'n_str']).to_csv(
        os.path.join(OUT, 'S2_REPLICA_aggregato.csv'), sep=';', index=False)
    pd.DataFrame(righe_trade, columns=['test_id', 'strumento', 'chiave', 'q', 'ret', 'costo_base', 'netto_base',
                                       'sigma', 'm', 't_in_srv', 't_out_srv', 'p_in', 'p_out', 'costo_stress',
                                       'netto_stress']).to_csv(os.path.join(OUT, 'S2_REPLICA_trade.csv'), sep=';', index=False)
    R = pd.DataFrame(righe_test); P = pd.DataFrame(righe_plac)
    # BH q=0,10 sugli 8
    pv = R.p.values; o = np.argsort(pv); m_ = len(pv); passa = np.zeros(m_, bool)
    kmax = 0
    for i, j in enumerate(o, 1):
        if pv[j] <= 0.10 * i / m_: kmax = i
    passa[o[:kmax]] = True
    R['BH'] = passa
    R.to_csv(os.path.join(OUT, 'S2_REPLICA_test.csv'), sep=';', index=False)
    P.to_csv(os.path.join(OUT, 'S2_REPLICA_placebo.csv'), sep=';', index=False)
    with open(os.path.join(OUT, 'S2_REPLICA_diag.txt'), 'w') as f:
        f.write(R.to_string() + '\n\nPLACEBO\n' + P.to_string() + '\n\n' + '\n'.join(lines) + '\n')
        f.write('\nvalidita giorni (tot, validi): ' + str({k: v['giorni_validi'] for k, v in diag.items()}) + '\n')
    pd.set_option('display.width', 250)
    print(R.to_string()); print(P.to_string())


if __name__ == '__main__':
    main()
