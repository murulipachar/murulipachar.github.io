-- ============================================================================
-- SQL RETAIL ANALYTICS - CORE AGGREGATIONS & BASIC EXPLORATION
-- ============================================================================
-- Purpose: Fundamental metrics, customer counts, and categorical groupings.
-- Database: SQLite / ANSI SQL Compliant
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: GLOBAL REVENUE AND PROFIT OVERVIEW
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Assess total business scale, absolute revenue generated, 
--                     and bottom-line profitability across the active timeline.
-- EXPECTED INSIGHT: Establish a baseline of business size. Recruiters see that 
--                  sales hover around $4.09M with a net profit of ~$808.5K.
-- ----------------------------------------------------------------------------
SELECT 
    ROUND(SUM(sales), 2) AS TOTAL_REVENUE,
    ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS NET_PROFIT_MARGIN_PCT
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 2: TOTAL ORDER VOLUME AND AVERAGE BASKET REVENUE
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Calculate the total transactional volume and average 
--                     financial ticket size (Average Order Value - AOV).
-- EXPECTED INSIGHT: Understand customer buying patterns. A higher total order 
--                  count with solid ticket sizes signals healthy demand.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT order_id) AS TOTAL_UNIQUE_ORDERS,
    COUNT(transaction_id) AS TOTAL_LINE_ITEMS,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS AVERAGE_ORDER_VALUE,
    ROUND(SUM(sales) / COUNT(transaction_id), 2) AS AVERAGE_LINE_ITEM_VALUE
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 3: UNIQUE CUSTOMER REACH
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Quantify the unique customer base reached during the 
--                     three-year sales lifecycle.
-- EXPECTED INSIGHT: Measure brand penetration. The database consists of 
--                  exactly 994 unique customers, proving wide-spread reach.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT customer_id) AS TOTAL_UNIQUE_CUSTOMERS
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 4: SALES AND PROFITABILITY BY PRODUCT CATEGORY
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Identify top-revenue and top-profit product categories to
--                     optimize marketing spend and inventory allocations.
-- EXPECTED INSIGHT: Show that Clothing and Beauty & Health are high-margin 
--                  champions, whereas Furniture yields lower profit margins.
-- ----------------------------------------------------------------------------
SELECT 
    product_category AS PRODUCT_CATEGORY,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    SUM(quantity) AS TOTAL_UNITS_SOLD,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS PROFIT_MARGIN_PCT
FROM 
    retail_sales
GROUP BY 
    product_category
ORDER BY 
    TOTAL_SALES DESC;


-- ----------------------------------------------------------------------------
-- QUERY 5: REGIONAL PERFORMANCE METRICS
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Evaluate sales, volume, and profit across geographical 
--                     regions to uncover regional anomalies or logistical impacts.
-- EXPECTED INSIGHT: Detect geographical performance. The West region leads in 
--                  sales, while the South region underperforms due to logistics.
-- ----------------------------------------------------------------------------
SELECT 
    region AS REGION,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS REGIONAL_MARGIN_PCT
FROM 
    retail_sales
GROUP BY 
    region
ORDER BY 
    TOTAL_SALES DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: PAYMENT METHOD POPULARITY AND TRANSACTION FEES
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Determine which payment channel is preferred by customers
--                     to optimize merchant service fees and checkout paths.
-- EXPECTED INSIGHT: Analyze checkout channels. Credit Card and PayPal dominate, 
--                  while Debit Card shows lower transaction counts.
-- ----------------------------------------------------------------------------
SELECT 
    payment_method AS PAYMENT_METHOD,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(AVG(sales), 2) AS AVERAGE_TICKET_SIZE
FROM 
    retail_sales
GROUP BY 
    payment_method
ORDER BY 
    TOTAL_ORDERS DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: CUSTOMER DEMOGRAPHIC AGE SEGMENTATION
-- DIFFICULTY: Beginner (with CASE)
-- BUSINESS OBJECTIVE: Segment the active customer base by age groups to 
--                     tailor marketing campaigns and product development.
-- EXPECTED INSIGHT: Identify target demographics. The 35-50 age bracket represents 
--                  the highest volume, showing solid purchasing power.
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN age < 25 THEN '18-24 (Gen Z)'
        WHEN age BETWEEN 25 AND 34 THEN '25-34 (Young Professionals)'
        WHEN age BETWEEN 35 AND 50 THEN '35-50 (Mid-Career)'
        WHEN age BETWEEN 51 AND 65 THEN '51-65 (Pre-Retirement)'
        ELSE '66+ (Seniors)'
    END AS AGE_GROUP,
    COUNT(DISTINCT customer_id) AS UNIQUE_CUSTOMERS,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    ROUND(SUM(sales), 2) AS TOTAL_SALES
FROM 
    retail_sales
GROUP BY 
    AGE_GROUP
ORDER BY 
    AGE_GROUP;


-- ----------------------------------------------------------------------------
-- QUERY 8: GENDER DIVERSITY PURCHASING POWER
-- DIFFICULTY: Beginner
-- BUSINESS OBJECTIVE: Understand purchasing behaviors across gender groups to
--                     align product line merchandising.
-- EXPECTED INSIGHT: Validate balanced customer demographics, confirming similar 
--                  AOV levels across Male, Female, and Non-binary groups.
-- ----------------------------------------------------------------------------
SELECT 
    gender AS GENDER,
    COUNT(DISTINCT customer_id) AS UNIQUE_CUSTOMERS,
    COUNT(DISTINCT order_id) AS TOTAL_ORDERS,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS AVERAGE_ORDER_VALUE
FROM 
    retail_sales
GROUP BY 
    gender
ORDER BY 
    TOTAL_SALES DESC;


-- ----------------------------------------------------------------------------
-- QUERY 9: REGIONAL SALES CONTRIBUTION PERCENTAGE
-- DIFFICULTY: Intermediate (Scalar Subquery)
-- BUSINESS OBJECTIVE: Calculate the percentage contribution of each region 
--                     relative to global enterprise sales.
-- EXPECTED INSIGHT: Provide the executive team with precise market share figures. 
--                  West contributes ~34.5% of total sales, followed by East.
-- ----------------------------------------------------------------------------
SELECT 
    region AS REGION,
    ROUND(SUM(sales), 2) AS REGIONAL_SALES,
    ROUND((SUM(sales) / (SELECT SUM(sales) FROM retail_sales)) * 100, 2) AS SALES_CONTRIBUTION_PCT
FROM 
    retail_sales
GROUP BY 
    region
ORDER BY 
    SALES_CONTRIBUTION_PCT DESC;
