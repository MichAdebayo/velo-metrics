from fastapi import APIRouter, Depends, HTTPException
from ..models.athlete import AthleteCreate
from ..database import get_db_connection
from ..utils.security import get_current_user, oauth2_scheme
import sqlite3

router = APIRouter(prefix="/athletes", tags=["athletes"])

@router.post("/add_athlete")
async def add_athlete(athlete: AthleteCreate, token: str = Depends(oauth2_scheme)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Athlete (user_id, gender, age, weight, height) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (athlete.user_id, athlete.gender, athlete.age, athlete.weight, athlete.height)
        )
        conn.commit()
        return {"message": "Athlete added successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="User ID already exists or is not valid") from e
    finally:
        conn.close()

@router.patch("/edit_athlete/{user_id}")
async def update_athlete(user_id: int, athlete: AthleteCreate, current_user: dict = Depends(get_current_user)):
    # Validate that user_id matches current_user['id']
    if user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this athlete")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE Athlete 
            SET gender = ?, age = ?, weight = ?, height = ?
            WHERE user_id = ?
            """,
            (athlete.gender, athlete.age, athlete.weight, athlete.height, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Athlete not found")
        return {"message": "Athlete information updated successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()

@router.get("/get_athlete_details/{user_id}")
async def get_athlete(user_id: int, current_user: dict = Depends(get_current_user)):
    # Allow access if user is admin or accessing their own details
    if not current_user.get('is_staff', 0) and user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to access this athlete's details")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Athlete WHERE user_id = ?", (user_id,))
        if athlete_record := cursor.fetchone(): # Map athlete_record to a schema/dict before returning
            # sqlite3.Row is not JSON serializable directly; convert to dict
            return {"athlete": dict(athlete_record)}
        else:
            raise HTTPException(status_code=404, detail="Athlete details not found")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()

@router.delete("/delete_athlete/{user_id}")
async def delete_athlete(user_id: int, current_user: dict = Depends(get_current_user)):
    # Allow access if user is admin or accessing their own details
    if not current_user.get('is_staff', 0) and user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this athlete")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the athlete exists
        cursor.execute("SELECT * FROM Athlete WHERE user_id = ?", (user_id,))
        athlete_record = cursor.fetchone()
        if not athlete_record:
            raise HTTPException(status_code=404, detail="Athlete details not found")
        
        # Delete the athlete record
        cursor.execute("DELETE FROM Athlete WHERE user_id = ?", (user_id,))
        conn.commit()
        return {"message": "Athlete information deleted successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()
