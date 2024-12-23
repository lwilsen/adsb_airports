"""
This Streamlit app outlines the future plans for the project, focusing on 
improving satellite imagery and ADS-B data collection.
"""

import streamlit as st


def future():

    st.title("Conclusions and Acknowledgements")

    st.header("Airport identification")
    st.write(
        """
    ### Successes:\n
             - I was able to generally identify major airports, and 
             identify evidence of aircraft activity
             in other areas that indicated smaller airports. \n
        - This project is easily scalable to other similar datasets 
        or an increased amount of data.\n

    ### Limitations:
             - An increased amount of data would more provide more 
             definitive evidence of airports, 
             and more information about smaller airports/helipads.\n
        - The image recognition model did not perform well, and a more 
        powerful/advanced model should
             be used to help analyze satellite images.\n
    """
    )

    st.header("Flight Tracker")
    st.write(
        """
    ### Successes: \n
             - Most flights had enough observations to roughly track 
             their flights during the timeframes
             for which data is available. \n
        - This project is easily scalable to other similar datasets 
        or an increased amount of data.\n
        - Easy access to plane type lookup database. \n

    ### Limitations:
             - An increased frequency of data collection would allow 
             for more precise tracking of 
             flight paths.
        - No real time tracking.
    """
    )

    st.header("Data statement")
    st.write(
        """
    The ADS-B data came from their online api, to which we were generously 
    given access to by Brett Waugh. 
    The Plane type lookup data came from Skylibary (https://skybrary.aero/), 
    and was available for free.
    """
    )
