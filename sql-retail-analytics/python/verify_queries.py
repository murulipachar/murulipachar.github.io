import sqlite3
import os
import re

def execute_sql_file(db_path, file_path):
    print(f"\n==================================================")
    print(f"VERIFYING FILE: {os.path.basename(file_path)}")
    print(f"==================================================")
    
    conn = sqlite3.connect(db_path)
    # Enable standard row factory to fetch dict-like rows for easy print formatting
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split content by semicolons to isolate individual queries
    # Be careful not to split inside comments or strings (we'll filter empty parts)
    queries = content.split(";")
    
    query_index = 1
    success_count = 0
    fail_count = 0
    
    for query in queries:
        query = query.strip()
        if not query:
            continue
            
        # Extract SQL content by stripping out leading comments
        sql_lines = []
        comments = []
        for line in query.split("\n"):
            line_strip = line.strip()
            if line_strip.startswith("--") or line_strip.startswith("/*") or line_strip.endswith("*/"):
                if "QUERY" in line_strip or "DIFFICULTY" in line_strip or "BUSINESS OBJECTIVE" in line_strip:
                    comments.append(line_strip)
            else:
                sql_lines.append(line)
                
        sql_to_run = "\n".join(sql_lines).strip()
        if not sql_to_run:
            continue
            
        query_title = "Query " + str(query_index)
        for c in comments:
            if "QUERY" in c:
                query_title = c.replace("--", "").replace("/*", "").replace("*/", "").strip()
                
        print(f"\nRunning {query_title}...")
        try:
            cursor.execute(sql_to_run)
            results = cursor.fetchall()
            
            # Print a neat small table preview of results
            if results:
                cols = results[0].keys()
                # Print column headers
                header_str = " | ".join(cols)
                print(header_str)
                print("-" * len(header_str))
                # Print first 3 rows
                for r in results[:4]:
                    row_str = " | ".join(str(r[c]) if r[c] is not None else "NULL" for c in cols)
                    print(row_str)
                if len(results) > 4:
                    print(f"... ({len(results) - 4} more rows)")
            else:
                print("Query executed successfully: returned 0 rows.")
                
            success_count += 1
        except Exception as e:
            print(f"[ERROR] in {query_title}:")
            print(f"Query text:\n{sql_to_run}")
            print(f"Exception message: {e}")
            fail_count += 1
            
        query_index += 1
        
    cursor.close()
    conn.close()
    
    print(f"\n--- In-File Summary: {success_count} Passed, {fail_count} Failed ---")
    return success_count, fail_count

def run_full_validation_suite():
    # Path configurations dynamically resolved to ensure complete portability
    python_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(python_dir)
    db_path = os.path.join(base_dir, "dataset", "retail_sales.db")
    sql_dir = os.path.join(base_dir, "sql")
    
    sql_files = [
        os.path.join(sql_dir, "basic_analysis.sql"),
        os.path.join(sql_dir, "intermediate_analysis.sql"),
        os.path.join(sql_dir, "advanced_analysis.sql"),
        os.path.join(sql_dir, "business_questions.sql"),
        os.path.join(sql_dir, "kpi_queries.sql")
    ]
    
    total_passed = 0
    total_failed = 0
    
    for f_path in sql_files:
        if os.path.exists(f_path):
            passed, failed = execute_sql_file(db_path, f_path)
            total_passed += passed
            total_failed += failed
        else:
            print(f"File not found: {f_path}")
            
    print(f"\n==================================================")
    print(f"GLOBAL SQL VALIDATION: {total_passed} PASSED, {total_failed} FAILED")
    print(f"==================================================")
    
    if total_failed > 0:
        print("[ERROR] Validation failed with errors! See details above.")
        exit(1)
    else:
        print("[SUCCESS] Success! All SQL queries passed syntax validation against SQLite database!")

if __name__ == "__main__":
    run_full_validation_suite()
