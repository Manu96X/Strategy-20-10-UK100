import pandas as pd, numpy as np
T = pd.read_csv("/home/user/Strategy-20-10-UK100/lavoro/f3/risultati/TRADE_scoperta.csv", sep=";", decimal=",")
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
print(T.shape)
print(T.groupby(["cella","feed","scenario"]).tipo.value_counts().unstack(fill_value=0))
