# src/models/experiment.py

import os
import yaml
import numpy as np
from loguru import logger
import sys
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
# 7
#To Run:"python src\models\experiment.py"
#Next Run:"mlflow ui"
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger.add("logs/experiment.log", rotation="10 MB")

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob)
    }

def main():
    logger.info("Starting Experiment Tracking with MLflow...")
    config = load_config()
    
    # Setup MLflow (Local Tracking)
    # This creates a 'mlruns' folder in your project root
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("churn_prediction_v1")
    
    # Load Data
    X_train = np.load(config['data']['train_data_path'].replace('.csv', '_x.npy'))
    y_train = np.load(config['data']['train_data_path'].replace('.csv', '_y.npy'))
    X_test = np.load(config['data']['test_data_path'].replace('.csv', '_x.npy'))
    y_test = np.load(config['data']['test_data_path'].replace('.csv', '_y.npy'))
    
    # Calculate weight for imbalance
    churn_counts = np.bincount(y_train.astype(int))
    scale_pos_weight = churn_counts[0] / churn_counts[1]
    
    # Define the optimized models we trained earlier
    models = {
        "LogisticRegression_Opt": LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
        "RandomForest_Opt": RandomForestClassifier(random_state=42, n_estimators=100, n_jobs=-1, class_weight='balanced'),
        "XGBoost_Opt": XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1, scale_pos_weight=scale_pos_weight)
    }
    
    # Training Loop with MLflow Logging
    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            logger.info(f"Logging run for {name}...")
            
            # Train
            model.fit(X_train, y_train)
            
            # Evaluate
            metrics = evaluate_model(model, X_test, y_test)
            
            # Log Parameters
            mlflow.log_param("model_type", name)
            mlflow.log_param("data_split", "80/20")
            
            # Log Metrics
            mlflow.log_metrics(metrics)
            
            # Log Model Artifact
            mlflow.sklearn.log_model(model, "model")
            
            logger.info(f"Run {name} logged. Recall: {metrics['recall']:.4f}")

    logger.success("Experiment Tracking Completed. Run 'mlflow ui' to view results.")

if __name__ == "__main__":
    main()