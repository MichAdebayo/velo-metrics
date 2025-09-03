from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email: str
    password: str
    is_staff: int = Field(None)

    @field_validator('is_staff')
    def validate_is_staff(cls, v):
        if v not in [0, 1]:
            raise ValueError('is_staff must be either 1 or 0 of type int')
        return v

class UserRead(UserCreate): 
    id: int
    first_name: str
    last_name: str
    user_name: str
    email: str
    is_staff: int

class AthleteWithPerformance(BaseModel):
    id: int
    first_name: str
    last_name: str
    user_name: str
    email: str
    is_staff: int
    weight: float
    height: float