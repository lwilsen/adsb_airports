"""
Utility Script for File Display and Interaction in Streamlit

This script provides utility functions to display and interact with various file types 
such as Markdown files, PDF documents, DOCX files, and others. Additionally, it includes
parsing capabilities for common file formats like CSV, Excel, JSON, and XML.

Functions:
----------

1. **display_readme(readme_path, img_folder_path)**:
    - Displays a README file with embedded images from a specified folder.
    - Use Case: Dynamically present project README files alongside visual aids.

2. **display_pdf(file_path)**:
    - Displays a PDF file within an iframe in a Streamlit app.
    - Use Case: Present reports, manuals, or any static PDF content in the application.

3. **doc_to_pdf_and_display(filepath)**:
    - Displays the content of a DOCX file in a Streamlit app.
    - Includes error handling for unsupported files or missing files.
    - Use Case: View DOCX documents directly within a web interface.
    - DISPLAYS IN PDF FORMAT

4. **parse_file(file)**:
    - Parses uploaded files based on their type and returns the content as a string.
    - Supported Types:
        - **CSV/Excel**: Converts to a CSV string.
        - **DOCX**: Extracts text from paragraphs.
        - **PDF**: Extracts text from pages.
        - **JSON**: Converts to a formatted JSON string.
        - **XML**: Converts XML to a string representation.
    - Use Case: Upload and process various file types for further analysis or display.

5. **extract_text_from_pdf(file_path)**:
    - Extracts and returns text content from a PDF file.
    - Use Case: Analyze or process textual data from PDF documents programmatically.

6. **send_request_to_llm(prompt, base_url, workspace, api_key, file_content=None)**:
    - Sends a request to an LLM host with optional file content for processing.
    - Use Case: Analyze uploaded files or generate responses based on file content.

7. **check_llm_connectivity(base_url, workspace, api_key)**:
    - Checks the connectivity to the LLM host by sending a test prompt.
    - Use Case: Ensure the LLM host is reachable and functioning as expected.

8. **check_and_append_llm_connectivity()**:
    - Checks LLM connectivity and appends the result to the Streamlit session state.
    - Use Case: Integrate LLM connection status into the application's session state.

9. **download_file(file_path, button_label)**:
    - Adds a button to download a specified file.
    - Use Case: Allow users to download generated or uploaded files in the app.

Requirements:
-------------
- **Libraries**:
    - `Streamlit`: Core framework for building the interactive UI.
    - `PyPDF2`: For handling PDF parsing and text extraction.
    - `python-docx`: For working with DOCX files.
    - `pandas`: For handling CSV and Excel files.
    - `xml.etree.ElementTree`: For processing XML files.
    - `base64`: For encoding files like PDFs to embed in HTML.
    - `requests`: For interacting with the LLM API.
    - `dotenv`: For loading environment variables.
    - `os` and `glob`: For file system operations.

- **File Handling**:
    - The script assumes a structured environment where files (e.g., README, PDFs, or datasets) 
      are accessible via paths or uploaded dynamically through Streamlit.

Potential Usage:
---------------
This script serves as a backend for a Streamlit application where:
- Markdown files are rendered for user guidance or documentation.
- PDFs are displayed, searchable, and extractable for enhanced user experience.
- DOCX files are displayed interactively for quick access to text content.
- Uploaded files (CSV, JSON, XML, etc.) are parsed and processed for further interaction.
- LLM connectivity enables analysis and interaction with file content using AI - with Mistral.

"""

import os
import base64
import glob
import xml.etree.ElementTree as ET
import requests
import streamlit as st
import pandas as pd

# Load environment variables

# Constants
BASE_URL = os.getenv("BASE_URL")  # Base URL for the API
API_KEY = os.getenv("API_KEY")  # API key for authentication
WORKSPACE = os.getenv("WORKSPACE")  # Workspace slug


def display_readme(readme_path: str, img_folder_path: str):
    """
    Displays a README file with embedded images.

    Args:
        readme_path (str): Path to the README file.
        img_folder_path (str): Path to the folder containing images.
    """
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_line = f.readlines()

        readme_buffer = []
        img_files = [os.path.basename(x) for x in glob.glob(f"{img_folder_path}/*")]

        for line in readme_line:
            readme_buffer.append(line)
            for image in img_files:
                if image in line:
                    st.markdown("".join(readme_buffer[:-1]))
                    st.image(f"{img_folder_path}/{image}", use_container_width=True)
                    readme_buffer.clear()

        if readme_buffer:
            st.markdown("".join(readme_buffer))

    except FileNotFoundError:
        st.error(f"README file not found at: {readme_path}")

        

def send_request_to_llm(prompt, base_url, workspace, api_key, file_content=None):
    """
    Sends a request to the LLM with an optional file content.

    Args:
        prompt (str): The user prompt.
        base_url (str): The base URL of the LLM host.
        workspace (str): The workspace ID.
        api_key (str): The API key.
        file_content (str, optional): Content of the uploaded file.

    Returns:
        str: Response from the LLM.
    """
    llm_prompt = prompt
    if file_content:
        llm_prompt = f"The following document content \
            was uploaded:\n\n{file_content}\n\nPrompt: {prompt}"

    # API request setup
    endpoint = f"{base_url}/v1/workspace/{workspace}/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "message": llm_prompt,
        "mode": "chat",
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result.get("textResponse", "No response received.")
        return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"


def check_llm_connectivity(base_url: str, workspace: str, api_key: str) -> bool:
    """
    Checks the connectivity to the LLM host by sending a test prompt.

    Args:
        base_url (str): The base URL of the LLM host.
        workspace (str): The workspace ID.
        api_key (str): The API key for authentication.
    Returns:
        bool: True if the host is reachable and responds correctly, False otherwise.
    """
    test_prompt = "This is a connectivity test. \
        Respond with just the word 'yes' if you are getting this."
    try:
        # Send a test request
        response = send_request_to_llm(
            prompt=test_prompt, base_url=base_url, workspace=workspace, api_key=api_key
        )
        # Check if the response is valid
        if "yes" in response.lower():
            return True
    except ConnectionError as e:
        # Log the error or provide feedback
        st.warning(f"LLM connectivity check failed: {e}")
        return False

    return False


def check_and_append_llm_connectivity():
    """
    Checks LLM connectivity and appends the result to the session state.
    """
    if "DATA" not in st.session_state:
        st.session_state["DATA"] = {}
    # Check connectivity only if not already connected
    if not st.session_state["DATA"].get("LLM_CONNECTED", False):
        is_llm_connected = check_llm_connectivity(BASE_URL, WORKSPACE, API_KEY)

        # Append LLM connection status to session state
        st.session_state["DATA"]["LLM_CONNECTED"] = is_llm_connected


def download_file(file_path: str, button_label: str):
    """Add a Download PDF button"""
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            download_link = f'<a href="data:application/pdf;base64,{base64_pdf}" \
                download="{os.path.basename(file_path)}">{button_label}</a>'
            st.markdown(download_link, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("File not found for download.")
