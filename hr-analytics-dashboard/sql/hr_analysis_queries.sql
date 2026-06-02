-- ==========================================
-- HR Analytics Dashboard - Database Analysis Queries
-- Target Engine: Standard ANSI SQL (PostgreSQL, MySQL, SQLite, SQL Server)
-- Purpose: Analytical SQL queries for extracting key HR metrics & business insights.
-- Focus: CTEs, Window Functions, Aggregations, CASE statements, and Subqueries.
-- ==========================================

-- --------------------------------------------------
-- QUERY 1: Executive KPI Metrics (Overview)
-- Calculates Total Employees, Active Employees, Attrition Count, and Attrition Rate.
-- Demonstrates: CASE statements, COUNT, SUM, and basic math.
-- --------------------------------------------------
SELECT 
    COUNT(EmployeeID) AS Total_Employees,
    SUM(CASE WHEN Attrition = 'No' THEN 1 ELSE 0 END) AS Active_Employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Attrition_Count,
    ROUND(
        (SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(EmployeeID)) * 100, 
        2
    ) AS Attrition_Rate_Pct,
    ROUND(AVG(Salary), 2) AS Average_Salary,
    ROUND(AVG(YearsAtCompany), 1) AS Average_Experience_Years
FROM hr_employee_data;


-- --------------------------------------------------
-- QUERY 2: Department-wise Attrition Analysis
-- Segregates employees, active, and attrition metrics by business unit.
-- Demonstrates: GROUP BY, ORDER BY, and percentages.
-- --------------------------------------------------
SELECT 
    Department,
    COUNT(EmployeeID) AS Total_Employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Attrition_Count,
    ROUND(
        (SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(EmployeeID)) * 100, 
        2
    ) AS Attrition_Rate_Pct,
    ROUND(AVG(Salary), 2) AS Avg_Salary
FROM hr_employee_data
GROUP BY Department
ORDER BY Attrition_Rate_Pct DESC;


-- --------------------------------------------------
-- QUERY 3: Gender Distribution and Retention Analysis
-- Analyzes staffing counts and retention statistics across genders.
-- Demonstrates: GROUP BY, CASE, and formatting ratios.
-- --------------------------------------------------
SELECT 
    Gender,
    COUNT(EmployeeID) AS Total_Employees,
    SUM(CASE WHEN Attrition = 'No' THEN 1 ELSE 0 END) AS Active_Employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Attrition_Count,
    ROUND(
        (SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(EmployeeID)) * 100, 
        2
    ) AS Attrition_Rate_Pct
FROM hr_employee_data
GROUP BY Gender
ORDER BY Total_Employees DESC;


-- --------------------------------------------------
-- QUERY 4: Overtime Impact on Employee Turnover
-- CTE to isolate Attrition rates between Overtime and Non-Overtime employee segments.
-- Demonstrates: Common Table Expressions (CTEs), Subqueries, and division.
-- --------------------------------------------------
WITH OvertimeSummary AS (
    SELECT 
        Overtime,
        COUNT(EmployeeID) AS Total_Staff,
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Exited_Staff
    FROM hr_employee_data
    GROUP BY Overtime
)
SELECT 
    Overtime,
    Total_Staff,
    Exited_Staff,
    ROUND((Exited_Staff * 100.0) / Total_Staff, 2) AS Attrition_Rate_Pct
FROM OvertimeSummary;


-- --------------------------------------------------
-- QUERY 5: Job Satisfaction Correlation Analysis
-- Traces how employee happiness impacts turnover, average experience, and salary levels.
-- Demonstrates: CASE mapping, GROUP BY, and aggregations.
-- --------------------------------------------------
SELECT 
    CASE JobSatisfaction
        WHEN 1 THEN '1 - Very Dissatisfied'
        WHEN 2 THEN '2 - Dissatisfied'
        WHEN 3 THEN '3 - Satisfied'
        WHEN 4 THEN '4 - Very Satisfied'
        ELSE 'Unknown'
    END AS Satisfaction_Level,
    COUNT(EmployeeID) AS Employee_Count,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Attrition_Count,
    ROUND(
        (SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(EmployeeID)) * 100, 
        2
    ) AS Attrition_Rate_Pct,
    ROUND(AVG(Salary), 2) AS Average_Salary,
    ROUND(AVG(YearsAtCompany), 1) AS Average_Tenure
FROM hr_employee_data
GROUP BY JobSatisfaction
ORDER BY JobSatisfaction ASC;


-- --------------------------------------------------
-- QUERY 6: Top-Paying Roles per Department (Career Pathways)
-- Ranks job roles within each business unit based on average salary.
-- Demonstrates: Window Functions (DENSE_RANK() OVER PARTITION), CTEs.
-- --------------------------------------------------
WITH RankedRoles AS (
    SELECT 
        Department,
        JobRole,
        ROUND(AVG(Salary), 2) AS Avg_Role_Salary,
        DENSE_RANK() OVER(
            PARTITION BY Department 
            ORDER BY AVG(Salary) DESC
        ) AS Salary_Rank
    FROM hr_employee_data
    GROUP BY Department, JobRole
)
SELECT 
    Department,
    JobRole,
    Avg_Role_Salary,
    Salary_Rank
FROM RankedRoles
WHERE Salary_Rank <= 3; -- Show top 3 highest paying roles per department


-- --------------------------------------------------
-- QUERY 7: Salary Disparity Audit (Underpaid vs Overpaid)
-- Compares individual salaries with the average salary of their specific role.
-- Demonstrates: Window Function AVG() OVER (PARTITION BY).
-- --------------------------------------------------
WITH SalaryDelta AS (
    SELECT 
        EmployeeID,
        EmployeeName,
        Department,
        JobRole,
        Salary,
        ROUND(AVG(Salary) OVER(PARTITION BY JobRole), 2) AS Avg_Role_Salary,
        Salary - ROUND(AVG(Salary) OVER(PARTITION BY JobRole), 2) AS Sal_Diff_From_Avg
    FROM hr_employee_data
    WHERE Attrition = 'No' -- Focus on active employees for adjustments
)
SELECT 
    EmployeeID,
    EmployeeName,
    Department,
    JobRole,
    Salary,
    Avg_Role_Salary,
    Sal_Diff_From_Avg,
    CASE 
        WHEN Sal_Diff_From_Avg < -10000 THEN 'Severely Underpaid'
        WHEN Sal_Diff_From_Avg < -2000 THEN 'Below Average'
        WHEN Sal_Diff_From_Avg > 10000 THEN 'Highly Compensated'
        ELSE 'Market Average'
    END AS Compensation_Category
FROM SalaryDelta
ORDER BY Sal_Diff_From_Avg ASC;


-- --------------------------------------------------
-- QUERY 8: High-Risk Turnover Dashboard (Flight Risk List)
-- Identifies active employees with critical turnover indicators:
-- Working Overtime, Low Satisfaction, Low Salary relative to job average, and Low Tenure.
-- Demonstrates: Complex CTEs, Window average, and multiple filter parameters.
-- --------------------------------------------------
WITH ActiveStaffDetails AS (
    SELECT 
        EmployeeID,
        EmployeeName,
        Department,
        JobRole,
        Age,
        Overtime,
        JobSatisfaction,
        YearsAtCompany,
        Salary,
        AVG(Salary) OVER (PARTITION BY JobRole) AS Avg_Role_Salary
    FROM hr_employee_data
    WHERE Attrition = 'No' -- Only evaluate currently active employees
)
SELECT 
    EmployeeID,
    EmployeeName,
    Department,
    JobRole,
    Age,
    Overtime,
    JobSatisfaction,
    YearsAtCompany,
    Salary,
    ROUND(Avg_Role_Salary, 2) AS Avg_Role_Salary,
    -- Simple rule-based Risk Score: Overtime (+1), Low Satisfaction (+2), Underpaid (+1), Short Tenure (+1)
    (
        CASE WHEN Overtime = 'Yes' THEN 1 ELSE 0 END +
        CASE WHEN JobSatisfaction <= 2 THEN 2 ELSE 0 END +
        CASE WHEN Salary < Avg_Role_Salary THEN 1 ELSE 0 END +
        CASE WHEN YearsAtCompany <= 2 THEN 1 ELSE 0 END
    ) AS Risk_Score
FROM ActiveStaffDetails
WHERE 
    Overtime = 'Yes' 
    AND JobSatisfaction <= 2 
    AND Salary < Avg_Role_Salary
ORDER BY Risk_Score DESC, YearsAtCompany ASC
LIMIT 15;


-- --------------------------------------------------
-- QUERY 9: Performance Rating vs Salary Growth & Attrition
-- Summarizes HR metrics by Performance Rating.
-- Demonstrates: GROUP BY, HAVING, and round operations.
-- --------------------------------------------------
SELECT 
    PerformanceRating,
    COUNT(EmployeeID) AS Total_Employees,
    ROUND(AVG(Salary), 2) AS Avg_Salary,
    ROUND(AVG(YearsAtCompany), 1) AS Avg_Tenure_Years,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Exited_Employees,
    ROUND(
        (SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(EmployeeID)) * 100, 
        2
    ) AS Attrition_Rate_Pct
FROM hr_employee_data
GROUP BY PerformanceRating
HAVING COUNT(EmployeeID) > 5 -- Filters out sparsely populated categories if they exist
ORDER BY PerformanceRating DESC;


-- --------------------------------------------------
-- QUERY 10: Age Group and Marital Status Retention Audit
-- Dynamic segmentation of employees into age groups to audit retention.
-- Demonstrates: CASE groups, GROUP BY, and nested sorting.
-- --------------------------------------------------
WITH Demographics AS (
    SELECT 
        EmployeeID,
        Attrition,
        MaritalStatus,
        CASE 
            WHEN Age < 30 THEN 'Under 30'
            WHEN Age BETWEEN 30 AND 39 THEN '30-39'
            WHEN Age BETWEEN 40 AND 49 THEN '40-49'
            ELSE '50 and Over'
        END AS Age_Group
    FROM hr_employee_data
)
SELECT 
    Age_Group,
    MaritalStatus,
    COUNT(EmployeeID) AS Total_Employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS Exited_Employees,
    ROUND(
        (SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(EmployeeID)) * 100, 
        2
    ) AS Attrition_Rate_Pct
FROM Demographics
GROUP BY Age_Group, MaritalStatus
ORDER BY Age_Group, Attrition_Rate_Pct DESC;
