# -*- coding: utf-8 -*-
"""
🛒 Retail Performance & Profitability Intelligence: Interactive Live Dashboard
============================================================================
Author: Portfolio Project
License: MIT
Description: Launches a self-contained, interactive web dashboard on a local server.
             Requires ZERO external pip installations (uses Python standard libraries).
             Features dynamic query parsing, interactive SQL execution, KPI trackers,
             custom query terminal, report browser, and ER diagram displays.
"""

import os
import sys
import json
import sqlite3
import re
import webbrowser
import threading
import time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import urllib.parse

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "dataset" / "retail_sales.db"
SQL_DIR = BASE_DIR / "sql"
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

def ensure_database():
    """Programmatically runs generate_dataset and load_data if database is missing."""
    if not DB_PATH.exists():
        print("[WARN] Database not detected. Initializing database and generating retail dataset...")
        try:
            # Generate dataset
            sys.path.append(str(BASE_DIR))
            from python import generate_dataset
            generate_dataset.main() if hasattr(generate_dataset, 'main') else os.system(f'python "{BASE_DIR}/python/generate_dataset.py"')
            
            # Load database
            from python import load_data
            load_data.main() if hasattr(load_data, 'main') else os.system(f'python "{BASE_DIR}/python/load_data.py"')
            print("[OK] Database successfully generated and loaded!")
        except Exception as e:
            print(f"[ERROR] Error initializing database: {e}")
            print("Trying terminal command execution as fallback...")
            os.system(f'python "{BASE_DIR}/python/generate_dataset.py"')
            os.system(f'python "{BASE_DIR}/python/load_data.py"')

def parse_sql_file(file_path):
    """Parses a retail analytics SQL file into modular structured query blocks."""
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into queries by matching separator comment line blocks
    raw_blocks = re.split(r'-+\r?\n--\s*QUERY\s+\d+:', content)
    queries = []
    
    # Extract file label for categorization
    file_label = file_path.stem.replace("_", " ").title()
    
    for idx, block in enumerate(raw_blocks[1:], start=1):
        lines = block.split("\n")
        
        # Meta parsing
        title = lines[0].strip()
        difficulty = "Unknown"
        objective = []
        insight = []
        sql_lines = []
        
        in_objective = False
        in_insight = False
        
        for line in lines[1:]:
            cleaned = line.strip()
            if cleaned.startswith("-- DIFFICULTY:"):
                difficulty = cleaned.replace("-- DIFFICULTY:", "").strip()
            elif cleaned.startswith("-- BUSINESS OBJECTIVE:"):
                in_objective = True
                in_insight = False
                objective.append(cleaned.replace("-- BUSINESS OBJECTIVE:", "").strip())
            elif cleaned.startswith("-- EXPECTED INSIGHT:"):
                in_objective = False
                in_insight = True
                insight.append(cleaned.replace("-- EXPECTED INSIGHT:", "").strip())
            elif cleaned.startswith("--"):
                # Handle multi-line descriptions
                stripped_comment = re.sub(r'^--\s*', '', cleaned).strip()
                if in_objective:
                    objective.append(stripped_comment)
                elif in_insight:
                    insight.append(stripped_comment)
            else:
                # Actual SQL code
                in_objective = False
                in_insight = False
                if cleaned:
                    sql_lines.append(line)
        
        # Clean SQL content
        sql_code = "\n".join(sql_lines).strip()
        # Remove trailing semi-colons or comments if needed, but SQLite is fine with standard queries
        
        # Extract SQL for actual execution (filter out multiple queries if packed)
        # We only want the query block
        sql_exec = sql_code
        if ";" in sql_code:
            parts = sql_code.split(";")
            sql_exec = parts[0] + ";"
        
        queries.append({
            "id": f"{file_path.stem}_q{idx}",
            "index": idx,
            "title": f"Query {idx}: {title}",
            "category": file_label,
            "difficulty": difficulty,
            "objective": " ".join([o for o in objective if o]),
            "insight": " ".join([i for i in insight if i]),
            "sql": sql_code,
            "sql_exec": sql_exec
        })
        
    return queries

def get_all_queries():
    """Aggregates all queries across sql files in alphabetical order of filename."""
    sql_files = [
        SQL_DIR / "basic_analysis.sql",
        SQL_DIR / "intermediate_analysis.sql",
        SQL_DIR / "advanced_analysis.sql",
        SQL_DIR / "business_questions.sql",
        SQL_DIR / "kpi_queries.sql"
    ]
    
    all_queries = []
    for sf in sql_files:
        if sf.exists():
            all_queries.extend(parse_sql_file(sf))
    return all_queries

def execute_query(sql_str):
    """Executes a SQL query against SQLite, returning status, duration, column names, and row data."""
    if not DB_PATH.exists():
        return {"status": "error", "message": "Database file not found."}
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_time = time.perf_counter()
        cursor.execute(sql_str)
        
        # Check if it returns rows
        rows = cursor.fetchall()
        end_time = time.perf_counter()
        duration_ms = round((end_time - start_time) * 1000, 3)
        
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Convert sqlite3.Row list to native lists for JSON serialization
        data = []
        for r in rows:
            data.append(list(r))
            
        return {
            "status": "success",
            "duration_ms": duration_ms,
            "columns": columns,
            "rows": data,
            "row_count": len(data)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()

def get_live_kpis():
    """Calculates dynamically connected high-level KPI cards directly from SQLite database."""
    kpi_sql = """
    SELECT 
        ROUND(SUM(sales), 2) AS total_revenue,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers
    FROM retail_sales;
    """
    res = execute_query(kpi_sql)
    if res["status"] == "success" and res["rows"]:
        row = res["rows"][0]
        return {
            "total_revenue": row[0],
            "total_profit": row[1],
            "profit_margin": row[2],
            "total_orders": row[3],
            "total_customers": row[4]
        }
    return {
        "total_revenue": 0,
        "total_profit": 0,
        "profit_margin": 0,
        "total_orders": 0,
        "total_customers": 0
    }

# HTML Embedded Resource Dashboard SPA (Single Page Application)
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RetailBI | Interactive SQL Executive Analytics Dashboard</title>
    <!-- Modern Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Marked JS for Markdown Parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-primary: #0b0f17;
            --bg-secondary: #111827;
            --bg-tertiary: #1f2937;
            --accent-glow: #00f0ff;
            --accent-glow-subtle: rgba(0, 240, 255, 0.15);
            --accent-pink: #ff007f;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-color: rgba(255, 255, 255, 0.08);
            --card-glow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            --transition-speed: 0.25s;
        }

        .light-theme {
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f1f5f9;
            --accent-glow: #0284c7;
            --accent-glow-subtle: rgba(2, 132, 199, 0.1);
            --accent-pink: #db2777;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: rgba(0, 0, 0, 0.08);
            --card-glow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            scrollbar-width: thin;
            scrollbar-color: var(--accent-glow) var(--bg-tertiary);
        }

        /* Scrollbar styles */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--bg-tertiary);
            border-radius: 4px;
            border: 2px solid var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-glow);
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            transition: background-color var(--transition-speed), color var(--transition-speed);
        }

        /* Loading Screen */
        #loading-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #0b0f17;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.5s ease-out;
        }

        .loader-glow-ring {
            position: relative;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: linear-gradient(45deg, transparent, transparent 40%, #00f0ff);
            animation: loader-spin 1.5s linear infinite;
        }

        .loader-glow-ring::before {
            content: '';
            position: absolute;
            top: 6px;
            left: 6px;
            right: 6px;
            bottom: 6px;
            background: #0b0f17;
            border-radius: 50%;
            z-index: 1000;
        }

        .loader-glow-ring::after {
            content: '';
            position: absolute;
            top: 0px;
            left: 0px;
            right: 0px;
            bottom: 0px;
            background: linear-gradient(45deg, transparent, transparent 40%, #00f0ff);
            border-radius: 50%;
            z-index: 1;
            filter: blur(20px);
        }

        @keyframes loader-spin {
            0% { transform: rotate(0deg); filter: hue-rotate(0deg); }
            100% { transform: rotate(360deg); filter: hue-rotate(360deg); }
        }

        .loading-text {
            color: #f3f4f6;
            margin-top: 30px;
            font-size: 1.25rem;
            letter-spacing: 2px;
            font-weight: 500;
            text-transform: uppercase;
            animation: text-pulse 1.5s ease-in-out infinite;
        }

        @keyframes text-pulse {
            0%, 100% { opacity: 0.4; text-shadow: 0 0 2px transparent; }
            50% { opacity: 1; text-shadow: 0 0 10px #00f0ff; }
        }

        /* Top Header Navigation */
        header {
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--card-glow);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }

        .header-logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            background: linear-gradient(135deg, var(--accent-glow), var(--accent-pink));
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            box-shadow: 0 0 15px var(--accent-glow-subtle);
        }

        .header-title h1 {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: linear-gradient(90deg, var(--text-main), var(--accent-glow));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-title p {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .header-controls {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .theme-toggle, .refresh-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            width: 38px;
            height: 38px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            transition: all 0.2s ease;
        }

        .theme-toggle:hover, .refresh-btn:hover {
            border-color: var(--accent-glow);
            box-shadow: 0 0 10px var(--accent-glow-subtle);
            color: var(--accent-glow);
        }

        .refresh-indicator {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-align: right;
        }

        .refresh-indicator span {
            color: var(--accent-glow);
            font-weight: 600;
        }

        /* Layout Grid */
        .app-container {
            display: flex;
            flex: 1;
            height: calc(100vh - 71px);
            overflow: hidden;
        }

        /* Sidebar UX */
        .sidebar {
            width: 320px;
            background-color: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            flex-shrink: 0;
            transition: all 0.3s ease;
        }

        .sidebar-section {
            border-bottom: 1px solid var(--border-color);
        }

        .section-header {
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            background: rgba(255, 255, 255, 0.01);
            transition: background 0.2s;
        }

        .section-header:hover {
            background: rgba(255, 255, 255, 0.03);
        }

        .section-header h3 {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-header h3 i {
            color: var(--accent-glow);
        }

        .section-header .chevron {
            font-size: 0.75rem;
            color: var(--text-muted);
            transition: transform 0.3s ease;
        }

        .section-content {
            max-height: 500px;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }

        .section-content.collapsed {
            max-height: 0;
        }

        .query-list {
            list-style: none;
            padding: 8px 12px;
        }

        .query-item {
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            margin-bottom: 4px;
            color: var(--text-muted);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            border: 1px solid transparent;
        }

        .query-item:hover {
            background: var(--bg-tertiary);
            color: var(--text-main);
            border-color: rgba(0, 240, 255, 0.1);
            box-shadow: inset 0 0 8px rgba(0, 240, 255, 0.03);
        }

        .query-item.active {
            background: var(--accent-glow-subtle);
            color: var(--accent-glow);
            border-color: var(--accent-glow);
            font-weight: 600;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.1);
        }

        .difficulty-badge {
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 10px;
            text-transform: uppercase;
            font-weight: 800;
            letter-spacing: 0.5px;
            flex-shrink: 0;
        }

        .diff-beginner {
            background-color: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .diff-intermediate {
            background-color: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .diff-advanced {
            background-color: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* Navigation menu for extra layers */
        .sidebar-menu {
            padding: 15px 12px;
            border-top: 1px solid var(--border-color);
            margin-top: auto;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-main);
            text-decoration: none;
            cursor: pointer;
            margin-bottom: 6px;
            transition: all 0.2s ease;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
        }

        .menu-item:hover {
            border-color: var(--accent-glow);
            box-shadow: 0 0 10px var(--accent-glow-subtle);
            color: var(--accent-glow);
        }

        .menu-item.active {
            background: linear-gradient(135deg, var(--accent-glow), var(--accent-glow));
            color: #0b0f17;
            border-color: var(--accent-glow);
            box-shadow: 0 0 15px var(--accent-glow-subtle);
        }

        /* Main Workspace View */
        .main-content {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        /* Executive KPI Section */
        .kpi-section {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
        }

        .kpi-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 12px;
            box-shadow: var(--card-glow);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: transform 0.2s, border-color 0.2s;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent-glow);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-glow);
        }

        .kpi-card:nth-child(2)::before { background: var(--accent-pink); }
        .kpi-card:nth-child(3)::before { background: #10b981; }
        .kpi-card:nth-child(4)::before { background: #f59e0b; }
        .kpi-card:nth-child(5)::before { background: #8b5cf6; }

        .kpi-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .kpi-label i {
            font-size: 0.9rem;
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.5px;
        }

        .kpi-subtext {
            font-size: 0.7rem;
            color: var(--text-muted);
        }

        .kpi-subtext span {
            font-weight: 600;
        }

        /* Content panels switcher */
        .workspace-panel {
            display: none;
            flex-direction: column;
            gap: 25px;
            animation: fade-in 0.3s ease-in-out;
        }

        .workspace-panel.active {
            display: flex;
        }

        @keyframes fade-in {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Card panels */
        .glass-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: var(--card-glow);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .card-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .card-title i {
            color: var(--accent-glow);
            font-size: 1.2rem;
        }

        .card-title h2 {
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .card-header-actions {
            display: flex;
            gap: 10px;
        }

        .btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }

        .btn:hover {
            border-color: var(--accent-glow);
            color: var(--accent-glow);
            box-shadow: 0 0 10px var(--accent-glow-subtle);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-glow), #00b8ff);
            color: #0b0f17;
            border: none;
            box-shadow: 0 4px 15px rgba(0, 240, 255, 0.2);
        }

        .btn-primary:hover {
            background: linear-gradient(135deg, #00b8ff, var(--accent-glow));
            color: #0b0f17;
            box-shadow: 0 4px 20px rgba(0, 240, 255, 0.4);
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--accent-glow);
            color: var(--accent-glow);
        }

        .btn-secondary:hover {
            background: var(--accent-glow-subtle);
        }

        /* SQL Details Dashboard */
        .meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px 24px;
            background: rgba(255, 255, 255, 0.01);
            border-bottom: 1px solid var(--border-color);
        }

        .meta-block {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .meta-block h4 {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .meta-block h4 i {
            color: var(--accent-glow);
        }

        .meta-block p {
            font-size: 0.9rem;
            line-height: 1.45;
            color: var(--text-main);
        }

        /* SQL Editor View */
        .sql-editor-container {
            position: relative;
            border-bottom: 1px solid var(--border-color);
        }

        .sql-code-box {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            background-color: #0d1117;
            color: #c9d1d9;
            padding: 24px;
            min-height: 100px;
            max-height: 350px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-all;
            outline: none;
            line-height: 1.6;
        }

        /* Custom SQL Console */
        .sql-textarea {
            width: 100%;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            background-color: #0d1117;
            color: #c9d1d9;
            padding: 24px;
            min-height: 200px;
            border: none;
            outline: none;
            resize: vertical;
            line-height: 1.6;
        }

        /* Execution Results Panel */
        .results-info-bar {
            padding: 12px 24px;
            background-color: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .results-info-bar span i {
            color: var(--accent-glow);
            margin-right: 4px;
        }

        .table-responsive-container {
            max-height: 500px;
            overflow: auto;
            position: relative;
        }

        /* Beautiful Data Table */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            text-align: left;
        }

        .data-table th {
            position: sticky;
            top: 0;
            background-color: var(--bg-secondary);
            color: var(--text-main);
            font-weight: 700;
            padding: 12px 18px;
            border-bottom: 2px solid var(--border-color);
            box-shadow: inset 0 -1px 0 var(--border-color);
            white-space: nowrap;
            user-select: none;
            cursor: pointer;
        }

        .data-table th:hover {
            color: var(--accent-glow);
        }

        .data-table th i {
            margin-left: 5px;
            font-size: 0.75rem;
        }

        .data-table td {
            padding: 10px 18px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
            white-space: nowrap;
        }

        .data-table tr:hover td {
            background-color: var(--accent-glow-subtle);
        }

        /* Empty State */
        .empty-state {
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 15px;
            color: var(--text-muted);
            text-align: center;
        }

        .empty-state i {
            font-size: 3rem;
            color: var(--accent-glow);
            opacity: 0.6;
            animation: float-pulse 3s infinite ease-in-out;
        }

        @keyframes float-pulse {
            0%, 100% { transform: translateY(0); opacity: 0.5; }
            50% { transform: translateY(-8px); opacity: 0.9; text-shadow: 0 0 15px var(--accent-glow); }
        }

        .empty-state h3 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-main);
        }

        .empty-state p {
            max-width: 400px;
            font-size: 0.85rem;
        }

        /* Markdown Reports View */
        .report-layout {
            display: grid;
            grid-template-columns: 240px 1fr;
            gap: 30px;
        }

        .report-nav-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 15px;
            height: fit-content;
            box-shadow: var(--card-glow);
        }

        .report-nav-title {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 10px;
        }

        .report-link {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 4px;
        }

        .report-link:hover, .report-link.active {
            background-color: var(--bg-tertiary);
            color: var(--accent-glow);
        }

        .report-body-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: var(--card-glow);
            padding: 40px;
            min-height: 500px;
        }

        /* Markdown Styles Inside Card */
        .markdown-content {
            font-size: 1rem;
            line-height: 1.7;
            color: var(--text-main);
        }

        .markdown-content h1 {
            font-size: 1.75rem;
            font-weight: 800;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            color: var(--accent-glow);
        }

        .markdown-content h2 {
            font-size: 1.35rem;
            font-weight: 700;
            margin-top: 30px;
            margin-bottom: 15px;
            color: var(--text-main);
        }

        .markdown-content h3 {
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        .markdown-content p {
            margin-bottom: 15px;
        }

        .markdown-content ul, .markdown-content ol {
            margin-left: 24px;
            margin-bottom: 15px;
        }

        .markdown-content li {
            margin-bottom: 6px;
        }

        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9rem;
        }

        .markdown-content table th, .markdown-content table td {
            padding: 10px 15px;
            border: 1px solid var(--border-color);
        }

        .markdown-content table th {
            background-color: var(--bg-tertiary);
            font-weight: 700;
        }

        .markdown-content table tr:hover td {
            background-color: rgba(255, 255, 255, 0.02);
        }

        .markdown-content blockquote {
            border-left: 4px solid var(--accent-glow);
            background-color: var(--bg-tertiary);
            padding: 15px 20px;
            margin: 20px 0;
            font-style: italic;
            border-radius: 0 8px 8px 0;
        }

        /* Screenshots / Heatmaps Board */
        .gallery-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }

        .gallery-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--card-glow);
            cursor: pointer;
            transition: transform 0.2s;
        }

        .gallery-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent-glow);
        }

        .gallery-img-container {
            background-color: #0b0f17;
            height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            border-bottom: 1px solid var(--border-color);
            position: relative;
        }

        .gallery-img-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }

        .gallery-card:hover .gallery-img-container img {
            transform: scale(1.05);
        }

        .gallery-card-body {
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .gallery-card-body h4 {
            font-size: 0.95rem;
            font-weight: 600;
        }

        .gallery-card-body p {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        /* Modal Image Viewer */
        .img-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(11, 15, 23, 0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            gap: 15px;
        }

        .modal-img {
            max-width: 85%;
            max-height: 80%;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: 0 0 40px rgba(0, 240, 255, 0.2);
        }

        .modal-close {
            position: absolute;
            top: 25px;
            right: 35px;
            color: white;
            font-size: 2rem;
            cursor: pointer;
            transition: color 0.2s;
        }

        .modal-close:hover {
            color: var(--accent-glow);
        }

        .modal-title {
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            text-align: center;
        }

        /* Success alerts */
        .toast-message {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #10b981;
            color: #0b0f17;
            padding: 15px 25px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
            z-index: 1001;
        }

        .toast-message.active {
            transform: translateY(0);
            opacity: 1;
        }

        /* Responsive */
        @media (max-width: 1400px) {
            .kpi-section {
                grid-template-columns: repeat(3, 1fr);
            }
        }

        @media (max-width: 1000px) {
            .app-container {
                flex-direction: column;
                height: auto;
                overflow: visible;
            }
            .sidebar {
                width: 100%;
                height: auto;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            .main-content {
                padding: 15px;
            }
            .kpi-section {
                grid-template-columns: 1fr 1fr;
            }
            .gallery-grid {
                grid-template-columns: 1fr;
            }
            .report-layout {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <!-- Loading Screen -->
    <div id="loading-screen">
        <div class="loader-glow-ring"></div>
        <div class="loading-text">Initializing RetailBI Dashboard...</div>
    </div>

    <!-- Header -->
    <header>
        <div class="header-logo">
            <div class="logo-icon">
                <i class="fa-solid fa-chart-line"></i>
            </div>
            <div class="header-title">
                <h1>RetailBI Analytics</h1>
                <p>Business Intelligence Executive Analytics Dashboard</p>
            </div>
        </div>
        
        <div class="header-controls">
            <div class="refresh-indicator">
                Last Refreshed:<br><span id="refresh-time">-</span>
            </div>
            <button class="refresh-btn" onclick="refreshKPIS()" title="Refresh KPI Metrics">
                <i class="fa-solid fa-arrows-rotate"></i>
            </button>
            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                <i class="fa-solid fa-moon" id="theme-icon"></i>
            </button>
        </div>
    </header>

    <div class="app-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="section-header" onclick="toggleSidebarSection(this)">
                    <h3><i class="fa-solid fa-database"></i> SQL Analysis Queries</h3>
                    <i class="fa-solid fa-chevron-down chevron"></i>
                </div>
                <div class="section-content">
                    <ul class="query-list" id="query-list-container">
                        <!-- Dynamically filled -->
                    </ul>
                </div>
            </div>

            <!-- Custom, Reports and Gallery Navigation Buttons -->
            <div class="sidebar-menu">
                <div class="menu-item" id="menu-custom-console" onclick="switchMainPanel('custom-console')">
                    <i class="fa-solid fa-terminal"></i> Custom SQL Console
                </div>
                <div class="menu-item" id="menu-reports" onclick="switchMainPanel('reports-explorer')">
                    <i class="fa-solid fa-file-invoice-dollar"></i> Reports & Insights
                </div>
                <div class="menu-item" id="menu-screenshots" onclick="switchMainPanel('screenshots-gallery')">
                    <i class="fa-solid fa-images"></i> Dashboards & Screenshots
                </div>
            </div>
        </aside>

        <!-- Workspace content -->
        <main class="main-content">
            <!-- KPIs Banner -->
            <section class="kpi-section" id="kpi-banner">
                <div class="kpi-card">
                    <div class="kpi-label">Gross Revenue <i class="fa-solid fa-money-bill-trend-up"></i></div>
                    <div class="kpi-value" id="kpi-revenue">$0</div>
                    <div class="kpi-subtext">Cumulative sales (3-yr baseline)</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Net Profit <i class="fa-solid fa-sack-dollar"></i></div>
                    <div class="kpi-value" id="kpi-profit">$0</div>
                    <div class="kpi-subtext">Calculated bottom-line return</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Net Profit Margin <i class="fa-solid fa-percent"></i></div>
                    <div class="kpi-value" id="kpi-margin">0%</div>
                    <div class="kpi-subtext">Return conversion index</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Total Volume <i class="fa-solid fa-dolly"></i></div>
                    <div class="kpi-value" id="kpi-orders">0</div>
                    <div class="kpi-subtext">Unique transaction order IDs</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Unique Customers <i class="fa-solid fa-users"></i></div>
                    <div class="kpi-value" id="kpi-customers">0</div>
                    <div class="kpi-subtext">Total active buyer cohorts</div>
                </div>
            </section>

            <!-- PANEL 1: Dynamic Query Viewer -->
            <section class="workspace-panel active" id="panel-query-viewer">
                <div class="glass-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-code"></i>
                            <h2 id="active-query-title">Select a query from the sidebar to inspect and run</h2>
                        </div>
                        <div class="card-header-actions">
                            <span class="difficulty-badge" id="active-query-diff-badge" style="display:none;">Beginner</span>
                        </div>
                    </div>

                    <!-- Meta Details -->
                    <div class="meta-grid" id="active-query-meta-grid" style="display:none;">
                        <div class="meta-block">
                            <h4><i class="fa-solid fa-crosshairs"></i> Business Objective</h4>
                            <p id="active-query-objective">To identify strategic levers of revenue growth.</p>
                        </div>
                        <div class="meta-block">
                            <h4><i class="fa-solid fa-lightbulb"></i> Strategic Insight Target</h4>
                            <p id="active-query-insight">Establish transactional averages.</p>
                        </div>
                    </div>

                    <!-- SQL Code Output Box -->
                    <div class="sql-editor-container">
                        <div class="sql-code-box" id="active-query-code-block">
                            -- SQL statement will render here
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="card-header" style="border-top: 1px solid var(--border-color); border-bottom: none; background: rgba(0, 0, 0, 0.05)">
                        <div>
                            <span style="font-size: 0.8rem; color: var(--text-muted)">Dataset: <strong style="color: var(--text-main)">Sample Superstore Dataset</strong></span>
                        </div>
                        <div style="display:flex; gap:10px;">
                            <button class="btn btn-secondary" onclick="copyActiveSQL()" id="copy-sql-btn">
                                <i class="fa-regular fa-copy"></i> Copy SQL
                            </button>
                            <button class="btn btn-primary" onclick="runActiveQuery()">
                                <i class="fa-solid fa-play"></i> Execute Query
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Execution Results Card -->
                <div class="glass-card" id="results-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-table"></i>
                            <h2>SQL Output Log</h2>
                        </div>
                        <div class="card-header-actions">
                            <button class="btn" onclick="exportResultsCSV()" id="export-csv-btn" style="display:none;">
                                <i class="fa-solid fa-file-csv"></i> Export CSV
                            </button>
                            <button class="btn" onclick="printDashboardResults()" title="Print table outputs">
                                <i class="fa-solid fa-print"></i> Print
                            </button>
                        </div>
                    </div>
                    
                    <div class="results-info-bar" id="results-info-bar" style="display:none;">
                        <span><i class="fa-regular fa-clock"></i> Query Execution Time: <strong id="exec-duration">0.0 ms</strong></span>
                        <span><i class="fa-solid fa-list-numeric"></i> Records Returned: <strong id="exec-row-count">0</strong></span>
                    </div>

                    <div class="table-responsive-container" id="results-table-container">
                        <div class="empty-state">
                            <i class="fa-solid fa-server"></i>
                            <h3>Database Ready</h3>
                            <p>Select a SQL analysis query from the sidebar or type a custom command, then click "Execute Query" to trace real-time retail intelligence logs.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- PANEL 2: Custom SQL Console -->
            <section class="workspace-panel" id="panel-custom-console">
                <div class="glass-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-terminal"></i>
                            <h2>Custom Interactive SQL Sandbox</h2>
                        </div>
                        <div>
                            <span style="font-size: 0.8rem; color: var(--text-muted)">Querying table: <strong style="color: var(--text-main)">retail_sales</strong></span>
                        </div>
                    </div>

                    <div class="sql-editor-container">
                        <textarea class="sql-textarea" id="custom-sql-textarea" placeholder="-- Write your custom SQLite statement here...\n-- Example:\nSELECT product_category, SUM(sales) AS revenue \nFROM retail_sales \nGROUP BY product_category \nORDER BY revenue DESC;"></textarea>
                    </div>

                    <div class="card-header" style="border-top: 1px solid var(--border-color); border-bottom: none; background: rgba(0, 0, 0, 0.05)">
                        <div>
                            <span style="font-size: 0.75rem; color: var(--accent-pink)"><i class="fa-solid fa-circle-exclamation"></i> Only read-only operations (SELECT, etc.) are suggested.</span>
                        </div>
                        <div style="display:flex; gap:10px;">
                            <button class="btn btn-secondary" onclick="clearConsole()">
                                <i class="fa-solid fa-trash-can"></i> Clear
                            </button>
                            <button class="btn btn-primary" onclick="runCustomQuery()">
                                <i class="fa-solid fa-play"></i> Execute SQL
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Outputs rendered inside same query outputs structure -->
                <div class="glass-card" id="custom-results-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-table"></i>
                            <h2>Sandbox Results Log</h2>
                        </div>
                        <div class="card-header-actions">
                            <button class="btn" onclick="exportSandboxCSV()" id="sandbox-export-csv-btn" style="display:none;">
                                <i class="fa-solid fa-file-csv"></i> Export CSV
                            </button>
                        </div>
                    </div>
                    
                    <div class="results-info-bar" id="sandbox-results-info-bar" style="display:none;">
                        <span><i class="fa-regular fa-clock"></i> SQLite clock duration: <strong id="sandbox-exec-duration">0.0 ms</strong></span>
                        <span><i class="fa-solid fa-list-numeric"></i> Rows affected/returned: <strong id="sandbox-exec-row-count">0</strong></span>
                    </div>

                    <div class="table-responsive-container" id="sandbox-table-container">
                        <div class="empty-state">
                            <i class="fa-solid fa-keyboard"></i>
                            <h3>Sandbox Terminal Awaiting Input</h3>
                            <p>Write an ANSI-SQL query on the database and hit Execute. Returns structured tabular records.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- PANEL 3: Reports Explorer -->
            <section class="workspace-panel" id="panel-reports-explorer">
                <div class="report-layout">
                    <div class="report-nav-card">
                        <div class="report-nav-title">Select Report Document</div>
                        <div class="report-link active" onclick="loadReport('business_insights.md', this)">
                            <i class="fa-solid fa-chart-line"></i> Business Insights
                        </div>
                        <div class="report-link" onclick="loadReport('sql_case_study.md', this)">
                            <i class="fa-solid fa-file-code"></i> SQL Case Study
                        </div>
                        <div class="report-link" onclick="loadReport('query_explanations.md', this)">
                            <i class="fa-solid fa-book-open"></i> Query Explanations
                        </div>
                    </div>

                    <div class="report-body-card">
                        <div class="markdown-content" id="report-rendered-markdown">
                            <!-- Dynamically loaded markdown -->
                        </div>
                    </div>
                </div>
            </section>

            <!-- PANEL 4: Screenshots Gallery -->
            <section class="workspace-panel" id="panel-screenshots-gallery">
                <div class="gallery-grid">
                    <div class="gallery-card" onclick="openImageModal('retail_analytics_er_diagram.png', 'Star-Schema ER Database Schema Visualization')">
                        <div class="gallery-img-container">
                            <img src="/api/image/retail_analytics_er_diagram.png" alt="Star-Schema ER Diagram">
                        </div>
                        <div class="gallery-card-body">
                            <div>
                                <h4>Star-Schema ER Diagram</h4>
                                <p>Dimension-to-Fact connection map</p>
                            </div>
                            <i class="fa-solid fa-expand" style="color: var(--accent-glow)"></i>
                        </div>
                    </div>

                    <div class="gallery-card" onclick="openImageModal('etl_terminal_execution.png', 'Terminal ETL Pipeline execution output log')">
                        <div class="gallery-img-container">
                            <img src="/api/image/etl_terminal_execution.png" alt="Terminal ETL Ingestion">
                        </div>
                        <div class="gallery-card-body">
                            <div>
                                <h4>Terminal ETL Ingestion Log</h4>
                                <p>Automated database ingestion and audits</p>
                            </div>
                            <i class="fa-solid fa-expand" style="color: var(--accent-glow)"></i>
                        </div>
                    </div>

                    <div class="gallery-card" onclick="openImageModal('cohort_retention_heatmap.png', 'Customer Inception Cohort Q-o-Q retention Heatmap Grid')">
                        <div class="gallery-img-container">
                            <img src="/api/image/cohort_retention_heatmap.png" alt="Cohort Retention heatmap grid">
                        </div>
                        <div class="gallery-card-body">
                            <div>
                                <h4>Cohort Retention Heatmap</h4>
                                <p>Quarterly cohort stickiness dashboard mock</p>
                            </div>
                            <i class="fa-solid fa-expand" style="color: var(--accent-glow)"></i>
                        </div>
                    </div>

                    <div class="gallery-card" onclick="openImageModal('kpi_dashboard_summary.png', 'Executive KPI Revenue Growth and margins Dashboard')">
                        <div class="gallery-img-container">
                            <img src="/api/image/kpi_dashboard_summary.png" alt="BI Executive Dashboard">
                        </div>
                        <div class="gallery-card-body">
                            <div>
                                <h4>Executive KPI BI Dashboard Summary</h4>
                                <p>Sales growth curves and margins visual overview</p>
                            </div>
                            <i class="fa-solid fa-expand" style="color: var(--accent-glow)"></i>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <!-- Image Modal Viewer -->
    <div class="img-modal" id="image-modal-viewer" onclick="closeImageModal()">
        <span class="modal-close"><i class="fa-solid fa-circle-xmark"></i></span>
        <img class="modal-img" id="modal-image-source" src="" alt="Fullscreen visualization view">
        <div class="modal-title" id="modal-image-title">Dashboard Visual</div>
    </div>

    <!-- Toast Success Notification -->
    <div class="toast-message" id="toast-message-box">
        <i class="fa-solid fa-circle-check"></i>
        <span id="toast-text-content">Executed successfully!</span>
    </div>

    <script>
        // Global State variables
        let queriesData = [];
        let activeQuery = null;
        let activeResults = null;
        let sandboxResults = null;

        // Initialize Page
        window.addEventListener('DOMContentLoaded', async () => {
            await fetchKPIs();
            await fetchQueries();
            
            // Hide Loader
            setTimeout(() => {
                const loader = document.getElementById('loading-screen');
                loader.style.opacity = '0';
                setTimeout(() => loader.style.display = 'none', 500);
            }, 800);

            // Set dynamic date in header
            document.getElementById('refresh-time').innerText = new Date().toLocaleTimeString();

            // Open the first query by default
            if (queriesData.length > 0) {
                selectQuery(queriesData[0].id);
            }
            
            // Load default report
            loadReport('business_insights.md');
        });

        // Theme Toggle
        function toggleTheme() {
            const body = document.body;
            const icon = document.getElementById('theme-icon');
            if (body.classList.contains('light-theme')) {
                body.classList.remove('light-theme');
                icon.className = 'fa-solid fa-moon';
            } else {
                body.classList.add('light-theme');
                icon.className = 'fa-solid fa-sun';
            }
            showToast("Theme switched successfully!");
        }

        // Collapse/Expand Sidebar Sections
        function toggleSidebarSection(header) {
            const content = header.nextElementSibling;
            const chevron = header.querySelector('.chevron');
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                chevron.style.transform = 'rotate(0deg)';
            } else {
                content.classList.add('collapsed');
                chevron.style.transform = 'rotate(-90deg)';
            }
        }

        // Switch Workspace panels (Queries, Sandbox, Reports, Images)
        function switchMainPanel(panelId) {
            // Remove active classes
            document.querySelectorAll('.workspace-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            
            if (panelId === 'query-viewer') {
                document.getElementById('panel-query-viewer').classList.add('active');
            } else if (panelId === 'custom-console') {
                document.getElementById('panel-custom-console').classList.add('active');
                document.getElementById('menu-custom-console').classList.add('active');
            } else if (panelId === 'reports-explorer') {
                document.getElementById('panel-reports-explorer').classList.add('active');
                document.getElementById('menu-reports').classList.add('active');
            } else if (panelId === 'screenshots-gallery') {
                document.getElementById('panel-screenshots-gallery').classList.add('active');
                document.getElementById('menu-screenshots').classList.add('active');
            }
        }

        // Fetch KPI numbers
        async function fetchKPIs() {
            try {
                const response = await fetch('/api/kpis');
                const kpis = await response.json();
                
                // Animate Numbers
                animateNumber('kpi-revenue', kpis.total_revenue, true);
                animateNumber('kpi-profit', kpis.total_profit, true);
                document.getElementById('kpi-margin').innerText = kpis.profit_margin.toFixed(2) + '%';
                animateNumber('kpi-orders', kpis.total_orders, false);
                animateNumber('kpi-customers', kpis.total_customers, false);
            } catch (err) {
                console.error("Error fetching KPIs:", err);
            }
        }

        // Refresh KPIs manual handler
        async function refreshKPIS() {
            document.getElementById('refresh-time').innerText = new Date().toLocaleTimeString();
            await fetchKPIs();
            showToast("Executive KPI parameters refreshed!");
        }

        // Number Increment Animation
        function animateNumber(id, endValue, isCurrency) {
            const el = document.getElementById(id);
            let start = 0;
            const duration = 800; // ms
            const steps = 30;
            const increment = endValue / steps;
            let currentStep = 0;
            
            const timer = setInterval(() => {
                currentStep++;
                start += increment;
                if (currentStep >= steps) {
                    clearInterval(timer);
                    el.innerText = isCurrency ? formatCurrency(endValue) : Math.round(endValue).toLocaleString();
                } else {
                    el.innerText = isCurrency ? formatCurrency(start) : Math.round(start).toLocaleString();
                }
            }, duration / steps);
        }

        function formatCurrency(val) {
            return '$' + parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        // Fetch Queries from API
        async function fetchQueries() {
            try {
                const response = await fetch('/api/queries');
                queriesData = await response.json();
                
                // Group by Category inside sidebar
                renderSidebarQueries();
            } catch (err) {
                console.error("Error fetching query listings:", err);
            }
        }

        function renderSidebarQueries() {
            const container = document.getElementById('query-list-container');
            container.innerHTML = '';
            
            // Sort by category groups
            const groups = {};
            queriesData.forEach(q => {
                if (!groups[q.category]) groups[q.category] = [];
                groups[q.category].push(q);
            });

            // Flatten list with category subtitle cues in design or simple direct list with difficulty badges
            queriesData.forEach(q => {
                const li = document.createElement('li');
                li.className = 'query-item';
                li.id = `sidebar-q-${q.id}`;
                li.setAttribute('onclick', `selectQuery('${q.id}')`);
                
                let diffClass = 'diff-beginner';
                if (q.difficulty.toLowerCase().includes('intermediate')) diffClass = 'diff-intermediate';
                if (q.difficulty.toLowerCase().includes('advanced')) diffClass = 'diff-advanced';

                li.innerHTML = `
                    <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${q.index}. ${q.title.split(': ')[1]}
                    </span>
                    <span class="difficulty-badge ${diffClass}">${q.difficulty.split(' ')[0]}</span>
                `;
                container.appendChild(li);
            });
        }

        // Select active query to inspect
        function selectQuery(queryId) {
            switchMainPanel('query-viewer');
            
            // Reset active sidebar items
            document.querySelectorAll('.query-item').forEach(li => li.classList.remove('active'));
            const activeLi = document.getElementById(`sidebar-q-${queryId}`);
            if (activeLi) activeLi.classList.add('active');

            activeQuery = queriesData.find(q => q.id === queryId);
            if (!activeQuery) return;

            // Render details
            document.getElementById('active-query-title').innerText = activeQuery.title;
            
            // Meta values
            document.getElementById('active-query-objective').innerText = activeQuery.objective || "To perform operational data analysis.";
            document.getElementById('active-query-insight').innerText = activeQuery.insight || "Establish core baseline totals.";
            document.getElementById('active-query-meta-grid').style.display = 'grid';
            
            // Diff badge
            const badge = document.getElementById('active-query-diff-badge');
            badge.innerText = activeQuery.difficulty;
            badge.className = 'difficulty-badge';
            if (activeQuery.difficulty.toLowerCase().includes('beginner')) badge.classList.add('diff-beginner');
            else if (activeQuery.difficulty.toLowerCase().includes('intermediate')) badge.classList.add('diff-intermediate');
            else badge.classList.add('diff-advanced');
            badge.style.display = 'inline-block';

            // Code
            document.getElementById('active-query-code-block').innerText = activeQuery.sql;
            
            // Reset results view
            document.getElementById('results-info-bar').style.display = 'none';
            document.getElementById('export-csv-btn').style.display = 'none';
            document.getElementById('results-table-container').innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-play" style="animation: none; cursor:pointer;" onclick="runActiveQuery()"></i>
                    <h3>SQL Query Staged</h3>
                    <p>Click "Execute Query" to run this statement against the real SQLite database and inspect returned records.</p>
                </div>
            `;
        }

        // Copy SQL Code
        function copyActiveSQL() {
            if (!activeQuery) return;
            navigator.clipboard.writeText(activeQuery.sql);
            showToast("SQL script copied to clipboard!");
        }

        // Execute Active Query
        async function runActiveQuery() {
            if (!activeQuery) return;
            
            // Set Table to Loader state
            document.getElementById('results-table-container').innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    <h3>Executing SQL query...</h3>
                    <p>Running window functions and B-Tree scans against the database.</p>
                </div>
            `;

            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query_id: activeQuery.id })
                });
                
                const result = await response.json();
                renderQueryResults(result, 'results-table-container', 'results-info-bar', 'exec-duration', 'exec-row-count', 'export-csv-btn');
                activeResults = result;
            } catch (err) {
                console.error("Error executing query:", err);
                showToast("Execution crashed! See terminal log.");
            }
        }

        // Render tabular SQL data returns
        function renderQueryResults(result, containerId, infoBarId, durationId, rowCountId, csvBtnId) {
            const container = document.getElementById(containerId);
            const infoBar = document.getElementById(infoBarId);
            const csvBtn = document.getElementById(csvBtnId);

            if (result.status === 'error') {
                infoBar.style.display = 'none';
                if (csvBtn) csvBtn.style.display = 'none';
                container.innerHTML = `
                    <div class="empty-state" style="color: var(--accent-pink)">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <h3>SQL Compile Error</h3>
                        <p style="color: var(--accent-pink); font-family:'JetBrains Mono', monospace; text-align:left; background:#111; padding: 15px; border-radius: 6px; font-size:0.8rem; overflow:auto; max-width:80%; border: 1px solid rgba(239, 68, 68, 0.3)">${result.message}</p>
                    </div>
                `;
                return;
            }

            // Fill meta
            document.getElementById(durationId).innerText = result.duration_ms + ' ms';
            document.getElementById(rowCountId).innerText = result.row_count.toLocaleString();
            infoBar.style.display = 'flex';
            if (csvBtn) csvBtn.style.display = 'inline-flex';

            if (result.row_count === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-filter-circle-xmark"></i>
                        <h3>Query Returned 0 Records</h3>
                        <p>The query compiled successfully but no matching records were found in the database.</p>
                    </div>
                `;
                return;
            }

            // Build table HTML
            let html = `<table class="data-table"><thead><tr>`;
            
            // Columns headers
            result.columns.forEach(col => {
                html += `<th>${col} <i class="fa-solid fa-sort"></i></th>`;
            });
            html += `</tr></thead><tbody>`;

            // Row cells
            result.rows.forEach(row => {
                html += `<tr>`;
                row.forEach(val => {
                    // Prettify numeric cell values
                    let displayVal = val;
                    if (val === null || val === undefined) {
                        displayVal = `<span style="color: var(--accent-pink); font-style:italic">NULL</span>`;
                    } else if (typeof val === 'number') {
                        // Check if currency or integer
                        if (val.toString().includes('.') && val.toString().split('.')[1].length > 1) {
                            displayVal = val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                        } else {
                            displayVal = val.toLocaleString();
                        }
                    }
                    html += `<td>${displayVal}</td>`;
                });
                html += `</tr>`;
            });

            html += `</tbody></table>`;
            container.innerHTML = html;
            
            showToast(`Returned ${result.row_count} rows!`);
        }

        // Custom sandbox Console operations
        async function runCustomQuery() {
            const sqlText = document.getElementById('custom-sql-textarea').value.trim();
            if (!sqlText) {
                showToast("Sandbox is empty!");
                return;
            }

            // Set UI to loader
            document.getElementById('sandbox-table-container').innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    <h3>Compiling SQLite custom sandbox script...</h3>
                    <p>Executing relational database sweeps.</p>
                </div>
            `;

            try {
                const response = await fetch('/api/custom_sql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql: sqlText })
                });
                
                const result = await response.json();
                renderQueryResults(
                    result, 
                    'sandbox-table-container', 
                    'sandbox-results-info-bar', 
                    'sandbox-exec-duration', 
                    'sandbox-exec-row-count', 
                    'sandbox-export-csv-btn'
                );
                sandboxResults = result;
            } catch (err) {
                console.error("Sandbox execution crashed:", err);
                showToast("Sandbox crashed! See console log.");
            }
        }

        function clearConsole() {
            document.getElementById('custom-sql-textarea').value = '';
            document.getElementById('sandbox-results-info-bar').style.display = 'none';
            document.getElementById('sandbox-export-csv-btn').style.display = 'none';
            document.getElementById('sandbox-table-container').innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-keyboard"></i>
                    <h3>Sandbox Terminal Cleared</h3>
                    <p>Write an ANSI-SQL query on the database and hit Execute.</p>
                </div>
            `;
            showToast("Sandbox editor cleared!");
        }

        // CSV Exporter Utility
        function exportResultsCSV() {
            if (!activeResults || activeResults.row_count === 0) return;
            downloadCSV(activeResults, 'retail_bi_query_export.csv');
        }

        function exportSandboxCSV() {
            if (!sandboxResults || sandboxResults.row_count === 0) return;
            downloadCSV(sandboxResults, 'retail_bi_custom_sandbox_export.csv');
        }

        function downloadCSV(resData, filename) {
            let csvContent = "data:text/csv;charset=utf-8,";
            
            // Append header columns
            csvContent += resData.columns.join(",") + "\\n";
            
            // Append data cells
            resData.rows.forEach(row => {
                const escapedCells = row.map(cell => {
                    if (cell === null || cell === undefined) return "";
                    let cStr = cell.toString().replace(/"/g, '""');
                    if (cStr.includes(",") || cStr.includes("\\n") || cStr.includes('"')) {
                        cStr = `"${cStr}"`;
                    }
                    return cStr;
                });
                csvContent += escapedCells.join(",") + "\\n";
            });

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast("CSV file successfully downloaded!");
        }

        // Print page results table
        function printDashboardResults() {
            window.print();
        }

        // Load Markdown Reports Explorer
        async function loadReport(reportName, linkElement) {
            if (linkElement) {
                document.querySelectorAll('.report-link').forEach(l => l.classList.remove('active'));
                linkElement.classList.add('active');
            }

            const body = document.getElementById('report-rendered-markdown');
            body.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    <h3>Rendering Markdown report...</h3>
                </div>
            `;

            try {
                const response = await fetch(`/api/reports?name=${reportName}`);
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Clean report output string
                    const rawMd = data.content;
                    
                    // Parse using Marked Library
                    body.innerHTML = marked.parse(rawMd);
                } else {
                    body.innerHTML = `<div style="color:var(--accent-pink)">Error loading document: ${data.message}</div>`;
                }
            } catch (err) {
                console.error("Report renderer crash:", err);
                body.innerHTML = `<div style="color:var(--accent-pink)">Report Renderer crashed. Please inspect local files.</div>`;
            }
        }

        // Fullscreen Visual/Heatmap Viewer Modal
        function openImageModal(imgName, title) {
            const modal = document.getElementById('image-modal-viewer');
            const modalImg = document.getElementById('modal-image-source');
            const modalTitle = document.getElementById('modal-image-title');
            
            modalImg.src = `/api/image/${imgName}`;
            modalTitle.innerText = title;
            modal.style.display = 'flex';
        }

        function closeImageModal() {
            document.getElementById('image-modal-viewer').style.display = 'none';
        }

        // Helper: Toast Notifications
        function showToast(message) {
            const box = document.getElementById('toast-message-box');
            document.getElementById('toast-text-content').innerText = message;
            box.classList.add('active');
            
            setTimeout(() => {
                box.classList.remove('active');
            }, 3000);
        }
    </script>
</body>
</html>
"""

# Custom HTTP Request Handler
class RetailBIRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default terminal request logs to keep terminal display extremely clean!
        pass

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        query_params = urllib.parse.parse_qs(url_parsed.query)
        
        # 1. Main SPA Dashboard View
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
            return
            
        # 2. API Endpoints - KPI Metrics
        elif path == "/api/kpis":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            kpis = get_live_kpis()
            self.wfile.write(json.dumps(kpis).encode("utf-8"))
            return
            
        # 3. API Endpoints - SQL Queries Catalog List
        elif path == "/api/queries":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            queries = get_all_queries()
            self.wfile.write(json.dumps(queries).encode("utf-8"))
            return
            
        # 4. API Endpoints - Markdown Reports Explorer Reader
        elif path == "/api/reports":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            name = query_params.get("name", [""])[0]
            report_file = REPORTS_DIR / name
            
            # Prevent path traversal attacks via strict filename checks
            is_safe = name and not any(sep in name for sep in ("..", "/", "\\"))
            
            if is_safe and report_file.exists():
                try:
                    with open(report_file, "r", encoding="utf-8") as f:
                        text = f.read()
                    self.wfile.write(json.dumps({"status": "success", "content": text}).encode("utf-8"))
                except Exception as e:
                    self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            else:
                self.wfile.write(json.dumps({"status": "error", "message": "Report document not found."}).encode("utf-8"))
            return
            
        # 5. API Endpoints - High-Fidelity Dashboards/Screenshots PNG Servings
        elif path.startswith("/api/image/"):
            image_name = path.replace("/api/image/", "")
            target_image = SCREENSHOTS_DIR / image_name
            
            # Prevent path traversal attacks via strict filename checks
            is_safe = image_name and not any(sep in image_name for sep in ("..", "/", "\\"))
            
            # Security verification
            if is_safe and target_image.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(target_image, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return
            
        # Fallback to default
        super().do_GET()

    def do_POST(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        
        # Read body contents
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        
        # 1. API: Execute catalog query by ID
        if path == "/api/run":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            try:
                params = json.loads(post_data)
                query_id = params.get("query_id")
                
                # Fetch target query from registry
                all_queries = get_all_queries()
                target = next((q for q in all_queries if q["id"] == query_id), None)
                
                if target:
                    res = execute_query(target["sql_exec"])
                else:
                    res = {"status": "error", "message": f"Query ID {query_id} not registered."}
                
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return
            
        # 2. API: Execute custom Sandbox SQL
        elif path == "/api/custom_sql":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            try:
                params = json.loads(post_data)
                sql_str = params.get("sql", "").strip()
                
                # Security: Enforce read-only locks to protect schema integrity
                forbidden_words = ["drop", "delete", "insert", "update", "alter", "create table", "replace into"]
                is_safe = True
                for word in forbidden_words:
                    if re.search(r'\b' + word + r'\b', sql_str.lower()):
                        is_safe = False
                        break
                
                if not is_safe:
                    res = {
                        "status": "error", 
                        "message": "🔒 Sandbox Security Violation: To protect the integrity of the Sample Superstore schema, only read-only statements (e.g. SELECT, WITH, etc.) are allowed."
                    }
                else:
                    res = execute_query(sql_str)
                    
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server(port):
    """Launches the TCP Server inside standard daemon thread."""
    handler = RetailBIRequestHandler
    TCPServer.allow_reuse_address = True
    
    # Try finding an open port starting from the target
    success = False
    current_port = port
    
    while not success and current_port < port + 100:
        try:
            with TCPServer(("", current_port), handler) as httpd:
                print(f"[OK] Web Server active and listening at: http://localhost:{current_port}/")
                success = True
                
                # Auto-open browser tab
                webbrowser.open_new_tab(f"http://localhost:{current_port}/")
                
                # Serve until manual escape
                httpd.serve_forever()
        except OSError:
            current_port += 1

def main():
    print("=" * 70)
    print("RETAIL PERFORMANCE & PROFITABILITY INTELLIGENCE: PORTFOLIO DASHBOARD")
    print("=" * 70)
    
    # Ensure database is generated and initialized
    ensure_database()
    
    # Run server
    target_port = 8000
    print(f"Starting server thread on port {target_port}...")
    server_thread = threading.Thread(target=run_server, args=(target_port,), daemon=True)
    server_thread.start()
    
    # Keep main execution thread alive
    print("Press Ctrl+C to terminate the dashboard session.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDashboard server shutdown successfully. Goodbye!")

if __name__ == "__main__":
    main()
