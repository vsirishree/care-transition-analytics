# ============================================================
# Care Transition Efficiency & Placement Outcome Analytics
# analysis.py (Part 1)
# ============================================================

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ============================================================
# Configuration
# ============================================================

INPUT_FILE = "HHS_Unaccompanied_Alien_Children_Program.csv"

OUTPUT_DIR = "figures"

OUTPUT_DATA = "processed_uac_metrics.csv"

DPI = 300

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# Plot Style
# ============================================================

plt.style.use("default")

COLORS = {
    "blue": "#2563EB",
    "green": "#10B981",
    "orange": "#F59E0B",
    "red": "#EF4444",
    "purple": "#7C3AED",
    "gray": "#6B7280",
    "grid": "#E5E7EB",
    "background": "#F9FAFB",
    "text": "#111827"
}

sns.set_theme(style="whitegrid")

# ============================================================
# Helper Functions
# ============================================================

def style_plot(ax, title, ylabel, xlabel="Date"):
    ax.set_facecolor(COLORS["background"])

    ax.set_title(
        title,
        fontsize=15,
        fontweight="bold",
        color=COLORS["text"]
    )

    ax.set_xlabel(
        xlabel,
        fontsize=11
    )

    ax.set_ylabel(
        ylabel,
        fontsize=11
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %Y")
    )

    ax.xaxis.set_major_locator(
        mdates.MonthLocator(interval=3)
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=45,
        ha="right"
    )


def save_plot(fig, filename):

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUTPUT_DIR, filename),
        dpi=DPI,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# Load Dataset
# ============================================================

print("=" * 60)
print("Loading Dataset...")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(df.head())

# ============================================================
# Data Cleaning
# ============================================================

df.columns = df.columns.str.strip()

df["Date"] = pd.to_datetime(df["Date"])

numeric_columns = [
    "Children apprehended and placed in CBP custody*",
    "Children in CBP custody",
    "Children transferred out of CBP custody",
    "Children in HHS Care",
    "Children discharged from HHS Care"
]

for col in numeric_columns:

    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.sort_values("Date")

df.reset_index(
    drop=True,
    inplace=True
)

print("\nDataset Shape")

print(df.shape)

print("\nMissing Values")

print(df.isnull().sum())

print("\nData Types")

print(df.dtypes)

# ============================================================
# Rename Columns (Easier to Use)
# ============================================================

df.rename(columns={

    "Children apprehended and placed in CBP custody*":
        "Apprehended",

    "Children in CBP custody":
        "CBP",

    "Children transferred out of CBP custody":
        "Transferred",

    "Children in HHS Care":
        "HHS",

    "Children discharged from HHS Care":
        "Discharged"

}, inplace=True)

# ============================================================
# Feature Engineering
# ============================================================

df["Weekday"] = df["Date"].dt.day_name()

df["Month"] = df["Date"].dt.to_period("M")

df["Year"] = df["Date"].dt.year

# ============================================================
# KPI Calculations
# ============================================================

print("\nCalculating KPIs...")

# ------------------------------------------------------------
# Transfer Efficiency Ratio
# ------------------------------------------------------------

df["Transfer_Efficiency"] = np.where(
    df["CBP"] == 0,
    0,
    df["Transferred"] / df["CBP"]
)

df["Transfer_Efficiency_Percent"] = (
    df["Transfer_Efficiency"] * 100
)

# ------------------------------------------------------------
# Discharge Effectiveness Index
# ------------------------------------------------------------

df["Discharge_Effectiveness"] = np.where(
    df["HHS"] == 0,
    0,
    df["Discharged"] / df["HHS"]
)

df["Discharge_Effectiveness_Percent"] = (
    df["Discharge_Effectiveness"] * 100
)

df["Pipeline_Throughput"] = np.where(
    df["Apprehended"] == 0,
    0,
    df["Discharged"] / df["Apprehended"]
)

df["Pipeline_Throughput_Percent"] = (
    df["Pipeline_Throughput"] * 100
)

# ------------------------------------------------------------
# System Backlog
# ------------------------------------------------------------

df["System_Backlog"] = (
    df["CBP"] +
    df["HHS"]
)

# ------------------------------------------------------------
# Backlog Accumulation
# ------------------------------------------------------------

df["Backlog_Accumulation"] = (
    df["Apprehended"] -
    df["Discharged"]
)

# ------------------------------------------------------------
# Net Flow
# ------------------------------------------------------------

df["Net_Flow"] = (
    df["Transferred"] -
    df["Discharged"]
)

# ------------------------------------------------------------
# Outcome Stability Score
# ------------------------------------------------------------

rolling_std = (
    df["Discharge_Effectiveness"]
    .rolling(window=7, min_periods=1)
    .std()
)

df["Outcome_Stability"] = 1 / (1 + rolling_std)

# ============================================================
# Summary Statistics
# ============================================================

print("\nSummary Statistics\n")

summary_columns = [

    "Transfer_Efficiency",

    "Discharge_Effectiveness",

    "Pipeline_Throughput",

    "System_Backlog",

    "Backlog_Accumulation",

    "Net_Flow"

]

print(df[summary_columns].describe())

# ============================================================
# Save Processed Dataset
# ============================================================

df.to_csv(
    OUTPUT_DATA,
    index=False
)

print("\nProcessed dataset saved successfully.")
# ============================================================
# PART 2
# Visualizations
# ============================================================

print("\nGenerating Visualizations...")

# ============================================================
# Graph 1
# Total Children in System
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    df["Date"],
    df["System_Backlog"],
    color=COLORS["blue"],
    linewidth=2.5
)

ax.fill_between(
    df["Date"],
    df["System_Backlog"],
    color=COLORS["blue"],
    alpha=0.15
)

peak = df["System_Backlog"].idxmax()

ax.scatter(
    df.loc[peak,"Date"],
    df.loc[peak,"System_Backlog"],
    color="red",
    s=70
)

ax.annotate(
    f"Peak = {df.loc[peak,'System_Backlog']:,.0f}",
    (
        df.loc[peak,"Date"],
        df.loc[peak,"System_Backlog"]
    ),
    xytext=(15,-20),
    textcoords="offset points"
)

style_plot(
    ax,
    "Total Children in Care Pipeline",
    "Children"
)

save_plot(
    fig,
    "system_backlog.png"
)

# ============================================================
# Graph 2
# Transfer Efficiency
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    df["Date"],
    df["Transfer_Efficiency_Percent"],
    color=COLORS["green"],
    linewidth=2
)

ax.axhline(
    df["Transfer_Efficiency_Percent"].mean(),
    color=COLORS["orange"],
    linestyle="--",
    label="Average"
)

ax.legend()

style_plot(
    ax,
    "Transfer Efficiency Ratio",
    "Percent"
)

save_plot(
    fig,
    "transfer_efficiency.png"
)

# ============================================================
# Graph 3
# Discharge Effectiveness
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    df["Date"],
    df["Discharge_Effectiveness_Percent"],
    color=COLORS["orange"],
    linewidth=2
)

ax.axhline(
    df["Discharge_Effectiveness_Percent"].mean(),
    color=COLORS["blue"],
    linestyle="--",
    label="Average"
)

ax.legend()

style_plot(
    ax,
    "Discharge Effectiveness",
    "Percent"
)

save_plot(
    fig,
    "discharge_effectiveness.png"
)

# ============================================================
# Graph 4
# Pipeline Throughput
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    df["Date"],
    df["Pipeline_Throughput_Percent"],
    color=COLORS["purple"],
    linewidth=2
)

style_plot(
    ax,
    "Pipeline Throughput",
    "Percent"
)

save_plot(
    fig,
    "pipeline_throughput.png"
)

# ============================================================
# Graph 5
# Backlog Accumulation
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

colors = np.where(
    df["Backlog_Accumulation"] > 0,
    COLORS["red"],
    COLORS["green"]
)

ax.bar(
    df["Date"],
    df["Backlog_Accumulation"],
    color=colors,
    width=18
)

ax.axhline(
    0,
    color="black",
    linewidth=1
)

style_plot(
    ax,
    "Backlog Accumulation",
    "Children"
)

save_plot(
    fig,
    "backlog_accumulation.png"
)

# ============================================================
# Graph 6
# Inflow vs Outflow
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    df["Date"],
    df["Apprehended"],
    label="Apprehended",
    color=COLORS["red"],
    linewidth=2
)

ax.plot(
    df["Date"],
    df["Discharged"],
    label="Discharged",
    color=COLORS["green"],
    linewidth=2
)

ax.legend()

style_plot(
    ax,
    "Inflow vs Outflow",
    "Children"
)

save_plot(
    fig,
    "inflow_outflow.png"
)

# ============================================================
# Graph 7
# Net Flow
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

colors = np.where(
    df["Net_Flow"] >= 0,
    COLORS["red"],
    COLORS["green"]
)

ax.bar(
    df["Date"],
    df["Net_Flow"],
    color=colors,
    width=18
)

ax.axhline(
    0,
    color="black"
)

style_plot(
    ax,
    "Net Flow Through Time",
    "Transferred - Discharged"
)

save_plot(
    fig,
    "net_flow.png"
)

# ============================================================
# Graph 8
# Outcome Stability
# ============================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    df["Date"],
    df["Outcome_Stability"],
    color=COLORS["purple"],
    linewidth=2
)

style_plot(
    ax,
    "Outcome Stability Score",
    "Rolling Std Dev"
)

save_plot(
    fig,
    "outcome_stability.png"
)

# ============================================================
# Graph 9
# Correlation Heatmap
# ============================================================

corr = df[
    [
        "Transfer_Efficiency",
        "Discharge_Effectiveness",
        "Pipeline_Throughput",
        "System_Backlog",
        "Backlog_Accumulation",
        "Net_Flow"
    ]
].corr()

fig, ax = plt.subplots(figsize=(8,6))

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    square=True,
    linewidths=0.5
)

ax.set_title(
    "Correlation Matrix",
    fontsize=15,
    fontweight="bold"
)

save_plot(
    fig,
    "correlation_heatmap.png"
)

print("Visualizations Completed.")
# ============================================================
# PART 3
# Trend Analysis, Bottlenecks & Reports
# ============================================================

print("\nRunning Advanced Analysis...")

# ============================================================
# Weekday vs Weekend Analysis
# ============================================================

df["Day_Type"] = np.where(
    df["Date"].dt.dayofweek < 5,
    "Weekday",
    "Weekend"
)

weekday_summary = (
    df.groupby("Day_Type")
    [
        [
            "Transfer_Efficiency",
            "Discharge_Effectiveness",
            "Pipeline_Throughput",
            "System_Backlog"
        ]
    ]
    .mean()
)

weekday_summary.to_csv(
    "weekday_weekend_summary.csv"
)

print("\nWeekday vs Weekend Summary")
print(weekday_summary)

# ============================================================
# Monthly Trend Analysis
# ============================================================

monthly = (
    df
    .groupby("Month")
    [
        [
            "Transfer_Efficiency",
            "Discharge_Effectiveness",
            "Pipeline_Throughput",
            "System_Backlog",
            "Backlog_Accumulation",
            "Net_Flow"
        ]
    ]
    .mean()
)

monthly.to_csv(
    "monthly_summary.csv"
)

print("\nMonthly Summary")
print(monthly.head())

# ============================================================
# Monthly Backlog Plot
# ============================================================

monthly_plot = monthly.copy()

monthly_plot.index = monthly_plot.index.astype(str)

fig, ax = plt.subplots(figsize=(12,5))

ax.bar(
    monthly_plot.index,
    monthly_plot["System_Backlog"],
    color=COLORS["blue"]
)

plt.xticks(rotation=45)

style_plot(
    ax,
    "Monthly Average System Backlog",
    "Children",
    "Month"
)

save_plot(
    fig,
    "monthly_backlog.png"
)

# ============================================================
# Bottleneck Detection
# ============================================================

print("\nDetecting Bottlenecks...")

df["Bottleneck"] = np.where(
    df["Backlog_Accumulation"] > 0,
    True,
    False
)

bottleneck_days = df["Bottleneck"].sum()

print(f"\nTotal Bottleneck Days : {bottleneck_days}")

top_bottlenecks = (

    df.nlargest(
        10,
        "Backlog_Accumulation"
    )

    [
        [
            "Date",
            "Backlog_Accumulation",
            "System_Backlog",
            "Transfer_Efficiency",
            "Discharge_Effectiveness"
        ]
    ]

)

top_bottlenecks.to_csv(
    "top_bottlenecks.csv",
    index=False
)

print("\nTop Bottleneck Days")
print(top_bottlenecks)

# ============================================================
# Best & Worst Performance
# ============================================================

best_transfer = df.loc[
    df["Transfer_Efficiency"].idxmax()
]

worst_transfer = df.loc[
    df["Transfer_Efficiency"].idxmin()
]

best_discharge = df.loc[
    df["Discharge_Effectiveness"].idxmax()
]

worst_discharge = df.loc[
    df["Discharge_Effectiveness"].idxmin()
]

print("\nBest Transfer Day")
print(best_transfer[["Date","Transfer_Efficiency"]])

print("\nWorst Transfer Day")
print(worst_transfer[["Date","Transfer_Efficiency"]])

print("\nBest Discharge Day")
print(best_discharge[["Date","Discharge_Effectiveness"]])

print("\nWorst Discharge Day")
print(worst_discharge[["Date","Discharge_Effectiveness"]])

# ============================================================
# KPI Summary
# ============================================================

stability_score = df["Discharge_Effectiveness"].std()

summary = pd.DataFrame({

    "Metric":[

        "Average Transfer Efficiency",

        "Average Discharge Effectiveness",

        "Average Pipeline Throughput",

        "Average System Backlog",

        "Average Backlog Accumulation",

        "Outcome Stability Score",

        "Total Bottleneck Days"

    ],

    "Value":[

        df["Transfer_Efficiency"].mean(),

        df["Discharge_Effectiveness"].mean(),

        df["Pipeline_Throughput"].mean(),

        df["System_Backlog"].mean(),

        df["Backlog_Accumulation"].mean(),

        stability_score,

        bottleneck_days

    ]

})

summary.to_csv(
    "kpi_summary.csv",
    index=False
)

# ============================================================
# Overall Correlation Report
# ============================================================

corr = df[
    [
        "Transfer_Efficiency",
        "Discharge_Effectiveness",
        "Pipeline_Throughput",
        "System_Backlog",
        "Backlog_Accumulation",
        "Net_Flow"
    ]
].corr()

corr.to_csv(
    "correlation_matrix.csv"
)

# ============================================================
# Final Processed Dataset
# ============================================================

df.to_csv(
    "processed_uac_metrics.csv",
    index=False
)

# ============================================================
# Console Report
# ============================================================

print("\n" + "="*65)
print("CARE TRANSITION EFFICIENCY ANALYSIS COMPLETED")
print("="*65)

print(f"\nRecords Analysed : {len(df):,}")

print(f"\nAverage Transfer Efficiency : {df['Transfer_Efficiency'].mean()*100:.2f}%")

print(f"Average Discharge Effectiveness : {df['Discharge_Effectiveness'].mean()*100:.2f}%")

print(f"Average Pipeline Throughput : {df['Pipeline_Throughput'].mean()*100:.2f}%")

print(f"Average System Backlog : {df['System_Backlog'].mean():,.0f}")

print(f"Average Backlog Accumulation : {df['Backlog_Accumulation'].mean():,.0f}")

print(f"Outcome Stability Score : {stability_score:.4f}")

print(f"Total Bottleneck Days : {bottleneck_days}")

print("\nGenerated Files")

print("✔ processed_uac_metrics.csv")
print("✔ monthly_summary.csv")
print("✔ weekday_weekend_summary.csv")
print("✔ top_bottlenecks.csv")
print("✔ kpi_summary.csv")
print("✔ correlation_matrix.csv")

print("\nGenerated Figures")

print("✔ system_backlog.png")
print("✔ transfer_efficiency.png")
print("✔ discharge_effectiveness.png")
print("✔ pipeline_throughput.png")
print("✔ backlog_accumulation.png")
print("✔ inflow_outflow.png")
print("✔ net_flow.png")
print("✔ outcome_stability.png")
print("✔ monthly_backlog.png")
print("✔ correlation_heatmap.png")

print("\nAnalysis Completed Successfully.")