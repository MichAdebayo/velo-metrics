import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import check_authentication
from utils.api import get_performance_history, get_athlete_details, get_stats

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "athlete":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Athlete Dashboard")

# Get athlete details
athlete = get_athlete_details(st.session_state.user_id, st.session_state.token)
if not athlete:
    st.warning("Athlete profile not found. Please contact your coach.")
    st.stop()

# Display athlete info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Age", athlete["age"])
with col2:
    st.metric("Weight (kg)", athlete["weight"])
with col3:
    st.metric("Height (cm)", athlete["height"])

# Get performance history
performance_df = get_performance_history(st.session_state.user_id, st.session_state.token)

if not performance_df.empty:
    st.subheader("Performance Trends")
    
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Power", "Heart Rate", "VO2 Max", "Respiratory Frequency", "Cadence"])
    
    with tab1:
        fig = px.line(performance_df, x="test_type", y="power_max", title="Maximum Power by Test Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(performance_df, x="test_type", y="hr_max", title="Maximum Heart Rate by Test Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.line(performance_df, x="test_type", y="vo2_max", title="VO2 Max by Test Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = px.line(performance_df, x="test_type", y="rf_max", title="Maximum Respiratory Frequency by Test Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        fig = px.line(performance_df, x="test_type", y="cadence_max", title="Maximum Cadence by Test Type")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No performance data available yet.")

# Compare with top performers
st.subheader("How You Compare")

stats = get_stats()
if stats:
    # Get the details of top performers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Show Strongest Athlete"):
            strongest_id = stats["strongest_athlete"][0]
            strongest_athlete = get_athlete_details(strongest_id, st.session_state.token)
            strongest_performance = get_performance_history(strongest_id, st.session_state.token)
            
            if strongest_athlete and not strongest_performance.empty:
                st.subheader(f"Strongest Athlete (ID: {strongest_id})")
                st.metric("Max Power", f"{strongest_performance['power_max'].max()} W")
                
                # Compare with user's max power

                # Compare with user's max power
                if not performance_df.empty:
                    user_max = performance_df['power_max'].max()
                    difference = strongest_performance['power_max'].max() - user_max
                    st.metric("Your Max Power", f"{user_max} W", delta=f"{-difference} W")
                    
                    # Create comparison chart
                    fig = px.bar(
                        x=["You", "Strongest Athlete"],
                        y=[user_max, strongest_performance['power_max'].max()],
                        title="Power Comparison"
                    )
                    st.plotly_chart(fig, use_container_width=True)

    with col2:
        if st.button("Show Highest VO2 Max Athlete"):
            vo2max_id = stats["highest_vo2max"][0]
            vo2max_athlete = get_athlete_details(vo2max_id, st.session_state.token)
            vo2max_performance = get_performance_history(vo2max_id, st.session_state.token)
            
            if vo2max_athlete and not vo2max_performance.empty:
                st.subheader(f"Highest VO2 Max Athlete (ID: {vo2max_id})")
                st.metric("Max VO2", f"{vo2max_performance['vo2_max'].max()} ml/kg/min")
                
                # Compare with user's VO2 max
                if not performance_df.empty:
                    user_max = performance_df['vo2_max'].max()
                    difference = vo2max_performance['vo2_max'].max() - user_max
                    st.metric("Your VO2 Max", f"{user_max} ml/kg/min", delta=f"{-difference} ml/kg/min")
                    
                    # Create comparison chart
                    fig = px.bar(
                        x=["You", "Highest VO2 Max Athlete"],
                        y=[user_max, vo2max_performance['vo2_max'].max()],
                        title="VO2 Max Comparison"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        if st.button("Show Best Power-to-Weight Ratio Athlete"):
            pwr_id = stats["best_power_weight_ratio"][0]
            pwr_athlete = get_athlete_details(pwr_id, st.session_state.token)
            pwr_performance = get_performance_history(pwr_id, st.session_state.token)
            
            if pwr_athlete and not pwr_performance.empty:
                pwr_ratio = stats["best_power_weight_ratio"][1]
                st.subheader(f"Best Power-to-Weight Athlete (ID: {pwr_id})")
                st.metric("Power-to-Weight Ratio", f"{pwr_ratio:.2f} W/kg")
                
                # Compare with user's power-to-weight ratio
                if not performance_df.empty and athlete:
                    user_max_power = performance_df['power_max'].max()
                    user_weight = athlete["weight"]
                    user_ratio = user_max_power / user_weight if user_weight > 0 else 0
                    difference = pwr_ratio - user_ratio
                    st.metric("Your Power-to-Weight", f"{user_ratio:.2f} W/kg", delta=f"{-difference:.2f} W/kg")
                    
                    # Create comparison chart
                    fig = px.bar(
                        x=["You", "Best Power-to-Weight Athlete"],
                        y=[user_ratio, pwr_ratio],
                        title="Power-to-Weight Ratio Comparison"
                    )
                    st.plotly_chart(fig, use_container_width=True)