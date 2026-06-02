-- ============================================================================
-- SQL RETAIL ANALYTICS - RELATIONAL DATABASE SCHEMA
-- ============================================================================
-- Database Flavor: SQLite / MySQL / PostgreSQL Compatible
-- Purpose: Schema definition with strict constraints and performance indexes.
-- Author: Data Analyst Portfolio Project
-- ============================================================================

-- Drop table if it exists to ensure clean slate
DROP TABLE IF EXISTS retail_sales;

-- Create main analytical table
CREATE TABLE retail_sales (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    customer_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    gender TEXT,
    age INTEGER CHECK (age >= 0 AND age <= 120),
    city TEXT NOT NULL,
    region TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    sales REAL NOT NULL CHECK (sales >= 0),
    discount REAL NOT NULL CHECK (discount >= 0.0 AND discount <= 1.0),
    profit REAL NOT NULL,
    payment_method TEXT NOT NULL,
    
    -- Data Quality Check Constraint with float tolerance
    CONSTRAINT check_sales_calculation CHECK (ABS(sales - (quantity * unit_price * (1.0 - discount))) < 0.05)
);

-- ============================================================================
-- INDEX OPTIMIZATION LAYER
-- ============================================================================
-- Performance indexes are critical to optimize complex analytical queries, 
-- including window functions, cumulative aggregations, and cohort analyses.

-- 1. Index for Temporal queries (rolling averages, MoM, YoY, monthly aggregations)
CREATE INDEX idx_retail_sales_order_date 
ON retail_sales (order_date);

-- 2. Index for Customer-centric analyses (retention, repeat cohorts, segmentations)
CREATE INDEX idx_retail_sales_customer_id 
ON retail_sales (customer_id);

-- 3. Index for Category and Product grouping metrics
CREATE INDEX idx_retail_sales_product_category 
ON retail_sales (product_category);

-- 4. Composite Index for regional product performance metrics (highly realistic optimizer search)
CREATE INDEX idx_retail_sales_region_category 
ON retail_sales (region, product_category);

-- 5. Index for customer segmentation profiling queries
CREATE INDEX idx_retail_sales_customer_segment 
ON retail_sales (customer_id, sales, profit);
