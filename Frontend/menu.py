import streamlit as st
from home import home_page
from data import data
from airports import airports
from tracker import tracker
from future import future


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
            "label": "Data Description",
            "icon": ":material/analytics:",
            "help": "Brief explanation of the data.",
            "func": data,
        },
        {
            "label": "Airport Detection",
            "icon": ":material/multiple_airports:",
            "help": "Airport detection functionality.",
            "func": airports,
        },
        {
            "label": "Flight Tracking",
            "icon": ":material/location_searching:",
            "help": "Individual flight histories.",
            "func": tracker,
        },
        {
            "label": "Conclusions + Acknowledgements",
            "icon": ":material/check_circle:",
            "help": "Conclusions and limitations.",
            "func": future,
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
