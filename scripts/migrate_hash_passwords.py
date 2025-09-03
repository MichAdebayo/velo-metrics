"""
Migration script to hash all plain text passwords in the User table.
Run this once to fix existing users.
"""
import sqlite3
import os
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.utils.security import hash_password

def get_db_path():
    return os.path.join(os.path.dirname(__file__), '..', 'cyclist_database.db')

def migrate_passwords():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM User")
    users = cursor.fetchall()
    updated = 0
    for user_id, password in users:
        # Heuristic: bcrypt hashes start with $2b$, pbkdf2_sha256 with $pbkdf2-sha256$
        if not (password.startswith("$2b$") or password.startswith("$pbkdf2-sha256$")):
            new_hash = hash_password(password)
            cursor.execute("UPDATE User SET password = ? WHERE id = ?", (new_hash, user_id))
            updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} user passwords.")

if __name__ == "__main__":
    migrate_passwords()
