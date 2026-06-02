#!/usr/bin/env python3
"""
Behavioral Churn Risk Scoring & Customer Segmentation Engine
Author: Antigravity AI Pair Programmer
Description: Applies a rule-based scoring algorithm (0-100) to evaluate churn
             risk in active telecom subscribers. Categorizes accounts into color-coded
             risk tiers, performs advanced segmentation, maps high-value customer
             personas, and calculates financial revenue exposure under risk.
"""

import os
import pandas as pd
import numpy as np

def run_risk_engine():
    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    clean_csv_path = os.path.join(project_root, "dataset", "customer_churn_cleaned.csv")
    output_csv_path = os.path.join(project_root, "dataset", "customer_churn_scored_active.csv")
    
    print(f"Loading cleaned dataset into Risk Scoring Engine from: {clean_csv_path}")
    if not os.path.exists(clean_csv_path):
        print(f"Error: Cleaned dataset not found at {clean_csv_path}. Run data_cleaning.py first.")
        return
        
    df = pd.read_csv(clean_csv_path)
    
    # Target only active (non-churned) customers for proactive retention strategy
    active_df = df[df["Churn"] == "No"].copy()
    
    print(f"Analyzing {len(active_df)} active subscribers for churn susceptibility...")
    
    # ----------------- Rule-Based Scoring Engine (0-100) -----------------
    scores = []
    
    for idx, row in active_df.iterrows():
        score = 0
        
        # 1. Contract Dissatisfaction (Max +35)
        if row["Contract"] == "Month-to-month":
            score += 35
        elif row["Contract"] == "One year":
            score += 10
            
        # 2. Payment Gateway Friction (Max +15)
        if row["PaymentMethod"] == "Electronic check":
            score += 15
            
        # 3. Network Technology Pricing Pressure (Max +15)
        if row["InternetService"] == "Fiber optic":
            score += 15
        elif row["InternetService"] == "DSL":
            score += 5
        else:
            score -= 5  # No internet has minimal churn friction
            
        # 4. Pricing / Bill Dissatisfaction (Max +15)
        if row["MonthlyCharges"] >= 85.0:
            score += 15
        elif row["MonthlyCharges"] >= 60.0:
            score += 8
        elif row["MonthlyCharges"] <= 35.0:
            score -= 5  # Very low bills represent low-risk budget lockers
            
        # 5. Tenure Stability Shield (Max +25)
        t = row["tenure"]
        if t < 6:
            score += 25
        elif t < 12:
            score += 15
        elif t < 36:
            score += 5
        elif t >= 48:
            score -= 10  # Long-term loyalty factor reduces risk score
            
        # 6. Demographics Package Modifiers (Max +10)
        if row["SeniorCitizen"] == "Yes":
            score += 5
        if row["Partner"] == "No" and row["Dependents"] == "No":
            score += 5
            
        # Bound score between 0 and 100
        score = max(0, min(100, score))
        scores.append(score)
        
    active_df["ChurnRiskScore"] = scores
    
    # Assign Risk Tiers and Color Codes
    # Low Risk: < 30 (Green), Medium Risk: 30-59 (Gold), High Risk: >= 60 (Red)
    active_df["RiskTier"] = pd.cut(
        active_df["ChurnRiskScore"],
        bins=[-1, 29, 59, 100],
        labels=["Low", "Medium", "High"]
    )
    
    # Color-coded labels mapping (ANSI & Hex for visualization compatibility)
    color_map = {"Low": "#00F5D4", "Medium": "#FFD700", "High": "#FF007F"}
    active_df["RiskColor"] = active_df["RiskTier"].map(color_map)
    
    # ----------------- Advanced Customer Segmentation -----------------
    # 1. Loyal: Tenure >= 48 months
    # 2. High-Risk: Risk Score >= 60
    # 3. Premium: MonthlyCharges >= 90
    # 4. Budget: MonthlyCharges <= 35
    # 5. Short-Term: Tenure <= 12 months
    
    segments = []
    for idx, row in active_df.iterrows():
        seg_list = []
        if row["tenure"] >= 48:
            seg_list.append("Loyal")
        if row["ChurnRiskScore"] >= 60:
            seg_list.append("High-Risk")
        if row["MonthlyCharges"] >= 90.0:
            seg_list.append("Premium")
        if row["MonthlyCharges"] <= 35.0:
            seg_list.append("Budget")
        if row["tenure"] <= 12:
            seg_list.append("Short-Term")
            
        if not seg_list:
            seg_list.append("Standard")
            
        segments.append(", ".join(seg_list))
        
    active_df["CustomerSegments"] = segments
    
    # ----------------- Customer Personas Mapping -----------------
    # A. Loyal Long-Term Users: long tenure, low risk, 1-2 yr contract
    # B. Promo-Sensitive Budget Users: short tenure, low charges, Month-to-month
    # C. High-Value Churn-Risk Users: high charges, high risk, active
    
    personas = []
    for idx, row in active_df.iterrows():
        p = "General Subscriber"
        
        # Persona checks
        is_loyal = row["tenure"] >= 48 and row["ChurnRiskScore"] < 30 and row["Contract"] in ["One year", "Two year"]
        is_promo = row["tenure"] <= 12 and row["MonthlyCharges"] <= 40.0 and row["Contract"] == "Month-to-month"
        is_high_val_risk = row["MonthlyCharges"] >= 80.0 and row["ChurnRiskScore"] >= 60
        
        if is_loyal:
            p = "Loyal Long-Term User"
        elif is_promo:
            p = "Promo-Sensitive Budget User"
        elif is_high_val_risk:
            p = "High-Value Churn-Risk"
            
        personas.append(p)
        
    active_df["CustomerPersona"] = personas
    
    # ----------------- Revenue Exposure Calculation -----------------
    # High-Risk Revenue Exposure = Sum of MonthlyCharges for all active High Risk customers
    high_risk_mask = active_df["RiskTier"] == "High"
    high_risk_count = high_risk_mask.sum()
    total_exposure = active_df.loc[high_risk_mask, "MonthlyCharges"].sum()
    total_active_revenue = active_df["MonthlyCharges"].sum()
    
    # Export scored dataset
    active_df.to_csv(output_csv_path, index=False)
    print(f"Scored active customers dataset exported to: {output_csv_path}")
    
    # Console C-Suite Logging
    print("\n==================================================")
    print("CHURN RISK PREDICTION & SEGMENTATION REPORT")
    print("==================================================")
    print(f"Total Active Customers: {len(active_df)}")
    print(f"  - Low Risk Tier:    {len(active_df[active_df['RiskTier'] == 'Low'])} accounts")
    print(f"  - Medium Risk Tier: {len(active_df[active_df['RiskTier'] == 'Medium'])} accounts")
    print(f"  - High Risk Tier:   {high_risk_count} accounts")
    print("--------------------------------------------------")
    print(f"Total Active Portfolio Monthly Billings: ${total_active_revenue:,.2f}")
    print(f"HIGH-RISK REVENUE EXPOSURE (Monthly):   ${total_exposure:,.2f} ({round(total_exposure / total_active_revenue * 100, 2)}% of billings)")
    print("--------------------------------------------------")
    print("PERSONA BREAKDOWN:")
    print(f"  - Loyal Long-Term Users:      {len(active_df[active_df['CustomerPersona'] == 'Loyal Long-Term User'])} accounts")
    print(f"  - Promo-Sensitive Budget:     {len(active_df[active_df['CustomerPersona'] == 'Promo-Sensitive Budget User'])} accounts")
    print(f"  - High-Value Churn-Risk:      {len(active_df[active_df['CustomerPersona'] == 'High-Value Churn-Risk'])} accounts")
    print("==================================================\n")

if __name__ == "__main__":
    run_risk_engine()
