import pandas as pd
df = pd.read_csv("Titanic.csv")
from config import COLS_DROP
from preprocessing import drop_cols
drop_cols(df,COLS_DROP)