# src/data/validation.py

import os
import pandas as pd
import json
import yaml
from loguru import logger
import sys
# 2
#To Run:"python src\data\validation.py"
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Logging
logger.add("logs/validation.log", rotation="10 MB", retention="5 days", level="INFO")

def load_config():
    """Load configuration from YAML file."""
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def validate_data(df: pd.DataFrame) -> dict:
    """
    Validates the dataframe against schema and quality checks.
    Returns a validation report dictionary.
    """
    logger.info("Starting Data Validation...")
    
    report = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "stats": {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "missing_values_total": int(df.isnull().sum().sum())
        }
    }

    # 1. Check Critical Columns
    expected_columns = ['customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents', 
                        'tenure', 'PhoneService', 'Contract', 'PaperlessBilling', 
                        'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn']
    
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        report['is_valid'] = False
        report['errors'].append(f"Missing columns: {missing_cols}")
        logger.error(f"Validation Failed: Missing columns {missing_cols}")
    
    # 2. Check Target Column for Nulls
    if 'Churn' in df.columns:
        null_count = df['Churn'].isnull().sum()
        if null_count > 0:
            report['is_valid'] = False
            report['errors'].append(f"Target column 'Churn' has {null_count} missing values.")
            logger.error("Target column 'Churn' has missing values.")
    
    # 3. Check for Duplicate Rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        report['warnings'].append(f"Found {duplicates} duplicate rows.")
        logger.warning(f"Found {duplicates} duplicate rows.")

    # 4. Specific Check: TotalCharges Type
    # In the Telco dataset, 'TotalCharges' is often loaded as an object (string) due to empty spaces.
    if 'TotalCharges' in df.columns:
        if df['TotalCharges'].dtype == 'object':
            # Attempt to convert to numeric to see how many errors exist
            coerced = pd.to_numeric(df['TotalCharges'], errors='coerce')
            nulls_in_conversion = coerced.isnull().sum() - df['TotalCharges'].isnull().sum()
            
            if nulls_in_conversion > 0:
                report['warnings'].append(f"TotalCharges has {nulls_in_conversion} non-numeric values (likely empty strings). Cleaning required in Phase 6.")
                logger.warning("TotalCharges contains non-numeric data. Cleaning required.")

    logger.info(f"Validation Finished. Status: {'PASSED' if report['is_valid'] else 'FAILED'}")
    return report

def save_report(report: dict, path: str = "reports/validation_report.json"):
    """Save the validation report to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=4)
    logger.info(f"Validation report saved to {path}")

def main():
    logger.info("Initializing Data Validation Pipeline...")
    
    # 1. Load Config
    config = load_config()
    raw_path = config['data']['raw_data_path']
    
    # 2. Load Raw Data
    try:
        df = pd.read_csv(raw_path)
        logger.info(f"Loaded raw data for validation: {df.shape}")
    except Exception as e:
        logger.error(f"Failed to load data for validation: {e}")
        return

    # 3. Run Validation
    report = validate_data(df)
    
    # 4. Save Report
    save_report(report)

    if report['is_valid']:
        logger.success("Data Validation Pipeline Completed Successfully.")
    else:
        logger.critical("Data Validation Pipeline Failed. Check reports.")

if __name__ == "__main__":
    main()