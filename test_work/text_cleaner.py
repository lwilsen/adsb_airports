"""
Text Cleaning Page
This page is designed to help clean up text using an LLM.
Users can input a string of text, submit it for cleaning, and view the cleaned version.
"""

import uuid
import streamlit as st
import yaml
from modules.functions import send_request_to_llm, check_and_append_llm_connectivity
from modules.constants import BASE_URL, API_KEY, WORKSPACE_ID

# from modules.detailed_prompts import prompt_options


# Load the YAML file
def load_prompts(file_path):
    """Quick Local function to load in a YAML file for easy configuation of prompts"""
    with open(file=file_path, mode="r", encoding="UTF-8") as file:
        data = yaml.safe_load(file)
    return data["prompts"]  # Access the dictionary under "prompts"


prompt_options = load_prompts("./files/prompts.yaml")


def text_cleaning_page():
    """
    Main page logic for text cleaning using AnythingLLM.
    """
    check_and_append_llm_connectivity()

    st.title("Text Cleaning Tool")

    is_connected_to_llm = st.session_state["DATA"].get("LLM_CONNECTED", False)

    # Layout with three columns
    col1, col2, col3 = st.columns([2, 1, 2], gap="medium")

    # Input box in the left column
    with col1:
        st.subheader("Input Text")
        user_input = st.text_area(
            "Paste your text here for cleaning:",
            value=st.session_state.get("text_cleaning_input", ""),
            key="text_cleaning_input",
            height=400,
        )
        if is_connected_to_llm:
            st.success("Connected to LLM")
        else:
            st.error("Not connected to LLM")

    # Middle column for buttons
    with col2:
        st.subheader("Actions")
        st.divider()
        with st.expander("Prompt Actions"):
            # Dropdown for prompt selection
            selected_prompt_key = st.selectbox(
                "Select prompt:",
                options=list(prompt_options.keys()),
                key="prompt_selection",
            )

        # Retrieve the detailed prompt (value) for the selected key
        selected_prompt = prompt_options[selected_prompt_key]

        (
            button1,
            button2,
        ) = st.columns([1, 1], gap="small")

        with button1:
            # Submit button to send prompt
            if st.button("Submit"):
                if not user_input.strip():
                    st.error("Please enter some text before submitting.")
                else:
                    # Combine the selected prompt with the user input
                    # Add in any aditional input here
                    full_prompt = f"KEEP EVERYTHING IN THE SAME PERSPECTIVE - {selected_prompt}: '{user_input}'"
                    response = send_request_to_llm(
                        prompt=full_prompt,
                        base_url=BASE_URL,
                        workspace=WORKSPACE_ID,
                        api_key=API_KEY,
                    )
                    st.session_state["text_cleaning_output"] = response

        with button2:
            # Reset button to clear inputs and outputs
            if st.button("Reset"):
                # Clear all session state variables related to this page
                for key in [
                    "text_cleaning_input",
                    "text_cleaning_output",
                    "text_cleaning_session_id",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]

                # Generate a new session ID for fresh context
                st.session_state["text_cleaning_session_id"] = str(uuid.uuid4())
                st.rerun()
    # Output box in the right column
    with col3:
        st.subheader("Cleaned Text")
        st.text_area(
            "Output:",
            value=st.session_state.get("text_cleaning_output", ""),
            height=400,
        )
        st.caption(
            "Running Mistral 7B, LLM can make mistakes. Double-check important info."
        )
