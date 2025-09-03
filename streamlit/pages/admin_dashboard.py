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

# Quick debug helper visible to admins to diagnose API auth / endpoint issues
with st.expander("Debug: API checks (show/hide)"):
    token_present = bool(st.session_state.get("token"))
    st.write("Token present:", token_present)
    if token_present:
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            resp1 = requests.get(f"{API_URL}/users/athletes-with-performance", headers=headers)
            st.write("/users/athletes-with-performance ->", resp1.status_code, "| rows:", len(resp1.json()) if resp1.status_code == 200 else "-")
            resp2 = requests.get(f"{API_URL}/performance/all_performances", headers=headers)
            st.write("/performance/all_performances ->", resp2.status_code, "| rows:", len(resp2.json()) if resp2.status_code == 200 else "-")
        except Exception as e:
            st.write("API check error:", str(e))
    else:
        st.info("Not logged in or token missing — log in as admin to run API checks.")

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
        # Setup session state for toggles
        if "show_strongest" not in st.session_state:
            st.session_state.show_strongest = False
        if "show_vo2max" not in st.session_state:
            st.session_state.show_vo2max = False
        if "show_pwr" not in st.session_state:
            st.session_state.show_pwr = False

        # Strongest Athlete
        strongest = stats["strongest_athlete"]
        if strongest:
            st.write(f"**Strongest Athlete:** {strongest['first_name']} {strongest['last_name']} (@{strongest['username']})")
            strongest_id = strongest['id']
            if not st.session_state.show_strongest:
                if st.button("View Strongest Athlete Details", key="view_strongest"):
                    st.session_state.show_strongest = True
            else:
                if st.button("Minimize Strongest Athlete Details", key="min_strongest"):
                    st.session_state.show_strongest = False
                else:
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
            if not st.session_state.show_vo2max:
                if st.button("View Highest VO2 Max Athlete Details", key="view_vo2max"):
                    st.session_state.show_vo2max = True
            else:
                if st.button("Minimize Highest VO2 Max Athlete Details", key="min_vo2max"):
                    st.session_state.show_vo2max = False
                else:
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
            if not st.session_state.show_pwr:
                if st.button("View Best Power-to-Weight Ratio Athlete Details", key="view_pwr"):
                    st.session_state.show_pwr = True
            else:
                if st.button("Minimize Best Power-to-Weight Ratio Athlete Details", key="min_pwr"):
                    st.session_state.show_pwr = False
                else:
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
                        st.error(f"Failed to load athlete details. Status code: {athlete_response.status_code}")
        else:
            st.write("No best power-to-weight ratio athlete found.")

    # Add spacing between sections
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    st.subheader("Overall Performance Trends")
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/performance/all_performances", headers=headers)
        if response.status_code == 200:
            all_perf = pd.DataFrame(response.json())
            if not all_perf.empty:
                # Fetch weights per athlete to avoid relying on the bulk endpoint (which may return 422)
                unique_ids = all_perf['user_id'].unique().tolist()
                athlete_weights = {}
                for uid in unique_ids:
                    athlete_resp = requests.get(f"{API_URL}/athletes/get_athlete_details/{uid}", headers=headers)
                    if athlete_resp.status_code == 200:
                        try:
                            athlete_weights[uid] = athlete_resp.json().get('athlete', {}).get('weight')
                        except Exception:
                            athlete_weights[uid] = None
                    else:
                        athlete_weights[uid] = None

                all_perf["weight"] = all_perf["user_id"].map(athlete_weights)
                all_perf["power_weight_ratio"] = all_perf.apply(lambda r: r["power_max"] / r["weight"] if r["weight"] not in [None, 0, np.nan] and r["weight"] > 0 else np.nan, axis=1)
                agg = all_perf.groupby("test_type").agg({
                    "power_max": ["mean"],
                    "vo2_max": ["mean"],
                    "hr_max": ["mean"],
                    "rf_max": ["mean"],
                    "cadence_max": ["mean"],
                    "power_weight_ratio": ["mean"]
                }).reset_index()
                agg.columns = ["test_type"] + [f"{metric}_mean" for metric in ["power_max", "vo2_max", "hr_max", "rf_max", "cadence_max", "power_weight_ratio"]]
                st.write("### Aggregated Performance by Test Type")
                st.dataframe(agg)
                fig = px.bar(agg, x="test_type", y="power_max_mean", title="Average Power by Test Type")
                st.plotly_chart(fig, use_container_width=True)
                fig2 = px.bar(agg, x="test_type", y="vo2_max_mean", title="Average VO2 Max by Test Type")
                st.plotly_chart(fig2, use_container_width=True)
                fig3 = px.bar(agg, x="test_type", y="power_weight_ratio_mean", title="Average Power-to-Weight Ratio by Test Type")
                st.plotly_chart(fig3, use_container_width=True)
                if agg["power_weight_ratio_mean"].isnull().all():
                    st.warning("No valid weights found for athletes. Power-to-weight ratio plot is empty.")
            else:
                st.info("No performance data available for aggregation.")
        else:
            st.error("Failed to fetch overall performance or athlete data.")
    except Exception as e:
        st.error(f"Error loading overall performance trends: {str(e)}")

with tab2:
    st.subheader("Compare Athletes")
    # Build athlete selection from users list (which is trusted) and fetch weights per-athlete when needed
    users_df_local = get_all_users(st.session_state.token)
    if not users_df_local.empty:
        user_names = users_df_local['user_name'].tolist()
        name_to_id = dict(zip(users_df_local['user_name'], users_df_local['id']))
    else:
        user_names = []
        name_to_id = {}

    selected_names = st.multiselect("Select Athletes to Compare (by name)", options=user_names)
    selected_ids = [name_to_id[name] for name in selected_names if name in name_to_id]

    if selected_ids:
        compare_data = []
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        for aid in selected_ids:
            # fetch performances directly to avoid possible utility scoping issues
            perf_resp = requests.get(f"{API_URL}/performance/user/{aid}", headers=headers)
            if perf_resp.status_code == 200:
                perfs = perf_resp.json()
            else:
                perfs = []

            if perfs:
                user_row = users_df_local[users_df_local['id'] == aid].iloc[0]
                athlete_name = f"{user_row['first_name']} {user_row['last_name']}"
                # fetch weight from athlete endpoint
                athlete_resp = requests.get(f"{API_URL}/athletes/get_athlete_details/{aid}", headers=headers)
                weight = None
                if athlete_resp.status_code == 200:
                    weight = athlete_resp.json().get('athlete', {}).get('weight')
                for perf in perfs:
                    compare_data.append({
                        "athlete_name": athlete_name,
                        "test_type": perf.get("test_type"),
                        "power_max": perf.get("power_max"),
                        "vo2_max": perf.get("vo2_max"),
                        "power_weight_ratio": (perf.get("power_max") / weight) if weight not in [None, 0, np.nan] and weight > 0 else np.nan
                    })
        compare_df = pd.DataFrame(compare_data)
        if not compare_df.empty:
            st.write("### Grouped Bar Charts for Selected Athletes")
            fig = px.bar(compare_df, x="test_type", y="power_max", color="athlete_name", barmode="group", title="Average Power Comparison")
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.bar(compare_df, x="test_type", y="vo2_max", color="athlete_name", barmode="group", title="Average VO2 Max Comparison")
            st.plotly_chart(fig2, use_container_width=True)
            fig3 = px.bar(compare_df, x="test_type", y="power_weight_ratio", color="athlete_name", barmode="group", title="Average Power-to-Weight Ratio Comparison")
            st.plotly_chart(fig3, use_container_width=True)
            if compare_df["power_weight_ratio"].isnull().all():
                st.warning("No valid weights found for selected athletes. Power-to-weight ratio plot is empty.")
        else:
            st.info("No performance data available for selected athletes.")
    else:
        st.info("Select athletes to compare.")