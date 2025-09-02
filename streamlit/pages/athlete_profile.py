import streamlit as st
from utils.auth import check_authentication
from utils.api import get_athlete_details, get_user_info

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "athlete":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("My Profile")

# Get user and athlete info
user_info = get_user_info(st.session_state.user_id, st.session_state.token)
athlete = get_athlete_details(st.session_state.user_id, st.session_state.token)

if not user_info:
    st.error("Failed to load user information")
    st.stop()

# Display user information
st.subheader("Personal Information")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Name:** {user_info['first_name']} {user_info['last_name']}")
    st.write(f"**Username:** {user_info['user_name']}")
with col2:
    st.write(f"**Email:** {user_info['email']}")

# Display athlete information if available
if athlete:
    st.subheader("Athlete Details")
    
    # Create form for editing athlete details
    with st.form("edit_athlete_form"):
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(athlete["gender"]) if athlete["gender"] in ["Male", "Female", "Other"] else 0)
            age = st.number_input("Age", min_value=0, max_value=120, value=athlete["age"])
        with col2:
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=athlete["weight"])
            height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, value=athlete["height"])
        
        submit = st.form_submit_button("Update Profile")
        
        if submit:
            # Call API to update athlete details
            import requests
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            data = {
                "user_id": st.session_state.user_id,
                "gender": gender,
                "age": age,
                "weight": weight,
                "height": height
            }
            response = requests.patch(
                f"http://your-fastapi-url/api/athletes/edit_athlete/{st.session_state.user_id}",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                st.success("Profile updated successfully!")
            else:
                st.error(f"Failed to update profile: {response.json().get('detail', 'Unknown error')}")
else:
    st.warning("Athlete profile not found. Please contact your coach to set up your athlete profile.")