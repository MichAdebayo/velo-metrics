import sqlite3
import os
from .config import settings


def _db_path() -> str:
    """Resolve the database path from settings or fall back to a sane default.

    This ensures different modules use the same sqlite file rather than
    hardcoding different filenames across the repo.
    """
    if getattr(settings, "DATABASE_URL", None):
        # If DATABASE_URL is just a filename, resolve it relative to project root
        if not os.path.isabs(settings.DATABASE_URL):
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.DATABASE_URL)
        return settings.DATABASE_URL
    # fallback to a single default DB in the repo root
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "cyclist_database.db")


def get_db_connection():
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn


def create_user_table():
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS User(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_staff INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

def create_athlete_table():
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS Athlete(
            user_id INTEGER PRIMARY KEY,
            gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL,
            age INTEGER CHECK(age > 0) NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
        """
    )
    conn.commit()
    conn.close()


def create_performance_table():
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS Performance(
            performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, 
            power_max REAL NOT NULL,
            hr_max REAL NOT NULL,
            vo2_max REAL NOT NULL,
            rf_max REAL NOT NULL,
            cadence_max REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
        """
    )
    conn.commit()
    conn.close()


def initialize_database():
    create_user_table()
    create_athlete_table()
    create_performance_table()

def reset_database():
    db_path = _db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
    initialize_database()