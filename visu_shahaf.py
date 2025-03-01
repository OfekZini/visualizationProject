import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def app():
    # Load the dataset
    @st.cache_data
    def load_data():
        return pd.read_csv('protests us final.csv')

    protests_df = load_data()

    # Preprocessing
    protests_df['event_date'] = pd.to_datetime(protests_df['event_date'], format='%d/%m/%Y')  # desired date format
    protests_df = protests_df.sort_values('event_date')  # sorting by date
    protests_df = protests_df[protests_df['country'] == 'United States']  # keeping protests from the USA only

    # Map count visualization
    def plot_usa_map(filtered_data, selected_state=None):
        # Create a new column for protest type
        filtered_data['Protest_Type'] = filtered_data.apply(
            lambda row: 'Pro Israel' if row['Pro Israel'] == 1 else
            ('Pro Palestine' if row['Pro Palestine'] == 1 else None),
            axis=1
        )

        # Format the date column for hover display
        filtered_data['formatted_date'] = filtered_data['event_date'].dt.strftime('%d/%m/%Y')

        # Create a copy of the filtered data
        plot_data = filtered_data.copy()

        # Adjust opacity based on selected state
        if selected_state and selected_state != "All States":
            plot_data = plot_data[plot_data['admin1'] == selected_state]

        # In the plot_usa_map function
        fig = px.scatter_geo(
            plot_data,
            lat='latitude',
            lon='longitude',
            color='Protest_Type',
            color_discrete_map={"Pro Israel": "blue", "Pro Palestine": "red"},
            scope="usa",
            hover_data={
                'Protest_Type': True,
                'admin1': True,
                'formatted_date': True,
                'Crowd_size': True,  # Add Crowd_size to hover data
                'latitude': False,
                'longitude': False,
            },
            hover_name=None,
            custom_data=['Protest_Type', 'admin1', 'formatted_date', 'Crowd_size']  # Add Crowd_size to custom_data
        )

        # Update hover template to include Crowd_size
        fig.update_traces(
            hovertemplate=(
                    "Protest Type: %{customdata[0]}<br>" +
                    "State: %{customdata[1]}<br>" +
                    "Event Date: %{customdata[2]}<br>" +
                    "Crowd Size: %{customdata[3]}<br>" +  # Add this line to display crowd size
                    "<extra></extra>"
            ),
            marker=dict(opacity=0.6)
        )

        # Adjust layout and height
        fig.update_layout(
            height=650,
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            legend_title="Protest Type"
        )

        return fig

    # Time-series histogram charts by selected state
    def plot_chronological_analysis(data, selected_state):
        # Get the full date range and extend the start date to October 2023
        min_date = pd.Timestamp('2023-10-01')  # Set to start of October 2023
        max_date = data['event_date'].max()
        date_range = [min_date, max_date]

        # Filter data by state if selected
        filtered_data = data
        if selected_state and selected_state != "All States":
            filtered_data = data[data['admin1'] == selected_state]

        # Calculate monthly sums for the filtered dataset
        monthly_sums_israel = filtered_data[filtered_data['Pro Israel'] == 1].groupby(
            filtered_data['event_date'].dt.to_period('M')).size()
        monthly_sums_palestine = filtered_data[filtered_data['Pro Palestine'] == 1].groupby(
            filtered_data['event_date'].dt.to_period('M')).size()

        # Find the maximum monthly sum across both types of protests for the selected state
        max_monthly_protests = max(
            monthly_sums_israel.max() if len(monthly_sums_israel) > 0 else 0,
            monthly_sums_palestine.max() if len(monthly_sums_palestine) > 0 else 0
        )

        yaxis_max = max_monthly_protests * 1.2 if max_monthly_protests > 0 else 10  # Add 20% buffer, minimum 10

        # allocate relevant subsets of the data by the protest type
        pro_israel = filtered_data[filtered_data['Pro Israel'] == 1]
        pro_palestine = filtered_data[filtered_data['Pro Palestine'] == 1]

        # Create the first histogram for Pro-Israel protests
        fig1 = go.Figure()

        fig1.add_trace(go.Histogram(
            x=pro_israel['event_date'],
            name='Pro-Israel',
            marker=dict(color='blue'),
            nbinsx=30,
            opacity=1
        ))

        fig1.update_layout(
            title="Pro-Israel Protests Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Protests",
            xaxis_range=date_range,
            xaxis=dict(
                dtick="M1",
                tickformat="%b %Y",
                tickangle=45
            ),
            yaxis_range=[0, yaxis_max],
            height=300,
            width=800,
            margin=dict(
                l=50,
                r=20,
                t=40,
                b=80
            ),
            barmode='overlay'
        )

        # Create the second histogram for Pro-Palestine protests
        fig2 = go.Figure()

        fig2.add_trace(go.Histogram(
            x=pro_palestine['event_date'],
            name='Pro-Palestine',
            marker=dict(color='red'),
            nbinsx=30,
            opacity=1
        ))

        fig2.update_layout(
            title="Pro-Palestine Protests Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Protests",
            xaxis_range=date_range,
            xaxis=dict(
                dtick="M1",
                tickformat="%b %Y",
                tickangle=45
            ),
            yaxis_range=[0, yaxis_max],
            height=300,
            width=800,
            margin=dict(
                l=50,
                r=20,
                t=40,
                b=80
            ),
            barmode='overlay'
        )

        return fig1, fig2

    st.markdown(
        """
        <style>
            .highlight {
                background-color: orange;
                font-weight: bold;
                padding: 2px 4px;
                border-radius: 4px;
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Where are the protests happening?")

    st.markdown(
        """
        This page provides a detailed analysis of **protests locations** in the USA during the first year of Swords of Iron
        War, following state-by-state analysis of the amount of protests occurred in every state.
        """
    )

    st.subheader("How To Use:")
    st.markdown("""
        **USA Map of Protests:**\n
        - Use the legend in order to filter Protest Type.
        - You can zoom in and out on the map using the tools menu or your mouse scroller, press 'Reset' on the tools
        menu in order to reset the zoom.
        - Hover over the points on the map to see the protest type, state, and event date.\n
            
        **State Selection and Chronological Analysis:**\n
        - Select the state you wish to observe (default - All States).
        - The y-axis scale is aligned for both plots, you can reset the scales by pressing the 'Autoscale' button. You
        can also reset to default scales by pressing the 'Reset axes' button.
        """)

    # Create a two-column layout with adjusted widths
    col1, col2 = st.columns([3, 2])  # col1 (map) is wider, col2 (plots) is narrower

    # State selection bar and time-series charts on the right (col2)
    with col2:
        st.subheader("State Selection and Chronological Analysis")  # subheader

        # Custom CSS to adjust the width of the selectbox to 50%
        st.markdown("""
            <style>
            div[data-baseweb="select"] > div {
                max-width: 200px; /* Set the maximum width */
                width: 50%; /* Set the desired width */
            }
            </style>
            """, unsafe_allow_html=True)

        # Create state selection bar
        all_states = ["All States"] + sorted(protests_df['admin1'].dropna().unique(), key=str)
        selected_state = st.selectbox("Select a State", all_states, index=0)

        # Generate the time-series plots
        fig1, fig2 = plot_chronological_analysis(protests_df, selected_state)

        # Display the two plots stacked vertically
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

    # Map on the left (col1)
    with col1:
        st.subheader("USA Map of Protests")  # subheader
        usa_map = plot_usa_map(protests_df, selected_state)
        st.plotly_chart(usa_map, use_container_width=True, height=700)  # Larger map height
