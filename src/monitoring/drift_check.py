# src/monitoring/drift_check.py

import pandas as pd
import sys
import os

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def check_for_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame, threshold: float = 0.5) -> bool:
    """
    Returns True if dataset drift is detected, False otherwise.
    """
    # Initialize the Evidently Report
    data_drift_report = Report(metrics=[
        DataDriftPreset(drift_share=threshold),
    ])
    
    # Run the report
    data_drift_report.run(reference_data=reference_data, current_data=current_data)
    
    # Extract the result dictionary
    result = data_drift_report.as_dict()
    
    # Check the 'dataset_drift' key
    # Structure: metrics -> [0] -> result -> dataset_drift
    is_drift_detected = result['metrics'][0]['result']['dataset_drift']
    
    return is_drift_detected