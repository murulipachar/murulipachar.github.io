import os
import pandas as pd
import json

def convert_csv_to_js():
    csv_path = "banking-risk-loan-analytics/dataset/banking_risk_data.csv"
    js_dir = "banking-risk-loan-analytics/dashboard"
    js_path = os.path.join(js_dir, "data.js")
    
    print(f"Reading banking master CSV from {csv_path}...")
    if not os.path.exists(csv_path):
        print("Error: CSV file not found! Run generate_dataset.py first.")
        return
        
    df = pd.read_csv(csv_path)
    
    # We want a loan-level summary to keep data.js compact (~800KB instead of 25MB)
    print("Aggregating payment-level records to loan-level summaries for visual dashboard...")
    
    # Define aggregation columns
    loan_cols = [
        "Customer_ID", "Customer_Name", "Age", "Gender", "Occupation", "Monthly_Income", "Credit_Score", 
        "Loan_ID", "Loan_Type", "Loan_Amount", "Interest_Rate", "Term_Months", "Monthly_EMI", "Branch_Name", "Region", 
        "Loan_Application_Date", "Approval_Status", "Risk_Score", "Risk_Category", 
        "Default_Status", "Default_Amount", "Recovered_Amount"
    ]
    
    # Drop duplicates to get loan-level metadata
    df_loans = df[loan_cols].drop_duplicates(subset=["Loan_ID"]).copy()
    
    # Pre-calculate payment metrics per loan
    # Filter payments (non-null Payment_ID)
    df_payments = df[df["Payment_ID"].notnull()]
    
    if len(df_payments) > 0:
        # Aggregate metrics
        df_pay_agg = df_payments.groupby("Loan_ID").agg(
            Total_Payments_Due=("Payment_ID", "count"),
            Payment_Late_Count=("Payment_Status", lambda s: sum(s == "Late")),
            Payment_Missed_Count=("Payment_Status", lambda s: sum(s == "Missed")),
            Interest_Collected=("Interest_Component", lambda i: sum(df.loc[i.index, "Payment_Status"] != "Missed"))
        ).reset_index()
        
        # Merge back to loans
        df_loans = df_loans.merge(df_pay_agg, on="Loan_ID", how="left")
    else:
        df_loans["Total_Payments_Due"] = 0
        df_loans["Payment_Late_Count"] = 0
        df_loans["Payment_Missed_Count"] = 0
        df_loans["Interest_Collected"] = 0.0

    # Fill NaNs
    df_loans["Total_Payments_Due"] = df_loans["Total_Payments_Due"].fillna(0).astype(int)
    df_loans["Payment_Late_Count"] = df_loans["Payment_Late_Count"].fillna(0).astype(int)
    df_loans["Payment_Missed_Count"] = df_loans["Payment_Missed_Count"].fillna(0).astype(int)
    df_loans["Interest_Collected"] = df_loans["Interest_Collected"].fillna(0.0)
    
    # Columns list to map indexes in the client dashboard
    columns = list(df_loans.columns)
    
    # Values list to minimize size
    records = df_loans.values.tolist()
    
    print(f"Aggregated to {len(records)} loans. Writing to {js_path}...")
    os.makedirs(js_dir, exist_ok=True)
    
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// Banking Risk & Loan Analytics - Compressed Loan Dataset\n")
        f.write(f"// Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"window.BANKING_COLUMNS = {json.dumps(columns)};\n")
        f.write(f"window.BANKING_DATA = {json.dumps(records)};\n")
        
    print("ETL Conversion complete! data.js created successfully.")

if __name__ == "__main__":
    convert_csv_to_js()
