-- SQL Query: Top 10 Profit-Generating Products and Bottom 5 Profit-Bleeding Products
WITH ProductSummary AS (
    SELECT 
        product_name,
        category,
        ROUND(SUM(sales), 2) AS total_sales,
        SUM(quantity) AS total_quantity,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND(AVG(discount) * 100, 2) AS avg_discount_percent
    FROM sales
    GROUP BY product_name, category
),
TopProfitable AS (
    SELECT 
        'TOP PROFITABLE' AS sku_classification,
        product_name,
        category,
        total_sales,
        total_quantity,
        total_profit,
        avg_discount_percent
    FROM ProductSummary
    ORDER BY total_profit DESC
    LIMIT 10
),
BottomProfitable AS (
    SELECT 
        'BOTTOM UNPROFITABLE' AS sku_classification,
        product_name,
        category,
        total_sales,
        total_quantity,
        total_profit,
        avg_discount_percent
    FROM ProductSummary
    ORDER BY total_profit ASC
    LIMIT 5
)
SELECT * FROM TopProfitable
UNION ALL
SELECT * FROM BottomProfitable;
