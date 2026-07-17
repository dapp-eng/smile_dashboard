import streamlit as st
import pandas as pd
import plotly.express as px

from utils.layout import (
    page_header, metric_strip, chart_panel,
    filter_bar, table_panel, panel, card_grid, section_divider,
)
from utils.theme import COLORS, apply_style
from utils import charts
from utils.queries import get_data_quality_master

# Page setup
page_header(
    "Data Quality",
    "BT-08 — Data Sync & Integrity Checks",
    page_title="Data Quality | SMILE",
)
apply_style()

# Load Data
df_master = get_data_quality_master()

if df_master.empty:
    st.info("No data available for sync evaluation.")
    st.stop()

# Row 2: Earliest / Latest Sync Date
earliest_sync = df_master["sync_date"].min()
latest_sync = df_master["sync_date"].max()

c1, c2 = card_grid(2)
with c1:
    with panel():
        st.markdown(f"<div style='text-align: center; color: var(--text-color); font-size: 0.9rem;'>Earliest Sync Date</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 600; color: var(--primary-color);'>{earliest_sync.strftime('%d %B %Y')}</div>", unsafe_allow_html=True)
with c2:
    with panel():
        st.markdown(f"<div style='text-align: center; color: var(--text-color); font-size: 0.9rem;'>Latest Sync Date</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 600; color: var(--primary-color);'>{latest_sync.strftime('%d %B %Y')}</div>", unsafe_allow_html=True)

section_divider()

# Row 3: Metric Strip
total_students = len(df_master)
pct_critical = round(len(df_master[df_master["staleness"] == "Critical"]) / total_students * 100, 1)
pct_mismatch = round(df_master["has_mismatch"].sum() / total_students * 100, 1)

metric_strip([
    {
        "label": "Total Students",
        "value": f"{total_students:,}",
    },
    {
        "label": "Critical Sync Data (>179d)",
        "value": f"{pct_critical}%",
        "sentiment": "success" if pct_critical < 10 else "danger",
    },
    {
        "label": "Mismatched Data",
        "value": f"{pct_mismatch}%",
        "sentiment": "success" if pct_mismatch < 5 else "warning",
    }
])

section_divider()

STALENESS_COLORS = {
    "Safe": COLORS["success"],
    "Stale": COLORS["warning"],
    "Critical": COLORS["danger"]
}

# Row 4: Histogram and Pie Chart
col_hist, col_pie = st.columns([3, 2], gap="medium")

with col_hist:
    with chart_panel("Days Since Last Sync", height=380):
        fig_hist = charts.histogram(
            df_master, 
            x="days_since_sync", 
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            height=300
        )
        fig_hist.update_traces(xbins_size=30, marker_line_color="var(--background-color)", marker_line_width=0.5)
        fig_hist.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Days Since Sync",
            yaxis_title="Count of Students",
            legend_title="",
            bargap=0.02 
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with col_pie:
    with chart_panel("Staleness Distribution", height=380):
        df_pie = df_master["staleness"].value_counts().reset_index()
        df_pie.columns = ["staleness", "count"]
        
        fig_pie = charts.pie(
            df_pie,
            names="staleness",
            values="count",
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            hole=0.4,
            height=300
        )
        fig_pie.update_traces(textinfo="label+percent", textposition="inside")
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# Row 5: Line chart for monthly sync
with chart_panel("Monthly Sync Volume", height=380):
    df_sync_time = df_master.copy()
    df_sync_time["sync_month"] = df_sync_time["sync_date"].dt.to_period("M").astype(str)
    monthly_counts = df_sync_time.groupby("sync_month").size().reset_index(name="syncs")
    
    fig_line = charts.line(
        monthly_counts, 
        x="sync_month", 
        y="syncs", 
        height=300
    )
    fig_line.update_traces(line_color=COLORS["primary"], marker=dict(size=8))
    fig_line.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Month",
        yaxis_title="Number of Syncs"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Row 6: Stacked Bar Charts (Semester and Program Studi)
col_sem, col_prog = st.columns([1, 1], gap="medium")

with col_sem:
    with chart_panel("Staleness by Semester", height=420):
        df_master["semester_status"] = df_master["semester_status"].fillna("Unknown").astype(str)
        # Sort semesters logically if they are numeric strings
        sorted_sems = sorted(df_master["semester_status"].unique(), key=lambda x: int(float(x)) if x.replace('.','',1).isdigit() else 999)
        
        # Pre-aggregate data for bar chart
        sem_counts = df_master.groupby(["semester_status", "staleness"]).size().reset_index(name="count")

        fig_sem = charts.bar(
            sem_counts, 
            x="semester_status", 
            y="count",
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            category_orders={"semester_status": sorted_sems},
            barmode="stack",
            height=340
        )
        fig_sem.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Semester",
            yaxis_title="Students",
            legend_title=""
        )
        st.plotly_chart(fig_sem, use_container_width=True)

with col_prog:
    with chart_panel("Staleness by Program Studi", height=420):
        # Program Studi is categorical, sort by value counts
        prog_order = df_master["program_studi_status"].value_counts().index.tolist()
        
        # Pre-aggregate data for bar chart
        prog_counts = df_master.groupby(["program_studi_status", "staleness"]).size().reset_index(name="count")
        
        fig_prog = charts.bar(
            prog_counts, 
            y="program_studi_status", 
            x="count",
            orientation="h",
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            category_orders={"program_studi_status": prog_order},
            barmode="stack",
            height=340
        )
        fig_prog.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="",
            xaxis_title="Students",
            legend_title="",
            xaxis_tickangle=0
        )
        st.plotly_chart(fig_prog, use_container_width=True)

section_divider()

# Row 7: Master Table
with table_panel("Master Quality Data", height=500):
    with filter_bar():
        f1, f2 = st.columns(2)
        with f1:
            stale_filter = st.multiselect(
                "Filter by Staleness", 
                options=["Safe", "Stale", "Critical"], 
                default=["Stale", "Critical"]
            )
        with f2:
            mismatch_filter = st.checkbox("Show only records with mismatched data", value=False)
            
    filtered_df = df_master[df_master["staleness"].isin(stale_filter)]
    if mismatch_filter:
        filtered_df = filtered_df[filtered_df["has_mismatch"]]
        
    display_cols = [
        "NIM", "nama_status", "program_studi_status", "sync_date", 
        "days_since_sync", "staleness", "has_mismatch", "mismatch_types"
    ]
    
    st.dataframe(
        filtered_df[display_cols].sort_values("days_since_sync", ascending=False), 
        use_container_width=True, 
        hide_index=True
    )
    st.caption(f"Showing {len(filtered_df)} of {total_students} total records")
