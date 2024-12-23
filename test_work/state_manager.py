"""
Initialize and manage Streamlit session state variables across multiple pages.

This is ran when the app boots up.

After setting up config.py, come here to load your data.

INSTRUCTIONS FOR USE:

Using the Key (name of the data you loaded and place in config.py data dictionary),
Instantiate your new dataset(s) into the session_state with the data.get notation.
"""

import uuid
import streamlit as st


def create_app_state(data: dict) -> dict:
    """
    Initialize or update Streamlit session state variables.

    Args:
        data (dict): Dictionary containing initial data to populate session state.

    Returns:
        dict: Updated session state.
    """

    # Define default values for session state variables
    default_values = {
        "VAN_DATA_DICTIONARY": data.get("VAN_DATA_DICTIONARY"),
        "TICKET_DATA_DICTIONARY": data.get("TICKET_DATA_DICTIONARY"),
        "SAMPLE_DATA": data.get("SAMPLE_DATA"),
        "TICKET_DATA": data.get("TICKET_DATA"),
        "SAMPLE_TRANSFORM_DATA": data.get("SAMPLE_TRANSFORM_DATA"),
        "DATAMINR1": data.get("DATAMINR1"),
        "GDF_COUNTRIES": data.get("GDF_COUNTRIES"),
        "Book2": data.get("Book2"),
        "Book3": data.get("Book3"),
        "POP_2023": data.get("POP_2023"),
        "login": "LoggedIn",  # LoggedOut
        # Chat and file upload session variables below
        "last_input": "",
        "last_response": "",
        "session_id": str(uuid.uuid4()),
        "uploaded_file": None,  # Placeholder for uploaded file content
        "text_cleaning_input": "",
        "text_cleaning_output": "",
        "text_cleaning_session_id": str(uuid.uuid4()),
    }

    # Update session state
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

    return st.session_state
