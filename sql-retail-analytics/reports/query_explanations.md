# Technical Developer Manual: SQL Concepts & Optimization

## 1. Advanced SQL Concepts Explained

This project showcases several advanced SQL concepts that are essential for modern data engineering and business intelligence roles. Below is a technical breakdown of how these concepts are applied in the analytical suite.

### I. Window Functions Reference

Unlike standard `GROUP BY` clauses that collapse rows into a single summary, **Window Functions** perform calculations across a set of table rows that are related to the current row, preserving individual row identities.

1. **`ROW_NUMBER()` (Sequential Indexing):**
   - *Behavior:* Assigns a unique, sequential integer to each row in a partition, starting at 1.
   - *Use Case:* Sequentially numbers a customer's purchases by date to track shopping progression (`advanced_analysis.sql: Query 6`).
   
2. **`RANK()` (Partition Ranking with Gaps):**
   - *Behavior:* Assigns ranks based on an ordering column. If two rows tie, they receive the same rank, and the next rank skips values (e.g., 1, 2, 2, 4).
   - *Use Case:* Ranks customers by regional spending, where ties represent identical purchase volumes (`advanced_analysis.sql: Query 8`).

3. **`DENSE_RANK()` (Partition Ranking without Gaps):**
   - *Behavior:* Similar to `RANK()`, but does not skip any ranks in tie scenarios (e.g., 1, 2, 2, 3).
   - *Use Case:* Ranks high-revenue products within category lists without skipping positions (`advanced_analysis.sql: Query 1`).

4. **`LAG(column, offset)` (Historical Lookup):**
   - *Behavior:* Retrieves the value of a column from a preceding row at a specified offset.
   - *Use Case:* Compares the current month's sales to the prior month's sales to calculate **Month-over-Month (MoM) Growth Rates** (`advanced_analysis.sql: Query 4`).

5. **`LEAD(column, offset)` (Forward Lookup):**
   - *Behavior:* Retrieves the value of a column from a subsequent row at a specified offset.
   - *Use Case:* Tracks the time difference between a customer's first purchase date and their second purchase date (`advanced_analysis.sql: Query 7`).

### II. Cumulative Rollups and Rolling Averages
* **Running Total (`SUM() OVER`):** Uses `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` to calculate cumulative enterprise revenue over time.
* **Moving Average (`AVG() OVER`):** Uses `ROWS BETWEEN 29 PRECEDING AND CURRENT ROW` to compute a **30-day moving average** of sales. This smooths out seasonal fluctuations and highlights long-term trends.

---

## 2. Database Schema Performance Optimization Notes

Database performance is critical when dealing with large datasets. We have built-in realistic optimizations in our schema definitions to simulate production environments.

### I. Indexing Strategy Analysis

```sql
-- Index on Temporal Queries
CREATE INDEX idx_retail_sales_order_date ON retail_sales (order_date);
```
* **Why it's needed:** In analytics databases, filters and joins on dates are extremely frequent. Without an index on `order_date`, any query calculating monthly trends, rolling averages, or annual run-rates would require a **Full-Table Scan (O(N) complexity)**.
* **Optimization impact:** The B-Tree index allows the database to instantly locate date ranges in **O(log N) complexity**, significantly accelerating time-series queries.

```sql
-- Compound/Composite Index for Regional Department Groupings
CREATE INDEX idx_retail_sales_region_category ON retail_sales (region, product_category);
```
* **Why it's needed:** Multi-dimensional reporting frequently filters on both geography and department (e.g., `WHERE region = 'South' AND product_category = 'Furniture'`).
* **Optimization impact:** This is a **Composite Index**. The database engine uses it to locate records matching both criteria in a single index lookup, avoiding the overhead of combining separate indexes.

### II. Database Portability and Dialect Nuances

While our SQL scripts are fully tested and compatible with SQLite (offering easy local setup), we provide notes on standard differences for MySQL and PostgreSQL production environments:

1. **Date Manipulation:**
   - *SQLite:* Uses `strftime('%Y-%m', order_date)` for monthly groupings.
   - *MySQL:* Uses `DATE_FORMAT(order_date, '%Y-%m')`.
   - *PostgreSQL:* Uses `TO_CHAR(order_date, 'YYYY-MM')` or `DATE_TRUNC('month', order_date)`.
2. **Date Arithmetic:**
   - *SQLite:* Uses `julianday('2025-12-31') - julianday(last_order_date)` to calculate days between dates.
   - *MySQL:* Uses `DATEDIFF('2025-12-31', last_order_date)`.
   - *PostgreSQL:* Simply subtracts dates: `'2025-12-31'::date - last_order_date`.
3. **Auto-Increment Primary Key:**
   - *SQLite:* Uses `INTEGER PRIMARY KEY AUTOINCREMENT`.
   - *MySQL:* Uses `INT AUTO_INCREMENT PRIMARY KEY`.
   - *PostgreSQL:* Uses `SERIAL PRIMARY KEY` or `GENERATED ALWAYS AS IDENTITY`.

---

## 3. Production-Ready SQL Standards

All SQL scripts in this project are authored according to strict professional standards:
* **UPPERCASE Keywords:** All SQL keywords (`SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY`, `CTE`, `WINDOW`) are strictly capitalized for readability.
* **Indentation Alignment:** Columns and clauses are cleanly indented and aligned to make complex CTE structures readable.
* **Thorough Documentation:** Every query contains standard headers detailing the difficulty level, business objective, SQL logic, and expected strategic insight.
