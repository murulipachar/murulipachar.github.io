#!/usr/bin/env python3
"""
Customer Churn Dataset Generator
Author: Antigravity AI Pair Programmer
Description: Simulates 7,043 high-fidelity telecom customer records with realistic 
             statistical correlations representing telecom business scenarios:
             - Month-to-month contracts and Fiber Optic service pricing pressure.
             - Payment friction in manual Electronic Checks.
             - Lower churn for long-term loyal contracts with partners/dependents.
             - Correct billing patterns with tenure=0 representing unbilled new accounts.
             - Calibrated to yield exactly 11 blank TotalCharges and ~26.5% overall Churn.
"""

import os
import csv
import random

# Seed random number generator for reproducibility
random.seed(42)

def generate_customer_id():
    """Generates a standard telecom customer ID: XXXX-XXXXX (e.g. 7590-VHVEG)"""
    part1 = "".join([str(random.randint(0, 9)) for _ in range(4)])
    part2 = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5)])
    return f"{part1}-{part2}"

def simulate_data(num_records=7043):
    """
    Simulates high-fidelity telecom customer attributes with real-world business correlations.
    """
    records = []
    
    # Pre-defined segments and demographic distributions
    genders = ["Female", "Male"]
    yes_no = ["Yes", "No"]
    internet_services = ["DSL", "Fiber optic", "No"]
    payment_methods = [
        "Electronic check", 
        "Mailed check", 
        "Bank transfer (automatic)", 
        "Credit card (automatic)"
    ]
    
    print(f"Initializing calibrated simulator for {num_records} subscriber records...")
    
    # We want exactly 11 accounts to have tenure = 0 (unbilled new customers)
    # We will pick 11 specific indices out of num_records to be new accounts.
    new_account_indices = set(random.sample(range(num_records), 11))
    
    churn_count = 0
    new_account_blanks = 0
    
    for i in range(num_records):
        cust_id = generate_customer_id()
        gender = random.choice(genders)
        
        # 16% senior citizens on average
        senior_citizen = 1 if random.random() < 0.162 else 0
        
        # Partner/Dependents correlation
        partner = random.choice(yes_no)
        if partner == "Yes":
            dependents = "Yes" if random.random() < 0.52 else "No"
        else:
            dependents = "Yes" if random.random() < 0.10 else "No"
            
        # 2. Tenure & Contract Type
        if i in new_account_indices:
            tenure = 0
            contract = random.choice(["Month-to-month", "One year", "Two year"])
        else:
            contract_rand = random.random()
            if contract_rand < 0.55:
                contract = "Month-to-month"
                # Month-to-month tenure starts from 1 month, average around 12
                tenure = max(1, int(random.gammavariate(alpha=1.2, beta=12)))
            elif contract_rand < 0.76:
                contract = "One year"
                tenure = max(1, int(random.normalvariate(mu=40, sigma=10)))
            else:
                contract = "Two year"
                tenure = max(1, int(random.normalvariate(mu=60, sigma=8)))
                
        # Bound tenure between 0 and 72
        tenure = max(0, min(72, tenure))
        if i in new_account_indices:
            tenure = 0 # Double check
            
        # Phone & Internet Service
        phone_service = "Yes" if random.random() < 0.90 else "No"
        internet_service = random.choice(internet_services)
        
        # Charges
        if internet_service == "Fiber optic":
            base_charge = 80.0
            phone_service = "Yes"
        elif internet_service == "DSL":
            base_charge = 45.0
        else:
            base_charge = 20.0
            
        addons_charge = random.uniform(5, 30) if internet_service != "No" else random.uniform(0, 5)
        monthly_charges = round(base_charge + addons_charge, 2)
        
        # Payment Method
        payment_method = random.choice(payment_methods)
        
        # TotalCharges calculation
        if tenure == 0:
            total_charges = " "
            new_account_blanks += 1
        else:
            billing_variance = random.uniform(0.99, 1.01)
            total_charges = round(monthly_charges * tenure * billing_variance, 2)
            
        # 6. Calibrated Churn Probability Model
        # Base probability of churn is low for long-term contract, high for month-to-month
        if tenure == 0:
            churn_prob = 0.0 # New customers don't churn in day 0
        else:
            # Calibrated baseline probabilities by contract
            if contract == "Month-to-month":
                churn_prob = 0.32
            elif contract == "One year":
                churn_prob = 0.08
            else:
                churn_prob = 0.02
                
            # Modifier for Fiber Optic service pricing pressure
            if internet_service == "Fiber optic":
                churn_prob += 0.12
            elif internet_service == "No":
                churn_prob -= 0.05
                
            # Modifier for payment method friction (Electronic check)
            if payment_method == "Electronic check":
                churn_prob += 0.10
                
            # Modifier for high charges
            if monthly_charges > 85.0:
                churn_prob += 0.08
            elif monthly_charges < 40.0:
                churn_prob -= 0.05
                
            # Modifier for early tenure friction (first year)
            if tenure < 12:
                churn_prob += 0.12
            elif tenure > 36:
                churn_prob -= 0.10
                
            # Demographics
            if senior_citizen == 1:
                churn_prob += 0.05
            if partner == "No" and dependents == "No":
                churn_prob += 0.03
                
        # Limit probability boundary
        churn_prob = max(0.01, min(0.95, churn_prob))
        if tenure == 0:
            churn_prob = 0.0
            
        # Determine Churn status
        if random.random() < churn_prob:
            churn = "Yes"
            churn_count += 1
        else:
            churn = "No"
            
        records.append({
            "customerID": cust_id,
            "gender": gender,
            "SeniorCitizen": senior_citizen,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": tenure,
            "PhoneService": phone_service,
            "InternetService": internet_service,
            "Contract": contract,
            "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges,
            "Churn": churn
        })

    return records, churn_count, new_account_blanks

def save_to_csv(records, target_dir, filename="customer_churn_dataset.csv"):
    """Saves simulated customer records to target path."""
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, filename)
    
    headers = [
        "customerID", "gender", "SeniorCitizen", "Partner", "Dependents", 
        "tenure", "PhoneService", "InternetService", "Contract", 
        "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"
    ]
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Success! Dataset successfully generated and written to: {file_path}")
    return file_path

if __name__ == "__main__":
    # Resolve project directory dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    dataset_dir = os.path.join(project_root, "dataset")
    
    # Run simulation
    sim_records, ch_count, bl_count = simulate_data(7043)
    
    # Save output
    output_path = save_to_csv(sim_records, dataset_dir)
    
    # Output quick validation parameters
    print("\n--- Dataset Calibrated Report ---")
    print(f"Total Transactions Generated: {len(sim_records)}")
    print(f"Total Churn Subscribers: {ch_count} ({round(ch_count / len(sim_records) * 100, 2)}% churn rate)")
    print(f"Unbilled New Accounts (blank TotalCharges): {bl_count}")
    print("---------------------------------")
