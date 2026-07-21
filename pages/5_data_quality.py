import streamlit as st
import pandas as pd
import plotly.express as px

from utils.layout import (
    inject_global_css, page_header, metric_strip, chart_panel,
    filter_bar, table_panel, panel, card_grid, section_divider,
)
from utils.theme import COLORS, CHART_PALETTE, apply_plotly_style
from utils.queries import get_data_quality_master

# Page setup
inject_global_css()
page_header(
    "Data Synchronization",
    "Cek Sinkronisasi Data mahasiswa untuk validasi kelengkapan serta kebaruan data",
    page_title="Data Synchronization | SMILE",
)

# Load Data
df_master = get_data_quality_master()

if df_master.empty:
    st.info("No data available for sync evaluation.")
    st.stop()

# Preprocess some columns for filtering
df_master["semester_status"] = df_master["semester_status"].fillna("Unknown").astype(str)
df_master["program_studi_status"] = df_master["program_studi_status"].fillna("Unknown").astype(str)

# Filters
with filter_bar():
    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        sorted_sems_filter = sorted(df_master["semester_status"].unique(), key=lambda x: int(float(x)) if x.replace('.','',1).isdigit() else 999)
        sel_semester = st.multiselect(
            "Semester",
            options=sorted_sems_filter,
            default=[]
        )
    with fc2:
        sorted_prodi = sorted(df_master["program_studi_status"].unique())
        sel_prodi = st.multiselect(
            "Program Studi",
            options=sorted_prodi,
            default=[]
        )
    with fc3:
        valid_dates = df_master["sync_date"].dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
        else:
            min_date = pd.Timestamp("2023-01-01").date()
            max_date = pd.Timestamp("2026-12-31").date()
            
        date_range = st.date_input(
            "Sync Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

# Apply filters
if sel_semester:
    df_master = df_master[df_master["semester_status"].isin(sel_semester)]
if sel_prodi:
    df_master = df_master[df_master["program_studi_status"].isin(sel_prodi)]
    
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt = pd.Timestamp(date_range[1])
    mask = df_master["sync_date"].notna()
    df_master = df_master[mask & (df_master["sync_date"] >= start_dt) & (df_master["sync_date"] <= end_dt)]

if df_master.empty:
    st.info("No data matches the selected filters.")
    st.stop()

# Row 2: Earliest / Latest Sync Date
earliest_sync = df_master["sync_date"].min()
latest_sync = df_master["sync_date"].max()

earliest_str = earliest_sync.strftime('%d %B %Y') if not pd.isnull(earliest_sync) else "N/A"
latest_str = latest_sync.strftime('%d %B %Y') if not pd.isnull(latest_sync) else "N/A"

metric_strip([
    {
        "label": "Earliest Sync Date",
        "value": earliest_str,
    },
    {
        "label": "Latest Sync Date",
        "value": latest_str,
    }
])

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
    "Safe": CHART_PALETTE[0],
    "Stale": CHART_PALETTE[1],
    "Critical": CHART_PALETTE[2]
}

# Row 4: Histogram and Pie Chart
col_hist, col_pie = st.columns([3, 2], gap="medium")

with col_hist:
    with chart_panel("Days Since Last Sync", height=380):
        fig_hist = px.histogram(
            df_master, 
            x="days_since_sync", 
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            height=300
        )
        fig_hist.update_traces(xbins_size=30, marker_line_color="var(--background-color)", marker_line_width=0.5)
        apply_plotly_style(fig_hist)
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
        
        fig_pie = px.pie(
            df_pie,
            names="staleness",
            values="count",
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            hole=0.5,
        )
        fig_pie.update_traces(
            textinfo="label+percent",
            textposition="outside",
            pull=[0.02] * len(df_pie),
        )
        apply_plotly_style(fig_pie)
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.caption(
    "**Keterangan Metrik Sinkronisasi:**  \n"
    "**Safe (<90 hari)**: Data rutin disinkronisasi baru-baru ini.  \n"
    "**Stale (90-179 hari)**: Data sudah mulai usang dan belum disinkronisasi dalam waktu yang cukup lama.  \n"
    "**Critical (>179 hari)**: Data sudah tidak disinkronisasi lebih dari 1 semester dan berisiko kehilangan relevansi."
)

# Row 5: Line chart for monthly sync
with chart_panel("Monthly Sync Volume", height=380):
    df_sync_time = df_master.copy()
    df_sync_time["sync_month"] = df_sync_time["sync_date"].dt.to_period("M").astype(str)
    monthly_counts = df_sync_time.groupby("sync_month").size().reset_index(name="syncs")
    
    fig_line = px.area(
        monthly_counts, 
        x="sync_month", 
        y="syncs",
        color_discrete_sequence=[CHART_PALETTE[0]],
        markers=True
    )
    apply_plotly_style(fig_line)
    fig_line.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Month",
        yaxis_title="Number of Syncs",
        height=300
    )
    fig_line.update_traces(
        line=dict(width=2.5),
        fillcolor="rgba(52,98,237,0.08)",
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Row 6: Stacked Bar Charts (Semester and Program Studi)
col_sem, col_prog = st.columns([2, 3], gap="medium")

with col_sem:
    with chart_panel("Staleness by Semester", height=420):
        sorted_sems = sorted(df_master["semester_status"].unique(), key=lambda x: int(float(x)) if x.replace('.','',1).isdigit() else 999)
        
        sem_counts = df_master.groupby(["semester_status", "staleness"]).size().reset_index(name="count")

        fig_sem = px.bar(
            sem_counts, 
            x="semester_status", 
            y="count",
            color="staleness",
            color_discrete_map=STALENESS_COLORS,
            category_orders={"semester_status": sorted_sems},
            barmode="stack",
            height=340
        )
        fig_sem.update_layout(xaxis_tickangle=-30)
        apply_plotly_style(fig_sem)
        fig_sem.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Semester",
            yaxis_title="Students",
            legend_title=""
        )
        st.plotly_chart(fig_sem, use_container_width=True)

with col_prog:
    with chart_panel("Staleness by Program Studi", height=420):
        prog_order = df_master["program_studi_status"].value_counts().index.tolist()
        
        prog_counts = df_master.groupby(["program_studi_status", "staleness"]).size().reset_index(name="count")
        
        fig_prog = px.bar(
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
        apply_plotly_style(fig_prog)
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