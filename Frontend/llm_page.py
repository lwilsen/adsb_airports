"""
AnythingLLM Interaction Page

This page allows users to interact with an AnythingLLM instance by querying it using text prompts 
or uploading documents. Supported file formats include CSV, DOCX, PDF, JSON, XML, and Excel.

The LLM processes the content of uploaded files alongside the user-provided prompt to generate 
context-aware responses. This is ideal for tasks such as summarization, analysis, and Q&A based 
on structured or unstructured data.

### Constants:
- `BASE_URL`: The URL where your AnythingLLM instance is hosted. \
    Replace the default value with the actual URL if hosted remotely.
- `API_KEY`: The API key for authenticating requests to the AnythingLLM \
    instance. Ensure this is replaced with a valid key.
- `WORKSPACE`: The workspace slug in AnythingLLM to which queries are sent. \
    Update this value as needed.

### Features:
1. **Text-Based Queries**:
   - Enter a text prompt in the "Input" section on the left-hand side and \
    click "Submit" to send your query to the LLM.
   - Example Prompt: 
     - "Explain the concept of reinforcement learning."
     - "Summarize this document for me."

2. **Document Uploads**:
   - Upload a document in the supported formats (CSV, DOCX, PDF, JSON, \
    XML, Excel) using the "Upload File" expander.
   - The document content is sent along with the user-provided prompt \
    for contextual processing by the LLM.
   - Example:
     - File: A CSV containing sales data.
     - Prompt: "What are the top 3 products with the highest sales?"

3. **Reset Functionality**:
   - Click the "Reset" button to clear the input prompt, response, \
    and uploaded file. This ensures a fresh start for new interactions.
   (Disclaimer - Sometimes needs to be clicked more than once!!)

### Instructions to Use:
1. **Enter a Prompt**:
   - Type a query or command into the input box labeled "Enter your message."

2. **Upload a File (Optional)**:
   - Expand the "Upload and Query a File" section in the middle column.
   - Upload a supported file type. The file content will be processed \
    and combined with your prompt.

3. **Submit the Query**:
   - Click the "Submit" button to send the query and file content to the LLM.
   - Wait for the response, which will appear in the right-hand column.

4. **Reset the Page**:
   - Use the "Reset" button to clear all inputs, outputs, and uploaded files.

### Example Use Cases:
1. **Document Summarization**:
   - Upload a PDF document or DOCX file and ask the LLM to summarize it.
   - Example:
     - File: A PDF research paper.
     - Prompt: "Summarize the main findings of this paper."

2. **Data Analysis**:
   - Upload a CSV or Excel file and query the LLM for insights or \
    specific details.
   - Example:
     - File: A CSV containing sales data.
     - Prompt: "Which product category has the highest revenue?"

3. **General Knowledge Queries**:
   - Use the LLM for standalone Q&A without uploading any files.
   - Example Prompt: "Explain the difference between supervised and \
    unsupervised learning."

This page is designed to simplify interactions with AnythingLLM (MISTRAL AI) 
by integrating text and document-based queries seamlessly.
"""

import uuid
import streamlit as st
import os
from functions import (
    check_and_append_llm_connectivity,
    send_request_to_llm,
)

API_KEY = os.environ.get("ANYTHINGLLM_API_KEY")
BASE_URL = "http://localhost:3001/api/v1/workspace/Airports/"
WORKSPACE_ID = 1

def llm_page():
    """
    Displays the page with the MISTRAL AI interface hosted by Anything LLM.
    """
    st.subheader("AnythingLLM Tool")

    check_and_append_llm_connectivity()

    is_connected = st.session_state["DATA"].get("LLM_CONNECTED", False)

    # Layout with three columns
    col1, col2, col3 = st.columns([2, 1.5, 2], gap="large")

    # Input box in the left column
    with col1:
        st.subheader("Input")
        user_input = st.text_area(
            "Enter your message:",
            value=st.session_state["last_input"],
            key="user_input",
            height=400,
        )
        if is_connected:
            st.success("Connected to LLM")
        else:
            st.error("Not connected to LLM")

    # Middle column for additional features
    with col2:
        st.subheader("Sumbit Query")
        st.divider()

        (
            button1,
            button2,
        ) = st.columns([1, 1], gap="small")

        # Expander for file upload
        with st.expander("Upload and Query a File"):
            file_uploader_key = "file_uploader_key_" + st.session_state["session_id"]
            uploaded_file = st.file_uploader(
                "Upload your file (CSV, DOCX, PDF, JSON, XML, Excel)",
                type=["csv", "docx", "pdf", "json", "xml", "xls", "xlsx"],
                key=file_uploader_key,
            )

        with button1:
            # Submit button to send prompt
            if st.button("Submit"):
                if not user_input.strip():
                    st.error("Please enter a prompt before submitting.")
                else:
                    response = send_request_to_llm(
                        prompt=user_input,
                        base_url=BASE_URL,
                        workspace=WORKSPACE_ID,
                        api_key=API_KEY,
                        file_content=st.session_state.get("uploaded_file"),
                    )

                    st.session_state["last_input"] = user_input
                    st.session_state["last_response"] = response
        with button2:
            # Reset button to clear inputs and outputs
            if st.button("Reset"):
                for key in ["last_input", "last_response", "uploaded_file"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state["session_id"] = str(uuid.uuid4())  # Resets session ID
                st.rerun()

    # Output box in the right column
    with col3:
        st.subheader("Response")
        st.text_area(
            "LLM Response:",
            value=st.session_state.get("last_response", ""),
            height=400,
        )
        st.caption(
            "Running Mistral 7B, LLM can make mistakes. Double-check important info."
        )
