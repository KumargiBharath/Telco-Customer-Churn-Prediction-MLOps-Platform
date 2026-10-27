# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
import os
import sys

# 8
#To Run:"uvicorn app.main:app --reload"
# Add src to path to import logger if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import CustomerData

app = FastAPI(
    title="Churn Prediction API",
    description="API for predicting customer churn",
    version="1.0"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and preprocessor
model = None
preprocessor = None

@app.on_event("startup")
def load_model():
    """
    Load the model and preprocessor when the API starts.
    """
    global model, preprocessor
    try:
        model = joblib.load("models/best_model.joblib")
        preprocessor = joblib.load("models/preprocessor.joblib")
        print("Model and Preprocessor loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.get("/")
def home():
    return {"message": "Churn Prediction API is running. Go to /docs for documentation."}

@app.post("/predict")
def predict(data: CustomerData):
    """
    Accepts customer data and returns churn prediction.
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # 1. Convert Pydantic model to DataFrame
    # We wrap input in a list because pandas expects a batch of rows
    input_data = pd.DataFrame([data.model_dump()])
    
    # 2. Preprocess the data
    # Note: The preprocessor expects the exact same columns as training
    try:
        processed_data = preprocessor.transform(input_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preprocessing Error: {e}")

    # 3. Predict
    prediction = model.predict(processed_data)[0]
    probability = model.predict_proba(processed_data)[0][1] # Probability of Churn (Class 1)

    # 4. Return Result
    return {
        "prediction": int(prediction),
        "prediction_label": "Churn" if prediction == 1 else "No Churn",
        "churn_probability": round(float(probability), 4)
    }