from pydantic import BaseModel

class AthleteCreate(BaseModel):
    user_id: int
    gender: str
    age: int
    weight: float
    height: float

