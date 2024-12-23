"""
This script launches a streamlit app that is the home page of a ADSB 
data based data science project.
"""

import pickle
import streamlit as st

def home_page():

    st.title("ADS-B/Airport Data Science Project")
    st.write("Luke Wilsen")
    st.divider()

    st.header("""**Project Goals**""")
    st.write("""#### 1. Predict the location of airports in Florida.""")
    st.write("#### 2. Track flight paths of specific planes in Florida.")

    if "tracker_geo_dataframe.pkl" not in st.session_state:
        with open("geo_dataframe.pkl", "rb") as f:
            geo_dataframe = pickle.load(f)
        st.session_state["tracker_geo_dataframe.pkl"] = geo_dataframe
