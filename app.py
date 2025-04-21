# app.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
import pickle
import os
from . import schemas, database, models, auth
from sqlalchemy.orm import Session
from datetime import timedelta

app = FastAPI()

# Load ML model
model_path = os.path.join(os.path.dirname(__file__), "models", "final_model.pkl")
with open(model_path, 'rb') as f:
    model = pickle.load(f)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict/", response_model=schemas.Prediction)
def predict(
    prediction_input: schemas.PredictionCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    # Prepare input data for model
    input_data = [
        [
            prediction_input.soil_type,
            prediction_input.ph,
            prediction_input.rainfall_mm,
            prediction_input.temperature_c,
            prediction_input.humidity_percent,
            prediction_input.seed_variety,
            prediction_input.fertilizer_type
        ]
    ]
    
    # Make prediction
    predicted_yield = model.predict(input_data)[0]
    
    # Determine confidence and recommendations
    if predicted_yield > 8:
        confidence = "high"
        recommendation = "Continue current practices, yield looks excellent."
    elif predicted_yield > 5:
        confidence = "moderate"
        recommendation = "Consider soil enrichment for better results."
    else:
        confidence = "low"
        recommendation = "Soil amendment and better irrigation needed."
    
    # Save prediction to database
    db_prediction = models.Prediction(
        **prediction_input.dict(),
        predicted_yield=predicted_yield,
        confidence=confidence,
        recommendation=recommendation,
        user_id=current_user.id
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction

@app.get("/predictions/", response_model=List[schemas.Prediction])
def get_predictions(
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    predictions = db.query(models.Prediction).filter(models.Prediction.user_id == current_user.id).all()
    return predictions

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user