# monitor request - bt-03 talent request analytics (characteristics, distribution, remuneration, priority)

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.layout import (
    inject_global_css, page_header, metric_strip,
    chart_panel, card_grid, section_divider, table_panel, filter_bar,
)
from utils.theme import (
    COLORS, CHART_PALETTE, JENIS_PENEMPATAN_COLORS,
    PIPELINE_COLORS, apply_plotly_style,
)
from utils.data_loader import load_csv_table
from utils.i18n import t

inject_global_css()

page_header(
    t("page.monitor_request"),
    bt_caption=t("bt.03_request"),
)

# load data
df_company = load_csv_table("company")
df_tc = load_csv_table("tracking_company")
df_tr = load_csv_table("talent_request")
df_ts = load_csv_table("tracking_student")

# parse dates
df_tc["request_date"] = pd.to_datetime(df_tc["request_date"], dayfirst=True, errors="coerce")
df_tc["send_date"] = pd.to_datetime(df_tc["send_date"], dayfirst=True, errors="coerce")
df_tr["request_date"] = pd.to_datetime(df_tr["request_date"], errors="coerce")

# enrich tracking_company with additional fields for filtering
df_tc_enriched = df_tc.merge(
    df_tr[["id_talent_req", "industri_sektor", "headcount", "working_arrangement",
           "durasi", "bidang_studi_dibutuhkan", "deskripsi_requirement", "renumerasi", "sumber_baris_form"]],
    on="id_talent_req", how="left",
)
df_tc_enriched = df_tc_enriched.merge(
    df_company[["id_company", "skala_perusahaan", "company_type", "kota"]],
    on="id_company", how="left",
)

# filters
with filter_bar():
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        sel_jenis = st.multiselect(
            t("mr.placement_type"),
            options=sorted(df_tc_enriched["jenis_penempatan"].dropna().unique()),
            default=[], key="mr_jenis",
        )
    with fc2:
        sel_industry = st.multiselect(
            t("mr.industry_sector"),
            options=sorted(df_tc_enriched["industri_sektor"].dropna().unique()),
            default=[], key="mr_industry",
        )
    with fc3:
        sel_progress = st.multiselect(
            t("mr.request_progress"),
            options=sorted(df_tc_enriched["progress"].dropna().unique()),
            default=[], key="mr_progress",
        )
    with fc4:
        sel_scale = st.multiselect(
            t("mr.company_scale"),
            options=sorted(df_tc_enriched["skala_perusahaan"].dropna().unique()),
            default=[], key="mr_scale",
        )

    date_col, _ = st.columns([1, 1])
    with date_col:
        valid_dates = df_tc_enriched["request_date"].dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
        else:
            min_date = pd.Timestamp("2023-01-01").date()
            max_date = pd.Timestamp("2026-12-31").date()
        date_range = st.date_input(
            t("mr.date_range"),
            value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
            key="mr_dates",
        )

# apply filters
filtered = df_tc_enriched.copy()
if sel_jenis:
    filtered = filtered[filtered["jenis_penempatan"].isin(sel_jenis)]
if sel_industry:
    filtered = filtered[filtered["industri_sektor"].isin(sel_industry)]
if sel_progress:
    filtered = filtered[filtered["progress"].isin(sel_progress)]
if sel_scale:
    filtered = filtered[filtered["skala_perusahaan"].isin(sel_scale)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt = pd.Timestamp(date_range[1])
    mask = filtered["request_date"].notna()
    filtered = filtered[mask & (filtered["request_date"] >= start_dt) & (filtered["request_date"] <= end_dt)]

# linked tracking_student rows
tc_ids = set(filtered["id_tracking_company"])
filtered_ts = df_ts[df_ts["id_tracking_company"].isin(tc_ids)]

# kpi metrics
total_requests = len(filtered)
total_headcount = int(filtered["jumlah_permintaan"].sum())
total_sent = int(filtered["jumlah_dikirimkan"].sum())
placements = len(filtered_ts[filtered_ts["progress_student"] == "Placement"])
fulfillment_pct = round(placements / total_headcount * 100, 1) if total_headcount > 0 else 0.0

valid_resp = filtered.dropna(subset=["request_date", "send_date"])
avg_resp_days = round(
    (valid_resp["send_date"] - valid_resp["request_date"]).dt.days.mean(), 1
) if len(valid_resp) > 0 else 0.0

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
metric_strip([
    {"label": t("mr.total_requests"), "value": f"{total_requests:,}"},
    {"label": t("mr.total_headcount"), "value": f"{total_headcount:,}"},
    {"label": t("mr.candidates_sent"), "value": f"{total_sent:,}"},
    {
        "label": t("mr.fulfillment_rate"),
        "value": f"{fulfillment_pct}%",
        "delta": f"{placements:,} {t('overview.placed')}",
        "sentiment": "success" if fulfillment_pct >= 50 else "warning" if fulfillment_pct >= 25 else "danger",
    },
    {"label": t("mr.avg_response"), "value": f"{avg_resp_days} {t('mr.days')}"},
])

# karakteristik dan kebutuhan talent
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mr.characteristics_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mr.characteristics_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

col_r1_1, col_r1_2, col_r1_3 = st.columns(3)

with col_r1_1:
    with chart_panel(t("mr.chart_type_dist"), height=460, subtitle=t("mr.chart_type_dist_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            jenis_agg = filtered["jenis_penempatan"].value_counts().reset_index()
            jenis_agg.columns = ["type", "count"]
            fig = px.pie(
                jenis_agg, names="type", values="count", hole=0.5,
                color="type", color_discrete_map=JENIS_PENEMPATAN_COLORS,
            )
            fig.update_traces(
                textinfo="label+percent", textposition="outside",
                pull=[0.02] * len(jenis_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=False, margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

with col_r1_2:
    with chart_panel(t("mr.chart_working_arr"), height=460, subtitle=t("mr.chart_working_arr_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            wa_agg = filtered["working_arrangement"].value_counts().reset_index()
            wa_agg.columns = ["arrangement", "count"]
            wa_colors = {
                "WFO": CHART_PALETTE[0],
                "Hybrid": CHART_PALETTE[2],
                "WFH": CHART_PALETTE[4],
            }
            fig = px.pie(
                wa_agg, names="arrangement", values="count", hole=0.5,
                color="arrangement", color_discrete_map=wa_colors,
            )
            fig.update_traces(
                textinfo="label+percent", textposition="outside",
                pull=[0.02] * len(wa_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=False, margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

with col_r1_3:
    with chart_panel(t("mr.chart_duration"), height=460, subtitle=t("mr.chart_duration_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            durasi_col = "durasi" if "durasi" in filtered.columns else None
            if durasi_col is None:
                dur_map = dict(zip(df_tr["id_talent_req"], df_tr["durasi"]))
                filtered["durasi"] = filtered["id_talent_req"].map(dur_map).fillna("Unknown")
                durasi_col = "durasi"

            durasi_agg = filtered[durasi_col].value_counts().reset_index()
            durasi_agg.columns = ["durasi", "count"]

            fig = px.pie(
                durasi_agg, names="durasi", values="count", hole=0.5,
                color_discrete_sequence=CHART_PALETTE,
            )
            fig.update_traces(
                textinfo="label+percent", textposition="outside",
                pull=[0.02] * len(durasi_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=False, margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)


# operasional dan pipeline
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mr.ops_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mr.ops_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

col_r2_left, col_r2_right = st.columns(2)

with col_r2_left:
    with chart_panel(t("mr.chart_sumber_form"), height=460, subtitle=t("mr.chart_sumber_form_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            if "sumber_baris_form" not in filtered.columns:
                sumber_map = dict(zip(df_tr["id_talent_req"], df_tr["sumber_baris_form"]))
                filtered["sumber_baris_form"] = filtered["id_talent_req"].map(sumber_map).fillna("Unknown")

            sumber_agg = filtered["sumber_baris_form"].value_counts().reset_index()
            sumber_agg.columns = ["source", "count"]
            fig = px.pie(
                sumber_agg, names="source", values="count", hole=0.5,
                color_discrete_sequence=CHART_PALETTE,
            )
            fig.update_traces(
                textinfo="label+percent", textposition="outside",
                pull=[0.02] * len(sumber_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=False, margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

with col_r2_right:
    with chart_panel(t("mr.chart_pipeline"), height=460, subtitle=t("mr.chart_pipeline_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            pipeline_order = ["Draft", "Submitted", "On Review", "Shortlisted", "Closed"]
            progress_agg = (
                filtered["progress"]
                .value_counts()
                .reindex(pipeline_order, fill_value=0)
                .reset_index()
            )
            progress_agg.columns = ["stage", "count"]
            fig = px.bar(
                progress_agg, x="count", y="stage", orientation="h",
                color="stage", color_discrete_map=PIPELINE_COLORS, text="count",
            )
            fig.update_traces(textposition="outside", showlegend=False)
            apply_plotly_style(fig)
            fig.update_layout(
                yaxis=dict(
                    categoryorder="array",
                    categoryarray=list(reversed(pipeline_order)),
                    title="",
                ),
                xaxis_title=t("mr.count"), height=400,
            )
            st.plotly_chart(fig, use_container_width=True)


# analisis kebutuhan prodi dan tools
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mr.demand_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mr.demand_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

col_r3_left, col_r3_right = st.columns(2)

with col_r3_left:
    with chart_panel(t("mr.chart_prodi_demand"), height=460, subtitle=t("mr.chart_prodi_demand_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            if "bidang_studi_dibutuhkan" not in filtered.columns:
                prodi_map = dict(zip(df_tr["id_talent_req"], df_tr["bidang_studi_dibutuhkan"]))
                filtered["bidang_studi_dibutuhkan"] = filtered["id_talent_req"].map(prodi_map).fillna("")

            all_prodi = []
            for val in filtered["bidang_studi_dibutuhkan"].dropna().astype(str):
                all_prodi.extend([p.strip() for p in val.split(",") if p.strip()])

            if not all_prodi:
                st.info(t("mr.no_data_filter"))
            else:
                prodi_df = pd.Series(all_prodi).value_counts().head(10).reset_index()
                prodi_df.columns = ["Prodi", "Count"]
                prodi_df = prodi_df.sort_values("Count", ascending=True)

                fig = px.bar(
                    prodi_df, x="Count", y="Prodi", orientation="h",
                    text="Count", color="Count", color_continuous_scale=["#1D4044", "#3462ED"]
                )
                apply_plotly_style(fig)
                fig.update_layout(height=400, margin=dict(t=10, l=10, r=20, b=0), xaxis_title="", yaxis_title="", coloraxis_showscale=False)
                fig.update_traces(textposition="outside", cliponaxis=False)
                st.plotly_chart(fig, use_container_width=True)

with col_r3_right:
    with chart_panel(t("mr.chart_tools_demand"), height=460, subtitle=t("mr.chart_tools_demand_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            if "deskripsi_requirement" not in filtered.columns:
                desc_map = dict(zip(df_tr["id_talent_req"], df_tr["deskripsi_requirement"]))
                filtered["deskripsi_requirement"] = filtered["id_talent_req"].map(desc_map).fillna("")

            # Get unique tools from status_student
            df_student = load_csv_table("status_student")
            all_student_tools = []
            for tools_list in df_student["tools"].dropna().astype(str):
                all_student_tools.extend([t_item.strip() for t_item in tools_list.split(",") if t_item.strip()])
            unique_tools = set(all_student_tools)

            tool_counts = {tool: 0 for tool in unique_tools}
            for desc in filtered["deskripsi_requirement"].dropna().astype(str):
                desc_lower = desc.lower()
                for tool in unique_tools:
                    if tool.lower() in desc_lower:
                        tool_counts[tool] += 1

            tools_df = pd.DataFrame(list(tool_counts.items()), columns=["Tool", "Count"])
            tools_df = tools_df[tools_df["Count"] > 0]

            if tools_df.empty:
                st.info(t("mr.no_data_filter"))
            else:
                tools_df = tools_df.sort_values("Count", ascending=False).head(10).sort_values("Count", ascending=True)

                fig = px.bar(
                    tools_df, x="Count", y="Tool", orientation="h",
                    text="Count", color="Count", color_continuous_scale=["#1D4044", "#3462ED"]
                )
                apply_plotly_style(fig)
                fig.update_layout(height=400, margin=dict(t=10, l=10, r=20, b=0), xaxis_title="", yaxis_title="", coloraxis_showscale=False)
                fig.update_traces(textposition="outside", cliponaxis=False)
                st.plotly_chart(fig, use_container_width=True)


# analisis gaji dan remunerasi
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mr.salary_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mr.salary_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)


def extract_salary(val):
    import re
    val = str(val).lower()
    if "rp" not in val:
        return pd.NA
    digits = re.sub(r'[^0-9]', '', val)
    if digits:
        return float(digits)
    return pd.NA


# Compute salary series
if "renumerasi" not in filtered.columns:
    renum_map = dict(zip(df_tr["id_talent_req"], df_tr["renumerasi"]))
    filtered["renumerasi"] = filtered["id_talent_req"].map(renum_map).fillna("Unknown")

filtered["salary_num"] = filtered["renumerasi"].apply(extract_salary)
paid_reqs = filtered.dropna(subset=["salary_num"])

col_r4_left, col_r4_right = st.columns(2)

with col_r4_left:
    with chart_panel(t("mr.chart_remuneration"), height=460, subtitle=t("mr.chart_remuneration_sub")):
        if filtered.empty:
            st.info(t("mr.no_data_filter"))
        else:
            def categorize_renum(val):
                v = str(val).lower()
                if "non-paid" in v or "tidak dibayar" in v:
                    return "Non-Paid"
                elif "transport" in v:
                    return "Uang Transport"
                elif "rp" in v:
                    return "Paid"
                return "Unknown"

            filtered["renumerasi_cat"] = filtered["renumerasi"].apply(categorize_renum)
            renum_agg = filtered[filtered["renumerasi_cat"] != "Unknown"]["renumerasi_cat"].value_counts().reset_index()
            renum_agg.columns = ["type", "count"]
            renum_agg = renum_agg.sort_values("count", ascending=True)

            fig = px.bar(
                renum_agg, x="count", y="type", orientation="h",
                text="count", color="count", color_continuous_scale=["#1D4044", "#3462ED"]
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, margin=dict(t=10, l=10, r=20, b=0), xaxis_title="", yaxis_title="", coloraxis_showscale=False)
            fig.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig, use_container_width=True)

with col_r4_right:
    with chart_panel(t("mr.chart_salary_dist"), height=460, subtitle=t("mr.chart_salary_dist_sub")):
        if paid_reqs.empty:
            st.info(t("mr.no_data_filter"))
        else:
            fig = px.histogram(
                paid_reqs, x="salary_num", nbins=10,
                color_discrete_sequence=[CHART_PALETTE[2]]
            )
            apply_plotly_style(fig)
            fig.update_layout(
                xaxis_title="Remunerasi (Rp)", yaxis_title="Jumlah Request", height=400,
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=True)

# Average salary by category (full width)
with chart_panel(t("mr.chart_salary_avg"), height=460, subtitle=t("mr.chart_salary_avg_sub")):
    if paid_reqs.empty:
        st.info(t("mr.no_data_filter"))
    else:
        view_mode = st.radio("Kategori:", ["Program Studi", "Tools"], horizontal=True, label_visibility="collapsed", key="mr_salary_mode")

        if view_mode == "Program Studi":
            prodi_salaries = []
            for _, row in paid_reqs.iterrows():
                prodis = [p.strip() for p in str(row.get("bidang_studi_dibutuhkan", "")).split(",") if p.strip()]
                sal = row["salary_num"]
                for p in prodis:
                    prodi_salaries.append({"Prodi": p, "Salary": sal})

            if prodi_salaries:
                sal_df = pd.DataFrame(prodi_salaries)
                sal_agg = sal_df.groupby("Prodi")["Salary"].mean().reset_index().sort_values("Salary", ascending=False).head(10).sort_values("Salary", ascending=True)
                fig = px.bar(
                    sal_agg, x="Salary", y="Prodi", orientation="h",
                    text="Salary", color="Salary", color_continuous_scale=["#1D4044", "#3462ED"]
                )
                fig.update_traces(texttemplate='Rp %{text:,.0f}', textposition="outside")
            else:
                fig = None
        else:
            if "unique_tools" not in dir():
                df_student = load_csv_table("status_student")
                all_student_tools_s = []
                for tools_list in df_student["tools"].dropna().astype(str):
                    all_student_tools_s.extend([t_item.strip() for t_item in tools_list.split(",") if t_item.strip()])
                unique_tools = set(all_student_tools_s)

            tool_salaries = {tool: [] for tool in unique_tools}
            for _, row in paid_reqs.iterrows():
                desc_lower = str(row.get("deskripsi_requirement", "")).lower()
                sal = row["salary_num"]
                for tool in unique_tools:
                    if tool.lower() in desc_lower:
                        tool_salaries[tool].append(sal)

            avg_tools = []
            for tool, sals in tool_salaries.items():
                if sals:
                    avg_tools.append({"Tool": tool, "Salary": sum(sals) / len(sals)})

            if avg_tools:
                sal_df = pd.DataFrame(avg_tools)
                sal_agg = sal_df.sort_values("Salary", ascending=False).head(10).sort_values("Salary", ascending=True)
                fig = px.bar(
                    sal_agg, x="Salary", y="Tool", orientation="h",
                    text="Salary", color="Salary", color_continuous_scale=["#1D4044", "#3462ED"]
                )
                fig.update_traces(texttemplate='Rp %{text:,.0f}', textposition="outside")
            else:
                fig = None

        if fig:
            apply_plotly_style(fig)
            fig.update_layout(height=380, margin=dict(t=10, l=10, r=40, b=0), xaxis_title="", yaxis_title="", coloraxis_showscale=False)
            fig.update_xaxes(showticklabels=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t("mr.no_data_filter"))


# detail table
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mr.detail_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mr.detail_title_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

with table_panel("", height=500):
    search_term = st.text_input(
        t("mr.search_label"), key="mr_search",
        placeholder=t("mr.search_placeholder"),
    )

    placed_counts = df_ts[df_ts["progress_student"] == "Placement"].groupby("id_tracking_company").size()

    def calculate_priority(row):
        req_date = pd.to_datetime(row.get("request_date"))
        if pd.isna(req_date):
            age_score = 0
        else:
            days_open = (pd.Timestamp.now() - req_date).days
            days_open = max(0, days_open)
            age_score = min(days_open / 30, 1.0) * 100

        requested = float(row.get("jumlah_permintaan", 0))
        if requested <= 0:
            hc_gap_score = 0
        else:
            tc_id = row.get("id_tracking_company")
            placed = placed_counts.get(tc_id, 0)
            hc_gap_score = max(0, (requested - placed) / requested) * 100

        progress = str(row.get("progress", "")).strip()
        prog_map = {"Draft": 100, "Submitted": 80, "On Review": 60, "Shortlisted": 40, "Closed": 0}
        prog_score = prog_map.get(progress, 0)

        ptype = str(row.get("jenis_penempatan", "")).strip()
        type_map = {"Full-time": 100, "Magang": 70, "Part-time": 50}
        type_score = type_map.get(ptype, 0)

        priority = (0.35 * age_score) + (0.30 * hc_gap_score) + (0.25 * prog_score) + (0.10 * type_score)
        return round(priority, 1)

    filtered["priority_score"] = filtered.apply(calculate_priority, axis=1)

    def get_priority_level(score):
        if score >= 75: return "High"
        if score >= 50: return "Medium"
        return "Low"

    filtered["priority_level"] = filtered["priority_score"].apply(get_priority_level)

    filtered["request_date"] = pd.to_datetime(filtered["request_date"], errors="coerce").dt.strftime('%d-%m-%Y')

    filtered["hc_gap"] = filtered.apply(
        lambda row: max(0, int(float(row.get("jumlah_permintaan", 0))) - int(float(row.get("jumlah_dikirimkan", 0)))),
        axis=1
    )

    display_cols = [
        "nama_perusahaan", "posisi", "jenis_penempatan",
        "jumlah_permintaan", "jumlah_dikirimkan", "hc_gap", "progress",
        "request_date", "priority_score", "priority_level",
    ]
    available_cols = [c for c in display_cols if c in filtered.columns]
    detail_df = filtered[available_cols].copy()
    detail_df = detail_df.sort_values("priority_score", ascending=False)

    col_labels = {
        "nama_perusahaan": "Company",
        "posisi": "Position",
        "jenis_penempatan": "Type",
        "jumlah_permintaan": "Requested",
        "jumlah_dikirimkan": "Sent",
        "hc_gap": "Gap",
        "progress": "Progress",
        "request_date": "Request Date",
        "priority_score": "Priority Score",
        "priority_level": "Priority Level",
    }
    detail_df = detail_df.rename(columns=col_labels)

    if search_term:
        mask = detail_df.apply(
            lambda row: search_term.lower() in str(row.values).lower(), axis=1
        )
        detail_df = detail_df[mask]

    def style_priority(val):
        if val == "High":
            return "background-color: #FEE2E2; color: #DC2626; font-weight: bold;"
        elif val == "Medium":
            return "background-color: #FEF3C7; color: #D97706; font-weight: bold;"
        elif val == "Low":
            return "background-color: #D1FAE5; color: #059669; font-weight: bold;"
        return ""

    if "Priority Level" in detail_df.columns:
        styled_df = detail_df.style.map(style_priority, subset=["Priority Level"])
    else:
        styled_df = detail_df

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Priority Score": st.column_config.ProgressColumn(
                "Priority Score", min_value=0, max_value=100, format="%.1f"
            ),
        }
    )
    st.caption(t("mr.showing_records", shown=f"{len(detail_df):,}", total=f"{total_requests:,}"))
