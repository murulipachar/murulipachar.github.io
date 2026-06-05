import os
import pandas as pd
import json

def convert_csv_to_js():
    csv_path = "e-commerce-bi-platform/dataset/ecommerce_data.csv"
    js_dir = "e-commerce-bi-platform/dashboard"
    js_path = os.path.join(js_dir, "data.js")
    
    print(f"Reading master CSV from {csv_path}...")
    if not os.path.exists(csv_path):
        print("Error: CSV file not found! Run generate_dataset.py first.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Fill NaN values to prevent JS errors
    df = df.fillna("")
    
    # Columns list to map indexes in the client dashboard
    columns = list(df.columns)
    
    # Values list to minimize size
    records = df.values.tolist()
    
    print(f"Loaded {len(records)} records. Writing to {js_path}...")
    os.makedirs(js_dir, exist_ok=True)
    
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// E-Commerce Business Intelligence Platform - Compressed Dataset\n")
        f.write(f"// Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"window.ECOMMERCE_COLUMNS = {json.dumps(columns)};\n")
        f.write(f"window.ECOMMERCE_DATA = {json.dumps(records)};\n")
        
    print("ETL Conversion complete! data.js created successfully.")

if __name__ == "__main__":
    convert_csv_to_js()
