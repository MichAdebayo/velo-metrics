from pydantic import BaseModel
from typing import Optional

class AthletePerformance(BaseModel):
    user_id: int
    power_max: float
    hr_max: int
    vo2_max: float
    rf_max: float
    cadence_max: float

class StatsResponse(BaseModel):
    strongest_athlete: int = None
    highest_vo2max: int = None
    best_power_weight_ratio: int = None

class AthleteInfo(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

class StatsResponseWithNames(BaseModel):
    strongest_athlete: Optional[AthleteInfo] = None
    highest_vo2max: Optional[AthleteInfo] = None
    best_power_weight_ratio: Optional[AthleteInfo] = None