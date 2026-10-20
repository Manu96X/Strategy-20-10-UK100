# Rilievo 2: sessione LSE troncata alle 12:30 il 24/12 e il 31/12 (semi-festivi) -> ricostruisce barre, indicatori, celle A1-A7
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
def barre_sessione_semi(feed, tz, apre, chiude, festivi_loc):
    loc = M.barre.ora_locale(feed.m1.ts, tz)
    ah, am = map(int, apre.split(":")); ch, cm = map(int, chiude.split(":"))
    mins = loc.dt.hour * 60 + loc.dt.minute
    a0 = ah * 60 + am
    data_loc = loc.dt.normalize()
    semi = (data_loc.dt.month == 12) & data_loc.dt.day.isin([24, 31])
    c0s = np.where(semi, 12 * 60 + 30, ch * 60 + cm)
    sel = (mins >= a0) & (mins < c0s) & loc.notna() & (data_loc.dt.weekday < 5) & ~data_loc.dt.date.isin(festivi_loc)
    x = feed.m1[sel].copy()
    x["dl"] = data_loc[sel]; x["k"] = ((mins[sel] - a0) // 60).astype(int)
    g = x.groupby(["dl", "k"], sort=True)
    b = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "n_m1": g.size()}).reset_index()
    c0b = np.where((b.dl.dt.month == 12) & b.dl.dt.day.isin([24, 31]), 12 * 60 + 30, ch * 60 + cm)
    fine_loc = b.dl + pd.to_timedelta(np.minimum(a0 + (b.k + 1) * 60, c0b), unit="m")
    b["fine_srv"] = M.locale_a_server(fine_loc, tz).values
    b["data"] = b.dl.dt.date; b["dow"] = b.dl.dt.weekday; b["anno"] = b.dl.dt.year
    return b.dropna(subset=["fine_srv"]).reset_index(drop=True)
T = trade_file(); cfg = M.SIMBOLI["UK100"]; fest_loc = M.festivi_borsa("ENG", E.ANNI)
for fk in ["PEP", "FTMO"]:
    C = pickle.load(open(f"cache_UK100_{fk}.pkl", "rb")); feed, tab, bs, bc = C["feed"], C["tab"], C["bs"], C["bc"]
    s = bs[(pd.to_datetime(bs.dl).dt.month == 12) & pd.to_datetime(bs.dl).dt.day.isin([24, 31])]
    print(fk, "barre sess del 24 e 31/12:", len(s), " di cui k>=5:", int((s.k >= 5).sum()), " giorni con k>=5:", sorted(set(s[s.k >= 5].data.astype(str))))
    bs2 = M.indicatori(barre_sessione_semi(feed, cfg["tz"], cfg["apre"], cfg["chiude"], fest_loc))
    print(fk, "barre:", len(bs), "->", len(bs2))
    for scen in ["base", "stress"]:
        out, _ = esegui(feed, bs2, bc, tab, ["A1", "A2", "A3", "A4", "A5", "A6", "A7"], scen, fk)
        for c, df in out.items():
            f = T[(T.cella == c) & (T.feed == fk) & (T.scenario == scen)]
            st = M.statistiche(df, nboot=10)
            same = len(f) == len(df) and (f.ts_in.values == df.ts_in.values).all() and np.allclose(f.R.values, df.R.values)
            print(f"  {fk} {scen:6s} {c} n {len(f)}->{len(df)} media {f.R.mean():+.5f} -> {df.R.mean():+.5f} ({df.R.mean()-f.R.mean():+.5f}) t {st['t']:.3f} identici={same}")
            if not same and scen == "base":
                a = set(zip(f.ts_in, f.R.round(6))); b2 = set(zip(df.ts_in, df.R.round(6)))
                for t, r in sorted(a - b2): print(f"       solo codice : {pd.Timestamp(int(t))} R {r:+.4f}")
                for t, r in sorted(b2 - a): print(f"       solo variante: {pd.Timestamp(int(t))} R {r:+.4f}")
