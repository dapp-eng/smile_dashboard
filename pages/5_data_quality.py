import streamlit as st
import pandas as pd
import plotly.express as px

from utils.layout import (
    inject_global_css, page_header, metric_strip, chart_panel,
    filter_bar, table_panel, panel, card_grid, section_divider,
)
from utils.theme import COLORS, CHART_PALETTE, apply_plotly_style
from utils.queries import (
    get_sync_mismatch, get_orphaned_tracking,
    get_denorm_inconsistencies, get_all_table_counts,
)
from utils import charts

# Page setup
inject_global_css()
page_header(
    "Data Quality",
    "Pemeriksaan sinkronisasi dan integritas data",
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

# validation summary section
section_divider()

# Validation status badges
check_results = [
    ("Sync Check", len(df_sync) == 0, f"{len(df_sync)} mismatch"),
    ("Orphan Check", len(df_orphan) == 0, f"{len(df_orphan)} orphaned record"),
    ("Denorm Check", len(df_denorm) == 0, f"{len(df_denorm)} inconsistency"),
]

status_html = '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px;">'
for name, passed, detail in check_results:
    badge_class = "smile-check-passed" if passed else "smile-check-failed"
    icon = "&#10003;" if passed else "&#10007;"
    label = "Passed" if passed else "Failed"
    status_html += (
        f'<div class="smile-check-badge {badge_class}">'
        f'{icon} {name}: {label} ({detail})'
        f'</div>'
    )
status_html += '</div>'
st.markdown(status_html, unsafe_allow_html=True)

# validation charts row
col_left, col_right = card_grid(2)

# Bar: table row counts (always visible)
with col_left:
    with chart_panel("Table Row Counts", height=420):
        df_counts = pd.DataFrame(
            [{"Table": t, "Rows": c} for t, c in table_counts.items()]
        ).sort_values("Rows", ascending=True)
        fig = px.bar(
            df_counts, x="Rows", y="Table", orientation="h",
            color_discrete_sequence=[CHART_PALETTE[0]],
            text="Rows",
            height=340,
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        apply_plotly_style(fig)
        fig.update_layout(
            yaxis_title="",
            xaxis_title="Row Count",
            margin=dict(t=10, b=40, l=10, r=80),
        )
        st.plotly_chart(fig, use_container_width=True)

# Bar: record sync comparison (always visible)
with col_right:
    with chart_panel("Record Sync Comparison", height=420):
        sync_data = pd.DataFrame([
            {"Table": "student_all", "Records": table_counts.get("student_all", 0)},
            {"Table": "status_student", "Records": table_counts.get("status_student", 0)},
            {"Table": "tracking_student", "Records": table_counts.get("tracking_student", 0)},
        ])
        fig = px.bar(
            sync_data, x="Table", y="Records",
            color_discrete_sequence=[CHART_PALETTE[0]],
            text="Records",
            height=340,
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        apply_plotly_style(fig)
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Record Count",
            margin=dict(t=30, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)
        match_status = "Records match" if total_students == total_status else f"Difference: {abs(total_students - total_status)}"
        st.caption(f"student_all: {total_students:,} | status_student: {total_status:,} | {match_status}")

# mismatch detail charts
section_divider()

col_left2, col_right2 = card_grid(2)

# Donut: mismatch type breakdown
with col_left2:
    with chart_panel("Sync Mismatch Breakdown", height=420):
        if df_sync.empty:
            st.success("Tidak ada sync mismatch yang terdeteksi. Semua data tersinkronisasi dengan benar.")
        else:
            mismatch_counts = (
                df_sync["mismatch_type"]
                .value_counts()
                .reset_index()
            )
            mismatch_counts.columns = ["type", "count"]

            color_map = {
                "missing_in_status_student": COLORS["danger"],
                "missing_in_student_all": COLORS["warning"],
                "name_mismatch": COLORS["secondary"],
            }
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
            apply_plotly_style(fig)
            fig.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

# Bar: issue count by table
with col_right2:
    with chart_panel("Issues By Table", height=420):
        issue_summary = []
        if not df_sync.empty:
            issue_summary.append({"table": "student_all / status_student", "issues": len(df_sync), "type": "Sync Mismatch"})
        if not df_orphan.empty:
            issue_summary.append({"table": "tracking_student", "issues": len(df_orphan), "type": "Orphaned Record"})
        if not df_denorm.empty:
            for tbl, grp in df_denorm.groupby("table"):
                issue_summary.append({"table": tbl, "issues": len(grp), "type": "Denorm Mismatch"})

        if not issue_summary:
            st.success("Tidak ada masalah kualitas data yang terdeteksi. Semua pengecekan lolos.")
        else:
            df_issues = pd.DataFrame(issue_summary)
            color_map = {
                "Sync Mismatch": COLORS["danger"],
                "Orphaned Record": COLORS["warning"],
                "Denorm Mismatch": COLORS["secondary"],
            }
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
            apply_plotly_style(fig)
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

# detail tables
section_divider()

with table_panel("Detail - Sync Mismatches (student_all / status_student)", height=400):
    if df_sync.empty:
        st.success("Tidak ada mismatch antara student_all dan status_student.")
    else:
        type_filter = st.multiselect(
            "Filter by mismatch type",
            options=df_sync["mismatch_type"].unique().tolist(),
            default=df_sync["mismatch_type"].unique().tolist(),
            key="sync_filter",
        )
        filtered = df_sync[df_sync["mismatch_type"].isin(type_filter)]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(f"Menampilkan {len(filtered)} dari {len(df_sync)} mismatch")

with table_panel("Detail - Orphaned Tracking Student Records", height=400):
    if df_orphan.empty:
        st.success("Tidak ada orphaned tracking_student rows yang ditemukan.")
    else:
        display_cols = [
            c for c in ["id_tracking_student", "NIM", "student_name",
                         "company", "position", "progress_student", "last_update"]
            if c in df_orphan.columns
        ]
        st.dataframe(df_orphan[display_cols], use_container_width=True, hide_index=True)
        st.caption(f"{len(df_orphan)} orphaned row(s) - NIM tidak ditemukan di student_all")

with table_panel("Detail - Denormalization Inconsistencies", height=400):
    if df_denorm.empty:
        st.success("Tidak ada denormalization mismatch yang terdeteksi.")
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
            f"Menampilkan {len(filtered)} dari {len(df_denorm)} inkonsistensi - "
            "kolom duplikat tidak sesuai dengan sumber FK kanoniknya"
        )
