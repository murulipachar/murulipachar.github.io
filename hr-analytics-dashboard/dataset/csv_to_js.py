import csv
import json
import os

csv_path = "dataset/HR_Analytics.csv"
js_dir = "dashboard"
js_path = "dashboard/data.js"

os.makedirs(js_dir, exist_ok=True)

records = []
with open(csv_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convert numeric fields
        row['Age'] = int(row['Age'])
        row['Salary'] = int(row['Salary'])
        row['YearsAtCompany'] = int(row['YearsAtCompany'])
        row['PerformanceRating'] = int(row['PerformanceRating'])
        row['JobSatisfaction'] = int(row['JobSatisfaction'])
        records.append(row)

with open(js_path, mode="w", encoding="utf-8") as f:
    f.write("const HR_DATA = ")
    json.dump(records, f, indent=2)
    f.write(";\n")

print(f"Successfully converted CSV to JS data file! Total records: {len(records)}")
