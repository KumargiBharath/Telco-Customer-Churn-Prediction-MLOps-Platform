# src/pipelines/retrain_pipeline.py

import os
import sys
import logging
import pandas as pd
import yaml
import mlflow
from mlflow.tracking import MlflowClient
# 11
#To Run:"python src/pipelines/retrain_pipeline.py"
#Next Run:"mlflow ui"
# Setup project root path
# --- FIX: Go up two levels to reach the Project Root ---
# This adds 'C:\Users\vulli\Desktop\Customer-churn-prediction' to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import Project Modules
from src.monitoring.drift_check import check_for_drift
from src.models.train import run_training

# ... (Rest of your code remains the same) ...
# NOTE: Import your feature engineering function here if you have it.
# from src.features.build_features import process_data 

# Configuration
CONFIG_PATH = "config/config.yaml"
MODEL_NAME = "ChurnModel"

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_production_model_metric():
    """
    Retrieves the Recall of the current production model from MLflow.
    Returns 0.0 if no model is in production.
    """
    client = MlflowClient()
    try:
        versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        if not versions:
            logging.info("No model currently in production.")
            return 0.0
        
        run_id = versions[0].run_id
        run = client.get_run(run_id)
        
        # We compare based on RECALL because that's your optimization target
        metric_value = run.data.metrics.get("recall", 0.0)
        logging.info(f"Current Production Model Recall: {metric_value}")
        return metric_value
        
    except Exception as e:
        logging.error(f"Error fetching production model: {e}")
        return 0.0

def promote_model_to_production(run_id):
    """
    Registers the model in MLflow Model Registry and moves it to 'Production'.
    """
    client = MlflowClient()
    
    # 1. Register the model
    model_uri = f"runs:/{run_id}/model"
    
    # Check if model is already registered
    try:
        client.get_registered_model(MODEL_NAME)
    except:
        client.create_registered_model(MODEL_NAME)

    # Create a new version
    model_version = client.create_model_version(
        name=MODEL_NAME,
        source=model_uri,
        run_id=run_id
    )
    
    # 2. Archive existing production models
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    for v in versions:
        if v.current_stage == "Production":
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=v.version,
                stage="Archived"
            )

    # 3. Promote new model
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=model_version.version,
        stage="Production"
    )
    logging.info(f"Model version {model_version.version} promoted to Production.")

def main():
    logging.info("=== Starting Phase 12: Automated Retraining System ===")
    
    config = load_config()
    
    # --- 1. Load Data ---
    # In a real scenario, you might fetch new data from a DB or API.
    # Here we simulate loading reference (old) and current (new) CSVs.
    # You need to ensure these files exist or point to your actual data sources.
    
    # For demonstration, we use the paths from your config if they exist
    # Ideally, you should have a specific 'new_data' path.
    ref_path = config['data']['raw_data_path'] # Using raw as reference for example
    cur_path = "data/raw/new_data.csv" # You need to supply this file
    
    if not os.path.exists(cur_path):
        logging.warning(f"New data file not found at {cur_path}. Aborting retrain check.")
        return

    ref_df = pd.read_csv(ref_path)
    cur_df = pd.read_csv(cur_path)

    # --- 2. Check for Drift ---
    logging.info("Checking for data drift...")
    
    # Simple preprocessing for drift check (drop ID, handle numeric conversion)
    # You should match the preprocessing done in your validation script
    if 'customerID' in ref_df.columns: ref_df = ref_df.drop('customerID', axis=1)
    if 'customerID' in cur_df.columns: cur_df = cur_df.drop('customerID', axis=1)
    
    # Handle total charges string issue if present
    ref_df['TotalCharges'] = pd.to_numeric(ref_df['TotalCharges'], errors='coerce').fillna(0)
    cur_df['TotalCharges'] = pd.to_numeric(cur_df['TotalCharges'], errors='coerce').fillna(0)

    drift_detected = check_for_drift(ref_df, cur_df, threshold=0.1)
    
    if not drift_detected:
        logging.info("No drift detected. Pipeline finished.")
        return

    # --- DRIFT DETECTED ---
    logging.info("DRIFT DETECTED! Initiating retraining pipeline...")

    # --- 3. Retraining Prep ---
    # CRITICAL STEP: You must update your processed .npy files before training.
    # If you have a feature engineering script (e.g., src/features/build_features.py),
    # you must run it here to update the .npy files used by train.py.
    
    # Example:
    # logging.info("Running feature engineering on new data...")
    # process_data(ref_df.append(cur_df)) 
    
    # For now, we assume the .npy files in config['data']['processed_data_path'] 
    # have been updated manually or by another script.
    
    # --- 4. Run Training ---
    new_run_id, new_metrics = run_training()
    
    if not new_run_id:
        logging.error("Training failed.")
        return

    # --- 5. Validation Gate ---
    # Compare new model vs current production model
    current_prod_metric = get_production_model_metric()
    new_model_metric = new_metrics.get("recall", 0.0)
    
    logging.info(f"Validation -> Production Recall: {current_prod_metric} | New Model Recall: {new_model_metric}")

    if new_model_metric >= current_prod_metric:
        logging.info("New model performs equal or better. Promoting...")
        promote_model_to_production(new_run_id)
        
        # --- 6. Update Reference Data ---
        # The current data now becomes the reference for the next cycle
        # (Optional but recommended best practice)
        try:
            cur_df.to_csv(ref_path, index=False)
            logging.info("Reference data updated for next cycle.")
        except Exception as e:
            logging.error(f"Failed to update reference data: {e}")
        
    else:
        logging.warning("New model performance worse than production. Keeping old model.")

if __name__ == "__main__":
    main()