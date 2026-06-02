-- SQL Query: Category & Sub-Category Sales and Profitability Analysis
SELECT 
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    SUM(quantity) AS total_quantity,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_percent,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_percent
FROM sales
GROUP BY category, sub_category
ORDER BY category, total_sales DESC;
