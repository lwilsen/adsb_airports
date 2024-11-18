import streamlit as st

st.title("Future Plans")

st.header("Better Satellite images")
st.write('''
Ideally it would be nice to have access to more advanced satellite imagery,
         but that's a little too expensive for the scope of this project.
''')

st.header("ADS-B data")
st.write('''
The ADS-B data I collected was only from a couple of days, and so when I pull more data, 
         it will be easier to identify airports and helipads. 
         I also am going to collect data on the actual types of the airplanes (model number) to better 
         understand who might be using specific airports.
''')

st.header("Containerize")
st.write('''
Right now this whole app runs through streamlit, so 
         I'm also going to create a fast-api backend and a docker container for this app.
''')