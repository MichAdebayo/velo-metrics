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

    if user_info:
        st.session_state.role = "admin" if user_info.get("is_staff") else "athlete"
    
    else:
        st.error("Failed to retrieve user information. Please log in again.")
        st.session_state.token = None # Clear invalid token
        st.rerun() # Rerun to show login screen

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.session_state.token = None
        st.session_state.user_id = None
        st.rerun()

    # Define all pages that should be accessible in your app
    home = st.Page("app.py", title="Home", icon="🏠")
    admin_dashboard = st.Page("pages/admin_dashboard.py", title="Admin Dashboard", icon="📊")
    user_management = st.Page("pages/user_management.py", title="User Management", icon="👥")
    performance_management = st.Page("pages/performance_management.py", title="Performance Management", icon="📈")
    athlete_dashboard = st.Page("pages/athlete_dashboard.py", title="Athlete Dashboard", icon="🏠")
    athlete_profile = st.Page("pages/athlete_profile.py", title="My Profile", icon="👤")
    performance_history = st.Page("pages/performance_history.py", title="Performance History", icon="📊")

    # Make all pages available but hide the default navigation
    all_pages = [
        home, admin_dashboard, user_management, performance_management,
        athlete_dashboard, athlete_profile, performance_history
    ]
    page = st.navigation(all_pages, position="hidden")

    # Create your custom navigation in the sidebar based on role
    if st.session_state.role == "admin":
        st.sidebar.title("Admin Navigation")
        st.sidebar.page_link("pages/admin_dashboard.py", label="Admin Dashboard", icon="📊")
        st.sidebar.page_link("pages/user_management.py", label="User Management", icon="👥")
        st.sidebar.page_link("pages/performance_management.py", label="Performance Management", icon="📈")
   
    elif st.session_state.role == "athlete":
        st.sidebar.title("Athlete Navigation")
        st.sidebar.page_link("pages/athlete_dashboard.py", label="Dashboard", icon="🏠")
        st.sidebar.page_link("pages/athlete_profile.py", label="My Profile", icon="👤")
        st.sidebar.page_link("pages/performance_history.py", label="Performance History", icon="📊")

    else:
        st.error("Invalid role. Please log in again.")
        st.session_state.token = None
        st.session_state.role = None
        st.rerun()

    # Run the current page
    page.run()