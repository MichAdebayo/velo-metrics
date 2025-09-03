import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.auth import check_authentication
from utils.api import get_performance_history, get_athlete_details

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "athlete":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Performance History")

# Get performance history
performance_df = get_performance_history(st.session_state.user_id, st.session_state.token)

if performance_df.empty:
    st.info("No performance data available yet.")
    st.stop()

# Add date filter
st.sidebar.header("Filter Data")
if 'date' in performance_df.columns:
    min_date = pd.to_datetime(performance_df['date']).min().date()
    max_date = pd.to_datetime(performance_df['date']).max().date()
    
    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter dataframe based on date
    filtered_df = performance_df[
        (pd.to_datetime(performance_df['date']).dt.date >= start_date) & 
        (pd.to_datetime(performance_df['date']).dt.date <= end_date)
    ]
else:
    filtered_df = performance_df

# Display performance data in a table
st.subheader("Performance Records")
st.dataframe(filtered_df)

# Create detailed visualizations
st.subheader("Performance Analysis")

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Metrics Over Time", "Radar Chart", "Correlations"])

with tab1:
    # Select metrics to display
    metrics = st.multiselect(
        "Select Metrics to Display",
        ["power_max", "hr_max", "vo2_max", "rf_max", "cadence_max"],
        default=["power_max", "vo2_max"]
    )
    
    if metrics:
        # Normalize data for comparison
        normalized_df = filtered_df.copy()
        for metric in metrics:
            if metric in filtered_df.columns:
                max_val = filtered_df[metric].max()
                if max_val > 0:  # Avoid division by zero
                    normalized_df[f"{metric}_normalized"] = filtered_df[metric] / max_val
        
        # Create line chart
        fig = go.Figure()
        for metric in metrics:
            if metric in filtered_df.columns:
                fig.add_trace(go.Scatter(
                    x=filtered_df['test_type'] if 'test_type' in filtered_df.columns else filtered_df.index,
                    y=filtered_df[metric],
                    mode='lines+markers',
                    name=metric
                ))
        fig.update_layout(title="Metrics by Test Type", xaxis_title="Test Type", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

        # Show normalized comparison
        st.subheader("Normalized Comparison")
        fig2 = go.Figure()
        for metric in metrics:
            if f"{metric}_normalized" in normalized_df.columns:
                fig2.add_trace(go.Scatter(
                    x=normalized_df['test_type'] if 'test_type' in normalized_df.columns else normalized_df.index,
                    y=normalized_df[f"{metric}_normalized"],
                    mode='lines+markers',
                    name=metric
                ))
        fig2.update_layout(title="Normalized Metrics (0-1 Scale)", xaxis_title="Test Type", yaxis_title="Normalized Value")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    # Get the latest performance record
    if not filtered_df.empty:
        latest_record = filtered_df.iloc[-1]
        
        # Create radar chart
        categories = ['Power Max', 'HR Max', 'VO2 Max', 'RF Max', 'Cadence Max']
        values = [
            latest_record.get('power_max', 0),
            latest_record.get('hr_max', 0),
            latest_record.get('vo2_max', 0),
            latest_record.get('rf_max', 0),
            latest_record.get('cadence_max', 0)
        ]
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Latest Performance'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            title="Performance Radar Chart"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Allow comparison with previous record
        if len(filtered_df) > 1:
            previous_record = filtered_df.iloc[-2]
            
            if st.checkbox("Compare with Previous Record"):
                prev_values = [
                    previous_record.get('power_max', 0),
                    previous_record.get('hr_max', 0),
                    previous_record.get('vo2_max', 0),
                    previous_record.get('rf_max', 0),
                    previous_record.get('cadence_max', 0)
                ]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Latest Performance'
                ))
                
                fig.add_trace(go.Scatterpolar(
                    r=prev_values,
                    theta=categories,
                    fill='toself',
                    name='Previous Performance'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                        )
                    ),
                    title="Performance Comparison"
                )
                
                st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Create correlation matrix
    if len(filtered_df) > 1:
        numeric_df = filtered_df.select_dtypes(include=['float64', 'int64'])
        corr = numeric_df.corr()
        
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Correlation Between Metrics"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("**Interpretation:**")
        st.write("- Values close to 1 indicate strong positive correlation")
        st.write("- Values close to -1 indicate strong negative correlation")
        st.write("- Values close to 0 indicate little to no correlation")
    else:
        st.info("Need more data points to calculate correlations.")