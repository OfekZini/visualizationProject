import dashboard_vis2
import open_page
import visu_shahaf
import visu_orian
import violentNew
import streamlit as st

st.set_page_config(page_title="Data Visualisation", layout="wide")

# Add global CSS for visualization sizing
# st.markdown("""
# <style>
#     /* Set minimum height for all Plotly charts without overflow */
#     .stPlotlyChart {
#         min-height: 500px !important;
#     }
#
#     /* Set specific heights for different screen sizes */
#     @media screen and (max-height: 600px) {
#         .stPlotlyChart {
#             min-height: 300px !important;
#         }
#     }
#
#     /* Remove unwanted scrollbars */
#     .element-container {
#         overflow-y: visible !important;
#     }
#
#     /* Ensure proper spacing between charts */
#     .stPlotlyChart + .stPlotlyChart {
#         margin-top: 2px;
#     }
#
#     /* Remove any other scrollbars */
#     ::-webkit-scrollbar {
#         display: none;
#     }
#
#     /* Make sure containers don't create scrollbars */
#     div.block-container {
#         overflow-y: visible !important;
#         max-height: none !important;
#     }
# </style>
# """, unsafe_allow_html=True)

st.markdown(
    """
    <style>
        body {
            zoom: 0.85; /* Adjust the zoom level (1 = 100%, 1.25 = 125%, etc.) */
        }
    </style>
    """,
    unsafe_allow_html=True
)

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