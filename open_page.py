import streamlit as st

def app():
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

    st.title("Protests in the USA over Swords of Iron War")

    st.subheader("Overview")
    st.markdown(
        """
        <div class="info-text">
        This page provides a detailed analysis of protests in the USA during the first year of Swords of Iron War.\n
        The data includes 460 <span class="highlight">Pro-Israeli</span> protests, 4170 <span class="highlight">Pro-Palestinian</span>
        protests and 660 <span class="highlight">Two-sided</span> protests, spannig from a month prior to the beginning
        of the war, till November 8th, 2024.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Motivation")
    st.markdown(
        """
        <div class="info-text">
        Our motivation is to understand the dynamics of protests in the USA during this period. Since the israeli media
        mainly focus on protests against Israel, we decided to check the reality of the protests in the USA along with 
        more relevant questions we believed that the data could help us answer them.\n
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Data Sources")
    st.markdown(
        """
        <div class="info-text">
        Our analysis is based on the <span class="highlight">ACLED</span> dataset, which provides reportings of protests
        over conflicts around the world.
        In addition to the ACLED dataset, we have also used the IDF's <span class="highlight">Swords of Iron Journal</span> 
        to construct a second dataset of significant events during the war, which we will use to analyze the frequency of
        protests around these events.\n
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Key Questions")
    st.markdown(
        """
        <div class="info-text">
        Our analysis covers the following key questions:
        <ul>
            <li>Where are the protests happening? (State-by-state analysis)</li>
            <li>What types of groups are involved? (Political groups, LGBTQ+, students, etc.)</li>
            <li>Are protests more frequent around significant events?</li>
            <li>What is the ratio of violent protests to peaceful ones?</li>
        </ul>
        Please use the sidebar to navigate between the different sections of our analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Hope you enjoy our analysis! :)")

