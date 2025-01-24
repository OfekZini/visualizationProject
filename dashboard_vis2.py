import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta, datetime

# Set page configuration to wide layout
st.set_page_config(page_title="Data Visualisation", layout="wide")

# Load the dataset
@st.cache_data
def load_data():
    # Load the dataset
    data = pd.read_csv('/Users/ofekzini/Documents/Data Engineering/Fall 2024/ויזואליזציה/Project/protests us final.csv')

    # Parse dates correctly
    data['event_date'] = pd.to_datetime(data['event_date'], dayfirst=True)

    # Replace -1 in the 'Crowd_size' column with a default value (e.g., 0 or 1)
    data['Crowd_size'] = data['Crowd_size'].apply(lambda x: max(x, 0))

    # Assign colors based on protest type
    data['color'] = data.apply(
        lambda row: '#ED665B' if row['Pro Palestine'] == 1 else (
            '#79B8DA' if row['Pro Israel'] == 1 else '#C4C4C4'  # Default color for other cases
        ),
        axis=1
    )

    # Filter for data in the United States
    data = data[data['country'] == 'United States']

    return data

def visualize_line_plot(df, start_date, end_date, selected_groups, pro_palestine=True):
    # Filter based on Pro Palestine or Pro Israel
    if pro_palestine:
        filtered_df = df[df['Pro Palestine'] == 1]
    else:
        filtered_df = df[df['Pro Israel'] == 1]

    # Convert start_date and end_date to datetime, and normalize to ensure both are at the start of the day
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()

    # Filter data by the selected date range
    filtered_df = filtered_df[
        (filtered_df['event_date'] >= start_date) &
        (filtered_df['event_date'] <= end_date)
    ]

    # Melt the data for easier grouping and visualization
    melted_df = filtered_df.melt(
        id_vars=['event_date', 'Crowd_size'],
        value_vars=selected_groups,
        var_name='group',
        value_name='count'
    )

    # Keep only rows where 'count' is 1 (indicating a protest for the group)
    melted_df = melted_df[melted_df['count'] == 1]

    # Group by month and group type, summing the number of protests and the crowd size
    melted_df['month'] = melted_df['event_date'].dt.to_period('M')
    grouped_data = melted_df.groupby(['month', 'group']).agg(
        num_protests=('count', 'size'),
        total_crowd=('Crowd_size', 'sum')
    ).reset_index()

    # Convert 'month' back to datetime for plotting
    grouped_data['month'] = grouped_data['month'].dt.to_timestamp()

    # Create the line plot
    fig = px.line(
        grouped_data,
        x='month',
        y='total_crowd',  # Y-axis as total protestors
        color='group',
        line_group='group',
        line_shape='linear',
        title='Protestors by Group Over Time',
        labels={'month': 'Month', 'total_crowd': 'Total Protestors', 'group': 'Group'},
        width=900,
        height=500
    )

    # Adjust line width based on the number of protests in that month
    for trace in fig.data:
        group = trace.name
        trace_data = grouped_data[grouped_data['group'] == group]
        trace['line']['width'] = trace_data['num_protests'].max() / 10  # Scale for better visibility

    return fig


# Load the data
protests_df = load_data()

# Streamlit App
st.title("Protest Visualization in the USA")

# Sidebar: Date Range Selection using two date inputs
st.sidebar.header("Filter Options")

min_date = protests_df['event_date'].min().date()
max_date = protests_df['event_date'].max().date()

start_date = st.sidebar.date_input(
    "Start Date (First day of month)",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date (Last day of month)",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Ensure start_date is before end_date
if start_date > end_date:
    st.sidebar.error("Start date must be before or equal to the end date.")

# Group Selection
groups = [
    "palestenian_group", "jewish_group", "students_group", "teachers_group",
    "women_group", "political_group", "lgbt_group", "other_group"
]
selected_groups = st.sidebar.multiselect("Select Groups to Display", groups, default=groups)

# Create two plots: one for Pro Palestine and one for Pro Israel
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pro Palestine Protests")
    # Plot for Pro Palestine
    palestine_plot = visualize_line_plot(protests_df, start_date, end_date, selected_groups, pro_palestine=True)
    st.plotly_chart(palestine_plot, use_container_width=True)

with col2:
    st.subheader("Pro Israel Protests")
    # Plot for Pro Israel
    israel_plot = visualize_line_plot(protests_df, start_date, end_date, selected_groups, pro_palestine=False)
    st.plotly_chart(israel_plot, use_container_width=True)