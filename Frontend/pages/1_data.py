"""
This script explores a dataset of grounded airplanes.

It reads a pickled DataFrame from 'grounded.pkl' and performs the following:

1. **Displays a descriptive text:** Provides context about the data and analysis.
2. **Displays a table:** Shows a tabular representation of the first few rows of the DataFrame.
3. **Plots histograms:** Visualizes the distribution of latitude, longitude, and ground speed using Matplotlib.
    - Latitude histogram: Shows the frequency of different latitude values.
    - Longitude histogram: Shows the frequency of different longitude values.
    - Ground Speed histogram: Shows the frequency of different ground speed values.
4. **Displays the plots:** Uses Streamlit to render the Matplotlib figures in the web app.
"""

import streamlit as st
import pickle
import matplotlib.pyplot as plt


st.title("Data Exploration!")

st.write('''I was able to identify when airplanes are on the ground using 
         the alt_barom column. Then I used the latitude and longitude 
         of those airplanes to make a prediction that there is an airport 
         there.''')

with open('grounded.pkl', 'rb') as f:
    grounded = pickle.load(f)

st.table(grounded.head())

fig1 = plt.figure( figsize=(11, 7))
grounded['lat'].hist(bins=20)
plt.xlabel('Latitude')
plt.ylabel('Frequency')
plt.title('Histogram of Latitude')
st.pyplot(fig1)

fig2 = plt.figure(figsize=(11,7))
grounded['lon'].hist(bins=20)
plt.xlabel('Longitude')
plt.ylabel('Frequency')
plt.title('Histogram of Longitude')
st.pyplot(fig2)

fig4 = plt.figure(figsize=(11,7))
grounded['gs'].hist(bins=20)
plt.xlabel('Ground Speed')
plt.ylabel('Frequency')
plt.title('Histogram of Ground Speed')
st.pyplot(fig4)