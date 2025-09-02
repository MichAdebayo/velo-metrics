from fastapi import APIRouter, Depends, HTTPException
from models.performance import AthletePerformance, StatsResponseWithNames #StatsResponse,
from database import get_db_connection
from utils.security import get_current_user  # Ensure oauth2_scheme is imported if needed elsewhere
import sqlite3
from typing import List

router = APIRouter(tags=["performance"])

@router.post("/add_performance")
async def add_performance(performance: List[AthletePerformance], current_user: dict = Depends(get_current_user)):
    """
    Adds a performance record for the authenticated user.
    """
    # Ensure only an admin can perform a mass insert
    if not dict(current_user).get("is_staff", 0):
        raise HTTPException(status_code=403, detail="Not authorized to add performance records")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
            for perf in performance:
                try:
                    cursor.execute(
                        """
                        INSERT INTO Performance (user_id, power_max, hr_max, vo2_max, rf_max, cadence_max) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            perf.user_id,
                            perf.power_max,
                            perf.hr_max,
                            perf.vo2_max,
                            perf.rf_max,
                            perf.cadence_max
                        )
                    )
                except sqlite3.Error as e: # Handle errors for each insertion
                    print("Database error:", e)
                    raise HTTPException(status_code=400, detail=f"Database error: {e}") from e
            conn.commit() # Commit outside the loop
            return {"message": "Performance added successfully"} # Return after the loop
    except sqlite3.Error as e: # Handle any other errors
            raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close() # Close connection after all operations

@router.patch("/edit_performance/{performance_id}")
async def update_performance(performance_id: int, performance: AthletePerformance, current_user: dict = Depends(get_current_user)):
    """
    Updates a performance record if it belongs to the authenticated user.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Performance 
            SET power_max = ?, hr_max = ?, vo2_max = ?, rf_max = ?, cadence_max = ?
            WHERE performance_id = ? AND user_id = ?
            """,
            (
                performance.power_max,
                performance.hr_max,
                performance.vo2_max,
                performance.rf_max,
                performance.cadence_max,
                performance_id,
                current_user['id']
            )
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Performance not found or you don't have permission to update")
        return {"message": "Performance updated successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()

@router.delete("/delete_performance/{performance_id}")
async def delete_performance(performance_id: int, current_user: dict = Depends(get_current_user)):
    """
    Deletes a performance record if it belongs to the authenticated user.
    Only an admin can delete a performance record.
    """
    # Ensure only an admin can perform deletion
    if not dict(current_user).get("is_staff", 0):
        raise HTTPException(status_code=403, detail="Not authorized to delete performance records")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM Performance WHERE performance_id = ?",
            (performance_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Performance not found or you don't have permission to delete")
        return {"message": "Performance deleted successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()


@router.get("/stats", response_model=StatsResponseWithNames)
def get_stats(current_user: dict = Depends(get_current_user)):
    """Retrieves performance statistics based on user role."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        stats = {}

        def get_username(user_id):
            user = cursor.execute("SELECT user_name FROM User WHERE id = ?", (user_id,)).fetchone()
            return user["user_name"] if user else None

        if current_user.get("is_staff", 1):  # Admin/staff user
            strongest = cursor.execute(
                """
                SELECT user_id 
                FROM Performance 
                WHERE power_max = (SELECT MAX(power_max) FROM Performance WHERE user_id IN (SELECT id FROM User WHERE is_staff = 0))
                """
            ).fetchone()

            highest_vo2max = cursor.execute(
                """
                SELECT user_id 
                FROM Performance 
                WHERE vo2_max = (SELECT MAX(vo2_max) FROM Performance WHERE user_id IN (SELECT id FROM User WHERE is_staff = 0))
                """
            ).fetchone()

            best_ratio = cursor.execute(
                """
                SELECT P.user_id 
                FROM Performance P 
                INNER JOIN Athlete A ON P.user_id = A.user_id
                WHERE (P.power_max * 1.0 / A.weight) = (
                    SELECT MAX(P1.power_max * 1.0 / A1.weight) 
                    FROM Performance P1 
                    INNER JOIN Athlete A1 ON P1.user_id = A1.user_id 
                    WHERE P1.user_id IN (SELECT id FROM User WHERE is_staff = 0)
                )
                """
            ).fetchone()
        else:  # Athlete user
            user_id = current_user.get("id")

            strongest = cursor.execute(
                "SELECT user_id FROM Performance WHERE user_id = ? ORDER BY power_max DESC LIMIT 1",
                (user_id,)
            ).fetchone()

            highest_vo2max = cursor.execute(
                "SELECT user_id FROM Performance WHERE user_id = ? ORDER BY vo2_max DESC LIMIT 1",
                (user_id,)
            ).fetchone()

            best_ratio = cursor.execute(
                """
                SELECT P.user_id 
                FROM Performance P 
                INNER JOIN Athlete A ON P.user_id = A.user_id 
                WHERE P.user_id = ? 
                ORDER BY P.power_max * 1.0 / A.weight DESC 
                LIMIT 1
                """, 
                (user_id,)
            ).fetchone()

        # Check for None before accessing [0]
        stats["strongest_athlete"] = get_username(strongest[0]) if strongest else None
        stats["highest_vo2max"] = get_username(highest_vo2max[0]) if highest_vo2max else None
        stats["best_power_weight_ratio"] = get_username(best_ratio[0]) if best_ratio else None

        return stats
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()



# @router.get("/stats", response_model=StatsResponseWithNames)
# def get_stats(current_user: dict = Depends(get_current_user)):
#     """
#     Retrieves performance statistics.
    
#     - If the current user is admin/staff (is_staff=1):  
#       Returns aggregated stats for all athlete (non-staff) users:
#         * Strongest athlete (highest power_max)
#         * Athlete with highest VO₂max
#         * Athlete with best power-to-weight ratio
      
#     - If the current user is an athlete (is_staff=0):  
#       Returns aggregated stats based solely on the current user's performance records.
#     """
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         stats = {}
        
#         # Helper to get username (for admin case)
#         def get_username(user_id):
#             user = conn.execute("SELECT user_name FROM User WHERE id = ?", (user_id,)).fetchone()
#             return user["user_name"] if user else None

#         if current_user.get("is_staff", 0):
#             # Admin: aggregate stats for all athletes (non-staff users)
#             strongest = cursor.execute(
#                 """
#                 SELECT P.user_id, MAX(P.power_max) AS max_power 
#                 FROM Performance P 
#                 INNER JOIN User U ON P.user_id = U.id 
#                 WHERE U.is_staff = 0
#                 GROUP BY P.user_id 
#                 ORDER BY power_max DESC 
#                 LIMIT 1
#                 """
#             ).fetchone()
#             stats["strongest_athlete"] = get_username(strongest["user_id"]) if strongest else None

#             highest_vo2max = cursor.execute(
#                 """
#                 SELECT P.user_id, MAX(P.vo2_max) AS max_oxygen 
#                 FROM Performance P 
#                 INNER JOIN User U ON P.user_id = U.id 
#                 WHERE U.is_staff = 0
#                 GROUP BY P.user_id 
#                 ORDER BY vo2_max DESC 
#                 LIMIT 1
#                 """
#             ).fetchone()
#             stats["highest_vo2max"] = get_username(highest_vo2max["user_id"]) if highest_vo2max else None

#             best_ratio = cursor.execute(
#                 """
#                 SELECT P.user_id, MAX(P.power_max * 1.0 / A.weight) AS ratio 
#                 FROM Performance P 
#                 INNER JOIN Athlete A ON P.user_id = A.user_id 
#                 INNER JOIN User U ON P.user_id = U.id 
#                 WHERE U.is_staff = 0
#                 GROUP BY P.user_id 
#                 ORDER BY ratio DESC 
#                 LIMIT 1
#                 """
#             ).fetchone()
#             stats["best_power_weight_ratio"] = get_username(best_ratio["user_id"]) if best_ratio else None
#         else:
#             # Athlete: aggregate stats only for the current user's performance records.
#             user_id = current_user["id"]
#             # Since we're filtering by a single user, the "max" value is computed over that user's records.
#             strongest = cursor.execute(
#                 "SELECT MAX(power_max) AS max_power FROM Performance WHERE user_id = ?",
#                 (user_id,)
#             ).fetchone()
#             # Here, since it's only for the current user, we use their username
#             stats["strongest_athlete"] = current_user.get("user_name", "Unknown")
            
#             highest_vo2max = cursor.execute(
#                 "SELECT MAX(vo2_max) AS max_oxygen FROM Performance WHERE user_id = ?",
#                 (user_id,)
#             ).fetchone()
#             stats["highest_vo2max"] = current_user.get("user_name", "Unknown")
            
#             best_ratio = cursor.execute(
#                 """
#                 SELECT MAX(power_max * 1.0 / A.weight) AS ratio 
#                 FROM Performance P 
#                 INNER JOIN Athlete A ON P.user_id = A.user_id 
#                 WHERE P.user_id = ?
#                 """,
#                 (user_id,)
#             ).fetchone()
#             stats["best_power_weight_ratio"] = current_user.get("user_name", "Unknown")
        
#         return stats
#     except sqlite3.Error as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
#     finally:
#         conn.close()




# @router.get("/all_users")
# def get_all_users():
#     """Récupère tous les utilisateurs pour déboguer"""
#     conn = get_db_connection()
#     try:
#         users = conn.execute("SELECT id, user_name, first_name, last_name FROM User").fetchall()
#         conn.close()
#         return [{"id": u["id"], "user_name": u["user_name"], 
#                 "name": f"{u['first_name']} {u['last_name']}"} for u in users]
#     except Exception as e:
#         conn.close()
#         return {"error": str(e)}


# @router.get("/user_name/{user_name}", response_model=List[PerformanceResponse])
# def get_user_performances_by_username(user_name: str, current_user=Depends(get_current_staff_user)):
#     conn = get_db_connection()
    
#     user = conn.execute(
#         "SELECT id FROM User WHERE user_name = ?",
#         (user_name,)
#     ).fetchone()
    
#     if not user:
#         conn.close()
#         raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
#     user_id = user["id"]
