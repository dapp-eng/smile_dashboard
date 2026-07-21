import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.layout import (
    inject_global_css, page_header, metric_strip, chart_panel,
    table_panel, card_grid, section_divider, filter_bar
)
from utils.theme import COLORS, CHART_PALETTE, apply_plotly_style, PROGRESS_COLORS
from utils.data_loader import load_csv_table
from utils.metrics import get_ghosting_flags

# Page setup
inject_global_css()
page_header(
    "Monitor Process",
    "BT-05 — Proses seleksi dan deteksi ghosting",
    page_title="Monitor Process | SMILE"
)

# Load Data
df_track = load_csv_table("tracking_student")
df_company = load_csv_table("tracking_company")

# Use max send_date as 'today' so old mock data doesn't falsely flag everyone as ghosted
df_company["send_date"] = pd.to_datetime(df_company["send_date"], dayfirst=True, errors="coerce")
reference_date = df_company["send_date"].max()
df_all_ghosting = get_ghosting_flags(df_track, tracking_company=df_company, today=reference_date, include_healthy=True)
df_ghost = df_all_ghosting[df_all_ghosting["ghosting_check"] != "Healthy"]

if df_track.empty:
    st.info("Tidak ada data tracking tersedia.")
    st.stop()

# -------------------------------------------------------------
# Row 1: KPI Metrics
# -------------------------------------------------------------
total_tracked = len(df_track)
finished_statuses = ["Placement", "Rejected", "Finish"]
active_in_process = len(df_track[~df_track["progress_student"].isin(finished_statuses)])
total_placement = len(df_track[df_track["progress_student"] == "Placement"])
total_ghosted = len(df_ghost)

metric_strip([
    {"label": "Total Candidates Tracked", "value": f"{total_tracked:,}"},
    {"label": "Total Active In Process", "value": f"{active_in_process:,}"},
    {"label": "Total Placement", "value": f"{total_placement:,}"},
    {"label": "Total Ghosted", "value": f"{total_ghosted:,}", "sentiment": "danger" if total_ghosted > 0 else "success"}
])

section_divider()

# -------------------------------------------------------------
# Row 2: Stage Distribution
# -------------------------------------------------------------
c1, c2 = st.columns([3, 2], gap="medium")

with c1:
    with chart_panel("Stage Distribution", height=420):
        stage_counts = df_track["progress_student"].value_counts().reset_index()
        stage_counts.columns = ["stage", "count"]
        stage_counts = stage_counts.sort_values("count", ascending=True)
        fig_stage = px.bar(
            stage_counts, x="count", y="stage", orientation="h",
            color_discrete_sequence=[CHART_PALETTE[0]],
            height=340
        )
        apply_plotly_style(fig_stage)
        fig_stage.update_layout(xaxis_title="Candidates", yaxis_title="")
        max_val = stage_counts["count"].max()
        fig_stage.update_xaxes(range=[0, max_val * 1.1])
        st.plotly_chart(fig_stage, use_container_width=True)

with c2:
    with chart_panel("Process Status (Active vs Finished)", height=420):
        def map_status(stage):
            if stage in ["Placement", "Rejected", "Finish"]:
                return stage
            elif stage == "Ghosting":
                return "Ghosting"
            return "Active"

        df_track["broad_status"] = df_track["progress_student"].apply(map_status)
        status_counts = df_track["broad_status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]

        status_colors = {
            "Active": CHART_PALETTE[0],
            "Placement": COLORS["success"],
            "Rejected": COLORS["danger"],
            "Finish": COLORS["neutral"],
            "Ghosting": COLORS["warning"]
        }

        fig_pie = px.pie(
            status_counts, names="status", values="count",
            color="status", color_discrete_map=status_colors,
            hole=0.4, height=340
        )
        fig_pie.update_traces(textinfo="label+percent", textposition="outside")
        apply_plotly_style(fig_pie)
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

section_divider()

# -------------------------------------------------------------
# Row 3: Rejection Metrics
# -------------------------------------------------------------
r1, r2 = st.columns([1, 1], gap="medium")

with r1:
    with chart_panel("Rejection Rate by Stage", height=420):
        def get_max_stage(row):
            rej = str(row['rejection'])
            prog = str(row['progress_student'])

            rej_map = {
                'Rejection Screening CV': 0,
                'Rejection Study Case': 1,
                'Rejection Interview User': 3,
                'Rejection Final Interview': 4,
                'Placement': 5
            }
            if rej in rej_map:
                return rej_map[rej]

            prog_map = {
                'Selecting Student by Company': 0,
                'Study Case': 1,
                'CDC Briefing Student': 2,
                'Interview User': 3,
                'Final Interview': 4,
                'Placement': 5,
                'Finish': 5,
            }
            return prog_map.get(prog, 0)

        df_track['max_stage'] = df_track.apply(get_max_stage, axis=1)

        stages = [
            (0, "Selecting Student by Company", "Rejection Screening CV"),
            (1, "Study Case", "Rejection Study Case"),
            (3, "Interview User", "Rejection Interview User"),
            (4, "Final Interview", "Rejection Final Interview")
        ]

        rates = []
        for idx, stage_name, rej_val in stages:
            denom = (df_track['max_stage'] >= idx).sum()
            num = (df_track['rejection'] == rej_val).sum()
            rate = (num / denom * 100).round(1) if denom > 0 else 0
            rates.append({"stage": stage_name, "rate": rate})

        df_rates = pd.DataFrame(rates)
        df_rates = df_rates.sort_values("rate", ascending=True)

        fig_rej = px.bar(
            df_rates, x="stage", y="rate", orientation="v",
            color_discrete_sequence=[COLORS["danger"]],
            height=340,
            text_auto='.1f'
        )
        apply_plotly_style(fig_rej)
        fig_rej.update_layout(
            xaxis_title="", yaxis_title="Rejection Rate (%)",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig_rej.update_yaxes(range=[0, 100])
        fig_rej.update_traces(texttemplate='%{y}%', textposition='outside')
        st.plotly_chart(fig_rej, use_container_width=True)

with r2:
    with chart_panel("Rejection Breakdown", height=420):
        rej_counts = df_track["rejection"].fillna("On Progress").value_counts()

        labels = ["Total Candidates", "On Progress", "Placement", "Ghosting", "Rejected",
                  "Screening CV", "Interview User", "Study Case", "Final Interview"]

        idx = {l: i for i, l in enumerate(labels)}

        source = []
        target = []
        value = []

        def add_flow(src, tgt, val):
            if val > 0:
                source.append(idx[src])
                target.append(idx[tgt])
                value.append(val)

        on_prog = rej_counts.get("On Progress", 0)
        place = rej_counts.get("Placement", 0)
        ghost = rej_counts.get("Ghosting", 0)

        rej_cv = rej_counts.get("Rejection Screening CV", 0)
        rej_int = rej_counts.get("Rejection Interview User", 0)
        rej_std = rej_counts.get("Rejection Study Case", 0)
        rej_fin = rej_counts.get("Rejection Final Interview", 0)
        total_rej = rej_cv + rej_int + rej_std + rej_fin

        add_flow("Total Candidates", "On Progress", on_prog)
        add_flow("Total Candidates", "Placement", place)
        add_flow("Total Candidates", "Ghosting", ghost)
        add_flow("Total Candidates", "Rejected", total_rej)

        add_flow("Rejected", "Screening CV", rej_cv)
        add_flow("Rejected", "Interview User", rej_int)
        add_flow("Rejected", "Study Case", rej_std)
        add_flow("Rejected", "Final Interview", rej_fin)

        node_colors = [
            COLORS["primary"], CHART_PALETTE[1], COLORS["success"], COLORS["warning"], COLORS["danger"],
            COLORS["danger"], COLORS["danger"], COLORS["danger"], COLORS["danger"]
        ]

        if len(source) > 0:
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15, thickness=20, line=dict(color="black", width=0.5),
                    label=labels,
                    color=node_colors
                ),
                link=dict(source=source, target=target, value=value)
            )])

            apply_plotly_style(fig_sankey)
            fig_sankey.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("No data available to construct Sankey chart.")

section_divider()

# -------------------------------------------------------------
# Row 4: Ghosting Metrics
# -------------------------------------------------------------
g1, g2 = st.columns([2, 3], gap="medium")

with g1:
    with chart_panel("Ghosting Proportion", height=400):
        def get_combined_severity(row):
            g = row["ghosting_check"]
            p = row["progress_student"]

            if g == "labeled":
                if p == "Ghosting":
                    return "Ghosting"
                elif p in ["FU 1", "FU 2", "FU 3"]:
                    return "FU 1-3"
            else:
                if g == "overdue_unlabeled_ghosting":
                    return "Ghosting"
                elif g in ["overdue_unlabeled_fu1", "overdue_unlabeled_fu2", "overdue_unlabeled_fu3"]:
                    return "FU 1-3"
            return "Healthy"

        counts = {"Healthy": active_in_process - len(df_ghost), "FU 1-3": 0, "Ghosting": 0}

        if not df_ghost.empty:
            df_ghost["combined_category"] = df_ghost.apply(get_combined_severity, axis=1)
            cat_counts = df_ghost["combined_category"].value_counts()
            counts["FU 1-3"] = cat_counts.get("FU 1-3", 0)
            counts["Ghosting"] = cat_counts.get("Ghosting", 0)

        gh_data = pd.DataFrame({
            "status": ["Healthy", "FU 1-3", "Ghosting"],
            "count": [counts["Healthy"], counts["FU 1-3"], counts["Ghosting"]]
        })

        fig_gh_pie = px.pie(
            gh_data, names="status", values="count",
            color="status", color_discrete_map={"Ghosting": COLORS["danger"], "FU 1-3": COLORS["warning"], "Healthy": CHART_PALETTE[0]},
            hole=0.6, height=320
        )
        fig_gh_pie.update_traces(textinfo="percent", textposition="inside")
        apply_plotly_style(fig_gh_pie)
        fig_gh_pie.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_gh_pie, use_container_width=True)

with g2:
    with chart_panel("Follow Up (FU) Severity", height=400):
        if not df_ghost.empty:
            def get_granular_severity(row):
                g = row["ghosting_check"]
                p = row["progress_student"]

                if g == "labeled":
                    if p == "Ghosting":
                        return "Ghosting"
                    elif p in ["FU 1", "FU 2", "FU 3"]:
                        return p
                else:
                    if g == "overdue_unlabeled_ghosting":
                        return "Ghosting"
                    elif g == "overdue_unlabeled_fu3":
                        return "FU 3"
                    elif g == "overdue_unlabeled_fu2":
                        return "FU 2"
                    elif g == "overdue_unlabeled_fu1":
                        return "FU 1"
                return "Unknown"

            df_ghost["granular_severity"] = df_ghost.apply(get_granular_severity, axis=1)

            order = ["FU 1", "FU 2", "FU 3", "Ghosting"]
            sev_counts = df_ghost["granular_severity"].value_counts().reindex(order).fillna(0).reset_index()
            sev_counts.columns = ["severity", "count"]

            fig_sev = px.bar(
                sev_counts, x="severity", y="count",
                color="severity",
                color_discrete_sequence=px.colors.sequential.Reds[2:],
                height=320,
                text_auto=True
            )
            apply_plotly_style(fig_sev)
            fig_sev.update_layout(xaxis_title="", yaxis_title="Cases", showlegend=False)
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.info("No ghosting data to display.")

section_divider()

# -------------------------------------------------------------
# Row 5: Unified Master Table & Drill Down
# -------------------------------------------------------------
with table_panel("Unified Master Table", height=None):
    if df_all_ghosting.empty:
        st.success("🎉 Tidak ada data kandidat aktif.")
    else:
        display_cols = [
            "NIM", "student_name", "company", "position",
            "jenis_penempatan", "progress_student", "ghosting_check", "days_since_update"
        ]

        with filter_bar():
            f1, f2, f3 = st.columns(3)
            with f1:
                search_query = st.text_input("Search (Name/NIM)", "")
            with f2:
                companies = sorted(df_all_ghosting["company"].dropna().unique())
                sel_company = st.multiselect("Filter by Company", options=companies)
            with f3:
                severities = sorted(df_all_ghosting["ghosting_check"].dropna().unique())
                sel_severity = st.multiselect("Filter by Severity", options=severities)

        df_ghost_view = df_all_ghosting.copy()

        if search_query:
            query = search_query.lower()
            mask = (
                df_ghost_view["student_name"].str.lower().str.contains(query, na=False) |
                df_ghost_view["NIM"].astype(str).str.contains(query, na=False)
            )
            df_ghost_view = df_ghost_view[mask]

        if sel_company:
            df_ghost_view = df_ghost_view[df_ghost_view["company"].isin(sel_company)]

        if sel_severity:
            df_ghost_view = df_ghost_view[df_ghost_view["ghosting_check"].isin(sel_severity)]

        df_ghost_view = df_ghost_view.sort_values("days_since_update", ascending=False).reset_index(drop=True)

        st.caption("Klik salah satu baris untuk melihat riwayat kandidat selengkapnya.")

        event = st.dataframe(
            df_ghost_view[display_cols],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "days_since_update": st.column_config.NumberColumn("Days Since Activity"),
                "ghosting_check": st.column_config.TextColumn("Severity")
            }
        )

        selected_rows = event.selection.rows
        if selected_rows:
            selected_idx = selected_rows[0]
            selected_nim = str(df_ghost_view.iloc[selected_idx]["NIM"])

            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            section_divider()
            st.subheader("Student Detail Profile")

            if "df_student_context" not in st.session_state:
                df_student = load_csv_table("student_all")
                df_status = load_csv_table("status_student")
                st.session_state["df_student_context"] = df_student.merge(df_status, on="NIM", how="inner", suffixes=("", "_status"))

            df_student_context = st.session_state["df_student_context"]

            student_info = df_student_context[df_student_context["NIM"].astype(str) == selected_nim]
            if not student_info.empty:
                student_info = student_info.iloc[0]
                st.markdown(
                    f"""
                    <div class="smile-panel" style="margin-bottom: 24px;">
                        <h4 style="margin-top: 0; margin-bottom: 16px; color: var(--smile-accent, #3462ED); font-family: 'Montserrat', sans-serif;">{student_info['nama']}</h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-family: 'Inter', sans-serif; font-size: 14px;">
                            <div><strong style="opacity:0.7">NIM:</strong><br>{student_info['NIM']}</div>
                            <div><strong style="opacity:0.7">Program Studi:</strong><br>{student_info['program_studi']}</div>
                            <div><strong style="opacity:0.7">Semester:</strong><br>{student_info['semester']}</div>
                            <div><strong style="opacity:0.7">IPK:</strong><br>{student_info.get('IPK', student_info.get('ipk', '-'))}</div>
                            <div><strong style="opacity:0.7">Status:</strong><br>{student_info.get('status', '-')}</div>
                            <div><strong style="opacity:0.7">Domisili:</strong><br>{student_info.get('domisili', '-')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )

            df_full_history = df_track.merge(df_company[['id_tracking_company', 'send_date']], on='id_tracking_company', how='left')
            if not df_all_ghosting.empty and 'id_tracking_student' in df_all_ghosting.columns:
                df_full_history = df_full_history.merge(df_all_ghosting[['id_tracking_student', 'ghosting_check', 'days_since_update']], on='id_tracking_student', how='left')
            else:
                df_full_history["ghosting_check"] = "-"
                df_full_history["days_since_update"] = 0

            df_full_history["ghosting_check"] = df_full_history["ghosting_check"].fillna("-")
            df_full_history["days_since_update"] = df_full_history["days_since_update"].fillna(0)

            df_history = df_full_history[df_full_history["NIM"].astype(str) == selected_nim].copy()

            if df_history.empty:
                st.info("Kandidat ini belum memiliki riwayat aplikasi.")
            else:
                df_history = df_history.sort_values("last_update", ascending=False)

                html_rows = []
                for _, row in df_history.iterrows():
                    prog = str(row["progress_student"])
                    color = PROGRESS_COLORS.get(prog, COLORS["neutral"])
                    badge_html = f'<span style="background-color: {color}; border-radius: 12px; padding: 4px 10px; color: white; font-size: 12px; font-weight: 600; white-space: nowrap;">{prog}</span>'

                    send_dt = pd.to_datetime(row["send_date"]).strftime("%Y-%m-%d") if pd.notnull(row["send_date"]) else "-"
                    last_dt = pd.to_datetime(row["last_update"], format="mixed", dayfirst=True).strftime("%Y-%m-%d") if pd.notnull(row["last_update"]) else "-"

                    ghost_check = row.get('ghosting_check', '-')

                    html_rows.append(f"""<tr style="border-bottom: 1px solid var(--border-color);">
    <td style="padding: 12px 16px;">{row.get('company', '-')}</td>
    <td style="padding: 12px 16px;">{row.get('position', '-')}</td>
    <td style="padding: 12px 16px;">{row.get('jenis_penempatan', '-')}</td>
    <td style="padding: 12px 16px;">{badge_html}</td>
    <td style="padding: 12px 16px;">{send_dt}</td>
    <td style="padding: 12px 16px;">{last_dt}</td>
    <td style="padding: 12px 16px;">{ghost_check}</td>
</tr>""")

                table_html = f"""<div class="smile-panel" style="padding: 0; overflow-x: auto; margin-bottom: 0;">
    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 14px; text-align: left;">
        <thead>
            <tr style="background-color: rgba(0,0,0,0.02);">
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Company</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Position</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Type</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Progress</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Send Date</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Last Update</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Severity</th>
            </tr>
        </thead>
        <tbody>
            {''.join(html_rows)}
        </tbody>
    </table>
</div>"""
                st.markdown(table_html, unsafe_allow_html=True)