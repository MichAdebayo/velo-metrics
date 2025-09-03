import sqlite3
import os
from typing import Dict, List, Optional
from ..database import get_db_connection
from ..utils.csv_processor import CSVProcessor
import hashlib

class DataIngestionService:
    """Service for ingesting cyclist performance data from CSV files"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.csv_processor = CSVProcessor(data_dir)

        # Sample athlete data for subjects (since CSV files don't contain physical characteristics)
        self.sample_athlete_data = {
            "1": {"gender": "male", "age": 25, "weight": 75.5, "height": 180.5},
            "2": {"gender": "female", "age": 22, "weight": 62.3, "height": 168.2},
            "3": {"gender": "male", "age": 28, "weight": 78.1, "height": 182.3},
            "4": {"gender": "female", "age": 24, "weight": 65.8, "height": 172.1},
            "5": {"gender": "male", "age": 26, "weight": 72.4, "height": 178.9},
            "6": {"gender": "female", "age": 23, "weight": 59.7, "height": 165.4},
            "7": {"gender": "male", "age": 27, "weight": 80.2, "height": 185.6}
        }

    def create_user_for_subject(self, subject_id: str) -> Optional[int]:
        """Create a user account for a subject"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute("SELECT id FROM User WHERE user_name = ?", (f"sbj_{subject_id}",))
            existing_user = cursor.fetchone()

            if existing_user:
                print(f"User sbj_{subject_id} already exists with ID: {existing_user[0]}")
                return existing_user[0]

            # Create new user
            user_data = {
                "user_name": f"sbj_{subject_id}",
                "first_name": f"Subject_{subject_id}",
                "last_name": f"Athlete_{subject_id}",
                "email": f"sbj_{subject_id}@cyclist.test",
                "password": self._hash_password(f"password_{subject_id}"),  # Simple password for testing
                "is_staff": 0  # All subjects are athletes, not staff
            }

            cursor.execute("""
                INSERT INTO User (user_name, first_name, last_name, email, password, is_staff)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_data["user_name"],
                user_data["first_name"],
                user_data["last_name"],
                user_data["email"],
                user_data["password"],
                user_data["is_staff"]
            ))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            print(f"Created user sbj_{subject_id} with ID: {user_id}")
            return user_id

        except Exception as e:
            print(f"Error creating user for subject {subject_id}: {str(e)}")
            return None

    def create_athlete_profile(self, user_id: int, subject_id: str) -> bool:
        """Create athlete profile for a user"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if athlete profile already exists
            cursor.execute("SELECT user_id FROM Athlete WHERE user_id = ?", (user_id,))
            existing_athlete = cursor.fetchone()

            if existing_athlete:
                print(f"Athlete profile already exists for user ID: {user_id}")
                return True

            # Get athlete data for this subject
            athlete_data = self.sample_athlete_data.get(subject_id)
            if not athlete_data:
                print(f"No athlete data available for subject {subject_id}")
                return False

            cursor.execute("""
                INSERT INTO Athlete (user_id, gender, age, weight, height)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                athlete_data["gender"],
                athlete_data["age"],
                athlete_data["weight"],
                athlete_data["height"]
            ))

            conn.commit()
            conn.close()

            print(f"Created athlete profile for user ID: {user_id}")
            return True

        except Exception as e:
            print(f"Error creating athlete profile for user {user_id}: {str(e)}")
            return False

    def process_and_insert_performance_data(self, user_id: int, subject_id: str) -> bool:
        """Process CSV files and insert performance data"""
        try:
            # Process all CSV files for this subject
            subject_data = self.csv_processor.process_subject_data(subject_id)

            if not subject_data:
                print(f"No data processed for subject {subject_id}")
                return False

            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert performance records for each test type
            for test_type, metrics in subject_data.items():
                if metrics:
                    try:
                        cursor.execute("""
                            INSERT INTO Performance (user_id, power_max, hr_max, vo2_max, rf_max, cadence_max)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            user_id,
                            metrics.get("power_max", 0),
                            metrics.get("hr_max", 0),
                            metrics.get("vo2_max", 0),
                            metrics.get("rf_max", 0),
                            metrics.get("cadence_max", 0)
                        ))

                        print(f"Inserted {test_type} performance data for user {user_id}")

                    except Exception as e:
                        print(f"Error inserting {test_type} data for user {user_id}: {str(e)}")
                        continue

            conn.commit()
            conn.close()

            print(f"Successfully processed performance data for subject {subject_id}")
            return True

        except Exception as e:
            print(f"Error processing performance data for subject {subject_id}: {str(e)}")
            return False

    def process_single_subject(self, subject_id: str) -> Dict:
        """Process a single subject completely (user + athlete + performance)"""
        result = {
            "subject_id": subject_id,
            "user_created": False,
            "athlete_created": False,
            "performance_processed": False,
            "user_id": None,
            "errors": []
        }

        try:
            # Step 1: Create user
            user_id = self.create_user_for_subject(subject_id)
            if user_id:
                result["user_created"] = True
                result["user_id"] = user_id

                # Step 2: Create athlete profile
                if self.create_athlete_profile(user_id, subject_id):
                    result["athlete_created"] = True

                    # Step 3: Process and insert performance data
                    if self.process_and_insert_performance_data(user_id, subject_id):
                        result["performance_processed"] = True
                    else:
                        result["errors"].append("Failed to process performance data")
                else:
                    result["errors"].append("Failed to create athlete profile")
            else:
                result["errors"].append("Failed to create user")

        except Exception as e:
            result["errors"].append(f"Unexpected error: {str(e)}")

        return result

    def process_all_subjects(self) -> List[Dict]:
        """Process all subjects (1-7)"""
        results = []

        for subject_id in range(1, 8):  # sbj_1 through sbj_7
            print(f"\nProcessing subject {subject_id}...")
            result = self.process_single_subject(str(subject_id))
            results.append(result)

            # Print summary for this subject
            status = "✅ SUCCESS" if all([
                result["user_created"],
                result["athlete_created"],
                result["performance_processed"]
            ]) else "❌ FAILED"

            print(f"Subject {subject_id}: {status}")
            if result["errors"]:
                for error in result["errors"]:
                    print(f"  - {error}")

        return results

    def get_processing_summary(self, results: List[Dict]) -> Dict:
        """Generate a summary of the processing results"""
        total_subjects = len(results)
        successful_subjects = sum(1 for r in results if all([
            r["user_created"], r["athlete_created"], r["performance_processed"]
        ]))

        total_users_created = sum(1 for r in results if r["user_created"])
        total_athletes_created = sum(1 for r in results if r["athlete_created"])
        total_performance_processed = sum(1 for r in results if r["performance_processed"])

        all_errors = []
        for result in results:
            all_errors.extend(result["errors"])

        return {
            "total_subjects": total_subjects,
            "successful_subjects": successful_subjects,
            "success_rate": f"{successful_subjects}/{total_subjects}",
            "users_created": total_users_created,
            "athletes_created": total_athletes_created,
            "performance_records_processed": total_performance_processed,
            "total_errors": len(all_errors),
            "errors": all_errors[:10]  # Show first 10 errors
        }

    def _hash_password(self, password: str) -> str:
        """Simple password hashing for testing purposes"""
        # In production, use proper password hashing like bcrypt
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_data_integrity(self) -> Dict:
        """Verify that all data relationships are correct"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check user count
            cursor.execute("SELECT COUNT(*) FROM User WHERE user_name LIKE 'sbj_%'")
            user_count = cursor.fetchone()[0]

            # Check athlete count
            cursor.execute("SELECT COUNT(*) FROM Athlete")
            athlete_count = cursor.fetchone()[0]

            # Check performance count
            cursor.execute("SELECT COUNT(*) FROM Performance")
            performance_count = cursor.fetchone()[0]

            # Check for orphaned records
            cursor.execute("""
                SELECT COUNT(*) FROM Athlete a
                LEFT JOIN User u ON a.user_id = u.id
                WHERE u.id IS NULL
            """)
            orphaned_athletes = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM Performance p
                LEFT JOIN User u ON p.user_id = u.id
                WHERE u.id IS NULL
            """)
            orphaned_performances = cursor.fetchone()[0]

            conn.close()

            return {
                "users": user_count,
                "athletes": athlete_count,
                "performances": performance_count,
                "orphaned_athletes": orphaned_athletes,
                "orphaned_performances": orphaned_performances,
                "data_integrity_ok": (orphaned_athletes == 0 and orphaned_performances == 0)
            }

        except Exception as e:
            return {"error": str(e)}
