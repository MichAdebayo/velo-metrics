from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, UserRead
from utils.security import hash_password, get_current_user
from database import get_db_connection
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