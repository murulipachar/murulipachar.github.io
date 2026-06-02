import os
import sqlite3
import pandas as pd
import json

def df_to_markdown(df):
    """Robust utility to convert a Pandas DataFrame to Markdown table format."""
    headers = list(df.columns)
    divider = ["---"] * len(headers)
    markdown_lines = [
        "| " + " | ".join(map(str, headers)) + " |",
        "| " + " | ".join(divider) + " |"
    ]
    for _, row in df.iterrows():
        # Replace newlines and pipe characters to avoid breaking Markdown formatting
        row_vals = [str(x).replace('\n', ' ').replace('|', '\\|') for x in row]
        markdown_lines.append("| " + " | ".join(row_vals) + " |")
    return "\n".join(markdown_lines)

def run_data_pipeline():
    print("--------------------------------------------------")
    print("STARTING DATA ANALYTICS PIPELINE...")
    print("--------------------------------------------------")
    
    # 1. Load Raw Data
    raw_path = 'dataset/raw_superstore_sales.csv'
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw CSV not found at {raw_path}. Run generate_data.py first.")
        
    print(f"Loading raw dataset from: {raw_path}")
    df = pd.read_csv(raw_path)
    
    # 2. Data Cleaning and Preprocessing
    print("Cleaning and preprocessing data...")
    # Check for missing values
    null_counts = df.isnull().sum().sum()
    if null_counts > 0:
        print(f"Warning: Found {null_counts} null values. Filling with appropriate defaults.")
        df = df.fillna({
            'Sales': 0.0,
            'Profit': 0.0,
            'Quantity': 1,
            'Discount': 0.0,
            'Postal Code': '00000'
        })
    
    # Format datatypes
    df['Order Date'] = pd.to_datetime(df['Order Date']).dt.strftime('%Y-%m-%d')
    df['Ship Date'] = pd.to_datetime(df['Ship Date']).dt.strftime('%Y-%m-%d')
    df['Sales'] = df['Sales'].astype(float).round(2)
    df['Profit'] = df['Profit'].astype(float).round(2)
    df['Quantity'] = df['Quantity'].astype(int)
    df['Discount'] = df['Discount'].astype(float).round(2)
    
    # Save cleaned dataset
    clean_path = 'dataset/cleaned_superstore_sales.csv'
    df.to_csv(clean_path, index=False)
    print(f"Cleaned dataset saved to: {clean_path}")
    
    # 3. SQLite Database Setup & Populating
    db_path = 'dataset/superstore.db'
    print(f"Connecting to SQLite Database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load and execute schema
    schema_path = 'sql/schema.sql'
    print(f"Running database schema script: {schema_path}")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    
    # Insert data (replace table if already exists for a clean pipeline run)
    # Rename columns to match database schema names (lowercase, underscores)
    df_db = df.copy()
    df_db.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df_db.columns]
    
    print("Populating database with preprocessed sales data...")
    df_db.to_sql('sales', conn, if_exists='replace', index=False)
    conn.commit()
    print("Database populated successfully.")
    
    # 4. Execute SQL Queries & Write Report
    print("Executing analytical SQL scripts and compiling reports...")
    sql_files = [
        ('01_kpi_summary.sql', 'Executive Summary Metrics'),
        ('02_monthly_sales_trend.sql', 'Monthly Sales & MoM Growth Trends'),
        ('03_category_analysis.sql', 'Category & Sub-Category Sales & Margin Breakdown'),
        ('04_region_wise_analysis.sql', 'Regional Market Volume & Profitability'),
        ('05_customer_segmentation.sql', 'Demographic Segmentation & Average Order Value (AOV)'),
        ('06_top_bottom_products.sql', 'Product Performance: Top 10 Profitable vs Bottom 5 Unprofitable SKUs'),
        ('07_profitability_analysis.sql', 'Impact Analysis of Promotional Discount Levels on Profit Margins')
    ]
    
    report_markdown = []
    report_markdown.append("# Executive Relational SQL Analytics Report")
    report_markdown.append("Generated automatically by the Superstore Sales data pipeline.")
    report_markdown.append(f"**Date Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_markdown.append("\n---\n")
    
    for filename, title in sql_files:
        sql_path = f"sql/{filename}"
        print(f"Running SQL Script: {sql_path}...")
        
        with open(sql_path, 'r') as f:
            query = f.read()
            
        try:
            res_df = pd.read_sql_query(query, conn)
            
            report_markdown.append(f"## {title}")
            report_markdown.append(f"*Source SQL script: [{filename}](../sql/{filename})*")
            report_markdown.append("\n" + df_to_markdown(res_df) + "\n")
            report_markdown.append("\n---\n")
        except Exception as e:
            print(f"Error running script {filename}: {e}")
            report_markdown.append(f"## {title} (Error)")
            report_markdown.append(f"Error executing query from `{filename}`: `{e}`")
            report_markdown.append("\n---\n")
            
    # Save Report
    os.makedirs('reports', exist_ok=True)
    report_path = 'reports/sql_report_results.md'
    with open(report_path, 'w') as f:
        f.write("\n".join(report_markdown))
    print(f"Executive Analysis Report compiled and saved to: {report_path}")
    
    # 5. Export Preprocessed JS Data for Interactive Frontend (Bypassing CORS on file://)
    print("Preparing and exporting lightweight JS data feed for Dashboard...")
    # Export only essential columns to keep JSON payload very light for browser speed
    compact_df = df[[
        'Category', 'Sub-Category', 'Region', 'Segment', 
        'Order Date', 'Sales', 'Profit', 'Quantity', 'Discount', 'Product Name', 'Order ID', 'Customer ID'
    ]].copy()
    
    # Rename columns to short keys to further minimize file size
    compact_df.columns = ['cat', 'sub', 'reg', 'seg', 'date', 'sales', 'profit', 'qty', 'disc', 'prod', 'ord', 'cust']
    
    # Sort by date
    compact_df = compact_df.sort_values('date')
    
    # Convert to dictionary array
    compact_records = compact_df.to_dict(orient='records')
    
    # Write to dashboard directory as a JS file to bypass browser CORS constraints
    os.makedirs('dashboard', exist_ok=True)
    js_path = 'dashboard/data.js'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("const superstoreData = ")
        json.dump(compact_records, f, indent=2)
        f.write(";\n")
        
    print(f"Frontend JS dataset successfully exported: {js_path} (Size: {round(os.path.getsize(js_path)/1024, 2)} KB)")
    
    # Close db connection
    conn.close()
    
    print("\n--------------------------------------------------")
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("--------------------------------------------------")

if __name__ == '__main__':
    run_data_pipeline()
