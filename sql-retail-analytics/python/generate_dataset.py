import csv
import random
from datetime import datetime, timedelta
import os
import math

# Set seeds for absolute reproducibility
random.seed(42)

def generate_retail_dataset():
    print("Initializing retail dataset generation...")
    
    # 1. Customer Profiles Setup (1,000 unique customers)
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", 
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", 
        "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley", 
        "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle", 
        "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa", 
        "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", 
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", 
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", 
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", 
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Diaz", "Howell", "Sullivan"
    ]
    
    regions = {
        "East": ["New York", "Boston", "Philadelphia", "Washington", "Baltimore"],
        "West": ["Los Angeles", "San Francisco", "Seattle", "Portland", "Denver"],
        "South": ["Miami", "Atlanta", "Houston", "Dallas", "Charlotte"],
        "Central": ["Chicago", "Detroit", "Minneapolis", "St. Louis", "Cleveland"]
    }
    
    payment_methods = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Bank Transfer"]
    
    customers = []
    # Create 1000 persistent customer profiles
    for i in range(1, 1001):
        cust_id = f"CUST-{1000 + i}"
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        gender = random.choice(["Male", "Female", "Non-binary"])
        age = random.randint(18, 75)
        
        # Select Region and City
        region = random.choice(list(regions.keys()))
        city = random.choice(regions[region])
        
        # Assign customer purchasing behavior archetype
        # HV = High Value (high quantity, premium items, low discount sensitivity)
        # RB = Repeat Buyer (frequent orders, medium quantity, average discount sensitivity)
        # BH = Bargain Hunter (infrequent orders, high discount sensitivity, low margins)
        # NC = Normal Customer (standard distributed behavior)
        archetype_roll = random.random()
        if archetype_roll < 0.12:
            archetype = "High-Value"
        elif archetype_roll < 0.32:
            archetype = "Frequent Repeat"
        elif archetype_roll < 0.50:
            archetype = "Bargain Hunter"
        else:
            archetype = "Standard"
            
        customers.append({
            "Customer_ID": cust_id,
            "Customer_Name": name,
            "Gender": gender,
            "Age": age,
            "City": city,
            "Region": region,
            "Archetype": archetype
        })
    
    # 2. Product Catalog Setup
    products = {
        "Electronics": [
            {"Name": "UltraView 4K Smart TV", "Price_Range": (450, 950), "Margin": 0.22},
            {"Name": "ProBook 15.6 Inch Laptop", "Price_Range": (650, 1200), "Margin": 0.18},
            {"Name": "AeroNoise Wireless Headphones", "Price_Range": (120, 250), "Margin": 0.30},
            {"Name": "PulseFit Active Smartwatch", "Price_Range": (80, 180), "Margin": 0.28},
            {"Name": "SonicCharge Multi-Port Hub", "Price_Range": (25, 60), "Margin": 0.35},
            {"Name": "WaveSync Bluetooth Speaker", "Price_Range": (45, 110), "Margin": 0.32},
            {"Name": "TabLite 10-Inch Tablet", "Price_Range": (150, 320), "Margin": 0.25}
        ],
        "Clothing": [
            {"Name": "UrbanFit Designer Jeans", "Price_Range": (45, 95), "Margin": 0.55},
            {"Name": "LuxeWeave Cotton T-Shirt", "Price_Range": (18, 35), "Margin": 0.65},
            {"Name": "SummitTech Running Shoes", "Price_Range": (70, 140), "Margin": 0.50},
            {"Name": "Legacy Leather Jacket", "Price_Range": (120, 280), "Margin": 0.45},
            {"Name": "Merino Wool Sweater", "Price_Range": (55, 110), "Margin": 0.52},
            {"Name": "Solstice Activewear Set", "Price_Range": (40, 85), "Margin": 0.58},
            {"Name": "Elysian Silk Scarf", "Price_Range": (25, 60), "Margin": 0.60}
        ],
        "Home & Kitchen": [
            {"Name": "BrewMaster Espresso Machine", "Price_Range": (150, 350), "Margin": 0.38},
            {"Name": "CrispAir XL Digital Air Fryer", "Price_Range": (80, 180), "Margin": 0.35},
            {"Name": "TerraStone 16pc Dinnerware Set", "Price_Range": (45, 95), "Margin": 0.45},
            {"Name": "SleepWell Memory Foam Pillow", "Price_Range": (30, 65), "Margin": 0.48},
            {"Name": "NutriBlend 1000W Blender", "Price_Range": (60, 130), "Margin": 0.40},
            {"Name": "CyclonePro Cordless Vacuum", "Price_Range": (120, 240), "Margin": 0.34},
            {"Name": "Lumina LED Desk Lamp", "Price_Range": (20, 50), "Margin": 0.42}
        ],
        "Furniture": [
            {"Name": "ErgoTask Mesh Office Chair", "Price_Range": (120, 280), "Margin": 0.28},
            {"Name": "ApexLift Electric Standing Desk", "Price_Range": (250, 550), "Margin": 0.24},
            {"Name": "Nordic Solid Oak Bookshelf", "Price_Range": (180, 420), "Margin": 0.30},
            {"Name": "Modena Tufted Leather Sofa", "Price_Range": (800, 1600), "Margin": 0.20},
            {"Name": "HearthStone 5pc Dining Set", "Price_Range": (400, 850), "Margin": 0.25},
            {"Name": "CloudRest Fabric Recliner", "Price_Range": (220, 480), "Margin": 0.27},
            {"Name": "Forma Minimalist Side Table", "Price_Range": (60, 130), "Margin": 0.35}
        ],
        "Beauty & Health": [
            {"Name": "HydroGlow Hyaluronic Serum", "Price_Range": (28, 65), "Margin": 0.68},
            {"Name": "SonicDental Electric Toothbrush", "Price_Range": (45, 110), "Margin": 0.60},
            {"Name": "AuraSync Essential Oil Diffuser", "Price_Range": (22, 50), "Margin": 0.65},
            {"Name": "SatinSmooth Ionic Hair Dryer", "Price_Range": (35, 80), "Margin": 0.58},
            {"Name": "VelvetTouch 12pc Makeup Brush Set", "Price_Range": (18, 40), "Margin": 0.70},
            {"Name": "Noir Woodsy Eau de Parfum", "Price_Range": (60, 150), "Margin": 0.62},
            {"Name": "SilkBreeze Therapeutic Massager", "Price_Range": (40, 95), "Margin": 0.55}
        ]
    }
    
    # Pre-calculate unit prices for catalog items to ensure exact match when same product is sold
    product_catalog = {}
    for cat, prod_list in products.items():
        for p in prod_list:
            min_p, max_p = p["Price_Range"]
            # Round unit price to .99 or .49 for realism
            unit_p = round(random.uniform(min_p, max_p), 2)
            if random.random() > 0.5:
                unit_p = math.floor(unit_p) + 0.99
            else:
                unit_p = math.floor(unit_p) + 0.49
                
            product_catalog[p["Name"]] = {
                "Category": cat,
                "Unit_Price": unit_p,
                "Margin": p["Margin"]
            }

    # 3. Transaction Timeline Setup (2023-01-01 to 2025-12-31)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    days_range = (end_date - start_date).days
    
    total_rows = 12500
    transactions = []
    
    print(f"Simulating {total_rows} high-fidelity transactions...")
    
    order_id_counter = 100001
    
    # We will generate orders. A single Order_ID can contain 1 to 3 items (simulating a shopping cart).
    while len(transactions) < total_rows:
        # Determine order date based on seasonal weights
        # We assign a probability weight to each day of the year
        # Q4 (Nov, Dec) has a high holiday sales spike
        # August has a back-to-school sales spike
        # We will roll a random day and check its probability
        while True:
            rand_days = random.randint(0, days_range)
            o_date = start_date + timedelta(days=rand_days)
            month = o_date.month
            
            # Seasonal sales spikes
            weight = 1.0
            if month in [11, 12]:  # Q4 holidays spike
                weight = 2.4
            elif month == 8:       # August back-to-school spike
                weight = 1.6
            elif month in [1, 2]:  # Post-holiday slump
                weight = 0.7
                
            if random.random() < (weight / 2.5):
                break
                
        # Pick a customer based on weights (repeat buyers buy more frequently)
        # Normal distribution of customer selection
        # High-value and Repeat Buyers are selected more often
        cust_weights = []
        for c in customers:
            if c["Archetype"] == "Frequent Repeat":
                cust_weights.append(4)
            elif c["Archetype"] == "High-Value":
                cust_weights.append(3)
            elif c["Archetype"] == "Bargain Hunter":
                cust_weights.append(2)
            else:
                cust_weights.append(1)
                
        customer = random.choices(customers, weights=cust_weights, k=1)[0]
        
        # Decide how many items are in this order (1 to 3 items)
        cart_size = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]
        
        # Make sure we don't overshoot total_rows
        if len(transactions) + cart_size > total_rows:
            cart_size = total_rows - len(transactions)
            
        order_id = f"TXN-{order_id_counter}"
        order_id_counter += 1
        
        # Payment method is constant per transaction
        pay_method = random.choice(payment_methods)
        
        order_items = []
        for _ in range(cart_size):
            # Select product category
            # High-Value buys more Electronics/Furniture
            # Bargain Hunter buys whatever category has high discounts
            # Standard distribute
            cat_weights = {
                "Electronics": 0.20,
                "Clothing": 0.25,
                "Home & Kitchen": 0.22,
                "Furniture": 0.15,
                "Beauty & Health": 0.18
            }
            if customer["Archetype"] == "High-Value":
                cat_weights["Electronics"] += 0.15
                cat_weights["Furniture"] += 0.10
                cat_weights["Clothing"] -= 0.10
                cat_weights["Beauty & Health"] -= 0.15
            elif customer["Archetype"] == "Bargain Hunter":
                cat_weights["Clothing"] += 0.10
                cat_weights["Home & Kitchen"] += 0.05
                cat_weights["Electronics"] -= 0.15
                
            # Normalize weights
            cats = list(cat_weights.keys())
            wts = list(cat_weights.values())
            
            chosen_cat = random.choices(cats, weights=wts, k=1)[0]
            
            # Select a random product from this category
            cat_prods = [p for p, d in product_catalog.items() if d["Category"] == chosen_cat]
            prod_name = random.choice(cat_prods)
            prod_info = product_catalog[prod_name]
            
            # Quantity
            if customer["Archetype"] == "High-Value":
                qty = random.choices([1, 2, 3, 4, 5], weights=[20, 30, 25, 15, 10], k=1)[0]
            elif customer["Archetype"] == "Frequent Repeat":
                qty = random.choices([1, 2, 3], weights=[50, 40, 10], k=1)[0]
            else:
                qty = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5], k=1)[0]
                
            # Discount (promotional rates: 0%, 5%, 10%, 15%, 20%, 30%, 50%)
            # Bargain hunters almost always get discounts
            # High-value customers are less discount-sensitive
            # Q4 shopping spike has higher discount distributions
            if customer["Archetype"] == "Bargain Hunter":
                discount = random.choices([0.15, 0.20, 0.30, 0.50], weights=[20, 30, 35, 15], k=1)[0]
            elif customer["Archetype"] == "High-Value":
                discount = random.choices([0.0, 0.05, 0.10], weights=[70, 20, 10], k=1)[0]
            else:
                if o_date.month in [11, 12]:  # Q4 Holiday Promotions
                    discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50], weights=[25, 15, 15, 15, 15, 10, 5], k=1)[0]
                else:
                    discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[55, 15, 15, 10, 5], k=1)[0]
                    
            # Pricing Mechanics
            unit_price = prod_info["Unit_Price"]
            
            # Apply regional pricing anomalies
            # South region has slightly weaker pricing power, so we simulate a slight mark-down or lower sales conversion
            if customer["Region"] == "South":
                unit_price = round(unit_price * 0.96, 2)
                
            sales = round(qty * unit_price * (1.0 - discount), 2)
            
            # Net margin accounting
            # Cost is calculated based on baseline production cost of item
            # Cost = qty * (original_unit_price * (1 - Margin))
            original_unit_price = prod_info["Unit_Price"]
            baseline_cost = round(qty * original_unit_price * (1.0 - prod_info["Margin"]), 2)
            
            # Apply Logistics Overhead: bulk items (Furniture) have a 5% high-shipping fee surcharge in cost calculation
            if chosen_cat == "Furniture":
                baseline_cost = round(baseline_cost * 1.06, 2)
            elif chosen_cat == "Electronics":
                baseline_cost = round(baseline_cost * 1.02, 2)
                
            # Profit = Sales - Cost
            profit = round(sales - baseline_cost, 2)
            
            # Anomaly: Heavy discount-bleed scenario!
            # If discount is > 20% on low-margin categories (like Furniture or Electronics), profit will naturally drop negative.
            # Let's ensure this is true.
            if discount >= 0.25 and chosen_cat in ["Furniture", "Electronics"]:
                # Explicitly double check that it becomes a net loss
                if profit > 0:
                    profit = round(-0.15 * sales, 2)
            
            transactions.append({
                "Order_ID": order_id,
                "Order_Date": o_date.strftime("%Y-%m-%d"),
                "Customer_ID": customer["Customer_ID"],
                "Customer_Name": customer["Customer_Name"],
                "Gender": customer["Gender"],
                "Age": customer["Age"],
                "City": customer["City"],
                "Region": customer["Region"],
                "Product_Category": chosen_cat,
                "Product_Name": prod_name,
                "Quantity": qty,
                "Unit_Price": unit_price,
                "Sales": sales,
                "Discount": discount,
                "Profit": profit,
                "Payment_Method": pay_method
            })

    # Save to CSV (dynamically resolved output path to ensure complete portability)
    python_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(python_dir)
    output_dir = os.path.join(base_dir, "dataset")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "retail_sales_dataset.csv")
    
    headers = [
        "Order_ID", "Order_Date", "Customer_ID", "Customer_Name", "Gender", "Age",
        "City", "Region", "Product_Category", "Product_Name", "Quantity", 
        "Unit_Price", "Sales", "Discount", "Profit", "Payment_Method"
    ]
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(transactions)
        
    print(f"Success! Dataset successfully written to: {output_file}")
    print(f"Total Transactions: {len(transactions)}")
    
    # Calculate global metrics to double check business scale consistency
    total_rev = sum(t["Sales"] for t in transactions)
    total_prof = sum(t["Profit"] for t in transactions)
    avg_disc = sum(t["Discount"] for t in transactions) / len(transactions)
    margin = (total_prof / total_rev) * 100 if total_rev > 0 else 0
    negative_profit_count = sum(1 for t in transactions if t["Profit"] < 0)
    
    print(f"--- Dataset Integrity Check ---")
    print(f"Total Sales (Revenue): ${total_rev:,.2f}")
    print(f"Total Profit: ${total_prof:,.2f}")
    print(f"Overall Profit Margin: {margin:.2f}%")
    print(f"Average Discount: {avg_disc*100:.2f}%")
    print(f"Loss Transactions (Negative Profit): {negative_profit_count} ({negative_profit_count/len(transactions)*100:.2f}%)")

if __name__ == "__main__":
    generate_retail_dataset()
