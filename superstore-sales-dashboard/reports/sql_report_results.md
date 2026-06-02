# Executive Relational SQL Analytics Report
Generated automatically by the Superstore Sales data pipeline.
**Date Generated:** 2026-05-20 20:38:51

---

## Executive Summary Metrics
*Source SQL script: [01_kpi_summary.sql](../sql/01_kpi_summary.sql)*

| total_sales | total_profit | total_orders | profit_margin_percent | total_customers |
| --- | --- | --- | --- | --- |
| 789447.07 | 111060.94 | 4997.0 | 14.07 | 447.0 |


---

## Monthly Sales & MoM Growth Trends
*Source SQL script: [02_monthly_sales_trend.sql](../sql/02_monthly_sales_trend.sql)*

| order_month | monthly_sales | monthly_profit | monthly_orders | previous_month_sales | mom_growth_percent |
| --- | --- | --- | --- | --- | --- |
| 2022-01 | 12927.38 | 1480.16 | 84 | nan | nan |
| 2022-02 | 14012.74 | 1995.34 | 103 | 12927.38 | 8.4 |
| 2022-03 | 15027.65 | 1468.55 | 101 | 14012.74 | 7.24 |
| 2022-04 | 16892.71 | 2723.46 | 84 | 15027.65 | 12.41 |
| 2022-05 | 11479.51 | 1202.34 | 84 | 16892.71 | -32.04 |
| 2022-06 | 11735.45 | 1480.77 | 95 | 11479.51 | 2.23 |
| 2022-07 | 15679.72 | 2167.67 | 108 | 11735.45 | 33.61 |
| 2022-08 | 15807.72 | 2537.41 | 92 | 15679.72 | 0.82 |
| 2022-09 | 15076.69 | 2093.26 | 90 | 15807.72 | -4.62 |
| 2022-10 | 19327.34 | 3859.17 | 87 | 15076.69 | 28.19 |
| 2022-11 | 25406.38 | 4314.42 | 155 | 19327.34 | 31.45 |
| 2022-12 | 19223.09 | 1776.08 | 138 | 25406.38 | -24.34 |
| 2023-01 | 19662.35 | 3401.44 | 104 | 19223.09 | 2.29 |
| 2023-02 | 24731.61 | 4702.58 | 85 | 19662.35 | 25.78 |
| 2023-03 | 15375.94 | 2141.09 | 108 | 24731.61 | -37.83 |
| 2023-04 | 19584.64 | 1778.74 | 100 | 15375.94 | 27.37 |
| 2023-05 | 16790.24 | 2792.25 | 88 | 19584.64 | -14.27 |
| 2023-06 | 12572.78 | 1686.0 | 96 | 16790.24 | -25.12 |
| 2023-07 | 18938.22 | 3633.91 | 112 | 12572.78 | 50.63 |
| 2023-08 | 16146.3 | 1887.68 | 96 | 18938.22 | -14.74 |
| 2023-09 | 15524.51 | 2588.03 | 97 | 16146.3 | -3.85 |
| 2023-10 | 15153.64 | 3224.54 | 101 | 15524.51 | -2.39 |
| 2023-11 | 30447.71 | 3824.27 | 163 | 15153.64 | 100.93 |
| 2023-12 | 19045.19 | 2393.92 | 152 | 30447.71 | -37.45 |
| 2024-01 | 14482.57 | 2161.99 | 103 | 19045.19 | -23.96 |
| 2024-02 | 6898.77 | 524.6 | 79 | 14482.57 | -52.37 |
| 2024-03 | 11170.2 | 1662.25 | 99 | 6898.77 | 61.92 |
| 2024-04 | 10730.05 | 800.87 | 88 | 11170.2 | -3.94 |
| 2024-05 | 15156.99 | 1984.99 | 83 | 10730.05 | 41.26 |
| 2024-06 | 16939.47 | 2326.26 | 109 | 15156.99 | 11.76 |
| 2024-07 | 8768.87 | -140.45 | 89 | 16939.47 | -48.23 |
| 2024-08 | 16156.41 | 4022.78 | 90 | 8768.87 | 84.25 |
| 2024-09 | 10108.86 | 1965.9 | 77 | 16156.41 | -37.43 |
| 2024-10 | 16773.11 | 1258.03 | 102 | 10108.86 | 65.92 |
| 2024-11 | 24300.24 | 3833.75 | 160 | 16773.11 | 44.88 |
| 2024-12 | 24264.65 | 3665.52 | 144 | 24300.24 | -0.15 |
| 2025-01 | 10129.43 | 1743.58 | 99 | 24264.65 | -58.25 |
| 2025-02 | 22344.55 | 5576.6 | 101 | 10129.43 | 120.59 |
| 2025-03 | 13176.65 | 891.73 | 86 | 22344.55 | -41.03 |
| 2025-04 | 10720.2 | 687.04 | 102 | 13176.65 | -18.64 |
| 2025-05 | 14997.23 | 1074.3 | 93 | 10720.2 | 39.9 |
| 2025-06 | 9326.17 | 617.28 | 82 | 14997.23 | -37.81 |
| 2025-07 | 20091.79 | 3295.57 | 109 | 9326.17 | 115.43 |
| 2025-08 | 17764.47 | 2568.82 | 96 | 20091.79 | -11.58 |
| 2025-09 | 12244.63 | 25.42 | 93 | 17764.47 | -31.07 |
| 2025-10 | 9462.34 | 1049.9 | 81 | 12244.63 | -22.72 |
| 2025-11 | 23496.26 | 2866.26 | 150 | 9462.34 | 148.31 |
| 2025-12 | 33373.65 | 5444.87 | 162 | 23496.26 | 42.04 |


---

## Category & Sub-Category Sales & Margin Breakdown
*Source SQL script: [03_category_analysis.sql](../sql/03_category_analysis.sql)*

| category | sub_category | total_sales | total_quantity | avg_discount_percent | total_profit | profit_margin_percent |
| --- | --- | --- | --- | --- | --- | --- |
| Furniture | Tables | 62693.35 | 1774 | 24.48 | -17167.55 | -27.38 |
| Furniture | Bookcases | 32934.26 | 1612 | 25.71 | -7707.56 | -23.4 |
| Furniture | Chairs | 24861.72 | 1629 | 25.07 | -4364.03 | -17.55 |
| Furniture | Furnishings | 7964.12 | 1801 | 26.13 | -965.64 | -12.12 |
| Office Supplies | Appliances | 20746.0 | 1648 | 15.38 | 1105.73 | 5.33 |
| Office Supplies | Storage | 14750.27 | 1584 | 14.53 | 82.16 | 0.56 |
| Office Supplies | Supplies | 9762.02 | 1547 | 13.26 | -347.01 | -3.55 |
| Office Supplies | Binders | 5653.33 | 1720 | 13.88 | 1130.71 | 20.0 |
| Office Supplies | Paper | 3369.01 | 1579 | 14.42 | 880.05 | 26.12 |
| Office Supplies | Art | 2181.28 | 1554 | 13.99 | 301.56 | 13.82 |
| Office Supplies | Envelopes | 1814.66 | 1681 | 14.69 | 348.73 | 19.22 |
| Office Supplies | Labels | 1652.38 | 1819 | 14.66 | 421.2 | 25.49 |
| Office Supplies | Fasteners | 1044.75 | 1553 | 13.96 | 138.05 | 13.21 |
| Technology | Copiers | 357837.89 | 1828 | 13.64 | 116150.66 | 32.46 |
| Technology | Machines | 157804.09 | 1393 | 12.85 | 8427.37 | 5.34 |
| Technology | Phones | 70222.71 | 1639 | 13.48 | 10568.57 | 15.05 |
| Technology | Accessories | 14155.23 | 1570 | 14.48 | 2057.94 | 14.54 |


---

## Regional Market Volume & Profitability
*Source SQL script: [04_region_wise_analysis.sql](../sql/04_region_wise_analysis.sql)*

| region | total_orders | total_sales | total_profit | profit_margin_percent |
| --- | --- | --- | --- | --- |
| West | 1620 | 257839.64 | 37209.07 | 14.43 |
| East | 1379 | 211755.77 | 30081.86 | 14.21 |
| Central | 1118 | 178433.22 | 25560.11 | 14.32 |
| South | 883 | 141418.44 | 18209.9 | 12.88 |


---

## Demographic Segmentation & Average Order Value (AOV)
*Source SQL script: [05_customer_segmentation.sql](../sql/05_customer_segmentation.sql)*

| segment | customer_count | order_count | total_sales | total_profit | avg_order_value | profit_margin_percent |
| --- | --- | --- | --- | --- | --- | --- |
| Home Office | 150 | 1696 | 274210.5 | 38996.24 | 161.68 | 14.22 |
| Corporate | 150 | 1664 | 262477.68 | 36473.78 | 157.74 | 13.9 |
| Consumer | 150 | 1639 | 252758.89 | 35590.92 | 154.22 | 14.08 |


---

## Product Performance: Top 10 Profitable vs Bottom 5 Unprofitable SKUs
*Source SQL script: [06_top_bottom_products.sql](../sql/06_top_bottom_products.sql)*

| sku_classification | product_name | category | total_sales | total_quantity | total_profit | avg_discount_percent |
| --- | --- | --- | --- | --- | --- | --- |
| TOP PROFITABLE | Copiers SKU-018 (Premium Quality) | Technology | 16793.68 | 79 | 6662.22 | 6.25 |
| TOP PROFITABLE | Copiers SKU-010 (Premium Quality) | Technology | 18458.81 | 95 | 5990.2 | 15.0 |
| TOP PROFITABLE | Copiers SKU-022 (Premium Quality) | Technology | 18313.31 | 93 | 5979.65 | 16.0 |
| TOP PROFITABLE | Copiers SKU-026 (Premium Quality) | Technology | 15448.93 | 68 | 5716.48 | 10.0 |
| TOP PROFITABLE | Copiers SKU-013 (Premium Quality) | Technology | 18089.48 | 83 | 5654.11 | 14.29 |
| TOP PROFITABLE | Copiers SKU-003 (Premium Quality) | Technology | 13712.94 | 67 | 4651.86 | 14.55 |
| TOP PROFITABLE | Copiers SKU-017 (Premium Quality) | Technology | 18392.65 | 99 | 4646.43 | 15.88 |
| TOP PROFITABLE | Copiers SKU-002 (Premium Quality) | Technology | 14225.45 | 66 | 4628.14 | 13.64 |
| TOP PROFITABLE | Copiers SKU-001 (Premium Quality) | Technology | 14632.99 | 76 | 4389.4 | 19.23 |
| TOP PROFITABLE | Copiers SKU-021 (Premium Quality) | Technology | 14221.94 | 74 | 4285.86 | 17.5 |
| BOTTOM UNPROFITABLE | Tables SKU-005 (Premium Quality) | Furniture | 2575.36 | 84 | -1187.75 | 32.73 |
| BOTTOM UNPROFITABLE | Tables SKU-007 (Premium Quality) | Furniture | 1869.88 | 57 | -1016.56 | 33.0 |
| BOTTOM UNPROFITABLE | Tables SKU-029 (Premium Quality) | Furniture | 2196.53 | 88 | -966.05 | 29.33 |
| BOTTOM UNPROFITABLE | Tables SKU-025 (Premium Quality) | Furniture | 2333.23 | 73 | -951.49 | 27.5 |
| BOTTOM UNPROFITABLE | Tables SKU-008 (Premium Quality) | Furniture | 2224.08 | 62 | -884.37 | 30.83 |


---

## Impact Analysis of Promotional Discount Levels on Profit Margins
*Source SQL script: [07_profitability_analysis.sql](../sql/07_profitability_analysis.sql)*

| discount_rate | order_line_count | total_sales | total_profit | avg_profit_per_line | profit_margin_percent |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1672.0 | 218409.34 | 69925.24 | 41.82 | 32.02 |
| 0.1 | 763.0 | 111603.42 | 27281.73 | 35.76 | 24.45 |
| 0.2 | 1174.0 | 236854.89 | 40273.15 | 34.3 | 17.0 |
| 0.3 | 590.0 | 122368.34 | 3795.96 | 6.43 | 3.1 |
| 0.4 | 588.0 | 86208.36 | -16324.37 | -27.76 | -18.94 |
| 0.5 | 101.0 | 7374.54 | -5719.65 | -56.63 | -77.56 |
| 0.6 | 112.0 | 6628.18 | -8171.12 | -72.96 | -123.28 |


---
