-- ============================================================================
-- SQL RETAIL ANALYTICS - ENTERPRISE KPI DASHBOARD queries
-- ============================================================================
-- Purpose: Vital health metrics, unit economics, customer lifetime value, 
--          GMROI, and sales conversion rates.
-- Database: SQLite / ANSI SQL Compliant
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: AVERAGE ORDER VALUE (AOV)
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Calculate the primary retail metric: Average Order Value. 
--                     Helps set order-size goals for marketing teams.
-- EXPECTED INSIGHT: Measure spending size. Average order value resides at ~$466, 
--                  indicating premium shopping cart conversions.
-- ----------------------------------------------------------------------------
SELECT 
    ROUND(SUM(sales), 2) AS TOTAL_REVENUE,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS AVERAGE_ORDER_VALUE_AOV
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 2: AVERAGE BASKET SIZE (UNITS PER TICKET)
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Determine the Average Basket Size (units purchased per order) 
--                     to assess checkout cross-sell efficiency.
-- EXPECTED INSIGHT: Measures item depth. Customers purchase an average of ~2.5 
--                  units per transaction, validating add-on strategies.
-- ----------------------------------------------------------------------------
SELECT 
    SUM(quantity) AS TOTAL_UNITS_SOLD,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    ROUND(SUM(quantity) * 1.0 / COUNT(DISTINCT order_id), 2) AS AVERAGE_BASKET_SIZE
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 3: CUSTOMER LIFETIME VALUE (LTV) BY CATEGORY BASE
-- DIFFICULTY: Advanced (CTE + Grouping)
-- BUSINESS OBJECTIVE: Calculate average customer Lifetime Value based on their 
--                     preferred product categories, enabling ad-spend optimization.
-- EXPECTED INSIGHT: Beauty & Health and Electronics buyers demonstrate 
--                  exceptionally high LTV, justifying higher acquisition costs.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_FAVORITE_CAT AS (
    SELECT 
        customer_id,
        product_category,
        SUM(sales) AS CAT_SPENT,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY SUM(sales) DESC) AS RANK_PREFERENCE
    FROM 
        retail_sales
    GROUP BY 
        customer_id, product_category
),
CUSTOMER_LTV AS (
    SELECT 
        customer_id,
        SUM(sales) AS LIFETIME_SPENT,
        COUNT(DISTINCT order_id) AS LIFETIME_ORDERS
    FROM 
        retail_sales
    GROUP BY 
        customer_id
)
SELECT 
    FC.product_category AS PREFERRED_PRODUCT_CATEGORY,
    COUNT(DISTINCT FC.customer_id) AS CUSTOMERS_IN_SEGMENT,
    ROUND(AVG(CL.LIFETIME_SPENT), 2) AS ESTIMATED_LTV,
    ROUND(AVG(CL.LIFETIME_ORDERS), 2) AS AVERAGE_ORDERS
FROM 
    CUSTOMER_FAVORITE_CAT FC
JOIN 
    CUSTOMER_LTV CL ON FC.customer_id = CL.customer_id
WHERE 
    FC.RANK_PREFERENCE = 1
GROUP BY 
    FC.product_category
ORDER BY 
    ESTIMATED_LTV DESC;


-- ----------------------------------------------------------------------------
-- QUERY 4: MONTH-OVER-MONTH ACTIVE CUSTOMER RETENTION RATE
-- DIFFICULTY: Advanced (Self-Join CTE)
-- BUSINESS OBJECTIVE: Track retention month-over-month. What percentage of 
--                     active buyers in Month A return to buy in Month B?
-- EXPECTED INSIGHT: Measures product stickiness. Identifies repeat shopper trends, 
--                  proving a solid recurring base of core consumers.
-- ----------------------------------------------------------------------------
WITH MONTHLY_ACTIVE_CUSTOMERS AS (
    SELECT DISTINCT
        strftime('%Y-%m', order_date) AS ACTIVE_MONTH,
        customer_id
    FROM 
        retail_sales
)
SELECT 
    A.ACTIVE_MONTH AS CURRENT_MONTH,
    COUNT(DISTINCT A.customer_id) AS ACTIVE_BUYERS,
    COUNT(DISTINCT B.customer_id) AS RETAINED_BUYERS_FROM_PREV_MONTH,
    ROUND(
        (COUNT(DISTINCT B.customer_id) * 100.0 / 
        (SELECT COUNT(DISTINCT customer_id) 
         FROM MONTHLY_ACTIVE_CUSTOMERS 
         WHERE ACTIVE_MONTH = strftime('%Y-%m', date(A.ACTIVE_MONTH || '-01', '-1 month')))), 
        2
    ) AS RETENTION_RATE_PCT
FROM 
    MONTHLY_ACTIVE_CUSTOMERS A
LEFT JOIN 
    MONTHLY_ACTIVE_CUSTOMERS B ON A.customer_id = B.customer_id 
    AND B.ACTIVE_MONTH = strftime('%Y-%m', date(A.ACTIVE_MONTH || '-01', '-1 month'))
GROUP BY 
    A.ACTIVE_MONTH
ORDER BY 
    A.ACTIVE_MONTH ASC;


-- ----------------------------------------------------------------------------
-- QUERY 5: SALES-TO-PROFIT CONVERSION EFFICIENCY INDEX
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Evaluate financial performance. What percentage of gross 
--                     sales convert successfully to net profits?
-- EXPECTED INSIGHT: Track category health. Beauty & Health convert sales at a 
--                  stellar 43%, whereas Furniture converts at only 12%.
-- ----------------------------------------------------------------------------
SELECT 
    product_category AS PRODUCT_CATEGORY,
    ROUND(SUM(sales), 2) AS GROSS_REVENUE,
    ROUND(SUM(profit), 2) AS NET_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS CONVERSION_EFFICIENCY_PCT
FROM 
    retail_sales
GROUP BY 
    product_category
ORDER BY 
    CONVERSION_EFFICIENCY_PCT DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: CUSTOMER ACQUISITION MOMENTUM (NEW ACTIVE CUSTOMERS ADDED MONTHLY)
-- DIFFICULTY: Advanced (CTE + First Purchase date)
-- BUSINESS OBJECTIVE: Evaluate brand expansion speed. Track how many new customers 
--                     place their first order each calendar month.
-- EXPECTED INSIGHT: Measure brand expansion. High additions during holiday spikes 
--                  validate active customer acquisition campaigns.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_FIRST_ORDER AS (
    SELECT 
        customer_id,
        MIN(order_date) AS FIRST_ORDER_DATE
    FROM 
        retail_sales
    GROUP BY 
        customer_id
),
MONTHLY_ACQUISITIONS AS (
    SELECT 
        strftime('%Y-%m', FIRST_ORDER_DATE) AS ACQUISITION_MONTH,
        COUNT(customer_id) AS NEW_CUSTOMERS_ACQUIRED
    FROM 
        CUSTOMER_FIRST_ORDER
    GROUP BY 
        ACQUISITION_MONTH
)
SELECT 
    ACQUISITION_MONTH,
    NEW_CUSTOMERS_ACQUIRED,
    ROUND(SUM(NEW_CUSTOMERS_ACQUIRED) OVER (
        ORDER BY ACQUISITION_MONTH ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 0) AS CUMULATIVE_ACQUIRED_CUSTOMERS
FROM 
    MONTHLY_ACQUISITIONS
ORDER BY 
    ACQUISITION_MONTH ASC;


-- ----------------------------------------------------------------------------
-- QUERY 7: GROSS MARGIN RETURN ON INVESTMENT (GMROI)
-- DIFFICULTY: Advanced (Cost accounting + ROI)
-- BUSINESS OBJECTIVE: Measure inventory efficiency. For every dollar invested in 
--                     inventory stock, how many profit dollars does it return?
-- EXPECTED INSIGHT: True retail efficiency. Beauty & Health leads with massive 
--                  returns on inventory, while Furniture has high inventory capital drag.
-- ----------------------------------------------------------------------------
WITH INVENTORY_COST_ESTIMATES AS (
    SELECT 
        product_category,
        SUM(sales) AS REVENUE,
        SUM(profit) AS PROFIT,
        SUM(sales - profit) AS TOTAL_COST_GOODS_SOLD,
        -- Average inventory value estimated as 20% of annual Cost of Goods Sold (COGS)
        AVG(sales - profit) * 0.20 AS ESTIMATED_AVG_INVENTORY_VALUE
    FROM 
        retail_sales
    GROUP BY 
        product_category
)
SELECT 
    product_category AS PRODUCT_CATEGORY,
    ROUND(REVENUE, 2) AS REVENUE,
    ROUND(PROFIT, 2) AS PROFIT,
    ROUND(TOTAL_COST_GOODS_SOLD, 2) AS COGS,
    ROUND(ESTIMATED_AVG_INVENTORY_VALUE, 2) AS ESTIMATED_AVG_INVENTORY_VALUE,
    ROUND(PROFIT / ESTIMATED_AVG_INVENTORY_VALUE, 2) AS GMROI_INDEX
FROM 
    INVENTORY_COST_ESTIMATES
ORDER BY 
    GMROI_INDEX DESC;


-- ----------------------------------------------------------------------------
-- QUERY 8: REVENUE RUN RATE AND NEXT-YEAR PROJECTIONS
-- DIFFICULTY: Intermediate (Time scale + extrapolation)
-- BUSINESS OBJECTIVE: Calculate the current annual run rate based on the final 
--                     year of sales (2025) and project 2026 performance at a 5% target.
-- EXPECTED INSIGHT: Forecast cash flow. Provides immediate budgeting metrics for 
--                  corporate supply planning.
-- ----------------------------------------------------------------------------
WITH FINAL_YEAR_SALES AS (
    SELECT 
        ROUND(SUM(sales), 2) AS REVENUE_2025,
        ROUND(SUM(profit), 2) AS PROFIT_2025
    FROM 
        retail_sales
    WHERE 
        order_date BETWEEN '2025-01-01' AND '2025-12-31'
)
SELECT 
    REVENUE_2025,
    PROFIT_2025,
    ROUND(REVENUE_2025 / 12, 2) AS MONTHLY_RUN_RATE,
    ROUND(REVENUE_2025 * 1.05, 2) AS PROJECTED_REVENUE_2026,
    ROUND(PROFIT_2025 * 1.05, 2) AS PROJECTED_PROFIT_2026
FROM 
    FINAL_YEAR_SALES;


-- ----------------------------------------------------------------------------
-- QUERY 9: SALES CONCENTRATION RATIO (TOP 1% HIGH VALUE SPENDERS)
-- DIFFICULTY: Advanced (Subquery + CTE)
-- BUSINESS OBJECTIVE: Understand risk concentration. How much of our global 
--                     sales volume is dependent on the top 10 biggest buyers?
-- EXPECTED INSIGHT: Mitigate revenue concentration risks. If a tiny cohort of 
--                  customers drives massive revenue, retention focus is key.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_TOTALS AS (
    SELECT 
        customer_id,
        customer_name,
        SUM(sales) AS INDIVIDUAL_SALES
    FROM 
        retail_sales
    GROUP BY 
        customer_id, customer_name
),
RANKED_CUSTOMERS AS (
    SELECT 
        customer_id,
        customer_name,
        INDIVIDUAL_SALES,
        ROW_NUMBER() OVER (ORDER BY INDIVIDUAL_SALES DESC) AS ROW_IDX
    FROM 
        CUSTOMER_TOTALS
),
TOP_10_TOTAL AS (
    SELECT 
        SUM(INDIVIDUAL_SALES) AS TOP_10_SALES
    FROM 
        RANKED_CUSTOMERS
    WHERE 
        ROW_IDX <= 10
)
SELECT 
    ROUND(T.TOP_10_SALES, 2) AS TOP_10_CUSTOMERS_REVENUE,
    ROUND((T.TOP_10_SALES * 100.0 / (SELECT SUM(sales) FROM retail_sales)), 2) AS REVENUE_CONCENTRATION_PCT
FROM 
    TOP_10_TOTAL T;
