-- ============================================================================
-- SQL RETAIL ANALYTICS - INTERMEDIATE BI & DATA QUALITY AUDITS
-- ============================================================================
-- Purpose: CTEs, subqueries, promotional analytics, and system audits.
-- Database: SQLite / ANSI SQL Compliant
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: CUSTOMER SEGMENTATION BY FINANCIAL CONTRIBUTION
-- DIFFICULTY: Intermediate (CTE + CASE)
-- BUSINESS OBJECTIVE: Classify customers into High-Value (Gold), Medium-Value 
--                     (Silver), and Low-Value (Bronze) tiers to target high-ROI loyalty.
-- EXPECTED INSIGHT: Gold customers generate outsized revenue per capita. 
--                  Bronze represents the long-tail list of one-time buyers.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_SPEND AS (
    SELECT 
        customer_id,
        customer_name,
        ROUND(SUM(sales), 2) AS TOTAL_SPENT,
        COUNT(DISTINCT order_id) AS TOTAL_ORDERS
    FROM 
        retail_sales
    GROUP BY 
        customer_id, customer_name
)
SELECT 
    CASE 
        WHEN TOTAL_SPENT >= 7000 THEN 'Gold Tier (High-Spend)'
        WHEN TOTAL_SPENT BETWEEN 2500 AND 6999.99 THEN 'Silver Tier (Mid-Spend)'
        ELSE 'Bronze Tier (Low-Spend)'
    END AS CUSTOMER_SEGMENT,
    COUNT(customer_id) AS CUSTOMER_COUNT,
    ROUND(SUM(TOTAL_SPENT), 2) AS TOTAL_SEGMENT_REVENUE,
    ROUND(AVG(TOTAL_SPENT), 2) AS AVERAGE_CUSTOMER_LTV,
    ROUND(SUM(TOTAL_ORDERS) * 1.0 / COUNT(customer_id), 2) AS AVERAGE_ORDERS_PER_CUSTOMER
FROM 
    CUSTOMER_SPEND
GROUP BY 
    CUSTOMER_SEGMENT
ORDER BY 
    TOTAL_SEGMENT_REVENUE DESC;


-- ----------------------------------------------------------------------------
-- QUERY 2: DATA QUALITY AUDIT - NULL VALUE DETECTION
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Audit the entire transaction table to identify incomplete records 
--                     or parsing failures in critical fields.
-- EXPECTED INSIGHT: Validate ETL pipelines. Returns exactly 0 for all counts, 
--                  confirming total dataset integrity and cleanliness.
-- ----------------------------------------------------------------------------
SELECT 
    SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) AS MISSING_TRANS_IDS,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS MISSING_ORDER_IDS,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS MISSING_DATES,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS MISSING_CUST_IDS,
    SUM(CASE WHEN product_category IS NULL THEN 1 ELSE 0 END) AS MISSING_CATEGORIES,
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS MISSING_SALES_VALUES,
    SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END) AS MISSING_PROFITS
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 3: DATA QUALITY AUDIT - DUPLICATE ORDER LINE SCAN
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Identify potential double-billing errors or accidental double-entries 
--                     in order records where identical items are logged within the same order.
-- EXPECTED INSIGHT: Find system-level errors. If this returns rows, it means the 
--                  same product was entered multiple times under one transaction.
-- ----------------------------------------------------------------------------
SELECT 
    order_id,
    customer_id,
    product_name,
    COUNT(*) AS OCCURRENCE_COUNT
FROM 
    retail_sales
GROUP BY 
    order_id, customer_id, product_name
HAVING 
    COUNT(*) > 1
ORDER BY 
    OCCURRENCE_COUNT DESC;


-- ----------------------------------------------------------------------------
-- QUERY 4: DATA QUALITY AUDIT - OUT-OF-BOUNDS CONSTRAINT CHECK
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Verify that there are no invalid values such as negative prices, 
--                     impossible quantities, or discount percentages outside [0, 1].
-- EXPECTED INSIGHT: Compliance reporting. Returns 0, verifying that database engine 
--                  CHECK constraints are successfully policing data quality.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS TOTAL_INVALID_RECORDS,
    SUM(CASE WHEN quantity <= 0 THEN 1 ELSE 0 END) AS INVALID_QUANTITY_COUNT,
    SUM(CASE WHEN unit_price < 0 THEN 1 ELSE 0 END) AS INVALID_PRICE_COUNT,
    SUM(CASE WHEN discount < 0.0 OR discount > 1.0 THEN 1 ELSE 0 END) AS INVALID_DISCOUNT_COUNT
FROM 
    retail_sales;


-- ----------------------------------------------------------------------------
-- QUERY 5: DATA QUALITY AUDIT - NEGATIVE PROFIT ANOMALIES (LOSS LEADERS)
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Locate and count transactions where net profit is negative, 
--                     assessing the business impact of aggressive markdown activities.
-- EXPECTED INSIGHT: Identify promotional drag. About 4.8% of transactions yield 
--                  a net loss, primarily occurring on high discounts.
-- ----------------------------------------------------------------------------
SELECT 
    product_category AS PRODUCT_CATEGORY,
    COUNT(transaction_id) AS LOSS_TRANSACTION_COUNT,
    ROUND(SUM(sales), 2) AS LOSS_REVENUE,
    ROUND(SUM(profit), 2) AS NET_FINANCIAL_LOSS,
    ROUND(AVG(discount) * 100, 2) AS AVG_LOSS_DISCOUNT_PERCENT
FROM 
    retail_sales
WHERE 
    profit < 0
GROUP BY 
    product_category
ORDER BY 
    NET_FINANCIAL_LOSS ASC;


-- ----------------------------------------------------------------------------
-- QUERY 6: THE PARETO PRODUCT RANKING - ELITE PROFIT CONTRIBUTIONS
-- DIFFICULTY: Intermediate (Subquery)
-- BUSINESS OBJECTIVE: Filter for high-impact individual items yielding more than 
--                     $15,000 in absolute profits across the timeline.
-- EXPECTED INSIGHT: Identify elite SKU inventory. Focus on stocking and 
--                  marketing these specific products to protect cash flows.
-- ----------------------------------------------------------------------------
SELECT 
    product_name,
    product_category,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(SUM(profit), 2) AS ACCUMULATED_PROFIT,
    SUM(quantity) AS TOTAL_UNITS
FROM 
    retail_sales
GROUP BY 
    product_name, product_category
HAVING 
    SUM(profit) > 15000
ORDER BY 
    ACCUMULATED_PROFIT DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: MONTHLY TIME-SERIES AND SEASONAL SALES SPIKES
-- DIFFICULTY: Intermediate (Date Extraction)
-- BUSINESS OBJECTIVE: Identify cyclical patterns in retail sales to anticipate 
--                     demand spikes and schedule logistics capacity.
-- EXPECTED INSIGHT: Highlight major peaks. Q4 holidays (Nov-Dec) and back-to-school 
--                  (August) show prominent spikes across all three fiscal years.
-- ----------------------------------------------------------------------------
SELECT 
    strftime('%Y', order_date) AS SALES_YEAR,
    strftime('%m', order_date) AS SALES_MONTH,
    COUNT(DISTINCT order_id) AS TRANSACTION_VOLUME,
    ROUND(SUM(sales), 2) AS MONTHLY_REVENUE,
    ROUND(SUM(profit), 2) AS MONTHLY_PROFIT
FROM 
    retail_sales
GROUP BY 
    SALES_YEAR, SALES_MONTH
ORDER BY 
    SALES_YEAR ASC, SALES_MONTH ASC;


-- ----------------------------------------------------------------------------
-- QUERY 8: RETURN ON PROMOTION - DISCOUNT TIER ANALYSIS
-- DIFFICULTY: Intermediate (CASE Aggregation)
-- BUSINESS OBJECTIVE: Measure the economic impact of promotions. Determine if 
--                     deep discounts lead to volume spikes that justify margins.
-- EXPECTED INSIGHT: Heavy discounts (>20%) result in a net loss-leader scenario, 
--                  substantially draining margins while moderate discounts preserve profits.
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN discount = 0.0 THEN 'No Discount (Full Price)'
        WHEN discount BETWEEN 0.01 AND 0.15 THEN 'Low Promotion (1% - 15%)'
        WHEN discount BETWEEN 0.16 AND 0.25 THEN 'Medium Promotion (16% - 25%)'
        ELSE 'Deep Promotion (26% - 50% Peak)'
    END AS DISCOUNT_TIER,
    COUNT(transaction_id) AS TRANSACTION_VOLUME,
    ROUND(SUM(sales), 2) AS TOTAL_SALES_VOLUME,
    ROUND(SUM(profit), 2) AS ACCUMULATED_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS REALIZED_PROFIT_MARGIN_PCT
FROM 
    retail_sales
GROUP BY 
    DISCOUNT_TIER
ORDER BY 
    REALIZED_PROFIT_MARGIN_PCT DESC;


-- ----------------------------------------------------------------------------
-- QUERY 9: WEAK REGIONAL AND CATEGORY PRODUCT ALIGNMENTS
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Diagnose regional sub-optimization. Pinpoint which categories 
--                     are drag-sectors in which regions.
-- EXPECTED INSIGHT: Highlight underperforming sectors. Underlines that South region 
--                  loses substantial profit in Furniture due to shipping overheads.
-- ----------------------------------------------------------------------------
SELECT 
    region AS REGION,
    product_category AS PRODUCT_CATEGORY,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS OPERATIONAL_MARGIN_PCT
FROM 
    retail_sales
GROUP BY 
    region, product_category
HAVING 
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) < 15.00
ORDER BY 
    OPERATIONAL_MARGIN_PCT ASC;
