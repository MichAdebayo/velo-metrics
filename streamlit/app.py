import streamlit as st

# Page configuration
st.set_page_config(page_title="Athlete Performance Tracker", layout="wide")

from utils.auth import login, check_authentication
from utils.api import get_user_info

# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "is_staff" not in st.session_state:
    st.session_state.is_staff = None

# Check if user is authenticated
if not check_authentication():
    st.title("Athlete Performance Tracker")
    st.subheader("Login")

    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if submit := st.form_submit_button("Login"):
            success, message = login(username, password)
            if success:
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(message)
else:
    if user_info := get_user_info():
        # Display welcome message
        st.title(f"Welcome, {user_info['first_name']} {user_info['last_name']}")
    else:
        st.error("Failed to retrieve user information. Please log in again.")
        st.session_state.token = None # Clear invalid token
        st.rerun() # Rerun to show login screen

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.session_state.token = None
        st.session_state.user_id = None
        st.session_state.is_staff = None
        st.rerun()

        # Custom navigation based on role
    if st.session_state.role == "admin":
        pages = [
            st.Page("pages/admin_dashboard.py", title="Admin Dashboard", icon="📊"),
            st.Page("pages/data_management.py", title="Data Management", icon="📥"),
            st.Page("pages/user_management.py", title="User Management", icon="👥"),
            st.Page("pages/performance_management.py", title="Performance Management", icon="📈"),
            st.Page("pages/statistics.py", title="Statistics", icon="📊"),
        ]
        pg = st.navigation(pages)
        pg.run()
   
    elif st.session_state.role == "athlete":
        pages = [
            st.Page("pages/athlete_dashboard.py", title="Dashboard", icon="🏠"),
            st.Page("pages/athlete_profile.py", title="My Profile", icon="👤"),
            st.Page("pages/performance_history.py", title="Performance History", icon="📊"),
        ]
        pg = st.navigation(pages)
        pg.run()

    else:
        st.error("Invalid role. Please log in again.")
        st.session_state.token = None
        st.session_state.role = None
        st.rerun()
