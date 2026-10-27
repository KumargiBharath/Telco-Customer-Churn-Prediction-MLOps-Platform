# create_drift_data.py
import pandas as pd
import numpy as np
import os
# 10
#To Run:"python create_drift_data.py"
print("Creating synthetic 'Drifted' data to test the pipeline...")

# 1. Load original data to keep the structure
original_path = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
if not os.path.exists(original_path):
    print("Error: Original data file not found.")
    exit()

df = pd.read_csv(original_path)

# 2. Simulate Drift (Change the data patterns)
# Example: Inflation hit, so monthly charges are much higher
df['MonthlyCharges'] = df['MonthlyCharges'] * 1.5 

# Example: Behavior change, tenure is now generally lower (newer customers)
df['tenure'] = np.random.randint(0, 12, size=len(df))

# 3. Save this as the "new_data.csv" the pipeline expects
output_path = "data/raw/new_data.csv"
df.to_csv(output_path, index=False)

print(f"SUCCESS: Drifted data saved to {output_path}")
print("Now run 'python src/pipelines/retrain_pipeline.py' to see the magic happen.")