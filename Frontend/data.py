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
import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
import json


def data():

    st.title("About the Data")
    st.write(
        """
    ##### What is ADS-B Data?

    ADS-B (Automatic Dependent Surveillance–Broadcast) is a surveillance technology used in aviation for tracking aircraft. It provides precise location and status information through messages transmitted by aircraft and picked up by ground stations or satellites.

    ---

    ### Basic Aircraft Information
    
    - **`alt_baro`**: Barometric altitude in feet.  
    - **`gs`**: Ground speed of the aircraft in knots.  
    - **`track`**: Heading of the aircraft in degrees, measured clockwise from north.  
    - **`category`**: Classification of the aircraft based on size and type.  

    ---

    ### Position and Navigation Data

    - **`lat`**: Latitude in degrees.  
    - **`lon`**: Longitude in degrees.  
    - **`timestamp`**: Timestamp of when the data was collected (Coordinated Universal Time/UTC).

    ---"""
    )

    data = {
        "alt_baro": [
            34000,
            36000,
            32000,
            1800,
            28000,
            38000,
            37925,
            11400,
            3450,
            45000,
        ],
        "gs": [445.2, 443.5, 426.7, 90.2, 461.2, 416.9, 433.2, 187.4, 75.9, 473.1],
        "track": [
            268.46,
            272.84,
            237.54,
            54.02,
            247.16,
            250.09,
            278.90,
            45.65,
            108.43,
            102.45,
        ],
        "baro_rate": [0.0, 0.0, 0.0, None, 64.0, 0.0, 0.0, 1408.0, None, 0.0],
        "lat": [
            28.821808,
            28.638890,
            29.966354,
            30.427551,
            29.769928,
            29.946496,
            28.797958,
            30.687747,
            30.158752,
            29.076920,
        ],
        "lon": [
            -91.527152,
            -91.345933,
            -91.177153,
            -91.151733,
            -91.056906,
            -90.934497,
            -90.922218,
            -90.903680,
            -90.790369,
            -90.753250,
        ],
        "category": ["A3", "A3", "A3", "A1", "A3", "A3", "A3", "A1", "A1", "A2"],
        "t": [
            "B38M",
            "B38M",
            "A321",
            "P28A",
            "A321",
            "B38M",
            "A20N",
            "PC12",
            "C172",
            "GLF4",
        ],
        "flight": [
            "UAL1929",
            "AAL1637",
            "DAL919",
            "N81149",
            "AAL2927",
            "SWA2992",
            "NKS3168",
            "SKQ37",
            "N346SP",
            "N43XT",
        ],
        "timestamp": [
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
            "2024-11-05 02:11:45.640097+00:00",
        ],
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Display the table in the Streamlit app
    st.subheader("Flight Data Table")
    st.dataframe(df)

    st.write("""### ADS-B Category Info""")

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
