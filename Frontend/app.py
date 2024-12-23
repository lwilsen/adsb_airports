"""
Streamlit Application for Interactive LLM and Vector Store Queries.

This module implements a Streamlit-based user interface for interacting \
    with a local LLM (Large Language Model) and a vector store. \
        It initializes the required components, processes user input, \
            and provides responses based on data from a specified folder.

Modules:
- document_processor: Handles keyword extraction \
    and context retrieval from the data folder.
- app_utils: Provides utilities for UI initialization, \
    user input handling, and LLM setup.
- vector_store: Manages the loading and querying of a local vector store.

Usage:
Run this script to launch the Streamlit app. The user can input queries to \
    interact with the model and retrieve information.
"""

import streamlit as st
from menu import render_menu


def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Home", layout="wide")
    render_menu()


if __name__ == "__main__":
    main()