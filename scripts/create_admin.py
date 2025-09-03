#!/usr/bin/env python3
"""
Create a test admin in the project's sqlite database.

Usage:
  python scripts/create_admin.py

You can override defaults by setting environment variables:
  ADMIN_USER, ADMIN_PASS, ADMIN_EMAIL

The script is idempotent: if a user with the same user_name exists it will update
the password and is_staff flag.
"""
import os
import sys

# Ensure the backend package directory is first on sys.path so imports resolve
repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.database import initialize_database, get_db_connection
from backend.utils.security import hash_password

# Fallback hashing if passlib bcrypt fails
try:
    from passlib.handlers.pbkdf2 import pbkdf2_sha256
except ImportError:
    pbkdf2_sha256 = None


def ensure_user(conn, user_name, first_name, last_name, email, plain_password, is_staff):
    cur = conn.cursor()
    # Attempt to use the project's hash function first. If passlib is not
    # correctly configured (missing bcrypt backend), fall back to pbkdf2_sha256
    # so the script remains usable in dev envs.
    try:
        hashed = hash_password(plain_password)
    except Exception as e:
        if pbkdf2_sha256:
            hashed = pbkdf2_sha256.hash(plain_password)
        else:
            raise Exception(
                "No hashing backend available. Install passlib or bcrypt."
            ) from e
    if existing := cur.execute(
        "SELECT id FROM User WHERE user_name = ? OR email = ?",
        (user_name, email),
    ).fetchone():
        cur.execute(
            "UPDATE User SET first_name = ?, last_name = ?, email = ?, password = ?, is_staff = ? WHERE id = ?",
            (first_name, last_name, email, hashed, int(is_staff), existing[0]),
        )
        print(f"Updated user: {user_name} (id={existing[0]})")
    else:
        cur.execute(
            "INSERT INTO User (user_name, first_name, last_name, email, password, is_staff) VALUES (?, ?, ?, ?, ?, ?)",
            (user_name, first_name, last_name, email, hashed, int(is_staff)),
        )
        print(f"Created user: {user_name}")
    conn.commit()


def main():
    # Defaults
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "AdminPass123")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")

    # Ensure DB and tables exist
    initialize_database()

    conn = get_db_connection()
    try:
        ensure_user(conn, admin_user, "Admin", "User", admin_email, admin_pass, True)
    finally:
        conn.close()

    print("Done. Use the credentials above to log in via /token or the Streamlit UI.")


if __name__ == "__main__":
    main()
