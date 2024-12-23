"""This will render the menu and handle menu related designs."""

import streamlit as st
from home_page import home_page
from add_data_page import data_page
from presentation import about_page
from course_conclusion import course_conclusion


def render_menu():
    """Render the sidebar menu with button-based navigation (no radio buttons)."""

    st.sidebar.title("Navigation:")

    # Define your menu items
    menu_items = [
        {
            "label": "Home",
            "icon": ":material/home:",
            "help": "Introduction to the app.",
            "func": home_page,
        },
        {
            "label": "Add New Data",
            "icon": ":material/analytics:",
            "help": "Upload new data to the app.",
            "func": data_page,
        },
        {
            "label": "About the app",
            "icon": ":material/business_center:",
            "help": "What is happening behind the scenes of the app.",
            "func": about_page,
        },
        {
            "label": "The RA Program",
            "icon": ":material/celebration:",
            "help": "Course conclusion.",
            "func": course_conclusion,
        },
    ]

    # Initialize the selected page in session state if it's not set
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"

    # Create a button for each menu item
    # When clicked, it updates the "selected_page" in session state
    for item in menu_items:
        # We combine icon + label in one string
        if st.sidebar.button(
            label=f"{item['icon']} {item['label']}",
            help=item["help"],  # Shows a small tooltip on hover
            use_container_width=True,
        ):
            st.session_state.selected_page = item["label"]

    # After the user clicks a button, this loop finds the chosen page’s function and calls it
    for item in menu_items:
        if item["label"] == st.session_state.selected_page:
            # Execute that page’s function
            item["func"]()
            break