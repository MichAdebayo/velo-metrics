# Data Ingestion System

This system provides automated ingestion of cyclist performance data from CSV files into the database for testing purposes.

## Overview

The data ingestion system processes 7 subjects (sbj_1 through sbj_7) with 4 types of performance tests each:

- **Wingate Test**: Anaerobic capacity assessment (30-second all-out effort)
- **Incremental Test**: Aerobic capacity assessment (graded exercise test)
- **General Tests (I & II)**: Overall performance metrics

## Components

### 1. CSV Processor (`backend/utils/csv_processor.py`)
- Extracts key performance metrics from time-series CSV data
- Handles different test types with appropriate algorithms
- Calculates derived metrics (fatigue index, peak power windows, etc.)

### 2. Data Ingestion Service (`backend/services/data_ingestion.py`)
- Creates user accounts for each subject
- Generates athlete profiles with realistic physical characteristics
- Processes and inserts performance data into database
- Maintains data integrity and relationships

### 3. Admin Interface (`streamlit/pages/data_management.py`)
- Web interface for triggering data ingestion
- Progress monitoring and results display
- Error handling and data integrity verification

## Usage

### Option 1: Web Interface (Recommended)
1. Start the Streamlit application
2. Login as admin
3. Navigate to "Data Management" page
4. Click "Start Data Ingestion"
5. Monitor progress and review results

### Option 2: Command Line Testing
```bash
cd /path/to/project
python test_data_ingestion.py
```

## Data Generated

### User Accounts
- **Username**: sbj_1, sbj_2, ..., sbj_7
- **Password**: password_1, password_2, ..., password_7
- **Role**: Athlete (not admin)

### Athlete Profiles
Generated realistic physical characteristics:
- **Gender**: Alternating male/female
- **Age**: 22-28 years
- **Weight**: 59.7-80.2 kg
- **Height**: 165.4-185.6 cm

### Performance Records
For each subject, creates up to 4 performance records with metrics:
- **power_max**: Peak power output
- **hr_max**: Maximum heart rate
- **vo2_max**: Peak oxygen consumption
- **rf_max**: Maximum respiratory frequency
- **cadence_max**: Peak pedaling cadence

## Test Coverage

After data ingestion, you can test:

### Statistics Page
- Strongest athlete ranking
- Highest VO2 max ranking
- Best power-to-weight ratio

### Performance Management
- View all athlete performance records
- Edit individual performance data
- Delete performance records

### Admin Dashboard
- User and athlete counts
- System statistics
- Data completeness metrics

### API Endpoints
- `/performance/stats` - Statistics endpoint
- `/performance/user/{id}` - User performance history
- `/athletes/get_athlete_details/{id}` - Athlete profile data

## Data Integrity

The system includes automatic verification:
- ✅ All users have corresponding athlete profiles
- ✅ All performance records link to valid users
- ✅ No orphaned database records
- ✅ Consistent data relationships

## Troubleshooting

### Common Issues
1. **CSV files not found**: Ensure data directory path is correct
2. **Database connection errors**: Check database configuration
3. **Permission errors**: Ensure write access to database file

### Recovery
- Run integrity check to identify issues
- Manually delete incomplete records if needed
- Re-run ingestion for failed subjects only

## Next Steps

After successful data ingestion:
1. Test all pages in the application
2. Verify API endpoints return expected data
3. Use the populated data for development and testing
4. Consider adding more sophisticated CSV processing if needed
