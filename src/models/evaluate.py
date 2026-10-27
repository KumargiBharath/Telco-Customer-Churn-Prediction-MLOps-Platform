# src/models/evaluate.py

import os
import yaml
import joblib
import numpy as np
import matplotlib.pyplot as plt
from loguru import logger
import sys
import shap
# 6
#To Run:"python src\models\evaluate.py"
# Setup paths
#This will create the two images in reports folder
#1.feature_importance.png
#2.shap_summary.png
# Setup paths
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger.add("logs/evaluate.log", rotation="10 MB")

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    logger.info("Starting Model Evaluation & Explainability...")
    config = load_config()
    
    # 1. Load Model and Preprocessor
    try:
        model = joblib.load("models/best_model.joblib")
        preprocessor = joblib.load("models/preprocessor.joblib")
        logger.info(f"Loaded model type: {type(model).__name__}")
    except Exception as e:
        logger.error(f"Error loading artifacts: {e}")
        return

    # 2. Load Test Data
    X_test = np.load(config['data']['test_data_path'].replace('.csv', '_x.npy'))
    
    # 3. Get Feature Names and Clean Them
    feature_names = preprocessor.get_feature_names_out()
    clean_feature_names = [name.split('__')[-1] for name in feature_names]
    
    # 4. Generate SHAP Values
    logger.info("Calculating SHAP values... (this may take a moment)")
    
    model_type = str(type(model))
    
    # Use a sample of background data for speed
    background = shap.sample(X_test, 100)
    
    # STRATEGY: Use Generic Explainer for XGBoost to avoid 'base_score' parsing errors
    # This is the most robust fix for version conflicts between XGBoost and SHAP.
    if "XGB" in model_type:
        logger.info("Using shap.Explainer (Model Agnostic) for XGBoost to ensure stability.")
        explainer = shap.Explainer(model.predict_proba, background)
        shap_values = explainer(X_test)
        
        # Note: Generic explainer returns shape (N, Features, Classes).
        # We need the SHAP values for the positive class (Index 1).
        # Check dimensions to be safe
        if len(shap_values.shape) == 3:
            shap_values_to_plot = shap_values[..., 1]
        else:
            shap_values_to_plot = shap_values
            
    elif "RandomForest" in model_type:
        logger.info("Detected RandomForest. Using shap.TreeExplainer.")
        explainer = shap.TreeExplainer(model)
        shap_values_to_plot = explainer.shap_values(X_test)
        # RF returns list of [class_0_values, class_1_values]
        if isinstance(shap_values_to_plot, list):
            shap_values_to_plot = shap_values_to_plot[1]
            
    else:
        # Fallback for Logistic Regression
        logger.info("Using generic shap.Explainer.")
        explainer = shap.Explainer(model, background)
        shap_values_to_plot = explainer(X_test)

    # 5. Plot Summary Plot (Detailed Beeswarm Plot)
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values_to_plot, features=X_test, feature_names=clean_feature_names, show=False)
    
    # Save Plot
    os.makedirs("reports", exist_ok=True)
    plot_path = "reports/shap_summary.png"
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    logger.success(f"SHAP Summary Plot saved to {plot_path}")
    
    # 6. Global Feature Importance (Bar Plot)
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values_to_plot, features=X_test, feature_names=clean_feature_names, plot_type="bar", show=False)
    
    importance_path = "reports/feature_importance.png"
    plt.savefig(importance_path, bbox_inches='tight')
    plt.close()
    logger.success(f"Feature Importance Plot saved to {importance_path}")
    
    logger.success("Evaluation Pipeline Completed.")

if __name__ == "__main__":
    main()