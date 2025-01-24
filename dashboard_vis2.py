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


def format_group_name(group_name):
    """Format group names to start with a capital letter and remove '_group'."""
    return group_name.replace("_group", "").capitalize()


def inverse_format_group_name(display_name):
    """Revert formatted group names back to the original column names."""
    return display_name.lower().replace(" ", "_") + "_group"


def visualize_line_plot(df, start_date, end_date, selected_groups, metric, aggregation, pro_palestine=True):
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

    # Add a column for aggregation period (week or month)
    if aggregation == 'Week':
        melted_df['period'] = melted_df['event_date'].dt.to_period('W')
    else:
        melted_df['period'] = melted_df['event_date'].dt.to_period('M')

    # Group by the selected period and group type, summing the number of protests and the crowd size
    grouped_data = melted_df.groupby(['period', 'group']).agg(
        num_protests=('count', 'size'),
        total_crowd=('Crowd_size', 'sum')
    ).reset_index()

    # Convert 'period' back to datetime for plotting
    grouped_data['period'] = grouped_data['period'].dt.to_timestamp()

    # Choose metric for y-axis
    y_axis = 'num_protests' if metric == 'Number of Protests' else 'total_crowd'
    y_label = 'Number of Protests' if metric == 'Number of Protests' else 'Number of Protesters'

    # Create the line plot
    fig = px.line(
        grouped_data,
        x='period',
        y=y_axis,
        color='group',
        line_group='group',
        line_shape='linear',
        title=f'{y_label} by Group Over Time',
        labels={
            'period': 'Period',
            y_axis: y_label,
            'group': 'Group'
        },
        width=900,
        height=500
    )

    # Adjust line width and opacity for all traces
    for trace in fig.data:
        trace['line']['width'] = 5  # Slightly thicker lines
        trace['opacity'] = 0.65
        trace['name'] = format_group_name(trace['name'])  # Format group names

    return fig, grouped_data


# Load the data
protests_df = load_data()

# Streamlit App
st.title("Protest Visualization in the USA")

# Selection Options: Displayed above the plots
st.subheader("Filter Options")

# Date Range Selection
min_date = protests_df['event_date'].min().date()
max_date = protests_df['event_date'].max().date()

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date (First day of month)",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

with col2:
    end_date = st.date_input(
        "End Date (Last day of month)",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

# Ensure start_date is before end_date
if start_date > end_date:
    st.error("Start date must be before or equal to the end date.")

# Group Selection, Metric Toggle, and Aggregation in the same row
col1, col2, col3 = st.columns(3)

with col1:
    original_groups = [
        "palestenian_group", "jewish_group", "students_group", "teachers_group",
        "women_group", "political_group", "lgbt_group", "other_group"
    ]
    display_groups = [format_group_name(group) for group in original_groups]
    selected_display_groups = st.multiselect("Select Groups to Display", display_groups, default=display_groups)

    # Map back to original group names for processing
    selected_groups = [inverse_format_group_name(group) for group in selected_display_groups]

with col2:
    metric = st.radio(
        "Select Metric to Display",
        ['Number of Protests', 'Number of Protesters'],
        horizontal=True
    )

with col3:
    aggregation = st.radio(
        "Select Aggregation",
        ['Week', 'Month'],
        horizontal=True
    )

col1, col2 = st.columns(2)

# Plot for Pro Palestine
palestine_plot, grouped_data_p = visualize_line_plot(protests_df, start_date, end_date, selected_groups, metric, aggregation, pro_palestine=True)

# Plot for Pro Israel
israel_plot, grouped_data_i = visualize_line_plot(protests_df, start_date, end_date, selected_groups, metric, aggregation, pro_palestine=False)

# Corrected code to get the maximum y-value for the selected metric
y_column = 'num_protests' if metric == 'Number of Protests' else 'total_crowd'

# Get the maximum y-value between the two plots (based on the metric)
y_max = max(grouped_data_p[y_column].max(), grouped_data_i[y_column].max())

# Set the same y-axis limit for both plots
palestine_plot.update_layout(yaxis=dict(range=[0, y_max]))
israel_plot.update_layout(yaxis=dict(range=[0, y_max]))

palestine_plot.update_layout(
    yaxis=dict(
        range=[0, y_max],
        showgrid=True,  # Enable grid lines
        gridcolor='lightgray',  # Set the color of the grid lines
        gridwidth=0.5  # Set the width of the grid lines
    ),
    xaxis=dict(
        showgrid=True,  # Enable grid lines
        gridcolor='lightgray',  # Set the color of the grid lines
        gridwidth=0.5  # Set the width of the grid lines
    )
)

israel_plot.update_layout(
    yaxis=dict(
        range=[0, y_max],
        showgrid=True,  # Enable grid lines
        gridcolor='lightgray',  # Set the color of the grid lines
        gridwidth=0.5  # Set the width of the grid lines
    ),
    xaxis=dict(
        showgrid=True,  # Enable grid lines
        gridcolor='lightgray',  # Set the color of the grid lines
        gridwidth=0.5  # Set the width of the grid lines
    )
)


# Display both plots side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pro Palestine Protests")
    st.plotly_chart(palestine_plot, use_container_width=True)

with col2:
    st.subheader("Pro Israel Protests")
    st.plotly_chart(israel_plot, use_container_width=True)