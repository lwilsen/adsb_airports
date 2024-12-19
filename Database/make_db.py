"""
Converts the CSV data into a SQLite database.

Reads the 'adsb_data_400m.csv' file into a Pandas DataFrame, then creates a SQLite database 
named 'adsb_data.db'. The DataFrame is inserted into a table named '400m' within the database, 
replacing any existing table with the same name.
"""

import sqlite3
import pandas as pd

geo_dataframe_expanded = pd.read_csv("geo_dataframe.csv")

conn = sqlite3.connect("adsb_data.db")

geo_dataframe_expanded.to_sql("gdf_expanded", conn, if_exists="replace", index=False)

conn.commit()
conn.close()
