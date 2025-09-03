# --- Added for dashboard statistics tab ---
def get_performances_by_username(username):
    """Get performances for a user by username"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/performance/by-username/{username}", headers=headers)
    if response.status_code == 200:
        return response.json()
    try:
        import streamlit as st
        st.error(f"Failed to get performances for username {username}")
    except (ImportError, AttributeError):
        print(f"Failed to get performances for username {username}")
    return []
import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8001/"

def get_user_info():
    """Get user information"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/user_info", headers=headers) 

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Unauthorized: Invalid or expired token. Please log in again.")
        st.session_state.token = None # Clear the invalid token from session state
        st.rerun() # Force a rerun to display the login screen
        return None # Explicitly return None to avoid further errors
    else:
        st.error(f"Failed to get user information: Status code {response.status_code}")
    return None

def get_user_info_by_username(username, token):
    """Get user info by username"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users/by-username/{username}", headers=headers)

    if response.status_code == 200:
        return response.json()
    
    # Handle error gracefully - don't use st.error if streamlit is not available
    try:
        import streamlit as st
        st.error("Failed to get user information")
    except (ImportError, AttributeError):
        print("Failed to get user information")
    return None

def get_athlete_details(user_id, token):
    """Get athlete details"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/athletes/get_athlete_details/{user_id}", headers=headers)

    if response.status_code == 200:
        return response.json()["athlete"]
    
    # Handle error gracefully
    try:
        import streamlit as st
        st.error("Failed to get athlete details")
    except (ImportError, AttributeError):
        print("Failed to get athlete details")
    return None

def get_performance_history(user_id, token):
    """Get performance history for a user"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/performance/user/{user_id}", headers=headers)

    if response.status_code == 200:
        return pd.DataFrame(response.json())
    
    # Handle error gracefully
    try:
        import streamlit as st
        st.error("Failed to get performance history")
    except (ImportError, AttributeError):
        print("Failed to get performance history")
    return pd.DataFrame()


def get_stats():
    """Get performance statistics"""
    response = requests.get(f"{API_URL}/performance/stats")

    if response.status_code == 200:
        return response.json()
    
    # Handle error gracefully
    try:
        import streamlit as st
        st.error("Failed to get statistics")
    except (ImportError, AttributeError):
        print("Failed to get statistics")
    return None

def get_all_users(token):
    """Get all users (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users", headers=headers)

    if response.status_code == 200:
        return pd.DataFrame(response.json())
    
    # Handle error gracefully
    try:
        import streamlit as st
        st.error("Failed to get users")
    except (ImportError, AttributeError):
        print("Failed to get users")
    return pd.DataFrame()

def register_user(user_data, token):
    """Register a new user (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/register", json=user_data, headers=headers)
    
    if response.status_code == 200:
        return True, "User registered successfully"
    else:
        return False, response.json().get("detail", "Failed to register user")

def add_athlete(athlete_data, token):
    """Add athlete details (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/athletes/add_athlete", json=athlete_data, headers=headers)
    
    if response.status_code == 200:
        return True, "Athlete added successfully"
    else:
        return False, response.json().get("detail", "Failed to add athlete")

def add_performance(performance_data, token):
    """Add performance record (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/performance/add_performance", json=performance_data, headers=headers)
    
    if response.status_code == 200:
        return True, "Performance added successfully"
    else:
        return False, response.json().get("detail", "Failed to add performance")
    

def get_performances(user_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}

        if st.session_state.is_staff:
            response = requests.get(f"{API_URL}/performance/user/{user_id}", headers=headers)
        else:

            response = requests.get(f"{API_URL}/performance/my-stats", headers=headers)

        if response.status_code == 200:
            return response.json()
        
        # Handle error gracefully
        try:
            import streamlit as st
            st.error(f"Impossible de récupérer les performances (Status: {response.status_code})")
        except (ImportError, AttributeError):
            print(f"Impossible de récupérer les performances (Status: {response.status_code})")
        return []
    except Exception as e:
        try:
            import streamlit as st
            st.error(f"Erreur: {str(e)}")
        except (ImportError, AttributeError):
            print(f"Erreur: {str(e)}")
        return []


def get_performance_by_id(performance_id):
    # Cette fonction est une simulation car l'API n'a pas d'endpoint spécifique
    # pour récupérer une performance par ID
    performances = get_performances(st.session_state.user_id)
    return next(
        (
            perf
            for perf in performances
            if perf.get("performance_id") == performance_id
        ),
        None,
    )

def update_performance(performance_id, power, vo2_max, heart_rate, respiration_frequency, cadence):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }

        # Récupérer d'abord les données actuelles de performance
        current_perf = get_performance_by_id(performance_id)
        if not current_perf:
            return False

        response = requests.patch(
            f"{API_URL}/performance/{performance_id}",
            headers=headers,
            json={
                "user_id": current_perf["user_id"],
                "time": current_perf["time"],
                "power": power,
                "vo2_max": vo2_max,
                "oxygen": current_perf.get("oxygen", 0),
                "cadence": cadence,
                "heart_rate": heart_rate,
                "respiration_frequency": respiration_frequency
            }
        )

        if response.status_code in {200, 202}:
            return True
        
        # Handle error gracefully
        try:
            import streamlit as st
            st.error(f"Erreur de mise à jour: {response.json().get('detail', 'Erreur inconnue')}")
        except (ImportError, AttributeError):
            print(f"Erreur de mise à jour: {response.json().get('detail', 'Erreur inconnue')}")
        return False
    except Exception as e:
        try:
            import streamlit as st
            st.error(f"Erreur: {str(e)}")
        except (ImportError, AttributeError):
            print(f"Erreur: {str(e)}")
        return False

def delete_performance(performance_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.delete(
            f"{API_URL}/performance/{performance_id}",
            headers=headers
        )

        if response.status_code in {200, 202, 204}:
            return True
        
        # Handle error gracefully
        try:
            import streamlit as st
            st.error(f"Erreur de suppression: {response.json().get('detail', 'Erreur inconnue')}")
        except ImportError:
            print(f"Erreur de suppression: {response.json().get('detail', 'Erreur inconnue')}")
        return False
    except Exception as e:
        try:
            import streamlit as st
            st.error(f"Erreur: {str(e)}")
        except ImportError:
            print(f"Erreur: {str(e)}")
        return False
    
def get_athletes_with_performance(token):
    """Get all athletes who have performance data (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users/athletes-with-performance", headers=headers)

    if response.status_code == 200:
        return pd.DataFrame(response.json())
    
    # Handle error gracefully
    try:
        import streamlit as st
        st.error("Failed to get athletes with performance data")
    except (ImportError, AttributeError):
        print("Failed to get athletes with performance data")
    return pd.DataFrame()
    
