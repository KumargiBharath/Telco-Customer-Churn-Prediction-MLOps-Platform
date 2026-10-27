# src/data/ingestion.py

import os
import requests
import pandas as pd
from loguru import logger
import yaml
import sys
# 1
#To Run:"python src\data\ingestion.py"
# Setup paths to allow imports from src if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Logging
# This creates a 'logs' folder if it doesn't exist and saves a .log file
logger.add("logs/ingestion.log", rotation="10 MB", retention="5 days", level="INFO")

def load_config():
    """Load configuration from YAML file."""
    try:
        with open("config/config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Config file not found at config/config.yaml")
        raise

def download_data(url: str, save_path: str):
    """
    Download dataset from a URL if it doesn't already exist locally.
    Uses streaming to handle large files efficiently.
    """
    if os.path.exists(save_path):
        logger.info(f"Data file already exists at: {save_path}")
        return

    logger.info(f"Downloading data from: {url}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Stream download to handle large files efficiently
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise error for bad status codes (404, 500, etc.)
        
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.success(f"Data successfully downloaded to: {save_path}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error downloading data: {e}")
        raise

def read_data(file_path: str) -> pd.DataFrame:
    """
    Read the CSV file into a Pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Data loaded successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise

def main():
    """
    Main execution function for the Data Ingestion Pipeline.
    """
    logger.info("Starting Data Ingestion Pipeline...")
    
    # 1. Load Config
    config = load_config()
    
    # 2. Get Parameters from Config
    raw_path = config['data']['raw_data_path']
    data_url = config['data']['source_url']
    
    # 3. Download Data
    download_data(data_url, raw_path)
    
    # 4. Verify Data (Read and Log basic stats)
    df = read_data(raw_path)
    
    logger.info(f"Columns found: {df.columns.tolist()}")
    logger.success("Data Ingestion Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()