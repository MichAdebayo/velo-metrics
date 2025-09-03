import streamlit as st
import pandas as pd
from utils.auth import check_authentication
from utils.api import get_all_users, register_user, add_athlete, API_URL
import requests

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "admin":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("User Management")

# Create tabs for different actions
tab1, tab2, tab3 = st.tabs(["View Users", "Register User", "Manage Athletes"])

with tab1:
    st.subheader("All Users")
    
    # Get all users
    users_df = get_all_users(st.session_state.token)
    
    if not users_df.empty:
        # Add filters
        st.sidebar.header("Filter Users")
        
        # Filter by role
        role_filter = st.sidebar.multiselect(
            "Role",
            ["Athlete", "Coach/Admin"],
            default=["Athlete", "Coach/Admin"]
        )
        
        filtered_df = users_df.copy()
        if role_filter:
            if "Athlete" in role_filter and "Coach/Admin" not in role_filter:
                filtered_df = filtered_df[filtered_df['is_staff'] == False]
            elif "Coach/Admin" in role_filter and "Athlete" not in role_filter:
                filtered_df = filtered_df[filtered_df['is_staff'] == True]
        
        # Display users table
        st.dataframe(filtered_df)
        
        # User details section
        st.subheader("User Details")
        selected_user_id = st.selectbox("Select User", filtered_df['id'].tolist())
        
        if selected_user_id:
            # Get selected user
            selected_user = filtered_df[filtered_df['id'] == selected_user_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {selected_user['first_name']} {selected_user['last_name']}")
                st.write(f"**Username:** {selected_user['user_name']}")
            with col2:
                st.write(f"**Email:** {selected_user['email']}")
                st.write(f"**Role:** {'Coach/Admin' if selected_user['is_staff'] else 'Athlete'}")
            
            # Actions for selected user
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if "show_edit_form" not in st.session_state:
                    st.session_state.show_edit_form = False
                if st.button("Edit User"):
                    st.session_state.show_edit_form = True
                if st.session_state.show_edit_form:
                    with st.form("edit_user_form"):
                        first_name = st.text_input("First Name", value=selected_user['first_name'])
                        last_name = st.text_input("Last Name", value=selected_user['last_name'])
                        user_name = st.text_input("Username", value=selected_user['user_name'])
                        email = st.text_input("Email", value=selected_user['email'])
                        password = st.text_input("Password (leave blank to keep unchanged)", value="", type="password")
                        is_staff = st.checkbox("Is Coach/Admin", value=selected_user['is_staff'])

                        submit = st.form_submit_button("Update User")

                        if submit:
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            data = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "user_name": user_name,
                                "email": email,
                                "password": password or "dummy_password",
                                "is_staff": int(is_staff)
                            }
                            response = requests.patch(
                                f"{API_URL}/users/{selected_user_id}",
                                json=data,
                                headers=headers
                            )
                            if response.status_code == 200:
                                st.success("User updated successfully!")
                                st.session_state.show_edit_form = False
                                st.rerun()
                            else:
                                try:
                                    err = response.json().get('detail', response.text or 'Unknown error')
                                except Exception:
                                    err = response.text or 'Unknown error'
                                st.error(f"Failed to update user: {err}")
            
            with col2:
                if st.button("Delete User"):
                    # Confirm deletion
                    if st.checkbox("I understand this action cannot be undone"):
                        # Call API to delete user
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        response = requests.delete(
                            f"{API_URL}/users/{selected_user_id}",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            st.success("User deleted successfully!")
                            st.rerun()
                        else:
                            try:
                                err = response.json().get('detail', response.text or 'Unknown error')
                            except Exception:
                                err = response.text or 'Unknown error'
                            st.error(f"Failed to delete user: {err}")
    else:
        st.info("No users found.")

with tab2:
    st.subheader("Register New User")
    
    with st.form("register_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            user_name = st.text_input("Username")
        
        with col2:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            is_staff = st.checkbox("Register as Coach/Admin")
        
        submit = st.form_submit_button("Register User")
        
        if submit:
            if not first_name or not last_name or not user_name or not email or not password:
                st.error("All fields are required")
            else:
                # Call API to register user
                user_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "user_name": user_name,
                    "email": email,
                    "password": password
                }
                
                success, message = register_user(user_data, st.session_state.token)
                
                if success:
                    st.success(message)
                    st.info("Now you can add athlete details for this user if needed.")
                else:
                    st.error(message)

with tab3:
    st.subheader("Manage Athlete Details")
    
    # Get all users who are athletes (not staff)
    users_df = get_all_users(st.session_state.token)
    
    if not users_df.empty:
        athletes_df = users_df[users_df['is_staff'] == False]
        
        if not athletes_df.empty:
            # Select athlete
            selected_athlete_id = st.selectbox("Select Athlete", athletes_df['id'].tolist())
            
            if selected_athlete_id:
                # Get selected athlete
                selected_athlete = athletes_df[athletes_df['id'] == selected_athlete_id].iloc[0]
                
                st.write(f"**Name:** {selected_athlete['first_name']} {selected_athlete['last_name']}")
                st.write(f"**Email:** {selected_athlete['email']}")
                
                # Check if athlete details exist
                import requests
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.get(
                    f"{API_URL}/athletes/get_athlete_details/{selected_athlete_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Athlete details exist, show edit form
                    athlete_data = response.json()["athlete"]
                    
                    st.subheader("Edit Athlete Details")
                    with st.form("edit_athlete_form"):
                        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(athlete_data["gender"]) if athlete_data["gender"] in ["Male", "Female", "Other"] else 0)
                        age = st.number_input("Age", min_value=0, max_value=120, value=athlete_data["age"])
                        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=athlete_data["weight"])
                        height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, value=athlete_data["height"])
                        
                        submit = st.form_submit_button("Update Athlete")
                        
                        if submit:
                            # Call API to update athlete
                            data = {
                                "user_id": selected_athlete_id,
                                "gender": gender,
                                "age": age,
                                "weight": weight,
                                "height": height
                            }
                            response = requests.patch(
                                f"{API_URL}/athletes/edit_athlete/{selected_athlete_id}",
                                json=data,
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                st.success("Athlete details updated successfully!")
                            else:
                                try:
                                    err = response.json().get('detail', response.text or 'Unknown error')
                                except Exception:
                                    err = response.text or 'Unknown error'
                                st.error(f"Failed to update athlete details: {err}")
                    
                    # Add delete button
                    if st.button("Delete Athlete Details"):
                        if st.checkbox("I understand this action cannot be undone"):
                            response = requests.delete(
                                f"{API_URL}/athletes/delete_athlete/{selected_athlete_id}",
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                st.success("Athlete details deleted successfully!")
                                st.rerun()
                            else:
                                try:
                                    err = response.json().get('detail', response.text or 'Unknown error')
                                except Exception:
                                    err = response.text or 'Unknown error'
                                st.error(f"Failed to delete athlete details: {err}")
                
                elif response.status_code == 404:
                    # Athlete details don't exist, show add form
                    st.subheader("Add Athlete Details")
                    with st.form("add_athlete_form"):
                        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                        age = st.number_input("Age", min_value=0, max_value=120)
                        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0)
                        height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0)
                        
                        submit = st.form_submit_button("Add Athlete")
                        
                        if submit:
                            # Call API to add athlete
                            data = {
                                "user_id": selected_athlete_id,
                                "gender": gender,
                                "age": age,
                                "weight": weight,
                                "height": height
                            }
                            
                            success, message = add_athlete(data, st.session_state.token)
                            
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.error("Failed to check athlete details")
        else:
            st.info("No athletes found. Register users as athletes first.")
    else:
        st.info("No users found.")