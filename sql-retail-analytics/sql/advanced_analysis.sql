-- ============================================================================
-- SQL RETAIL ANALYTICS - ADVANCED ANALYTICAL SUITE (WINDOW FUNCTIONS & COHORTS)
-- ============================================================================
-- Purpose: Window functions, running totals, MoM/YoY growth, cohort tracking.
-- Database: SQLite / ANSI SQL Compliant (MySQL & PostgreSQL compatible comments)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: PRODUCT VALUE RANKING WITHIN CATEGORIES (DENSE_RANK)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Rank products within their respective categories based on 
--                     accumulated sales to identify core revenue drivers.
-- EXPECTED INSIGHT: DENSE_RANK handles ties gracefully without skipping ranks. 
--                  Helps category managers locate top 3 SKUs per department.
-- ----------------------------------------------------------------------------
WITH PRODUCT_AGGREGATES AS (
    SELECT 
        product_category,
        product_name,
        ROUND(SUM(sales), 2) AS TOTAL_SALES,
        SUM(quantity) AS TOTAL_QUANTITY
    FROM 
        retail_sales
    GROUP BY 
        product_category, product_name
)
SELECT 
    product_category AS PRODUCT_CATEGORY,
    product_name AS PRODUCT_NAME,
    TOTAL_SALES,
    TOTAL_QUANTITY,
    DENSE_RANK() OVER(
        PARTITION BY product_category 
        ORDER BY TOTAL_SALES DESC
    ) AS PRODUCT_RANK
FROM 
    PRODUCT_AGGREGATES
ORDER BY 
    PRODUCT_CATEGORY ASC, PRODUCT_RANK ASC;


-- ----------------------------------------------------------------------------
-- QUERY 2: CUMULATIVE RUNNING TOTAL OF REVENUE (SUM OVER)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Track the progressive accumulation of sales revenue over 
--                     time to report growth curves to executive investors.
-- EXPECTED INSIGHT: Illustrates the upward inflection of business sales, 
--                  climbing from $0 to over $4.09M by the end of 2025.
-- ----------------------------------------------------------------------------
WITH MONTHLY_AGGREGATES AS (
    SELECT 
        strftime('%Y-%m', order_date) AS SALES_MONTH,
        ROUND(SUM(sales), 2) AS MONTHLY_SALES
    FROM 
        retail_sales
    GROUP BY 
        SALES_MONTH
)
SELECT 
    SALES_MONTH,
    MONTHLY_SALES,
    ROUND(SUM(MONTHLY_SALES) OVER(
        ORDER BY SALES_MONTH ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS RUNNING_TOTAL_REVENUE
FROM 
    MONTHLY_AGGREGATES
ORDER BY 
    SALES_MONTH ASC;


-- ----------------------------------------------------------------------------
-- QUERY 3: 30-DAY ROLLING MOVING AVERAGE OF REVENUE (AVG OVER)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Smooth out weekday/weekend volatility to identify 
--                     underlying business growth trajectories.
-- EXPECTED INSIGHT: Moving averages prevent overreactions to short-term sales 
--                  dips and showcase actual quarterly momentum.
-- ----------------------------------------------------------------------------
WITH DAILY_SALES AS (
    SELECT 
        order_date,
        SUM(sales) AS DAILY_REVENUE
    FROM 
        retail_sales
    GROUP BY 
        order_date
)
SELECT 
    order_date AS ORDER_DATE,
    ROUND(DAILY_REVENUE, 2) AS DAILY_REVENUE,
    ROUND(AVG(DAILY_REVENUE) OVER(
        ORDER BY order_date ASC
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ROLLING_30DAY_AVG_REVENUE
FROM 
    DAILY_SALES
ORDER BY 
    order_date ASC
LIMIT 120; -- Show a snippet of initial records for readability


-- ----------------------------------------------------------------------------
-- QUERY 4: MONTH-OVER-MONTH (MOM) REVENUE GROWTH ANALYSIS (LAG)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Measure month-over-month revenue expansions and contractions 
--                     to check the health of operational marketing cycles.
-- EXPECTED INSIGHT: Quantify immediate growth rate. Easily identifies the holiday 
--                  peak (e.g. +80% sales spike in Nov/Dec) followed by January drops.
-- ----------------------------------------------------------------------------
WITH MONTHLY_REVENUE AS (
    SELECT 
        strftime('%Y-%m', order_date) AS SALES_MONTH,
        ROUND(SUM(sales), 2) AS REVENUE
    FROM 
        retail_sales
    GROUP BY 
        SALES_MONTH
)
SELECT 
    SALES_MONTH,
    REVENUE AS CURRENT_MONTH_REVENUE,
    LAG(REVENUE, 1) OVER (ORDER BY SALES_MONTH ASC) AS PREVIOUS_MONTH_REVENUE,
    ROUND(REVENUE - LAG(REVENUE, 1) OVER (ORDER BY SALES_MONTH ASC), 2) AS NET_CHANGE,
    ROUND(
        ((REVENUE - LAG(REVENUE, 1) OVER (ORDER BY SALES_MONTH ASC)) / 
        LAG(REVENUE, 1) OVER (ORDER BY SALES_MONTH ASC)) * 100, 
        2
    ) AS MOM_GROWTH_PCT
FROM 
    MONTHLY_REVENUE
ORDER BY 
    SALES_MONTH ASC;


-- ----------------------------------------------------------------------------
-- QUERY 5: YEAR-OVER-YEAR (YOY) REVENUE GROWTH ANALYSIS (LAG OFFSET 12)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Compare seasonal sales directly with the corresponding 
--                     month in the prior fiscal year, eliminating seasonality factors.
-- EXPECTED INSIGHT: True brand velocity measurement. Shows steady YoY expansions 
--                  for 2024 and 2025 relative to 2023 baselines.
-- ----------------------------------------------------------------------------
WITH MONTHLY_REVENUE AS (
    SELECT 
        strftime('%Y-%m', order_date) AS SALES_MONTH,
        ROUND(SUM(sales), 2) AS REVENUE
    FROM 
        retail_sales
    GROUP BY 
        SALES_MONTH
)
SELECT 
    SALES_MONTH,
    REVENUE AS CURRENT_YEAR_REVENUE,
    LAG(REVENUE, 12) OVER (ORDER BY SALES_MONTH ASC) AS PRIOR_YEAR_REVENUE,
    ROUND(
        ((REVENUE - LAG(REVENUE, 12) OVER (ORDER BY SALES_MONTH ASC)) / 
        LAG(REVENUE, 12) OVER (ORDER BY SALES_MONTH ASC)) * 100, 
        2
    ) AS YOY_GROWTH_PCT
FROM 
    MONTHLY_REVENUE
ORDER BY 
    SALES_MONTH ASC;


-- ----------------------------------------------------------------------------
-- QUERY 6: SEQUENTIAL CUSTOMER TRANSACTION LOGGING (ROW_NUMBER)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Assign sequential indexes to each customer's order line items 
--                     by date to trace buying progression histories.
-- EXPECTED INSIGHT: Identifies first-time purchases vs. deep repeat interactions 
--                  at the customer level. Excellent for cohort initialization.
-- ----------------------------------------------------------------------------
SELECT 
    customer_id AS CUSTOMER_ID,
    customer_name AS CUSTOMER_NAME,
    order_date AS ORDER_DATE,
    order_id AS ORDER_ID,
    product_category AS PRODUCT_CATEGORY,
    sales AS TRANSACTION_SALES,
    ROW_NUMBER() OVER(
        PARTITION BY customer_id 
        ORDER BY order_date ASC, order_id ASC
    ) AS CUSTOMER_PURCHASE_SEQUENCE
FROM 
    retail_sales
ORDER BY 
    customer_id ASC, CUSTOMER_PURCHASE_SEQUENCE ASC
LIMIT 100; -- Limit preview length


-- ----------------------------------------------------------------------------
-- QUERY 7: FIRST-TO-SECOND TRANSACTION VELOCITY ANALYSIS (LEAD)
-- DIFFICULTY: Advanced (CTE + LEAD)
-- BUSINESS OBJECTIVE: Determine the average days it takes for a customer to return 
--                     and make their second purchase. Optimize repeat-sales targeting.
-- EXPECTED INSIGHT: Measures customer replenishment frequency. Shorter spacing 
--                  means high brand engagement, reducing retention overheads.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_ORDER_DATES AS (
    SELECT DISTINCT 
        customer_id,
        order_date,
        order_id
    FROM 
        retail_sales
),
ORDER_TIMELINES AS (
    SELECT 
        customer_id,
        order_date,
        LEAD(order_date, 1) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date ASC
        ) AS NEXT_ORDER_DATE,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id 
            ORDER BY order_date ASC
        ) AS ORDER_INDEX
    FROM 
        CUSTOMER_ORDER_DATES
)
SELECT 
    COUNT(customer_id) AS RETAINED_CUSTOMERS,
    ROUND(AVG(julianday(NEXT_ORDER_DATE) - julianday(order_date)), 1) AS AVG_DAYS_TO_SECOND_ORDER
FROM 
    ORDER_TIMELINES
WHERE 
    ORDER_INDEX = 1 
    AND NEXT_ORDER_DATE IS NOT NULL;


-- ----------------------------------------------------------------------------
-- QUERY 8: THE ELITE REGIONAL SPENDERS (RANK OVER PARTITION)
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Identify the top 3 highest-spending customers in each region 
--                     to establish high-touch executive relationship strategies.
-- EXPECTED INSIGHT: RANK handles partition ties. Pinpoints the key economic players 
--                  driving localized volume, useful for premium marketing initiatives.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_REGIONAL_SPEND AS (
    SELECT 
        region,
        customer_id,
        customer_name,
        ROUND(SUM(sales), 2) AS TOTAL_REGIONAL_SPEND
    FROM 
        retail_sales
    GROUP BY 
        region, customer_id, customer_name
),
REGIONAL_RANKS AS (
    SELECT 
        region,
        customer_id,
        customer_name,
        TOTAL_REGIONAL_SPEND,
        RANK() OVER (
            PARTITION BY region 
            ORDER BY TOTAL_REGIONAL_SPEND DESC
        ) AS SPENDING_RANK
    FROM 
        CUSTOMER_REGIONAL_SPEND
)
SELECT 
    region AS REGION,
    customer_id AS CUSTOMER_ID,
    customer_name AS CUSTOMER_NAME,
    TOTAL_REGIONAL_SPEND,
    SPENDING_RANK
FROM 
    REGIONAL_RANKS
WHERE 
    SPENDING_RANK <= 3
ORDER BY 
    region ASC, SPENDING_RANK ASC;


-- ----------------------------------------------------------------------------
-- QUERY 9: CUSTOMER CHURN RISK DIAGNOSIS
-- DIFFICULTY: Advanced
-- BUSINESS OBJECTIVE: Flags customers whose last order occurred over 180 days 
--                     before the final date in the dataset (2025-12-31).
-- EXPECTED INSIGHT: Proactive win-back strategies. Helps CRM teams export list 
--                  of dormant customers for re-activation discount campaigns.
-- ----------------------------------------------------------------------------
WITH LAST_PURCHASE_DATA AS (
    SELECT 
        customer_id,
        customer_name,
        MAX(order_date) AS LAST_ORDER_DATE,
        ROUND(SUM(sales), 2) AS LIFETIME_SALES
    FROM 
        retail_sales
    GROUP BY 
        customer_id, customer_name
)
SELECT 
    customer_id AS CUSTOMER_ID,
    customer_name AS CUSTOMER_NAME,
    LAST_ORDER_DATE,
    LIFETIME_SALES,
    CAST(julianday('2025-12-31') - julianday(LAST_ORDER_DATE) AS INTEGER) AS DAYS_SINCE_LAST_ORDER,
    CASE 
        WHEN julianday('2025-12-31') - julianday(LAST_ORDER_DATE) > 270 THEN 'High Churn Risk (Dormant > 9 months)'
        WHEN julianday('2025-12-31') - julianday(LAST_ORDER_DATE) BETWEEN 180 AND 270 THEN 'Medium Churn Risk (Inactive 6-9 months)'
        ELSE 'Active (Purchased within 6 months)'
    END AS CHURN_RISK_STATUS
FROM 
    LAST_PURCHASE_DATA
ORDER BY 
    DAYS_SINCE_LAST_ORDER DESC
LIMIT 50; -- Show top risk listings


-- ----------------------------------------------------------------------------
-- QUERY 10: CUSTOMER COHORT RETENTION TRACKING
-- DIFFICULTY: Advanced (Complex CTE Cohort Grid)
-- BUSINESS OBJECTIVE: Group customers into cohorts based on the quarter of their 
--                     first purchase, and track transaction rates in subsequent quarters.
-- EXPECTED INSIGHT: Measure lifetime customer stickiness. Proves that repeat 
--                  buyers consistently return, validating business model durability.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_INCEPTION AS (
    -- Identify the first purchase quarter for each customer
    SELECT 
        customer_id,
        MIN(strftime('%Y-Q', order_date) || 
            CASE 
                WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1 AND 3 THEN '1'
                WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4 AND 6 THEN '2'
                WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7 AND 9 THEN '3'
                ELSE '4'
            END
        ) AS COHORT_QUARTER
    FROM 
        retail_sales
    GROUP BY 
        customer_id
),
TRANSACTION_QUARTERS AS (
    -- Fetch unique quarters where each customer transacted
    SELECT DISTINCT
        customer_id,
        strftime('%Y-Q', order_date) || 
        CASE 
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1 AND 3 THEN '1'
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4 AND 6 THEN '2'
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7 AND 9 THEN '3'
            ELSE '4'
        END AS ACTIVE_QUARTER
    FROM 
        retail_sales
),
COHORT_SIZES AS (
    -- Calculate how many customers started in each cohort quarter
    SELECT 
        COHORT_QUARTER,
        COUNT(customer_id) AS COHORT_SIZE
    FROM 
        CUSTOMER_INCEPTION
    GROUP BY 
        COHORT_QUARTER
),
COHORT_RETENTION AS (
    -- Join inception quarter to transaction quarter to track repeat buying
    SELECT 
        CI.COHORT_QUARTER,
        TQ.ACTIVE_QUARTER,
        COUNT(DISTINCT TQ.customer_id) AS ACTIVE_CUSTOMERS
    FROM 
        CUSTOMER_INCEPTION CI
    JOIN 
        TRANSACTION_QUARTERS TQ ON CI.customer_id = TQ.customer_id
    GROUP BY 
        CI.COHORT_QUARTER, TQ.ACTIVE_QUARTER
)
SELECT 
    CR.COHORT_QUARTER,
    CS.COHORT_SIZE,
    CR.ACTIVE_QUARTER,
    CR.ACTIVE_CUSTOMERS,
    ROUND((CR.ACTIVE_CUSTOMERS * 100.0 / CS.COHORT_SIZE), 2) AS RETENTION_PCT
FROM 
    COHORT_RETENTION CR
JOIN 
    COHORT_SIZES CS ON CR.COHORT_QUARTER = CS.COHORT_QUARTER
ORDER BY 
    CR.COHORT_QUARTER ASC, CR.ACTIVE_QUARTER ASC
LIMIT 100;
