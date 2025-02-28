import dashboard_vis2
import open_page
import visu_shahaf
import visu_orian
import visu_yarin
import violentNew
import streamlit as st

st.set_page_config(page_title="Data Visualisation", layout="wide")

# Page options
pages = {
    "Home": open_page,
    "Protests Locations": visu_shahaf,
    "Protests Participants": dashboard_vis2,
    "Significant Events": visu_orian,
    "Violent Protests": violentNew
}

# Sidebar menu
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Call the selected page's app function
selected_page = pages[selection]
selected_page.app()