import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_banking_risk_data():
    np.random.seed(101)
    print("Initializing Banking Risk & Loan Dataset Generation...")

    # 1. Generate Branches (10 branches)
    branches_data = [
        {"Branch_ID": "BR-01", "Branch_Name": "Downtown Plaza", "Region": "East", "Manager": "Alice Smith"},
        {"Branch_ID": "BR-02", "Branch_Name": "Metro North", "Region": "East", "Manager": "Robert Johnson"},
        {"Branch_ID": "BR-03", "Branch_Name": "Pacific Coast", "Region": "West", "Manager": "Carol Williams"},
        {"Branch_ID": "BR-04", "Branch_Name": "Valley View", "Region": "West", "Manager": "David Brown"},
        {"Branch_ID": "BR-05", "Branch_Name": "Gulf Shore", "Region": "South", "Manager": "Eva Jones"},
        {"Branch_ID": "BR-06", "Branch_Name": "Peach Tree", "Region": "South", "Manager": "Frank Miller"},
        {"Branch_ID": "BR-07", "Branch_Name": "Lakeshore Central", "Region": "Central", "Manager": "Grace Davis"},
        {"Branch_ID": "BR-08", "Branch_Name": "Windy City East", "Region": "Central", "Manager": "Henry Garcia"},
        {"Branch_ID": "BR-09", "Branch_Name": "Sunset Boulevard", "Region": "West", "Manager": "Iris Rodriguez"},
        {"Branch_ID": "BR-10", "Branch_Name": "Wall Street Annex", "Region": "East", "Manager": "Jack Wilson"}
    ]
    df_branches = pd.DataFrame(branches_data)

    # 2. Generate Customers (3,000 customers)
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Elizabeth", "William", "Linda",
                   "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
                   "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
                   "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                  "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"]

    occupations = ["Salaried Professional", "Blue Collar Worker", "Self-Employed Business", "Gig Economy Worker", "Freelancer", "Retired", "Student"]
    occupation_probs = [0.45, 0.20, 0.15, 0.08, 0.06, 0.04, 0.02]

    customers_list = []
    start_date = datetime(2020, 1, 1)

    for i in range(3000):
        cust_id = f"CUST-{1001 + i}"
        name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        age = int(np.random.normal(40, 12))
        age = max(18, min(80, age))
        gender = np.random.choice(["Male", "Female"], p=[0.49, 0.51])
        
        occ = np.random.choice(occupations, p=occupation_probs)
        
        # Base income ranges per occupation
        if occ == "Salaried Professional":
            income = np.round(np.random.uniform(4500, 14000), 2)
        elif occ == "Self-Employed Business":
            income = np.round(np.random.uniform(3500, 16000), 2)
        elif occ == "Freelancer":
            income = np.round(np.random.uniform(2500, 8000), 2)
        elif occ == "Blue Collar Worker":
            income = np.round(np.random.uniform(2200, 5500), 2)
        elif occ == "Gig Economy Worker":
            income = np.round(np.random.uniform(1800, 4800), 2)
        elif occ == "Retired":
            income = np.round(np.random.uniform(1500, 4200), 2)
        else: # Student
            income = np.round(np.random.uniform(500, 2000), 2)

        # Credit score base on income, age and some randomness
        credit_base = 620 + (income / 1000) * 8 + (age - 30) * 1.5
        credit_score = int(np.clip(np.random.normal(credit_base, 75), 300, 850))

        join_days = np.random.randint(0, 1000)
        join_date = start_date + timedelta(days=join_days)

        customers_list.append({
            "Customer_ID": cust_id,
            "Customer_Name": name,
            "Age": age,
            "Gender": gender,
            "Occupation": occ,
            "Monthly_Income": income,
            "Credit_Score": credit_score,
            "Join_Date": join_date.strftime("%Y-%m-%d")
        })

    df_customers = pd.DataFrame(customers_list)

    # 3. Generate Credit History Dimension
    credit_hist_list = []
    for _, cust in df_customers.iterrows():
        score = cust["Credit_Score"]
        
        # Debt-to-income and delinquencies correlate with credit score
        if score < 580:
            dti = np.round(np.random.uniform(0.40, 0.70), 2)
            existing_loans = np.random.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
            delinquencies = np.random.choice([1, 2, 3, 4, 5], p=[0.2, 0.3, 0.2, 0.2, 0.1])
        elif score < 670:
            dti = np.round(np.random.uniform(0.25, 0.50), 2)
            existing_loans = np.random.choice([0, 1, 2, 3], p=[0.2, 0.5, 0.2, 0.1])
            delinquencies = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        else:
            dti = np.round(np.random.uniform(0.10, 0.35), 2)
            existing_loans = np.random.choice([0, 1, 2], p=[0.5, 0.4, 0.1])
            delinquencies = 0

        credit_hist_list.append({
            "Customer_ID": cust["Customer_ID"],
            "Debt_To_Income_Ratio": dti,
            "Existing_Loans_Count": existing_loans,
            "Past_Delinquencies": delinquencies
        })
    df_credit_history = pd.DataFrame(credit_hist_list)

    # 4. Generate Loans applied for (4,500 loans)
    loans_list = []
    loan_types = ["Personal Loan", "Auto Loan", "Home Loan", "Education Loan", "Business Loan"]
    loan_type_probs = [0.35, 0.25, 0.20, 0.12, 0.08]
    
    start_loan_date = datetime(2023, 1, 1)

    for i in range(4500):
        loan_id = f"LOAN-{10001 + i}"
        customer = df_customers.sample(1).iloc[0]
        cust_id = customer["Customer_ID"]
        cust_income = customer["Monthly_Income"]
        cust_score = customer["Credit_Score"]
        
        l_type = np.random.choice(loan_types, p=loan_type_probs)
        
        # Scale loan amount based on income and type
        if l_type == "Home Loan":
            amount = np.round(np.random.uniform(80000, 450000), -3)
            term = np.random.choice([120, 180, 240, 360])
            # Interest rate base
            base_rate = 6.5
        elif l_type == "Business Loan":
            amount = np.round(np.random.uniform(20000, 150000), -3)
            term = np.random.choice([36, 48, 60, 120])
            base_rate = 9.0
        elif l_type == "Auto Loan":
            amount = np.round(np.random.uniform(15000, 60000), -3)
            term = np.random.choice([36, 48, 60, 72])
            base_rate = 5.5
        elif l_type == "Personal Loan":
            amount = np.round(np.random.uniform(5000, 35000), -3)
            term = np.random.choice([12, 24, 36, 48, 60])
            base_rate = 11.0
        else: # Education Loan
            amount = np.round(np.random.uniform(8000, 45000), -3)
            term = np.random.choice([60, 84, 120])
            base_rate = 7.0

        # Adjust interest rate based on credit score
        if cust_score < 550:
            interest_rate = base_rate + 6.5
        elif cust_score < 620:
            interest_rate = base_rate + 4.0
        elif cust_score < 680:
            interest_rate = base_rate + 2.0
        elif cust_score < 750:
            interest_rate = base_rate + 0.5
        else:
            interest_rate = base_rate - 0.5

        interest_rate = np.round(max(3.5, interest_rate), 2)

        # Monthly EMI Amortization calculation
        r = (interest_rate / 100) / 12
        n = term
        if r > 0:
            emi = np.round((amount * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1), 2)
        else:
            emi = np.round(amount / n, 2)

        # Determine branch
        branch_id = np.random.choice(df_branches["Branch_ID"].tolist())

        # Determine loan application date
        cust_join_dt = datetime.strptime(customer["Join_Date"], "%Y-%m-%d")
        min_offset_days = (start_loan_date - cust_join_dt).days
        days_offset = np.random.randint(max(0, min_offset_days), 1150) # up to late 2025/early 2026
        loan_date = cust_join_dt + timedelta(days=days_offset)
        
        # Clamp to max April 1, 2026
        clamp_date = datetime(2026, 4, 1)
        if loan_date > clamp_date:
            loan_date = clamp_date - timedelta(days=np.random.randint(1, 30))

        # Check Approval Status based on credit score, DTI, and income
        dti_info = df_credit_history[df_credit_history["Customer_ID"] == cust_id].iloc[0]
        dti = dti_info["Debt_To_Income_Ratio"]
        
        approval_prob = 0.80
        if cust_score < 550:
            approval_prob = 0.05
        elif cust_score < 600:
            approval_prob = 0.25
        elif cust_score < 660:
            approval_prob = 0.65
        
        if dti > 0.55:
            approval_prob = max(0.02, approval_prob - 0.40)
        
        # EMI capacity check (EMI shouldn't exceed 45% of income for high approval)
        if emi > (cust_income * 0.45):
            approval_prob = max(0.01, approval_prob - 0.35)

        approval_status = "Approved" if np.random.rand() < approval_prob else "Rejected"

        loans_list.append({
            "Loan_ID": loan_id,
            "Customer_ID": cust_id,
            "Loan_Type": l_type,
            "Loan_Amount": amount,
            "Interest_Rate": interest_rate,
            "Term_Months": term,
            "Monthly_EMI": emi,
            "Branch_ID": branch_id,
            "Loan_Application_Date": loan_date.strftime("%Y-%m-%d"),
            "Approval_Status": approval_status
        })

    df_loans = pd.DataFrame(loans_list)

    # 5. Generate Loan Payments and Defaults (aiming for 25,000+ transaction payments)
    payments_list = []
    defaults_list = []
    
    approved_loans = df_loans[df_loans["Approval_Status"] == "Approved"]
    
    pmt_id_counter = 100001
    default_id_counter = 5001
    
    max_date = datetime(2026, 6, 1)

    print(f"Simulating payment schedules for {len(approved_loans)} approved loans...")

    for _, loan in approved_loans.iterrows():
        loan_id = loan["Loan_ID"]
        cust_id = loan["Customer_ID"]
        emi = loan["Monthly_EMI"]
        term = loan["Term_Months"]
        amount = loan["Loan_Amount"]
        interest_rate = loan["Interest_Rate"]
        
        # Get customer data
        customer = df_customers[df_customers["Customer_ID"] == cust_id].iloc[0]
        cust_score = customer["Credit_Score"]
        cust_occ = customer["Occupation"]
        
        # Get credit info
        cred_info = df_credit_history[df_credit_history["Customer_ID"] == cust_id].iloc[0]
        dti = cred_info["Debt_To_Income_Ratio"]

        # Date of loan start
        loan_start = datetime.strptime(loan["Loan_Application_Date"], "%Y-%m-%d") + timedelta(days=7) # funded after 7 days
        
        # Base payment risk profile
        base_late_prob = 0.04
        base_missed_prob = 0.02
        
        if cust_score < 560:
            base_late_prob = 0.20
            base_missed_prob = 0.15
        elif cust_score < 620:
            base_late_prob = 0.12
            base_missed_prob = 0.07
        elif cust_score < 680:
            base_late_prob = 0.06
            base_missed_prob = 0.03
            
        if cust_occ in ["Gig Economy Worker", "Freelancer"]:
            base_late_prob += 0.05
            base_missed_prob += 0.03
            
        if dti > 0.50:
            base_late_prob += 0.05
            base_missed_prob += 0.02

        # Simulate payments month by month
        consecutive_missed = 0
        defaulted = False
        remaining_balance = amount
        monthly_rate = (interest_rate / 100) / 12

        # Total payments to generate depends on how many months have elapsed until clamp_date
        elapsed_months = ((max_date.year - loan_start.year) * 12 + max_date.month - loan_start.month)
        payments_to_gen = min(term, max(0, elapsed_months))

        for month_idx in range(payments_to_gen):
            if defaulted:
                break
                
            pmt_date = loan_start + timedelta(days=30 * (month_idx + 1))
            if pmt_date > max_date:
                break

            # Determine payment status
            miss_prob = base_missed_prob
            if consecutive_missed > 0:
                miss_prob = 0.55 + (consecutive_missed * 0.10)
            
            rand_val = np.random.rand()
            if rand_val < miss_prob:
                status = "Missed"
                consecutive_missed += 1
            elif rand_val < (miss_prob + base_late_prob):
                status = "Late"
                consecutive_missed = 0
            else:
                status = "On-Time"
                consecutive_missed = 0

            # Calculate interest and principal components of payment
            interest_paid = np.round(remaining_balance * monthly_rate, 2)
            principal_paid = np.round(emi - interest_paid, 2)
            
            if status != "Missed":
                remaining_balance = max(0, np.round(remaining_balance - principal_paid, 2))

            payments_list.append({
                "Payment_ID": f"PMT-{pmt_id_counter}",
                "Loan_ID": loan_id,
                "Payment_Month_Number": month_idx + 1,
                "Payment_Date": pmt_date.strftime("%Y-%m-%d"),
                "Amount_Due": emi,
                "Amount_Paid": 0 if status == "Missed" else emi,
                "Interest_Component": interest_paid,
                "Principal_Component": principal_paid,
                "Payment_Status": status
            })
            pmt_id_counter += 1

            # Check Default condition: 3 consecutive missed payments
            if consecutive_missed >= 3:
                defaulted = True
                default_date = pmt_date
                
                # Default amount is remaining balance plus 2 missed EMIs
                def_amt = np.round(remaining_balance, 2)
                
                # Recovery percentage is higher for better credit score and salaried customers
                rec_pct = 0.05
                if cust_score > 680:
                    rec_pct = np.random.uniform(0.20, 0.45)
                elif cust_score > 600:
                    rec_pct = np.random.uniform(0.10, 0.30)
                else:
                    rec_pct = np.random.uniform(0.0, 0.15)
                    
                rec_amt = np.round(def_amt * rec_pct, 2)
                
                status_default = "Written-Off" if (def_amt - rec_amt) > 5000 else "Recovered"
                if rec_amt == 0:
                    status_default = "Defaulted"

                defaults_list.append({
                    "Default_ID": f"DEF-{default_id_counter}",
                    "Loan_ID": loan_id,
                    "Default_Date": default_date.strftime("%Y-%m-%d"),
                    "Default_Amount": def_amt,
                    "Recovered_Amount": rec_amt,
                    "Default_Status": status_default
                })
                default_id_counter += 1

    df_payments = pd.DataFrame(payments_list)
    df_defaults = pd.DataFrame(defaults_list)

    # 6. Generate Transactions Table (repurposing payments as transactions for relational check)
    transactions_list = []
    tx_id_counter = 800001
    
    for _, pmt in df_payments.iterrows():
        if pmt["Amount_Paid"] > 0:
            # Transaction for the EMI payment
            transactions_list.append({
                "Transaction_ID": f"TX-{tx_id_counter}",
                "Loan_ID": pmt["Loan_ID"],
                "Transaction_Date": pmt["Payment_Date"],
                "Amount": pmt["Amount_Paid"],
                "Transaction_Type": "Payment"
            })
            tx_id_counter += 1
            
    # Also create loan disbursements as transactions
    for _, loan in approved_loans.iterrows():
        loan_start_str = (datetime.strptime(loan["Loan_Application_Date"], "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        transactions_list.append({
            "Transaction_ID": f"TX-{tx_id_counter}",
            "Loan_ID": loan["Loan_ID"],
            "Transaction_Date": loan_start_str,
            "Amount": loan["Loan_Amount"],
            "Transaction_Type": "Disbursement"
        })
        tx_id_counter += 1

    df_transactions = pd.DataFrame(transactions_list)

    # 7. Apply Advanced Analytics Risk Scoring Model (0-100 score)
    # Weights: Credit Score (40%), DTI (20%), Occupation (15%), Delinquencies/Missed Payments (25%)
    print("Computing Risk Scores and Tiers...")
    
    # Pre-calculate delinquency counts per loan
    delinq_counts = {}
    if len(df_payments) > 0:
        late_missed = df_payments[df_payments["Payment_Status"].isin(["Late", "Missed"])]
        delinq_counts = late_missed.groupby("Loan_ID").size().to_dict()

    risk_list = []
    for _, loan in df_loans.iterrows():
        cust_id = loan["Customer_ID"]
        loan_id = loan["Loan_ID"]
        
        # Get customer data
        cust = df_customers[df_customers["Customer_ID"] == cust_id].iloc[0]
        score = cust["Credit_Score"]
        occ = cust["Occupation"]
        
        # Get credit data
        cred = df_credit_history[df_credit_history["Customer_ID"] == cust_id].iloc[0]
        dti = cred["Debt_To_Income_Ratio"]
        past_del = cred["Past_Delinquencies"]

        # A. Credit Score Component (0-40 points: lower score = higher points)
        # 850 score -> 0 points, 300 score -> 40 points
        score_pts = (850 - score) / (850 - 300) * 40
        
        # B. DTI Component (0-20 points: higher DTI = higher points)
        # DTI 0.10 -> 0 points, 0.70 -> 20 points
        dti_pts = max(0, min(20, (dti - 0.10) / (0.70 - 0.10) * 20))

        # C. Occupation Stability Component (0-15 points)
        occ_map = {
            "Salaried Professional": 0,
            "Retired": 2,
            "Blue Collar Worker": 5,
            "Freelancer": 8,
            "Self-Employed Business": 10,
            "Gig Economy Worker": 12,
            "Student": 15
        }
        occ_pts = occ_map.get(occ, 5)

        # D. Delinquency History Component (0-25 points)
        # Combine past delinquencies and simulated late/missed payments
        sim_del = delinq_counts.get(loan_id, 0)
        total_del = past_del + sim_del
        del_pts = min(25, total_del * 5)

        # E. Default status surcharge
        is_defaulted = loan_id in df_defaults["Loan_ID"].values
        default_surcharge = 15 if is_defaulted else 0

        # Calculate final score
        risk_score = min(100, int(score_pts + dti_pts + occ_pts + del_pts + default_surcharge))
        
        # Tiers: Low Risk (<30), Medium Risk (30-55), High Risk (55-75), Critical Risk (>75)
        if risk_score < 30:
            category = "Low Risk"
        elif risk_score < 55:
            category = "Medium Risk"
        elif risk_score < 75:
            category = "High Risk"
        else:
            category = "Critical Risk"

        risk_list.append({
            "Loan_ID": loan_id,
            "Risk_Score": risk_score,
            "Risk_Category": category
        })
    df_risk_scores = pd.DataFrame(risk_list)

    # 8. Merge all into Consolidated flat file (banking_risk_data.csv)
    print("Merging data for master flat file...")
    # Flat file links customer, loan, branch, and payments details
    df_flat = df_loans.merge(df_customers, on="Customer_ID")
    df_flat = df_flat.merge(df_credit_history, on="Customer_ID")
    df_flat = df_flat.merge(df_branches, on="Branch_ID")
    df_flat = df_flat.merge(df_risk_scores, on="Loan_ID")
    
    # We want a payment-level transactional flat file, so we do a left join with payments
    df_flat_final = df_flat.merge(df_payments, on="Loan_ID", how="left")
    
    # Left join defaults to get details
    df_flat_final = df_flat_final.merge(df_defaults, on="Loan_ID", how="left")
    
    # Clean default status and payment date
    df_flat_final["Default_Status"] = df_flat_final["Default_Status"].fillna("Active/Paid")
    df_flat_final["Default_Amount"] = df_flat_final["Default_Amount"].fillna(0.0)
    df_flat_final["Recovered_Amount"] = df_flat_final["Recovered_Amount"].fillna(0.0)
    df_flat_final["Payment_Status"] = df_flat_final["Payment_Status"].fillna("N/A - Rejected")

    print(f"Generated Customers: {len(df_customers)}")
    print(f"Generated Credit History: {len(df_credit_history)}")
    print(f"Generated Branches: {len(df_branches)}")
    print(f"Generated Loans Applied: {len(df_loans)}")
    print(f"Generated Payments Ingested: {len(df_payments)}")
    print(f"Generated Defaults Tracked: {len(df_defaults)}")
    print(f"Generated Transactions Ingested: {len(df_transactions)}")
    print(f"Generated Consolidated Flat Records: {len(df_flat_final)}")

    # 9. Create folder paths and save files
    dataset_dir = "banking-risk-loan-analytics/dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Save normalized tables
    df_customers.to_csv(os.path.join(dataset_dir, "customers.csv"), index=False)
    df_credit_history.to_csv(os.path.join(dataset_dir, "credit_history.csv"), index=False)
    df_branches.to_csv(os.path.join(dataset_dir, "branches.csv"), index=False)
    df_loans.to_csv(os.path.join(dataset_dir, "loans.csv"), index=False)
    df_payments.to_csv(os.path.join(dataset_dir, "loan_payments.csv"), index=False)
    df_defaults.to_csv(os.path.join(dataset_dir, "defaults.csv"), index=False)
    df_transactions.to_csv(os.path.join(dataset_dir, "transactions.csv"), index=False)
    
    # Save master flat files
    df_flat_final.to_csv(os.path.join(dataset_dir, "banking_risk_data.csv"), index=False)
    
    # Save Excel flat master sheet (limiting size to keep file writing fast, 10,000 row sample or full data)
    # We will write the full data but Excel writer might be slow for 30,000 rows, so let's save flat data in chunks or standard excel
    df_flat_final.to_excel(os.path.join(dataset_dir, "banking_risk_data.xlsx"), index=False, sheet_name="RiskData")
    
    print("All datasets successfully generated and saved to banking-risk-loan-analytics/dataset/!")

if __name__ == "__main__":
    generate_banking_risk_data()
