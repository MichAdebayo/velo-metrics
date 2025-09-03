import pandas as pd
import numpy as np
from typing import Dict, List
import os

class CSVProcessor:
    """Processes cycling performance CSV files to extract key metrics"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def process_wingate_file(self, filepath: str) -> Dict:
        """Process Wingate test file - anaerobic capacity assessment"""
        try:
            df = pd.read_csv(filepath)

            # Normalize column names to handle different formats
            df = self._normalize_column_names(df)

            # Wingate test typically lasts 30 seconds with all-out effort
            # Find the 30-second window with highest average power
            window_size = 30  # seconds
            max_power_window = self._find_max_power_window(df, window_size)

            metrics = {
                "test_type": "wingate",
                "power_max": float(df['Power'].max()),
                "power_mean_30s": float(max_power_window['power_mean']),
                "hr_max": float(df['HR'].max()),
                "cadence_max": float(df['Cadence'].max()),
                "rf_max": float(df['RF'].max()),
                "vo2_max": float(df['Oxygen'].max()),
                "fatigue_index": self._calculate_fatigue_index(df),
                "peak_power_time": int(max_power_window['start_time'])
            }

            return metrics

        except Exception as e:
            raise Exception(f"Error processing Wingate file {filepath}: {str(e)}") from e

    def process_incremental_file(self, filepath: str) -> Dict:
        """Process incremental test file - aerobic capacity assessment"""
        try:
            df = pd.read_csv(filepath)

            # Normalize column names to handle different formats
            df = self._normalize_column_names(df)

            metrics = {
                "test_type": "incremental",
                "power_max": float(df['Power'].max()),
                "hr_max": float(df['HR'].max()),
                "cadence_max": float(df['Cadence'].max()),
                "rf_max": float(df['RF'].max()),
                "vo2_max": float(df['Oxygen'].max()),
                "vo2_mean": float(df['Oxygen'].mean()),
                "hr_mean": float(df['HR'].mean()),
                "test_duration": int(df['time'].max())
            }

            return metrics

        except Exception as e:
            raise Exception(
                f"Error processing incremental file {filepath}: {str(e)}"
            ) from e

    def process_general_test_file(self, filepath: str, test_label: str) -> Dict:
        """Process general test files (I.csv, II.csv)"""
        try:
            df = pd.read_csv(filepath)

            # Normalize column names to handle different formats
            df = self._normalize_column_names(df)

            metrics = {
                "test_type": f"general_{test_label}",
                "power_max": float(df['Power'].max()),
                "hr_max": float(df['HR'].max()),
                "cadence_max": float(df['Cadence'].max()),
                "rf_max": float(df['RF'].max()),
                "vo2_max": float(df['Oxygen'].max()),
                "power_mean": float(df['Power'].mean()),
                "hr_mean": float(df['HR'].mean()),
                "test_duration": int(df['time'].max())
            }

            return metrics

        except Exception as e:
            raise Exception(
                f"Error processing {test_label} file {filepath}: {str(e)}"
            ) from e

    def process_subject_data(self, subject_id: str) -> Dict:
        """Process all CSV files for a given subject"""
        base_path = os.path.join(self.data_dir, f"sbj_{subject_id}")

        files_to_process = {
            "I": f"{base_path}_I.csv",
            "II": f"{base_path}_II.csv",
            "incremental": f"{base_path}_incremental.csv",
            "Wingate": f"{base_path}_Wingate.csv"
        }

        results = {}

        for test_type, filepath in files_to_process.items():
            if os.path.exists(filepath):
                try:
                    if test_type == "Wingate":
                        results[test_type] = self.process_wingate_file(filepath)
                    elif test_type == "incremental":
                        results[test_type] = self.process_incremental_file(filepath)
                    else:
                        results[test_type] = self.process_general_test_file(filepath, test_type)
                except Exception as e:
                    print(f"Warning: Failed to process {test_type} for subject {subject_id}: {str(e)}")
                    results[test_type] = None
            else:
                print(f"Warning: File {filepath} not found")
                results[test_type] = None

        return results

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to handle different CSV formats"""
        column_mapping = {
            'power': 'Power',
            'oxygen': 'Oxygen',
            'cadence': 'Cadence',
            'heart_rate': 'HR',
            'respiratory_frequency': 'RF'
        }

        # Rename columns if they exist in lowercase
        df = df.rename(columns=column_mapping)
        return df

    def _find_max_power_window(self, df: pd.DataFrame, window_size: int = 30) -> Dict:
        """Find the 30-second window with highest average power in Wingate test"""
        max_power = 0
        max_window_start = 0

        for start_time in range(int(df['time'].min()), int(df['time'].max()) - window_size + 1):
            window_data = df[(df['time'] >= start_time) & (df['time'] < start_time + window_size)]
            if not window_data.empty:
                avg_power = window_data['Power'].mean()
                if avg_power > max_power:
                    max_power = avg_power
                    max_window_start = start_time

        return {
            "power_mean": max_power,
            "start_time": max_window_start
        }

    def _calculate_fatigue_index(self, df: pd.DataFrame) -> float:
        """Calculate fatigue index for Wingate test (power decline over time)"""
        try:
            # Get power values from the peak 30-second window
            peak_window = self._find_max_power_window(df)
            start_time = peak_window['start_time']

            window_data = df[(df['time'] >= start_time) & (df['time'] < start_time + 30)]
            if len(window_data) < 10:  # Need at least 10 data points
                return 0.0

            # Calculate linear regression slope of power over time using numpy
            try:
                slope, _ = np.polyfit(window_data['time'], window_data['Power'], 1)
                slope = float(slope)
            except Exception:
                # Fallback to simple calculation
                time_diff = window_data['time'].max() - window_data['time'].min()
                power_diff = window_data['Power'].max() - window_data['Power'].min()
                slope = power_diff / time_diff if time_diff > 0 else 0.0

            # Fatigue index is the absolute value of the slope (power decline rate)
            # Negative slope indicates fatigue, we take absolute value
            fatigue_index = abs(slope) * 100  # Scale for readability

            return round(fatigue_index, 2)

        except Exception:
            return 0.0

    def get_aggregated_metrics(self, subject_data: Dict) -> Dict:
        """Aggregate metrics across all tests for a subject to get best values"""
        aggregated = {
            "power_max": 0,
            "hr_max": 0,
            "vo2_max": 0,
            "rf_max": 0,
            "cadence_max": 0
        }

        for test_type, metrics in subject_data.items():
            if metrics:
                for key in aggregated:
                    if key in metrics:
                        aggregated[key] = max(aggregated[key], metrics[key])

        return aggregated

