import os
import pandas as pd
import yaml
from loguru import logger
import sys
# 9
#To Run:"python src/monitoring/drift_detection.py"
# Correct imports for evidently 0.7.21
# We try to import the Preset first
try:
    from evidently import Report
    from evidently.metric_preset import DataDriftPreset
except ImportError:
    # Fallback if structure is slightly different
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger.add("logs/drift.log", rotation="10 MB")

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    logger.info("Starting Drift Monitoring Pipeline...")
    config = load_config()
    
    # 1. Load Raw Data
    try:
        raw_path = config['data']['raw_data_path']
        df = pd.read_csv(raw_path)
        logger.info(f"Loaded raw data: {df.shape}")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return

    # 2. Simulate Reference vs Current Data
    if 'customerID' in df.columns:
        df = df.drop('customerID', axis=1)
    
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
    
    reference_data = df.sample(frac=0.5, random_state=42)
    current_data = df.drop(reference_data.index)
    
    logger.info(f"Reference Data Shape: {reference_data.shape}")
    logger.info(f"Current Data Shape: {current_data.shape}")

    # 3. Run Evidently Report
    try:
        logger.info("Calculating Data Drift...")
        
        # Use the Preset (handles all columns automatically)
        drift_report = Report(metrics=[
            DataDriftPreset()
        ])
        
        drift_report.run(reference_data=reference_data, current_data=current_data)
        logger.info("Drift calculation complete.")
        
    except Exception as e:
        logger.error(f"Error generating drift report: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Save Report
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/drift_report.html"
    
    try:
        drift_report.save_html(report_path)
        logger.success(f"Drift Report saved to {report_path}")
        logger.success("Open the HTML file in your browser to view the dashboard.")
    except Exception as e:
        logger.error(f"Error saving report: {e}")

if __name__ == "__main__":
    main()