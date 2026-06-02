#!/usr/bin/env python3
"""
Exploratory Data Analysis & Corporate Visualization Engine
Author: Antigravity AI Pair Programmer
Description: Sets up a custom corporate dark theme in Matplotlib/Seaborn,
             generates the 10 core business-intelligence visualizations,
             saves them to images/, and extracts analytical insights.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define Custom Corporate Dark Palette
BG_COLOR = "#14141C"      # Deep charcoal grey/blue
CARD_COLOR = "#1A1A24"    # Charcoal navy card background
TEXT_COLOR = "#E2E8F0"    # Off-white Slate
GRID_COLOR = "#2A2A38"    # Subtle muted lines
PRIMARY_NEON = "#00D2FF"  # Neon Cyan (Active Customers)
ACCENT_PINK = "#FF007F"   # Sunset Pink/Hot Pink (Churned Customers)
EMERALD_GREEN = "#00F5D4" # Mint Emerald (Low Risk / Loyal)
GOLD_ALERT = "#FFD700"    # Gold Warning (Medium Risk / Value)

def setup_premium_theme():
    """Configures global Matplotlib and Seaborn style aesthetics."""
    plt.style.use("dark_background")
    
    # Configure custom parameters
    plt.rcParams["figure.facecolor"] = BG_COLOR
    plt.rcParams["axes.facecolor"] = CARD_COLOR
    plt.rcParams["axes.edgecolor"] = GRID_COLOR
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.color"] = GRID_COLOR
    plt.rcParams["grid.alpha"] = 0.5
    plt.rcParams["text.color"] = TEXT_COLOR
    plt.rcParams["axes.labelcolor"] = TEXT_COLOR
    plt.rcParams["xtick.color"] = TEXT_COLOR
    plt.rcParams["ytick.color"] = TEXT_COLOR
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Inter", "DejaVu Sans", "Arial"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    
    # Set default palette
    sns.set_palette([PRIMARY_NEON, ACCENT_PINK, EMERALD_GREEN, GOLD_ALERT])

def generate_visualizations():
    # Dynamically resolve directory structures
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    clean_csv_path = os.path.join(project_root, "dataset", "customer_churn_cleaned.csv")
    images_dir = os.path.join(project_root, "images")
    
    os.makedirs(images_dir, exist_ok=True)
    
    print(f"Loading cleaned dataset for visual profiling from: {clean_csv_path}")
    if not os.path.exists(clean_csv_path):
        print(f"Error: Cleaned dataset not found at {clean_csv_path}. Run data_cleaning.py first.")
        return
        
    df = pd.read_csv(clean_csv_path)
    
    # ----------------- Visual 1: Churn Donut Chart -----------------
    print("Generating Visual 1: Churn Percentage Donut Chart...")
    fig, ax = plt.subplots(figsize=(6, 6))
    churn_counts = df["Churn"].value_counts()
    
    wedges, texts, autotexts = ax.pie(
        churn_counts, 
        labels=churn_counts.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=[PRIMARY_NEON, ACCENT_PINK],
        wedgeprops=dict(width=0.4, edgecolor=BG_COLOR, linewidth=3)
    )
    
    for text in texts:
        text.set_color(TEXT_COLOR)
        text.set_fontsize(12)
        text.set_weight("semibold")
    for autotext in autotexts:
        autotext.set_color("#FFFFFF")
        autotext.set_fontsize(13)
        autotext.set_weight("bold")
        
    ax.text(0, 0, "Telecom\nChurn\nAnalysis", ha='center', va='center', fontsize=12, color=TEXT_COLOR, weight="bold")
    ax.set_title("Customer Retention vs Churn Ratio", fontsize=15, pad=15, weight="bold", color=PRIMARY_NEON)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "01_churn_distribution.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 2: Churn by Contract Type Grouped Bar Chart -----------------
    print("Generating Visual 2: Churn by Contract Type...")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Calculate percentages for standardizing labels
    contract_churn = df.groupby(["Contract", "Churn"]).size().unstack(fill_value=0)
    contract_churn_pct = contract_churn.div(contract_churn.sum(axis=1), axis=0) * 100
    
    ax = contract_churn_pct.plot(kind="bar", stacked=False, color=[PRIMARY_NEON, ACCENT_PINK], ax=ax, width=0.6)
    
    # Add values on top of bars
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f"{height:.1f}%", 
                    (p.get_x() + p.get_width() / 2., height + 1.5), 
                    ha='center', va='center', 
                    xytext=(0, 5), 
                    textcoords='offset points', 
                    fontsize=10, color=TEXT_COLOR, weight="bold")
                    
    ax.set_title("Churn Rate by Contract Commitment Type", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Contract Agreement", fontsize=12)
    ax.set_ylabel("Percentage of Segment (%)", fontsize=12)
    ax.set_xticklabels(contract_churn_pct.index, rotation=0, weight="semibold")
    ax.legend(title="Churned?", labels=["Retained (No)", "Churned (Yes)"], frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "02_contract_churn.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 3: Monthly Charges KDE/Density Plot -----------------
    print("Generating Visual 3: Monthly Charges Density...")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.kdeplot(df[df["Churn"] == "No"]["MonthlyCharges"], fill=True, label="Retained (No)", color=PRIMARY_NEON, alpha=0.3, ax=ax, linewidth=2)
    sns.kdeplot(df[df["Churn"] == "Yes"]["MonthlyCharges"], fill=True, label="Churned (Yes)", color=ACCENT_PINK, alpha=0.3, ax=ax, linewidth=2)
    
    ax.set_title("Monthly Billing Distribution vs Customer Churn", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Monthly Charges ($)", fontsize=12)
    ax.set_ylabel("Probability Density", fontsize=12)
    ax.legend(frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "03_monthly_charges_distribution.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 4: Tenure Distribution / Decay Curve -----------------
    print("Generating Visual 4: Tenure Decay Curve...")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.histplot(
        data=df, 
        x="tenure", 
        hue="Churn", 
        multiple="stack", 
        bins=30, 
        palette=[PRIMARY_NEON, ACCENT_PINK], 
        edgecolor=BG_COLOR, 
        alpha=0.85, 
        ax=ax
    )
    
    ax.set_title("Customer Lifecycle Cohort Decay Curve (Tenure)", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Tenure (Months in Service)", fontsize=12)
    ax.set_ylabel("Subscriber Count", fontsize=12)
    ax.legend(labels=["Churned (Yes)", "Retained (No)"], frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "04_tenure_distribution.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 5: Churn by Payment Method -----------------
    print("Generating Visual 5: Churn by Payment Method...")
    fig, ax = plt.subplots(figsize=(9, 5))
    
    payment_churn = df.groupby(["PaymentMethod", "Churn"]).size().unstack(fill_value=0)
    payment_churn_pct = payment_churn.div(payment_churn.sum(axis=1), axis=0) * 100
    
    ax = payment_churn_pct.plot(kind="barh", stacked=False, color=[PRIMARY_NEON, ACCENT_PINK], ax=ax, width=0.6)
    
    # Value annotations on horizontal bars
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(f"{width:.1f}%", 
                        (width + 1.5, p.get_y() + p.get_height() / 2.), 
                        ha='left', va='center', 
                        xytext=(5, 0), 
                        textcoords='offset points', 
                        fontsize=9, color=TEXT_COLOR, weight="bold")
                        
    ax.set_title("Churn Susceptibility by Payment Methods", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Percentage of Payment Segment (%)", fontsize=12)
    ax.set_ylabel("Billing Gateway", fontsize=12)
    ax.set_yticklabels(payment_churn_pct.index, fontsize=10, weight="semibold")
    ax.legend(title="Churned?", labels=["Retained (No)", "Churned (Yes)"], loc="lower right", frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    ax.set_xlim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "05_payment_method_churn.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 6: Internet Service Type Retention Countplot -----------------
    print("Generating Visual 6: Internet Service Churn Patterns...")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    internet_churn = df.groupby(["InternetService", "Churn"]).size().unstack(fill_value=0)
    internet_churn_pct = internet_churn.div(internet_churn.sum(axis=1), axis=0) * 100
    
    ax = internet_churn_pct.plot(kind="bar", stacked=False, color=[PRIMARY_NEON, ACCENT_PINK], ax=ax, width=0.6)
    
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f"{height:.1f}%", 
                    (p.get_x() + p.get_width() / 2., height + 1.5), 
                    ha='center', va='center', 
                    xytext=(0, 5), 
                    textcoords='offset points', 
                    fontsize=10, color=TEXT_COLOR, weight="bold")
                    
    ax.set_title("Churn Rate by Network Gateway Technology", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Internet Service Type", fontsize=12)
    ax.set_ylabel("Percentage of Technology Cohort (%)", fontsize=12)
    ax.set_xticklabels(internet_churn_pct.index, rotation=0, weight="semibold")
    ax.legend(title="Churned?", labels=["Retained (No)", "Churned (Yes)"], frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "06_internet_service_churn.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 7: Senior Citizen Churn Rate -----------------
    print("Generating Visual 7: Senior Citizen Churn...")
    fig, ax = plt.subplots(figsize=(7, 5))
    
    senior_churn = df.groupby(["SeniorCitizen", "Churn"]).size().unstack(fill_value=0)
    senior_churn_pct = senior_churn.div(senior_churn.sum(axis=1), axis=0) * 100
    
    ax = senior_churn_pct.plot(kind="bar", stacked=False, color=[PRIMARY_NEON, ACCENT_PINK], ax=ax, width=0.5)
    
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f"{height:.1f}%", 
                    (p.get_x() + p.get_width() / 2., height + 1.5), 
                    ha='center', va='center', 
                    xytext=(0, 5), 
                    textcoords='offset points', 
                    fontsize=10, color=TEXT_COLOR, weight="bold")
                    
    ax.set_title("Subscriber Attrition: Senior Citizens vs General Population", fontsize=13, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Senior Citizen Designation?", fontsize=12)
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_xticklabels(["Non-Seniors (No)", "Seniors (Yes)"], rotation=0, weight="semibold")
    ax.legend(title="Churned?", labels=["Retained (No)", "Churned (Yes)"], frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "07_senior_citizen_churn.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 8: High/Low Value Customer Segment Scatter -----------------
    print("Generating Visual 8: High/Low Value Segments Scatter...")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    
    # Subsample to avoid visual over-crowding in presentation
    sample_df = df.sample(n=1200, random_state=42) if len(df) > 1200 else df
    
    sns.scatterplot(
        data=sample_df, 
        x="tenure", 
        y="MonthlyCharges", 
        hue="Churn", 
        palette=[PRIMARY_NEON, ACCENT_PINK], 
        alpha=0.6, 
        edgecolor=GRID_COLOR, 
        linewidth=0.5,
        ax=ax
    )
    
    ax.set_title("Customer Segmentation Landscape (Tenure vs. Monthly Charges)", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Tenure (Months of Brand Engagement)", fontsize=12)
    ax.set_ylabel("Monthly charges ($ / Month)", fontsize=12)
    ax.legend(title="Subscriber Status", labels=["Retained (No)", "Churned (Yes)"], frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "08_customer_segmentation_scatter.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 9: Correlation Matrix Heatmap -----------------
    print("Generating Visual 9: Correlation Matrix Heatmap...")
    fig, ax = plt.subplots(figsize=(8, 6.5))
    
    # Map target feature to numeric
    corr_df = df.copy()
    corr_df["ChurnNumeric"] = corr_df["Churn"].map({"Yes": 1, "No": 0})
    corr_df["SeniorNumeric"] = corr_df["SeniorCitizen"].map({"Yes": 1, "No": 0})
    corr_df["PartnerNumeric"] = corr_df["Partner"].map({"Yes": 1, "No": 0})
    corr_df["DependentsNumeric"] = corr_df["Dependents"].map({"Yes": 1, "No": 0})
    
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges", "ChurnNumeric", "SeniorNumeric", "PartnerNumeric", "DependentsNumeric"]
    corr_matrix = corr_df[numeric_cols].corr()
    
    # Custom Diverging Palette
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        fmt=".2f", 
        cmap=cmap, 
        vmin=-1, 
        vmax=1, 
        center=0, 
        square=True, 
        linewidths=1, 
        linecolor=BG_COLOR, 
        cbar_kws={"shrink": .8},
        ax=ax
    )
    
    # Clean up labels
    labels = ["Tenure", "Monthly Charges", "Total Charges", "Churn Rate", "Senior Citizen", "Has Partner", "Has Dependents"]
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10, weight="semibold")
    ax.set_yticklabels(labels, rotation=0, fontsize=10, weight="semibold")
    
    ax.set_title("Telecom Retention Correlative Grid Map", fontsize=14, pad=20, weight="bold", color=PRIMARY_NEON)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "09_correlation_heatmap.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    # ----------------- Visual 10: Tenure vs Monthly Charges Boxplot -----------------
    print("Generating Visual 10: Billing vs Tenure Churn Segments...")
    fig, ax = plt.subplots(figsize=(8.5, 5))
    
    sns.boxplot(
        data=df, 
        x="Contract", 
        y="MonthlyCharges", 
        hue="Churn", 
        palette=[PRIMARY_NEON, ACCENT_PINK],
        ax=ax,
        linewidth=1.5
    )
    
    ax.set_title("Contract Pricing Thresholds vs Customer Loyalty", fontsize=14, pad=15, weight="bold", color=PRIMARY_NEON)
    ax.set_xlabel("Contract Agreement Class", fontsize=12)
    ax.set_ylabel("Monthly billing ($ / Month)", fontsize=12)
    ax.legend(title="Subscriber Status", labels=["Retained (No)", "Churned (Yes)"], frameon=True, facecolor=CARD_COLOR, edgecolor=GRID_COLOR)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "10_contract_charges_boxplot.png"), dpi=200, facecolor=BG_COLOR)
    plt.close()
    
    print("\nVisual EDA Engine completed processing successfully!")
    print(f"All 10 professional dark-mode graphics exported to: {images_dir}")
    
    # Automated Feature Impact Analysis to screen output
    churn_yes = df[df["Churn"] == "Yes"]
    churn_no = df[df["Churn"] == "No"]
    
    print("\n==================================================")
    print("AUTOMATED BUSINESS INTELLIGENCE INSIGHTS ENGINE")
    print("==================================================")
    print(f"1. RETENTION DECAY: Mean tenure for churned subscribers is {churn_yes['tenure'].mean():.1f} months, vs {churn_no['tenure'].mean():.1f} months for retained.")
    print(f"2. BILLING STRESS: Mean MonthlyCharges for churned subscribers is ${churn_yes['MonthlyCharges'].mean():.2f}/mo, vs ${churn_no['MonthlyCharges'].mean():.2f}/mo for retained.")
    print(f"3. CONTRACT LEAKAGE: Month-to-month contracts have an exceptionally high churn rate of {contract_churn_pct.loc['Month-to-month', 'Yes']:.1f}%.")
    print(f"4. PAYMENTS GATEWAY: Electronic Check payment represents the highest attrition portal with {payment_churn_pct.loc['Electronic check', 'Yes']:.1f}% churn.")
    print(f"5. INFRASTRUCTURE FRICTION: Fiber optic subscribers churn at {internet_churn_pct.loc['Fiber optic', 'Yes']:.1f}%, indicating massive pricing dissatisfaction or local service degradation.")
    print("==================================================\n")

if __name__ == "__main__":
    setup_premium_theme()
    generate_visualizations()
