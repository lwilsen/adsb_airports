"""
This script launches a streamlit app that is the home page of a ADSB data based data science project.
"""
import streamlit as st

st.title("ADS-B/Airport Data Science Project")
st.write("Luke Wilsen")
st.divider()

st.header('''**Project Goal**''')
st.write('''Predict the location of airports in Florida''')

st.subheader("About the Data")
st.write('''
- This data contains information about aircraft and was obtained from an online API of ADSB data, courtesy of Brett Waugh. (Thanks Brett!)

### What is ADS-B Data?

ADS-B (Automatic Dependent Surveillance–Broadcast) is a surveillance technology used in aviation for tracking aircraft. It provides precise location and status information through messages transmitted by aircraft and picked up by ground stations or satellites.

Below is a detailed explanation of the different fields available in the data.

---

## Basic Aircraft Information
  
- **`alt_baro`**: Barometric altitude in feet.  
- **`gs`**: Ground speed of the aircraft in knots.  
- **`track`**: Heading of the aircraft in degrees, measured clockwise from north.  
- **`category`**: Classification of the aircraft based on size and type.  

---

## Position and Navigation Data

- **`lat`**: Latitude in degrees.  
- **`lon`**: Longitude in degrees.  

---''')
