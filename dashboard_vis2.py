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
    data = pd.read_csv('protests us final.csv')
    data['event_date'] = pd.to_datetime(data['event_date'], dayfirst=True)
    data['Crowd_size'] = data['Crowd_size'].apply(lambda x: max(x, 0))
    return data


protests_df = load_data()


# Title
st.title("Protests in North America")

# Display a sample of the data
st.subheader("Dataset Preview")
st.dataframe(protests_df.head())

# Add a selectbox to filter by a column (example: 'state' or any column in your dataset)
columns = protests_df.columns
selected_column = st.selectbox("Select a column to filter", columns)

unique_values = protests_df[selected_column].unique()
selected_value = st.selectbox(f"Select a value in '{selected_column}'", unique_values)

# Filter data based on selection
filtered_df = protests_df[protests_df[selected_column] == selected_value]

# Display the filtered data
st.subheader(f"Filtered Data by {selected_column}: {selected_value}")
st.dataframe(filtered_df)


def plot_usa_map(filtered_data):
    # Create a new column for protest type
    filtered_data['Protest_Type'] = filtered_data.apply(
        lambda row: 'Pro Israel' if row['Pro Israel'] == 1 else
        ('Pro Palestine' if row['Pro Palestine'] == 1 else None),
        axis=1
    )

    # Create the scatter_geo plot
    fig = px.scatter_geo(
        filtered_data,
        lat='latitude',
        lon='longitude',
        color='Protest_Type',
        color_discrete_map={"Pro Israel": "blue", "Pro Palestine": "red"},
        scope="usa",
        hover_data=['admin1', 'event_date'],
        title="Protests in the USA",
    )

    # Adjust layout
    fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

def plot_by_who(df):
    # Streamlit app
    st.title("Interactive Group Selection for Graph")

    # Multiselect widget for group selection
    selected_groups = st.multiselect(
        "Select groups to include in the graph:",
        options=df["group"].unique(),
        default=df["group"].unique()  # Preselect all groups
    )


    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(filtered_df["group"], filtered_df["count"], color="skyblue")
    ax.set_xlabel("Group")
    ax.set_ylabel("Count")
    ax.set_title("Counts by Group")
    ax.set_xticklabels(filtered_df["group"], rotation=45, ha="right")

    # Display plot
    st.pyplot(fig)

    # Optional: Display filtered data
    if st.checkbox("Show filtered data"):
        st.write(filtered_df)


df = load_data()


# Filter for rows within the USA
usa_data = df[df["country"] == "United States"]

# Calculate group totals for Pro-Israel and Pro-Palestine protests
group_columns = [
    "palestenian_group",
    "jewish_group",
    "students_group",
    "teachers_group",
    "women_group",
    "political_group",
    "lgbt_group",
    "other_group",
]

# Sum up the Pro-Israel and Pro-Palestine counts by group
group_data = {}
for group in group_columns:
    group_data[group] = {
        "Pro Israel": usa_data.loc[usa_data[group] == 1, "Pro Israel"].sum(),
        "Pro Palestine": usa_data.loc[usa_data[group] == 1, "Pro Palestine"].sum(),
    }

# Create a DataFrame from the grouped data
group_df = pd.DataFrame(group_data).T.reset_index()
group_df.columns = ["group", "Pro Israel", "Pro Palestine"]

# Display options for the user
st.title("Protest Counts by Group Across the USA")
selected_group = st.multiselect(
    "Select groups to display on the map:",
    options=group_columns,
    default=group_columns,
)

# Filter data based on the selected groups
filtered_group_df = group_df[group_df["group"].isin(selected_group)]

# Create a map visualization
if not filtered_group_df.empty:
    # Merge group data back with the main dataset for geographic visualization
    map_data = usa_data[usa_data[selected_group].sum(axis=1) > 0]

    fig = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color="Pro Israel",  # Default color
        size="Crowd_size",  # Bubble size
        hover_data=["notes", "Pro Israel", "Pro Palestine"],
        mapbox_style="carto-positron",
        title="Protest Map (Pro Israel and Pro Palestine)",
        zoom=3,
        center={"lat": 37.0902, "lon": -95.7129},  # Centered on the USA
    )

    st.plotly_chart(fig)

# Show the summary table
st.subheader("Summary Data")
st.write(filtered_group_df)