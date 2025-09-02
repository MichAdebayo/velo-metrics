from fastapi import APIRouter, HTTPException, Depends
from ..models.user import UserCreate, UserRead
from ..utils.security import hash_password, get_current_user
from ..database import get_db_connection
import sqlite3

router = APIRouter(tags=["users"])  

@router.post("/register")
def register_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(user.password)
    try:
        cursor.execute(
            "INSERT INTO User (first_name, last_name, user_name, email, password, is_staff) VALUES (?, ?, ?, ?, ?, ?)",
            (user.first_name, user.last_name, user.user_name, user.email, hashed_password, int(user.is_staff))
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already exists") from e
    finally:
        conn.close()

@router.get("/user_info", response_model=UserRead)
def get_user(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's information.
    """
    return dict(current_user)

@router.get("/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Not authorized")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, user_name, email, is_staff FROM User")
    users = cursor.fetchall()
    conn.close()
    return users

@router.get("/users/by-username/{username}")
def get_user_by_username(username: str, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Not authorized")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, user_name, email, is_staff FROM User WHERE user_name = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Not authorized")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, user_name, email, is_staff FROM User WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Not authorized")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE User SET first_name = ?, last_name = ?, email = ?, is_staff = ? WHERE id = ?", (user.first_name, user.last_name, user.email, int(user.is_staff), user_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    conn.close()
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Not authorized")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    conn.close()
    return {"message": "User deleted successfully"}