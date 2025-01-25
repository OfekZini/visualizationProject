import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# # Set page configuration to wide layout
# st.set_page_config(layout="wide")


def app():
    # Set page configuration to wide layout
    # st.set_page_config(page_title="Data Visualisation", layout="wide")
# Load the datasets
    @st.cache_data
    def load_data():
        protests_df = pd.read_csv(r'protests us final.csv')
        timeline_df = pd.read_excel(r'Timeline.xlsx')
        return protests_df, timeline_df

    protests_df, timeline_df = load_data()

    # Convert dates
    protests_df['event_date'] = pd.to_datetime(protests_df['event_date'], dayfirst=True)
    timeline_df['Date'] = pd.to_datetime(timeline_df['Date'], dayfirst=True)

    # Title
    st.title("Protests in North America")

    # Create multi-select for protest types
    st.subheader("Select protest types to visualize:")
    col1, col2, col3 = st.columns(3)
    with col1:
        pro_palestine = st.checkbox("Pro Palestine", value=True)
    with col2:
        pro_israel = st.checkbox("Pro Israel")
    with col3:
        both = st.checkbox("Pro Israel & Pro Palestine")

    # Colors for different protest types
    colors = {
        "Pro Palestine": "#FF0000",  # Red
        "Pro Israel": "#0000FF",    # Blue
        "Pro Israel & Pro Palestine": "#800080"  # Purple
    }

    # Main content
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # Initialize figure
        fig = go.Figure()

        # Add selected protest types to the graph
        selected_types = []
        if pro_palestine:
            data = protests_df[(protests_df['Pro Palestine'] == 1) &
                               (protests_df['Violent'] == 1) &
                               (protests_df['Pro Israel'] == 0)]
            selected_types.append(("Pro Palestine", data))

        if pro_israel:
            data = protests_df[(protests_df['Pro Israel'] == 1) &
                               (protests_df['Violent'] == 1) &
                               (protests_df['Pro Palestine'] == 0)]
            selected_types.append(("Pro Israel", data))

        if both:
            data = protests_df[(protests_df['Pro Palestine'] == 1) &
                               (protests_df['Pro Israel'] == 1) &
                               (protests_df['Violent'] == 1)]
            selected_types.append(("Pro Israel & Pro Palestine", data))

        # Add traces for selected types
        for protest_type, data in selected_types:
            grouped = data.groupby(data['event_date'].dt.to_period('D')).agg({
                'Crowd_size': 'sum'
            }).reset_index()

            # Convert the 'event_date' index to proper datetime format
            grouped['event_date'] = grouped['event_date'].dt.to_timestamp()

            fig.add_trace(go.Scatter(
                x=grouped['event_date'],
                y=grouped['Crowd_size'],
                mode='lines',
                name=protest_type,
                line=dict(color=colors[protest_type], width=2),
                fill='tozeroy',
                hovertemplate="<b>Date:</b> %{x}<br><b>Total Crowd Size:</b> %{y}"
            ))

        fig.update_layout(
            title="Violent Protests Over Time",
            xaxis_title="Date",
            yaxis_title="Total Crowd Size",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("Insights")
        selected_types = []

        if pro_palestine:
            selected_types.append("Pro Palestine")
        if pro_israel:
            selected_types.append("Pro Israel")
        if both:
            selected_types.append("Pro Israel & Pro Palestine")

        if len(selected_types) == 1:
            protest_type = selected_types[0]

            # Filter the dataset for the selected protest type
            if protest_type == "Pro Palestine":
                filtered_df = protests_df[(protests_df['Pro Palestine'] == 1) & (protests_df['Pro Israel'] == 0)]
            elif protest_type == "Pro Israel":
                filtered_df = protests_df[(protests_df['Pro Israel'] == 1) & (protests_df['Pro Palestine'] == 0)]
            else:  # Both
                filtered_df = protests_df[(protests_df['Pro Palestine'] == 1) & (protests_df['Pro Israel'] == 1)]

            # Violent vs Non-Violent Protests
            violent_protests = len(filtered_df[filtered_df['Violent'] == 1])
            non_violent_protests = len(filtered_df) - violent_protests

            # Horizontal stacked bar plot
            fig_violent = go.Figure()
            fig_violent.add_trace(go.Bar(
                name="Violent",
                y=[protest_type],
                x=[violent_protests],
                marker=dict(color=colors[protest_type], line=dict(width=0)),
                text=f"{violent_protests} Violent",
                textposition="auto",
                orientation="h"
            ))
            fig_violent.add_trace(go.Bar(
                name="Non-Violent",
                y=[protest_type],
                x=[non_violent_protests],
                marker=dict(color="#D3D3D3", line=dict(width=0)),
                text=f"{non_violent_protests} Non-Violent",
                textposition="auto",
                orientation="h"
            ))

            fig_violent.update_layout(
                title="Violent vs Non-Violent Protests",
                barmode="stack",
                height=200,
                xaxis_title="Number of Protests",
                yaxis_title="",
                template="plotly_white",
                xaxis=dict(showgrid=False,showticklabels=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_violent, use_container_width=True)

            # Group Participation (same as before)
            groups = [
                'palestenian_group', 'jewish_group', 'students_group',
                'teachers_group', 'women_group', 'political_group',
                'lgbt_group', 'other_group'
            ]
            group_colors = {
                'palestenian_group': "#FF0000",  # Red
                'jewish_group': "#0000FF",      # Blue
                'students_group': "#800080",    # Purple
                'teachers_group': "#FFFF00",    # Yellow
                'women_group': "#00FF00",       # Green
                'political_group': "#FFA500",   # Orange
                'lgbt_group': "#FFC0CB",        # Pink
                'other_group': "#808080"        # Grey
            }

            group_counts = {group: filtered_df[group].sum() for group in groups if group in filtered_df.columns}
            group_totals = sum(group_counts.values())

            # Combine groups with <10% into "Other"
            threshold = 5
            processed_groups = {}
            other_count = 0

            for group, count in group_counts.items():
                percentage = (count / group_totals * 100) if group_totals > 0 else 0
                if percentage >= threshold:
                    processed_groups[group] = percentage
                else:
                    other_count += percentage

            if other_count > 0:
                processed_groups['Combine'] = other_count

            # Build the updated bar chart
            fig_groups = go.Figure()
            for group, percentage in processed_groups.items():
                fig_groups.add_trace(go.Bar(
                    name="",  # No legend name
                    y=["Group Participation"],
                    x=[percentage],
                    marker=dict(color=group_colors.get(group, "#808080"), line=dict(width=0)),
                    text=f"{percentage:.1f}% ({group.replace('_group', '').title()})",
                    textposition="inside",
                    orientation="h",
                    hovertemplate=f"<b>{group.replace('_group', '').title()}</b>: {percentage:.1f}%<extra></extra>"
                ))

            fig_groups.update_layout(
                title="Group Participation Distribution",
                barmode="stack",
                height=200,
                xaxis_title="Percentage (%)",
                yaxis_title="",
                template="plotly_white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False,showticklabels=False),
                showlegend=False  # Disable legend
            )
            st.plotly_chart(fig_groups, use_container_width=True)
        else:

            # Filter the dataset to include only violent protests
            violent_protests_df = protests_df[protests_df['Violent'] == 1]

            # If multiple or no types are selected, show "In Total" breakdown
            total_protests = len(violent_protests_df)

            # Count how many protests were for each type
            pro_palestine_count = len(violent_protests_df[(violent_protests_df['Pro Palestine'] == 1) & (violent_protests_df['Pro Israel'] == 0) & (violent_protests_df['Violent'] == 1)])
            pro_israel_count = len(violent_protests_df[(violent_protests_df['Pro Israel'] == 1) & (violent_protests_df['Pro Palestine'] == 0) & (violent_protests_df['Violent'] == 1)])
            both_count = len(violent_protests_df[(violent_protests_df['Pro Palestine'] == 1) & (violent_protests_df['Pro Israel'] == 1) & (violent_protests_df['Violent'] == 1)])

            # Calculate percentages
            pro_palestine_pct = (pro_palestine_count / total_protests) * 100
            pro_israel_pct = (pro_israel_count / total_protests) * 100
            both_pct = (both_count / total_protests) * 100

            # Bar plot showing the breakdown in percentages
            fig_total = go.Figure()

            fig_total.add_trace(go.Bar(
                name="Pro Palestine Only",
                x=["Protest Type"],  # X-axis will display the category
                y=[pro_palestine_pct],
                marker=dict(color=colors["Pro Palestine"]),
                text=f"{pro_palestine_pct:.1f}%",
                textposition="auto"
            ))
            fig_total.add_trace(go.Bar(
                name="Pro Israel Only",
                x=["Protest Type"],
                y=[pro_israel_pct],
                marker=dict(color=colors["Pro Israel"]),
                text=f"{pro_israel_pct:.1f}%",
                textposition="auto"
            ))
            fig_total.add_trace(go.Bar(
                name="Pro Israel & Pro Palestine",
                x=["Protest Type"],
                y=[both_pct],
                marker=dict(color=colors["Pro Israel & Pro Palestine"]),
                text=f"{both_pct:.1f}%",
                textposition="auto"
            ))

            # Update layout for grouped bar plot
            fig_total.update_layout(
                title="In Total: Protest Type Breakdown",
                barmode="group",  # Change to "group" for side-by-side bars
                height=400,
                xaxis_title="Protest Type",
                yaxis_title="Percentage (%)",
                template="plotly_white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                showlegend=True  # Enable legend for better readability
            )

            st.plotly_chart(fig_total, use_container_width=True)

    # Bottom section
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Crowd Size Distribution")
        # Check if selected_types is empty before proceeding
        # Check if selected_types is empty before proceeding
        if selected_types:
            # Combine all relevant dataframes for selected protest types
            filtered_data = pd.DataFrame()  # Initialize an empty DataFrame
            if pro_palestine:
                filtered_data = pd.concat([filtered_data, protests_df[
                    (protests_df['Pro Palestine'] == 1) & (protests_df['Violent'] == 1) & (
                            protests_df['Pro Israel'] == 0)]])
            if pro_israel:
                filtered_data = pd.concat([filtered_data, protests_df[
                    (protests_df['Pro Israel'] == 1) & (protests_df['Violent'] == 1) & (
                            protests_df['Pro Palestine'] == 0)]])
            if both:
                filtered_data = pd.concat([filtered_data, protests_df[
                    (protests_df['Pro Palestine'] == 1) & (protests_df['Pro Israel'] == 1) & (
                            protests_df['Violent'] == 1)]])

            # Remove rows with NaN in the Crowd_size column
            filtered_data = filtered_data.dropna(subset=['Crowd_size'])

            if not filtered_data.empty:
                # Define bins and labels based on protest type
                if pro_israel and not pro_palestine and not both:
                    # Specific bins for Pro Israel protests
                    bins = [0, 50, 100, 150, 200, 250, 1000, 5000, 10000]
                    labels = ['1-50', '50-100', '100-150', '150-200', '200-250', '250-1000', '1000-5000', '5000+']
                else:
                    # General bins for other protest types
                    bins = [0, 150, 500, 1000, 5000, 10000]
                    labels = ['1-150', '150-500', '500-1000', '1000-5000', '5000+']

                # Adjust the binning process to include values greater than 5000
                filtered_data['size_range'] = pd.cut(filtered_data['Crowd_size'],
                                                     bins=bins,
                                                     labels=labels,
                                                     include_lowest=True,
                                                     right=True)

                # Manually add values greater than 5000 to the '5000+' category
                filtered_data.loc[filtered_data['Crowd_size'] > bins[-2], 'size_range'] = '5000+'

                # Count occurrences for each size range
                size_dist = filtered_data['size_range'].value_counts().reindex(labels, fill_value=0)

                # Determine color based on selected checkbox
                if pro_palestine and not pro_israel and not both:
                    bar_color = colors["Pro Palestine"]
                elif pro_israel and not pro_palestine and not both:
                    bar_color = colors["Pro Israel"]
                else:
                    bar_color = colors["Pro Israel & Pro Palestine"]

                # Create bar plot with dynamic color
                fig_size = px.bar(
                    x=size_dist.index.astype(str),
                    y=size_dist.values,
                    labels={"x": "Crowd Size", "y": "Number of Protests"},
                    title="Crowd Size Distribution",
                    color_discrete_sequence=[bar_color]  # Apply dynamic color
                )
                st.plotly_chart(fig_size)
            else:
                st.write("No data available for the selected protest types.")

    with right_col:
        st.subheader("Peak Events")

        # Check if selected_types is empty before proceeding
        if selected_types:
            # Combine all relevant dataframes for selected protest types
            filtered_data = pd.DataFrame()  # Initialize an empty DataFrame
            if pro_palestine:
                filtered_data = pd.concat([filtered_data, protests_df[
                    (protests_df['Pro Palestine'] == 1) & (protests_df['Violent'] == 1) & (
                                protests_df['Pro Israel'] == 0)]])
            if pro_israel:
                filtered_data = pd.concat([filtered_data, protests_df[
                    (protests_df['Pro Israel'] == 1) & (protests_df['Violent'] == 1) & (
                                protests_df['Pro Palestine'] == 0)]])
            if both:
                filtered_data = pd.concat([filtered_data, protests_df[
                    (protests_df['Pro Palestine'] == 1) & (protests_df['Pro Israel'] == 1) & (
                                protests_df['Violent'] == 1)]])

            if not filtered_data.empty:
                # Group data by date and sum crowd sizes
                grouped_data = filtered_data.groupby(filtered_data['event_date'].dt.to_period('D')).agg({
                    'Crowd_size': 'sum'
                }).reset_index()

                # Convert the 'event_date' index to proper datetime format
                grouped_data['event_date'] = grouped_data['event_date'].dt.to_timestamp()

                # Find top 2 peak events
                peaks = grouped_data.nlargest(2, 'Crowd_size')

                booli = True  # For displaying the section header once
                for i, peak in peaks.iterrows():
                    peak_date = peak['event_date']

                    # Find the closest event within -10 days
                    closest_event = timeline_df[
                        (timeline_df['Date'] <= peak_date) &
                        (timeline_df['Date'] >= peak_date - pd.Timedelta(days=10))
                        ]

                    # Get the most recent event (if any)
                    if not closest_event.empty:
                        closest_event = closest_event.iloc[-1]

                        st.write(f"*Date of the protest:* {peak_date.strftime('%d-%m-%Y')}")
                        st.write(f"*Event:* {closest_event['Event']}")
                        st.write(f"*Date of the Event:* {closest_event['Date'].strftime('%d-%m-%Y')}")
                        st.write(f"*Total Protesters:* {int(peak['Crowd_size']):,}")
                        st.write("---")
            else:
                st.write("No data available for the selected protest types.")