"""Convert the data into a sqlite database here"""

import sqlite3
import pandas as pd

df_400m = pd.read_csv("adsb_data_400/adsb_data_400m.csv")

conn = sqlite3.connect("adsb_data.db")

df_400m.to_sql("400m", conn, if_exists="replace", index=False)

conn.commit()
conn.close()