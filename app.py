# ============================================================
# Care Transition Efficiency & Placement Outcome Analytics
# app.py (Part 1)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Care Transition Analytics",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# Title
# ============================================================

st.title("📊 Care Transition Efficiency & Placement Outcome Analytics")

st.markdown("""
This dashboard evaluates the efficiency of the Unaccompanied Alien Children (UAC)
care pipeline from **CBP Custody → HHS Care → Sponsor Placement**.

Use the filters on the left to explore different time periods and monitor
system performance.
""")

# ============================================================
# Load Data
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("processed_uac_metrics.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ============================================================
# Sidebar
# ============================================================

st.sidebar.header("Dashboard Controls")

start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Date"].max()
)

filtered = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
]

st.sidebar.markdown("---")

metric_choice = st.sidebar.selectbox(

    "Select KPI",

    [

        "Transfer_Efficiency",

        "Discharge_Effectiveness",

        "Pipeline_Throughput",

        "System_Backlog",

        "Backlog_Accumulation",

        "Net_Flow"

    ]

)

# ============================================================
# KPI Cards
# ============================================================

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Transfer Efficiency",

        f"{filtered['Transfer_Efficiency'].mean()*100:.2f}%"

    )

with col2:

    st.metric(

        "Discharge Effectiveness",

        f"{filtered['Discharge_Effectiveness'].mean()*100:.2f}%"

    )

with col3:

    st.metric(

        "Pipeline Throughput",

        f"{filtered['Pipeline_Throughput'].mean()*100:.2f}%"

    )

col4, col5, col6 = st.columns(3)

with col4:

    st.metric(

        "Average System Backlog",

        f"{filtered['System_Backlog'].mean():,.0f}"

    )

with col5:

    st.metric(

        "Average Net Flow",

        f"{filtered['Net_Flow'].mean():,.0f}"

    )

with col6:

    st.metric(

        "Backlog Accumulation",

        f"{filtered['Backlog_Accumulation'].mean():,.0f}"

    )

# ============================================================
# Threshold Alerts
# ============================================================

st.markdown("---")
st.markdown("---")

st.subheader("🏆 Best & Worst Performance")

best_transfer = filtered.loc[
    filtered["Transfer_Efficiency"].idxmax()
]

worst_transfer = filtered.loc[
    filtered["Transfer_Efficiency"].idxmin()
]

col1, col2 = st.columns(2)

with col1:
    st.success(
        f"Best Transfer Efficiency\n\n{best_transfer['Date'].date()} : {best_transfer['Transfer_Efficiency']*100:.1f}%"
    )

with col2:
    st.error(
        f"Worst Transfer Efficiency\n\n{worst_transfer['Date'].date()} : {worst_transfer['Transfer_Efficiency']*100:.1f}%"
    )
st.subheader("System Status")

transfer = filtered["Transfer_Efficiency"].mean()

discharge = filtered["Discharge_Effectiveness"].mean()

backlog = filtered["Backlog_Accumulation"].mean()

if transfer < 0.60:

    st.error(
        "🚨 Transfer Efficiency is critically low."
    )

elif transfer < 0.80:

    st.warning(
        "⚠ Transfer Efficiency is below target."
    )

else:

    st.success(
        "✅ Transfer Efficiency is healthy."
    )

if discharge < 0.60:

    st.error(
        "🚨 Sponsor placement performance is low."
    )

elif discharge < 0.80:

    st.warning(
        "⚠ Discharge Effectiveness needs improvement."
    )

else:

    st.success(
        "✅ Sponsor placement is performing well."
    )

if backlog > 0:

    st.warning(
        "⚠ Inflow exceeds successful exits. Backlog is increasing."
    )

else:

    st.success(
        "✅ Backlog accumulation is under control."
    )

st.markdown("---")

# ============================================================
# Care Pipeline Diagram
# ============================================================

st.subheader("Care Pipeline")

st.markdown("""
```text
Children Apprehended
          │
          ▼
 CBP Custody
          │
          ▼
Transferred to HHS
          │
          ▼
 HHS Care
          │
          ▼
Sponsor Placement / Discharge""")
# ============================================================
# PART 2
# Interactive Charts
# ============================================================

st.subheader("📈 KPI Trend Analysis")

fig = px.line(
    filtered,
    x="Date",
    y=metric_choice,
    title=f"{metric_choice.replace('_',' ')} Over Time",
    markers=True
)

fig.update_layout(
    template="plotly_white",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# ============================================================
# Inflow vs Outflow
# ============================================================

st.subheader("📊 Daily Inflow vs Outflow")

fig = px.line(

    filtered,

    x="Date",

    y=["Apprehended", "Discharged"],

    labels={
        "value":"Children",
        "variable":"Metric"
    },

    title="Daily Inflow and Successful Exits"

)

fig.update_layout(
    template="plotly_white",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# ============================================================
# Transfer Efficiency
# ============================================================

st.subheader("🚚 Transfer Efficiency")

fig = px.line(

    filtered,

    x="Date",

    y="Transfer_Efficiency",

    markers=True,

    title="Transfer Efficiency Ratio"

)

fig.update_layout(
    yaxis_tickformat=".0%",
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ============================================================
# Discharge Effectiveness
# ============================================================

st.subheader("🏠 Discharge Effectiveness")

fig = px.line(

    filtered,

    x="Date",

    y="Discharge_Effectiveness",

    markers=True,

    title="Discharge Effectiveness"

)

fig.update_layout(
    yaxis_tickformat=".0%",
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# ============================================================
# Pipeline Throughput
# ============================================================

st.subheader("⚡ Pipeline Throughput")

fig = px.line(

    filtered,

    x="Date",

    y="Pipeline_Throughput",

    markers=True,

    title="Pipeline Throughput"

)

fig.update_layout(
    yaxis_tickformat=".0%",
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# ============================================================
# System Backlog
# ============================================================

st.subheader("📦 System Backlog")

fig = px.area(

    filtered,

    x="Date",

    y="System_Backlog",

    title="Children Currently in Care Pipeline"

)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# ============================================================
# Backlog Accumulation
# ============================================================

st.subheader("📈 Backlog Accumulation")

fig = px.bar(

    filtered,

    x="Date",

    y="Backlog_Accumulation",

    color="Backlog_Accumulation",

    color_continuous_scale="RdYlGn_r",

    title="Daily Backlog Accumulation"

)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

st.subheader("📈 Outcome Stability")

fig = px.line(
    filtered,
    x="Date",
    y="Outcome_Stability",
    markers=True,
    title="Outcome Stability Score"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# Net Flow
# ============================================================

st.subheader("🔄 Net Flow")

fig = px.bar(

    filtered,

    x="Date",

    y="Net_Flow",

    color="Net_Flow",

    color_continuous_scale="RdYlGn",

    title="Net Flow (Transferred - Discharged)"

)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
st.markdown("---")

st.subheader("🚨 Top 10 Bottleneck Days")

top10 = (
    filtered
    .sort_values(
        "Backlog_Accumulation",
        ascending=False
    )
    .head(10)
)
st.markdown("---")

st.subheader("Correlation Heatmap")

corr = filtered[
    [
        "Transfer_Efficiency",
        "Discharge_Effectiveness",
        "Pipeline_Throughput",
        "System_Backlog",
        "Backlog_Accumulation",
        "Net_Flow"
    ]
].corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    title="Correlation Matrix"
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    top10[
        [
            "Date",
            "Backlog_Accumulation",
            "System_Backlog",
            "Transfer_Efficiency",
            "Discharge_Effectiveness"
        ]
    ]
)

st.subheader("📅 Weekday vs Weekend Comparison")

weekday = (
    filtered
    .groupby("Day_Type")[
        [
            "Transfer_Efficiency",
            "Discharge_Effectiveness",
            "Pipeline_Throughput"
        ]
    ]
    .mean()
    .reset_index()
)

fig = px.bar(
    weekday,
    x="Day_Type",
    y=[
        "Transfer_Efficiency",
        "Discharge_Effectiveness",
        "Pipeline_Throughput"
    ],
    barmode="group",
    title="Weekday vs Weekend Performance"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("📅 Monthly Trends")

monthly = (
    filtered
    .groupby("Month")[
        [
            "Transfer_Efficiency",
            "Discharge_Effectiveness",
            "Pipeline_Throughput"
        ]
    ]
    .mean()
    .reset_index()
)

monthly["Month"] = monthly["Month"].astype(str)

fig = px.line(
    monthly,
    x="Month",
    y=[
        "Transfer_Efficiency",
        "Discharge_Effectiveness",
        "Pipeline_Throughput"
    ],
    markers=True
)

st.plotly_chart(fig, use_container_width=True)