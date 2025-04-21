# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PredictionBase(BaseModel):
    soil_type: str
    ph: float
    rainfall_mm: float
    temperature_c: float
    humidity_percent: float
    seed_variety: str
    fertilizer_type: str
    planting_date: str

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    predicted_yield: float
    confidence: str
    recommendation: str
    user_id: int
    
    class Config:
        orm_mode = True