-- ==============================================================================
-- BANKING RISK & LOAN ANALYTICS PLATFORM
-- SQL ANALYTICS ENGINE (52 ANALYTICS QUERIES)
--
-- Target Dialect: ANSI-SQL / PostgreSQL
-- This file contains production-grade SQL scripts answering core business risk inquiries.
--
-- Table Schemas Reference:
-- 1. branches (Branch_ID, Branch_Name, Region, Manager)
-- 2. customers (Customer_ID, Customer_Name, Age, Gender, Occupation, Monthly_Income, Credit_Score, Join_Date)
-- 3. credit_history (Customer_ID, Debt_To_Income_Ratio, Existing_Loans_Count, Past_Delinquencies)
-- 4. loans (Loan_ID, Customer_ID, Loan_Type, Loan_Amount, Interest_Rate, Term_Months, Monthly_EMI, Branch_ID, Loan_Application_Date, Approval_Status)
-- 5. loan_payments (Payment_ID, Loan_ID, Payment_Month_Number, Payment_Date, Amount_Due, Amount_Paid, Interest_Component, Principal_Component, Payment_Status)
-- 6. defaults (Default_ID, Loan_ID, Default_Date, Default_Amount, Recovered_Amount, Default_Status)
-- 7. transactions (Transaction_ID, Loan_ID, Transaction_Date, Amount, Transaction_Type)
-- ==============================================================================

-- ==============================================================================
-- PART 1: BASIC & RELATIONAL FILTERING (10 QUERIES)
-- Grouping, Having, Ordering, and Demographics.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 01: Global Business and Risk KPIs
-- Business Objective: Determine total lending capital, total applications, and approval rates.
-- Logic: Aggregate Loan_Amount, count Loan_ID, and segment by Approval_Status.
-- Business Insight: Shows overall capital deployed and baseline loan approval ratios.
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(Loan_ID) AS Total_Applications,
    SUM(CASE WHEN Approval_Status = 'Approved' THEN 1 ELSE 0 END) AS Approved_Loans,
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END) AS Rejected_Loans,
    ROUND((SUM(CASE WHEN Approval_Status = 'Approved' THEN 1 ELSE 0 END)::NUMERIC / COUNT(Loan_ID) * 100), 2) AS Approval_Rate_PCT,
    ROUND(SUM(CASE WHEN Approval_Status = 'Approved' THEN Loan_Amount ELSE 0 END)::NUMERIC, 2) AS Total_Capital_Deployed
FROM loans;

-- ------------------------------------------------------------------------------
-- Query 02: Loan Portfolio Distribution
-- Business Objective: Identify which loan categories represent the largest share of our capital.
-- Logic: Group by Loan_Type, aggregate loan volume and average interest rate.
-- Business Insight: Reveals if the portfolio is overly concentrated in high-risk categories (e.g. Business loans).
-- ------------------------------------------------------------------------------
SELECT 
    Loan_Type,
    COUNT(Loan_ID) AS Loan_Count,
    ROUND(SUM(Loan_Amount)::NUMERIC, 2) AS Total_Disbursed,
    ROUND(AVG(Interest_Rate)::NUMERIC, 2) AS Avg_Interest_Rate,
    ROUND((SUM(Loan_Amount) / (SELECT SUM(Loan_Amount) FROM loans WHERE Approval_Status = 'Approved') * 100)::NUMERIC, 2) AS Portfolio_Share_PCT
FROM loans
WHERE Approval_Status = 'Approved'
GROUP BY Loan_Type
ORDER BY Total_Disbursed DESC;

-- ------------------------------------------------------------------------------
-- Query 03: Prime Customer Registry (Credit Score >= 750)
-- Business Objective: Extract high-value prime borrowers for target marketing.
-- Logic: Filter customers with Credit_Score >= 750, order by income.
-- Business Insight: These borrowers have the lowest default risk and are ideal for credit card cross-selling.
-- ------------------------------------------------------------------------------
SELECT 
    Customer_ID,
    Customer_Name,
    Age,
    Occupation,
    Monthly_Income,
    Credit_Score
FROM customers
WHERE Credit_Score >= 750
ORDER BY Monthly_Income DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 04: Long-Term Lending Exposure Audit
-- Business Objective: Identify loans stretched over 15+ years (180+ months).
-- Logic: Filter approved loans with Term_Months >= 180.
-- Business Insight: Highlights long-duration interest rate risk exposure.
-- ------------------------------------------------------------------------------
SELECT 
    Loan_ID,
    Customer_ID,
    Loan_Type,
    Loan_Amount,
    Term_Months,
    Interest_Rate
FROM loans
WHERE Term_Months >= 180 AND Approval_Status = 'Approved'
ORDER BY Loan_Amount DESC;

-- ------------------------------------------------------------------------------
-- Query 05: Customer Inflow Trends by Region
-- Business Objective: Monitor where new customer acquisition is concentrated geographically.
-- Logic: Join customers and branches, count customers per region.
-- Business Insight: Helps regional heads evaluate branch expansion effectiveness.
-- ------------------------------------------------------------------------------
SELECT 
    b.Region,
    COUNT(c.Customer_ID) AS Customer_Count,
    ROUND(AVG(c.Credit_Score), 2) AS Average_Credit_Score
FROM customers c
JOIN loans l ON c.Customer_ID = l.Customer_ID
JOIN branches b ON l.Branch_ID = b.Branch_ID
GROUP BY b.Region
ORDER BY Customer_Count DESC;

-- ------------------------------------------------------------------------------
-- Query 06: Income Distribution of Borrowers
-- Business Objective: Analyze credit risk profiles across occupation tiers.
-- Logic: Group by occupation, compute average income and credit score.
-- Business Insight: Identifies high-income cohorts representing potential wealth management leads.
-- ------------------------------------------------------------------------------
SELECT 
    Occupation,
    COUNT(Customer_ID) AS Customer_Count,
    ROUND(AVG(Monthly_Income)::NUMERIC, 2) AS Avg_Monthly_Income,
    ROUND(AVG(Credit_Score), 0) AS Avg_Credit_Score
FROM customers
GROUP BY Occupation
ORDER BY Avg_Monthly_Income DESC;

-- ------------------------------------------------------------------------------
-- Query 07: Regional Branch Count Audits
-- Business Objective: Review physical footprint distribution across territories.
-- Logic: Group by region, count physical branches.
-- Business Insight: Evaluates network density for retail operations planning.
-- ------------------------------------------------------------------------------
SELECT 
    Region,
    COUNT(Branch_ID) AS Active_Branches,
    STRING_AGG(Branch_Name, ', ') AS Branch_List
FROM branches
GROUP BY Region
ORDER BY Active_Branches DESC;

-- ------------------------------------------------------------------------------
-- Query 08: Rejected Loan Capital Demands
-- Business Objective: Measure the volume of lending demand the bank turned down.
-- Logic: Filter by 'Rejected' status, calculate total requested amount.
-- Business Insight: Quantifies the size of rejected credit demand, indicating market demand.
-- ------------------------------------------------------------------------------
SELECT 
    Loan_Type,
    COUNT(Loan_ID) AS Rejected_Count,
    ROUND(SUM(Loan_Amount)::NUMERIC, 2) AS Total_Rejected_Capital,
    ROUND(AVG(Loan_Amount)::NUMERIC, 2) AS Avg_Requested_Amount
FROM loans
WHERE Approval_Status = 'Rejected'
GROUP BY Loan_Type
ORDER BY Total_Rejected_Capital DESC;

-- ------------------------------------------------------------------------------
-- Query 09: Delinquency Distribution in Credit History
-- Business Objective: Understand structural payment behaviors before loan intake.
-- Logic: Group credit histories by past delinquencies.
-- Business Insight: Reveals if the intake pool includes a high number of serial delinquents.
-- ------------------------------------------------------------------------------
SELECT 
    Past_Delinquencies,
    COUNT(Customer_ID) AS Borrower_Count,
    ROUND((COUNT(Customer_ID)::NUMERIC / (SELECT COUNT(*) FROM credit_history) * 100), 2) AS Share_PCT
FROM credit_history
GROUP BY Past_Delinquencies
ORDER BY Past_Delinquencies;

-- ------------------------------------------------------------------------------
-- Query 10: High-Yield Personal Loans
-- Business Objective: Audit high-risk, high-interest personal loans.
-- Logic: Filter personal loans with Interest_Rate > 15%.
-- Business Insight: Highlights high-yield assets that require close default monitoring.
-- ------------------------------------------------------------------------------
SELECT 
    Loan_ID,
    Customer_ID,
    Loan_Amount,
    Interest_Rate,
    Monthly_EMI
FROM loans
WHERE Loan_Type = 'Personal Loan' AND Interest_Rate > 15.00 AND Approval_Status = 'Approved'
ORDER BY Interest_Rate DESC;


-- ==============================================================================
-- PART 2: MULTI-TABLE JOINS & LOAN AUDITS (10 QUERIES)
-- Inner, Outer Joins, and Multi-Table Relational Integrity.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 11: Master Loan Underwriting Log
-- Business Objective: Connect customer profiles with their active loan terms for credit auditing.
-- Logic: Join customers, loans, and branches.
-- Business Insight: Standard audit view mapping borrower details to physical branches.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_ID,
    c.Customer_Name,
    c.Credit_Score,
    l.Loan_Type,
    l.Loan_Amount,
    l.Interest_Rate,
    b.Branch_Name,
    b.Region
FROM loans l
JOIN customers c ON l.Customer_ID = c.Customer_ID
JOIN branches b ON l.Branch_ID = b.Branch_ID
WHERE l.Approval_Status = 'Approved'
ORDER BY l.Loan_Application_Date DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 12: Write-off Recoveries Analysis
-- Business Objective: Measure efficiency in recovering capital from defaulted accounts.
-- Logic: Join defaults and loans; calculate recovery rates.
-- Business Insight: High recovery rates on Home loans indicate strong collateral control.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_Type,
    COUNT(d.Default_ID) AS Default_Count,
    ROUND(SUM(d.Default_Amount)::NUMERIC, 2) AS Gross_Defaults,
    ROUND(SUM(d.Recovered_Amount)::NUMERIC, 2) AS Total_Recovered,
    ROUND((SUM(d.Recovered_Amount) / SUM(d.Default_Amount) * 100)::NUMERIC, 2) AS Recovery_Rate_PCT
FROM defaults d
JOIN loans l ON d.Loan_ID = l.Loan_ID
GROUP BY l.Loan_Type
ORDER BY Recovery_Rate_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 13: Total Interest Collected (Bank Revenue)
-- Business Objective: Calculate the net interest income generated by active loans.
-- Logic: Join loans and loan_payments; aggregate interest component.
-- Business Insight: Represents the core net margin revenue driver for retail operations.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_Type,
    COUNT(DISTINCT l.Loan_ID) AS Active_Loans,
    ROUND(SUM(lp.Amount_Paid)::NUMERIC, 2) AS Total_Collected,
    ROUND(SUM(lp.Interest_Component)::NUMERIC, 2) AS Interest_Collected,
    ROUND(SUM(lp.Principal_Component)::NUMERIC, 2) AS Principal_Recovered
FROM loan_payments lp
JOIN loans l ON lp.Loan_ID = l.Loan_ID
WHERE lp.Payment_Status <> 'Missed'
GROUP BY l.Loan_Type
ORDER BY Interest_Collected DESC;

-- ------------------------------------------------------------------------------
-- Query 14: Customer Lending Lifetime Value
-- Business Objective: Identify customer relationships that generated the highest interest.
-- Logic: Join customers, loans, and loan_payments; group by customer.
-- Business Insight: Highlights our most valuable borrowing relationships.
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    c.Occupation,
    COUNT(DISTINCT l.Loan_ID) AS Total_Loans,
    ROUND(SUM(lp.Interest_Component)::NUMERIC, 2) AS Lifetime_Interest_Paid
FROM customers c
JOIN loans l ON c.Customer_ID = l.Customer_ID
JOIN loan_payments lp ON l.Loan_ID = lp.Loan_ID
WHERE lp.Payment_Status <> 'Missed'
GROUP BY c.Customer_ID, c.Customer_Name, c.Occupation
ORDER BY Lifetime_Interest_Paid DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 15: Physical Branch Performance Metrics
-- Business Objective: Evaluate lending volume and default exposure by physical location.
-- Logic: Join branches, loans, and left join defaults.
-- Business Insight: Signals underperforming branches that require credit underwriting audits.
-- ------------------------------------------------------------------------------
SELECT 
    b.Branch_ID,
    b.Branch_Name,
    COUNT(l.Loan_ID) AS Loans_Approved,
    ROUND(SUM(l.Loan_Amount)::NUMERIC, 2) AS Total_Disbursed,
    COUNT(d.Default_ID) AS Defaults_Count,
    ROUND(SUM(d.Default_Amount)::NUMERIC, 2) AS Defaults_Volume
FROM branches b
JOIN loans l ON b.Branch_ID = l.Branch_ID AND l.Approval_Status = 'Approved'
LEFT JOIN defaults d ON l.Loan_ID = d.Loan_ID
GROUP BY b.Branch_ID, b.Branch_Name
ORDER BY Total_Disbursed DESC;

-- ------------------------------------------------------------------------------
-- Query 16: Late Payment Delinquency Runs
-- Business Objective: List customers with active payment delays to update collections queues.
-- Logic: Join loan_payments, loans, and customers; filter for 'Late' payments.
-- Business Insight: Provides the frontline collections team with their daily call list.
-- ------------------------------------------------------------------------------
SELECT 
    lp.Payment_ID,
    c.Customer_Name,
    c.Monthly_Income,
    l.Loan_Type,
    lp.Amount_Due,
    lp.Payment_Date,
    lp.Payment_Status
FROM loan_payments lp
JOIN loans l ON lp.Loan_ID = l.Loan_ID
JOIN customers c ON l.Customer_ID = c.Customer_ID
WHERE lp.Payment_Status = 'Late'
ORDER BY lp.Payment_Date DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 17: Missed Capital Recoveries Audit
-- Business Objective: Quantify outstanding interest lost from missed payments.
-- Logic: Sum missed interest components from loan_payments.
-- Business Insight: Measures the immediate profit drain resulting from late stage delinquencies.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_Type,
    COUNT(lp.Payment_ID) AS Missed_Payments_Count,
    ROUND(SUM(lp.Amount_Due)::NUMERIC, 2) AS Missed_Cash_Flow,
    ROUND(SUM(lp.Interest_Component)::NUMERIC, 2) AS Lost_Interest_Income
FROM loan_payments lp
JOIN loans l ON lp.Loan_ID = l.Loan_ID
WHERE lp.Payment_Status = 'Missed'
GROUP BY l.Loan_Type
ORDER BY Lost_Interest_Income DESC;

-- ------------------------------------------------------------------------------
-- Query 18: Unsecured Lending Exposure by Branch
-- Business Objective: Measure high-risk unsecured exposure (Personal & Business) by branch.
-- Logic: Join branches, loans, filter for unsecured types.
-- Business Insight: Monitors branch compliance with risk concentration caps.
-- ------------------------------------------------------------------------------
SELECT 
    b.Branch_Name,
    b.Region,
    COUNT(l.Loan_ID) AS Unsecured_Loans,
    ROUND(SUM(l.Loan_Amount)::NUMERIC, 2) AS Unsecured_Exposure
FROM loans l
JOIN branches b ON l.Branch_ID = b.Branch_ID
WHERE l.Loan_Type IN ('Personal Loan', 'Business Loan') AND l.Approval_Status = 'Approved'
GROUP BY b.Branch_Name, b.Region
ORDER BY Unsecured_Exposure DESC;

-- ------------------------------------------------------------------------------
-- Query 19: High-delinquency Customer Audits
-- Business Objective: Identify active borrowers with high pre-intake delinquencies.
-- Logic: Join customers, credit_history, loans; filter on past delinquencies >= 3.
-- Business Insight: Evaluates if underwriting allowed historical defaulters into the portfolio.
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    c.Credit_Score,
    ch.Past_Delinquencies,
    l.Loan_ID,
    l.Loan_Amount,
    l.Approval_Status
FROM customers c
JOIN credit_history ch ON c.Customer_ID = ch.Customer_ID
JOIN loans l ON c.Customer_ID = l.Customer_ID
WHERE ch.Past_Delinquencies >= 3
ORDER BY ch.Past_Delinquencies DESC, c.Credit_Score ASC;

-- ------------------------------------------------------------------------------
-- Query 20: Net Written-Off Capital Loss by Region
-- Business Objective: Calculate regional default write-offs net of collateral recoveries.
-- Logic: Join branches, loans, defaults; aggregate default minus recovery.
-- Business Insight: Pinpoints regional credit weaknesses.
-- ------------------------------------------------------------------------------
SELECT 
    b.Region,
    COUNT(d.Default_ID) AS Defaults_Count,
    ROUND(SUM(d.Default_Amount)::NUMERIC, 2) AS Gross_Defaults,
    ROUND(SUM(d.Recovered_Amount)::NUMERIC, 2) AS Total_Recoveries,
    ROUND((SUM(d.Default_Amount) - SUM(d.Recovered_Amount))::NUMERIC, 2) AS Net_Write_Off_Loss
FROM defaults d
JOIN loans l ON d.Loan_ID = l.Loan_ID
JOIN branches b ON l.Branch_ID = b.Branch_ID
GROUP BY b.Region
ORDER BY Net_Write_Off_Loss DESC;


-- ==============================================================================
-- PART 3: ADVANCED CONDITIONAL METRICS & SUBQUERIES (10 QUERIES)
-- Case When, Nested Subqueries, and Correlated sub-conditions.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 21: High-DTI Approval Audits
-- Business Objective: Check the approval volume of high DTI applicants (>0.50).
-- Logic: CASE WHEN nested in conditional selection.
-- Business Insight: Verifies underwriting compliance with DTI safety boundaries.
-- ------------------------------------------------------------------------------
SELECT 
    CASE WHEN ch.Debt_To_Income_Ratio > 0.50 THEN 'High DTI (>0.50)' ELSE 'Standard DTI (<=0.50)' END AS DTI_Risk_Tier,
    COUNT(l.Loan_ID) AS Applied,
    SUM(CASE WHEN l.Approval_Status = 'Approved' THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN l.Approval_Status = 'Approved' THEN 1 ELSE 0 END)::NUMERIC / COUNT(l.Loan_ID) * 100), 2) AS Approval_Rate_PCT
FROM loans l
JOIN credit_history ch ON l.Customer_ID = ch.Customer_ID
GROUP BY 
    CASE WHEN ch.Debt_To_Income_Ratio > 0.50 THEN 'High DTI (>0.50)' ELSE 'Standard DTI (<=0.50)' END;

-- ------------------------------------------------------------------------------
-- Query 22: Credit Score Metrics: Defaulted vs Active Loans
-- Business Objective: Prove the correlation between credit score and default rates.
-- Logic: Subqueries comparing average scores.
-- Business Insight: Provides the analytical basis for establishing credit score floors.
-- ------------------------------------------------------------------------------
SELECT 
    (SELECT ROUND(AVG(Credit_Score)) FROM customers c JOIN loans l ON c.Customer_ID = l.Customer_ID WHERE l.Approval_Status = 'Approved') AS Avg_Approved_Borrower_Score,
    (SELECT ROUND(AVG(Credit_Score)) FROM customers c JOIN loans l ON c.Customer_ID = l.Customer_ID JOIN defaults d ON l.Loan_ID = d.Loan_ID) AS Avg_Defaulted_Borrower_Score,
    (SELECT ROUND(AVG(Credit_Score)) FROM customers c JOIN loans l ON c.Customer_ID = l.Customer_ID WHERE l.Approval_Status = 'Rejected') AS Avg_Rejected_Score;

-- ------------------------------------------------------------------------------
-- Query 23: Payment Delinquencies in Gig Economy & Freelance Segments
-- Business Objective: Audit cash-flow delay rates for gig economy and freelance occupations.
-- Logic: CASE WHEN grouping payment status, joining customers.
-- Business Insight: Shows if seasonal earners show higher late payment rates.
-- ------------------------------------------------------------------------------
SELECT 
    c.Occupation,
    COUNT(lp.Payment_ID) AS Total_Due_Payments,
    ROUND((SUM(CASE WHEN lp.Payment_Status = 'Late' THEN 1 ELSE 0 END)::NUMERIC / COUNT(lp.Payment_ID) * 100), 2) AS Late_Rate_PCT,
    ROUND((SUM(CASE WHEN lp.Payment_Status = 'Missed' THEN 1 ELSE 0 END)::NUMERIC / COUNT(lp.Payment_ID) * 100), 2) AS Missed_Rate_PCT
FROM loan_payments lp
JOIN loans l ON lp.Loan_ID = l.Loan_ID
JOIN customers c ON l.Customer_ID = c.Customer_ID
WHERE c.Occupation IN ('Gig Economy Worker', 'Freelancer', 'Salaried Professional')
GROUP BY c.Occupation;

-- ------------------------------------------------------------------------------
-- Query 24: Largest Approved Loan per Branch (Correlated Subquery)
-- Business Objective: Identify the single largest lending exposure in each branch.
-- Logic: Correlated subquery matching Branch_ID.
-- Business Insight: Helps branch managers audit their largest single-client risks.
-- ------------------------------------------------------------------------------
SELECT 
    l1.Branch_ID,
    b.Branch_Name,
    l1.Loan_ID,
    l1.Loan_Type,
    l1.Loan_Amount
FROM loans l1
JOIN branches b ON l1.Branch_ID = b.Branch_ID
WHERE l1.Approval_Status = 'Approved' AND l1.Loan_Amount = (
    SELECT MAX(l2.Loan_Amount)
    FROM loans l2
    WHERE l2.Branch_ID = l1.Branch_ID AND l2.Approval_Status = 'Approved'
)
ORDER BY l1.Loan_Amount DESC;

-- ------------------------------------------------------------------------------
-- Query 25: Multi-Product Customers (Cross-Lending Audit)
-- Business Objective: Find customers holding multiple approved loans.
-- Logic: Subquery filtering grouped customer IDs with counts > 1.
-- Business Insight: Identifies highly engaged clients for VIP customer treatment.
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    c.Credit_Score,
    sub.Active_Approved_Loans
FROM customers c
JOIN (
    SELECT Customer_ID, COUNT(Loan_ID) AS Active_Approved_Loans
    FROM loans
    WHERE Approval_Status = 'Approved'
    GROUP BY Customer_ID
    HAVING COUNT(Loan_ID) > 1
) sub ON c.Customer_ID = sub.Customer_ID
ORDER BY sub.Active_Approved_Loans DESC;

-- ------------------------------------------------------------------------------
-- Query 26: Underperforming Branches - Above Regional Average Default Rate
-- Business Objective: Identify branches whose default rate exceeds the average default rate of their region.
-- Logic: Subquery calculating regional default ratios.
-- Business Insight: Focuses management attention on outlier branches with structural underwriting weaknesses.
-- ------------------------------------------------------------------------------
SELECT 
    l.Branch_ID,
    b.Branch_Name,
    b.Region,
    COUNT(l.Loan_ID) AS Approved_Loans,
    COUNT(d.Default_ID) AS Defaults_Count,
    ROUND((COUNT(d.Default_ID)::NUMERIC / COUNT(l.Loan_ID) * 100), 2) AS Branch_Default_Rate_PCT
FROM loans l
JOIN branches b ON l.Branch_ID = b.Branch_ID
LEFT JOIN defaults d ON l.Loan_ID = d.Loan_ID
WHERE l.Approval_Status = 'Approved'
GROUP BY l.Branch_ID, b.Branch_Name, b.Region
HAVING (COUNT(d.Default_ID)::NUMERIC / COUNT(l.Loan_ID) * 100) > (
    SELECT (COUNT(d_inner.Default_ID)::NUMERIC / COUNT(l_inner.Loan_ID) * 100)
    FROM loans l_inner
    JOIN branches b_inner ON l_inner.Branch_ID = b_inner.Branch_ID
    LEFT JOIN defaults d_inner ON l_inner.Loan_ID = d_inner.Loan_ID
    WHERE l_inner.Approval_Status = 'Approved' AND b_inner.Region = b.Region
)
ORDER BY Branch_Default_Rate_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 27: Customer Credit Tier Classification
-- Business Objective: Segment our borrowing customer base into credit risk bands.
-- Logic: CASE WHEN statements grouping credit scores.
-- Business Insight: Aligns the database with credit bureau standards.
-- ------------------------------------------------------------------------------
SELECT 
    Customer_ID,
    Customer_Name,
    Credit_Score,
    CASE 
        WHEN Credit_Score >= 750 THEN 'Super Prime (>=750)'
        WHEN Credit_Score >= 680 AND Credit_Score < 750 THEN 'Prime (680-749)'
        WHEN Credit_Score >= 620 AND Credit_Score < 680 THEN 'Near Prime (620-679)'
        WHEN Credit_Score >= 580 AND Credit_Score < 620 THEN 'Subprime (580-619)'
        ELSE 'Deep Subprime (<580)'
    END AS Credit_Score_Band
FROM customers
ORDER BY Credit_Score DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 28: Loan Types Exceeding Global Default Rate
-- Business Objective: Identify loan types carrying above-average default rates.
-- Logic: Group default rates compared to global default rate in HAVING subquery.
-- Business Insight: Guides product managers to tighten criteria on high-default products.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_Type,
    COUNT(l.Loan_ID) AS Approved_Loans,
    COUNT(d.Default_ID) AS Defaults_Count,
    ROUND((COUNT(d.Default_ID)::NUMERIC / COUNT(l.Loan_ID) * 100), 2) AS Product_Default_Rate_PCT
FROM loans l
LEFT JOIN defaults d ON l.Loan_ID = d.Loan_ID
WHERE l.Approval_Status = 'Approved'
GROUP BY l.Loan_Type
HAVING (COUNT(d.Default_ID)::NUMERIC / COUNT(l.Loan_ID) * 100) > (
    SELECT (COUNT(d_g.Default_ID)::NUMERIC / COUNT(l_g.Loan_ID) * 100)
    FROM loans l_g
    LEFT JOIN defaults d_g ON l_g.Loan_ID = d_g.Loan_ID
    WHERE l_g.Approval_Status = 'Approved'
)
ORDER BY Product_Default_Rate_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 29: Loan Interest Rates Above Product Type Averages
-- Business Objective: Identify loans carrying higher rates than the average for their type.
-- Logic: Correlated subquery checking Interest_Rate against type averages.
-- Business Insight: Highlights loans that may have high risk or high pricing terms.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_ID,
    l.Customer_ID,
    l.Loan_Type,
    l.Interest_Rate,
    ROUND((SELECT AVG(l_avg.Interest_Rate) FROM loans l_avg WHERE l_avg.Loan_Type = l.Loan_Type AND l_avg.Approval_Status = 'Approved')::NUMERIC, 2) AS Product_Avg_Rate
FROM loans l
WHERE l.Approval_Status = 'Approved' AND l.Interest_Rate > (
    SELECT AVG(l_avg.Interest_Rate)
    FROM loans l_avg
    WHERE l_avg.Loan_Type = l.Loan_Type AND l_avg.Approval_Status = 'Approved'
)
ORDER BY l.Loan_Type, l.Interest_Rate DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 30: Unprofitable Branches Audit
-- Business Objective: Find branches where net default losses exceed collected interest.
-- Logic: Sum collected interest and compare with defaults in a HAVING subquery.
-- Business Insight: Signals critical structural risk at specific branches.
-- ------------------------------------------------------------------------------
SELECT 
    b.Branch_ID,
    b.Branch_Name,
    ROUND(SUM(lp.Interest_Component)::NUMERIC, 2) AS Collected_Interest,
    COALESCE(ROUND(d.Loss_Amt::NUMERIC, 2), 0.00) AS Default_Capital_Loss,
    ROUND((SUM(lp.Interest_Component) - COALESCE(d.Loss_Amt, 0))::NUMERIC, 2) AS Net_Earnings
FROM branches b
JOIN loans l ON b.Branch_ID = l.Branch_ID AND l.Approval_Status = 'Approved'
JOIN loan_payments lp ON l.Loan_ID = lp.Loan_ID AND lp.Payment_Status <> 'Missed'
LEFT JOIN (
    SELECT l_inner.Branch_ID, SUM(d_inner.Default_Amount - d_inner.Recovered_Amount) AS Loss_Amt
    FROM defaults d_inner
    JOIN loans l_inner ON d_inner.Loan_ID = l_inner.Loan_ID
    GROUP BY l_inner.Branch_ID
) d ON b.Branch_ID = d.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name, d.Loss_Amt
HAVING COALESCE(d.Loss_Amt, 0) > SUM(lp.Interest_Component)
ORDER BY Net_Earnings ASC;


-- ==============================================================================
-- PART 4: COMMON TABLE EXPRESSIONS (CTEs) & RISK MODELS (10 QUERIES)
-- Multi-step analytics, roll rates, LTV, and cohort performance.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 31: Monthly Loan Disbursement Volume Trends
-- Business Objective: Evaluate credit demand growth and deployment volumes month-over-month.
-- Logic: CTE aggregations grouped by year and month.
-- Business Insight: Measures business development team target achievement.
-- ------------------------------------------------------------------------------
WITH Monthly_Disbursements AS (
    SELECT 
        EXTRACT(YEAR FROM Loan_Application_Date::DATE) AS Loan_Year,
        EXTRACT(MONTH FROM Loan_Application_Date::DATE) AS Loan_Month,
        SUM(Loan_Amount) AS Capital_Volume
    FROM loans
    WHERE Approval_Status = 'Approved'
    GROUP BY EXTRACT(YEAR FROM Loan_Application_Date::DATE), EXTRACT(MONTH FROM Loan_Application_Date::DATE)
)
SELECT 
    cur.Loan_Month,
    ROUND(SUM(CASE WHEN cur.Loan_Year = 2023 THEN cur.Capital_Volume ELSE 0 END)::NUMERIC, 2) AS Volume_2023,
    ROUND(SUM(CASE WHEN cur.Loan_Year = 2024 THEN cur.Capital_Volume ELSE 0 END)::NUMERIC, 2) AS Volume_2024,
    ROUND(SUM(CASE WHEN cur.Loan_Year = 2025 THEN cur.Capital_Volume ELSE 0 END)::NUMERIC, 2) AS Volume_2025
FROM Monthly_Disbursements cur
GROUP BY cur.Loan_Month
ORDER BY cur.Loan_Month;

-- ------------------------------------------------------------------------------
-- Query 32: Monthly Customer Join Cohorts
-- Business Objective: Monitor historical customer acquisition growth rates.
-- Logic: CTE counting customer records by registration month.
-- Business Insight: Assesses marketing acquisition channel efficiency.
-- ------------------------------------------------------------------------------
WITH Customer_Cohorts AS (
    SELECT 
        TO_CHAR(Join_Date::DATE, 'YYYY-MM') AS Cohort_Month,
        Customer_ID
    FROM customers
)
SELECT 
    Cohort_Month,
    COUNT(Customer_ID) AS New_Acquisitions
FROM Customer_Cohorts
GROUP BY Cohort_Month
ORDER BY Cohort_Month;

-- ------------------------------------------------------------------------------
-- Query 33: First-Payment Delinquency Velocity
-- Business Objective: Measure the average months active before a loan records its first late payment.
-- Logic: CTE identifying first late/missed payment month number per loan.
-- Business Insight: Early delinquencies (months 1-3) indicate fraud or poor credit screening.
-- ------------------------------------------------------------------------------
WITH First_Delinquencies AS (
    SELECT 
        Loan_ID,
        MIN(Payment_Month_Number) AS First_Delinquent_Month
    FROM loan_payments
    WHERE Payment_Status IN ('Late', 'Missed')
    GROUP BY Loan_ID
)
SELECT 
    l.Loan_Type,
    COUNT(fd.Loan_ID) AS Delinquent_Loans_Count,
    ROUND(AVG(fd.First_Delinquent_Month), 1) AS Avg_Months_Before_First_Delinquency
FROM First_Delinquencies fd
JOIN loans l ON fd.Loan_ID = l.Loan_ID
GROUP BY l.Loan_Type
ORDER BY Avg_Months_Before_First_Delinquency ASC;

-- ------------------------------------------------------------------------------
-- Query 34: Capital Concentration by Risk Category
-- Business Objective: Measure the concentration of our credit exposure across risk tiers.
-- Logic: Join loans, customers, credit_history to calculate score, group by tier.
-- Business Insight: High concentration in Critical/High risk indicates portfolio vulnerability.
-- ------------------------------------------------------------------------------
WITH Risk_Score_Model AS (
    SELECT 
        l.Loan_ID,
        l.Loan_Amount,
        (850 - c.Credit_Score) / 550.0 * 40 +
        (ch.Debt_To_Income_Ratio - 0.10) / 0.60 * 20 +
        (CASE WHEN c.Occupation = 'Gig Economy Worker' THEN 12 WHEN c.Occupation = 'Freelancer' THEN 8 ELSE 0 END) +
        (ch.Past_Delinquencies * 5) AS Score
    FROM loans l
    JOIN customers c ON l.Customer_ID = c.Customer_ID
    JOIN credit_history ch ON c.Customer_ID = ch.Customer_ID
    WHERE l.Approval_Status = 'Approved'
),
Risk_Tiers AS (
    SELECT 
        Loan_ID,
        Loan_Amount,
        CASE 
            WHEN Score < 30 THEN 'Low Risk'
            WHEN Score < 55 THEN 'Medium Risk'
            WHEN Score < 75 THEN 'High Risk'
            ELSE 'Critical Risk'
        END AS Risk_Tier
    FROM Risk_Score_Model
)
SELECT 
    Risk_Tier,
    COUNT(Loan_ID) AS Loans_Count,
    ROUND(SUM(Loan_Amount)::NUMERIC, 2) AS Capital_Exposure,
    ROUND((SUM(Loan_Amount) / (SELECT SUM(Loan_Amount) FROM loans WHERE Approval_Status = 'Approved') * 100)::NUMERIC, 2) AS Exposure_PCT
FROM Risk_Tiers
GROUP BY Risk_Tier
ORDER BY Exposure_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 35: Top 3 Borrowers per Region
-- Business Objective: Track the largest credit exposures in each geographic region.
-- Logic: CTE with window function DENSE_RANK partitioned by Region.
-- Business Insight: Ensures high exposures are monitored by regional credit heads.
-- ------------------------------------------------------------------------------
WITH Regional_Borrowers AS (
    SELECT 
        b.Region,
        c.Customer_ID,
        c.Customer_Name,
        SUM(l.Loan_Amount) AS Total_Borrowed,
        DENSE_RANK() OVER (PARTITION BY b.Region ORDER BY SUM(l.Loan_Amount) DESC) AS Rank_Within_Region
    FROM loans l
    JOIN customers c ON l.Customer_ID = c.Customer_ID
    JOIN branches b ON l.Branch_ID = b.Branch_ID
    WHERE l.Approval_Status = 'Approved'
    GROUP BY b.Region, c.Customer_ID, c.Customer_Name
)
SELECT 
    Region,
    Rank_Within_Region,
    Customer_ID,
    Customer_Name,
    ROUND(Total_Borrowed::NUMERIC, 2) AS Borrowed_Capital
FROM Regional_Borrowers
WHERE Rank_Within_Region <= 3
ORDER BY Region, Rank_Within_Region;

-- ------------------------------------------------------------------------------
-- Query 36: Quarterly Default Volatility
-- Business Objective: Track how defaults evolve quarter-over-quarter.
-- Logic: CTE summarizing defaults by year and quarter.
-- Business Insight: Highlights default acceleration rates.
-- ------------------------------------------------------------------------------
WITH Quarterly_Defaults AS (
    SELECT 
        EXTRACT(YEAR FROM Default_Date::DATE) AS Fiscal_Year,
        EXTRACT(QUARTER FROM Default_Date::DATE) AS Fiscal_Quarter,
        COUNT(Default_ID) AS Default_Count,
        SUM(Default_Amount) AS Default_Volume
    FROM defaults
    GROUP BY EXTRACT(YEAR FROM Default_Date::DATE), EXTRACT(QUARTER FROM Default_Date::DATE)
)
SELECT 
    Fiscal_Year,
    Fiscal_Quarter,
    Default_Count,
    ROUND(Default_Volume::NUMERIC, 2) AS Default_Capital
FROM Quarterly_Defaults
ORDER BY Fiscal_Year, Fiscal_Quarter;

-- ------------------------------------------------------------------------------
-- Query 37: Customer Loan Application Sequence
-- Business Objective: Understand the product sequence path that repeat borrowers take.
-- Logic: CTE using ROW_NUMBER to rank customer loans chronologically.
-- Business Insight: Informs product offering pathways for repeat customers.
-- ------------------------------------------------------------------------------
WITH Customer_Loan_Timeline AS (
    SELECT 
        Customer_ID,
        Loan_Type,
        Loan_Application_Date,
        ROW_NUMBER() OVER (PARTITION BY Customer_ID ORDER BY Loan_Application_Date ASC) AS Sequence_Number
    FROM loans
    WHERE Approval_Status = 'Approved'
)
SELECT 
    Sequence_Number,
    Loan_Type,
    COUNT(Customer_ID) AS Borrowers_Count
FROM Customer_Loan_Timeline
WHERE Sequence_Number <= 3
GROUP BY Sequence_Number, Loan_Type
ORDER BY Sequence_Number, Borrowers_Count DESC;

-- ------------------------------------------------------------------------------
-- Query 38: Delinquency Score Impact on Portfolio defaults
-- Business Objective: Determine how pre-intake delinquencies affect default rates.
-- Logic: CTE grouping by past delinquencies, calculating default rates.
-- Business Insight: Provides empirical proof that past delinquencies drive future defaults.
-- ------------------------------------------------------------------------------
WITH Intake_Pool AS (
    SELECT 
        ch.Past_Delinquencies,
        l.Loan_ID,
        CASE WHEN d.Default_ID IS NOT NULL THEN 1 ELSE 0 END AS Has_Defaulted
    FROM loans l
    JOIN credit_history ch ON l.Customer_ID = ch.Customer_ID
    LEFT JOIN defaults d ON l.Loan_ID = d.Loan_ID
    WHERE l.Approval_Status = 'Approved'
)
SELECT 
    Past_Delinquencies,
    COUNT(Loan_ID) AS Approved_Loans,
    SUM(Has_Defaulted) AS Defaulted_Loans,
    ROUND((SUM(Has_Defaulted)::NUMERIC / COUNT(Loan_ID) * 100), 2) AS Default_Rate_PCT
FROM Intake_Pool
GROUP BY Past_Delinquencies
ORDER BY Past_Delinquencies;

-- ------------------------------------------------------------------------------
-- Query 39: Net Portfolio Yield
-- Business Objective: Calculate the net return rate of product lines after defaults.
-- Logic: CTE aggregating interest income minus net default loss.
-- Business Insight: Crucial strategic metric indicating true product profitability.
-- ------------------------------------------------------------------------------
WITH Product_Earnings AS (
    SELECT 
        l.Loan_Type,
        SUM(lp.Interest_Component) AS Gross_Interest
    FROM loan_payments lp
    JOIN loans l ON lp.Loan_ID = l.Loan_ID
    WHERE lp.Payment_Status <> 'Missed'
    GROUP BY l.Loan_Type
),
Product_Losses AS (
    SELECT 
        l.Loan_Type,
        SUM(d.Default_Amount - d.Recovered_Amount) AS Net_Default_Loss
    FROM defaults d
    JOIN loans l ON d.Loan_ID = l.Loan_ID
    GROUP BY l.Loan_Type
)
SELECT 
    pe.Loan_Type,
    ROUND(pe.Gross_Interest::NUMERIC, 2) AS Interest_Revenue,
    ROUND(COALESCE(pl.Net_Default_Loss, 0.00)::NUMERIC, 2) AS Default_Losses,
    ROUND((pe.Gross_Interest - COALESCE(pl.Net_Default_Loss, 0))::NUMERIC, 2) AS Net_Portfolio_Earnings
FROM Product_Earnings pe
LEFT JOIN Product_Losses pl ON pe.Loan_Type = pl.Loan_Type
ORDER BY Net_Portfolio_Earnings DESC;

-- ------------------------------------------------------------------------------
-- Query 40: Customer Repayment Interval Latency
-- Business Objective: Identify payment date variances for repeat late payers.
-- Logic: CTE with LAG comparing payment dates for delinquent accounts.
-- Business Insight: Shows if late-payers pay consistently late or slip deeper monthly.
-- ------------------------------------------------------------------------------
WITH Late_Payments_Sequence AS (
    SELECT 
        Loan_ID,
        Payment_Date::DATE AS Pmt_Date,
        LAG(Payment_Date::DATE) OVER (PARTITION BY Loan_ID ORDER BY Payment_Date::DATE) AS Prev_Pmt_Date
    FROM loan_payments
    WHERE Payment_Status = 'Late'
)
SELECT 
    ROUND(AVG(Pmt_Date - Prev_Pmt_Date), 1) AS Average_Days_Between_Late_Payments
FROM Late_Payments_Sequence
WHERE Prev_Pmt_Date IS NOT NULL;


-- ==============================================================================
-- PART 5: ADVANCED WINDOW FUNCTIONS (12 QUERIES)
-- LAG, LEAD, RANK, DENSE_RANK, ROW_NUMBER, running sums, and rolling metrics.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 41: Cumulative Deployed Capital by Branch
-- Business Objective: Track physical branches' cumulative loan volume growth.
-- Logic: SUM() OVER ordered by Date partitioned by Branch_ID.
-- Business Insight: Monitors the growth speed of new branch portfolios.
-- ------------------------------------------------------------------------------
SELECT 
    l.Loan_ID,
    l.Loan_Application_Date,
    b.Branch_Name,
    l.Loan_Amount,
    ROUND(SUM(l.Loan_Amount) OVER (PARTITION BY l.Branch_ID ORDER BY l.Loan_Application_Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)::NUMERIC, 2) AS Cumulative_Branch_Lending
FROM loans l
JOIN branches b ON l.Branch_ID = b.Branch_ID
WHERE l.Approval_Status = 'Approved'
ORDER BY l.Branch_ID, l.Loan_Application_Date
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 42: Month-over-Month Loan Applications Growth Rate
-- Business Objective: Evaluate lending business momentum.
-- Logic: LAG to fetch previous month application count.
-- Business Insight: Identifies if credit demand is decelerating.
-- ------------------------------------------------------------------------------
WITH Monthly_Applications AS (
    SELECT 
        TO_CHAR(Loan_Application_Date::DATE, 'YYYY-MM') AS Year_Month,
        COUNT(Loan_ID) AS Application_Count
    FROM loans
    GROUP BY TO_CHAR(Loan_Application_Date::DATE, 'YYYY-MM')
)
SELECT 
    Year_Month,
    Application_Count,
    LAG(Application_Count) OVER (ORDER BY Year_Month) AS Prior_Month_Applications,
    ROUND(((Application_Count - LAG(Application_Count) OVER (ORDER BY Year_Month))::NUMERIC / 
           LAG(Application_Count) OVER (ORDER BY Year_Month) * 100), 2) AS MoM_Growth_Rate_PCT
FROM Monthly_Applications
ORDER BY Year_Month;

-- ------------------------------------------------------------------------------
-- Query 43: Rolling 3-Month Interest Revenue Trend (Moving Average)
-- Business Objective: Smooth monthly interest variations to identify structural income growth.
-- Logic: AVG() OVER with 2 preceding rows.
-- Business Insight: Key metric for financial forecasting and cash flow planning.
-- ------------------------------------------------------------------------------
WITH Monthly_Interest AS (
    SELECT 
        TO_CHAR(lp.Payment_Date::DATE, 'YYYY-MM') AS Year_Month,
        SUM(lp.Interest_Component) AS Interest_Collected
    FROM loan_payments lp
    WHERE lp.Payment_Status <> 'Missed'
    GROUP BY TO_CHAR(lp.Payment_Date::DATE, 'YYYY-MM')
)
SELECT 
    Year_Month,
    ROUND(Interest_Collected::NUMERIC, 2) AS Current_Month_Interest,
    ROUND(AVG(Interest_Collected) OVER (ORDER BY Year_Month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)::NUMERIC, 2) AS Rolling_3M_Avg_Interest
FROM Monthly_Interest
ORDER BY Year_Month;

-- ------------------------------------------------------------------------------
-- Query 44: Rank Borrowers by Income within Branch
-- Business Objective: Identify the highest-income clients per branch.
-- Logic: DENSE_RANK partitioned by Branch_ID ordered by Monthly_Income.
-- Business Insight: Useful for branch managers to identify wealth management leads.
-- ------------------------------------------------------------------------------
WITH Ranked_Customers AS (
    SELECT 
        l.Branch_ID,
        b.Branch_Name,
        c.Customer_ID,
        c.Customer_Name,
        c.Monthly_Income,
        DENSE_RANK() OVER (PARTITION BY l.Branch_ID ORDER BY c.Monthly_Income DESC) AS Income_Rank
    FROM loans l
    JOIN customers c ON l.Customer_ID = c.Customer_ID
    JOIN branches b ON l.Branch_ID = b.Branch_ID
    WHERE l.Approval_Status = 'Approved'
    GROUP BY l.Branch_ID, b.Branch_Name, c.Customer_ID, c.Customer_Name, c.Monthly_Income
)
SELECT 
    Branch_Name,
    Income_Rank,
    Customer_ID,
    Customer_Name,
    ROUND(Monthly_Income::NUMERIC, 2) AS Income
FROM Ranked_Customers
WHERE Income_Rank <= 3
ORDER BY Branch_Name, Income_Rank;

-- ------------------------------------------------------------------------------
-- Query 45: Payment Number Indexing
-- Business Objective: Index chronological payments for audit control.
-- Logic: ROW_NUMBER partitioned by Loan_ID.
-- Business Insight: Audits complete receipt history matching billing terms.
-- ------------------------------------------------------------------------------
SELECT 
    Loan_ID,
    ROW_NUMBER() OVER (PARTITION BY Loan_ID ORDER BY Payment_Date) AS Payment_Sequence_Index,
    Payment_ID,
    Payment_Date,
    Amount_Paid,
    Payment_Status
FROM loan_payments
ORDER BY Loan_ID, Payment_Sequence_Index
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 46: Rolling 7-Payment Delay Trend lines
-- Business Objective: Detect if payment delays are worsening.
-- Logic: AVG(delays) OVER with 6 preceding rows.
-- Business Insight: Shows if collection operations are losing efficiency.
-- ------------------------------------------------------------------------------
WITH Payment_Delays AS (
    SELECT 
        Payment_ID,
        Payment_Date::DATE AS Pmt_Date,
        CASE WHEN Payment_Status = 'Late' THEN 1 ELSE 0 END AS Is_Late
    FROM loan_payments
)
SELECT 
    Payment_ID,
    Pmt_Date,
    Is_Late,
    ROUND(AVG(Is_Late) OVER (ORDER BY Pmt_Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) * 100, 2) AS Rolling_7Pmt_Late_Rate_PCT
FROM Payment_Delays
ORDER BY Pmt_Date
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 47: Consecutiveness Check for Missed Payments
-- Business Objective: Detect loans with consecutive missed payments before default.
-- Logic: LAG and LEAD checking adjacent payment status.
-- Business Insight: Acts as an early warning alert system for collections managers.
-- ------------------------------------------------------------------------------
WITH Payment_Sequence AS (
    SELECT 
        Loan_ID,
        Payment_Month_Number,
        Payment_Status,
        LAG(Payment_Status) OVER (PARTITION BY Loan_ID ORDER BY Payment_Month_Number) AS Prev_Status,
        LAG(Payment_Status, 2) OVER (PARTITION BY Loan_ID ORDER BY Payment_Month_Number) AS Prev_2_Status
    FROM loan_payments
)
SELECT 
    Loan_ID,
    Payment_Month_Number,
    Payment_Status,
    Prev_Status,
    Prev_2_Status
FROM Payment_Sequence
WHERE Payment_Status = 'Missed' AND Prev_Status = 'Missed' AND Prev_2_Status = 'Missed'
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 48: Lifecycle Repayment Behaviors (First & Last status)
-- Business Objective: Compare customer payment status at onboarding vs their latest status.
-- Logic: FIRST_VALUE and LAST_VALUE window functions.
-- Business Insight: Checks if payment behaviors deteriorate over time.
-- ------------------------------------------------------------------------------
WITH Lifecycle_Payments AS (
    SELECT 
        Loan_ID,
        Payment_Status,
        ROW_NUMBER() OVER (PARTITION BY Loan_ID ORDER BY Payment_Month_Number ASC) AS Row_Asc,
        ROW_NUMBER() OVER (PARTITION BY Loan_ID ORDER BY Payment_Month_Number DESC) AS Row_Desc
    FROM loan_payments
)
SELECT 
    Loan_ID,
    MAX(CASE WHEN Row_Asc = 1 THEN Payment_Status END) AS Onboarding_Payment_Status,
    MAX(CASE WHEN Row_Desc = 1 THEN Payment_Status END) AS Latest_Payment_Status
FROM Lifecycle_Payments
GROUP BY Loan_ID
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 49: Outlier High-EMI Loans (Top 5% highest EMIs)
-- Business Objective: Identify loans carrying high monthly payments.
-- Logic: NTILE(20) bucket classification of EMIs.
-- Business Insight: High EMIs represent massive repayment stress risk.
-- ------------------------------------------------------------------------------
WITH Emi_Buckets AS (
    SELECT 
        Loan_ID,
        Customer_ID,
        Monthly_EMI,
        NTILE(20) OVER (ORDER BY Monthly_EMI DESC) AS Emi_Ventile
    FROM loans
    WHERE Approval_Status = 'Approved'
)
SELECT 
    Loan_ID,
    Customer_ID,
    ROUND(Monthly_EMI::NUMERIC, 2) AS EMI,
    CASE WHEN Emi_Ventile = 1 THEN 'Outlier High EMI (Top 5%)' ELSE 'Standard EMI' END AS Outlier_Label
FROM Emi_Buckets
WHERE Emi_Ventile = 1
ORDER BY Monthly_EMI DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 50: Product Share and Cumulative Revenue Contribution
-- Business Objective: Measure the contribution share of product lines.
-- Logic: SUM and Ratio OVER partitions.
-- Business Insight: Shows which products drive the bulk of interest revenues.
-- ------------------------------------------------------------------------------
WITH Product_Interest AS (
    SELECT 
        l.Loan_Type,
        SUM(lp.Interest_Component) AS Collected_Interest
    FROM loan_payments lp
    JOIN loans l ON lp.Loan_ID = l.Loan_ID
    WHERE lp.Payment_Status <> 'Missed'
    GROUP BY l.Loan_Type
)
SELECT 
    Loan_Type,
    ROUND(Collected_Interest::NUMERIC, 2) AS Total_Interest,
    ROUND((Collected_Interest / SUM(Collected_Interest) OVER () * 100)::NUMERIC, 2) AS Share_PCT
FROM Product_Interest
ORDER BY Collected_Interest DESC;

-- ------------------------------------------------------------------------------
-- Query 51: Expected Credit Loss (ECL) Calculation by Branch
-- Business Objective: Calculate Expected Credit Loss (ECL) by branch.
-- Logic: ECL = Loan_Amount * PD (Probability of Default based on credit score) * LGD (0.85).
-- Business Insight: Highlights branch risk exposure for loss reserve allocation.
-- ------------------------------------------------------------------------------
WITH Loan_PD AS (
    SELECT 
        l.Branch_ID,
        l.Loan_Amount,
        CASE 
            WHEN c.Credit_Score < 580 THEN 0.45 
            WHEN c.Credit_Score < 680 THEN 0.12 
            ELSE 0.02 
        END AS PD
    FROM loans l
    JOIN customers c ON l.Customer_ID = c.Customer_ID
    WHERE l.Approval_Status = 'Approved'
),
Branch_ECL AS (
    SELECT 
        Branch_ID,
        SUM(Loan_Amount * PD * 0.85) AS Expected_Credit_Loss
    FROM Loan_PD
    GROUP BY Branch_ID
)
SELECT 
    b.Branch_Name,
    b.Region,
    ROUND(be.Expected_Credit_Loss::NUMERIC, 2) AS ECL_Reserves_Needed
FROM Branch_ECL be
JOIN branches b ON be.Branch_ID = b.Branch_ID
ORDER BY ECL_Reserves_Needed DESC;

-- ------------------------------------------------------------------------------
-- Query 52: Manager Performance Recoveries Ranking
-- Business Objective: Rank branch managers by collection recovery rates.
-- Logic: Join branches, loans, defaults, aggregate recoveries and rank.
-- Business Insight: Evaluates manager collections team effectiveness.
-- ------------------------------------------------------------------------------
WITH Manager_Recoveries AS (
    SELECT 
        b.Manager,
        b.Branch_Name,
        SUM(d.Default_Amount) AS Dealt_Amt,
        SUM(d.Recovered_Amount) AS Rec_Amt
    FROM defaults d
    JOIN loans l ON d.Loan_ID = l.Loan_ID
    JOIN branches b ON l.Branch_ID = b.Branch_ID
    GROUP BY b.Manager, b.Branch_Name
),
Ranked_Managers AS (
    SELECT 
        Manager,
        Branch_Name,
        ROUND(Dealt_Amt::NUMERIC, 2) AS Default_Volume,
        ROUND(Rec_Amt::NUMERIC, 2) AS Recovered_Volume,
        ROUND((Rec_Amt / Dealt_Amt * 100)::NUMERIC, 2) AS Recovery_Rate_PCT,
        RANK() OVER (ORDER BY (Rec_Amt / Dealt_Amt) DESC) AS Manager_Rank
    FROM Manager_Recoveries
    WHERE Dealt_Amt > 0
)
SELECT 
    Manager_Rank,
    Manager,
    Branch_Name,
    Default_Volume,
    Recovered_Volume,
    Recovery_Rate_PCT
FROM Ranked_Managers
ORDER BY Manager_Rank;
