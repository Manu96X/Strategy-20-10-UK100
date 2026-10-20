import pandas as pd, numpy as np, sys
f, start = sys.argv[1], sys.argv[2]
df = pd.read_csv(f, sep='\t', usecols=['<DATE>','<TIME>','<TICKVOL>'])
df = df[df['<DATE>']>=start.replace('-','.')]
t = pd.to_datetime(df['<DATE>']+' '+df['<TIME>'], format='%Y.%m.%d %H:%M:%S')
df['t']=t.values
df['m']=t.dt.month; df['hm']=t.dt.strftime('%H:%M'); df['y']=t.dt.year
print(f, df['t'].min(), df['t'].max())
for mo in [(1,),(7,),(3,),(11,)]:
    s=df[df.m.isin(mo)]
    g=s.groupby('hm')['<TICKVOL>'].median()
    # jump: ratio vs previous minute
    r=(g/g.shift(1)).sort_values(ascending=False).head(4)
    print(mo, r.round(2).to_dict())
