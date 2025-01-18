import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from natsort import index_natsorted

# Set page configuration to wide layout
st.set_page_config(layout="wide")


# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv('NA_protests_filtered.csv')


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

# Create a simple Plotly visualization (example: count by state or other column)
if "state" in columns:
    state_count = protests_df['state'].value_counts().reset_index()
    state_count.columns = ['state', 'count']

    fig = px.bar(
        state_count,
        x='state',
        y='count',
        title="Number of Protests by State",
        labels={'count': 'Number of Protests', 'state': 'State'},
        color='state'
    )

    st.plotly_chart(fig)
else:
    st.write("No 'state' column found in the dataset for this example.")
