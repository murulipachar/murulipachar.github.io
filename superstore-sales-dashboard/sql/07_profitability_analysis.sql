-- SQL Query: Profitability by Discount Level Correlation Study
SELECT 
    discount AS discount_rate,
    COUNT(*) AS order_line_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit), 2) AS avg_profit_per_line,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_percent
FROM sales
GROUP BY discount_rate
ORDER BY discount_rate;
