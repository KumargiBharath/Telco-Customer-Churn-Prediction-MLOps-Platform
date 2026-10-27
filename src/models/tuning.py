# src/models/tuning.py

import os
import yaml
import joblib
import numpy as np
from loguru import logger
import sys
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, make_scorer
# 5
#To Run:"python src\models\tuning.py"
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger.add("logs/tuning.log", rotation="10 MB")

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    logger.info("Starting Hyperparameter Tuning for XGBoost...")
    config = load_config()
    
    # 1. Load Data
    X_train = np.load(config['data']['train_data_path'].replace('.csv', '_x.npy'))
    y_train = np.load(config['data']['train_data_path'].replace('.csv', '_y.npy'))
    X_test = np.load(config['data']['test_data_path'].replace('.csv', '_x.npy'))
    y_test = np.load(config['data']['test_data_path'].replace('.csv', '_y.npy'))
    
    # Calculate scale_pos_weight
    churn_counts = np.bincount(y_train.astype(int))
    scale_pos_weight = churn_counts[0] / churn_counts[1]

    # 2. Define Parameter Grid
    # We test different combinations of settings
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
        'scale_pos_weight': [scale_pos_weight]
    }

    # 3. Setup Grid Search
    # We optimize specifically for RECALL
    xgb = XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1)
    
    grid_search = GridSearchCV(
        estimator=xgb,
        param_grid=param_grid,
        scoring='recall',  # FOCUS ON RECALL
        cv=3,              # 3-fold cross-validation
        verbose=1,
        n_jobs=-1
    )

    logger.info("Fitting Grid Search... (This may take a minute)")
    
    # 4. Fit Model
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best Parameters found: {grid_search.best_params_}")
    
    # 5. Evaluate Best Model
    best_model = grid_search.best_estimator_
    
    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]
    
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4)
    }
    
    logger.info(f"Tuned XGBoost Metrics: {metrics}")

    # Compare with previous best (LogReg Recall was ~0.78)
    if metrics['recall'] > 0.78:
        logger.success("New Best Model Found! Saving...")
        joblib.dump(best_model, "models/best_model.joblib")
        logger.success("Updated best_model.joblib saved.")
    else:
        logger.info("Tuned XGBoost did not beat Logistic Regression. Keeping previous model.")

if __name__ == "__main__":
    main()