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

# inject global css theme and layout styles
inject_global_css()


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
    # overview page with interactive summary and placement recapitulation
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

    # global kpi strip (always visible)
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

    # section 1: ringkasan sistem (interactive overview)
    section_divider()

    st.markdown(f'''
        <h3 style='margin-bottom: 0.2rem;'>{t("overview.section1_title")}</h3>
        <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("overview.section1_sub")}</p>
        <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
    ''', unsafe_allow_html=True)

    # interactive chart selector
    chart_options = [
        t("overview.s1_placement_trend"),
        t("overview.s1_eligibility"),
        t("overview.s1_stage_funnel"),
        t("overview.s1_data_health"),
    ]
    s1_sel = st.radio(
        t("overview.section1_chart_label"),
        chart_options,
        horizontal=True,
        key="overview_s1_chart",
        label_visibility="visible",
    )

    if s1_sel == t("overview.s1_placement_trend"):
        # placement trend and type breakdown
        col_trend, col_type = st.columns([3, 2])

        with col_trend:
            with chart_panel(t("overview.monthly_trend"), height=430, subtitle=t("mc.chart_monthly_sub")):
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

        with col_type:
            with chart_panel(t("overview.placement_by_type"), height=430, subtitle=t("mr.chart_type_dist_sub")):
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
                    fig.update_layout(height=360, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

    elif s1_sel == t("overview.s1_eligibility"):
        # eligibility bar chart and donut chart
        col_e1, col_e2 = st.columns([3, 2])

        with col_e1:
            with chart_panel(t("ms.chart_elig_prodi"), height=430, subtitle=t("ms.chart_elig_prodi_sub")):
                ELIGIBILITY_COLORS = {"Eligible": CHART_PALETTE[0], "Ineligible": CHART_PALETTE[2]}
                by_prodi = (
                    df_eligibility
                    .assign(elig=df_eligibility["is_eligible"].map({True: "Eligible", False: "Ineligible"}))
                    .groupby(["program_studi", "elig"]).size().reset_index(name="jumlah")
                )
                if by_prodi.empty:
                    st.info(t("mc.no_data_filter"))
                else:
                    fig = px.bar(
                        by_prodi, x="program_studi", y="jumlah", color="elig",
                        barmode="stack",
                        color_discrete_map=ELIGIBILITY_COLORS,
                        category_orders={"elig": ["Eligible", "Ineligible"]},
                        height=350,
                    )
                    fig.update_layout(
                        xaxis_title="", yaxis_title=t("ms.student_count"),
                        xaxis_tickangle=-25, legend_title_text="",
                        margin=dict(t=10, b=10, l=10, r=10),
                    )
                    apply_plotly_style(fig)
                    st.plotly_chart(fig, use_container_width=True)

        with col_e2:
            with chart_panel(t("ms.chart_elig_comp"), height=430, subtitle=t("ms.chart_elig_comp_sub")):
                ELIGIBILITY_COLORS = {"Eligible": CHART_PALETTE[0], "Ineligible": CHART_PALETTE[2]}
                comp = (
                    df_eligibility["is_eligible"]
                    .map({True: "Eligible", False: "Ineligible"})
                    .value_counts().reset_index()
                )
                comp.columns = ["status", "jumlah"]
                if comp.empty:
                    st.info(t("mc.no_data_filter"))
                else:
                    fig = px.pie(
                        comp, names="status", values="jumlah", hole=0.55, color="status",
                        color_discrete_map=ELIGIBILITY_COLORS,
                        height=350,
                    )
                    fig.update_traces(textinfo="label+percent")
                    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                    apply_plotly_style(fig)
                    st.plotly_chart(fig, use_container_width=True)

    elif s1_sel == t("overview.s1_stage_funnel"):
        # stage distribution and top companies
        col_f1, col_f2 = st.columns([3, 2])

        with col_f1:
            with chart_panel(t("overview.selection_funnel"), height=430, subtitle=t("mp.stage_dist_sub") if "mp.stage_dist_sub" in dir() else "Distribusi tahapan seleksi saat ini"):
                stage_counts = df_ts["progress_student"].value_counts().reset_index()
                stage_counts.columns = ["stage", "count"]
                stage_counts = stage_counts.sort_values("count", ascending=True)
                if stage_counts.empty:
                    st.info(t("mc.no_data_filter"))
                else:
                    fig = px.bar(
                        stage_counts, x="count", y="stage", orientation="h",
                        color_discrete_sequence=[CHART_PALETTE[0]], text="count",
                    )
                    fig.update_traces(textposition="outside")
                    apply_plotly_style(fig)
                    fig.update_layout(
                        yaxis=dict(categoryorder="total ascending", title=""),
                        xaxis_title=t("overview.total_students"), height=360,
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with col_f2:
            with chart_panel(t("overview.top_companies"), height=430, subtitle=t("mc.chart_top_companies_sub")):
                placed = df_ts[df_ts["progress_student"] == "Placement"]
                placed_counts_c = placed.groupby("company").size().reset_index(name="placements")
                placed_counts_c = placed_counts_c.nlargest(10, "placements").sort_values("placements", ascending=True)
                if placed_counts_c.empty:
                    st.info(t("mc.no_data_filter"))
                else:
                    fig = px.bar(
                        placed_counts_c, x="placements", y="company", orientation="h",
                        color_discrete_sequence=[CHART_PALETTE[1]], text="placements",
                    )
                    fig.update_traces(textposition="outside")
                    apply_plotly_style(fig)
                    fig.update_layout(
                        yaxis=dict(categoryorder="total ascending", title=""),
                        xaxis_title="Placements", height=360,
                    )
                    st.plotly_chart(fig, use_container_width=True)

    elif s1_sel == t("overview.s1_data_health"):
        # data health staleness and ghosting charts
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            with chart_panel(t("overview.data_health"), height=430, subtitle=t("dq.staleness_sub") if "dq.staleness_sub" in dir() else "Distribusi keusangan sinkronisasi data mahasiswa"):
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

        with col_d2:
            with chart_panel(t("overview.ghosting_rate"), height=430, subtitle=t("mp.ghost_sub") if "mp.ghost_sub" in dir() else "Proporsi ghosting dan FU pada kandidat aktif"):
                healthy_c = max(0, active_in_process - total_ghosted)
                fu_count = len(df_ghost_only[df_ghost_only["progress_student_system"].isin(["FU 1", "FU 2", "FU 3"])])
                ghost_strict = len(df_ghost_only[df_ghost_only["progress_student_system"] == "Ghosting"])
                ghost_labels = ["Healthy", "FU 1-3", "Ghosting"]
                ghost_vals = [healthy_c, fu_count, ghost_strict]
                ghost_colors = [COLORS["primary"], COLORS["warning"], COLORS["danger"]]
                fig_ghost = px.pie(
                    values=ghost_vals, names=ghost_labels, hole=0.55,
                    color_discrete_sequence=ghost_colors,
                )
                fig_ghost.update_traces(
                    textinfo="label+percent", textposition="outside",
                    pull=[0.02, 0.04, 0.06],
                )
                apply_plotly_style(fig_ghost)
                fig_ghost.update_layout(height=360, showlegend=False)
                st.plotly_chart(fig_ghost, use_container_width=True)

    # section 2: rekapitulasi placement (bt-07)
    section_divider()

    st.markdown(f'''
        <h3 style='margin-bottom: 0.2rem;'>{t("overview.section2_title")}</h3>
        <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("overview.section2_sub")}</p>
        <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
    ''', unsafe_allow_html=True)

    # chart selector for section 2
    bt07_options = [
        t("overview.bt07_by_semester"),
        t("overview.bt07_by_prodi"),
        t("overview.bt07_by_company"),
        t("overview.bt07_by_type"),
    ]
    bt07_sel = st.radio(
        t("overview.bt07_chart_selector"),
        bt07_options,
        horizontal=True,
        key="overview_bt07_chart",
        label_visibility="visible",
    )

    # merge student status and tracking data
    student_prodi = df_status_student[["NIM", "program_studi", "semester"]].drop_duplicates()
    placed_df = df_ts[df_ts["progress_student"] == "Placement"].copy()
    placed_merged = placed_df.merge(student_prodi, on="NIM", how="left")
    # merge company info
    placed_merged = placed_merged.merge(
        df_tc[["id_tracking_company", "jenis_penempatan"]].drop_duplicates(),
        on="id_tracking_company", how="left", suffixes=("", "_tc"),
    )
    if "jenis_penempatan_tc" in placed_merged.columns and "jenis_penempatan" not in placed_merged.columns:
        placed_merged = placed_merged.rename(columns={"jenis_penempatan_tc": "jenis_penempatan"})

    if bt07_sel == t("overview.bt07_by_semester"):
        with chart_panel(t("overview.bt07_placement_semester"), height=520, subtitle="Jumlah mahasiswa yang berhasil ditempatkan pada tiap semester akademik"):
            if placed_merged.empty or "semester" not in placed_merged.columns:
                st.info(t("mc.no_data_filter"))
            else:
                sem_counts = placed_merged["semester"].value_counts().reset_index()
                sem_counts.columns = ["semester", "count"]
                sem_counts["semester"] = sem_counts["semester"].astype(str)
                sem_counts = sem_counts.sort_values("semester")

                fig = px.bar(
                    sem_counts, x="semester", y="count",
                    color_discrete_sequence=[CHART_PALETTE[0]], text="count",
                )
                fig.update_traces(textposition="outside", marker_color=CHART_PALETTE[0])
                apply_plotly_style(fig)
                fig.update_layout(
                    xaxis_title="Semester",
                    yaxis_title="Jumlah Placement",
                    height=440,
                    xaxis=dict(type="category"),
                    margin=dict(t=20, b=20, l=20, r=20),
                )
                fig.update_yaxes(range=[0, sem_counts["count"].max() * 1.2 if not sem_counts.empty else 10])
                st.plotly_chart(fig, use_container_width=True)

                # summary table for semester placement
                total_placed_s = int(sem_counts["count"].sum())
                st.caption(f"Total mahasiswa placed: **{total_placed_s:,}** | Rata-rata per semester: **{total_placed_s / len(sem_counts):.1f}**")

    elif bt07_sel == t("overview.bt07_by_prodi"):
        with chart_panel(t("overview.bt07_placement_prodi"), height=520, subtitle="Jumlah mahasiswa yang berhasil ditempatkan per program studi"):
            if placed_merged.empty or "program_studi" not in placed_merged.columns:
                st.info(t("mc.no_data_filter"))
            else:
                prodi_counts = placed_merged["program_studi"].value_counts().reset_index()
                prodi_counts.columns = ["prodi", "count"]
                prodi_counts = prodi_counts.sort_values("count", ascending=True)

                fig = px.bar(
                    prodi_counts, x="count", y="prodi", orientation="h",
                    color="count", color_continuous_scale=["#1D4044", "#3462ED"], text="count",
                )
                fig.update_traces(textposition="outside", cliponaxis=False)
                apply_plotly_style(fig)
                fig.update_layout(
                    xaxis_title="Jumlah Placement",
                    yaxis_title="",
                    height=440,
                    coloraxis_showscale=False,
                    margin=dict(t=20, b=20, l=20, r=40),
                )
                st.plotly_chart(fig, use_container_width=True)

                total_placed_pr = int(prodi_counts["count"].sum())
                st.caption(f"Total mahasiswa placed: **{total_placed_pr:,}** | Program studi: **{len(prodi_counts)}**")

    elif bt07_sel == t("overview.bt07_by_company"):
        with chart_panel(t("overview.bt07_placement_company"), height=520, subtitle="10 perusahaan dengan jumlah mahasiswa yang berhasil ditempatkan terbanyak"):
            placed_cols = df_ts[df_ts["progress_student"] == "Placement"]
            if placed_cols.empty or "company" not in placed_cols.columns:
                st.info(t("mc.no_data_filter"))
            else:
                company_counts = (
                    placed_cols.groupby("company")
                    .size().reset_index(name="count")
                    .nlargest(10, "count")
                    .sort_values("count", ascending=True)
                )

                fig = px.bar(
                    company_counts, x="count", y="company", orientation="h",
                    color="count", color_continuous_scale=["#1D4044", "#3462ED"], text="count",
                )
                fig.update_traces(textposition="outside", cliponaxis=False)
                apply_plotly_style(fig)
                fig.update_layout(
                    xaxis_title="Jumlah Placement",
                    yaxis_title="",
                    height=440,
                    coloraxis_showscale=False,
                    margin=dict(t=20, b=20, l=20, r=40),
                )
                st.plotly_chart(fig, use_container_width=True)

                total_top10 = int(company_counts["count"].sum())
                grand_total = int(placed_cols.shape[0])
                st.caption(f"Total placed di Top 10 perusahaan: **{total_top10:,}** dari **{grand_total:,}** total placement")

    elif bt07_sel == t("overview.bt07_by_type"):
        with chart_panel(t("overview.bt07_placement_type"), height=520, subtitle="Distribusi mahasiswa yang berhasil ditempatkan berdasarkan jenis penempatan (Magang, Full-time, Part-time)"):
            if placed_merged.empty:
                st.info(t("mc.no_data_filter"))
            else:
                jenis_col = "jenis_penempatan"
                if jenis_col not in placed_merged.columns or placed_merged[jenis_col].dropna().empty:
                    st.info(t("mc.no_data_filter"))
                else:
                    jenis_counts = placed_merged[jenis_col].value_counts().reset_index()
                    jenis_counts.columns = ["type", "count"]

                    col_chart, col_stats = st.columns([3, 1])
                    with col_chart:
                        fig = px.pie(
                            jenis_counts, names="type", values="count", hole=0.55,
                            color="type", color_discrete_map=JENIS_PENEMPATAN_COLORS,
                        )
                        fig.update_traces(
                            textinfo="label+value+percent",
                            textposition="outside",
                            pull=[0.02] * len(jenis_counts),
                        )
                        apply_plotly_style(fig)
                        fig.update_layout(height=400, showlegend=False, margin=dict(t=40, b=40, l=40, r=40))
                        st.plotly_chart(fig, use_container_width=True)

                    with col_stats:
                        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
                        total_p = int(jenis_counts["count"].sum())
                        for _, row in jenis_counts.iterrows():
                            pct = round(row["count"] / total_p * 100, 1) if total_p > 0 else 0
                            color = JENIS_PENEMPATAN_COLORS.get(row["type"], CHART_PALETTE[0])
                            st.markdown(
                                f"""<div style="margin-bottom:16px; padding:12px 16px; border-radius:8px;
                                    background:var(--bg-color); border-left:4px solid {color};
                                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                                    <div style="font-size:11px; font-weight:700; text-transform:uppercase;
                                        color:var(--text-color); opacity:0.6; margin-bottom:4px;">{row["type"]}</div>
                                    <div style="font-size:22px; font-weight:800; color:{color};">{int(row["count"]):,}</div>
                                    <div style="font-size:12px; color:var(--text-color); opacity:0.7;">{pct}% dari total</div>
                                </div>""",
                                unsafe_allow_html=True,
                            )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.info(t("overview.bt07_note"), icon=":material/bar_chart:")

    section_divider()

    # periodic pdf report download section
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


# setup navigation and render sidebar
_setup_logo()

pg = st.navigation([
    st.Page(overview_page, title=t("page.overview"), icon=":material/dashboard:", default=True),
    st.Page("pages/1_monitor_student.py", title=t("page.monitor_student"), icon=":material/school:"),
    st.Page("pages/2_monitor_company.py", title=t("page.monitor_company"), icon=":material/business:"),
    st.Page("pages/5_monitor_request.py", title=t("page.monitor_request"), icon=":material/request_page:"),
    st.Page("pages/3_monitor_process.py", title=t("page.monitor_process"), icon=":material/sync:"),
    st.Page("pages/4_data_quality.py", title=t("page.data_sync"), icon=":material/verified:"),
])

render_sidebar_footer()
pg.run()
