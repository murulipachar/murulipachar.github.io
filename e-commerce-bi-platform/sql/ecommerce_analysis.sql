-- ==============================================================================
-- E-COMMERCE BUSINESS INTELLIGENCE PLATFORM
-- SQL ANALYTICS ENGINE (50 ANALYTICS QUERIES)
--
-- Target Dialect: ANSI-SQL / PostgreSQL
-- This file contains production-grade SQL scripts answering core business inquiries.
--
-- Table Schemas Reference:
-- 1. regions (Region_ID, Region)
-- 2. categories (Category_ID, Category)
-- 3. products (Product_ID, Product_Name, Category_ID, Subcategory, Unit_Price, Unit_Cost)
-- 4. customers (Customer_ID, Customer_Name, Segment, Region_ID, State, City, Join_Date)
-- 5. orders (Order_ID, Customer_ID, Region_ID, State, City, Order_Date, Ship_Date, Ship_Mode)
-- 6. order_items (Order_Item_ID, Order_ID, Product_ID, Quantity, Unit_Price, Discount, Sales, Cost, Profit)
-- 7. returns (Order_ID, Return_Date, Return_Reason)
-- ==============================================================================

-- ==============================================================================
-- PART 1: FOUNDATIONAL OPERATIONS (10 QUERIES)
-- Filters, Grouping, Basic Aggregations, and HAVING clauses.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 01: Global Business performance KPIs
-- Business Objective: Determine overall sales volume, costs, and net profitability.
-- Logic: Aggregate Sales, Cost, and Profit columns from order_items.
-- Business Insight: Shows overall scale and baseline profit margins (Profit / Sales).
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(Cost)::NUMERIC, 2) AS Total_Cost,
    ROUND(SUM(Profit)::NUMERIC, 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales) * 100)::NUMERIC, 2) AS Profit_Margin_PCT
FROM order_items;

-- ------------------------------------------------------------------------------
-- Query 02: Top 5 States by Sales Volume
-- Business Objective: Find the states generating the highest revenues to guide expansion.
-- Logic: Group order sales by state from orders and order_items.
-- Business Insight: Identifies geographical powerhouses for resource allocation.
-- ------------------------------------------------------------------------------
SELECT 
    o.State,
    COUNT(DISTINCT o.Order_ID) AS Order_Count,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Total_Profit
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
GROUP BY o.State
ORDER BY Total_Sales DESC
LIMIT 5;

-- ------------------------------------------------------------------------------
-- Query 03: Inventory Evaluation - Premium High-Value Products
-- Business Objective: List all premium items priced over $500 to audit high-value stock.
-- Logic: Filter products by Unit_Price > 500, ordered by Category and Subcategory.
-- Business Insight: Highlights high-risk, high-value catalog items that require insurance or separate warehousing.
-- ------------------------------------------------------------------------------
SELECT 
    p.Product_ID,
    p.Product_Name,
    c.Category,
    p.Subcategory,
    p.Unit_Price,
    p.Unit_Cost,
    ROUND((p.Unit_Price - p.Unit_Cost)::NUMERIC, 2) AS Nominal_Margin
FROM products p
JOIN categories c ON p.Category_ID = c.Category_ID
WHERE p.Unit_Price > 500
ORDER BY c.Category, p.Subcategory, p.Unit_Price DESC;

-- ------------------------------------------------------------------------------
-- Query 04: Bulky Orders Audit (Quantity >= 5)
-- Business Objective: Track wholesale-like purchase behaviors to target bulk discount marketing.
-- Logic: Filter order_items where Quantity is 5 or more.
-- Business Insight: Highlights whether high-volume single-item orders represent a significant portion of sales.
-- ------------------------------------------------------------------------------
SELECT 
    Order_ID,
    Product_ID,
    Quantity,
    Sales,
    Profit,
    Discount
FROM order_items
WHERE Quantity >= 5
ORDER BY Quantity DESC, Sales DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 05: Office Supplies Segment Analysis for Consumer Segment
-- Business Objective: Focus on Consumer purchases within the Office Supplies category.
-- Logic: Join order_items, products, categories, orders, and customers with specific WHERE filters.
-- Business Insight: Audits standard retail office supply spend, a high-frequency low-value segment.
-- ------------------------------------------------------------------------------
SELECT 
    c.Segment,
    cat.Category,
    COUNT(DISTINCT o.Order_ID) AS Total_Orders,
    SUM(oi.Quantity) AS Total_Qty,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Total_Profit
FROM order_items oi
JOIN orders o ON oi.Order_ID = o.Order_ID
JOIN customers c ON o.Customer_ID = c.Customer_ID
JOIN products p ON oi.Product_ID = p.Product_ID
JOIN categories cat ON p.Category_ID = cat.Category_ID
WHERE c.Segment = 'Consumer' AND cat.Category = 'Office Supplies'
GROUP BY c.Segment, cat.Category;

-- ------------------------------------------------------------------------------
-- Query 06: Underperforming Subcategories (Negative Profit)
-- Business Objective: Find subcategories losing money to identify pricing or return issues.
-- Logic: Group by subcategory and filter using HAVING SUM(Profit) < 0.
-- Business Insight: Signals category managers to renegotiate vendor costs or cut items.
-- ------------------------------------------------------------------------------
SELECT 
    p.Subcategory,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(oi.Cost)::NUMERIC, 2) AS Total_Cost,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Net_Profit,
    ROUND((SUM(oi.Profit) / SUM(oi.Sales) * 100)::NUMERIC, 2) AS Profit_Margin_PCT
FROM order_items oi
JOIN products p ON oi.Product_ID = p.Product_ID
GROUP BY p.Subcategory
HAVING SUM(oi.Profit) < 0
ORDER BY Net_Profit ASC;

-- ------------------------------------------------------------------------------
-- Query 07: Average Discount Rate by Region
-- Business Objective: Evaluate regional sales team discount behaviors.
-- Logic: Join order_items, orders, regions, group by region.
-- Business Insight: Shows if some regional teams rely too heavily on price slashing to hit sales targets.
-- ------------------------------------------------------------------------------
SELECT 
    r.Region,
    ROUND(AVG(oi.Discount) * 100, 2) AS Avg_Discount_Percent,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Total_Profit
FROM order_items oi
JOIN orders o ON oi.Order_ID = o.Order_ID
JOIN regions r ON o.Region_ID = r.Region_ID
GROUP BY r.Region
ORDER BY Avg_Discount_Percent DESC;

-- ------------------------------------------------------------------------------
-- Query 08: Year 2025 Order Volume & Seasonality Check
-- Business Objective: Extract transaction counts and volume specifically for the year 2025.
-- Logic: EXTRACT or LIKE or DATE range on Order_Date.
-- Business Insight: Serves as a baseline benchmark for YoY modeling.
-- ------------------------------------------------------------------------------
SELECT 
    TO_CHAR(Order_Date::DATE, 'YYYY-MM') AS Order_Month,
    COUNT(DISTINCT Order_ID) AS Order_Count,
    SUM(Quantity) AS Total_Items,
    ROUND(SUM(Sales)::NUMERIC, 2) AS Sales_Volume
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
WHERE Order_Date >= '2025-01-01' AND Order_Date <= '2025-12-31'
GROUP BY TO_CHAR(Order_Date::DATE, 'YYYY-MM')
ORDER BY Order_Month;

-- ------------------------------------------------------------------------------
-- Query 09: Top 10 Most Expensive Products
-- Business Objective: Identify peak pricing in the product catalogue.
-- Logic: SELECT Unit_Price from products, ORDER BY Unit_Price DESC.
-- Business Insight: Reveals high-end inventory candidates for premium marketing.
-- ------------------------------------------------------------------------------
SELECT 
    p.Product_ID,
    p.Product_Name,
    c.Category,
    p.Subcategory,
    p.Unit_Price
FROM products p
JOIN categories c ON p.Category_ID = c.Category_ID
ORDER BY p.Unit_Price DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 10: Segment Distribution in Key States (NY & CA)
-- Business Objective: Analyze customer demographics in the two highest-volume states.
-- Logic: Group by State and Segment, filtering for CA and NY.
-- Business Insight: Reveals whether corporate or individual buyers dominate coastal states.
-- ------------------------------------------------------------------------------
SELECT 
    State,
    Segment,
    COUNT(Customer_ID) AS Customer_Count,
    MIN(Join_Date) AS Earliest_Join_Date
FROM customers
WHERE State IN ('California', 'New York')
GROUP BY State, Segment
ORDER BY State, Customer_Count DESC;


-- ==============================================================================
-- PART 2: MULTI-TABLE JOINS & RELATIONAL AUDITS (10 QUERIES)
-- Inner, Outer Joins, and Relational Integrity Checks.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 11: Comprehensive Transaction Detail Log
-- Business Objective: Generate a master transaction log linking customers, regions, products, and order values.
-- Logic: Join 5 tables (orders, customers, regions, order_items, products).
-- Business Insight: Standard dashboard back-end view for transactional detail auditing.
-- ------------------------------------------------------------------------------
SELECT 
    o.Order_ID,
    o.Order_Date,
    c.Customer_Name,
    r.Region,
    p.Product_Name,
    oi.Quantity,
    oi.Sales,
    oi.Profit
FROM orders o
JOIN customers c ON o.Customer_ID = c.Customer_ID
JOIN regions r ON o.Region_ID = r.Region_ID
JOIN order_items oi ON o.Order_ID = oi.Order_ID
JOIN products p ON oi.Product_ID = p.Product_ID
ORDER BY o.Order_Date DESC, o.Order_ID
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 12: Profitability of Delivered vs Returned Orders
-- Business Objective: Measure the precise cash impact of returns on our bottom line.
-- Logic: Left join orders with returns; analyze aggregates by return status.
-- Business Insight: quantifies lost profit and operational drag from returns.
-- ------------------------------------------------------------------------------
SELECT 
    CASE WHEN ret.Order_ID IS NOT NULL THEN 'Returned' ELSE 'Successfully Delivered' END AS Order_Status,
    COUNT(DISTINCT o.Order_ID) AS Order_Count,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Gross_Sales,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Net_Profit,
    ROUND((SUM(oi.Profit)/SUM(oi.Sales)*100)::NUMERIC, 2) AS Margin_PCT
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
LEFT JOIN returns ret ON o.Order_ID = ret.Order_ID
GROUP BY CASE WHEN ret.Order_ID IS NOT NULL THEN 'Returned' ELSE 'Successfully Delivered' END;

-- ------------------------------------------------------------------------------
-- Query 13: Product Category Return Rates
-- Business Objective: Determine which categories have the highest return rates.
-- Logic: Join products, categories, order_items, orders, and left join returns.
-- Business Insight: Highlights high-return products (like Furniture) requiring packaging or description audits.
-- ------------------------------------------------------------------------------
SELECT 
    c.Category,
    COUNT(DISTINCT o.Order_ID) AS Total_Orders,
    COUNT(DISTINCT ret.Order_ID) AS Returned_Orders,
    ROUND((COUNT(DISTINCT ret.Order_ID)::NUMERIC / COUNT(DISTINCT o.Order_ID)::NUMERIC * 100), 2) AS Return_Rate_PCT
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
JOIN products p ON oi.Product_ID = p.Product_ID
JOIN categories c ON p.Category_ID = c.Category_ID
LEFT JOIN returns ret ON o.Order_ID = ret.Order_ID
GROUP BY c.Category
ORDER BY Return_Rate_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 14: Customer Order Frequency Distribution
-- Business Objective: Identify customer loyalty tiers by lifetime order counts.
-- Logic: Join customers and orders, group by customer.
-- Business Insight: Helps differentiate one-time buyers from heavy users to tailor campaigns.
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    c.Segment,
    COUNT(o.Order_ID) AS Lifetime_Orders,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Lifetime_Spend,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Lifetime_Profit
FROM customers c
LEFT JOIN orders o ON c.Customer_ID = o.Customer_ID
LEFT JOIN order_items oi ON o.Order_ID = oi.Order_ID
GROUP BY c.Customer_ID, c.Customer_Name, c.Segment
ORDER BY Lifetime_Orders DESC, Lifetime_Spend DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 15: Regional Shipping Cost Surcharge Impact
-- Business Objective: Quantify profit compression in the South Region (REG-03) due to logistics.
-- Logic: Join orders, order_items, regions; calculate profit margin rates.
-- Business Insight: Confirms if the 8% shipping surcharge in REG-03 makes it less profitable.
-- ------------------------------------------------------------------------------
SELECT 
    r.Region,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(oi.Cost)::NUMERIC, 2) AS Total_Cost,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Total_Profit,
    ROUND((SUM(oi.Profit) / SUM(oi.Sales) * 100)::NUMERIC, 2) AS Net_Margin_PCT
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
JOIN regions r ON o.Region_ID = r.Region_ID
GROUP BY r.Region
ORDER BY Net_Margin_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 16: Returned Products Audit & Common Reasons
-- Business Objective: Investigate why specific subcategories get returned.
-- Logic: Join order_items, products, and returns.
-- Business Insight: Highlights qualitative return factors (e.g. late shipping vs wrong items).
-- ------------------------------------------------------------------------------
SELECT 
    p.Subcategory,
    ret.Return_Reason,
    COUNT(DISTINCT o.Order_ID) AS Return_Count,
    SUM(oi.Quantity) AS Returned_Quantity,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Lost_Sales
FROM order_items oi
JOIN products p ON oi.Product_ID = p.Product_ID
JOIN orders o ON oi.Order_ID = o.Order_ID
JOIN returns ret ON o.Order_ID = ret.Order_ID
GROUP BY p.Subcategory, ret.Return_Reason
ORDER BY Lost_Sales DESC, Return_Count DESC;

-- ------------------------------------------------------------------------------
-- Query 17: Shipping Latency Analysis by Mode
-- Business Objective: Compare actual shipping delays (in days) against targets for shipping modes.
-- Logic: Group ship mode, calculate difference between Ship_Date and Order_Date.
-- Business Insight: Measures carrier SLAs. Standard Class taking >5 days increases return risk.
-- ------------------------------------------------------------------------------
SELECT 
    o.Ship_Mode,
    COUNT(o.Order_ID) AS Total_Orders,
    ROUND(AVG(o.Ship_Date::DATE - o.Order_Date::DATE), 2) AS Avg_Days_To_Ship,
    MAX(o.Ship_Date::DATE - o.Order_Date::DATE) AS Max_Days_To_Ship,
    MIN(o.Ship_Date::DATE - o.Order_Date::DATE) AS Min_Days_To_Ship
FROM orders o
GROUP BY o.Ship_Mode
ORDER BY Avg_Days_To_Ship;

-- ------------------------------------------------------------------------------
-- Query 18: Unsold Catalog Products (Relational Integrity check)
-- Business Objective: Find products in the database that have never recorded a sale.
-- Logic: Right outer join or LEFT join where order_item is NULL.
-- Business Insight: Identifies dead stock or catalog entry errors to clean the database.
-- ------------------------------------------------------------------------------
SELECT 
    p.Product_ID,
    p.Product_Name,
    c.Category,
    p.Subcategory,
    p.Unit_Price
FROM products p
JOIN categories c ON p.Category_ID = c.Category_ID
LEFT JOIN order_items oi ON p.Product_ID = oi.Product_ID
WHERE oi.Order_Item_ID IS NULL
ORDER BY p.Product_ID;

-- ------------------------------------------------------------------------------
-- Query 19: Order Values by Customer Segment
-- Business Objective: Determine which customer segments generate the largest baskets.
-- Logic: Join customers, orders, order_items; aggregate total spend and average basket size.
-- Business Insight: Tells us whether B2B (Corporate) baskets are larger than consumer ones.
-- ------------------------------------------------------------------------------
SELECT 
    c.Segment,
    COUNT(DISTINCT o.Order_ID) AS Total_Orders,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(AVG(oi.Sales)::NUMERIC, 2) AS Avg_Item_Value,
    ROUND((SUM(oi.Sales) / COUNT(DISTINCT o.Order_ID))::NUMERIC, 2) AS Avg_Order_Value
FROM customers c
JOIN orders o ON c.Customer_ID = o.Customer_ID
JOIN order_items oi ON o.Order_ID = oi.Order_ID
GROUP BY c.Segment
ORDER BY Avg_Order_Value DESC;

-- ------------------------------------------------------------------------------
-- Query 20: VIP Customers in East Region
-- Business Objective: Extract high-value customers located in the East Region (REG-01).
-- Logic: Join customers, orders, order_items, filter by Region_ID = REG-01, group, HAVING spend > $3000.
-- Business Insight: Identifies local VIPs for regional targeted events or concierge service.
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    c.State,
    c.City,
    COUNT(DISTINCT o.Order_ID) AS Total_Orders,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Lifetime_East_Spend,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Lifetime_East_Profit
FROM customers c
JOIN orders o ON c.Customer_ID = o.Customer_ID
JOIN order_items oi ON o.Order_ID = oi.Order_ID
WHERE c.Region_ID = 'REG-01'
GROUP BY c.Customer_ID, c.Customer_Name, c.State, c.City
HAVING SUM(oi.Sales) > 3000
ORDER BY Lifetime_East_Spend DESC;


-- ==============================================================================
-- PART 3: ADVANCED CONDITIONAL METRICS & SUBQUERIES (10 QUERIES)
-- Nested Selects, Correlated Subqueries, and Complex Case statements.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 21: High Discount Profitability Audit
-- Business Objective: Assess profitability when discounts exceed 30%.
-- Logic: CASE WHEN categorization inside aggregate.
-- Business Insight: quantifies the extent of discount-driven margin loss.
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN Discount = 0 THEN '0% No Discount'
        WHEN Discount > 0 AND Discount <= 0.15 THEN '1-15% Light Discount'
        WHEN Discount > 0.15 AND Discount <= 0.30 THEN '16-30% Moderate Discount'
        ELSE '31%+: High Discount'
    END AS Discount_Tier,
    COUNT(Order_Item_ID) AS Item_Count,
    ROUND(SUM(Sales)::NUMERIC, 2) AS Total_Sales,
    ROUND(SUM(Profit)::NUMERIC, 2) AS Net_Profit,
    ROUND((SUM(Profit) / SUM(Sales) * 100)::NUMERIC, 2) AS Net_Margin_PCT
FROM order_items
GROUP BY 
    CASE 
        WHEN Discount = 0 THEN '0% No Discount'
        WHEN Discount > 0 AND Discount <= 0.15 THEN '1-15% Light Discount'
        WHEN Discount > 0.15 AND Discount <= 0.30 THEN '16-30% Moderate Discount'
        ELSE '31%+: High Discount'
    END
ORDER BY Discount_Tier;

-- ------------------------------------------------------------------------------
-- Query 22: Customers with Above-Average Basket Values
-- Business Objective: Target elite spenders whose average order value exceeds the company average.
-- Logic: Subquery to calculate global AOV, filtering grouped customers.
-- Business Insight: Builds the list of high-spending customers for priority support.
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    ROUND(AVG(sub.Order_Sales)::NUMERIC, 2) AS Customer_Avg_Order_Value
FROM customers c
JOIN (
    SELECT Order_ID, Customer_ID, SUM(Sales) AS Order_Sales
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY Order_ID, Customer_ID
) sub ON c.Customer_ID = sub.Customer_ID
GROUP BY c.Customer_ID, c.Customer_Name
HAVING AVG(sub.Order_Sales) > (
    SELECT AVG(Order_Sales) 
    FROM (
        SELECT Order_ID, SUM(Sales) AS Order_Sales
        FROM order_items
        GROUP BY Order_ID
    ) global_sales
)
ORDER BY Customer_Avg_Order_Value DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 23: Returns Driven by Extreme Shipping Latencies
-- Business Objective: Determine if late shipping (>5 days) directly correlates with product returns.
-- Logic: Subquery measuring shipping latency, left join with returns, group by delay status.
-- Business Insight: Shows if logistics failures drive customers to reject products.
-- ------------------------------------------------------------------------------
SELECT 
    CASE WHEN (o.Ship_Date::DATE - o.Order_Date::DATE) > 5 THEN 'Delayed (>5 Days)' ELSE 'On-Time (<=5 Days)' END AS Shipping_Status,
    COUNT(DISTINCT o.Order_ID) AS Total_Orders,
    COUNT(DISTINCT ret.Order_ID) AS Returned_Orders,
    ROUND((COUNT(DISTINCT ret.Order_ID)::NUMERIC / COUNT(DISTINCT o.Order_ID)::NUMERIC * 100), 2) AS Return_Rate_PCT
FROM orders o
LEFT JOIN returns ret ON o.Order_ID = ret.Order_ID
GROUP BY CASE WHEN (o.Ship_Date::DATE - o.Order_Date::DATE) > 5 THEN 'Delayed (>5 Days)' ELSE 'On-Time (<=5 Days)' END;

-- ------------------------------------------------------------------------------
-- Query 24: Top Product in Each Subcategory (Correlated Subquery)
-- Business Objective: Identify the #1 flagship product for each subcategory.
-- Logic: Correlated subquery checking total sales.
-- Business Insight: pinpoints product catalogue stars that drive category success.
-- ------------------------------------------------------------------------------
SELECT 
    p1.Subcategory,
    p1.Product_ID,
    p1.Product_Name,
    ROUND(SUM(oi1.Sales)::NUMERIC, 2) AS Product_Sales
FROM products p1
JOIN order_items oi1 ON p1.Product_ID = oi1.Product_ID
GROUP BY p1.Subcategory, p1.Product_ID, p1.Product_Name
HAVING SUM(oi1.Sales) = (
    SELECT MAX(Subcat_Sales)
    FROM (
        SELECT p2.Product_ID, SUM(oi2.Sales) AS Subcat_Sales
        FROM products p2
        JOIN order_items oi2 ON p2.Product_ID = oi2.Product_ID
        WHERE p2.Subcategory = p1.Subcategory
        GROUP BY p2.Product_ID
    ) inner_agg
)
ORDER BY Product_Sales DESC;

-- ------------------------------------------------------------------------------
-- Query 25: Cross-Category Orders (Tech and Furniture)
-- Business Objective: Find orders where high-end Tech and Furniture were bought together.
-- Logic: Intersect or EXISTS clauses validating dual presence in order items.
-- Business Insight: Targets customers buying home office upgrades (Chairs/Tables + Phones/Accessories).
-- ------------------------------------------------------------------------------
SELECT 
    o.Order_ID,
    o.Order_Date,
    o.Customer_ID,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS Order_Total
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
WHERE EXISTS (
    SELECT 1 FROM order_items oi_tech 
    JOIN products p_tech ON oi_tech.Product_ID = p_tech.Product_ID
    WHERE oi_tech.Order_ID = o.Order_ID AND p_tech.Category_ID = 'CAT-01' -- Tech
)
AND EXISTS (
    SELECT 1 FROM order_items oi_furn 
    JOIN products p_furn ON oi_furn.Product_ID = p_furn.Product_ID
    WHERE oi_furn.Order_ID = o.Order_ID AND p_furn.Category_ID = 'CAT-02' -- Furniture
)
GROUP BY o.Order_ID, o.Order_Date, o.Customer_ID
ORDER BY Order_Total DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 26: Underperforming Regions - States Below Regional Average
-- Business Objective: Find specific states whose sales are lower than the average state sales in their region.
-- Logic: Compare state sales against regional state averages calculated via subquery.
-- Business Insight: Isolates struggling states inside otherwise healthy regions.
-- ------------------------------------------------------------------------------
SELECT 
    o.Region_ID,
    r.Region,
    o.State,
    ROUND(SUM(oi.Sales)::NUMERIC, 2) AS State_Sales
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
JOIN regions r ON o.Region_ID = r.Region_ID
GROUP BY o.Region_ID, r.Region, o.State
HAVING SUM(oi.Sales) < (
    SELECT AVG(State_Sales)
    FROM (
        SELECT o_inner.Region_ID, o_inner.State, SUM(oi_inner.Sales) AS State_Sales
        FROM orders o_inner
        JOIN order_items oi_inner ON o_inner.Order_ID = oi_inner.Order_ID
        GROUP BY o_inner.Region_ID, o_inner.State
    ) sub
    WHERE sub.Region_ID = o.Region_ID
)
ORDER BY r.Region, State_Sales ASC;

-- ------------------------------------------------------------------------------
-- Query 27: Customer Contribution Classification
-- Business Objective: Score and segment customer base based on profit contributions.
-- Logic: CASE WHEN statements grouping lifetime profit.
-- Business Insight: Supports retention marketing (VIPs vs margin drainers).
-- ------------------------------------------------------------------------------
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    ROUND(SUM(oi.Profit)::NUMERIC, 2) AS Lifetime_Profit,
    CASE 
        WHEN SUM(oi.Profit) > 1500 THEN 'Platinum Contributor (>$1500)'
        WHEN SUM(oi.Profit) > 500 AND SUM(oi.Profit) <= 1500 THEN 'Gold Contributor ($500-$1500)'
        WHEN SUM(oi.Profit) >= 0 AND SUM(oi.Profit) <= 500 THEN 'Silver Contributor ($0-$500)'
        ELSE 'Unprofitable / Margin Squeeze (<$0)'
    END AS Profitability_Class
FROM customers c
JOIN orders o ON c.Customer_ID = o.Customer_ID
JOIN order_items oi ON o.Order_ID = oi.Order_ID
GROUP BY c.Customer_ID, c.Customer_Name
ORDER BY Lifetime_Profit DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 28: Subcategories Exceeding Global Return Rate
-- Business Objective: Track subcategories experiencing higher than normal return rates.
-- Logic: Group return rates compared to global return rate in HAVING subquery.
-- Business Insight: Isolates subcategories with systemic issues (quality control/defect rates).
-- ------------------------------------------------------------------------------
SELECT 
    p.Subcategory,
    COUNT(DISTINCT oi.Order_ID) AS Total_Sales_Orders,
    COUNT(DISTINCT ret.Order_ID) AS Returned_Orders,
    ROUND((COUNT(DISTINCT ret.Order_ID)::NUMERIC / COUNT(DISTINCT oi.Order_ID) * 100), 2) AS Return_Rate_PCT
FROM order_items oi
JOIN products p ON oi.Product_ID = p.Product_ID
LEFT JOIN returns ret ON oi.Order_ID = ret.Order_ID
GROUP BY p.Subcategory
HAVING (COUNT(DISTINCT ret.Order_ID)::NUMERIC / COUNT(DISTINCT oi.Order_ID) * 100) > (
    SELECT (COUNT(DISTINCT r_g.Order_ID)::NUMERIC / COUNT(DISTINCT o_g.Order_ID) * 100)
    FROM orders o_g
    LEFT JOIN returns r_g ON o_g.Order_ID = r_g.Order_ID
)
ORDER BY Return_Rate_PCT DESC;

-- ------------------------------------------------------------------------------
-- Query 29: Products Priced Higher Than Subcategory Average
-- Business Objective: Audit luxury products that carry premium pricing inside their category.
-- Logic: Correlated subquery checking Unit_Price against Subcategory average.
-- Business Insight: Helps ensure price premium is justified by customer value.
-- ------------------------------------------------------------------------------
SELECT 
    p.Product_ID,
    p.Product_Name,
    p.Subcategory,
    p.Unit_Price,
    ROUND((SELECT AVG(p_avg.Unit_Price) FROM products p_avg WHERE p_avg.Subcategory = p.Subcategory)::NUMERIC, 2) AS Subcategory_Avg_Price
FROM products p
WHERE p.Unit_Price > (
    SELECT AVG(p_avg.Unit_Price)
    FROM products p_avg
    WHERE p_avg.Subcategory = p.Subcategory
)
ORDER BY p.Subcategory, p.Unit_Price DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 30: Unprofitable High-Discount Orders
-- Business Objective: Track orders where discounting resulted in a net loss.
-- Logic: Filter orders where Discount > 0 and Profit < 0.
-- Business Insight: Demonstrates the concrete cost of excessive sales discounting.
-- ------------------------------------------------------------------------------
SELECT 
    oi.Order_ID,
    p.Product_Name,
    oi.Quantity,
    oi.Discount,
    oi.Sales,
    oi.Profit
FROM order_items oi
JOIN products p ON oi.Product_ID = p.Product_ID
WHERE oi.Discount >= 0.20 AND oi.Profit < 0
ORDER BY oi.Profit ASC
LIMIT 10;


-- ==============================================================================
-- PART 4: COMMON TABLE EXPRESSIONS (CTEs) (10 QUERIES)
-- Multi-step analysis, Cohorts, Lifetime Value, and Recursive-like logic.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 31: Monthly Year-Over-Year Sales Growth
-- Business Objective: Evaluate sales acceleration month-by-month across years.
-- Logic: CTE aggregations grouped by year and month.
-- Business Insight: Isolates seasonal revenue spikes from true growth trends.
-- ------------------------------------------------------------------------------
WITH Monthly_Sales AS (
    SELECT 
        EXTRACT(YEAR FROM Order_Date::DATE) AS Sales_Year,
        EXTRACT(MONTH FROM Order_Date::DATE) AS Sales_Month,
        SUM(Sales) AS Total_Sales
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY EXTRACT(YEAR FROM Order_Date::DATE), EXTRACT(MONTH FROM Order_Date::DATE)
)
SELECT 
    cur.Sales_Month,
    ROUND(SUM(CASE WHEN cur.Sales_Year = 2024 THEN cur.Total_Sales ELSE 0 END)::NUMERIC, 2) AS Sales_2024,
    ROUND(SUM(CASE WHEN cur.Sales_Year = 2025 THEN cur.Total_Sales ELSE 0 END)::NUMERIC, 2) AS Sales_2025,
    ROUND(SUM(CASE WHEN cur.Sales_Year = 2026 THEN cur.Total_Sales ELSE 0 END)::NUMERIC, 2) AS Sales_2026
FROM Monthly_Sales cur
GROUP BY cur.Sales_Month
ORDER BY cur.Sales_Month;

-- ------------------------------------------------------------------------------
-- Query 32: Monthly Cohort Join Volumes
-- Business Objective: Monitor the acquisition pace of new customer cohorts over time.
-- Logic: CTE counting registrations by cohort month.
-- Business Insight: Evaluates marketing acquisition strength month-by-month.
-- ------------------------------------------------------------------------------
WITH Cohorts AS (
    SELECT 
        TO_CHAR(Join_Date::DATE, 'YYYY-MM') AS Cohort_Month,
        Customer_ID
    FROM customers
)
SELECT 
    Cohort_Month,
    COUNT(Customer_ID) AS New_Customers_Acquired
FROM Cohorts
GROUP BY Cohort_Month
ORDER BY Cohort_Month;

-- ------------------------------------------------------------------------------
-- Query 33: 30-Day Repeat Purchase Rate
-- Business Objective: Calculate the percentage of customers who buy again within 30 days of their first order.
-- Logic: CTE finding first order date, second order date, and calculating diff.
-- Business Insight: Key SaaS/E-commerce metric indicating brand stickiness.
-- ------------------------------------------------------------------------------
WITH First_Orders AS (
    SELECT 
        Customer_ID,
        MIN(Order_Date::DATE) AS First_Order_Date
    FROM orders
    GROUP BY Customer_ID
),
Subsequent_Orders AS (
    SELECT 
        o.Customer_ID,
        o.Order_Date::DATE AS Next_Order_Date
    FROM orders o
    JOIN First_Orders fo ON o.Customer_ID = fo.Customer_ID
    WHERE o.Order_Date::DATE > fo.First_Order_Date
),
Next_Order_Diff AS (
    SELECT 
        so.Customer_ID,
        MIN(so.Next_Order_Date - fo.First_Order_Date) AS Days_To_Next_Order
    FROM Subsequent_Orders so
    JOIN First_Orders fo ON so.Customer_ID = fo.Customer_ID
    GROUP BY so.Customer_ID
)
SELECT 
    (SELECT COUNT(DISTINCT Customer_ID) FROM orders) AS Total_Transacting_Customers,
    COUNT(Customer_ID) AS Repeat_Customers_Within_30_Days,
    ROUND((COUNT(Customer_ID)::NUMERIC / (SELECT COUNT(DISTINCT Customer_ID) FROM orders) * 100), 2) AS Repeat_Rate_30_Days_PCT
FROM Next_Order_Diff
WHERE Days_To_Next_Order <= 30;

-- ------------------------------------------------------------------------------
-- Query 34: Customer Lifetime Value (LTV) Decile Segmentation
-- Business Objective: Group customer profiles into deciles to target high-end offers.
-- Logic: CTE calculates spend, NTILE(10) assigns deciles.
-- Business Insight: Identifies the exact revenue concentration (e.g. does the top 10% generate 50% of sales?).
-- ------------------------------------------------------------------------------
WITH Customer_LTV AS (
    SELECT 
        c.Customer_ID,
        c.Customer_Name,
        SUM(oi.Sales) AS Lifetime_Value
    FROM customers c
    JOIN orders o ON c.Customer_ID = o.Customer_ID
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY c.Customer_ID, c.Customer_Name
),
LTV_Deciles AS (
    SELECT 
        Customer_ID,
        Customer_Name,
        Lifetime_Value,
        NTILE(10) OVER (ORDER BY Lifetime_Value DESC) AS LTV_Decile
    FROM Customer_LTV
)
SELECT 
    LTV_Decile,
    COUNT(Customer_ID) AS Customer_Count,
    ROUND(MIN(Lifetime_Value)::NUMERIC, 2) AS Floor_LTV,
    ROUND(MAX(Lifetime_Value)::NUMERIC, 2) AS Ceiling_LTV,
    ROUND(SUM(Lifetime_Value)::NUMERIC, 2) AS Decile_Total_Revenue
FROM LTV_Deciles
GROUP BY LTV_Decile
ORDER BY LTV_Decile;

-- ------------------------------------------------------------------------------
-- Query 35: Top 3 Sales Products Per Subcategory
-- Business Objective: Determine subcategory leaders for homepage promotion.
-- Logic: CTE ranking products with DENSE_RANK inside.
-- Business Insight: Highlights which products represent the majority of category revenue.
-- ------------------------------------------------------------------------------
WITH Product_Subcategory_Sales AS (
    SELECT 
        p.Subcategory,
        p.Product_ID,
        p.Product_Name,
        SUM(oi.Sales) AS Total_Sales,
        DENSE_RANK() OVER (PARTITION BY p.Subcategory ORDER BY SUM(oi.Sales) DESC) AS Sales_Rank
    FROM order_items oi
    JOIN products p ON oi.Product_ID = p.Product_ID
    GROUP BY p.Subcategory, p.Product_ID, p.Product_Name
)
SELECT 
    Subcategory,
    Sales_Rank,
    Product_ID,
    Product_Name,
    ROUND(Total_Sales::NUMERIC, 2) AS Product_Sales
FROM Product_Subcategory_Sales
WHERE Sales_Rank <= 3
ORDER BY Subcategory, Sales_Rank;

-- ------------------------------------------------------------------------------
-- Query 36: Quarterly Profit Margin Growth MoM
-- Business Objective: Track quarterly changes in profit margins.
-- Logic: CTE to group by Year and Quarter, calculate metrics.
-- Business Insight: Provides clean executive performance reporting.
-- ------------------------------------------------------------------------------
WITH Quarterly_Metrics AS (
    SELECT 
        EXTRACT(YEAR FROM o.Order_Date::DATE) AS Fiscal_Year,
        EXTRACT(QUARTER FROM o.Order_Date::DATE) AS Fiscal_Quarter,
        SUM(oi.Sales) AS Total_Sales,
        SUM(oi.Profit) AS Total_Profit
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY EXTRACT(YEAR FROM o.Order_Date::DATE), EXTRACT(QUARTER FROM o.Order_Date::DATE)
)
SELECT 
    Fiscal_Year,
    Fiscal_Quarter,
    ROUND(Total_Sales::NUMERIC, 2) AS Quarter_Sales,
    ROUND(Total_Profit::NUMERIC, 2) AS Quarter_Profit,
    ROUND((Total_Profit / Total_Sales * 100)::NUMERIC, 2) AS Quarter_Margin_PCT
FROM Quarterly_Metrics
ORDER BY Fiscal_Year, Fiscal_Quarter;

-- ------------------------------------------------------------------------------
-- Query 37: Customer Category Purchase Affinity
-- Business Objective: Determine the product category combination purchased first by buyers.
-- Logic: CTE finding customer first order items and categories.
-- Business Insight: Informs product onboarding cross-sell strategies.
-- ------------------------------------------------------------------------------
WITH Customer_First_Order AS (
    SELECT 
        Customer_ID,
        MIN(Order_ID) AS First_Order_ID
    FROM orders
    GROUP BY Customer_ID
),
First_Order_Categories AS (
    SELECT 
        cfo.Customer_ID,
        cat.Category,
        COUNT(oi.Order_Item_ID) AS Category_Item_Count
    FROM Customer_First_Order cfo
    JOIN order_items oi ON cfo.First_Order_ID = oi.Order_ID
    JOIN products p ON oi.Product_ID = p.Product_ID
    JOIN categories cat ON p.Category_ID = cat.Category_ID
    GROUP BY cfo.Customer_ID, cat.Category
)
SELECT 
    Category AS Entry_Category,
    COUNT(DISTINCT Customer_ID) AS Customer_Count
FROM First_Order_Categories
GROUP BY Category
ORDER BY Customer_Count DESC;

-- ------------------------------------------------------------------------------
-- Query 38: Discount Elasticity Performance Matrix
-- Business Objective: Formulate profit impact groups based on discount thresholds.
-- Logic: CTE grouping records, aggregating elasticity ratios.
-- Business Insight: Shows that profit margins collapse above 20% discount.
-- ------------------------------------------------------------------------------
WITH Item_Discounts AS (
    SELECT 
        Quantity,
        Discount,
        Sales,
        Cost,
        Profit
    FROM order_items
)
SELECT 
    CASE 
        WHEN Discount = 0 THEN '0% No Discount'
        WHEN Discount > 0 AND Discount <= 0.10 THEN '0-10% Low Discount'
        WHEN Discount > 0.10 AND Discount <= 0.20 THEN '10-20% Medium Discount'
        ELSE '20%+ High Discount'
    END AS Discount_Policy,
    COUNT(*) AS Transactions,
    SUM(Quantity) AS Total_Qty,
    ROUND(SUM(Sales)::NUMERIC, 2) AS Sales_Volume,
    ROUND(SUM(Profit)::NUMERIC, 2) AS Net_Profit,
    ROUND((SUM(Profit) / SUM(Sales) * 100)::NUMERIC, 2) AS Profitability_Rate
FROM Item_Discounts
GROUP BY 
    CASE 
        WHEN Discount = 0 THEN '0% No Discount'
        WHEN Discount > 0 AND Discount <= 0.10 THEN '0-10% Low Discount'
        WHEN Discount > 0.10 AND Discount <= 0.20 THEN '10-20% Medium Discount'
        ELSE '20%+ High Discount'
    END
ORDER BY Profitability_Rate DESC;

-- ------------------------------------------------------------------------------
-- Query 39: Returns Lost Sales Contribution
-- Business Objective: Identify which regions and categories contribute the most to lost sales from returns.
-- Logic: CTE filtering returns, grouping by dimensions.
-- Business Insight: Localizes return risk to optimize shipping/logistics.
-- ------------------------------------------------------------------------------
WITH Returned_Sales AS (
    SELECT 
        r.Region,
        c.Category,
        oi.Sales AS Returned_Val
    FROM returns ret
    JOIN order_items oi ON ret.Order_ID = oi.Order_ID
    JOIN products p ON oi.Product_ID = p.Product_ID
    JOIN categories c ON p.Category_ID = c.Category_ID
    JOIN orders o ON ret.Order_ID = o.Order_ID
    JOIN regions r ON o.Region_ID = r.Region_ID
)
SELECT 
    Region,
    Category,
    ROUND(SUM(Returned_Val)::NUMERIC, 2) AS Gross_Returned_Revenue,
    COUNT(*) AS Return_Items_Count
FROM Returned_Sales
GROUP BY Region, Category
ORDER BY Gross_Returned_Revenue DESC;

-- ------------------------------------------------------------------------------
-- Query 40: Customer Order Latency (Days Between Orders)
-- Business Objective: Determine how long repeat customers wait before ordering again.
-- Logic: Lead/Lag within CTE, calculating average days.
-- Business Insight: Establishes purchase frequency profiles to trigger timed marketing emails.
-- ------------------------------------------------------------------------------
WITH Order_Dates AS (
    SELECT 
        Customer_ID,
        Order_Date::DATE AS Ord_Date,
        LAG(Order_Date::DATE) OVER (PARTITION BY Customer_ID ORDER BY Order_Date::DATE) AS Prev_Ord_Date
    FROM orders
)
SELECT 
    ROUND(AVG(Ord_Date - Prev_Ord_Date), 2) AS Avg_Days_Between_Orders,
    MAX(Ord_Date - Prev_Ord_Date) AS Max_Days_Between_Orders,
    MIN(Ord_Date - Prev_Ord_Date) AS Min_Days_Between_Orders
FROM Order_Dates
WHERE Prev_Ord_Date IS NOT NULL;


-- ==============================================================================
-- PART 5: ADVANCED WINDOW FUNCTIONS (10 QUERIES)
-- LAG, LEAD, RANK, DENSE_RANK, ROW_NUMBER, running sums, and rolling metrics.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 41: Cumulative Running Sales by Region
-- Business Objective: Track intra-year sales progress using running sums.
-- Logic: SUM() OVER with ORDER BY Date partitioned by Region.
-- Business Insight: Shows speed of regional sales build-up across quarters.
-- ------------------------------------------------------------------------------
SELECT 
    o.Order_ID,
    o.Order_Date,
    r.Region,
    ROUND(SUM(oi.Sales) OVER (PARTITION BY r.Region ORDER BY o.Order_Date::DATE ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)::NUMERIC, 2) AS Running_Regional_Sales
FROM orders o
JOIN order_items oi ON o.Order_ID = oi.Order_ID
JOIN regions r ON o.Region_ID = r.Region_ID
ORDER BY r.Region, o.Order_Date::DATE
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 42: Month-over-Month Sales Growth Percentage
-- Business Objective: Monitor business growth momentum.
-- Logic: LAG to fetch previous month sales, calculating percentage change.
-- Business Insight: High-priority KPI for growth monitoring.
-- ------------------------------------------------------------------------------
WITH Monthly_Totals AS (
    SELECT 
        TO_CHAR(o.Order_Date::DATE, 'YYYY-MM') AS Year_Month,
        SUM(oi.Sales) AS Month_Sales
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY TO_CHAR(o.Order_Date::DATE, 'YYYY-MM')
)
SELECT 
    Year_Month,
    ROUND(Month_Sales::NUMERIC, 2) AS Monthly_Revenue,
    ROUND(LAG(Month_Sales) OVER (ORDER BY Year_Month)::NUMERIC, 2) AS Previous_Month_Revenue,
    ROUND(((Month_Sales - LAG(Month_Sales) OVER (ORDER BY Year_Month)) / LAG(Month_Sales) OVER (ORDER BY Year_Month) * 100)::NUMERIC, 2) AS MoM_Growth_Rate_PCT
FROM Monthly_Totals
ORDER BY Year_Month;

-- ------------------------------------------------------------------------------
-- Query 43: Rolling 3-Month Sales Trend (Moving Average)
-- Business Objective: Smooth out seasonal volatility to observe structural sales trends.
-- Logic: AVG() OVER with ROWS BETWEEN 2 PRECEDING AND CURRENT ROW.
-- Business Insight: Standard metric for forecasting and tracking momentum.
-- ------------------------------------------------------------------------------
WITH Monthly_Aggs AS (
    SELECT 
        TO_CHAR(o.Order_Date::DATE, 'YYYY-MM') AS Year_Month,
        SUM(oi.Sales) AS Month_Sales
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY TO_CHAR(o.Order_Date::DATE, 'YYYY-MM')
)
SELECT 
    Year_Month,
    ROUND(Month_Sales::NUMERIC, 2) AS Current_Month_Sales,
    ROUND(AVG(Month_Sales) OVER (ORDER BY Year_Month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)::NUMERIC, 2) AS Rolling_3M_Avg_Sales
FROM Monthly_Aggs
ORDER BY Year_Month;

-- ------------------------------------------------------------------------------
-- Query 44: Rank Spenders within Each State
-- Business Objective: Find the top 3 buyers in every state for direct contact.
-- Logic: DENSE_RANK partitioned by State ordered by spend.
-- Business Insight: Essential for local field sales representatives to establish account priorities.
-- ------------------------------------------------------------------------------
WITH State_Spenders AS (
    SELECT 
        o.State,
        c.Customer_ID,
        c.Customer_Name,
        SUM(oi.Sales) AS Total_State_Spend,
        DENSE_RANK() OVER (PARTITION BY o.State ORDER BY SUM(oi.Sales) DESC) AS Spend_Rank
    FROM orders o
    JOIN customers c ON o.Customer_ID = c.Customer_ID
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY o.State, c.Customer_ID, c.Customer_Name
)
SELECT 
    State,
    Spend_Rank,
    Customer_ID,
    Customer_Name,
    ROUND(Total_State_Spend::NUMERIC, 2) AS Total_Spend
FROM State_Spenders
WHERE Spend_Rank <= 3
ORDER BY State, Spend_Rank;

-- ------------------------------------------------------------------------------
-- Query 45: Product Price Indexing inside Subcategory
-- Business Objective: Assign product value rankings within product lines.
-- Logic: ROW_NUMBER partitioned by subcategory ordered by price.
-- Business Insight: Audits product assortment pricing spreads.
-- ------------------------------------------------------------------------------
SELECT 
    Subcategory,
    ROW_NUMBER() OVER (PARTITION BY Subcategory ORDER BY Unit_Price DESC) AS Product_Index,
    Product_ID,
    Product_Name,
    Unit_Price
FROM products
ORDER BY Subcategory, Product_Index
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 46: Shipping Delay Trend lines (Rolling 7-Order Average)
-- Business Objective: Audit delivery delays to detect logistics quality drops in real time.
-- Logic: AVG(Ship_Date - Order_Date) OVER with 6 preceding rows.
-- Business Insight: Detects warehouse backlogs and shipping company bottlenecks.
-- ------------------------------------------------------------------------------
WITH Delayed_Ships AS (
    SELECT 
        Order_ID,
        Order_Date::DATE AS Ord_Date,
        Ship_Mode,
        (Ship_Date::DATE - Order_Date::DATE) AS Ship_Diff
    FROM orders
)
SELECT 
    Order_ID,
    Ord_Date,
    Ship_Mode,
    Ship_Diff AS Days_To_Ship,
    ROUND(AVG(Ship_Diff) OVER (ORDER BY Ord_Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS Rolling_7Order_Avg_Delay
FROM Delayed_Ships
ORDER BY Ord_Date
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 47: Basket Value Shift (Order-to-Order comparison)
-- Business Objective: Measure customer ticket growth over consecutive transactions.
-- Logic: LAG to calculate difference in Sales from previous order.
-- Business Insight: Determines if customer retention programs successfully grow purchase amounts.
-- ------------------------------------------------------------------------------
WITH Cust_Sequential_Sales AS (
    SELECT 
        o.Customer_ID,
        o.Order_ID,
        o.Order_Date::DATE AS Ord_Date,
        SUM(oi.Sales) AS Order_Total
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY o.Customer_ID, o.Order_ID, o.Order_Date::DATE
)
SELECT 
    Customer_ID,
    Order_ID,
    Ord_Date,
    ROUND(Order_Total::NUMERIC, 2) AS Current_Order_Total,
    ROUND(LAG(Order_Total) OVER (PARTITION BY Customer_ID ORDER BY Ord_Date)::NUMERIC, 2) AS Previous_Order_Total,
    ROUND((Order_Total - LAG(Order_Total) OVER (PARTITION BY Customer_ID ORDER BY Ord_Date))::NUMERIC, 2) AS Absolute_Ticket_Change
FROM Cust_Sequential_Sales
ORDER BY Customer_ID, Ord_Date
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Query 48: Customer Lifecycle Purchase Borders
-- Business Objective: Identify customer lifecycle boundaries (first and last item purchased).
-- Logic: FIRST_VALUE and LAST_VALUE window functions.
-- Business Insight: Tracks brand engagement over time.
-- ------------------------------------------------------------------------------
WITH Lifecycle_Items AS (
    SELECT 
        o.Customer_ID,
        p.Product_Name,
        o.Order_Date::DATE AS Ord_Date,
        ROW_NUMBER() OVER (PARTITION BY o.Customer_ID ORDER BY o.Order_Date::DATE ASC, o.Order_ID ASC) AS Row_Asc,
        ROW_NUMBER() OVER (PARTITION BY o.Customer_ID ORDER BY o.Order_Date::DATE DESC, o.Order_ID DESC) AS Row_Desc
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    JOIN products p ON oi.Product_ID = p.Product_ID
)
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    MAX(CASE WHEN li.Row_Asc = 1 THEN li.Product_Name END) AS Onboarding_Product,
    MAX(CASE WHEN li.Row_Desc = 1 THEN li.Product_Name END) AS Latest_Product
FROM customers c
JOIN Lifecycle_Items li ON c.Customer_ID = li.Customer_ID
GROUP BY c.Customer_ID, c.Customer_Name
ORDER BY c.Customer_Name
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Query 49: Outlier Sales Performance Days (Top 10% daily sales)
-- Business Objective: Mark daily sales records that are statistical outliers.
-- Logic: NTILE(10) bucket classification of daily total sales.
-- Business Insight: Detects seasonal promotions or bulk buying spikes.
-- ------------------------------------------------------------------------------
WITH Daily_Sales AS (
    SELECT 
        Order_Date::DATE AS Sales_Date,
        SUM(Sales) AS Day_Sales
    FROM orders o
    JOIN order_items oi ON o.Order_ID = oi.Order_ID
    GROUP BY Order_Date::DATE
),
Bucketed_Daily_Sales AS (
    SELECT 
        Sales_Date,
        Day_Sales,
        NTILE(10) OVER (ORDER BY Day_Sales DESC) AS Sales_Decile
    FROM Daily_Sales
)
SELECT 
    Sales_Date,
    ROUND(Day_Sales::NUMERIC, 2) AS Peak_Sales_Amount,
    CASE WHEN Sales_Decile = 1 THEN 'Peak Outlier Day (Top 10%)' ELSE 'Standard Performance Day' END AS Outlier_Label
FROM Bucketed_Daily_Sales
WHERE Sales_Decile = 1
ORDER BY Day_Sales DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 50: Subcategory Share and Running contribution inside Category
-- Business Objective: Determine subcategory shares within parent category.
-- Logic: SUM and Ratio OVER partitions.
-- Business Insight: Informs product planning by showing which subcategory drives parent category performance.
-- ------------------------------------------------------------------------------
WITH Subcat_Sales AS (
    SELECT 
        cat.Category,
        p.Subcategory,
        SUM(oi.Sales) AS Sales_Amount
    FROM order_items oi
    JOIN products p ON oi.Product_ID = p.Product_ID
    JOIN categories cat ON p.Category_ID = cat.Category_ID
    GROUP BY cat.Category, p.Subcategory
)
SELECT 
    Category,
    Subcategory,
    ROUND(Sales_Amount::NUMERIC, 2) AS Subcategory_Sales,
    ROUND((Sales_Amount / SUM(Sales_Amount) OVER (PARTITION BY Category) * 100)::NUMERIC, 2) AS Category_Share_PCT
FROM Subcat_Sales
ORDER BY Category, Subcategory_Sales DESC;
