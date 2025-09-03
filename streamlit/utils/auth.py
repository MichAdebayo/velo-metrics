import streamlit as st
import requests
from utils.api import get_user_info_by_username 

API_URL = "http://localhost:8001/"

def login(username: str, password: str):
    """
    Call FastAPI /token endpoint for authentication.
    Then fetch user details to determine role.
    """
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code != 200:
            return False, "Invalid credentials"
        
        data = response.json()
        st.session_state.token = data["access_token"]
        st.session_state.username = username
        
        # Get user info to determine role
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        user_response = requests.get(f"{API_URL}/user_info", headers=headers)
        
        if user_response.status_code == 200:
            user_info = user_response.json()
            st.session_state.role = "admin" if user_info.get("is_staff") else "athlete"
            st.session_state.user_id = user_info.get("id")
            st.session_state.is_staff = user_info.get("is_staff", False)
        else:
            # Fallback if user info can't be retrieved
            st.session_state.role = "athlete"
            st.session_state.is_staff = False
        
        return True, "Login successful"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get("token") is not None