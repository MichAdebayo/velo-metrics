import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import backend modules with error handling
try:
    from backend.services.data_ingestion import DataIngestionService
    from backend.database import get_db_connection

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure the backend modules are properly set up.")
    IMPORTS_SUCCESSFUL = False
    st.stop()

# Import auth from streamlit utils
try:
    streamlit_path = os.path.join(project_root, 'streamlit')
    if streamlit_path not in sys.path:
        sys.path.insert(0, streamlit_path)

    import importlib
    auth_module = importlib.import_module('utils.auth')
    check_authentication = auth_module.check_authentication
except ImportError:
    st.error("Authentication module not found. Please check streamlit/utils/auth.py")
    st.stop()

# Check authentication
if not check_authentication():
    st.switch_page("app.py")

if st.session_state.role != "admin":
    st.error("You don't have permission to access this page")
    st.stop()

st.title("📊 Data Management - CSV Ingestion")

st.markdown("""
This page allows you to ingest cyclist performance data from CSV files into the database.
The system will:
1. Create user accounts for each subject (sbj_1 through sbj_7)
2. Generate athlete profiles with physical characteristics
3. Process performance data from all test types
4. Populate the database for testing all endpoints
""")

# Initialize session state for processing status
if "processing_results" not in st.session_state:
    st.session_state.processing_results = None
if "processing_summary" not in st.session_state:
    st.session_state.processing_summary = None

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Data Ingestion Process")

    if st.button("🚀 Start Data Ingestion", type="primary", use_container_width=True):
        with st.spinner("Processing cyclist data... This may take a few minutes."):

            # Initialize the data ingestion service
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            ingestion_service = DataIngestionService(data_dir)

            # Process all subjects
            results = ingestion_service.process_all_subjects()

            # Generate summary
            summary = ingestion_service.get_processing_summary(results)

            # Store results in session state
            st.session_state.processing_results = results
            st.session_state.processing_summary = summary

            st.success("Data ingestion completed!")
            st.rerun()

with col2:
    st.subheader("Data Overview")

    # Show current database status
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current counts
        cursor.execute("SELECT COUNT(*) FROM User WHERE user_name LIKE 'sbj_%'")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Athlete")
        athlete_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Performance")
        performance_count = cursor.fetchone()[0]

        conn.close()

        st.metric("Test Subjects", user_count)
        st.metric("Athlete Profiles", athlete_count)
        st.metric("Performance Records", performance_count)

    except Exception as e:
        st.error(f"Database connection error: {str(e)}")

# Display results if processing has been completed
if st.session_state.processing_results:
    st.divider()
    st.subheader("📋 Processing Results")

    # Summary metrics
    summary = st.session_state.processing_summary

    if summary:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Success Rate", summary.get("success_rate", "N/A"))
        with col2:
            st.metric("Users Created", summary.get("users_created", 0))
        with col3:
            st.metric("Athletes Created", summary.get("athletes_created", 0))
        with col4:
            st.metric("Performance Records", summary.get("performance_records_processed", 0))
    else:
        st.warning("No summary data available")

    # Detailed results table
    st.subheader("Subject Processing Details")

    results_data = []
    for result in st.session_state.processing_results:
        results_data.append({
            "Subject": f"sbj_{result['subject_id']}",
            "User Created": "✅" if result["user_created"] else "❌",
            "Athlete Created": "✅" if result["athlete_created"] else "❌",
            "Performance Processed": "✅" if result["performance_processed"] else "❌",
            "Status": "Success" if all([result["user_created"], result["athlete_created"], result["performance_processed"]]) else "Failed",
            "Errors": len(result["errors"])
        })

    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, use_container_width=True)

    # Show errors if any
    all_errors = []
    for result in st.session_state.processing_results:
        for error in result["errors"]:
            all_errors.append({
                "Subject": f"sbj_{result['subject_id']}",
                "Error": error
            })

    if all_errors:
        st.subheader("⚠️ Errors Encountered")
        errors_df = pd.DataFrame(all_errors)
        st.dataframe(errors_df, use_container_width=True)

    # Data integrity check
    st.subheader("🔍 Data Integrity Check")

    try:
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        ingestion_service = DataIngestionService(data_dir)
        integrity_check = ingestion_service.verify_data_integrity()

        if "error" not in integrity_check:
            integrity_status = "✅ All Good" if integrity_check["data_integrity_ok"] else "⚠️ Issues Found"

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", integrity_check["users"])
            with col2:
                st.metric("Total Athletes", integrity_check["athletes"])
            with col3:
                st.metric("Total Performances", integrity_check["performances"])

            st.write(f"**Data Integrity Status:** {integrity_status}")

            if not integrity_check["data_integrity_ok"]:
                st.warning("Found orphaned records that may need attention.")
        else:
            st.error(f"Integrity check failed: {integrity_check['error']}")

    except Exception as e:
        st.error(f"Failed to perform integrity check: {str(e)}")

# Information section
st.divider()
st.subheader("ℹ️ About This Process")

st.markdown("""
**What gets created:**
- **7 User accounts** (sbj_1 through sbj_7) with athlete role
- **7 Athlete profiles** with generated physical characteristics (age, weight, height, gender)
- **Up to 28 Performance records** (4 test types × 7 subjects)

**Test Types Processed:**
- **Wingate**: Anaerobic capacity (peak power, fatigue index)
- **Incremental**: Aerobic capacity (VO2 max, lactate threshold)
- **General Tests (I & II)**: Overall performance metrics

**Generated Data:**
- Realistic physical characteristics for each athlete
- Peak performance metrics extracted from time-series data
- Proper database relationships maintained

**Next Steps After Ingestion:**
- Test the Statistics page for athlete comparisons
- Use Performance Management to view/edit records
- Verify Admin Dashboard shows populated data
- Test all athlete-related endpoints
""")

# Clear results button
if st.session_state.processing_results and st.button("🗑️ Clear Results"):
    st.session_state.processing_results = None
    st.session_state.processing_summary = None
    st.rerun()
