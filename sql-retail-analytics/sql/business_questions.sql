-- ============================================================================
-- SQL RETAIL ANALYTICS - BUSINESS INTEL & DECISION-SUPPORT SUITE
-- ============================================================================
-- Purpose: Answering strategic retail questions, discount leak diagnostics, 
--          logistics costs, and growth expansion metrics.
-- Database: SQLite / ANSI SQL Compliant
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: THE DISCOUNT BLEED - IDENTIFYING REVENUE DRAINS
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Diagnose promotional leakage. Find transactions with high 
--                     discounts (>=20%) that resulted in negative net profits.
-- EXPECTED INSIGHT: Highlights deep markdowns on high-cost categories (e.g. 
--                  Furniture and Electronics) that destroy bottom-line profit.
-- ----------------------------------------------------------------------------
SELECT 
    order_id AS ORDER_ID,
    product_category AS CATEGORY,
    product_name AS SKU,
    quantity AS QTY,
    sales AS REVENUE,
    discount * 100 AS DISCOUNT_PERCENT,
    profit AS NET_LOSS
FROM 
    retail_sales
WHERE 
    discount >= 0.20
    AND profit < 0
ORDER BY 
    profit ASC
LIMIT 50;


-- ----------------------------------------------------------------------------
-- QUERY 2: WEAKEST CATEGORIES IN UNDERPERFORMING REGIONS (THE SHIPPING DRAG)
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Identify underperforming regional segments. Why does 
--                     Furniture have poor profit margins in the South region?
-- EXPECTED INSIGHT: Uncover logistics issues. High shipping and fulfillment 
--                  costs on bulky Furniture items in the South region drain profits.
-- ----------------------------------------------------------------------------
SELECT 
    region AS REGION,
    product_category AS CATEGORY,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS REALIZED_MARGIN_PCT,
    SUM(quantity) AS TOTAL_UNITS
FROM 
    retail_sales
WHERE 
    region = 'South'
    AND product_category = 'Furniture'
GROUP BY 
    region, product_category;


-- ----------------------------------------------------------------------------
-- QUERY 3: TARGET AUDIENCES - PAYMENT PREFERENCES BY AGE GROUP
-- DIFFICULTY: Intermediate (CASE + COUNT)
-- BUSINESS OBJECTIVE: Investigate payment selections across customer generations.
-- EXPECTED INSIGHT: Apple Pay and PayPal are highly favored by Gen Z and Young 
--                  Professionals, while Credit Cards remain popular with Seniors.
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN age < 25 THEN 'Gen Z (18-24)'
        WHEN age BETWEEN 25 AND 40 THEN 'Millennials (25-40)'
        WHEN age BETWEEN 41 AND 60 THEN 'Gen X (41-60)'
        ELSE 'Boomers/Seniors (61+)'
    END AS GENERATION_COHORT,
    SUM(CASE WHEN payment_method = 'Apple Pay' THEN 1 ELSE 0 END) AS APPLE_PAY_COUNT,
    SUM(CASE WHEN payment_method = 'PayPal' THEN 1 ELSE 0 END) AS PAYPAL_COUNT,
    SUM(CASE WHEN payment_method = 'Credit Card' THEN 1 ELSE 0 END) AS CREDIT_CARD_COUNT,
    SUM(CASE WHEN payment_method = 'Debit Card' THEN 1 ELSE 0 END) AS DEBIT_CARD_COUNT,
    SUM(CASE WHEN payment_method = 'Bank Transfer' THEN 1 ELSE 0 END) AS BANK_TRANSFER_COUNT,
    COUNT(transaction_id) AS TOTAL_TRANSACTIONS
FROM 
    retail_sales
GROUP BY 
    GENERATION_COHORT
ORDER BY 
    TOTAL_TRANSACTIONS DESC;


-- ----------------------------------------------------------------------------
-- QUERY 4: BEST AND WORST PERFORMING EXPANSION CITIES
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Rank cities based on total profitability to guide retail 
--                     brick-and-mortar expansion and localized marketing.
-- EXPECTED INSIGHT: Los Angeles and Seattle top the charts with strong sales 
--                  and margins, while Miami shows lower average returns.
-- ----------------------------------------------------------------------------
WITH CITY_PERFORMANCE AS (
    SELECT 
        city,
        region,
        ROUND(SUM(sales), 2) AS TOTAL_SALES,
        ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS REALIZED_MARGIN_PCT
    FROM 
        retail_sales
    GROUP BY 
        city, region
)
SELECT 
    city,
    region,
    TOTAL_SALES,
    TOTAL_PROFIT,
    REALIZED_MARGIN_PCT
FROM 
    CITY_PERFORMANCE
ORDER BY 
    TOTAL_PROFIT DESC;


-- ----------------------------------------------------------------------------
-- QUERY 5: THE HIGH-VALUED VS. LOW-PROFIT COHORT DICHOTOMY
-- DIFFICULTY: Advanced (CTE + CASE)
-- BUSINESS OBJECTIVE: Segment the active customer base into three profiles: 
--                     High-Value Spender, Loyal Repeater, and Bargain Hunter.
-- EXPECTED INSIGHT: Bargain Hunters account for high order volumes but minimal 
--                  profitability, while High-Value Spenders drive gross margins.
-- ----------------------------------------------------------------------------
WITH CUSTOMER_PROFILES AS (
    SELECT 
        customer_id,
        customer_name,
        COUNT(DISTINCT order_id) AS ORDER_COUNT,
        ROUND(SUM(sales), 2) AS LIFETIME_REVENUE,
        ROUND(SUM(profit), 2) AS LIFETIME_PROFIT,
        ROUND(AVG(discount) * 100, 2) AS AVG_DISCOUNT_PCT
    FROM 
        retail_sales
    GROUP BY 
        customer_id, customer_name
)
SELECT 
    CASE 
        WHEN LIFETIME_REVENUE >= 6000 AND AVG_DISCOUNT_PCT < 10.00 THEN '1. High-Value Spender (Premium Focus)'
        WHEN ORDER_COUNT >= 8 AND LIFETIME_PROFIT > 1000 THEN '2. Loyal Repeat Buyer (Core Anchor)'
        WHEN AVG_DISCOUNT_PCT >= 15.00 AND LIFETIME_PROFIT < 500 THEN '3. Bargain Hunter (Promo Sensitive)'
        ELSE '4. General Retail Shopper'
    END AS RETAIL_CUSTOMER_PROFILE,
    COUNT(customer_id) AS CUSTOMER_COUNT,
    ROUND(SUM(LIFETIME_REVENUE), 2) AS SEGMENT_SALES,
    ROUND(SUM(LIFETIME_PROFIT), 2) AS SEGMENT_PROFIT,
    ROUND(AVG(AVG_DISCOUNT_PCT), 2) AS SEGMENT_AVG_DISCOUNT
FROM 
    CUSTOMER_PROFILES
GROUP BY 
    RETAIL_CUSTOMER_PROFILE
ORDER BY 
    RETAIL_CUSTOMER_PROFILE ASC;


-- ----------------------------------------------------------------------------
-- QUERY 6: THE SEASONAL RE-STOCKING FORMULA
-- DIFFICULTY: Advanced (CTE)
-- BUSINESS OBJECTIVE: Analyze average unit sales of product categories in Q3 vs Q4 
--                     to help supply chain directors adjust inventory levels.
-- EXPECTED INSIGHT: Electronics sales double in Q4 compared to Q3, requiring 
--                  proactive restocking in September/October.
-- ----------------------------------------------------------------------------
WITH QUARTERLY_CAT_SALES AS (
    SELECT 
        product_category,
        SUM(CASE WHEN strftime('%m', order_date) IN ('07', '08', '09') THEN quantity ELSE 0 END) AS Q3_UNITS,
        SUM(CASE WHEN strftime('%m', order_date) IN ('10', '11', '12') THEN quantity ELSE 0 END) AS Q4_UNITS
    FROM 
        retail_sales
    GROUP BY 
        product_category
)
SELECT 
    product_category AS CATEGORY,
    Q3_UNITS AS UNITS_SOLD_Q3,
    Q4_UNITS AS UNITS_SOLD_Q4,
    Q4_UNITS - Q3_UNITS AS VOLUMETRIC_SPIKE,
    ROUND(((Q4_UNITS - Q3_UNITS) * 100.0 / Q3_UNITS), 2) AS SPIKE_PERCENT
FROM 
    QUARTERLY_CAT_SALES
ORDER BY 
    SPIKE_PERCENT DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: GENDER SEGMENT PREFERENCES IN CLOTHING AND BEAUTY
-- DIFFICULTY: Intermediate
-- BUSINESS OBJECTIVE: Assess if Clothing and Beauty & Health are dominated 
--                     by specific gender groups to align target ad spend.
-- EXPECTED INSIGHT: Shows that Beauty & Health purchases are evenly distributed, 
--                  debunking assumptions and optimizing ad-targeting.
-- ----------------------------------------------------------------------------
SELECT 
    product_category AS CATEGORY,
    gender AS GENDER,
    COUNT(DISTINCT customer_id) AS UNIQUE_BUYERS,
    SUM(quantity) AS UNITS_PURCHASED,
    ROUND(SUM(sales), 2) AS CATEGORICAL_SALES,
    ROUND(SUM(profit), 2) AS CATEGORICAL_PROFIT
FROM 
    retail_sales
WHERE 
    product_category IN ('Clothing', 'Beauty & Health')
GROUP BY 
    product_category, gender
ORDER BY 
    product_category ASC, CATEGORICAL_SALES DESC;


-- ----------------------------------------------------------------------------
-- QUERY 8: WEEKDAY VS WEEKEND SHOPPING BEHAVIORS
-- DIFFICULTY: Intermediate (strftime %w)
-- BUSINESS OBJECTIVE: Determine if checkout basket sizes differ on weekends 
--                     to optimize real-time promotions and server capacity.
-- EXPECTED INSIGHT: Weekend transactions show larger basket sizes, indicating 
--                  that customers take time to browse and add more items on Saturdays.
-- ----------------------------------------------------------------------------
WITH DAY_CLASSIFICATION AS (
    SELECT 
        transaction_id,
        sales,
        quantity,
        CASE 
            WHEN strftime('%w', order_date) IN ('0', '6') THEN 'Weekend'
            ELSE 'Weekday'
        END AS DAY_TYPE
    FROM 
        retail_sales
)
SELECT 
    DAY_TYPE,
    COUNT(transaction_id) AS TOTAL_LINE_ITEMS,
    ROUND(SUM(sales), 2) AS TOTAL_SALES,
    ROUND(AVG(sales), 2) AS AVG_TRANSACTION_VALUE,
    ROUND(AVG(quantity), 2) AS AVG_UNITS_PER_ITEM
FROM 
    DAY_CLASSIFICATION
GROUP BY 
    DAY_TYPE;


-- ----------------------------------------------------------------------------
-- QUERY 9: DISCOUNTS VS VOLUME CORRELATION MATRIX
-- DIFFICULTY: Advanced (Subquery + CTE)
-- BUSINESS OBJECTIVE: Map the pricing elasticity of demand. Identify the optimal 
--                     discount range that maximizes sales volume without losing profit.
-- EXPECTED INSIGHT: The 5-15% discount range represents the sweet spot, yielding 
--                  solid volume growth while preserving double-digit profit margins.
-- ----------------------------------------------------------------------------
WITH DISCOUNT_PERFORMANCE AS (
    SELECT 
        discount AS DISCOUNT_RATE,
        COUNT(transaction_id) AS TRANSACTION_COUNT,
        SUM(quantity) AS TOTAL_UNITS,
        ROUND(SUM(sales), 2) AS TOTAL_REVENUE,
        ROUND(SUM(profit), 2) AS TOTAL_PROFIT,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS REALIZED_MARGIN_PCT
    FROM 
        retail_sales
    GROUP BY 
        discount
)
SELECT 
    DISCOUNT_RATE * 100 AS DISCOUNT_PERCENTAGE,
    TRANSACTION_COUNT,
    TOTAL_UNITS,
    TOTAL_REVENUE,
    TOTAL_PROFIT,
    REALIZED_MARGIN_PCT
FROM 
    DISCOUNT_PERFORMANCE
ORDER BY 
    DISCOUNT_RATE ASC;
