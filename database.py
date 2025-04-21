# database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./instance/app.db"

# Ensure instance directory exists
os.makedirs(os.path.dirname(SQLALCHEMY_DATABASE_URL.split("///")[1]), exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    soil_type = Column(String)
    ph = Column(Float)
    rainfall_mm = Column(Float)
    temperature_c = Column(Float)
    humidity_percent = Column(Float)
    seed_variety = Column(String)
    fertilizer_type = Column(String)
    planting_date = Column(String)
    predicted_yield = Column(Float)
    confidence = Column(String)
    recommendation = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()