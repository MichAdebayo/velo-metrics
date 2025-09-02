import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import check_authentication
from utils.api import get_all_users, get_stats

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "admin":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Admin Dashboard")

# Get all users
users_df = get_all_users(st.session_state.token)

# Get performance stats
stats = get_stats()

# Display summary metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Athletes", 0 if users_df.empty else len(users_df[users_df['is_staff'] == False]))
with col2:
    st.metric("Total Coaches/Admins", 0 if users_df.empty else len(users_df[users_df['is_staff'] == True]))
with col3:
    st.metric("Total Users", 0 if users_df.empty else len(users_df))

# Display top performers
st.subheader("Top Performers")

if stats:
    tab1, tab2, tab3 = st.tabs(["Strongest Athletes", "Highest VO2 Max", "Best Power-to-Weight Ratio"])

    with tab1:
        # Get details of strongest athlete
        strongest_id = stats["strongest_athlete"][0]
        st.write(f"**Strongest Athlete ID:** {strongest_id}")

        # Display button to view details
        if st.button("View Strongest Athlete Details", key="view_strongest"):
            # Call API to get athlete details and performance
            import requests
            headers = {"Authorization": f"Bearer {st.session_state.token}"}

            user_response = requests.get(f"http://your-fastapi-url/api/users/{strongest_id}", headers=headers)
            athlete_response = requests.get(f"http://your-fastapi-url/api/athletes/get_athlete_details/{strongest_id}", headers=headers)
            performance_response = requests.get(f"http://your-fastapi-url/api/performance/user/{strongest_id}", headers=headers)

            if user_response.status_code == 200 and athlete_response.status_code == 200 and performance_response.status_code == 200:
                user_data = user_response.json()
                athlete_data = athlete_response.json()["athlete"]
                performance_data = performance_response.json()

                st.write(f"**Name:** {user_data['first_name']} {user_data['last_name']}")
                st.write(f"**Age:** {athlete_data['age']}")
                st.write(f"**Gender:** {athlete_data['gender']}")

                # Display max power
                max_power = (
                    max(p['power_max'] for p in performance_data)
                    if performance_data
                    else 0
                )
                st.metric("Maximum Power", f"{max_power} W")

                # Plot power over time
                if performance_data:
                    df = pd.DataFrame(performance_data)
                    fig = px.line(df, x="date", y="power_max", title="Power Over Time")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to load athlete details")

    with tab2:
        # Get details of highest VO2 Max athlete
        vo2max_id = stats["highest_vo2max"][0]
        st.write(f"**Highest VO2 Max Athlete ID:** {vo2max_id}")

        # Display button to view details
        if st.button("View Highest VO2 Max Athlete Details", key="view_vo2max"):
            # Similar API calls as above
            import requests
            headers = {"Authorization": f"Bearer {st.session_state.token}"}

            user_response = requests.get(f"http://your-fastapi-url/api/users/{vo2max_id}", headers=headers)
            athlete_response = requests.get(f"http://your-fastapi-url/api/athletes/get_athlete_details/{vo2max_id}", headers=headers)
            performance_response = requests.get(f"http://your-fastapi-url/api/performance/user/{vo2max_id}", headers=headers)

            if user_response.status_code == 200 and athlete_response.status_code == 200 and performance_response.status_code == 200:
                user_data = user_response.json()
                athlete_data = athlete_response.json()["athlete"]
                performance_data = performance_response.json()

                st.write(f"**Name:** {user_data['first_name']} {user_data['last_name']}")
                st.write(f"**Age:** {athlete_data['age']}")
                st.write(f"**Gender:** {athlete_data['gender']}")

                # Display max VO2
                max_vo2 = (
                    max(p['vo2_max'] for p in performance_data)
                    if performance_data
                    else 0
                )
                st.metric("Maximum VO2 Max", f"{max_vo2} ml/kg/min")

                # Plot VO2 max over time
                if performance_data:
                    df = pd.DataFrame(performance_data)
                    fig = px.line(df, x="date", y="vo2_max", title="VO2 Max Over Time")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to load athlete details")

    with tab3:
        # Get details of best power-to-weight ratio athlete
        pwr_id = stats["best_power_weight_ratio"][0]
        pwr_ratio = stats["best_power_weight_ratio"][1]
        st.write(f"**Best Power-to-Weight Ratio Athlete ID:** {pwr_id}")
        st.write(f"**Ratio:** {pwr_ratio:.2f} W/kg")

        # Display button to view details
        if st.button("View Best Power-to-Weight Athlete Details", key="view_pwr"):
            # Similar API calls as above
            # Display relevant metrics and charts
            pass

# Display overall performance trends
st.subheader("Overall Performance Trends")

# This would require an additional API endpoint to get aggregated data
# For now, we'll just show a placeholder
st.info("This section would show aggregated performance trends across all athletes.")