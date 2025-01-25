import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_TIME, 'en_GB')


# Set page configuration to wide layout
st.set_page_config(layout="wide")

# Load the datasets
@st.cache_data
def load_protests_data():
    return pd.read_csv("C:\\Users\\User\\Downloads\\protests us final.csv")

@st.cache_data
def load_timeline_data():
    return pd.read_csv("C:\\Users\\User\\Downloads\\Timeline_cleaned.csv")

# Load data
protests_df = load_protests_data()
timeline_df = load_timeline_data()

# Convert dates to datetime format
protests_df['event_date'] = pd.to_datetime(protests_df['event_date'], dayfirst=True)
timeline_df['Date'] = pd.to_datetime(timeline_df['Date'])



# Define date range
START_DATE = datetime(2023, 10, 8)
END_DATE = datetime(2024, 11, 7)

# Filter data within the specified date range
protests_df = protests_df[
    (protests_df['event_date'] >= START_DATE) & 
    (protests_df['event_date'] <= END_DATE)
]
timeline_df = timeline_df[
    (timeline_df['Date'] >= START_DATE) & 
    (timeline_df['Date'] <= END_DATE)
]

# Remove missing values
protests_df = protests_df.dropna(subset=['event_date'])
timeline_df = timeline_df.dropna(subset=['Date'])

# Sort timeline dates
timeline_df = timeline_df.sort_values('Date')

# Create options for selection bars
date_options = []
for _, row in timeline_df.iterrows():
    formatted_date = row['Date'].strftime("%d/%m/%Y")
    date_options.append(f"{formatted_date} - {row['Event']}")

# Title and description
st.title("Protests in North America")
st.markdown("Explore protest trends during the Israel–Hamas war.")

# Function to create date input with specific range
def custom_date_input(label, key, default_date=None):
    return st.date_input(
        label, 
        value=default_date,
        min_value=START_DATE.date(), 
        max_value=END_DATE.date(), 
        key=key
    )

# Function to check if a date has protests
def get_protests_for_date(selected_date):
    date_protests = protests_df[protests_df['event_date'].dt.date == selected_date.date()]

    return date_protests

# Function to find event for a given date (if exists in timeline)
def find_timeline_event(selected_date):
    timeline_row = timeline_df[timeline_df['Date'].dt.date == selected_date.date()]
    return timeline_row['Event'].iloc[0] if len(timeline_row) > 0 else "Not listed in special events"
def select_dates():
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### First Date Selection")
        col1_row1, col1_row2 = st.columns([1, 3], gap="small")
        
        with col1_row1:
            first_method = st.radio(
                "Method:",
                ["Predefined Events", "Custom Date"],
                key="first_method",
                horizontal=True
            )
        
        with col1_row2:
            if first_method == "Predefined Events":
                selected_date1 = st.selectbox(
                    "Date:",
                    options=date_options,
                    index=0,
                    key="date1"
                )
                date1 = datetime.strptime(selected_date1.split(' - ')[0], '%d/%m/%Y')
                event1 = selected_date1.split(' - ')[1]
            else:
                date1 = custom_date_input(
                    "Custom Date:", 
                    key="custom_date1",
                    default_date=datetime(2023, 10, 8).date()
                )
                date1 = datetime.combine(date1, datetime.min.time())
                event1 = find_timeline_event(date1)

    with col2:
        st.markdown("### Second Date Selection")
        col2_row1, col2_row2 = st.columns([1, 3], gap="small")
        
        with col2_row1:
            second_method = st.radio(
                "Method:",
                ["Predefined Events", "Custom Date"],
                key="second_method",
                horizontal=True
            )
        
        with col2_row2:
            if second_method == "Predefined Events":
                filtered_options = date_options if first_method != "Predefined Events" else [option for option in date_options if option != selected_date1]
                selected_date2 = st.selectbox(
                    "Date:",
                    options=filtered_options,
                    index=0,
                    key="date2"
                )
                date2 = datetime.strptime(selected_date2.split(' - ')[0], '%d/%m/%Y')
                event2 = selected_date2.split(' - ')[1]
            else:
                date2 = custom_date_input(
                    "Custom Date:", 
                    key="custom_date2", 
                    default_date=datetime(2023, 10, 9).date()
                )
                date2 = datetime.combine(date2, datetime.min.time())
                event2 = find_timeline_event(date2)
    
    return date1, date2, event1, event2



# Get selected dates and events
date1, date2, event1, event2 = select_dates()


def get_population_details(selected_date):
    filtered_df = protests_df[protests_df['event_date'] == selected_date]
    
    population_groups = [
        'palestenian_group', 'jewish_group', 'students_group', 
        'teachers_group', 'women_group', 'political_group', 
        'lgbt_group', 'other_group'
    ]
    
    group_counts = {group: filtered_df[group].sum() for group in population_groups}
    
    most_prevalent_group = max(group_counts, key=group_counts.get) if group_counts else None
    
    max_crowd_size = filtered_df['Crowd_size'].max()
    
    violent_protests = filtered_df['Violent'].max()
    
    return {
        'most_prevalent_group': most_prevalent_group.replace('_', ' ').replace('group', '').strip() if most_prevalent_group else 'No group found',
        'group_count': group_counts.get(most_prevalent_group, 0),
        'max_crowd_size': max_crowd_size if max_crowd_size != -1 else 'No information about crowd size for the selected date',
        'violent_protests': 'YES' if violent_protests == 1 else 'NO'
    }

# Function to create protest graph with consistent scaling
def create_protest_graph(center_date, event, max_y):
    start_date = center_date - timedelta(days=10)
    end_date = center_date + timedelta(days=10)
    
    # Filter protests within date range
    mask = (protests_df['event_date'] >= start_date) & (protests_df['event_date'] <= end_date)
    filtered_df = protests_df[mask]
    
    # Create date range for complete x-axis
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Split data into selected date and other dates
    selected_df = filtered_df[filtered_df['event_date'].dt.date == center_date.date()]
    
    # Create the stacked bar plot
    fig = go.Figure()
    
    # Add traces for other dates (with lower opacity)
    for date in date_range:
        if date.date() != center_date.date():
            day_data = filtered_df[filtered_df['event_date'].dt.date == date.date()]
            
            # Pro Israel
            count = len(day_data[day_data['Pro Israel'] == 1])
            if count > 0:
                fig.add_trace(go.Bar(x=[date], y=[count], name='Pro Israel',
                                   marker_color='blue', opacity=0.5, showlegend=False))
            
            # Pro Palestine
            count = len(day_data[day_data['Pro Palestine'] == 1])
            if count > 0:
                fig.add_trace(go.Bar(x=[date], y=[count], name='Pro Palestine',
                                   marker_color='red', opacity=0.5, showlegend=False))
    
    # Add traces for selected date (with full opacity)
    # Pro Israel
    count = len(selected_df[selected_df['Pro Israel'] == 1])
    if count > 0:
        fig.add_trace(go.Bar(x=[center_date], y=[count], name='Pro Israel',
                           marker_color='blue', showlegend=True))
    
    # Pro Palestine
    count = len(selected_df[selected_df['Pro Palestine'] == 1])
    if count > 0:
        fig.add_trace(go.Bar(x=[center_date], y=[count], name='Pro Palestine',
                           marker_color='red', showlegend=True))
    
    # Title with event information
    
    fig.update_layout(
        title='',
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Number of Protests",
        barmode='stack',
        height=400,
        yaxis=dict(range=[0, max_y]),  # Set consistent y-axis range
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Calculate max y-value for consistent scaling
def get_max_y_value(date1, date2):
    def calculate_max_for_date(date):
        start_date = date - timedelta(days=10)
        end_date = date + timedelta(days=10)
        
        mask = (protests_df['event_date'] >= start_date) & (protests_df['event_date'] <= end_date)
        filtered_df = protests_df[mask]
        
        # Calculate daily totals
        daily_totals = filtered_df.groupby(filtered_df['event_date'].dt.date).apply(
            lambda x: len(x[x['Pro Israel'] == 1]) + len(x[x['Pro Palestine'] == 1])
        )
        
        return daily_totals.max() if not daily_totals.empty else 0
    
    return max(calculate_max_for_date(date1), calculate_max_for_date(date2))

# Get max y-value for consistent scaling
max_y = get_max_y_value(date1, date2)

# Create graphs
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Protests around {date1.strftime('%d/%m/%Y')}")
    st.markdown(f"*Event:* {event1}")
    st.plotly_chart(create_protest_graph(date1, event1, max_y), use_container_width=True)
    
    pop_details1 = get_population_details(date1)
    st.markdown(f"""
    *Protest Details:*
    - Most Prevalent Group: {pop_details1['most_prevalent_group'].title()}
    - Largest Crowd Size: {pop_details1['max_crowd_size']}
    - Violent Protest: {pop_details1['violent_protests']}

    """)

with col2:
    st.markdown(f"### Protests around {date2.strftime('%d/%m/%Y')}")
    st.markdown(f"*Event:* {event2}")
    st.plotly_chart(create_protest_graph(date2, event2, max_y), use_container_width=True)

    pop_details2 = get_population_details(date2)
    st.markdown(f"""
    *Protest Details:*
    - Most Prevalent Group: {pop_details2['most_prevalent_group'].title()}
    - Largest Crowd Size: {pop_details2['max_crowd_size']}
    - Violent Protest: {pop_details2['violent_protests']}
    """)