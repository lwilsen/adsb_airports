import streamlit as st
import pandas as pd
import requests
import pickle

if st.sidebar.button("Reset Page"):
    st.markdown(
        """
        <script>
        document.documentElement.scrollTop = 0;
        </script>
        """,
        unsafe_allow_html=True,
    )



st.title("Aircraft Category Prediction")

data = [
    [-83.19397, 2, 3868, 10.0, 442.4, 199, 2, -1664.0, 30200.0, 152.1, 4291, 31975.0, 27.791428, -11.597031, 11008.0, 2.0, 14.0],
    [-83.099318, 2, 1686, 10.0, 225.6, 163, 2, -1536.0, 8300.0, 134.46, 1861, 8550.0, 27.873385, -11.597031, 3008.0, 2.0, 3.0],
    [-82.855925, 2, 1909, 10.0, 190.1, 24, 2, 47.531835, 4075.0, 358.19, 182, 4075.0, 28.326106, 64.0, 14137.141991, 2.0, 1.0],
    [-82.319553, 2, 2257, 10.0, 70.6, 29, 2, 64.0, 1075.0, 282.26, 800, 950.0, 27.971375, -11.597031, 14137.141991, 2.0, 10.0],
    [-82.178408, 2, 784, 10.0, 501.4, 14, 2, 0.0, 39000.0, 163.19, 2860, 41375.0, 27.655701, -11.597031, 39008.0, 2.0, 20.0],
    [-82.045069, 2, 2555, 10.0, 414.5, 174, 2, 47.531835, 25375.0, 163.31, 1427, 26850.0, 27.249344, -1024.0, 24000.0, 1.0, 0.0],
    [-82.526814, 2, 781, 10.0, 454.0, 51, 3, 47.531835, 37000.0, 180.0, 4219, 39250.0, 28.68457, 0.0, 36992.0, 2.0, 15.0],
    [20000.0, 2, 4106, 0.343, 413.4, 135, 109, 47.531835, 13425.0, 23.53, 5107, 14100.0, 1012.8, -11.9, 0.2, 2.0, 16.0],
    [-82.55412, 2, 2224, 10.0, 93.8, 268, 3, 320.0, 5000.0, 144.11, 729, 5250.0, 27.187546, 320.0, 5504.0, 2.0, 2.0]
]

# Create a DataFrame
columns = [
    "lon", "emergency", "flight", "nac_p", "gs", "t", "alert", "baro_rate",
    "alt_baro", "track", "hex", "alt_geom", "lat", "geom_rate",
    "nav_altitude_mcp", "nac_v", "category"
]
df = pd.DataFrame(data, columns=columns)

# Display the DataFrame in Streamlit
st.write("### ADS-B Category Example Table")
st.dataframe(df)

st.subheader("Enter your specifications below")
LAT = 27.9506
LONG = -82.4572

emergency = st.selectbox("Emergency Status:", ["No Emergency", 
                                               "General Emergency",
                                               "Lifegaurd/Medical",
                                               "Minimum Fuel",
                                               "No Comms",
                                               "Unlawful Interference"])
em_map = {"No Emergency":0, 
        "General Emergency":1,
        "Lifegaurd/Medical": 2,
        "Minimum Fuel": 3,
        "No Comms": 4,
        "Unlawful Interference": 5}

gs = st.slider("Ground Speed (knots):", 0.0, 1000.0, 350.0)

nac_p = st.slider("Navigation Accuracy Category (Position):", 0.0, 10.0, 5.0)

aircraft_type  = st.text_input("Aircraft Type (e.g., A320, B737, etc.):", value=90)

#90% of the dataset has alert == 3, and until I figure out what alerts mean,
#default value is going to be 3
alert = 3

baro_rate = st.slider("Barometric Rate (feet/min):", -6000.0, 6000.0, 0.0)

alt_baro = st.slider("Barometric Altitude (feet):", 0.0, 45000.0, 10000.0)

track = st.slider("Track (degrees):", 0.0, 360.0, 150.0)

alt_geom = st.slider("Geometric Altitude (feet):", 0.0, 45000.0, 10000.0)

geom_rate = st.slider("Geometric Rate (feet/min):", -6000.0, 6000.0, 0.0)

nav_altitude_mcp = st.slider("MCP/FCU Selected Altitude (feet):", 0.0, 45000.0, 10000.0)

nac_v = st.slider("Navigation Accuracy Category (Velocity):", 0.0, 10.0, 5.0)

flight = st.text_input("Flight Number (Optional):", value="1234")
if flight == "":
    flight = 1234
hex_code = st.text_input("Hex Code (Optional):", value="1234")
if hex_code == "":
    hex_code = 1234

user_input_features = {
    "lon": LONG,
    "emergency": em_map[emergency],
    "flight": int(flight),
    "nac_p": nac_p,
    "gs": gs,
    "t": aircraft_type,
    "alert": alert, #defalt value of 3
    "baro_rate": baro_rate,
    "alt_baro": alt_baro,
    "track": track,
    "hex": int(hex_code),
    "alt_geom": alt_geom,
    "lat": LAT,
    "geom_rate": geom_rate,
    "nav_altitude_mcp": nav_altitude_mcp,
    "nac_v": nac_v,
}

if st.button("Predict"):
    st.write("Predicting now!")

    response = requests.post(
        "http://fastapi_route:5001/predict-data",
        json = user_input_features,
        timeout=10
    )
    if response.status_code == 200:

        result = response.json()
        st.write(result)

    else:
        st.error(f"Failed to get prediction: {response.status_code}")
        st.write(f"Error details: {response.text}")       