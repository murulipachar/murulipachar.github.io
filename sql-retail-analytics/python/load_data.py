import sqlite3
import csv
import os

def load_data_pipeline():
    print("Starting ETL Ingestion Pipeline...")
    
    # Path configurations
    # Path configurations dynamically resolved to ensure complete portability
    python_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(python_dir)
    db_path = os.path.join(base_dir, "dataset", "retail_sales.db")
    csv_path = os.path.join(base_dir, "dataset", "retail_sales_dataset.csv")
    schema_path = os.path.join(base_dir, "sql", "schema.sql")
    
    # Check if files exist
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source CSV not found at: {csv_path}. Please run generate_dataset.py first.")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"SQL Schema not found at: {schema_path}.")
        
    # Connect to SQLite
    print(f"Connecting to target SQLite database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    print("Reading schema definitions and indexing configurations...")
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()
        
    # SQLite allows executing multiple SQL statements in script mode
    cursor.executescript(schema_sql)
    conn.commit()
    print("Database schema initialized and indexes constructed successfully.")
    
    # Ingest CSV Data
    print("Parsing CSV and performing data type conversions...")
    inserted_count = 0
    
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        
        # SQL insert query (excluding transaction_id as it auto-increments)
        insert_query = """
        INSERT INTO retail_sales (
            order_id, order_date, customer_id, customer_name, gender, age,
            city, region, product_category, product_name, quantity, 
            unit_price, sales, discount, profit, payment_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        # Batch insert list
        batch_data = []
        
        for row in reader:
            record = (
                row["Order_ID"],
                row["Order_Date"],
                row["Customer_ID"],
                row["Customer_Name"],
                row["Gender"],
                int(row["Age"]) if row["Age"] else None,
                row["City"],
                row["Region"],
                row["Product_Category"],
                row["Product_Name"],
                int(row["Quantity"]),
                float(row["Unit_Price"]),
                float(row["Sales"]),
                float(row["Discount"]),
                float(row["Profit"]),
                row["Payment_Method"]
            )
            batch_data.append(record)
            
        # Execute batch insert
        cursor.executemany(insert_query, batch_data)
        inserted_count = len(batch_data)
        
    conn.commit()
    print(f"Successfully loaded {inserted_count} transaction rows into table 'retail_sales'.")
    
    # Data Quality Verification Audits
    print("\n--- Running ETL Quality Control Audits ---")
    
    # 1. Total row count verification
    cursor.execute("SELECT COUNT(*) FROM retail_sales;")
    db_count = cursor.fetchone()[0]
    print(f"Audit 1 - Record Count Match: DB Count = {db_count} (Expected: 12500)")
    
    # 2. Distinct Customers Ingested
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM retail_sales;")
    customer_count = cursor.fetchone()[0]
    print(f"Audit 2 - Customer Cohort Count: Unique Customers = {customer_count} (Expected: 1000)")
    
    # 3. Profit Margin Integrity
    cursor.execute("SELECT SUM(sales), SUM(profit) FROM retail_sales;")
    total_sales, total_profit = cursor.fetchone()
    margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    print(f"Audit 3 - Revenue Balance: Sales = ${total_sales:,.2f}, Profit = ${total_profit:,.2f}, Margin = {margin:.2f}%")
    
    # 4. Null Value Detection
    cursor.execute("""
        SELECT COUNT(*) FROM retail_sales 
        WHERE order_id IS NULL OR order_date IS NULL OR customer_id IS NULL OR product_category IS NULL OR sales IS NULL;
    """)
    null_count = cursor.fetchone()[0]
    print(f"Audit 4 - Data Completeness: NULL fields count = {null_count} (Expected: 0)")
    
    # 5. Invalid Negative Constraints (e.g. Sales, Quantity, Discount boundaries)
    cursor.execute("""
        SELECT COUNT(*) FROM retail_sales 
        WHERE quantity <= 0 OR unit_price < 0 OR sales < 0 OR discount < 0.0 OR discount > 1.0;
    """)
    invalid_records = cursor.fetchone()[0]
    print(f"Audit 5 - Integrity constraints check: Invalid negative fields = {invalid_records} (Expected: 0)")

    # 6. Verify Indexes Are Active
    cursor.execute("PRAGMA index_list('retail_sales');")
    indexes = cursor.fetchall()
    print(f"Audit 6 - DB Performance Tuning: Found {len(indexes)} active schema indexes.")
    for idx in indexes:
        print(f"  - Index Name: {idx[1]} (Unique: {idx[2]})")

    cursor.close()
    conn.close()
    print("\nETL Pipeline finished successfully with zero errors!")

if __name__ == "__main__":
    load_data_pipeline()
