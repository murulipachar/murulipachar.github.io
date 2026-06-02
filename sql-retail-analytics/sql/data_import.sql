-- ============================================================================
-- SQL RETAIL ANALYTICS - DATA IMPORT AND INGESTION GUIDE
-- ============================================================================
-- Purpose: Documentation of production-grade import commands for SQLite,
--          MySQL, and PostgreSQL databases.
-- Author: Data Analyst Portfolio Project
-- ============================================================================

-- ----------------------------------------------------------------------------
-- METHOD 1: SQLite CLI Import (Zero-Dependency Local Setup)
-- ----------------------------------------------------------------------------
-- Run these commands inside the SQLite interactive shell (`sqlite3 dataset/retail_sales.db`):

/*
-- Enable CSV mode in the SQLite CLI interpreter
.mode csv

-- Configure SQLite to treat the first line of CSV as header names
.headers on

-- Import the CSV file into a temporary staging table or directly to the target table.
-- Note: In SQLite, if the table already exists with an AUTOINCREMENT transaction_id, 
-- we import to a staging table first to avoid mapping mismatched columns.

-- 1. Create a temporary staging table without the auto-increment column
CREATE TABLE temp_retail_sales (
    order_id TEXT,
    order_date TEXT,
    customer_id TEXT,
    customer_name TEXT,
    gender TEXT,
    age INTEGER,
    city TEXT,
    region TEXT,
    product_category TEXT,
    product_name TEXT,
    quantity INTEGER,
    unit_price REAL,
    sales REAL,
    discount REAL,
    profit REAL,
    payment_method TEXT
);

-- 2. Direct ingestion from CSV into the staging table
.import dataset/retail_sales_dataset.csv temp_retail_sales

-- 3. Insert and cast records from staging table into production table
INSERT INTO retail_sales (
    order_id, order_date, customer_id, customer_name, gender, age,
    city, region, product_category, product_name, quantity, 
    unit_price, sales, discount, profit, payment_method
)
SELECT 
    order_id, 
    order_date, 
    customer_id, 
    customer_name, 
    gender, 
    CAST(age AS INTEGER),
    city, 
    region, 
    product_category, 
    product_name, 
    CAST(quantity AS INTEGER), 
    CAST(unit_price AS REAL), 
    CAST(sales AS REAL), 
    CAST(discount AS REAL), 
    CAST(profit AS REAL), 
    payment_method
FROM temp_retail_sales
WHERE order_id != 'Order_ID'; -- Skip header line if imported as data row

-- 4. Clean up staging table
DROP TABLE temp_retail_sales;
*/

-- ----------------------------------------------------------------------------
-- METHOD 2: MySQL CLI Load (Production Corporate Server Setup)
-- ----------------------------------------------------------------------------
-- Ensure that your MySQL server has `local_infile` enabled. Run within MySQL CLI:

/*
SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE '/path/to/retail_sales_dataset.csv'
INTO TABLE retail_sales
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    order_id, 
    @order_date, -- Use variable to clean date format if necessary
    customer_id, 
    customer_name, 
    gender, 
    age,
    city, 
    region, 
    product_category, 
    product_name, 
    quantity, 
    unit_price, 
    sales, 
    discount, 
    profit, 
    payment_method
)
SET order_date = STR_TO_DATE(@order_date, '%Y-%m-%d');
*/

-- ----------------------------------------------------------------------------
-- METHOD 3: PostgreSQL COPY (High-Performance Enterprise Setup)
-- ----------------------------------------------------------------------------
-- Run as superuser inside psql terminal or via python client:

/*
COPY retail_sales(
    order_id, order_date, customer_id, customer_name, gender, age,
    city, region, product_category, product_name, quantity, 
    unit_price, sales, discount, profit, payment_method
)
FROM '/path/to/retail_sales_dataset.csv'
DELIMITER ','
CSV HEADER;
*/
