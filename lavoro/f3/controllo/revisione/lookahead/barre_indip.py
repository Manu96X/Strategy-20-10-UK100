# Ricostruzione INDIPENDENTE delle barre di sessione: offset UTC calcolati a mano con le regole DST USA/UE/UK
sys_path_hack = __import__("sys").path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3")
import sys, pickle, numpy as np, pandas as pd, datetime as dt
sim, fk = sys.argv[1], sys.argv[2]
d = pickle.load(open(f"cache_{sim}_{fk}.pkl","rb")); feed, bs = d["feed"], d["bs"]
def nth_sunday(y, m, n):
    d0 = dt.date(y, m, 1); first = d0 + dt.timedelta(days=(6 - d0.weekday()) % 7); return first + dt.timedelta(weeks=n-1)
def last_sunday(y, m):
    d0 = dt.date(y, m+1, 1) - dt.timedelta(days=1); return d0 - dt.timedelta(days=(d0.weekday()+1) % 7)
anni = range(2016, 2025)
# USA: DST da 2a domenica marzo 02:00 locale (=07:00 UTC) a 1a domenica nov 02:00 EDT (=06:00 UTC)
us = {y: (pd.Timestamp(nth_sunday(y,3,2)) + pd.Timedelta(hours=7), pd.Timestamp(nth_sunday(y,11,1)) + pd.Timedelta(hours=6)) for y in anni}
# UE/UK: DST da ultima dom. marzo 01:00 UTC a ultima dom. ottobre 01:00 UTC
eu = {y: (pd.Timestamp(last_sunday(y,3)) + pd.Timedelta(hours=1), pd.Timestamp(last_sunday(y,10)) + pd.Timedelta(hours=1)) for y in anni}
ts = feed.m1.ts
# server = NY + 7 -> UTC = server - 7 - offsetNY ; offsetNY = -5 (EST) o -4 (EDT): UTC = server - 2 (EST) o server - 3 (EDT)
utc_est = ts - pd.Timedelta(hours=2); utc_edt = ts - pd.Timedelta(hours=3)
y = ts.dt.year.values
a = np.array([us[v][0] for v in y], dtype="datetime64[ns]"); b_ = np.array([us[v][1] for v in y], dtype="datetime64[ns]")
inedt = (utc_edt.values >= a) & (utc_edt.values < b_)
utc = pd.Series(np.where(inedt, utc_edt.values, utc_est.values))
tzname = {"UK100": ("eu", 0, "08:00", "16:30"), "GER40": ("eu", 1, "09:00", "17:30"), "US500": ("us", -5, "09:30", "16:00"), "US100": ("us", -5, "09:30", "16:00")}[sim]
regole, base, apre, chiude = tzname
yu = utc.dt.year.values
R = eu if regole == "eu" else us
a = np.array([R[v][0] for v in yu], dtype="datetime64[ns]"); b_ = np.array([R[v][1] for v in yu], dtype="datetime64[ns]")
dst = (utc.values >= a) & (utc.values < b_)
loc = utc + pd.to_timedelta(base + dst.astype(int), unit="h")
ah, am = map(int, apre.split(":")); ch, cm = map(int, chiude.split(":")); a0, c0 = ah*60+am, ch*60+cm
mins = loc.dt.hour*60 + loc.dt.minute
sel = (mins >= a0) & (mins < c0) & (loc.dt.weekday < 5)
x = feed.m1[sel.values].copy(); x["dl"] = loc[sel.values].dt.normalize().values; x["k"] = ((mins[sel.values] - a0)//60).values
g = x.groupby(["dl","k"])
B = pd.DataFrame({"o":g.o.first(),"h":g.h.max(),"l":g.l.min(),"c":g.c.last(),"n":g.size(),"ultimo_m1":g.ts.max()}).reset_index()
# fine nominale in server: locale fine -> UTC -> server
fl = B.dl + pd.to_timedelta(np.minimum(a0+(B.k+1)*60, c0), unit="m")
# locale -> UTC (prova le due ipotesi di DST)
fu = fl - pd.Timedelta(hours=base)
yy = fu.dt.year.values
a = np.array([R[v][0] for v in yy], dtype="datetime64[ns]"); b_ = np.array([R[v][1] for v in yy], dtype="datetime64[ns]")
fu2 = fu - pd.Timedelta(hours=1)
fu = pd.Series(np.where((fu2.values >= a) & (fu2.values < b_), fu2.values, fu.values))
ya = fu.dt.year.values
a = np.array([us[v][0] for v in ya], dtype="datetime64[ns]"); b_ = np.array([us[v][1] for v in ya], dtype="datetime64[ns]")
B["fine_srv"] = np.where((fu.values >= a) & (fu.values < b_), (fu + pd.Timedelta(hours=3)).values, (fu + pd.Timedelta(hours=2)).values)
# confronto con motore (che esclude i festivi: confronto sull'intersezione)
mm = bs.merge(B, on=["dl","k"], how="outer", suffixes=("_m","_i"), indicator=True)
print("solo motore:", (mm._merge=="left_only").sum(), " solo indipendente:", (mm._merge=="right_only").sum(), " comuni:", (mm._merge=="both").sum())
both = mm[mm._merge=="both"]
for c in ["o","h","l","c"]: print(c, "differenze:", int((both[c+"_m"] != both[c+"_i"]).sum()))
print("n_m1 diff:", int((both.n_m1 != both.n).sum()), " fine_srv diff:", int((both.fine_srv_m != both.fine_srv_i).sum()))
print("barre con ultimo M1 >= fine nominale (look-ahead):", int((both.ultimo_m1 >= both.fine_srv_m).sum()))
print("ultimo M1 + 1min > fine:", int((both.ultimo_m1 + pd.Timedelta(minutes=1) > both.fine_srv_m).sum()))
ro = mm[mm._merge=="right_only"]
print("giorni solo indipendente (festivi esclusi dal motore?):", sorted(set(ro.dl.dt.date))[:40], len(set(ro.dl.dt.date)))
# esempi DST disallineati
for day in ["2023-03-13","2023-03-27","2023-10-30","2023-11-06","2019-03-11","2019-11-01"]:
    r = bs[bs.dl == pd.Timestamp(day)][["dl","k","fine_srv","n_m1"]].head(2)
    print(day, r.values.tolist())
