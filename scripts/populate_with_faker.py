import sqlite3
import os
from faker import Faker
import random

def get_db_path():
    """Returns the path to the cyclist database file.

    This function constructs and returns the absolute path to the 'cyclist_database.db' file located one directory above the current script.

    Returns:
        str: The absolute path to the cyclist database file.
    """
    return os.path.join(os.path.dirname(__file__), '..', 'cyclist_database.db')

def populate_database(num_athletes=50):
    """Populates the database with fake athlete, user, and performance data.
    
    This function generates a specified number of fake athletes, users, and their associated performance records using the Faker library and inserts them into the database.

    Args:
        num_athletes (int, optional): The number of athlete records to generate. Defaults to 50.

    """
    fake = Faker()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    test_types = ['Wingate', 'Incremental', 'I', 'II']
    athlete_genders = ['male', 'female']

    is_staff = 0

    # Create users and athletes
    from backend.utils.security import hash_password
    for i in range(num_athletes):
        user_name = f"athlete_{i+1}"
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        password_plain = fake.password(length=10)
        password = hash_password(password_plain)
        # Check for duplicate user
        cursor.execute("SELECT id FROM User WHERE user_name = ?", (user_name,))
        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO User (user_name, first_name, last_name, email, password, is_staff)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_name, first_name, last_name, email, password, is_staff))
        user_id = cursor.lastrowid

        # Athlete profile
        gender = random.choice(athlete_genders)
        age = random.randint(18, 35)
        weight = round(random.uniform(55, 90), 1)
        height = round(random.uniform(160, 200), 1)

        cursor.execute("SELECT user_id FROM Athlete WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO Athlete (user_id, gender, age, weight, height)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, gender, age, weight, height))

        # Performance records
        for test_type in test_types:
            # Check for duplicate performance
            cursor.execute("""
                SELECT performance_id FROM Performance WHERE user_id = ? AND test_type = ?
            """, (user_id, test_type))
            if cursor.fetchone():
                continue
            power_max = round(random.uniform(250, 900), 2)
            hr_max = round(random.uniform(120, 210), 2)
            vo2_max = round(random.uniform(3000, 6000), 2)
            rf_max = round(random.uniform(30, 80), 2)
            cadence_max = round(random.uniform(80, 160), 2)
            cursor.execute("""
                INSERT INTO Performance (user_id, test_type, power_max, hr_max, vo2_max, rf_max, cadence_max)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, test_type, power_max, hr_max, vo2_max, rf_max, cadence_max))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_database(num_athletes=50)
