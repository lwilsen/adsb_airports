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