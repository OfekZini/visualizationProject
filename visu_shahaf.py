import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page configuration to wide layout
# st.set_page_config(layout="wide")

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

        # Create the scatter_geo plot
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
                'latitude': False,
                'longitude': False,
            },
            hover_name=None,
            custom_data=['Protest_Type', 'admin1', 'formatted_date']
        )

        # Update hover template and marker opacity
        fig.update_traces(
            hovertemplate=(
                    "Protest Type: %{customdata[0]}<br>" +
                    "State: %{customdata[1]}<br>" +
                    "Event Date: %{customdata[2]}<br>" +
                    "<extra></extra>"
            ),
            marker=dict(opacity=0.6)
        )

        # Adjust layout and height
        fig.update_layout(
            height=650,
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
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
            opacity=0.7
        ))

        fig1.update_layout(
            title="Pro-Israel Protests Over Time",
            xaxis_title="Date",
            yaxis_title="Count of Protests",
            xaxis_range=date_range,
            xaxis=dict(
                dtick="M1",
                tickformat="%b %Y",
                tickangle=45
            ),
            yaxis_range=[0, max_monthly_protests],
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
            opacity=0.7
        ))

        fig2.update_layout(
            title="Pro-Palestine Protests Over Time",
            xaxis_title="Date",
            yaxis_title="Count of Protests",
            xaxis_range=date_range,
            xaxis=dict(
                dtick="M1",
                tickformat="%b %Y",
                tickangle=45
            ),
            yaxis_range=[0, max_monthly_protests],
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

    st.title("Protests in the USA: October 7th, 2023, and Beyond")

    st.markdown("""
    <style>
        .main-title { font-size: 28px; font-weight: bold; text-align: center; }
        .section-title { font-size: 20px; font-weight: bold; margin-top: 20px; }
        .highlight { color: #FF5733; font-weight: bold; }
        .info-text { font-size: 16px; line-height: 1.6; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

    # st.markdown(
    #     '<p class="main-title">This dashboard offers a comprehensive analysis of protests in the United States.</p>',
    #     unsafe_allow_html=True)

    st.markdown("""
    <div class="info-text">
    The data covers both <span class="highlight">Pro-Israeli</span> and <span class="highlight">Pro-Palestinian</span> protests from 
    October 7th, 2023, to November 8th, 2024.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-title">Key Questions Explored:</p>', unsafe_allow_html=True)
    st.markdown("""
    - Where are the protests happening? (State-by-state analysis)
    - What types of groups are involved? (Political groups, LGBTQ+, students, etc.)
    - Are protests more frequent around significant events?
    - What is the ratio of violent protests to peaceful ones?
    """)

    st.markdown('<p class="section-title">Protest Locations Across the USA</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-text">
    Each point on the map represents a protest event. Hover over a point to view detailed event information.
    </div>

    <div class="info-text">
    Features of the map:
    - Use the <span class="highlight">state selection box</span> (on the right) to filter protests by state.
    - Toggle between <span class="highlight">Pro-Israeli</span> and <span class="highlight">Pro-Palestinian</span> protests using the legend.
    - View monthly protest counts for a selected state on the right side of the dashboard.
    </div>
    """, unsafe_allow_html=True)

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
        # print in terminal the selected state
        usa_map = plot_usa_map(protests_df, selected_state)
        st.plotly_chart(usa_map, use_container_width=True, height=700)  # Larger map height
