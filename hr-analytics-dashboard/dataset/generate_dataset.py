import os
import random
import csv
import pandas as pd

# Define paths
output_csv = "dataset/HR_Analytics.csv"
output_xlsx = "dataset/HR_Analytics.xlsx"

# Ensure dataset directory exists
os.makedirs("dataset", exist_ok=True)

# Seed for reproducibility
random.seed(42)

# Names generation lists
first_names_m = [
    "Rajesh", "Amit", "David", "Michael", "Vikram", "Rahul", "John", "Robert", "Arjun", "Sanjay",
    "Vijay", "Rohan", "Anil", "Sandeep", "James", "William", "Daniel", "Matthew", "Abhishek", "Karan",
    "Aditya", "Vivek", "Manoj", "Harish", "Pranav", "Thomas", "Charles", "Joseph", "Richard", "Christopher"
]
first_names_f = [
    "Priya", "Sunita", "Sarah", "Emily", "Kavita", "Deepa", "Linda", "Jessica", "Sneha", "Neha",
    "Anjali", "Ritu", "Pooja", "Meera", "Elizabeth", "Jennifer", "Patricia", "Barbara", "Mary", "Swati",
    "Kiran", "Divya", "Aishwarya", "Shruti", "Shalini", "Susan", "Margaret", "Dorothy", "Lisa", "Karen"
]
first_names_nb = [
    "Alex", "Sam", "Taylor", "Jordan", "Morgan", "Robin", "Casey", "Jamie", "Riley", "Avery",
    "Skyler", "Pat", "Chris", "Jesse", "Dana", "Ren", "Shiloh", "Rowan", "Hayden", "Dakota"
]
last_names = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Smith", "Johnson", "Williams", "Brown", "Jones",
    "Das", "Joshi", "Nair", "Reddy", "Rao", "Fernandez", "Sen", "Mehta", "Bhat", "Chawla",
    "Miller", "Davis", "Wilson", "Anderson", "Taylor", "Thomas", "White", "Harris", "Martin", "Clark",
    "Pillai", "Deshmukh", "Kulkarni", "Iyer", "Banerjee", "Chatterjee", "Roy", "Verma", "Prasad", "Mishra"
]

# Educational background distribution
education_levels = ["High School", "Associate Degree", "Bachelor's Degree", "Master's Degree", "Doctoral Degree"]

# Marital status distribution
marital_statuses = ["Single", "Married", "Divorced"]

# Departments and Roles mapping
dept_roles = {
    "Research & Development": [
        ("Research Director", 110000, 160000, 15, "Doctoral Degree"),
        ("Senior Scientist", 85000, 120000, 8, "Master's Degree"),
        ("Research Scientist", 60000, 90000, 3, "Bachelor's Degree"),
        ("Laboratory Technician", 38000, 55000, 0, "Associate Degree"),
        ("Manufacturing Director", 95000, 140000, 12, "Bachelor's Degree"),
        ("Healthcare Representative", 50000, 80000, 2, "Bachelor's Degree")
    ],
    "Sales": [
        ("Sales Director", 105000, 155000, 14, "Bachelor's Degree"),
        ("Account Manager", 75000, 110000, 7, "Bachelor's Degree"),
        ("Sales Executive", 55000, 85000, 4, "Bachelor's Degree"),
        ("Sales Representative", 32000, 48000, 0, "High School")
    ],
    "IT & Infrastructure": [
        ("IT Director", 115000, 170000, 15, "Master's Degree"),
        ("Lead Software Engineer", 95000, 135000, 9, "Bachelor's Degree"),
        ("Software Engineer", 65000, 95000, 3, "Bachelor's Degree"),
        ("Data Analyst", 55000, 85000, 2, "Bachelor's Degree"),
        ("IT Support Specialist", 35000, 52000, 0, "Associate Degree")
    ],
    "Finance": [
        ("Finance Manager", 90000, 130000, 10, "Master's Degree"),
        ("Senior Financial Analyst", 75000, 110000, 7, "Bachelor's Degree"),
        ("Financial Analyst", 55000, 80000, 2, "Bachelor's Degree"),
        ("Accountant", 45000, 70000, 1, "Bachelor's Degree")
    ],
    "Human Resources": [
        ("HR Manager", 85000, 120000, 10, "Master's Degree"),
        ("HR Specialist", 52000, 78000, 4, "Bachelor's Degree"),
        ("Recruiter", 40000, 60000, 1, "Bachelor's Degree"),
        ("HR Coordinator", 34000, 48000, 0, "Associate Degree")
    ]
}

data = []
total_records = 1475

for i in range(1, total_records + 1):
    emp_id = f"EMP{i:04d}"
    
    # 1. Gender distribution: Male (~55%), Female (~42%), Non-binary (~3%)
    gender_rand = random.random()
    if gender_rand < 0.55:
        gender = "Male"
        first_name = random.choice(first_names_m)
    elif gender_rand < 0.97:
        gender = "Female"
        first_name = random.choice(first_names_f)
    else:
        gender = "Non-binary"
        first_name = random.choice(first_names_nb)
        
    last_name = random.choice(last_names)
    emp_name = f"{first_name} {last_name}"
    
    # 2. Age distribution: 21 to 60
    age = int(random.normalvariate(37, 9))
    age = max(21, min(60, age))
    
    # 3. Department & Job Role assignment
    dept = random.choices(
        list(dept_roles.keys()),
        weights=[0.40, 0.22, 0.20, 0.11, 0.07], # R&D has most employees, HR least
        k=1
    )[0]
    
    role_tuple = random.choice(dept_roles[dept])
    job_role, min_sal, max_sal, min_exp_req, min_edu_req = role_tuple
    
    # 4. Education Level assignment relative to job role min education requirement
    min_edu_idx = education_levels.index(min_edu_req)
    # Give them a random level at or above minimum required, weighted towards bachelor/master
    edu_weights = [0.05, 0.10, 0.50, 0.30, 0.05]
    # Filter weights starting from min_edu_idx
    valid_edu = education_levels[min_edu_idx:]
    valid_weights = edu_weights[min_edu_idx:]
    # Re-normalize weights
    sum_weights = sum(valid_weights)
    valid_weights = [w / sum_weights for w in valid_weights]
    education = random.choices(valid_edu, weights=valid_weights, k=1)[0]
    
    # Adjust age if doctoral degree was selected (doctoral degree holders should be older)
    if education == "Doctoral Degree" and age < 28:
        age = random.randint(28, 42)
    elif education == "Master's Degree" and age < 24:
        age = random.randint(24, 35)
        
    # 5. Years at Company (Experience)
    # Must be less than age - 18 - (extra education years)
    edu_years_offset = education_levels.index(education) * 2
    max_experience = max(0, age - 18 - edu_years_offset)
    years_at_company = int(random.triangular(0, min(max_experience, 22), min(max_experience, 4)))
    
    # 6. Marital Status
    marital_status = random.choice(marital_statuses)
    
    # 7. Salary calculation based on job role boundaries and experience
    experience_ratio = min(1.0, years_at_company / 15.0)
    salary = int(min_sal + (max_sal - min_sal) * experience_ratio + random.uniform(-5000, 5000))
    # Cap salary to role max plus small variance
    salary = max(min_sal - 2000, min(max_sal + 10000, salary))
    
    # 8. Performance Rating: 1 (Needs Improvement) to 4 (Outstanding)
    # Normally distributed weights
    performance_rating = random.choices([1, 2, 3, 4], weights=[0.08, 0.62, 0.22, 0.08], k=1)[0]
    
    # 9. Overtime (Yes / No)
    overtime = random.choices(["Yes", "No"], weights=[0.28, 0.72], k=1)[0]
    
    # 10. Job Satisfaction: 1 (Very Dissatisfied) to 4 (Very Satisfied)
    # Highly correlated with overtime and performance rating (low performance/high overtime -> lower satisfaction)
    sat_weights = [0.10, 0.20, 0.40, 0.30] # default
    if overtime == "Yes":
        sat_weights = [0.20, 0.30, 0.35, 0.15] # stressed
    if performance_rating == 1:
        sat_weights = [0.35, 0.35, 0.20, 0.10] # disengaged
    job_satisfaction = random.choices([1, 2, 3, 4], weights=sat_weights, k=1)[0]
    
    # 11. Attrition calculation (Yes / No) - MODELING A REALISTIC PATTERN
    # Base probability
    attr_prob = 0.04
    
    # Overtime penalty
    if overtime == "Yes":
        attr_prob += 0.18
        
    # Job satisfaction penalty
    if job_satisfaction == 1:
        attr_prob += 0.25
    elif job_satisfaction == 2:
        attr_prob += 0.12
        
    # Tenure penalty (newer employees leave more often)
    if years_at_company <= 1:
        attr_prob += 0.15
    elif years_at_company <= 3:
        attr_prob += 0.08
    elif years_at_company > 10:
        attr_prob -= 0.05
        
    # Salary relative check
    # Check if salary is below the average for this specific role
    avg_role_sal = (min_sal + max_sal) / 2.0
    if salary < avg_role_sal:
        attr_prob += 0.10
        
    # Age factor
    if age < 30:
        attr_prob += 0.08
    elif age > 50:
        # Retirement or stable
        attr_prob -= 0.04
        
    # Performance rating impact (low ratings get terminated/leave; high rating might leave if underpaid)
    if performance_rating == 1:
        attr_prob += 0.30
    elif performance_rating == 4 and salary < avg_role_sal:
        attr_prob += 0.15 # flight risk
        
    # Marital status factor
    if marital_status == "Single":
        attr_prob += 0.04
        
    # Cap probability between 1% and 92%
    attr_prob = max(0.01, min(0.92, attr_prob))
    
    attrition = "Yes" if random.random() < attr_prob else "No"
    
    data.append({
        "EmployeeID": emp_id,
        "EmployeeName": emp_name,
        "Gender": gender,
        "Age": age,
        "Department": dept,
        "JobRole": job_role,
        "Education": education,
        "MaritalStatus": marital_status,
        "Salary": salary,
        "YearsAtCompany": years_at_company,
        "PerformanceRating": performance_rating,
        "Overtime": overtime,
        "JobSatisfaction": job_satisfaction,
        "Attrition": attrition
    })

# Write to CSV
with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

# Write to Excel
df = pd.DataFrame(data)
df.to_excel(output_xlsx, index=False, sheet_name="HR Employees")

print(f"Data generation complete!")
print(f"Total Records Generated: {len(data)}")
print(f"Overall Attrition Count: {df[df['Attrition'] == 'Yes'].shape[0]} ({df[df['Attrition'] == 'Yes'].shape[0] / len(data) * 100:.2f}%)")
print(f"Overtime Attrition Rate: {df[(df['Overtime'] == 'Yes') & (df['Attrition'] == 'Yes')].shape[0] / df[df['Overtime'] == 'Yes'].shape[0] * 100:.2f}%")
print(f"Low Satisfaction (1) Attrition Rate: {df[(df['JobSatisfaction'] == 1) & (df['Attrition'] == 'Yes')].shape[0] / df[df['JobSatisfaction'] == 1].shape[0] * 100:.2f}%")
