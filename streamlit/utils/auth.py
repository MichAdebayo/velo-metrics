import streamlit as st
import requests
from utils.api import get_user_info_by_username 

API_URL = "http://localhost:8001/"

def login(username: str, password: str):
    """
    Call FastAPI /token endpoint for authentication.
    Then fetch user details using the username.
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
        
        st.session_state.role = "athlete"  
        
        return True, "Login successful"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get("token") is not None