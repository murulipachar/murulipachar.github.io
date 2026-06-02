-- SQL Query: Monthly Sales and Profit Trends with Month-over-Month (MoM) Growth
WITH MonthlySales AS (
    SELECT 
        strftime('%Y-%m', order_date) AS order_month,
        ROUND(SUM(sales), 2) AS monthly_sales,
        ROUND(SUM(profit), 2) AS monthly_profit,
        COUNT(DISTINCT order_id) AS monthly_orders
    FROM sales
    GROUP BY order_month
)
SELECT 
    order_month,
    monthly_sales,
    monthly_profit,
    monthly_orders,
    ROUND(LAG(monthly_sales, 1) OVER (ORDER BY order_month), 2) AS previous_month_sales,
    ROUND(
        ((monthly_sales - LAG(monthly_sales, 1) OVER (ORDER BY order_month)) / 
        LAG(monthly_sales, 1) OVER (ORDER BY order_month)) * 100, 
        2
    ) AS mom_growth_percent
FROM MonthlySales
ORDER BY order_month;
