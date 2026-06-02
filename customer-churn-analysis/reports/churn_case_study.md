# Portfolio Case Study: Customer Churn & Retention Analytics
**Project Owner:** Business Intelligence Analytics Division  
**Technological Stack:** Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook  
**Analytical Scope:** End-to-end subscriber lifecycles, rule-based risk profiling, customer segmentation, and financial exposure auditing.

---

## 1. Executive Summary & Project Objective
In the highly saturated telecommunications sector, customer acquisition cost (CAC) typically exceeds retention costs by 5x to 7x. Maintaining brand loyalty is paramount.

This case study details the deployment of a **Customer Churn Analytics Engine** analyzing a customer base of **7,043 subscribers**. The core objectives are:
1. **Identify** key demographical and behavioral features driving customer attrition.
2. **Design** a custom, rule-based Churn Risk Scoring Engine to identify active accounts heading toward cancellation.
3. **Establish** highly targeted C-Suite recommendations and calculate billing revenue exposure under risk.

---

## 2. Relational Database Schema & Data Dictionary

The analytical pipeline utilizes a standardized structure, mapping 13 core customer and service attributes:

| Feature | Category | Data Type | Description | Values |
| :--- | :--- | :--- | :--- | :--- |
| **customerID** | Identifier | `object` | Alphanumeric unique subscriber ID | e.g. `7590-VHVEG` |
| **gender** | Demographic | `object` | Gender category | `Female`, `Male` |
| **SeniorCitizen** | Demographic | `object` | Senior citizen status | `Yes`, `No` |
| **Partner** | Demographic | `object` | Whether the subscriber has a domestic partner | `Yes`, `No` |
| **Dependents** | Demographic | `object` | Whether the subscriber has family dependents | `Yes`, `No` |
| **tenure** | Behavior | `int64` | Number of months subscriber has been with brand | `0` to `72` months |
| **PhoneService** | Service | `object` | Whether subscriber has voice services | `Yes`, `No` |
| **InternetService** | Service | `object` | Data network technology | `DSL`, `Fiber optic`, `No` |
| **Contract** | Service | `object` | Billing commitment structure | `Month-to-month`, `One year`, `Two year` |
| **PaymentMethod** | Financial | `object` | Payment billing gateway | `Electronic check`, `Mailed check`, `Credit card`, etc. |
| **MonthlyCharges** | Financial | `float64` | Current monthly recurring bill amount ($) | `$18.25` - `$123.50` |
| **TotalCharges** | Financial | `float64` | Cumulative billing charges over customer life ($) | `$0.00` - `$8,684.80` |
| **Churn** | Target | `object` | Target label: Did subscriber cancel in past month | `Yes`, `No` |

---

## 3. Data Engineering & Sanitization Pipeline
Prior to statistical profiling, the raw database went through a rigorous, automated cleaning script (`python/data_cleaning.py`):
1. **Null Analysis & Coercion:** Coerced `TotalCharges` from string to float. Identified exactly **11 blank values** in `TotalCharges`.
2. **Business Alignment:** Verified that all 11 empty records belonged to customers with `tenure == 0` months. These represent brand-new active subscribers who have not completed their first billing cycle. Rather than dropping these rows (introducing a survival bias), their values were set to `0.00`.
3. **Feature Standardizations:** Mapped the binary `SeniorCitizen` numeric values (`0`/`1`) to readable `"No"`/`"Yes"` strings for consistency.
4. **Duplicate & Outlier Checks:** Checked for duplicate subscriber IDs and confirmed billing ranges (zero outliers detected).

---

## 4. Advanced Risk Scoring & Customer Segmentation

Active, non-churned subscribers (`4,929` accounts) were processed through a custom **Behavioral Churn Risk Scoring Engine** (`python/churn_prediction_logic.py`). A risk score between 0 and 100 was computed for each customer based on behavioral risk indicators:

- **Month-to-Month Contract:** `+35` points
- **Electronic Check Payment:** `+15` points
- **Fiber Optic Service:** `+15` points
- **High Monthly Charges (>= $85):** `+15` points
- **Low Tenure (< 6 months):** `+25` points
- **Loyalty tenure protection (>= 48 months):** `-10` points

### Portfolio Risk Tier Breakdown

```
[Active Customers Pool: 4,929]
 ├── Low Risk Tier (Score <30)     : 2,233 (45.3%)
 ├── Medium Risk Tier (Score 30-59): 1,656 (33.6%)
 └── High Risk Tier (Score >=60)   : 1,040 (21.1%)  <-- Safekeep $78,490.22/mo
```

### Advanced Customer Segments Profiled

1. **Loyal Customers (1803 accounts):** Active subscribers with >=48 months of tenure. Highly resilient, low churn risk.
2. **Premium Customers (1851 accounts):** High-value subscribers with monthly bills >= $90. Crucial for ARPU (Average Revenue Per User).
3. **High-Risk Customers (1040 accounts):** Active accounts exhibiting Churn Risk Scores >= 60.
4. **Short-Term Customers (2260 accounts):** Brand new subscribers in their first year of brand engagement. Subject to high onboarding friction.

---

## 5. Strategic Personas and Revenue Impact

Our engine mapped active customers into three distinct C-suite marketing personas to guide personalized retention offers:

### Persona A: The Loyal Long-Term User
- **Profile:** Tenure >= 48 months, long-term contract, automated billing.
- **Active Accounts:** `1536`
- **Recommendation:** Do not disturb with marketing offers. Maintain core service quality. Show appreciation via surprise loyalty perks.

### Persona B: The Promo-Sensitive Budget User
- **Profile:** Tenure <= 12 months, Month-to-month, very low monthly charges (<$40).
- **Active Accounts:** `453`
- **Recommendation:** Sensitive to pricing. Migrate to entry-level 1-year agreements with minor discounts.

### Persona C: The High-Value Churn-Risk User
- **Profile:** High billing (MonthlyCharges >= $80), high risk score (>=60), active customer.
- **Active Accounts:** `489`
- **Revenue Under Threat:** **$47,656.12 / month**
- **Recommendation:** Immediate customer success intervention. Offer premium fiber bundles and auto-pay bonuses.

---
*Case Study compiled for recruiter review and portfolio presentation.*
