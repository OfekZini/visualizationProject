import streamlit as st
import pandas as pd
import plotly.express as px


def app():
    # Load the dataset
    @st.cache_data
    def load_data():
        # Load the dataset
        data = pd.read_csv('protests us final.csv')

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
        group_name = group_name.replace("_group", "")
        # Adjust specific formatting for LGBT
        if group_name.lower() == 'lgbt':
            return 'LGBT'  # Always display as LGBT
        return group_name.capitalize()

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
        y_label = 'Number of Protests' if metric == 'Number of Protests' else 'Number of Protestors'

        # Define color mapping for the selected groups
        selected_colors = {
            group: original_groups_with_colors[group]
            for group in selected_groups
        }

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
                'period': 'Date',
                y_axis: y_label,
                'group': 'Group'
            },
            color_discrete_map=selected_colors,  # Use the fixed color mapping
            width=900,
            height=500
        )

        # Customize hover data
        fig.update_traces(
            hovertemplate=(
                "Group: %{customdata[0]}<br>"
                "Date: %{x|%Y-%m-%d}<br>"
                "Number of Protests: %{y}<br>"
                "<extra></extra>"
            ),
            customdata=[[format_group_name(group)] for group in grouped_data['group']]  # Add the group info as customdata
        )

        # Adjust line width and opacity for all traces
        for trace in fig.data:
            trace['line']['width'] = 3  # Slightly thicker lines
            trace['opacity'] = 0.7
            trace['name'] = format_group_name(trace['name'])  # Format group names

        return fig, grouped_data


    # Define the original groups and their associated colors
    original_groups_with_colors = {
        "palestenian_group": "#FF0000",
        "jewish_group": "#0000FF",
        "students_group": "#D34611",
        "teachers_group": "#F1CD00",
        "women_group": "#3B2C6A",
        "lgbt_group": "#F6478A",
        "other_group": "#00BABA"
    }

    # Load the data
    protests_df = load_data()

    # Streamlit App
    st.title("Who Are The Protestors?")

    # Selection Options: Displayed above the plots
    st.markdown("""  
    This page focuses on **groups of protestors** in USA, providing the trendlines aggregated by week/month showcasing 
    different protest groups over a selected period of time.
    """)

    st.subheader("How To Use:")
    st.markdown("""
    - Select the start date and end date for the period you wish to view.
    - Select the groups of protestors you wish to analyze.
    - Select whether you'd like to view the amount of **protests** or the amount of **protestors**.
    - Select the time resolution (week or month).
    - You can zoom in on the plots by selecting a specific area on the plot using your mouse.
    """)

    # Filter Options
    st.subheader("Filter Options")

    # Define date range for selection
    min_date = protests_df['event_date'].min().date()
    max_date = protests_df['event_date'].max().date()

    # Create a row with columns where the group selection is wider
    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])

    with col1:
        # Start date picker
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        # End date picker
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    # Ensure start_date is before end_date
    if start_date > end_date:
        st.error("Start date must be before or equal to the end date.")

    with col3:
        # Group selection
        display_groups = [format_group_name(group) for group in original_groups_with_colors.keys()]

        # Define default groups to be preselected
        default_display_groups = ["Palestenian", "Jewish", "Students", "LGBT"]

        # Multi-select dropdown for groups (without "Select All" checkbox)
        selected_display_groups = st.multiselect(
            "Groups",
            display_groups,
            default=default_display_groups
        )

        # Map back to original group names for processing
        selected_groups = [inverse_format_group_name(group) for group in selected_display_groups]

    with col4:
        # Metric selection
        metric = st.radio(
            "Show:",
            ['Number of Protests', 'Number of Protestors'],
            horizontal=True
        )

    with col5:
        # Aggregation selection
        aggregation = st.radio(
            "Resolution:",
            ['Week', 'Month'],
            horizontal=True
        )

    # Plot for Pro Palestine
    palestine_plot, grouped_data_p = visualize_line_plot(protests_df, start_date, end_date, selected_groups, metric, aggregation, pro_palestine=True)

    # Plot for Pro Israel
    israel_plot, grouped_data_i = visualize_line_plot(protests_df, start_date, end_date, selected_groups, metric, aggregation, pro_palestine=False)

    # Get the maximum y-value between the two plots
    y_column = 'num_protests' if metric == 'Number of Protests' else 'total_crowd'
    y_max = max(grouped_data_p[y_column].max(), grouped_data_i[y_column].max())
    y_max = y_max * 1.25 if y_max > 0 else 10  # Add 10% buffer, minimum 10

    # Set the same y-axis limit for both plots
    palestine_plot.update_layout(yaxis=dict(range=[0, y_max]))
    israel_plot.update_layout(yaxis=dict(range=[0, y_max]))

    # Display both plots side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pro Palestine Protests")
        st.plotly_chart(palestine_plot, use_container_width=True)

    with col2:
        st.subheader("Pro Israel Protests")
        st.plotly_chart(israel_plot, use_container_width=True)
