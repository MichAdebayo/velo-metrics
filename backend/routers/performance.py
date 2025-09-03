from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..database import get_db_connection

from ..models.performance import AthletePerformance, StatsResponseWithNames
from ..utils.security import get_current_user

router = APIRouter()


# Get all performance records (for overall trends)
@router.get("/all_performances")
def get_all_performances(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Performance")
        performances = cursor.fetchall()
        conn.close()
        return [dict(row) for row in performances]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    
@router.post("/add_performance")
def add_performance(performances: List[AthletePerformance], current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for performance in performances:
            cursor.execute("""
                INSERT INTO Performance (user_id, power_max, hr_max, vo2_max, rf_max, cadence_max)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                performance.user_id,
                performance.power_max,
                performance.hr_max,
                performance.vo2_max,
                performance.rf_max,
                performance.cadence_max
            ))
        conn.commit()
        conn.close()
        return {"message": "Performance records added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/user/{user_id}")
def get_user_performances(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Performance WHERE user_id = ? ORDER BY performance_id DESC", (user_id,))
        performances = cursor.fetchall()
        conn.close()
        return [dict(row) for row in performances]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.patch("/{performance_id}")
def update_performance(performance_id: int, performance: AthletePerformance, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Performance
            SET power_max = ?, hr_max = ?, vo2_max = ?, rf_max = ?, cadence_max = ?
            WHERE performance_id = ?
        """, (
            performance.power_max,
            performance.hr_max,
            performance.vo2_max,
            performance.rf_max,
            performance.cadence_max,
            performance_id
        ))
        conn.commit()
        conn.close()
        return {"message": "Performance updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete("/{performance_id}")
def delete_performance(performance_id: int, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Performance WHERE performance_id = ?", (performance_id,))
        conn.commit()
        conn.close()
        return {"message": "Performance deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/stats")
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get strongest athlete
        cursor.execute("""
            SELECT u.id, u.user_name, u.first_name, u.last_name, p.power_max
            FROM Performance p
            JOIN User u ON p.user_id = u.id
            WHERE u.is_staff = 0
            ORDER BY p.power_max DESC
            LIMIT 1
        """)
        strongest = cursor.fetchone()

        # Get highest VO2 max
        cursor.execute("""
            SELECT u.id, u.user_name, u.first_name, u.last_name, p.vo2_max
            FROM Performance p
            JOIN User u ON p.user_id = u.id
            WHERE u.is_staff = 0
            ORDER BY p.vo2_max DESC
            LIMIT 1
        """)
        highest_vo2max = cursor.fetchone()

        # Get best power-to-weight ratio
        cursor.execute("""
            SELECT u.id, u.user_name, u.first_name, u.last_name, (p.power_max * 1.0 / a.weight) as ratio
            FROM Performance p
            JOIN User u ON p.user_id = u.id
            JOIN Athlete a ON p.user_id = a.user_id
            WHERE u.is_staff = 0
            ORDER BY ratio DESC
            LIMIT 1
        """)
        best_ratio = cursor.fetchone()

        conn.close()

        def make_athlete_info(row):
            if not row:
                return None
            return {
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3]
            }

        return StatsResponseWithNames(
            strongest_athlete=make_athlete_info(strongest),
            highest_vo2max=make_athlete_info(highest_vo2max),
            best_power_weight_ratio=make_athlete_info(best_ratio)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/user_name/{username}")
def get_performance_by_username(username: str, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user ID from username
        cursor.execute("SELECT id FROM User WHERE user_name = ?", (username,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_id = user[0]

        # Get performances
        cursor.execute("SELECT * FROM Performance WHERE user_id = ? ORDER BY performance_id DESC", (user_id,))
        performances = cursor.fetchall()
        conn.close()

        return [dict(row) for row in performances]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e