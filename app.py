# smile dashboard - main entry point and overview page

import os
import streamlit as st

icon_path = os.path.join("assets", "smile-b2.png")
page_icon = icon_path if os.path.exists(icon_path) else None

st.set_page_config(
    page_title="SMILE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=page_icon,
)

import pandas as pd
import plotly.express as px

from utils.layout import (
    inject_global_css, page_header, render_sidebar_footer,
    metric_strip, chart_panel, card_grid, section_divider, panel,
)
from utils.theme import (
    COLORS, CHART_PALETTE, JENIS_PENEMPATAN_COLORS, STALENESS_COLORS, apply_plotly_style,
)
from utils.data_loader import load_csv_table
from utils.i18n import t, get_lang
from utils import queries, metrics

# session state defaults
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
if "lang" not in st.session_state:
    st.session_state["lang"] = "id"


def _setup_logo():
    # configure sidebar logo based on current theme mode
    mode = st.session_state.get("theme_mode", "light")
    logo_expanded = os.path.join("assets", "smile-w3.png")
    if mode == "light":
        logo_collapsed = os.path.join("assets", "smile-b2.png")
    else:
        logo_collapsed = os.path.join("assets", "smile-w2.png")
    if os.path.exists(logo_expanded) and os.path.exists(logo_collapsed):
        st.logo(logo_expanded, size="large", icon_image=logo_collapsed)


def overview_page():
    # overview page with kpi summary, charts, enriched process/data quality sections, and pdf download (bt-07)
    inject_global_css()

    page_header(
        t("page.overview"),
        bt_caption=t("bt.07"),
    )

    # load all data
    df_student_all = load_csv_table("student_all")
    df_status_student = load_csv_table("status_student")
    df_company = load_csv_table("company")
    df_tc = load_csv_table("tracking_company")
    df_tr = load_csv_table("talent_request")
    df_ts = load_csv_table("tracking_student")

    df_tc["request_date"] = pd.to_datetime(df_tc["request_date"], dayfirst=True, errors="coerce")
    df_tc["send_date"] = pd.to_datetime(df_tc["send_date"], dayfirst=True, errors="coerce")

    df_eligibility = metrics.get_student_eligibility(df_student_all, df_status_student)

    # core kpis
    total_students = df_student_all["NIM"].nunique()
    total_companies = df_company["id_company"].nunique()
    total_requests = len(df_tc)
    total_placement = len(df_ts[df_ts["progress_student"] == "Placement"])
    total_sent = int(df_tc["jumlah_dikirimkan"].sum()) if "jumlah_dikirimkan" in df_tc.columns else 0
    fulfillment_pct = round(total_placement / total_sent * 100, 1) if total_sent > 0 else 0.0

    eligible_count = int(df_eligibility["is_eligible"].sum())
    eligible_pct = round(eligible_count / total_students * 100, 1) if total_students > 0 else 0.0

    # ghosting stats
    reference_date = df_tc["send_date"].max()
    df_ghost_all = metrics.get_ghosting_flags(
        df_ts, tracking_company=df_tc, today=reference_date, include_healthy=True
    )
    df_ghost_only = df_ghost_all[df_ghost_all["progress_student_system"].isin(["FU 1", "FU 2", "FU 3", "Ghosting"])]
    total_ghosted = len(df_ghost_only)
    finished = ["Placement", "Rejected", "Finish"]
    active_in_process = len(df_ts[~df_ts["progress_student"].isin(finished)])
    ghost_pct = round(total_ghosted / active_in_process * 100, 1) if active_in_process > 0 else 0.0

    # avg response time
    valid_resp = df_tc.dropna(subset=["request_date", "send_date"])
    avg_resp = round(
        (valid_resp["send_date"] - valid_resp["request_date"]).dt.days.mean(), 1
    ) if len(valid_resp) > 0 else 0.0

    metric_strip([
        {"label": t("overview.total_students"), "value": f"{total_students:,}"},
        {"label": t("overview.total_companies"), "value": f"{total_companies:,}"},
        {"label": t("overview.total_requests"), "value": f"{total_requests:,}"},
        {
            "label": t("overview.total_placement"),
            "value": f"{total_placement:,}",
            "delta": f"{fulfillment_pct}%",
            "sentiment": "success" if fulfillment_pct >= 30 else "warning",
        },
        {
            "label": t("overview.eligible_rate"),
            "value": f"{eligible_pct}%",
            "sentiment": "success" if eligible_pct >= 50 else "warning",
        },
        {
            "label": t("overview.ghosting_rate"),
            "value": f"{ghost_pct}%",
            "sentiment": "danger" if ghost_pct > 20 else "success",
        },
    ])

    section_divider()

    # charts row 1: placement by type + monthly trend
    col_l, col_r = card_grid(2)

    with col_l:
        with chart_panel(t("overview.placement_by_type"), height=430):
            placed = df_ts[df_ts["progress_student"] == "Placement"]
            if "jenis_penempatan" in placed.columns and not placed["jenis_penempatan"].dropna().empty:
                type_agg = placed["jenis_penempatan"].value_counts().reset_index()
            else:
                merged = placed.merge(
                    df_tc[["id_tracking_company", "jenis_penempatan"]],
                    on="id_tracking_company", how="left",
                    suffixes=("", "_tc"),
                )
                col_name = "jenis_penempatan" if "jenis_penempatan" in merged.columns else "jenis_penempatan_tc"
                type_agg = merged[col_name].value_counts().reset_index()
            type_agg.columns = ["type", "count"]
            if type_agg.empty:
                st.info(t("mc.no_data_filter"))
            else:
                fig = px.pie(
                    type_agg, names="type", values="count", hole=0.5,
                    color="type", color_discrete_map=JENIS_PENEMPATAN_COLORS,
                )
                fig.update_traces(
                    textinfo="label+percent", textposition="outside",
                    pull=[0.02] * len(type_agg),
                )
                apply_plotly_style(fig)
                fig.update_layout(height=360, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

    with col_r:
        with chart_panel(t("overview.monthly_trend"), height=430):
            monthly_data = df_tc.dropna(subset=["request_date"]).copy()
            if monthly_data.empty:
                st.info(t("mc.no_data_filter"))
            else:
                monthly = (
                    monthly_data
                    .groupby(monthly_data["request_date"].dt.to_period("M"))
                    .size().reset_index(name="count")
                )
                monthly["request_date"] = monthly["request_date"].astype(str)
                fig = px.area(
                    monthly, x="request_date", y="count",
                    color_discrete_sequence=[CHART_PALETTE[0]], markers=True,
                )
                apply_plotly_style(fig)
                fig.update_layout(
                    xaxis_title=t("mc.month"),
                    yaxis_title=t("mc.request_count"),
                    height=360,
                )
                fig.update_traces(line=dict(width=2.5), fillcolor="rgba(52,98,237,0.08)")
                st.plotly_chart(fig, use_container_width=True)

    section_divider()

    # charts row 2: top companies + placement by prodi
    col_l2, col_r2 = card_grid(2)

    with col_l2:
        with chart_panel(t("overview.top_companies"), height=430):
            placed = df_ts[df_ts["progress_student"] == "Placement"]
            placed_counts = placed.groupby("company").size().reset_index(name="placements")
            placed_counts = placed_counts.nlargest(10, "placements")
            if placed_counts.empty:
                st.info(t("mc.no_data_filter"))
            else:
                fig = px.bar(
                    placed_counts, x="placements", y="company", orientation="h",
                    color_discrete_sequence=[CHART_PALETTE[0]], text="placements",
                )
                fig.update_traces(textposition="outside")
                apply_plotly_style(fig)
                fig.update_layout(
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis_title="Placements", height=360,
                )
                st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        with chart_panel(t("overview.placement_by_prodi"), height=430):
            placed = df_ts[df_ts["progress_student"] == "Placement"]
            student_prodi = df_status_student[["NIM", "program_studi"]].drop_duplicates()
            placed_prodi = placed.merge(student_prodi, on="NIM", how="left")
            prodi_counts = placed_prodi["program_studi"].value_counts().head(10).reset_index()
            prodi_counts.columns = ["prodi", "count"]
            if prodi_counts.empty:
                st.info(t("mc.no_data_filter"))
            else:
                fig = px.bar(
                    prodi_counts, x="count", y="prodi", orientation="h",
                    color_discrete_sequence=[CHART_PALETTE[1]], text="count",
                )
                fig.update_traces(textposition="outside")
                apply_plotly_style(fig)
                fig.update_layout(
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis_title="Placements", height=360,
                )
                st.plotly_chart(fig, use_container_width=True)

    section_divider()

    # charts row 3: selection stage breakdown (process monitor) + data health summary (data quality)
    col_l3, col_r3 = card_grid(2)

    with col_l3:
        with chart_panel(t("overview.selection_funnel"), height=430):
            stage_counts = df_ts["progress_student"].value_counts().reset_index()
            stage_counts.columns = ["stage", "count"]
            if stage_counts.empty:
                st.info(t("mc.no_data_filter"))
            else:
                fig = px.bar(
                    stage_counts, x="count", y="stage", orientation="h",
                    color_discrete_sequence=[CHART_PALETTE[2]], text="count",
                )
                fig.update_traces(textposition="outside")
                apply_plotly_style(fig)
                fig.update_layout(
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis_title=t("overview.total_students"), height=360,
                )
                st.plotly_chart(fig, use_container_width=True)

    with col_r3:
        with chart_panel(t("overview.data_health"), height=430):
            df_quality = queries.get_data_quality_master()
            if df_quality.empty:
                st.info(t("mc.no_data_filter"))
            else:
                counts = df_quality["staleness"].value_counts().reset_index()
                counts.columns = ["staleness", "count"]
                fig_health = px.pie(
                    counts, names="staleness", values="count", hole=0.55,
                    color="staleness", color_discrete_map=STALENESS_COLORS,
                )
                fig_health.update_traces(
                    textinfo="label+value", textposition="outside",
                    pull=[0.02] * len(counts),
                )
                apply_plotly_style(fig_health)
                fig_health.update_layout(height=360, showlegend=True)
                st.plotly_chart(fig_health, use_container_width=True)

    section_divider()

    # periodic pdf report download section (centered divider above)
    header_title = "Laporan Periodik" if get_lang() == "id" else "Periodic Report"
    st.markdown(
        f"""<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <span class="smile-pdf-badge" style="display:inline-flex; align-items:center; justify-content:center; padding:4px 10px; border-radius:6px; background-color:#3462ED !important; background:#3462ED !important; color:#FFFFFF !important; font-size:12px; font-weight:800; letter-spacing:0.05em; font-family:'Montserrat', sans-serif;"><span style="color:#FFFFFF !important;">PDF</span></span>
            <h3 style="margin:0; font-size:24px; font-weight:800; color:var(--text-color);">{header_title}</h3>
        </div>""",
        unsafe_allow_html=True,
    )
    st.caption(t("overview.report_desc"))

    if "pdf_data" not in st.session_state:
        if st.button(f":material/download: {t('overview.download_report')}", key="btn_gen_pdf", type="primary"):
            spinner_msg = "Membuat laporan PDF..." if get_lang() == "id" else "Generating PDF report..."
            with st.spinner(spinner_msg):
                try:
                    from utils.pdf_report import generate_report_pdf

                    fu_labels = ["FU 1", "FU 2", "FU 3"]
                    ghost_labels = ["Ghosting"]
                    total_fu = len(df_ghost_only[df_ghost_only["progress_student_system"].isin(fu_labels)]) if not df_ghost_only.empty else 0
                    total_ghost_strict = len(df_ghost_only[df_ghost_only["progress_student_system"].isin(ghost_labels)]) if not df_ghost_only.empty else 0

                    df_quality = queries.get_data_quality_master()

                    pdf_bytes = generate_report_pdf(
                        df_student_eligibility=df_eligibility,
                        df_company=df_company,
                        df_tc=df_tc,
                        df_tr=df_tr,
                        df_ts=df_ts,
                        df_student_status=df_status_student,
                        df_quality_master=df_quality,
                        ghosting_stats={
                            "total_ghosted": total_ghost_strict,
                            "total_fu": total_fu,
                        },
                    )
                    st.session_state["pdf_data"] = pdf_bytes
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
    else:
        success_msg = (
            "Laporan berhasil dibuat! Klik tombol di bawah untuk mengunduh."
            if get_lang() == "id" else
            "Report generated successfully! Click the button below to download."
        )
        st.success(success_msg)
        st.download_button(
            label=f":material/download: {t('overview.download_report')}",
            data=st.session_state["pdf_data"],
            file_name=f"SMILE_Report_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            key="btn_download_ready",
            type="primary",
        )


# logo and navigation
_setup_logo()

pg = st.navigation([
    st.Page(overview_page, title=t("page.overview"), icon=":material/dashboard:", default=True),
    st.Page("pages/1_monitor_student.py", title=t("page.monitor_student"), icon=":material/school:"),
    st.Page("pages/2_monitor_company.py", title=t("page.monitor_company"), icon=":material/business:"),
    st.Page("pages/3_monitor_process.py", title=t("page.monitor_process"), icon=":material/sync:"),
    st.Page("pages/4_data_quality.py", title=t("page.data_sync"), icon=":material/verified:"),
])

render_sidebar_footer()
pg.run()
