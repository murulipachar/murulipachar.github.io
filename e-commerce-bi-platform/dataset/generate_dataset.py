import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_ecommerce_data():
    np.random.seed(42)
    print("Initializing E-Commerce Dataset Generation...")

    # 1. Generate Regions
    regions_data = [
        {"Region_ID": "REG-01", "Region": "East"},
        {"Region_ID": "REG-02", "Region": "West"},
        {"Region_ID": "REG-03", "Region": "South"},
        {"Region_ID": "REG-04", "Region": "Central"}
    ]
    df_regions = pd.DataFrame(regions_data)

    # State mapping per region
    region_states = {
        "REG-01": [("New York", "New York"), ("Massachusetts", "Boston"), ("Pennsylvania", "Philadelphia"), ("New Jersey", "Newark"), ("Ohio", "Cleveland")],
        "REG-02": [("California", "Los Angeles"), ("California", "San Francisco"), ("Washington", "Seattle"), ("Oregon", "Portland"), ("Colorado", "Denver"), ("Arizona", "Phoenix")],
        "REG-03": [("Texas", "Houston"), ("Texas", "Austin"), ("Florida", "Miami"), ("Georgia", "Atlanta"), ("North Carolina", "Charlotte"), ("Virginia", "Richmond")],
        "REG-04": [("Illinois", "Chicago"), ("Michigan", "Detroit"), ("Indiana", "Indianapolis"), ("Wisconsin", "Milwaukee"), ("Minnesota", "Minneapolis")]
    }

    # 2. Generate Categories & Subcategories
    categories_data = [
        {"Category_ID": "CAT-01", "Category": "Technology"},
        {"Category_ID": "CAT-02", "Category": "Furniture"},
        {"Category_ID": "CAT-03", "Category": "Office Supplies"}
    ]
    df_categories = pd.DataFrame(categories_data)

    subcategories_map = {
        "CAT-01": ["Phones", "Copiers", "Accessories", "Machines"],
        "CAT-02": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "CAT-03": ["Paper", "Art", "Binders", "Storage", "Envelopes"]
    }

    # 3. Generate Products (500 items)
    product_catalogue = {
        "Phones": ["iPhone 15 Pro", "Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12", "iPhone SE", "Moto G Power", "Xiaomi Redmi Note", "Nokia G310"],
        "Copiers": ["Canon ImageRUNNER", "HP LaserJet Enterprise", "Xerox Altalink Copier", "Brother Monochrome Copier", "Epson WorkForce Pro", "Ricoh IM C3000"],
        "Accessories": ["Wireless Mouse", "Mechanical Keyboard", "USB-C Hub Multiport", "Bluetooth Headphones", "External Hard Drive 2TB", "Laptop Cooling Stand", "Webcam 1080p", "USB Flash Drive 128GB"],
        "Machines": ["3D Printer Pro", "Cricut Cutting Machine", "Document Scanner HighSpeed", "Label Maker Wireless", "Heavy Duty Paper Shredder", "Cash Register Terminal"],
        "Chairs": ["Ergonomic Office Chair", "Mesh Task Chair", "Executive Leather Chair", "Gaming Chair with Support", "Drafting Stool", "Folding Chair Set 4-Pack", "Stackable Guest Chair"],
        "Tables": ["Standing Desk Electric", "Conference Room Table", "Writing Desk Wood", "Drafting Table Adjustable", "L-Shaped Corner Desk", "Folding Work Bench"],
        "Bookcases": ["5-Shelf Bookcase Wood", "Metal Frame Bookshelf", "Corner Bookshelf Unit", "Modular Storage Bookcase", "Floating Shelf Set 3-Pack"],
        "Furnishings": ["Desk Pad Leather", "LED Desk Lamp USB", "Anti-Fatigue Floor Mat", "Waste Basket Metal Mesh", "Wall Clock Modern", "Monitor Mount Arm"],
        "Paper": ["A4 Copy Paper Ream", "Colored Cardstock Pack", "Graph Paper Notebook", "Sticky Notes 3x3 Pack", "Ruled Notepad Set 5-Pack"],
        "Art": ["Dual Tip Brush Pens", "Sketchbook Spiral Bound", "Acrylic Paint Set 24-Colors", "Colored Pencils 48-Pack", "Drafting Pens Precision"],
        "Binders": ["3-Ring Binder 2-Inch", "Heavy Duty View Binder", "Sheet Protectors 100-Pack", "Index Dividers 8-Tab", "Pocket Folder Pack 10-Pack"],
        "Storage": ["Plastic Storage Totes 4-Pack", "File Drawer Storage Box", "Desktop Organizer Tiered", "Drawer Organizer Tray", "Heavy Duty Shelving Unit"],
        "Envelopes": ["Self-Seal Mailing Envelopes", "Bubble Mailers Pack 25", "Clasp Kraft Envelopes", "Catalog Envelopes Pack", "Window Business Envelopes"]
    }

    products_list = []
    prod_id_counter = 1001
    
    # Generate prices and costs
    for cat_id, subcats in subcategories_map.items():
        for subcat in subcats:
            items = product_catalogue[subcat]
            for item_name in items:
                # Base price ranges per subcategory
                if subcat in ["Phones", "Copiers", "Machines"]:
                    price = np.round(np.random.uniform(250, 1500), 2)
                    # Tech cost is ~70% of price
                    cost = np.round(price * 0.70, 2)
                elif subcat in ["Chairs", "Tables", "Bookcases"]:
                    price = np.round(np.random.uniform(80, 600), 2)
                    # Furniture cost is ~82% of price (high margin squeeze)
                    cost = np.round(price * 0.82, 2)
                else: # Office supplies
                    price = np.round(np.random.uniform(5, 120), 2)
                    # Office supplies cost is ~55% of price (good margins)
                    cost = np.round(price * 0.55, 2)
                
                products_list.append({
                    "Product_ID": f"PROD-{prod_id_counter}",
                    "Product_Name": f"{item_name} Model {np.random.choice(['X', 'Pro', 'Elite', 'Plus', 'Classic'])}",
                    "Category_ID": cat_id,
                    "Subcategory": subcat,
                    "Unit_Price": price,
                    "Unit_Cost": cost
                })
                prod_id_counter += 1
                
    # Pad to 500 products if needed
    while len(products_list) < 500:
        cat_id = np.random.choice(list(subcategories_map.keys()))
        subcat = np.random.choice(subcategories_map[cat_id])
        item_name = np.random.choice(product_catalogue[subcat])
        price = np.round(np.random.uniform(10, 800), 2)
        cost = np.round(price * np.random.uniform(0.5, 0.85), 2)
        products_list.append({
            "Product_ID": f"PROD-{prod_id_counter}",
            "Product_Name": f"{item_name} Gen-{np.random.randint(2, 6)}",
            "Category_ID": cat_id,
            "Subcategory": subcat,
            "Unit_Price": price,
            "Unit_Cost": cost
        })
        prod_id_counter += 1

    df_products = pd.DataFrame(products_list)

    # 4. Generate Customers (2,000 customers)
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "James", "Jessica", "Robert", "Karen", 
                   "William", "Lisa", "Joseph", "Sandra", "Richard", "Michelle", "Thomas", "Donna", "Charles", "Carol", 
                   "Christopher", "Amanda", "Daniel", "Dorothy", "Matthew", "Patricia", "Anthony", "Nancy", "Mark", "Betty", 
                   "Donald", "Helen", "Steven", "Paul", "Margaret", "Andrew", "Ashley", "Kenneth", "Kimberly", "Joshua"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson", 
                  "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", 
                  "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Perez", "Hall", 
                  "Young", "Allen", "Sanchez", "Wright", "King", "Scott", "Green", "Baker", "Adams", "Nelson"]
    
    customers_list = []
    start_date = datetime(2022, 1, 1)
    
    for i in range(2000):
        cust_id = f"CUST-{1001 + i}"
        name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        segment = np.random.choice(["Consumer", "Corporate", "Home Office"], p=[0.55, 0.30, 0.15])
        region_id = np.random.choice(df_regions["Region_ID"].tolist())
        state_city = np.random.choice(len(region_states[region_id]))
        state, city = region_states[region_id][state_city]
        
        # Customer join date
        join_days = np.random.randint(0, 1000)
        join_date = start_date + timedelta(days=join_days)
        
        customers_list.append({
            "Customer_ID": cust_id,
            "Customer_Name": name,
            "Segment": segment,
            "Region_ID": region_id,
            "State": state,
            "City": city,
            "Join_Date": join_date.strftime("%Y-%m-%d")
        })
        
    df_customers = pd.DataFrame(customers_list)

    # 5. Generate Orders & Order_Items (Targeting 15,500 transactional items)
    # Target: ~8,000 orders, with average 1.94 items per order
    num_orders = 8000
    orders_list = []
    order_items_list = []
    
    order_id_counter = 10001
    order_item_id_counter = 100001
    
    order_start_date = datetime(2024, 1, 1)
    # Order items lists to populate flat file
    
    for _ in range(num_orders):
        order_id = f"ORD-{order_id_counter}"
        customer = df_customers.sample(1).iloc[0]
        cust_id = customer["Customer_ID"]
        region_id = customer["Region_ID"]
        state = customer["State"]
        city = customer["City"]
        
        # Order date after customer joined
        cust_join_dt = datetime.strptime(customer["Join_Date"], "%Y-%m-%d")
        min_order_days = (order_start_date - cust_join_dt).days
        days_offset = np.random.randint(max(0, min_order_days), 880) # 880 days span (up to mid-2026)
        order_date = cust_join_dt + timedelta(days=days_offset)
        
        # Check order date constraint (clamp to June 1, 2026)
        clamp_date = datetime(2026, 6, 1)
        if order_date > clamp_date:
            order_date = clamp_date - timedelta(days=np.random.randint(1, 30))
            
        # Ship date based on mode
        ship_mode = np.random.choice(["Standard Class", "Second Class", "First Class", "Same Day"], p=[0.60, 0.20, 0.15, 0.05])
        if ship_mode == "Same Day":
            ship_days = 0
        elif ship_mode == "First Class":
            ship_days = np.random.randint(1, 3)
        elif ship_mode == "Second Class":
            ship_days = np.random.randint(2, 5)
        else:
            ship_days = np.random.randint(4, 8) # delay risk
            
        ship_date = order_date + timedelta(days=ship_days)
        
        orders_list.append({
            "Order_ID": order_id,
            "Customer_ID": cust_id,
            "Region_ID": region_id,
            "State": state,
            "City": city,
            "Order_Date": order_date.strftime("%Y-%m-%d"),
            "Ship_Date": ship_date.strftime("%Y-%m-%d"),
            "Ship_Mode": ship_mode
        })
        
        # Generate items per order (1 to 4 items)
        num_items = np.random.choice([1, 2, 3, 4], p=[0.45, 0.30, 0.15, 0.10])
        chosen_prods = df_products.sample(num_items)
        
        for _, prod in chosen_prods.iterrows():
            prod_id = prod["Product_ID"]
            qty = np.random.choice([1, 2, 3, 4, 5], p=[0.40, 0.30, 0.15, 0.10, 0.05])
            u_price = prod["Unit_Price"]
            u_cost = prod["Unit_Cost"]
            cat_id = prod["Category_ID"]
            subcat = prod["Subcategory"]
            
            # Weighted discount rates
            # Cyber-dark default: high discount risk in South region ("REG-03") and Furniture ("CAT-02")
            if region_id == "REG-03" or cat_id == "CAT-02":
                discount = np.random.choice([0.0, 0.10, 0.15, 0.20, 0.30, 0.40], p=[0.30, 0.15, 0.15, 0.15, 0.15, 0.10])
            else:
                discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.60, 0.15, 0.10, 0.10, 0.05])
                
            # Sales cost calculations
            sales = np.round((qty * u_price) * (1 - discount), 2)
            cost = np.round(qty * u_cost, 2)
            
            # Shipping surcharge adjustment for South region (REG-03) to compress profit
            if region_id == "REG-03":
                cost = np.round(cost * 1.08, 2) # 8% logistics cost surcharge
                
            profit = np.round(sales - cost, 2)
            
            order_items_list.append({
                "Order_Item_ID": f"ITEM-{order_item_id_counter}",
                "Order_ID": order_id,
                "Product_ID": prod_id,
                "Quantity": qty,
                "Unit_Price": u_price,
                "Discount": discount,
                "Sales": sales,
                "Cost": cost,
                "Profit": profit
            })
            order_item_id_counter += 1
            
        order_id_counter += 1

    df_orders = pd.DataFrame(orders_list)
    df_order_items = pd.DataFrame(order_items_list)

    # 6. Generate Returns
    # Returns should be higher for:
    # 1. Furniture category (CAT-02)
    # 2. Shipping latency > 5 days
    returns_list = []
    
    # Merge order items with product category and order shipping latency to flag returned orders
    df_temp = df_order_items.merge(df_products, on="Product_ID")
    df_temp = df_temp.merge(df_orders, on="Order_ID")
    
    unique_orders = df_orders["Order_ID"].tolist()
    
    for ord_id in unique_orders:
        order_items = df_temp[df_temp["Order_ID"] == ord_id]
        
        # Calculate shipping delay
        ord_dt = datetime.strptime(order_items.iloc[0]["Order_Date"], "%Y-%m-%d")
        shp_dt = datetime.strptime(order_items.iloc[0]["Ship_Date"], "%Y-%m-%d")
        latency = (shp_dt - ord_dt).days
        
        has_furniture = "CAT-02" in order_items["Category_ID"].values
        has_tech = "CAT-01" in order_items["Category_ID"].values
        
        # Determine base return probability
        prob = 0.04 # 4% base
        if has_furniture:
            prob = 0.12 # 12% for furniture
        elif has_tech:
            prob = 0.03 # 3% for tech
            
        # Add latency penalty
        if latency > 5:
            prob += 0.15 # 15% bump for slow shipping
            
        if np.random.rand() < prob:
            # Pick a return reason
            reason = np.random.choice(
                ["Defective", "Wrong Item", "Delayed Delivery", "Unsatisfied"],
                p=[0.30, 0.20, 0.35 if latency > 5 else 0.15, 0.15 if latency > 5 else 0.35]
            )
            
            # Return date is order date + 7-15 days
            ret_dt = ord_dt + timedelta(days=np.random.randint(7, 16))
            returns_list.append({
                "Order_ID": ord_id,
                "Return_Date": ret_dt.strftime("%Y-%m-%d"),
                "Return_Reason": reason
            })
            
    df_returns = pd.DataFrame(returns_list)

    # 7. Merge all into Consolidated flat file (ecommerce_data.csv)
    # Let's align all fields:
    # Customer ID, Order ID, Product ID, Category, Subcategory, Region, State, Order Date, 
    # Quantity, Unit Price, Discount, Sales, Cost, Profit, Return Status
    df_flat = df_order_items.merge(df_orders, on="Order_ID")
    df_flat = df_flat.merge(df_customers.drop(columns=["Region_ID", "State", "City"]), on="Customer_ID")
    df_flat = df_flat.merge(df_products, on="Product_ID")
    df_flat = df_flat.merge(df_regions, on="Region_ID")
    df_flat = df_flat.merge(df_categories, on="Category_ID")
    df_flat = df_flat.merge(df_returns, on="Order_ID", how="left")
    
    df_flat["Return_Status"] = df_flat["Return_Reason"].apply(lambda x: "Returned" if pd.notnull(x) else "Delivered")
    
    # Select final requested fields
    final_cols = [
        "Customer_ID", "Customer_Name", "Segment", "Order_ID", "Order_Date", 
        "Ship_Date", "Ship_Mode", "Product_ID", "Product_Name", "Category", 
        "Subcategory", "Region", "State", "City", "Quantity", "Unit_Price_x", 
        "Discount", "Sales", "Cost", "Profit", "Return_Status", "Return_Reason"
    ]
    df_flat_final = df_flat[final_cols].rename(columns={"Unit_Price_x": "Unit_Price"})

    print(f"Generated Customers: {len(df_customers)}")
    print(f"Generated Products: {len(df_products)}")
    print(f"Generated Orders: {len(df_orders)}")
    print(f"Generated Order Items: {len(df_order_items)}")
    print(f"Generated Returns: {len(df_returns)}")
    print(f"Generated Flat Master Records: {len(df_flat_final)}")

    # 8. Create folder paths and save files
    os.makedirs("e-commerce-bi-platform/dataset", exist_ok=True)
    
    # Save normalized tables
    df_customers.to_csv("e-commerce-bi-platform/dataset/customers.csv", index=False)
    df_products.to_csv("e-commerce-bi-platform/dataset/products.csv", index=False)
    df_orders.to_csv("e-commerce-bi-platform/dataset/orders.csv", index=False)
    df_order_items.to_csv("e-commerce-bi-platform/dataset/order_items.csv", index=False)
    df_returns.to_csv("e-commerce-bi-platform/dataset/returns.csv", index=False)
    df_regions.to_csv("e-commerce-bi-platform/dataset/regions.csv", index=False)
    df_categories.to_csv("e-commerce-bi-platform/dataset/categories.csv", index=False)
    
    # Save Master flat file
    df_flat_final.to_csv("e-commerce-bi-platform/dataset/ecommerce_data.csv", index=False)
    
    # Save Excel master sheet (formatted copy for pivots)
    # We will limit size to avoid excessive writing times, saving only flat data
    df_flat_final.to_excel("e-commerce-bi-platform/dataset/ecommerce_data.xlsx", index=False, sheet_name="MasterData")
    print("All datasets successfully generated and saved to e-commerce-bi-platform/dataset/!")

if __name__ == "__main__":
    generate_ecommerce_data()
