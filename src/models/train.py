# src/models/train.py

import os
import json
import yaml
import joblib
import numpy as np
from loguru import logger
import sys
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
# 4
#To Run:"python src\models\train.py"
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Logging
logger.add("logs/train.log", rotation="10 MB", retention="5 days", level="INFO")

def load_config():
    """Load configuration from YAML file."""
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def evaluate_model(model, X_test, y_test):
    """Evaluates the model and returns a dictionary of metrics."""
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
        roc_auc = round(roc_auc_score(y_test, y_prob), 4)
    else:
        roc_auc = 0.0
        
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": roc_auc
    }
    return metrics

def run_training():
    """
    Main training logic callable by automation.
    Returns: (best_run_id, best_metrics_dict)
    """
    logger.info("Starting Optimized Model Training Pipeline...")
    
    # 1. Load Config
    config = load_config()
    
    # 2. Load Processed Data
    try:
        X_train = np.load(config['data']['train_data_path'].replace('.csv', '_x.npy'))
        y_train = np.load(config['data']['train_data_path'].replace('.csv', '_y.npy'))
        X_test = np.load(config['data']['test_data_path'].replace('.csv', '_x.npy'))
        y_test = np.load(config['data']['test_data_path'].replace('.csv', '_y.npy'))
        
        logger.info(f"Train Data: {X_train.shape}, Test Data: {X_test.shape}")
    except Exception as e:
        logger.error(f"Error loading processed data: {e}")
        return None, {}

    # Calculate scale_pos_weight for XGBoost
    churn_counts = np.bincount(y_train.astype(int))
    scale_pos_weight = churn_counts[0] / churn_counts[1]
    
    # 3. Define Models
    models = {
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
        "RandomForest": RandomForestClassifier(random_state=42, n_estimators=100, n_jobs=-1, class_weight='balanced'),
        "XGBoost": XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1, scale_pos_weight=scale_pos_weight)
    }
    
    best_model = None
    best_model_name = None
    best_recall = 0
    best_metrics = {}
    best_run_id = None
    
    # Set Experiment
    mlflow.set_experiment("Churn_Prediction_Auto_Retrain")

    # 4. Train and Evaluate
    for name, model in models.items():
        with mlflow.start_run(run_name=name) as run:
            logger.info(f"Training {name}...")
            
            # Train
            model.fit(X_train, y_train)
            
            # Evaluate
            metrics = evaluate_model(model, X_test, y_test)
            logger.info(f"{name} Metrics: {metrics}")
            
            # Log to MLflow
            mlflow.log_param("model_type", name)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, "model")
            
            # Selection Logic (Optimizing for Recall)
            if metrics['recall'] > best_recall:
                best_recall = metrics['recall']
                best_model = model
                best_model_name = name
                best_metrics = metrics
                best_run_id = run.info.run_id

    logger.success(f"Best Model: {best_model_name} with Recall: {best_recall}")
    
    # 5. Save the Best Model Locally (For API)
    os.makedirs("models", exist_ok=True)
    model_path = "models/best_model.joblib"
    joblib.dump(best_model, model_path)
    logger.success(f"Best model saved to {model_path}")
    
    # 6. Save Metrics Report
    report = {
        "best_model": best_model_name,
        "metrics": best_metrics,
        "run_id": best_run_id
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/training_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    return best_run_id, best_metrics

def main():
    run_training()
    logger.success("Optimized Model Training Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()