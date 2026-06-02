-- SQL Query: Calculate Executive KPIs
SELECT 
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_percent,
    COUNT(DISTINCT customer_id) AS total_customers
FROM sales;
