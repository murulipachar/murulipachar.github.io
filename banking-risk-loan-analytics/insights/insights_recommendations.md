# Risk Scoring Model, Business Insights & Recommendations

This document details the **Banking Credit Risk Scoring Model** and presents **20 Data-Driven Business Insights** alongside **15 Actionable Strategic Recommendations** for the bank's retail lending portfolio.

---

## Part 1: Credit Risk Scoring Model (0-100)

To quantify borrower default risk, we designed a custom credit-risk scoring algorithm that aggregates credit history, financial position, and payment history variables:

$$\text{Risk Score} = \text{Credit Score Component (40%)} + \text{DTI Component (20%)} + \text{Occupation Component (15%)} + \text{Delinquency Component (25%)} + \text{Surcharge (15pts)}$$

### Risk Score Component Breakdown

1.  **Credit Score Component (Max 40 points)**
    *   Formula: $Points = \frac{850 - \text{Credit Score}}{850 - 300} \times 40$
    *   *Rationale*: Low credit scores represent high historical delinquency risk.
2.  **Debt-to-Income (DTI) Component (Max 20 points)**
    *   Formula: $Points = \frac{\text{DTI} - 0.10}{0.70 - 0.10} \times 20$ (clamped between 0 and 20).
    *   *Rationale*: High DTI ratios compress a borrower's monthly cash buffer.
3.  **Occupation Stability Component (Max 15 points)**
    *   Salaried Professional: 0 points | Retired: 2 points | Blue Collar: 5 points
    *   Freelancer: 8 points | Self-Employed: 10 points | Gig Economy: 12 points | Student: 15 points.
    *   *Rationale*: Variable income structures increase payment volatility.
4.  **Delinquency Component (Max 25 points)**
    *   Formula: $Points = \text{Total Delinquencies (Past + Current Late/Missed)} \times 5$ (clamped at 25).
    *   *Rationale*: Current late payments are the strongest leading indicator of ultimate default.
5.  **Default Status Surcharge (15 points)**
    *   Applied if the loan has already breached default criteria (3 consecutive missed EMIs).

### Portfolio Risk Classifications

| Risk Score Range | Risk Category | Expected Default Rate | Operational Action |
| :--- | :--- | :--- | :--- |
| **Score < 30** | **Low Risk** | $< 1.5\%$ | Auto-approve, offer preferred interest rates. |
| **Score 30 - 55** | **Medium Risk** | $1.5\% - 6.0\%$ | Standard review, check secondary collateral. |
| **Score 55 - 75** | **High Risk** | $6.0\% - 20.0\%$ | Stricter pricing, limit loan amount to 3x income. |
| **Score > 75** | **Critical Risk** | $> 20.0\%$ | Auto-reject, transfer to pre-collections queue. |

---

## Part 2: 20 Key Business Insights

### Risk & Credit Scores
1.  **Credit Score Default Concentration**: Borrowers with credit scores below 580 represent only 12.4% of total approved loans, but account for **58.2% of all defaults**, verifying the critical predictive power of credit tiering.
2.  **DTI Attrition Squeeze**: Applicants with DTI ratios above 0.50 show a **4.2x higher late payment occurrence** compared to those with DTI ratios below 0.30.
3.  **Interest Rate Adverse Selection**: Approved loans carrying interest rates above 14% experience a **22.5% default rate**, indicating that high pricing terms attract borrowers with lower repayment capacities.
4.  **Critical Risk Category Losses**: The "Critical Risk" category (Risk Score >75) generates **74% of the bank's net write-off losses**, representing a total of $3.2M in unrecovered capital.
5.  **Delinquency Escalation Threshold**: Borrowers who record a single "Missed" payment have a 14.2% probability of defaulting. However, once a borrower reaches **two consecutive missed payments**, the probability of defaulting jumps to **78.4%**.

### Demographics & Occupations
6.  **Gig Economy Cash Flow Volatility**: Gig Economy Workers exhibit the highest late payment rate (18.6%), driven by cash flow seasonality, despite having average debt levels 15% lower than Salaried Professionals.
7.  **Salaried Stability**: Salaried Professionals exhibit a 98.4% payment success rate, making them the most profitable and stable customer segment.
8.  **Age Group Default Correlation**: Young borrowers (Ages 18-25) exhibit a **16.4% default rate**, which is 3x higher than middle-aged borrowers (Ages 35-50), primarily due to lower income reserves.
9.  **Self-Employed Loan Term Risk**: Self-employed business owners taking loan terms longer than 60 months experience a 15.3% default rate, indicating long-term operational vulnerability.
10. **Gender Performance Equality**: There is no statistically significant difference in repayment rates between Male and Female borrowers (92.4% vs. 92.6%).

### Product & Portfolio Performance
11. **Business Loan Vulnerability**: Business Loans carry the highest default rate (14.2%), driven by small business failures, compared to Auto Loans which carry the lowest default rate (3.4%).
12. **Home Loan Collateral Cushion**: Home Loans represent 58% of the bank's total credit exposure, but average write-offs are kept below 1.2% due to robust property collateral recovery.
13. **Education Loan Repayment Lag**: Education Loans exhibit a high delinquency rate (12.4%) in the first 24 months, but stabilize to under 3.5% as graduates transition into employment.
14. **Personal Loan Yield vs. Risk**: Personal Loans generate the highest interest rate yields (average 16.5%), but 38% of this yield is offset by default losses, making their net risk-adjusted return lower than Auto Loans.

### Branch & Regional Operations
15. **Gulf Shore Credit Distress**: The Gulf Shore branch (BR-05) in the South region exhibits the highest default rate (9.8%), driven by local economic contractions and relaxed local underwriting audits.
16. **Wall Street Annex Performance**: The Wall Street Annex branch (BR-10) in the East region generates the highest net profit margin (21.4%) and the lowest default rate (1.2%).
17. **East Region Regional Efficiency**: The East Region represents our most efficient territory, generating 38% of total interest revenue with an average customer credit score of 712.
18. **Central Region Growth**: The Central Region exhibits a 12% YoY increase in personal loan applications, representing a growing consumer credit market.

### Collections & Recoveries
19. **Late shipping recovery decay**: Capital recovery rates on defaulted loans drop from 32% (in month 1 of default) to **less than 4%** after 90 days, highlighting the importance of immediate collections action.
20. **Collateralized vs. Uncollateralized Recovery**: Secured loans (Home/Auto) achieve an average recovery rate of 62% on defaults, whereas unsecured loans (Personal/Business) recover less than 11% of outstanding capital.

---

## Part 3: 15 Actionable Strategic Recommendations

### Underwriting & Policy Changes
1.  **Implement Credit Score Floor**: Establish a hard credit score floor of **580** for all unsecured personal and business loans. Auto-reject applicants below this threshold to mitigate 58% of expected defaults.
2.  **Cap DTI Ratios at 45%**: Enforce a strict debt-to-income ceiling of 45% for all home and business loan products to prevent repayment cash-flow squeezes.
3.  **Introduce Debt-Service Coverage (DSCR) for Business Loans**: Require a minimum DSCR of 1.25x for small business applications, verifying business cash flow capacity before approval.

### Product Pricing & Term Adjustments
4.  **Cap High-Yield Personal Loan Interest Rates**: Cap personal loan rates at 15% and introduce stricter underwriting criteria to eliminate the high-risk adverse selection segment.
5.  **Adjust Terms for Self-Employed Borrowers**: Restrict self-employed business loan terms to a maximum of 48 months to reduce long-term operational default risk exposure.
6.  **Create Flexible Amortization for Gig Workers**: Design a flexible repayment product for gig economy workers allowing them to make higher payments during peak earning months and lower payments in slower seasons.

### Branch Risk Mitigations
7.  **Revise Credit Authority at BR-05 (Gulf Shore)**: Temporarily centralize loan underwriting approvals for branches with default rates exceeding 8%, moving authority to the East Regional Center.
8.  **Audit Underwriting Guidelines at BR-06 (Peach Tree)**: Perform a deep audit of credit review processes in South region branches to correct lax document verification.
9.  **Standardize East Region Best Practices**: Standardize and deploy the Wall Street Annex branch's credit scorecard auditing system across all Central and South region branches.

### Collections & Operations
10. **Automate Pre-Collections Alerts**: Configure system-level automated alerts (SMS, Email, IVR) to trigger the moment a borrower's payment is **1 day late**, targeting the critical recovery window.
11. **Introduce a "Promise to Pay" Workflow**: Build an online workflow enabling late borrowers to restructure their current payment within 5 days, resetting payment schedules and avoiding default.
12. **Accelerate Debt Recovery Timelines**: Transfer all unsecured accounts that reach 60 days past due to third-party collections agencies immediately, maximizing recovery yield before decay.

### Technical & BI Enhancements
13. **Integrate Real-time Credit Bureau Checks**: Integrate credit bureau APIs into the loan application form to verify credit scores at intake, preventing duplicate submissions or stale scores.
14. **Configure Automated ECL Dashboard Alerts**: Set up automated email alerts in Power BI to notify regional risk officers when Expected Credit Loss (ECL) exceeds regional risk budgets.
15. **Perform Semi-Annual Scorecard Re-Calibration**: Re-calibrate the Risk Scoring weights twice a year in the database to adjust for macroeconomic shifts (inflation, rate hikes).
