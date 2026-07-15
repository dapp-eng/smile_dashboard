import streamlit as st
import pandas as pd

from utils.layout import (
    page_header, metric_strip, chart_panel,
    filter_bar, table_panel, panel, card_grid, section_divider,
)
from utils.theme import COLORS
from utils.queries import (
    get_sync_mismatch, get_orphaned_tracking,
    get_denorm_inconsistencies, get_all_table_counts,
)
from utils import charts

# Page setup
page_header(
    "Data Quality",
    "BT-08 — Data Sync & Integrity Checks",
    page_title="Data Quality | SMILE",
)

# Load data
df_sync = get_sync_mismatch()
df_orphan = get_orphaned_tracking()
df_denorm = get_denorm_inconsistencies()
table_counts = get_all_table_counts()

total_students = table_counts.get("student_all", 0)
total_status = table_counts.get("status_student", 0)
total_issues = len(df_sync) + len(df_orphan) + len(df_denorm)

synced_count = total_students - len(
    df_sync[df_sync["mismatch_type"] == "missing_in_status_student"]
) if not df_sync.empty else total_students

# Metric strip
sync_pct = round(synced_count / total_students * 100, 1) if total_students else 0
metric_strip([
    {
        "label": "Total Students",
        "value": f"{total_students:,}",
    },
    {
        "label": "Synced Records",
        "value": f"{synced_count:,}",
        "delta": f"{sync_pct}%",
        "sentiment": "success" if sync_pct >= 95 else "warning" if sync_pct >= 80 else "danger",
    },
    {
        "label": "Sync Mismatches",
        "value": len(df_sync),
        "sentiment": "success" if len(df_sync) == 0 else "danger",
    },
    {
        "label": "Orphaned Records",
        "value": len(df_orphan),
        "sentiment": "success" if len(df_orphan) == 0 else "danger",
    },
    {
        "label": "Denorm Issues",
        "value": len(df_denorm),
        "sentiment": "success" if len(df_denorm) == 0 else "warning",
    },
])

# Charts row
section_divider()

col_left, col_right = card_grid(2)

# Donut: mismatch type breakdown
with col_left:
    with chart_panel("Sync Mismatch Breakdown", height=420):
        if df_sync.empty:
            st.info("No sync mismatches detected.")
        else:
            mismatch_counts = (
                df_sync["mismatch_type"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "mismatch_type", "mismatch_type": "type", "count": "count"})
            )
            # Ensure column names are correct after value_counts
            if "type" in mismatch_counts.columns:
                mismatch_counts.columns = ["type", "count"]
            else:
                mismatch_counts.columns = ["type", "count"]

            color_map = {
                "missing_in_status_student": COLORS["danger"],
                "missing_in_student_all": COLORS["warning"],
                "name_mismatch": COLORS["secondary"],
            }
            import plotly.express as px
            fig = px.pie(
                mismatch_counts,
                names="type",
                values="count",
                hole=0.5,
                color="type",
                color_discrete_map=color_map,
                height=340,
            )
            fig.update_traces(
                textinfo="label+value",
                textposition="outside",
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

# Bar: issue count by table
with col_right:
    with chart_panel("Issues by Table", height=420):
        issue_summary = []
        if not df_sync.empty:
            issue_summary.append({"table": "student_all / status_student", "issues": len(df_sync), "type": "Sync Mismatch"})
        if not df_orphan.empty:
            issue_summary.append({"table": "tracking_student", "issues": len(df_orphan), "type": "Orphaned Record"})
        if not df_denorm.empty:
            for tbl, grp in df_denorm.groupby("table"):
                issue_summary.append({"table": tbl, "issues": len(grp), "type": "Denorm Mismatch"})

        if not issue_summary:
            st.info("No data quality issues detected.")
        else:
            df_issues = pd.DataFrame(issue_summary)
            color_map = {
                "Sync Mismatch": COLORS["danger"],
                "Orphaned Record": COLORS["warning"],
                "Denorm Mismatch": COLORS["secondary"],
            }
            import plotly.express as px
            fig = px.bar(
                df_issues,
                x="table",
                y="issues",
                color="type",
                color_discrete_map=color_map,
                text="issues",
                height=340,
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Issue Count",
                xaxis_tickangle=-20,
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

# Row counts table
section_divider()

with panel("Table Row Counts"):
    df_counts = pd.DataFrame(
        [{"Table": t, "Rows": c} for t, c in table_counts.items()]
    ).sort_values("Rows", ascending=False)
    st.dataframe(df_counts, use_container_width=True, hide_index=True)

# Detail: sync mismatches
section_divider()

with table_panel("Detail - Sync Mismatches (student_all / status_student)", height=400):
    if df_sync.empty:
        st.info("No mismatches found between student_all and status_student.")
    else:
        type_filter = st.multiselect(
            "Filter by mismatch type",
            options=df_sync["mismatch_type"].unique().tolist(),
            default=df_sync["mismatch_type"].unique().tolist(),
            key="sync_filter",
        )
        filtered = df_sync[df_sync["mismatch_type"].isin(type_filter)]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} of {len(df_sync)} mismatch(es)")

# Detail: orphaned records
with table_panel("Detail - Orphaned tracking_student Records", height=400):
    if df_orphan.empty:
        st.info("No orphaned tracking_student rows found.")
    else:
        display_cols = [
            c for c in ["id_tracking_student", "nim", "student_name",
                         "company", "position", "progress_student", "last_update"]
            if c in df_orphan.columns
        ]
        st.dataframe(df_orphan[display_cols], use_container_width=True, hide_index=True)
        st.caption(f"{len(df_orphan)} orphaned row(s) — nim not found in student_all")

# Detail: denormalization inconsistencies
with table_panel("Detail - Denormalization Inconsistencies", height=400):
    if df_denorm.empty:
        st.info("No denormalization mismatches detected.")
    else:
        tbl_filter = st.multiselect(
            "Filter by source table",
            options=df_denorm["source_table"].unique().tolist(),
            default=df_denorm["source_table"].unique().tolist(),
            key="denorm_filter",
        )
        filtered = df_denorm[df_denorm["source_table"].isin(tbl_filter)]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(
            f"Showing {len(filtered)} of {len(df_denorm)} inconsistency(ies) — "
            "duplicated columns disagree with their canonical FK source"
        )
