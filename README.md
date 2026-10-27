# 📉 Telco Customer Churn Prediction & MLOps Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14%2B-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2.svg)](https://mlflow.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.0%2B-38B2AC.svg)](https://tailwindcss.com/)
[![Evidently](https://img.shields.io/badge/Evidently-Drift%20Monitoring-000000.svg)](https://docs.evidentlyai.com/)

A full-stack, production-grade Machine Learning application designed to predict telecommunications customer churn. This project bridges the gap between data science and software engineering by combining a robust **Python MLOps pipeline** (data ingestion, validation, training, drift detection, and automated retraining) with a modern, responsive **Next.js frontend** (single/batch predictions, real-time analytics, and dark mode).

---

## 📋 Table of Contents

1. [Problem Statement & Objectives](#problem-statement)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation)
6. [Execution Guide](#execution)
7. [API Documentation](#api-documentation)
8. [MLOps & Monitoring](#mlops)
9. [Future Improvements](#future-improvements)

---

## 🎯 Problem Statement & Objectives

### Business Objective
The business is losing revenue due to customer attrition. Current retention strategies are reactive and lack personalization. 
1. **Goal:** Reduce monthly churn rate by identifying at-risk customers early.
2. **Action:** Trigger targeted retention workflows for customers flagged as `Churn = 1`.
3. **KPI:** Customer Lifetime Value (CLV) retention and Campaign ROI.

### Machine Learning Objective
1. **Task:** Binary Classification (Churn vs. No Churn).
2. **Optimization Target:** **Maximize Recall** to capture the maximum number of actual churners.
3. **Constraint:** Maintain Precision above a usable threshold to avoid wasting marketing resources on false positives.
4. **Output:** Prediction label (0/1) and Probability Score (0.0 to 1.0).

---

## ✨ Key Features

### 🧠 Machine Learning & MLOps
1. **Automated Pipeline:** Modular scripts for ingestion, validation, feature engineering, training, and evaluation.
2. **Imbalanced Data Handling:** Optimized for Recall using `class_weight='balanced'` and XGBoost `scale_pos_weight`.
3. **Explainability (XAI):** Automated SHAP summary and feature importance plots for model interpretability.
4. **Drift Detection:** Evidently AI integration to monitor data drift between reference and current datasets.
5. **Automated Retraining:** A gating pipeline that checks for drift, retrains models, compares Recall against the production baseline, and promotes the best model via MLflow Model Registry.

### 💻 Frontend & User Experience
1. **Modern UI:** Built with Next.js 14 (App Router), React, and Tailwind CSS.
2. **Dark/Light Mode:** Seamless theme toggling with persistent local storage.
3. **Dual Prediction Modes:** 
  3.1 **Single Prediction:** Interactive form with real-time validation.
  3.2 **Batch Processing:** CSV upload support (via `papaparse`) for bulk customer analysis.
4. **Real-time Analytics:** Interactive Pie and Bar charts (via `recharts`) visualizing session history and churn distribution.
5. **Explainable UI:** Dynamic "Key Risk Factors" display based on customer input.
6. **Local Authentication:** Secure, session-based mock authentication using React Context API.

---

## 🛠️ Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS, Recharts, PapaParse, Lucide React |
| **Backend API** | FastAPI, Uvicorn, Pydantic, Python-Multipart |
| **Core Data Science** | Pandas, NumPy, Scikit-Learn, XGBoost, SciPy |
| **MLOps & Tracking** | MLflow, Joblib |
| **Data Validation & Monitoring** | Evidently AI |
| **Configuration & Utils** | PyYAML, Python-Dotenv, Loguru, Requests |

---

## 📂 Project Structure
```text
├── app/                          # Next.js Frontend
│   ├── components/               # React components (AuthPage.tsx, Dashboard.tsx)
│   ├── context/                  # AppContext.tsx (Auth & Theme state management)
│   ├── globals.css               # Tailwind CSS & global styles
│   ├── layout.tsx                # Root layout with AppProvider
│   └── page.tsx                  # Main routing logic (Auth vs. Dashboard)
├── src/                          # Python Backend & MLOps Pipeline
│   ├── data/                     # ingestion.py, validation.py
│   ├── features/                 # engineering.py (Cleaning, Scaling, OHE)
│   ├── models/                   # train.py, tuning.py, evaluate.py, experiment.py
│   ├── monitoring/               # drift_check.py, drift_detection.py
│   └── pipelines/                # retrain_pipeline.py (Automated gating)
├── config/
│   └── config.yaml               # Centralized configuration (paths, model params)
├── data/                         # Raw and processed datasets (.csv, .npy)
├── models/                       # Saved ML artifacts (preprocessor.joblib, best_model.joblib)
├── reports/                      # Generated artifacts (SHAP plots, drift_report.html)
├── create_drift_data.py          # Utility to generate synthetic drifted data for testing
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
└── README.md                     # You are here!
```

---

## ⚙️ Installation & Setup

## 1. Clone the Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

## 2. Backend Setup (Python)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```
### (Ensure requirements.txt includes: pandas, numpy, scikit-learn, xgboost, mlflow, fastapi, uvicorn, pydantic, loguru, pyyaml, evidently, shap, joblib, requests)

## 3. Frontend Setup (Next.js)
```bash
# Install Node.js dependencies
npm install
# or yarn install / pnpm install
```

---

## 🚀 Execution Guide
Run the backend pipeline and frontend server in separate terminal windows.
## Step 1: Run the MLOps Pipeline (Backend)
### Execute the pipeline steps sequentially from the project root:
```bash
# 1. Download Data
python src/data/ingestion.py

# 2. Validate Data
python src/data/validation.py

# 3. Feature Engineering (Creates preprocessor.joblib and .npy splits)
python src/features/engineering.py

# 4. Hyperparameter Tuning (Optimizes XGBoost for Recall)
python src/models/tuning.py

# 5. Train Models & Log to MLflow
python src/models/train.py

# 6. Generate SHAP Explainability Plots
python src/models/evaluate.py
```
## Step 2: Start the FastAPI Server
```bash
uvicorn app.main:app --reload
```
### The API will be available at http://localhost:8000.

---

## 📡 API Documentation
### The FastAPI backend exposes a single prediction endpoint. You can test it via the frontend or directly via Swagger UI at http://localhost:8000/docs.

## Example:
For POST /predict
### Request Body:
```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 1,
  "PhoneService": "No",
  "MultipleLines": "No phone service",
  "InternetService": "DSL",
  "OnlineSecurity": "No",
  "OnlineBackup": "Yes",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 29.85,
  "TotalCharges": 29.85
}
```
### Response:
```json
{
  "prediction": 1,
  "prediction_label": "Churn",
  "churn_probability": 0.8742
}
```

---

## 🔍 MLOps & Monitoring
### Experiment Tracking (MLflow)
All training runs are logged locally. To view the MLflow UI and compare model metrics:
```bash
mlflow ui
```
### Navigate to http://127.0.0.1:5000 to view the dashboard.
## Data Drift Detection & Automated Retraining
### The system uses Evidently AI to monitor data drift and trigger retraining.
1. Simulate Drift: Generate a synthetic dataset with altered patterns (e.g., inflated charges).
```bash
   python create_drift_data.py
```
2. Run Retraining Pipeline: This script checks for drift, retrains models, compares the new model's Recall against the current Production model in MLflow, and promotes it if it performs equally or better.
```bash
   python src/pipelines/retrain_pipeline.py
```
3. View Drift Report: Open reports/drift_report.html in your browser to see the interactive Evidently dashboard.

---

## 🗺️ Future Improvements
1. Containerization: Dockerize both the FastAPI backend and Next.js frontend for consistent, one-command deployment.
2. CI/CD: Set up GitHub Actions to run pytest and black on pull requests, and automate model retraining workflows.
3. Database Integration: Replace local CSV/JSON storage with PostgreSQL (via sqlalchemy) for user management and persistent prediction history.
4. Advanced Auth: Replace local storage mock auth with JWT/OAuth2 (e.g., NextAuth or Auth0).
5. Cloud Deployment: Deploy the API to AWS/GCP and the frontend to Vercel, with MLflow tracking pointing to a remote Databricks or AWS S3 backend.

---

## 📄 License
### This project is licensed under the MIT License. See the LICENSE file for details.

## Built with ❤️ for robust, production-ready, full-stack Machine Learning.
