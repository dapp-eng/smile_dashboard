# data synchronization - bt-08 student data management

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.layout import (
    inject_global_css, page_header, metric_strip, chart_panel,
    filter_bar, table_panel, card_grid, section_divider,
)
from utils.theme import COLORS, CHART_PALETTE, STALENESS_COLORS, apply_plotly_style
from utils.queries import get_data_quality_master
from utils.data_loader import load_csv_table
from utils.i18n import t

inject_global_css()

page_header(
    t("page.data_sync"),
    bt_caption=t("bt.08"),
)

# load data
df_master = get_data_quality_master()

if df_master.empty:
    st.info(t("ds.no_data"))
    st.stop()

# preprocess columns for filtering
df_master["semester_status"] = df_master["semester_status"].fillna("Unknown").astype(str)
df_master["program_studi_status"] = df_master["program_studi_status"].fillna("Unknown").astype(str)

# filters
with filter_bar():
    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        sorted_sems_filter = sorted(
            df_master["semester_status"].unique(),
            key=lambda x: int(float(x)) if x.replace(".", "", 1).isdigit() else 999,
        )
        sel_semester = st.multiselect(t("ds.semester"), options=sorted_sems_filter, default=[])
    with fc2:
        sorted_prodi = sorted(df_master["program_studi_status"].unique())
        sel_prodi = st.multiselect(t("ds.prodi"), options=sorted_prodi, default=[])
    with fc3:
        valid_dates = df_master["sync_date"].dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
        else:
            min_date = pd.Timestamp("2023-01-01").date()
            max_date = pd.Timestamp("2026-12-31").date()
        date_range = st.date_input(
            t("ds.sync_date_range"),
            value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )

# apply filters
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
    st.info(t("ds.no_data_filter"))
    st.stop()

# sync date range metrics
earliest_sync = df_master["sync_date"].min()
latest_sync = df_master["sync_date"].max()
earliest_str = earliest_sync.strftime("%d %B %Y") if not pd.isnull(earliest_sync) else "N/A"
latest_str = latest_sync.strftime("%d %B %Y") if not pd.isnull(latest_sync) else "N/A"

metric_strip([
    {"label": t("ds.earliest_sync"), "value": earliest_str},
    {"label": t("ds.latest_sync"), "value": latest_str},
])

section_divider()

# staleness and mismatch metrics
total_students = len(df_master)
pct_critical = round(len(df_master[df_master["staleness"] == "Critical"]) / total_students * 100, 1)
pct_mismatch = round(df_master["has_mismatch"].sum() / total_students * 100, 1)

metric_strip([
    {"label": t("ds.total_students"), "value": f"{total_students:,}"},
    {
        "label": t("ds.critical_sync"),
        "value": f"{pct_critical}%",
        "sentiment": "success" if pct_critical < 10 else "danger",
    },
    {
        "label": t("ds.mismatched"),
        "value": f"{pct_mismatch}%",
        "sentiment": "success" if pct_mismatch < 5 else "warning",
    },
])

section_divider()

# histogram and pie chart
col_hist, col_pie = st.columns([3, 2], gap="medium")

with col_hist:
    with chart_panel(t("ds.chart_days_sync"), height=380):
        fig_hist = px.histogram(
            df_master, x="days_since_sync", color="staleness",
            color_discrete_map=STALENESS_COLORS, height=300,
        )
        fig_hist.update_traces(
            xbins_size=30,
            marker_line_color="rgba(128,128,128,0.2)",
            marker_line_width=0.5,
        )
        apply_plotly_style(fig_hist)
        fig_hist.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=t("ds.days_since_sync"),
            yaxis_title=t("ds.count_students"),
            legend_title="", bargap=0.02,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with col_pie:
    with chart_panel(t("ds.chart_staleness"), height=380):
        df_pie = df_master["staleness"].value_counts().reset_index()
        df_pie.columns = ["staleness", "count"]
        fig_pie = px.pie(
            df_pie, names="staleness", values="count",
            color="staleness", color_discrete_map=STALENESS_COLORS, hole=0.5,
        )
        fig_pie.update_traces(
            textinfo="label+percent", textposition="outside",
            pull=[0.02] * len(df_pie),
        )
        apply_plotly_style(fig_pie)
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300, showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.caption(t("ds.staleness_note"))

# monthly sync volume
with chart_panel(t("ds.chart_monthly_sync"), height=380):
    df_sync_time = df_master.copy()
    df_sync_time["sync_month"] = df_sync_time["sync_date"].dt.to_period("M").astype(str)
    monthly_counts = df_sync_time.groupby("sync_month").size().reset_index(name="syncs")

    fig_line = px.area(
        monthly_counts, x="sync_month", y="syncs",
        color_discrete_sequence=[CHART_PALETTE[0]], markers=True,
    )
    apply_plotly_style(fig_line)
    fig_line.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=t("mc.month"), yaxis_title=t("ds.syncs"), height=300,
    )
    fig_line.update_traces(line=dict(width=2.5), fillcolor="rgba(52,98,237,0.08)")
    st.plotly_chart(fig_line, use_container_width=True)

# staleness by semester and program studi
col_sem, col_prog = st.columns([2, 3], gap="medium")

with col_sem:
    with chart_panel(t("ds.chart_sem_staleness"), height=420):
        sorted_sems = sorted(
            df_master["semester_status"].unique(),
            key=lambda x: int(float(x)) if x.replace(".", "", 1).isdigit() else 999,
        )
        sem_counts = df_master.groupby(["semester_status", "staleness"]).size().reset_index(name="count")
        fig_sem = px.bar(
            sem_counts, x="semester_status", y="count",
            color="staleness", color_discrete_map=STALENESS_COLORS,
            category_orders={"semester_status": sorted_sems},
            barmode="stack", height=340,
        )
        fig_sem.update_layout(xaxis_tickangle=-30)
        apply_plotly_style(fig_sem)
        fig_sem.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=t("ds.semester"), yaxis_title=t("ds.students"), legend_title="",
        )
        st.plotly_chart(fig_sem, use_container_width=True)

with col_prog:
    with chart_panel(t("ds.chart_prodi_staleness"), height=420):
        prog_order = df_master["program_studi_status"].value_counts().index.tolist()
        prog_counts = df_master.groupby(["program_studi_status", "staleness"]).size().reset_index(name="count")
        fig_prog = px.bar(
            prog_counts, y="program_studi_status", x="count",
            orientation="h", color="staleness", color_discrete_map=STALENESS_COLORS,
            category_orders={"program_studi_status": prog_order},
            barmode="stack", height=340,
        )
        apply_plotly_style(fig_prog)
        fig_prog.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="", xaxis_title=t("ds.students"),
            legend_title="", xaxis_tickangle=0,
        )
        st.plotly_chart(fig_prog, use_container_width=True)

section_divider()

# master quality data table
with table_panel(t("ds.master_table"), height=500):
    with filter_bar():
        f1, f2 = st.columns([1, 1], vertical_alignment="bottom")
        with f1:
            stale_filter = st.multiselect(
                t("ds.filter_staleness"),
                options=["Safe", "Stale", "Critical"],
                default=["Stale", "Critical"],
            )
        with f2:
            mismatch_filter = st.checkbox(t("ds.show_mismatch"), value=False)

    filtered_df = df_master[df_master["staleness"].isin(stale_filter)]
    if mismatch_filter:
        filtered_df = filtered_df[filtered_df["has_mismatch"]]

    display_cols = [
        "NIM", "nama_status", "program_studi_status", "sync_date",
        "days_since_sync", "staleness", "has_mismatch", "mismatch_types",
    ]

    st.dataframe(
        filtered_df[display_cols].sort_values("days_since_sync", ascending=False),
        use_container_width=True, hide_index=True,
    )
    st.caption(t("ds.showing_records", shown=f"{len(filtered_df)}", total=f"{total_students}"))

section_divider()

# -------------------------------------------------------------
# Row 8: "Finish" Status Reclassification Analysis
# -------------------------------------------------------------
df_tracking = load_csv_table("tracking_student")
df_finish = df_tracking[df_tracking["_original_progress"] == "Finish"].copy()

if not df_finish.empty:
    st.markdown('''
        <h3 style='margin-bottom: 0.2rem;'>"Finish" Status Reclassification</h3>
        <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>
            The raw data used "Finish" as a catch-all close-out status. We reclassify these records using the <code>rejection</code> column to reveal the true outcome.
        </p>
        <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
    ''', unsafe_allow_html=True)

    total_finish = len(df_finish)
    unresolved_count = len(df_finish[df_finish["progress_student"] == "Unresolved"])
    reclassified_count = total_finish - unresolved_count

    metric_strip([
        {"label": "Total \"Finish\" Records", "value": f"{total_finish:,}"},
        {"label": "Reclassified", "value": f"{reclassified_count:,}", "sentiment": "success"},
        {"label": "Truly Unresolved", "value": f"{unresolved_count:,}", "sentiment": "warning"},
        {"label": "Unresolved Rate", "value": f"{unresolved_count / total_finish * 100:.1f}%", "sentiment": "warning"},
    ])

    section_divider()

    dq1, dq2 = st.columns([1, 1], gap="medium")

    with dq1:
        with chart_panel("Original Rejection Values", height=420, subtitle="What the rejection column actually said for 'Finish' records"):
            rej_counts = df_finish["rejection"].value_counts().reset_index()
            rej_counts.columns = ["rejection", "count"]

            rej_color_map = {
                "On Progress": COLORS["warning"],
                "Placement": COLORS["success"],
                "Ghosting": COLORS["neutral"],
                "Rejection Interview User": COLORS["danger"],
                "Rejection Screening CV": COLORS["danger"],
                "Rejection Study Case": COLORS["danger"],
                "Rejection Final Interview": COLORS["danger"],
            }

            fig_donut = px.pie(
                rej_counts, names="rejection", values="count",
                color="rejection", color_discrete_map=rej_color_map,
                hole=0.45, height=340
            )
            fig_donut.update_traces(textinfo="label+percent", textposition="outside")
            apply_plotly_style(fig_donut)
            fig_donut.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with dq2:
        with chart_panel("Reclassification Flow", height=420, subtitle="How 'Finish' records were remapped to their true outcomes"):
            reclass_map = {
                "Placement": "Placement",
                "Ghosting": "Ghosting",
                "On Progress": "Unresolved",
                "Rejection Interview User": "Rejected",
                "Rejection Screening CV": "Rejected",
                "Rejection Study Case": "Rejected",
                "Rejection Final Interview": "Rejected",
            }
            df_finish["reclassified"] = df_finish["rejection"].map(reclass_map).fillna("Unresolved")

            rejections = df_finish["rejection"].value_counts().index.tolist()
            reclassified = df_finish["reclassified"].value_counts().index.tolist()

            nodes = ["Finish"] + rejections + reclassified
            node_indices = {name: i for i, name in enumerate(nodes)}

            node_color_map = {
                "Finish": COLORS["neutral"],
                "On Progress": COLORS["warning"],
                "Placement": COLORS["success"],
                "Ghosting": CHART_PALETTE[4],
                "Rejection Interview User": COLORS["danger"],
                "Rejection Screening CV": COLORS["danger"],
                "Rejection Study Case": COLORS["danger"],
                "Rejection Final Interview": COLORS["danger"],
                "Rejected": COLORS["danger"],
                "Unresolved": COLORS["warning"],
            }
            node_colors = [node_color_map.get(n, COLORS["neutral"]) for n in nodes]

            sources, targets, values = [], [], []

            for rej, count in df_finish["rejection"].value_counts().items():
                sources.append(node_indices["Finish"])
                targets.append(node_indices[rej])
                values.append(count)

            flow = df_finish.groupby(["rejection", "reclassified"]).size().reset_index(name="count")
            for _, row in flow.iterrows():
                sources.append(node_indices[row["rejection"]])
                targets.append(node_indices[row["reclassified"]])
                values.append(row["count"])

            fig_sankey = go.Figure(go.Sankey(
                node=dict(
                    pad=20, thickness=20,
                    label=nodes,
                    color=node_colors,
                ),
                link=dict(
                    source=sources, target=targets, value=values,
                    color="rgba(150,150,150,0.25)"
                )
            ))
            apply_plotly_style(fig_sankey)
            fig_sankey.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_sankey, use_container_width=True)