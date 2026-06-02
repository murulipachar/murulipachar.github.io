# Data Quality and Integrity Report

**Project:** Customer Churn Analytics
**Date:** 2026-05-21
**Pipeline Operator:** Antigravity AI Data Engine

This report documents the data cleaning, coercion, and validation steps executed on the raw telecom customer churn dataset to establish a portfolio-ready, high-integrity analytical database.

---

## 1. Initial State Assessment
- **Raw Row Count:** `7043`
- **Raw Column Count:** `13`
- **Dataset Features:** `customerID`, `gender`, `SeniorCitizen`, `Partner`, `Dependents`, `tenure`, `PhoneService`, `InternetService`, `Contract`, `PaymentMethod`, `MonthlyCharges`, `TotalCharges`, `Churn`

---

## 2. Integrity Checks & Cleaning Actions

### A. Duplicate Analysis
- **Duplicate Rows Detected:** `0`
- **Action taken:** None required (no duplicates detected)

### B. Missing Values & Billing Anomalies
- **Anomalous `TotalCharges` Strings (Spaces):** `11`
- **New Account Verification (`tenure == 0` check):** `SUCCESS (All empty charges are tenure = 0)`
- **Action taken:** Coerced `TotalCharges` to numeric float and populated missing values with `0.0`.
- **Business Rationale:** These `11` records represent newly acquired active accounts with `tenure = 0` months who have not completed their first monthly billing cycle. Deleting them would introduce a survival bias against new subscribers; setting their total revenue contribution to `$0.00` is the mathematically correct and business-aligned action.

### C. Feature Engineering & Standardizations
- **Action taken:** Converted binary `SeniorCitizen` numeric column (`1` / `0`) into human-readable labels (`"Yes"` / `"No"`) to align with demographic features (`Partner`, `Dependents`).

### D. Outlier & Range Validation
- **Negative Billing Records:** `0`
- **Monthly Charges Outliers (Outside $18 - $125):** `0`
- **Action taken:** Verified that monthly bills and accumulated revenues fall into realistic industry intervals. Zero invalid entries detected.

---

## 3. Final Cleaned Database Profile
- **Cleaned Row Count:** `7043`
- **Cleaned Column Count:** `13`
- **Null Value Count:** `0` (Fully complete)
- **Export Destination:** `dataset/customer_churn_cleaned.csv`

---

## 4. Verification Check
Below is the data distribution profile for the cleaned dataset:

| Feature | Data Type | Non-Null Count | Unique Values | Sample Values / Range |
| :--- | :--- | :--- | :--- | :--- |
| **customerID** | `object` | 7043 | 7043 | e.g. `7590-VHVEG` |
| **gender** | `object` | 7043 | 2 | `Female`, `Male` |
| **SeniorCitizen** | `object` | 7043 | 2 | `Yes`, `No` |
| **Partner** | `object` | 7043 | 2 | `Yes`, `No` |
| **Dependents** | `object` | 7043 | 2 | `Yes`, `No` |
| **tenure** | `int64` | 7043 | 73 | 0 - 72 months |
| **PhoneService** | `object` | 7043 | 2 | `Yes`, `No` |
| **InternetService** | `object` | 7043 | 3 | `DSL`, `Fiber optic`, `No` |
| **Contract** | `object` | 7043 | 3 | `Month-to-month`, `One year`, `Two year` |
| **PaymentMethod** | `object` | 7043 | 4 | `Electronic check`, `Mailed check`, etc. |
| **MonthlyCharges** | `float64` | 7043 | 3546 | $20.0 - $109.98 |
| **TotalCharges** | `float64` | 7043 | 6927 | $0.0 - $7855.95 |
| **Churn** | `object` | 7043 | 2 | `Yes`, `No` |

---
**Report compiled successfully. All systems green.**
