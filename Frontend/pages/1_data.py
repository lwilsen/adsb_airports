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

st.title("Data Information")

st.write('''### ADS-B Category Info''')

with st.expander("ADS-B aircraft category **A** information"):
    st.subheader("A Category")
    st.markdown(
        """
    * **A0:** No ADS-B emitter category information.
    * **A1:** Light (< 15500 lbs) - Any airplane with a maximum takeoff weight less than 15,500 pounds.
    * **A2:** Small (15500 to 75000 lbs) - Any airplane with a maximum takeoff weight greater than or equal to 15,500 pounds but less than 75,000 pounds.
    * **A3:** Large (75000 to 300000 lbs) - Any airplane with a maximum takeoff weight greater than or equal to 75,000 pounds but less than 300,000 pounds that does not qualify for the high vortex category.
    * **A4:** High vortex large (aircraft such as B-757) - Any airplane with a maximum takeoff weight greater than or equal to 75,000 pounds but less than 300,000 pounds that has been determined to generate a high wake vortex.
    * **A5:** Heavy (> 300000 lbs) - Any airplane with a maximum takeoff weight equal to or above 300,000 pounds.
    * **A6:** High performance (> 5g acceleration and 400 kts) - Any airplane, regardless of weight, which can maneuver in excess of 5 G's and maintain true airspeed above 400 knots.
    * **A7:** Rotorcraft - Any rotorcraft regardless of weight.
    """
    )
with st.expander("ADS-B aircraft category **B** information"):
    st.subheader("B Category")
    st.markdown(
        """
    * **B0:** No ADS-B emitter category information.
    * **B1:** Glider / sailplane - Any glider or sailplane regardless of weight.
    * **B2:** Lighter-than-air - Any lighter than air (airship or balloon) regardless of weight.
    * **B3:** Parachutist / skydiver
    * **B4:** Ultralight / hang-glider / paraglider - A vehicle that meets the requirements of 14 CFR § 103.1.
    * **B5:** Reserved
    * **B6:** Unmanned aerial vehicle - Any unmanned aerial vehicle or unmanned aircraft system regardless of weight.
    * **B7:** Space / trans-atmospheric vehicle
    """
    )

with st.expander("ADS-B aircraft category **C** information"):
    st.subheader("C Category")
    st.markdown(
        """
    * **C0:** No ADS-B emitter category information.
    * **C1:** Surface vehicle - emergency vehicle
    * **C2:** Surface vehicle - service vehicle
    * **C3:** Point obstacle (includes tethered balloons)
    * **C4:** Cluster obstacle
    * **C5:** Line obstacle
    * **C6:** Reserved
    * **C7:** Reserved
    """
    )

