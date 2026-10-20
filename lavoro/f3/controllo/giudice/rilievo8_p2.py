# Rilievo 8: P2 (lunedi' contro martedi'-venerdi') anche per A2 e A3, con la stessa formula di analizza_f3; A1 come controllo
import sys; sys.path.insert(0, "/home/user/Strategy-20-10-UK100/lavoro/f3/controllo/giudice")
from base_g import *
T = trade_file()
P2f = pd.read_csv(RIS + "P2_scoperta.csv", sep=";", decimal=",")
for fk in ["PEP", "FTMO"]:
    C = pickle.load(open(f"cache_UK100_{fk}.pkl", "rb")); feed, tab, bs = C["feed"], C["tab"], C["bs"]
    for c in ["A1", "A2", "A3"]:
        _, tipo, reg, m, usc, k = E.CELLE[c]
        e = M.esiti_tutte_le_barre(feed, bs, m, usc, tab, M.SCENARI["base"])
        d1 = E.trades_df(M.segnali_R1(bs, e, (0,), 40.0, True), bs, c, fk, "base")
        d2 = E.trades_df(M.segnali_R1(bs, e, (1, 2, 3, 4), 40.0, True), bs, c + "_P2", fk, "base")
        f = T[(T.cella == c) & (T.feed == fk) & (T.scenario == "base")]
        assert np.allclose(f.R.values, d1.R.values)
        s1, s2 = M.statistiche(d1, nboot=10), M.statistiche(d2, nboot=10)
        se1, se2 = s1["media"] / s1["t"], s2["media"] / s2["t"]; diff = s1["media"] - s2["media"]
        rif = P2f[(P2f.cella == c) & (P2f.feed == fk)]
        print(f"P2 {c} {fk}: lun n={s1['n']} media={s1['media']:+.4f} | mar-ven n={s2['n']} media={s2['media']:+.4f} | diff={diff:+.4f} t_diff={diff/np.sqrt(se1**2+se2**2):.3f}"
              + (f"  [file: diff={rif['diff'].iat[0]:+.4f} t={rif.t_diff.iat[0]:.3f}]" if len(rif) else "  [assente nel file]"))
