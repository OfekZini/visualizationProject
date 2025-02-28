import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def app():
    # Load the dataset
    @st.cache_data
    def load_data():
        return pd.read_csv('protests us final.csv')

    @st.cache_data
    def load_timeline():
        return pd.read_csv("shrinked timeline.csv")

    protests_df = load_data()
    timeline_df = load_timeline()

    # Convert dates
    protests_df['event_date'] = pd.to_datetime(protests_df['event_date'], dayfirst=True)

    # Title
    st.title("Violent Protests Overview")

    st.markdown("""  
        This page focuses on **violent protests** for **Pro-Isareli, Pro-Palestinian, and Two-sided protests** in the USA.
        """)

    st.subheader("How To Use:")
    st.markdown("""
        **Violent Protestors:**\n
        - Hover with your mouse over the curves to see specific date and crowd size of the evebt.
        - The y-axis scale is aligned for all plots, you can reset the scales by pressing the 'Autoscale' button. You
        can also reset to default scales by pressing the 'Reset axes' button.\n
            
        **Violent vs Non-Violent Distribution:**\n
        - Hover with your mouse over the bars to see the percentage and count of violent and non-violent protests.\n
        
        **Peak Events:**\n
        - The section on the buttom right displays the peak event for each protest category.
            """)

    # Colors for different protest types
    colors = {
        "Pro Palestine Protests": "#FF0000",  # Red
        "Pro Israel Protests": "#0000FF",  # Blue
        "Two-sided Protests": "#800080"  # Purple
    }

    # Main layout
    col1, col2 = st.columns([1, 1])  # Adjusted the width of col1 to be narrower

    # Define protest types and their corresponding filters (Reordered)
    protest_types = {
        "Two-sided Protests": (protests_df['Pro Palestine'] == 1) &
                              (protests_df['Pro Israel'] == 1) &
                              (protests_df['Violent'] == 1),

        "Pro Palestine Protests": (protests_df['Pro Palestine'] == 1) &
                                  (protests_df['Violent'] == 1) &
                                  (protests_df['Pro Israel'] == 0),

        "Pro Israel Protests": (protests_df['Pro Israel'] == 1) &
                               (protests_df['Violent'] == 1) &
                               (protests_df['Pro Palestine'] == 0)
    }

    # Find the global min and max event_date for a consistent x-axis range
    global_min_date = protests_df['event_date'].min()
    global_max_date = pd.Timestamp("2024-11-30")  # Ensure it extends to Nov 2024

    with col1:
        # Initialize subplots
        fig = make_subplots(rows=3, cols=1, shared_xaxes=False, subplot_titles=list(protest_types.keys()))

        max_y_value = 0  # Variable to store the maximum y-value

        # Loop through protest types and add traces
        for i, (protest_type, condition) in enumerate(protest_types.items(), start=1):
            data = protests_df[condition]

            if not data.empty:  # Avoid adding empty traces
                grouped = data.groupby(data['event_date'].dt.to_period('D')).agg({'Crowd_size': 'sum'}).reset_index()
                grouped['event_date'] = grouped['event_date'].dt.to_timestamp()

                max_y_value = max(max_y_value, grouped['Crowd_size'].max())  # Update max y-value

                fig.add_trace(
                    go.Scatter(
                        x=grouped['event_date'],
                        y=grouped['Crowd_size'],
                        mode='lines',
                        name=protest_type,
                        line=dict(color=colors[protest_type], width=2),
                        hovertemplate="<b>Date:</b> %{x}<br><b>Total Crowd Size:</b> %{y}"
                    ),
                    row=i, col=1
                )

        # Update layout
        fig.update_layout(
            title="Number of Violent Protesters Over Time",
            height=750,  # Reduced height
            template="plotly_white",
            showlegend=False,  # Remove legend since titles indicate each protest type
            xaxis_range=[global_min_date, global_max_date]  # Extend x-axis to Nov 2024
        )

        # Set the same y-axis range across all subplots
        for i in range(1, 4):
            fig.update_yaxes(range=[0, max_y_value], row=i, col=1, title_text="Number of Protesters")
            fig.update_xaxes(title_text="Date", row=i, col=1,
                             range=[global_min_date, global_max_date])  # Ensure same x-range

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Define the correct order
        protest_categories = ["Pro Israel Protests", "Pro Palestine Protests", "Two-sided Protests"]

        violent_counts = []
        non_violent_counts = []
        total_counts = []

        for category in protest_categories:
            if category == "Pro Palestine Protests":
                filtered_df = protests_df[(protests_df['Pro Palestine'] == 1) & (protests_df['Pro Israel'] == 0)]
            elif category == "Pro Israel Protests":
                filtered_df = protests_df[(protests_df['Pro Israel'] == 1) & (protests_df['Pro Palestine'] == 0)]
            else:
                filtered_df = protests_df[(protests_df['Pro Palestine'] == 1) & (protests_df['Pro Israel'] == 1)]

            violent_count = len(filtered_df[filtered_df['Violent'] == 1])
            non_violent_count = len(filtered_df) - violent_count
            total_count = violent_count + non_violent_count

            violent_counts.append(violent_count)
            non_violent_counts.append(non_violent_count)
            total_counts.append(total_count)

            # Convert to percentage
        violent_percentages = [(v / t * 100) if t > 0 else 0 for v, t in zip(violent_counts, total_counts)]
        non_violent_percentages = [(nv / t * 100) if t > 0 else 0 for nv, t in zip(non_violent_counts, total_counts)]

        # Append total count to category names for y-axis labels
        protest_categories_with_totals = [f"{cat} ({total})" for cat, total in zip(protest_categories, total_counts)]

        # Define colors
        colors = {
            "Pro Palestine Protests": "#FF0000",
            "Pro Israel Protests": "#0000FF",
            "Two-sided Protests": "#800080"
        }

        # Create stacked bar plot
        fig_stacked_bar = go.Figure()

        fig_stacked_bar.add_trace(go.Bar(
            name="Violent",
            y=protest_categories_with_totals,
            x=violent_percentages,
            orientation='h',
            marker=dict(color=[colors[cat] for cat in protest_categories]),
            text=[f"{p:.1f}% ({c})" for p, c in zip(violent_percentages, violent_counts)],
            textposition="inside"
        ))

        fig_stacked_bar.add_trace(go.Bar(
            name="Non-Violent",
            y=protest_categories_with_totals,
            x=non_violent_percentages,
            orientation='h',
            marker=dict(color="#ADADAD"),
            text=[f"{p:.1f}% ({c})" for p, c in zip(non_violent_percentages, non_violent_counts)],
            textposition="inside",
            insidetextfont=dict(color="white")
        ))

        # Update layout for better visibility
        fig_stacked_bar.update_layout(
            title="Violent vs. Non-Violent Protest Distribution",
            barmode="stack",
            height=300,  # Reduce height for compact view
            xaxis_title="Percentage (%)",
            yaxis_title="Protest Category",
            template="plotly_white",
            xaxis=dict(range=[0, 100]),  # Ensure 100% is visible
            bargap=0.2,  # Reduce width between bars
            margin=dict(l=50, r=20, t=50, b=50),  # Adjust margins for balance
            showlegend=False
        )

        # Display the stacked bar chart
        st.plotly_chart(fig_stacked_bar, use_container_width=True)

        # Find peak event dates with the highest 'Crowd_size' for violent protests
        peak_events = {}

        for category, condition in protest_types.items():
            violent_protests = protests_df[condition]
            if not violent_protests.empty:
                # Find the protest with the highest crowd size for this category
                peak_protest_idx = violent_protests['Crowd_size'].idxmax()
                peak_protest = violent_protests.loc[peak_protest_idx]
                peak_date = peak_protest['event_date']
                peak_crowd_size = peak_protest['Crowd_size']

                # Find the closest event in the timeline data
                timeline_df['Date'] = pd.to_datetime(timeline_df['Date'], errors='coerce')
                timeline_df['date_diff'] = abs(timeline_df['Date'] - peak_date)
                closest_event_idx = timeline_df['date_diff'].idxmin()
                closest_event = timeline_df.loc[closest_event_idx]

                # Store the information for this category
                peak_events[category] = {
                    'event_name': closest_event['Event'],
                    'event_date': closest_event['Date'].strftime('%d-%m-%Y'),
                    'protest_date': peak_date.strftime('%Y-%m-%d'),
                    'crowd_size': peak_crowd_size
                }

        # Create empty columns to push the peak events section to the right
        _, right_content = st.columns([0.1, 0.9])  # 20% empty space, 80% content

        with right_content:
            st.subheader("Peak Events")
            for category, event_info in peak_events.items():
                st.markdown(f"""**{category}:**  
        Event Name: {event_info['event_name']}  
        Date: {event_info['event_date']}  
        Total Protesters: {int(event_info['crowd_size']):,}""")

    # Adjust the layout for columns
    col1, col2 = st.columns([2, 1])  # Slightly reduce width of col2 to increase distance


