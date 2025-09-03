import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import check_authentication
from utils.api import get_all_users, get_performance_history, add_performance, API_URL, get_user_info_by_username
import requests

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "admin":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Performance Management")

# Option to select how to find athletes
selection_method = st.radio(
    "How would you like to select an athlete?",
    ["Browse all athletes", "Search by username"],
    key="selection_method"
)

if selection_method == "Browse all athletes":
    # Get all users (athletes are non-staff users)
    users_df = get_all_users(st.session_state.token)

    # Filter to get only athletes (non-staff users)
    if not users_df.empty:
        athletes_df = users_df[users_df['is_staff'] == 0]
    else:
        athletes_df = pd.DataFrame()

    if not athletes_df.empty:
        selected_username = None
        # Create tabs for different actions
        tab1, tab2, tab3 = st.tabs(["View Performance", "Add Performance", "Edit/Delete Performance"])

        with tab1:
            st.subheader("View Athlete Performance")

            if selected_username := st.selectbox(
                "Select Athlete",
                athletes_df['user_name'].tolist(),
                key="view_athlete",
            ):
                # Get selected athlete info
                selected_athlete = athletes_df[athletes_df['user_name'] == selected_username].iloc[0]

                st.write(f"**Name:** {selected_athlete['first_name']} {selected_athlete['last_name']}")
                st.write(f"**Username:** {selected_athlete['user_name']}")

                # Get performance history
                performance_df = get_performance_history(selected_athlete['id'], st.session_state.token)

                if not performance_df.empty:
                    # Display performance data
                    st.dataframe(performance_df)

                    # Create visualizations
                    st.subheader("Performance Visualizations")

                    # Select metric to visualize
                    metric = st.selectbox(
                        "Select Metric",
                        ["power_max", "hr_max", "vo2_max", "rf_max", "cadence_max"],
                        key="view_metric"
                    )

                    # Create line chart
                    fig = px.line(
                        performance_df,
                        x="date" if "date" in performance_df.columns else performance_df.index,
                        y=metric,
                        title=f"{metric.replace('_', ' ').title()} Over Time"
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No performance data available for this athlete.")

        with tab2:
            st.subheader("Add Performance Record")

            if selected_username := st.selectbox(
                "Select Athlete", athletes_df['user_name'].tolist(), key="add_athlete"
            ):
                # Get selected athlete info
                selected_athlete = athletes_df[athletes_df['user_name'] == selected_username].iloc[0]

                st.write(f"**Name:** {selected_athlete['first_name']} {selected_athlete['last_name']}")
                st.write(f"**Username:** {selected_athlete['user_name']}")

                # Form to add performance
                with st.form("add_performance_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        power_max = st.number_input("Power Max (W)", min_value=0, max_value=3000)
                        hr_max = st.number_input("Heart Rate Max (bpm)", min_value=0, max_value=250)
                        vo2_max = st.number_input("VO2 Max (ml/kg/min)", min_value=0.0, max_value=100.0)

                    with col2:
                        rf_max = st.number_input("Respiratory Frequency Max (breaths/min)", min_value=0, max_value=100)
                        cadence_max = st.number_input("Cadence Max (rpm)", min_value=0, max_value=300)

                    if submit := st.form_submit_button("Add Performance"):
                        # Call API to add performance
                        performance_data = {
                            "user_id": selected_athlete['id'],
                            "power_max": power_max,
                            "hr_max": hr_max,
                            "vo2_max": vo2_max,
                            "rf_max": rf_max,
                            "cadence_max": cadence_max
                        }

                        # We need to use the current user's token but add performance for the selected athlete
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}

                        # This is a workaround since the API expects the current user's ID
                        # We might need to modify the API to accept a user_id parameter
                        response = requests.post(
                            f"{API_URL}/performance/add_performance",
                            json=[performance_data],
                            headers=headers,
                        )

                        if response.status_code == 200:
                            st.success("Performance added successfully!")
                        else:
                            st.error(f"Failed to add performance: {response.json().get('detail', 'Unknown error')}")

        with tab3:
            st.subheader("Edit/Delete Performance")

            if selected_username := st.selectbox(
                "Select Athlete",
                athletes_df['user_name'].tolist(),
                key="edit_athlete",
            ):
                # Get selected athlete info
                selected_athlete = athletes_df[athletes_df['user_name'] == selected_username].iloc[0]

                st.write(f"**Name:** {selected_athlete['first_name']} {selected_athlete['last_name']}")
                st.write(f"**Username:** {selected_athlete['user_name']}")

                # Get performance history
                performance_df = get_performance_history(selected_athlete['id'], st.session_state.token)

                if not performance_df.empty:
                    # Display performance data with selection
                    selected_performance = st.selectbox(
                        "Select Performance Record",
                        performance_df.index,
                        format_func=lambda x: f"ID: {performance_df.loc[x, 'performance_id']} - Date: {performance_df.loc[x, 'date']}" if 'date' in performance_df.columns else f"ID: {performance_df.loc[x, 'performance_id']}"
                    )

                    if selected_performance is not None:
                        selected_record = performance_df.loc[selected_performance]
                        performance_id = selected_record['performance_id']

                        # Create tabs for edit and delete
                        edit_tab, delete_tab = st.tabs(["Edit", "Delete"])

                        with edit_tab:
                            # Form to edit performance
                            with st.form("edit_performance_form"):
                                col1, col2 = st.columns(2)

                                with col1:
                                    power_max = st.number_input("Power Max (W)", min_value=0, max_value=max(3000, int(selected_record['power_max'])), value=int(selected_record['power_max']))
                                    hr_max = st.number_input("Heart Rate Max (bpm)", min_value=0, max_value=max(250, int(selected_record['hr_max'])), value=int(selected_record['hr_max']))
                                    vo2_max = st.number_input("VO2 Max (ml/kg/min)", min_value=0.0, max_value=max(100.0, float(selected_record['vo2_max'])), value=float(selected_record['vo2_max']))

                                with col2:
                                    rf_max = st.number_input("Respiratory Frequency Max (breaths/min)", min_value=0, max_value=max(100, int(selected_record['rf_max'])), value=int(selected_record['rf_max']))
                                    cadence_max = st.number_input("Cadence Max (rpm)", min_value=0, max_value=max(300, int(selected_record['cadence_max'])), value=int(selected_record['cadence_max']))

                                if submit := st.form_submit_button(
                                    "Update Performance"
                                ):
                                    # Call API to update performance
                                    performance_data = {
                                        "power_max": power_max,
                                        "hr_max": hr_max,
                                        "vo2_max": vo2_max,
                                        "rf_max": rf_max,
                                        "cadence_max": cadence_max
                                    }

                                    import requests
                                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                    response = requests.patch(
                                        f"{API_URL}/performance/{performance_id}",
                                        json=performance_data,
                                        headers=headers
                                    )

                                    if response.status_code == 200:
                                        st.success("Performance updated successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to update performance: {response.json().get('detail', 'Unknown error')}")

                        with delete_tab:
                            st.warning("This action cannot be undone.")
                            if st.button("Delete Performance Record") and st.checkbox("I understand this action cannot be undone"):
                                import requests
                                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                response = requests.delete(
                                    f"{API_URL}/performance/{performance_id}",
                                    headers=headers
                                )

                                if response.status_code == 200:
                                    st.success("Performance deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete performance: {response.json().get('detail', 'Unknown error')}")
                else:
                    st.info("No performance data available for this athlete.")
    else:
        st.info("No athletes found. Register users as athletes first.")

else:  # Search by username
    st.subheader("Search Athlete by Username")
    
    username_input = st.text_input("Enter athlete username:")
    
    if username_input:
        # Use get_user_info_by_username to get athlete info
        athlete_info = get_user_info_by_username(username_input, st.session_state.token)
        
        if athlete_info:
            # Check if the user is an athlete (not staff)
            if athlete_info.get('is_staff', 1) == 0:  # 0 means not staff (athlete)
                selected_athlete = athlete_info
                selected_athlete_id = selected_athlete['id']
                
                st.write(f"**Name:** {selected_athlete['first_name']} {selected_athlete['last_name']}")
                st.write(f"**Username:** {selected_athlete['user_name']}")
                
                # Create tabs for different actions
                tab1, tab2, tab3 = st.tabs(["View Performance", "Add Performance", "Edit/Delete Performance"])

                with tab1:
                    st.subheader("View Athlete Performance")

                    # Get performance history
                    performance_df = get_performance_history(selected_athlete_id, st.session_state.token)

                    if not performance_df.empty:
                        # Display performance data
                        st.dataframe(performance_df)

                        # Create visualizations
                        st.subheader("Performance Visualizations")

                        # Select metric to visualize
                        metric = st.selectbox(
                            "Select Metric",
                            ["power_max", "hr_max", "vo2_max", "rf_max", "cadence_max"],
                            key="view_metric_username"
                        )

                        # Create line chart
                        fig = px.line(
                            performance_df,
                            x="date" if "date" in performance_df.columns else performance_df.index,
                            y=metric,
                            title=f"{metric.replace('_', ' ').title()} Over Time"
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No performance data available for this athlete.")

                with tab2:
                    st.subheader("Add Performance Record")

                    # Form to add performance
                    with st.form("add_performance_form_username"):
                        col1, col2 = st.columns(2)

                        with col1:
                            power_max = st.number_input("Power Max (W)", min_value=0, max_value=3000, key="power_username")
                            hr_max = st.number_input("Heart Rate Max (bpm)", min_value=0, max_value=250, key="hr_username")
                            vo2_max = st.number_input("VO2 Max (ml/kg/min)", min_value=0.0, max_value=100.0, key="vo2_username")

                        with col2:
                            rf_max = st.number_input("Respiratory Frequency Max (breaths/min)", min_value=0, max_value=100, key="rf_username")
                            cadence_max = st.number_input("Cadence Max (rpm)", min_value=0, max_value=300, key="cadence_username")

                        if submit := st.form_submit_button("Add Performance"):
                            # Call API to add performance
                            performance_data = {
                                "user_id": selected_athlete_id,
                                "power_max": power_max,
                                "hr_max": hr_max,
                                "vo2_max": vo2_max,
                                "rf_max": rf_max,
                                "cadence_max": cadence_max
                            }

                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            response = requests.post(
                                f"{API_URL}/performance/add_performance",
                                json=[performance_data],
                                headers=headers,
                            )

                            if response.status_code == 200:
                                st.success("Performance added successfully!")
                            else:
                                st.error(f"Failed to add performance: {response.json().get('detail', 'Unknown error')}")

                with tab3:
                    st.subheader("Edit/Delete Performance")

                    # Get performance history
                    performance_df = get_performance_history(selected_athlete_id, st.session_state.token)

                    if not performance_df.empty:
                        # Display performance data with selection
                        selected_performance = st.selectbox(
                            "Select Performance Record",
                            performance_df.index,
                            format_func=lambda x: f"ID: {performance_df.loc[x, 'performance_id']} - Date: {performance_df.loc[x, 'date']}" if 'date' in performance_df.columns else f"ID: {performance_df.loc[x, 'performance_id']}",
                            key="edit_performance_username"
                        )

                        if selected_performance is not None:
                            selected_record = performance_df.loc[selected_performance]
                            performance_id = selected_record['performance_id']

                            # Create tabs for edit and delete
                            edit_tab, delete_tab = st.tabs(["Edit", "Delete"])

                            with edit_tab:
                                # Form to edit performance
                                with st.form("edit_performance_form_username"):
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        power_max = st.number_input("Power Max (W)", min_value=0, max_value=max(3000, int(selected_record['power_max'])), value=int(selected_record['power_max']), key="edit_power_username")
                                        hr_max = st.number_input("Heart Rate Max (bpm)", min_value=0, max_value=max(250, int(selected_record['hr_max'])), value=int(selected_record['hr_max']), key="edit_hr_username")
                                        vo2_max = st.number_input("VO2 Max (ml/kg/min)", min_value=0.0, max_value=max(100.0, float(selected_record['vo2_max'])), value=float(selected_record['vo2_max']), key="edit_vo2_username")

                                    with col2:
                                        rf_max = st.number_input("Respiratory Frequency Max (breaths/min)", min_value=0, max_value=max(100, int(selected_record['rf_max'])), value=int(selected_record['rf_max']), key="edit_rf_username")
                                        cadence_max = st.number_input("Cadence Max (rpm)", min_value=0, max_value=max(300, int(selected_record['cadence_max'])), value=int(selected_record['cadence_max']), key="edit_cadence_username")

                                    if submit := st.form_submit_button("Update Performance"):
                                        # Call API to update performance
                                        performance_data = {
                                            "power_max": power_max,
                                            "hr_max": hr_max,
                                            "vo2_max": vo2_max,
                                            "rf_max": rf_max,
                                            "cadence_max": cadence_max
                                        }

                                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                        response = requests.patch(
                                            f"{API_URL}/performance/{performance_id}",
                                            json=performance_data,
                                            headers=headers
                                        )

                                        if response.status_code == 200:
                                            st.success("Performance updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error(f"Failed to update performance: {response.json().get('detail', 'Unknown error')}")

                            with delete_tab:
                                st.warning("This action cannot be undone.")
                                if st.button("Delete Performance Record", key="delete_btn_username") and st.checkbox("I understand this action cannot be undone", key="delete_checkbox_username"):
                                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                    response = requests.delete(
                                        f"{API_URL}/performance/{performance_id}",
                                        headers=headers
                                    )

                                    if response.status_code == 200:
                                        st.success("Performance deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to delete performance: {response.json().get('detail', 'Unknown error')}")
                    else:
                        st.info("No performance data available for this athlete.")
            else:
                st.error("The specified user is not an athlete (staff member).")
        else:
            st.error("Athlete not found. Please check the username and try again.")