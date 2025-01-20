import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from natsort import index_natsorted
from datetime import timedelta, datetime

# Set page configuration to wide layout
st.set_page_config(page_title="Data Visualisation", layout="wide")

# Load the dataset
@st.cache_data
def load_data():
    # Load the dataset
    data = pd.read_csv('protests us final.csv')

    # Parse dates correctly
    data['event_date'] = pd.to_datetime(data['event_date'], dayfirst=True)

    # Replace -1 in the 'crowd_size' column with a default value (e.g., 0 or 1)
    data['Crowd_size'] = data['Crowd_size'].apply(lambda x: max(x, 0))

    # Assign colors based on protest type
    data['color'] = data.apply(
        lambda row: '#ED665B' if row['Pro Palestine'] == 1 else (
            '#79B8DA' if row['Pro Israel'] == 1 else '#C4C4C4'  # Default color for other cases
        ),
        axis=1
    )
    return data


def visualize_protests(df, selected_date_range, selected_groups):
    # Filter data based on selected date range
    filtered_df = df[
        (df['event_date'] >= pd.to_datetime(selected_date_range[0])) &
        (df['event_date'] <= pd.to_datetime(selected_date_range[1]))
    ]

    # Filter data based on selected groups
    if selected_groups:
        group_filter = filtered_df[selected_groups].sum(axis=1) > 0
        filtered_df = filtered_df[group_filter]

    # USA Map Visualization
    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        size=None,  # Remove size dependency
        color="color",  # Use the custom color column
        hover_name="location",
        hover_data=["admin1", "Crowd_size", "event_date"],  # Only show state name, crowd size, and date
        zoom=3,
        mapbox_style="carto-positron",
        height=800  # Increased map size
    )

    if filtered_df.empty:
        st.write("No data to display for the selected filters. Showing empty map.")
        fig = px.scatter_mapbox(
            pd.DataFrame({"latitude": [], "longitude": []}),  # Empty map
            lat="latitude",
            lon="longitude",
            zoom=3,
            mapbox_style="carto-positron",
            height=800
        )

    # Display the map
    st.plotly_chart(fig, use_container_width=True)

# Load the data
protests_df = load_data()

# Streamlit App
st.title("Protest Visualization in the USA")

# Date Range Selection
min_date = protests_df['event_date'].min().date()  # Convert to datetime.date
max_date = protests_df['event_date'].max().date()  # Convert to datetime.date

st.sidebar.header("Filter Options")
selected_date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Group Selection
groups = [
    "palestenian_group", "jewish_group", "students_group", "teachers_group",
    "women_group", "political_group", "lgbt_group", "other_group"
]
selected_groups = st.sidebar.multiselect("Select Groups to Display", groups, default=groups)

# Call the function to visualize the protests
visualize_protests(protests_df, selected_date_range, selected_groups)
