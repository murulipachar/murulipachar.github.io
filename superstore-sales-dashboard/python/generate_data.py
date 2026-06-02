import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_superstore_dataset(num_rows=5000):
    # Lists of realistic values
    ship_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
    
    segments = ['Consumer', 'Corporate', 'Home Office']
    segment_weights = [0.50, 0.30, 0.20]
    
    regions = ['West', 'East', 'Central', 'South']
    region_weights = [0.32, 0.28, 0.22, 0.18]
    
    # State and City map to keep data geo-consistent
    geo_map = {
        'West': [
            ('California', 'Los Angeles', '90036'),
            ('California', 'San Francisco', '94110'),
            ('California', 'San Diego', '92109'),
            ('Washington', 'Seattle', '98103'),
            ('Washington', 'Spokane', '99201'),
            ('Oregon', 'Portland', '97201'),
            ('Arizona', 'Phoenix', '85001'),
            ('Colorado', 'Denver', '80202'),
            ('Utah', 'Salt Lake City', '84101'),
            ('Nevada', 'Las Vegas', '89101')
        ],
        'East': [
            ('New York', 'New York City', '10011'),
            ('New York', 'Albany', '12203'),
            ('Pennsylvania', 'Philadelphia', '19104'),
            ('Pennsylvania', 'Pittsburgh', '15213'),
            ('Massachusetts', 'Boston', '02116'),
            ('Ohio', 'Columbus', '43215'),
            ('Ohio', 'Cleveland', '44114'),
            ('Delaware', 'Wilmington', '19801'),
            ('Maryland', 'Baltimore', '21201'),
            ('New Jersey', 'Newark', '07102')
        ],
        'Central': [
            ('Illinois', 'Chicago', '60611'),
            ('Texas', 'Houston', '77002'),
            ('Texas', 'Dallas', '75201'),
            ('Texas', 'Austin', '78701'),
            ('Texas', 'San Antonio', '78201'),
            ('Michigan', 'Detroit', '48201'),
            ('Minnesota', 'Minneapolis', '55401'),
            ('Wisconsin', 'Milwaukee', '53202'),
            ('Indiana', 'Indianapolis', '46201'),
            ('Missouri', 'Saint Louis', '63101')
        ],
        'South': [
            ('Florida', 'Miami', '33139'),
            ('Florida', 'Tampa', '33602'),
            ('Florida', 'Jacksonville', '32202'),
            ('Georgia', 'Atlanta', '30303'),
            ('North Carolina', 'Charlotte', '28202'),
            ('North Carolina', 'Raleigh', '27601'),
            ('Virginia', 'Richmond', '23219'),
            ('Virginia', 'Virginia Beach', '23451'),
            ('Tennessee', 'Nashville', '37203'),
            ('Kentucky', 'Louisville', '40202')
        ]
    }
    
    categories = {
        'Furniture': {
            'Subcategories': {
                'Bookcases': ('FUR-BO', 12, 45, 0.12),
                'Chairs': ('FUR-CH', 8, 35, 0.15),
                'Tables': ('FUR-TA', 18, 80, 0.08),
                'Furnishings': ('FUR-FU', 1, 12, 0.20)
            }
        },
        'Office Supplies': {
            'Subcategories': {
                'Appliances': ('OFF-AP', 4, 28, 0.25),
                'Binders': ('OFF-BI', 0.2, 8, 0.35),
                'Art': ('OFF-AR', 0.2, 3.5, 0.30),
                'Paper': ('OFF-PA', 0.5, 5, 0.40),
                'Storage': ('OFF-ST', 3, 20, 0.20),
                'Supplies': ('OFF-SU', 1, 15, 0.15),
                'Envelopes': ('OFF-EN', 0.2, 2.5, 0.35),
                'Labels': ('OFF-LA', 0.2, 2, 0.40),
                'Fasteners': ('OFF-FA', 0.1, 1.5, 0.30)
            }
        },
        'Technology': {
            'Subcategories': {
                'Phones': ('TEC-PH', 15, 90, 0.30),
                'Accessories': ('TEC-AC', 2, 20, 0.32),
                'Machines': ('TEC-MA', 30, 250, 0.22),
                'Copiers': ('TEC-CO', 40, 450, 0.45)
            }
        }
    }
    
    # Generate customer bank
    customer_segments = {
        'Consumer': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles', 
                     'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen'],
        'Corporate': ['Smith Corp', 'Johnson LLC', 'Williams Inc', 'Brown Co', 'Jones Group', 'Miller Enterprise', 'Davis Ltd', 
                      'Garcia Bros', 'Rodriguez Partners', 'Wilson Holdings', 'Martinez Tech', 'Anderson Ventures', 'Taylor Logistics', 
                      'Thomas & Sons', 'Moore Industries', 'Martin & Co', 'Jackson Global', 'White & Sons', 'Harris Group', 'Martin Consulting'],
        'Home Office': ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah', 'Ian', 'Julia',
                        'Kevin', 'Laura', 'Marcus', 'Nora', 'Oscar', 'Penelope', 'Quinn', 'Rachel', 'Samuel', 'Tina']
    }
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia', 'Rodriguez', 'Wilson', 
                  'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Hernandez', 'Moore', 'Martin', 'Jackson', 'Martin', 'Lee']

    customer_pool = []
    for seg in segments:
        for idx in range(1, 151): # 150 customers per segment
            if seg == 'Corporate':
                name = random.choice(customer_segments[seg]) + f" #{random.randint(1, 9)}"
            else:
                name = random.choice(customer_segments[seg]) + " " + random.choice(last_names)
            cust_id = f"{seg[0][:1]}{name[:2].upper()}-{idx:05d}"
            customer_pool.append({'ID': cust_id, 'Name': name, 'Segment': seg})
            
    # Generate products pool
    product_pool = []
    product_id_counter = 10000000
    for cat, cat_data in categories.items():
        for subcat, (prefix, min_p, max_p, base_m) in cat_data['Subcategories'].items():
            for idx in range(1, 31): # 30 products per subcategory
                product_id_counter += 1
                prod_id = f"{prefix}-{product_id_counter}"
                prod_name = f"{subcat} SKU-{idx:03d} (Premium Quality)"
                product_pool.append({
                    'ID': prod_id, 
                    'Category': cat, 
                    'SubCategory': subcat, 
                    'ProductName': prod_name,
                    'MinPrice': min_p,
                    'MaxPrice': max_p,
                    'BaseMargin': base_m
                })

    start_date = datetime(2022, 1, 1)
    
    data = []
    
    for row_idx in range(1, num_rows + 1):
        # 1. Order and Ship dates with Seasonality (higher weight in Nov/Dec, and August)
        month_rand = random.random()
        if month_rand < 0.25: # Nov, Dec (25% of orders)
            month = random.choice([11, 12])
        elif month_rand < 0.40: # Aug, Sep (15% of orders)
            month = random.choice([8, 9])
        else: # Other months
            month = random.choice([1, 2, 3, 4, 5, 6, 7, 10])
            
        year = random.choice([2022, 2023, 2024, 2025])
        day = random.randint(1, 28)
        order_date = datetime(year, month, day)
        
        # Ship Mode & Lead times
        ship_mode = random.choice(ship_modes)
        if ship_mode == 'Same Day':
            ship_delay = 0
        elif ship_mode == 'First Class':
            ship_delay = random.randint(1, 2)
        elif ship_mode == 'Second Class':
            ship_delay = random.randint(2, 4)
        else: # Standard Class
            ship_delay = random.randint(3, 7)
            
        ship_date = order_date + timedelta(days=ship_delay)
        
        # 2. Customer
        cust = random.choice(customer_pool)
        segment = cust['Segment']
        cust_id = cust['ID']
        cust_name = cust['Name']
        
        # 3. Geography based on weights
        region = np.random.choice(regions, p=region_weights)
        state_city_zip = random.choice(geo_map[region])
        state, city, postal_code = state_city_zip
        
        # 4. Product Selection
        prod = random.choice(product_pool)
        prod_id = prod['ID']
        category = prod['Category']
        sub_category = prod['SubCategory']
        prod_name = prod['ProductName']
        base_margin = prod['BaseMargin']
        
        # 5. Financials
        base_unit_price = random.uniform(prod['MinPrice'], prod['MaxPrice'])
        quantity = random.randint(1, 10)
        
        # Add volume discount
        if quantity >= 8:
            discount = random.choice([0.2, 0.3, 0.4])
        elif quantity >= 5:
            discount = random.choice([0.0, 0.1, 0.2])
        else:
            discount = random.choice([0.0, 0.0, 0.0, 0.0, 0.1, 0.2]) # 0% is most common
            
        # Furniture is discounted more aggressively to represent retail struggles
        if category == 'Furniture' and random.random() < 0.4:
            discount = random.choice([0.3, 0.4, 0.5, 0.6])
            
        sales_raw = base_unit_price * quantity
        sales_actual = round(sales_raw * (1 - discount), 2)
        
        # Base product cost is based on base margins
        product_unit_cost = base_unit_price * (1 - base_margin)
        total_product_cost = product_unit_cost * quantity
        
        # Profit = Sales - Cost. Highly realistic: heavy discounts turn profit negative
        profit = round(sales_actual - total_product_cost, 2)
        
        # Generate clean Order ID: CA-YYYY-XXXXXX
        order_id = f"CA-{year}-{random.randint(100000, 999999)}"
        
        data.append({
            'Row ID': row_idx,
            'Order ID': order_id,
            'Order Date': order_date.strftime('%Y-%m-%d'),
            'Ship Date': ship_date.strftime('%Y-%m-%d'),
            'Ship Mode': ship_mode,
            'Customer ID': cust_id,
            'Customer Name': cust_name,
            'Segment': segment,
            'Country': 'United States',
            'City': city,
            'State': state,
            'Postal Code': postal_code,
            'Region': region,
            'Product ID': prod_id,
            'Category': category,
            'Sub-Category': sub_category,
            'Product Name': prod_name,
            'Sales': sales_actual,
            'Quantity': quantity,
            'Discount': discount,
            'Profit': profit
        })
        
    df = pd.DataFrame(data)
    # Sort by order date to make chronological
    df['Order Date Temp'] = pd.to_datetime(df['Order Date'])
    df = df.sort_values('Order Date Temp').drop(columns=['Order Date Temp'])
    df['Row ID'] = range(1, len(df) + 1)
    
    return df

if __name__ == '__main__':
    import os
    print("Generating highly realistic Superstore Sales dataset...")
    df_superstore = generate_superstore_dataset(5000)
    
    # Create dataset folder if not exists
    os.makedirs('dataset', exist_ok=True)
    df_superstore.to_csv('dataset/raw_superstore_sales.csv', index=False)
    print(f"Dataset generated and saved successfully: dataset/raw_superstore_sales.csv ({len(df_superstore)} rows)")
