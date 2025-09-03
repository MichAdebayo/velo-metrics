import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import check_authentication
from utils.api import get_all_users, get_stats, API_URL, get_performances, get_performances_by_username
import requests
import numpy as np

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "admin":
    st.error("You don't have permission to access this page")
    st.stop()


st.title("Admin Dashboard")
users_df = get_all_users(st.session_state.token)
stats = get_stats()

tab1, tab2 = st.tabs(["Overview & Trends", "Compare Athletes"])

with tab1:
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Athletes", 0 if users_df.empty else len(users_df[users_df['is_staff'] == False]))
    with col2:
        st.metric("Total Coaches/Admins", 0 if users_df.empty else len(users_df[users_df['is_staff'] == True]))
    with col3:
        st.metric("Total Users", 0 if users_df.empty else len(users_df))

    st.subheader("Top Performers")
    if stats:
        # Strongest Athlete
        strongest = stats["strongest_athlete"]
        if strongest:
            st.write(f"**Strongest Athlete:** {strongest['first_name']} {strongest['last_name']} (@{strongest['username']})")
            strongest_id = strongest['id']
            if st.button("View Strongest Athlete Details", key="view_strongest"):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                user_response = requests.get(f"{API_URL}/users/{strongest_id}", headers=headers)
                athlete_response = requests.get(f"{API_URL}/athletes/get_athlete_details/{strongest_id}", headers=headers)
                performance_response = requests.get(f"{API_URL}/performance/user/{strongest_id}", headers=headers)
                if user_response.status_code == 200 and athlete_response.status_code == 200 and performance_response.status_code == 200:
                    user_data = user_response.json()
                    athlete_data = athlete_response.json()["athlete"]
                    performance_data = performance_response.json()
                    st.write(f"**Name:** {user_data['first_name']} {user_data['last_name']}")
                    st.write(f"**Age:** {athlete_data['age']}")
                    st.write(f"**Gender:** {athlete_data['gender']}")
                    max_power = max(p['power_max'] for p in performance_data) if performance_data else 0
                    st.metric("Maximum Power", f"{max_power} W")
                    if performance_data:
                        df = pd.DataFrame(performance_data)
                        fig = px.line(df, x="test_type", y="power_max", title="Power by Test Type")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Failed to load athlete details. Status codes: user={user_response.status_code}, athlete={athlete_response.status_code}, performance={performance_response.status_code}")
        else:
            st.write("No strongest athlete found.")

        # Highest VO2 Max Athlete
        vo2max = stats["highest_vo2max"]
        if vo2max:
            st.write(f"**Highest VO2 Max Athlete:** {vo2max['first_name']} {vo2max['last_name']} (@{vo2max['username']})")
            vo2max_id = vo2max['id']
            if st.button("View Highest VO2 Max Athlete Details", key="view_vo2max"):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                user_response = requests.get(f"{API_URL}/users/{vo2max_id}", headers=headers)
                athlete_response = requests.get(f"{API_URL}/athletes/get_athlete_details/{vo2max_id}", headers=headers)
                performance_response = requests.get(f"{API_URL}/performance/user/{vo2max_id}", headers=headers)
                if user_response.status_code == 200 and athlete_response.status_code == 200 and performance_response.status_code == 200:
                    user_data = user_response.json()
                    athlete_data = athlete_response.json()["athlete"]
                    performance_data = performance_response.json()
                    st.write(f"**Name:** {user_data['first_name']} {user_data['last_name']}")
                    st.write(f"**Age:** {athlete_data['age']}")
                    st.write(f"**Gender:** {athlete_data['gender']}")
                    max_vo2 = max(p['vo2_max'] for p in performance_data) if performance_data else 0
                    st.metric("Maximum VO2 Max", f"{max_vo2} ml/kg/min")
                    if performance_data:
                        df = pd.DataFrame(performance_data)
                        fig = px.line(df, x="test_type", y="vo2_max", title="VO2 Max by Test Type")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Failed to load athlete details. Status codes: user={user_response.status_code}, athlete={athlete_response.status_code}, performance={performance_response.status_code}")
        else:
            st.write("No highest VO2 max athlete found.")

        # Best Power-to-Weight Ratio Athlete
        pwr = stats["best_power_weight_ratio"]
        if pwr:
            st.write(f"**Best Power-to-Weight Ratio Athlete:** {pwr['first_name']} {pwr['last_name']} (@{pwr['username']})")
            pwr_id = pwr['id']
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            athlete_response = requests.get(f"{API_URL}/athletes/get_athlete_details/{pwr_id}", headers=headers)
            if athlete_response.status_code == 200:
                athlete_data = athlete_response.json()["athlete"]
                weight = athlete_data["weight"]
                performance_response = requests.get(f"{API_URL}/performance/user/{pwr_id}", headers=headers)
                if performance_response.status_code == 200:
                    performance_data = performance_response.json()
                    df = pd.DataFrame(performance_data)
                    if not df.empty:
                        df["ratio"] = df["power_max"] / weight
                        st.write("### Power-to-Weight Ratio per Test Type")
                        st.dataframe(df[["test_type", "ratio"]])
                        fig = px.bar(df, x="test_type", y="ratio", title="Power-to-Weight Ratio by Test Type")
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No best power-to-weight ratio athlete found.")

    # Overall Performance Trends
    st.subheader("Overall Performance Trends")
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/performance/all_performances", headers=headers)
        if response.status_code == 200:
            all_perf = pd.DataFrame(response.json())
            if not all_perf.empty:
                # Aggregate by test_type
                # Add power-to-weight ratio aggregation
                # For each row, get athlete weight
                # Fetch all athletes
                athlete_weights = {}
                athlete_response = requests.get(f"{API_URL}/users/athletes-with-performance", headers=headers)
                if athlete_response.status_code == 200:
                    athletes_df = pd.DataFrame(athlete_response.json())
                    for _, row in athletes_df.iterrows():
                        athlete_weights[row["id"]] = row["weight"] if "weight" in row else None
                all_perf["weight"] = all_perf["user_id"].map(athlete_weights)
                all_perf["power_weight_ratio"] = all_perf["power_max"] / all_perf["weight"]
                agg = all_perf.groupby("test_type").agg({
                    "power_max": ["mean", "max"],
                    "vo2_max": ["mean", "max"],
                    "hr_max": ["mean", "max"],
                    "rf_max": ["mean", "max"],
                    "cadence_max": ["mean", "max"],
                    "power_weight_ratio": ["mean", "max"]
                }).reset_index()
                agg.columns = ["test_type"] + [f"{metric}_{stat}" for metric, stat in agg.columns[1:]]
                st.write("### Aggregated Performance by Test Type")
                st.dataframe(agg)
                fig = px.bar(agg, x="test_type", y="power_max_mean", title="Average Power by Test Type")
                st.plotly_chart(fig, use_container_width=True)
                fig2 = px.bar(agg, x="test_type", y="vo2_max_max", title="Max VO2 Max by Test Type")
                st.plotly_chart(fig2, use_container_width=True)
                fig3 = px.bar(agg, x="test_type", y="power_weight_ratio_mean", title="Average Power-to-Weight Ratio by Test Type")
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No performance data available for aggregation.")
        else:
            st.error("Failed to fetch overall performance data.")
    except Exception as e:
        st.error(f"Error loading overall performance trends: {str(e)}")

with tab2:
    st.subheader("Compare Athletes")
    users_df = get_all_users(st.session_state.token)
    if not users_df.empty:
        user_names = users_df['user_name'].tolist()
        user_ids = users_df['id'].tolist()
        name_to_id = dict(zip(users_df['user_name'], users_df['id']))
    else:
        user_names = []
        user_ids = []
        name_to_id = {}

    selected_names = st.multiselect("Select Athletes to Compare (by name)", options=user_names)
    selected_ids = [name_to_id[name] for name in selected_names if name in name_to_id]

    if selected_ids:
        compare_data = []
        for aid in selected_ids:
            perfs = get_performances(aid)
            if perfs:
                athlete_row = users_df[users_df['id'] == aid].iloc[0]
                athlete_name = f"{athlete_row['first_name']} {athlete_row['last_name']}"
                # Fetch athlete weight
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                athlete_response = requests.get(f"{API_URL}/athletes/get_athlete_details/{aid}", headers=headers)
                if athlete_response.status_code == 200:
                    athlete_data = athlete_response.json()["athlete"]
                    weight = athlete_data["weight"]
                else:
                    weight = np.nan
                for perf in perfs:
                    compare_data.append({
                        "athlete_name": athlete_name,
                        "test_type": perf["test_type"],
                        "power_max": perf["power_max"],
                        "vo2_max": perf["vo2_max"],
                        "power_weight_ratio": perf["power_max"] / weight if weight else np.nan
                    })
        compare_df = pd.DataFrame(compare_data)
        if not compare_df.empty:
            st.write("### Grouped Bar Charts for Selected Athletes")
            fig = px.bar(compare_df, x="test_type", y="power_max", color="athlete_name", barmode="group", title="Power Max Comparison")
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.bar(compare_df, x="test_type", y="vo2_max", color="athlete_name", barmode="group", title="VO2 Max Comparison")
            st.plotly_chart(fig2, use_container_width=True)
            fig3 = px.bar(compare_df, x="test_type", y="power_weight_ratio", color="athlete_name", barmode="group", title="Power-to-Weight Ratio Comparison")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No performance data available for selected athletes.")
    else:
        st.info("Select athletes to compare.")