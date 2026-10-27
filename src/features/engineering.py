# src/features/engineering.py

import os
import pandas as pd
import numpy as np
import yaml
import joblib
from loguru import logger
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
# 3
#To Run:"python src\features\engineering.py"
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Logging
logger.add("logs/engineering.log", rotation="10 MB", retention="5 days", level="INFO")

def load_config():
    """Load configuration from YAML file."""
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs basic data cleaning:
    - Convert TotalCharges to numeric.
    - Drop CustomerID (not useful for prediction).
    - Handle missing values.
    """
    logger.info("Starting Data Cleaning...")
    
    # 1. Fix TotalCharges (detected as string in Phase 5)
    # Coerce errors to NaN (empty strings become NaN)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    
    # Fill missing TotalCharges with 0 (assuming these are new customers with 0 tenure)
    df['TotalCharges'] = df['TotalCharges'].fillna(0)
    
    # 2. Drop CustomerID
    if 'customerID' in df.columns:
        df = df.drop('customerID', axis=1)
        logger.info("Dropped 'customerID' column.")
        
    # 3. Drop rows with any remaining missing values (if any)
    initial_rows = df.shape[0]
    df = df.dropna()
    if df.shape[0] < initial_rows:
        logger.warning(f"Dropped {initial_rows - df.shape[0]} rows with missing values.")
        
    return df

def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Target column 'Churn' to binary (0/1).
    """
    if 'Churn' in df.columns:
        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
        logger.info("Encoded target column 'Churn' to 1/0.")
    return df

def build_preprocessor(categorical_cols: list, numerical_cols: list):
    """
    Builds a Scikit-Learn ColumnTransformer for preprocessing.
    - Standardizes numerical features.
    - One-Hot Encodes categorical features.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ],
        remainder='passthrough' # Keep other columns if any
    )
    return preprocessor

def main():
    logger.info("Starting Feature Engineering Pipeline...")
    
    # 1. Load Config
    config = load_config()
    raw_path = config['data']['raw_data_path']
    processed_path = config['data']['processed_data_path']
    model_config = config['model']
    
    # 2. Load Raw Data
    try:
        df = pd.read_csv(raw_path)
        logger.info(f"Loaded raw data: {df.shape}")
    except Exception as e:
        logger.error(f"Failed to load raw data: {e}")
        return

    # 3. Clean Data
    df = clean_data(df)
    
    # 4. Encode Target
    df = encode_target(df)
    
    # 5. Split Features (X) and Target (y)
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    
    # Identify Column Types
    # We exclude the target column from features
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    
    logger.info(f"Numerical Columns: {numerical_cols}")
    logger.info(f"Categorical Columns: {categorical_cols}")

    # 6. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=model_config['test_size'], 
        random_state=model_config['random_state'],
        stratify=y # Ensure balanced split
    )
    logger.info(f"Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")

    # 7. Build and Fit Preprocessor
    preprocessor = build_preprocessor(categorical_cols, numerical_cols)
    
    # Fit on Training Data ONLY (to prevent data leakage)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test) # Only transform test data
    
    logger.info("Preprocessing complete (Scaling & Encoding).")

    # 8. Save Processed Data and Artifacts
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Save Datasets
    # We save as numpy arrays for efficiency, or convert back to DataFrame for readability
    # Let's save as arrays for performance
    np.save(config['data']['train_data_path'].replace('.csv', '_x.npy'), X_train_processed)
    np.save(config['data']['train_data_path'].replace('.csv', '_y.npy'), y_train)
    np.save(config['data']['test_data_path'].replace('.csv', '_x.npy'), X_test_processed)
    np.save(config['data']['test_data_path'].replace('.csv', '_y.npy'), y_test)
    
    logger.info(f"Processed data saved to {config['data']['processed_data_path']}")

    # Save Preprocessor Object (CRITICAL for Production API)
    os.makedirs("models", exist_ok=True)
    joblib.dump(preprocessor, "models/preprocessor.joblib")
    logger.success("Preprocessor object saved to models/preprocessor.joblib")
    
    logger.success("Feature Engineering Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()