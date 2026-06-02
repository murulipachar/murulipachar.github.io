# Power BI Design Guide: HR Analytics Dashboard

This document details the configuration, schema, DAX calculations, and styling guidelines required to construct the Power BI dashboard for the HR Analytics project. Follow these guidelines to build a recruiter-ready business intelligence report.

---

## 1. Data Model & Schema Design

For this project, we ingest the generated dataset (`HR_Analytics.csv` or `HR_Analytics.xlsx`). While the source file is a flat sheet, a robust dimensional model is configured inside Power BI using a Star Schema layout.

### Relationships Schema
- **Fact Table**: `Fact_Employees` (The primary query loaded from the source data)
- **Dimension Tables** (Created inside Power BI using Power Query or DAX):
  - `Dim_Calendar`: Generated to handle temporal analysis (if hiring/exit dates are added, or for trend forecasting).
  - `Dim_JobRoles`: Reference dimension created by referencing `Fact_Employees` to clean role categorization.

### Calendar Table DAX Formula
Create a standard calendar dimension to support time intelligence if needed:
```dax
Dim_Calendar = 
CALENDAR(
    DATE(2020, 1, 1),
    DATE(2026, 12, 31)
)
```

---

## 2. DAX Measures Dictionary

To populate the Key Performance Indicators (KPIs) and dynamic charts, create a dedicated table named `_Measures` and define the following metrics:

### Total Employee Count
```dax
Total Employees = COUNT(Fact_Employees[EmployeeID])
```

### Active Employee Count
```dax
Active Employees = CALCULATE(
    COUNT(Fact_Employees[EmployeeID]),
    Fact_Employees[Attrition] = "No"
)
```

### Attrition Count
```dax
Attrition Count = CALCULATE(
    COUNT(Fact_Employees[EmployeeID]),
    Fact_Employees[Attrition] = "Yes"
)
```

### Attrition Rate %
```dax
Attrition Rate % = DIVIDE([Attrition Count], [Total Employees], 0)
```

### Average Salary
```dax
Average Salary = AVERAGE(Fact_Employees[Salary])
```

### Average Experience (Tenure)
```dax
Average Experience = AVERAGE(Fact_Employees[YearsAtCompany])
```

### Overtime Attrition Rate %
```dax
Overtime Attrition Rate % = CALCULATE(
    [Attrition Rate %],
    Fact_Employees[Overtime] = "Yes"
)
```

### Low Job Satisfaction Attrition Rate %
```dax
Low Satisfaction Attrition % = CALCULATE(
    [Attrition Rate %],
    Fact_Employees[JobSatisfaction] <= 2
)
```

---

## 3. UI/UX Design System & Color Palette

To make the dashboard look like a real enterprise solution used by executives, avoid default Power BI colors. Use a HSL-harmonized corporate theme:

*   **Primary Corporate Theme Dark**: Slate Blue (`#1E293B`) — Used for header bars, side navigation panels, and visual containers.
*   **Secondary Accent Teal**: Deep Teal (`#0F766E`) / Mint Teal (`#2DD4BF`) — Represents active staff, positive satisfaction, and baseline metrics.
*   **Warning Accent Rose/Coral**: Ruby Rose (`#E11D48`) / Coral (`#F43F5E`) — Specifically reserved for Attrition KPIs and flight-risk alerts.
*   **Background Off-White**: Soft Slate (`#F8FAFC`) — Applied as the main page canvas background.
*   **Typography**: Use **Segoe UI Semibold** for titles, **Segoe UI** for general text, and **DIN** (or bold Arial) for KPI numbers.

---

## 4. Report Pages & Visual Layouts

The report is structured into 4 distinct pages, utilizing standard visual guidelines:

### Page 1: Executive Summary
*Goal: Provide executives with a high-level overview of workforce health.*
*   **Top KPI Section**: 5 visual cards showcasing:
    1.  `Total Employees` (Format: General Number)
    2.  `Active Employees` (Format: General Number)
    3.  `Attrition Count` (Color: Coral Accent)
    4.  `Attrition Rate %` (Format: Percentage, 1 decimal place)
    5.  `Average Salary` (Format: Currency, 0 decimals)
*   **Visuals**:
    -   *Bar Chart (Horizontal)*: Employee Count by Department.
    -   *Donut Chart*: Gender Distribution (Teal/Blue/Purple).
    -   *Column Chart (Stacked)*: Age Group Analysis (e.g., Under 30, 30-39, 40-49, 50+).
    -   *Area Chart*: Salary Distribution (X-axis: Salary bins, Y-axis: Count of Employees).
*   **Slicers**: Department, Gender (Horizontal button list format).

### Page 2: Attrition Analysis
*Goal: Detail why people are leaving and identify hotspots.*
*   **Top KPI Section**: `Attrition Count`, `Attrition Rate %`, `Overtime Attrition Rate %`.
*   **Visuals**:
    -   *100% Stacked Bar Chart*: Attrition by Department (X-axis: Attrition Yes/No, Y-axis: Department).
    -   *Column Chart*: Attrition by Job Role (Sorted descending by Attrition Rate).
    -   *Clustered Column Chart*: Attrition by Overtime (Yes vs No).
    -   *Line & Clustered Column Chart*: Attrition Count and Rate by Age Group.
    -   *Treemap*: Attrition by Education Level.
*   **Insights Panel**: Text box detailing retention recommendations based on satisfaction metrics.
*   **Slicers**: Department, Overtime (Dropdown list format).

### Page 3: Employee Demographics
*Goal: Provide HR recruiters with deep demographic segmentation.*
*   **Visuals**:
    -   *Donut Chart*: Workforce by Marital Status.
    -   *Bar Chart*: Education Level Distribution.
    -   *Scatter Plot*: Age vs. Experience (Tenure), colored by Department.
    -   *Clustered Bar Chart*: Gender Distribution by Department.
    -   *Matrix Grid Table*: Department -> Job Role hierarchical tree showing Total Employees, Average Age, and Average Tenure.
*   **Slicers**: Department, Education, Marital Status.

### Page 4: Performance Analysis
*Goal: Correlate employee performance with compensation and experience.*
*   **Visuals**:
    -   *Donut/Column Chart*: Performance Rating Distribution (1 to 4).
    -   *Scatter Plot*: Salary vs. Years at Company, grouped/colored by Performance Rating.
    -   *Matrix Grid Table*: Job Role by average Salary, average Performance Rating, and average Job Satisfaction.
    -   *Clustered Column Chart*: Average Salary by Department, segregated by Performance Rating.
*   **Slicers**: Department, Performance Rating.

---

## 5. Interactive Features & Polish

To achieve a premium, recruiter-ready finish:
1.  **Page Tooltips**: Set up customized tooltips that show the `Attrition Rate %` and `Job Satisfaction` when hovering over job roles in the bar charts.
2.  **Cross-Filtering**: Configure edit interactions to ensure selecting a department on Page 1 filters all other charts instead of highlighting them.
3.  **Clear All Filters Button**: Implement a bookmark-linked reset button on the top-right of each dashboard header to clear all slicers in one click.
