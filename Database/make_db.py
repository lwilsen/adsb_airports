"""
Converts the CSV data into a SQLite database.

Reads the 'adsb_data_400m.csv' file into a Pandas DataFrame, then creates a SQLite database 
named 'adsb_data.db'. The DataFrame is inserted into a table named '400m' within the database, 
replacing any existing table with the same name.
"""

import sqlite3
import pandas as pd

df_400m = pd.read_csv("adsb_data_400m.csv")

df_expanded = pd.read_csv("adsb_data_400m_expanded.csv")

geo_dataframe_expanded = pd.read_csv("geo_dataframe.csv")

conn = sqlite3.connect("adsb_data.db")

df_400m.to_sql("400m", conn, if_exists="replace", index=False)

df_expanded.to_sql("expanded", conn, if_exists="replace", index=False)

geo_dataframe_expanded.to_sql("gdf_expanded", conn, if_exists="replace", index=False)

conn.commit()
conn.close()
