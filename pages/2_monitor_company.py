# monitor company - company demographics, volume, trend, and performance leaderboard (bt-03, bt-04)

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
from utils import metrics

inject_global_css()

page_header(
    t("page.monitor_company"),
    bt_caption=t("bt.03_04"),
)

# load core tables
df_company = load_csv_table("company")
df_tc = load_csv_table("tracking_company")
df_tr = load_csv_table("talent_request")
df_ts = load_csv_table("tracking_student")

# parse request and send dates
df_tc["request_date"] = pd.to_datetime(df_tc["request_date"], dayfirst=True, errors="coerce")
df_tc["send_date"] = pd.to_datetime(df_tc["send_date"], dayfirst=True, errors="coerce")

# enrich tracking_company with sector, headcount, working arrangement from talent_request
df_tc_enriched = df_tc.merge(
    df_tr[["id_talent_req", "industri_sektor", "headcount", "working_arrangement"]],
    on="id_talent_req", how="left",
)
df_tc_enriched = df_tc_enriched.merge(
    df_company[["id_company", "skala_perusahaan", "company_type", "kota"]],
    on="id_company", how="left",
)

# filter bar tailored for company exploration
with filter_bar():
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sel_industry = st.multiselect(
            t("mc.industry_sector"),
            options=sorted(df_tc_enriched["industri_sektor"].dropna().unique()),
            default=[], key="mc_industry",
        )
    with fc2:
        sel_scale = st.multiselect(
            t("mc.company_scale"),
            options=sorted(df_tc_enriched["skala_perusahaan"].dropna().unique()),
            default=[], key="mc_scale",
        )
    with fc3:
        sel_city = st.multiselect(
            t("mc.city_location"),
            options=sorted(df_tc_enriched["kota"].dropna().unique()),
            default=[], key="mc_city",
        )

    fc4, fc5, fc6 = st.columns(3)
    with fc4:
        sel_jenis = st.multiselect(
            t("mc.placement_type"),
            options=sorted(df_tc_enriched["jenis_penempatan"].dropna().unique()),
            default=[], key="mc_jenis",
        )
    with fc5:
        sel_progress = st.multiselect(
            t("mc.request_progress"),
            options=sorted(df_tc_enriched["progress"].dropna().unique()),
            default=[], key="mc_progress",
        )
    with fc6:
        valid_dates = df_tc_enriched["request_date"].dropna()
        min_date = valid_dates.min().date() if len(valid_dates) > 0 else pd.Timestamp("2023-01-01").date()
        max_date = valid_dates.max().date() if len(valid_dates) > 0 else pd.Timestamp("2026-12-31").date()
        date_range = st.date_input(
            t("mc.date_range"),
            value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
            key="mc_dates",
        )

# apply filters
filtered = df_tc_enriched.copy()
if sel_jenis:
    filtered = filtered[filtered["jenis_penempatan"].isin(sel_jenis)]
if sel_industry:
    filtered = filtered[filtered["industri_sektor"].isin(sel_industry)]
if sel_scale:
    filtered = filtered[filtered["skala_perusahaan"].isin(sel_scale)]
if sel_progress:
    filtered = filtered[filtered["progress"].isin(sel_progress)]
if sel_city:
    filtered = filtered[filtered["kota"].isin(sel_city)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt = pd.Timestamp(date_range[1])
    mask = filtered["request_date"].notna()
    filtered = filtered[mask & (filtered["request_date"] >= start_dt) & (filtered["request_date"] <= end_dt)]

tc_ids = set(filtered["id_tracking_company"])
filtered_ts = df_ts[df_ts["id_tracking_company"].isin(tc_ids)]

# company-oriented kpis computation
comp_name_col = "company_name" if "company_name" in df_company.columns else ("nama_perusahaan" if "nama_perusahaan" in df_company.columns else "id_company")
total_db_companies = len(df_company[comp_name_col].dropna().unique())
filtered_companies = set(filtered["nama_perusahaan"].dropna().unique())
num_req_companies = len(filtered_companies)

active_companies = set(filtered[filtered["progress"] != "Closed"]["nama_perusahaan"].dropna().unique())
num_active_companies = len(active_companies)

placed_ts = filtered_ts[filtered_ts["progress_student"] == "Placement"]
placed_companies = set(placed_ts["company"].dropna().unique()) if not placed_ts.empty else set()
num_placed_companies = len(placed_companies)
placed_comp_pct = round(num_placed_companies / num_req_companies * 100, 1) if num_req_companies > 0 else 0.0

total_placements = len(placed_ts)
total_headcount = int(filtered["jumlah_permintaan"].sum())

avg_headcount_per_comp = round(total_headcount / num_req_companies, 1) if num_req_companies > 0 else 0.0

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
metric_strip([
    {
        "label": t("mc.kpi_companies_requested"),
        "value": f"{num_req_companies:,}",
    },
    {
        "label": t("mc.kpi_active_contacts"),
        "value": f"{num_active_companies:,}",
    },
    {
        "label": t("mc.kpi_placed_partners"),
        "value": f"{num_placed_companies:,}",
        "delta": f"{placed_comp_pct}% success",
        "sentiment": "success" if placed_comp_pct >= 50 else "warning",
    },
    {
        "label": t("mc.kpi_total_placements"),
        "value": f"{total_placements:,}",
    },
    {
        "label": t("mc.kpi_avg_headcount"),
        "value": f"{avg_headcount_per_comp}",
    },
])

# demographics: industry treemap and company type treemap
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mc.demographics_volume_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mc.demographics_volume_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

col_r1_left, col_r1_right = st.columns([3, 2])

with col_r1_left:
    with chart_panel(t("mc.chart_industry"), height=460, subtitle=t("mc.chart_industry_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
        else:
            industry_agg = filtered["industri_sektor"].value_counts().reset_index()
            industry_agg.columns = ["industry", "count"]
            fig = px.treemap(
                industry_agg, path=["industry"], values="count",
                color="industry", color_discrete_sequence=CHART_PALETTE
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, margin=dict(t=30, l=10, r=10, b=30))
            fig.update_traces(textinfo="label+value", textfont_size=12)
            st.plotly_chart(fig, use_container_width=True)

with col_r1_right:
    with chart_panel(t("mc.chart_company_type"), height=460, subtitle=t("mc.chart_company_type_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
        else:
            ctype_agg = filtered["company_type"].value_counts().reset_index()
            ctype_agg.columns = ["type", "count"]
            fig = px.treemap(
                ctype_agg, path=["type"], values="count",
                color="type", color_discrete_sequence=CHART_PALETTE[::-1]
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, margin=dict(t=30, l=10, r=10, b=30))
            fig.update_traces(textinfo="label+value", textfont_size=12)
            st.plotly_chart(fig, use_container_width=True)

# company scale donut and top 10 volume leaderboard
col_r2_left, col_r2_right = st.columns([2, 3])

with col_r2_left:
    with chart_panel(t("mc.chart_company_scale"), height=460, subtitle=t("mc.chart_company_scale_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
        else:
            scale_agg = filtered["skala_perusahaan"].value_counts().reset_index()
            scale_agg.columns = ["scale", "count"]
            fig = px.pie(
                scale_agg, names="scale", values="count", hole=0.5,
                color_discrete_sequence=CHART_PALETTE[2:],
            )
            fig.update_traces(
                textinfo="label+percent", textposition="outside",
                pull=[0.02] * len(scale_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=False, margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

with col_r2_right:
    with chart_panel(t("mc.chart_top_companies"), height=460, subtitle=t("mc.chart_top_companies_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
        else:
            company_vol = (
                filtered
                .groupby("nama_perusahaan")
                .agg(requests=("jumlah_permintaan", "sum"), sent=("jumlah_dikirimkan", "sum"))
                .reset_index()
                .nlargest(10, "requests")
            )
            # build annotations for bar labels since text inside dark bars needs white
            annotations = []
            for _, row in company_vol.iterrows():
                if row["requests"] > 0:
                    annotations.append(dict(
                        x=row["requests"], y=row["nama_perusahaan"],
                        text=str(row["requests"]),
                        xanchor="right", xshift=-5, yanchor="middle",
                        showarrow=False, font=dict(color="white", size=10)
                    ))
            fig = px.bar(
                company_vol, x="requests", y="nama_perusahaan", orientation="h",
                color_discrete_sequence=[CHART_PALETTE[0]],
            )
            apply_plotly_style(fig)
            fig.update_layout(
                yaxis=dict(
                    categoryorder="total ascending", title=t("mc.company"),
                    showticklabels=False, automargin=False
                ),
                xaxis_title=t("mc.total_headcount_req"), height=400,
                annotations=annotations, margin=dict(l=30)
            )
            max_val = company_vol["requests"].max() if not company_vol.empty else 1
            fig.update_xaxes(range=[0, max_val * 1.6])
            st.plotly_chart(fig, use_container_width=True)

# monthly request trend (full width)
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mc.trend_ops_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mc.trend_ops_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

with chart_panel(t("mc.chart_monthly"), height=460, subtitle=t("mc.chart_monthly_sub")):
    if filtered.empty:
        st.info(t("mc.no_data_filter"))
    else:
        monthly_data = filtered.dropna(subset=["request_date"]).copy()
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
            xaxis_title=t("mc.month"), yaxis_title=t("mc.request_count"), height=400,
        )
        fig.update_traces(line=dict(width=2.5), fillcolor="rgba(52,98,237,0.08)")
        st.plotly_chart(fig, use_container_width=True)

# performance leaderboard: placement rate, rejection rate, ghosting rate per company
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mc.performance_leaderboard_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mc.performance_leaderboard_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)


def _composite_impact(df_agg, count_col):
    # compute impact score from volume and rate rankings, normalized 0-100
    rate_col = f"{count_col} Rate (%)"
    df_agg["_rank_vol"] = df_agg[count_col].rank(method="min", ascending=False)
    df_agg["_rank_rate"] = df_agg[rate_col].rank(method="min", ascending=False)
    df_agg["_comp"] = df_agg["_rank_vol"] + df_agg["_rank_rate"]
    c_min, c_max = df_agg["_comp"].min(), df_agg["_comp"].max()
    if c_max > c_min:
        df_agg["Impact Score"] = 100 * (1 - (df_agg["_comp"] - c_min) / (c_max - c_min))
    else:
        df_agg["Impact Score"] = 100.0
    return df_agg.drop(columns=["_rank_vol", "_rank_rate", "_comp"])


company_totals = df_ts.groupby("company").size().reset_index(name="Total")

# top 10 placement rate
with chart_panel(t("mc.top10_placement"), height=460, subtitle=t("mc.top10_placement_sub")):
    placed_candidates = df_ts[df_ts["progress_student"] == "Placement"]
    if not placed_candidates.empty:
        place_agg = placed_candidates.groupby("company").size().reset_index(name="Placement Count")
        place_agg = place_agg.merge(company_totals, on="company")
        place_agg["Placement Count Rate (%)"] = (place_agg["Placement Count"] / place_agg["Total"] * 100).round(1)
        place_agg["custom_label"] = place_agg.apply(
            lambda row: f"{int(row['Placement Count'])}/{int(row['Total'])} ({row['Placement Count Rate (%)']}%)", axis=1
        )
        place_agg = _composite_impact(place_agg, "Placement Count")
        top10 = place_agg.sort_values(["Impact Score"], ascending=[False]).head(10).sort_values("Impact Score", ascending=True)

        fig = px.bar(
            top10, x="Impact Score", y="company", orientation="h",
            color="Impact Score", color_continuous_scale=["#37A2B9", "#3462ED"],
            text="custom_label"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        apply_plotly_style(fig)
        fig.update_layout(
            height=380, margin=dict(t=10, l=10, r=40, b=10),
            xaxis_title=t("mp.impact_score_axis"),
            yaxis=dict(title="", showticklabels=True),
            coloraxis_showscale=False
        )
        fig.update_xaxes(range=[80, 108])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No placement data available.")

# top 10 rejection rate
with chart_panel(t("mc.top10_rejection"), height=460, subtitle=t("mc.top10_rejection_sub")):
    rejected_candidates = df_ts[df_ts["progress_student"] == "Rejected"]
    if not rejected_candidates.empty:
        rej_agg = rejected_candidates.groupby("company").size().reset_index(name="Rejection Count")
        rej_agg = rej_agg.merge(company_totals, on="company")
        rej_agg["Rejection Count Rate (%)"] = (rej_agg["Rejection Count"] / rej_agg["Total"] * 100).round(1)
        rej_agg["custom_label"] = rej_agg.apply(
            lambda row: f"{int(row['Rejection Count'])}/{int(row['Total'])} ({row['Rejection Count Rate (%)']}%)", axis=1
        )
        rej_agg = _composite_impact(rej_agg, "Rejection Count")
        top10 = rej_agg.sort_values("Impact Score", ascending=False).head(10).sort_values("Impact Score", ascending=True)

        fig = px.bar(
            top10, x="Impact Score", y="company", orientation="h",
            color="Impact Score", color_continuous_scale=["#37A2B9", "#EF4444"],
            text="custom_label"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        apply_plotly_style(fig)
        fig.update_layout(
            height=380, margin=dict(t=10, l=10, r=40, b=10),
            xaxis_title=t("mp.impact_score_axis"),
            yaxis=dict(title="", showticklabels=True),
            coloraxis_showscale=False
        )
        fig.update_xaxes(range=[80, 108])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rejection data available.")

# top 10 ghosting rate per company
with chart_panel(t("mc.top10_ghosting"), height=460, subtitle=t("mc.top10_ghosting_sub")):
    reference_date = df_tc["send_date"].max()
    df_ghost = metrics.get_ghosting_flags(
        df_ts, tracking_company=df_tc, today=reference_date, include_healthy=False
    )
    if not df_ghost.empty:
        ghost_agg = df_ghost.groupby("company").size().reset_index(name="Ghosting Count")
        ghost_agg = ghost_agg.merge(company_totals, on="company")
        ghost_agg["Ghosting Count Rate (%)"] = (ghost_agg["Ghosting Count"] / ghost_agg["Total"] * 100).round(1)
        ghost_agg["custom_label"] = ghost_agg.apply(
            lambda row: f"{int(row['Ghosting Count'])}/{int(row['Total'])} ({row['Ghosting Count Rate (%)']}%)", axis=1
        )
        ghost_agg = _composite_impact(ghost_agg, "Ghosting Count")
        top10 = ghost_agg.sort_values("Impact Score", ascending=False).head(10).sort_values("Impact Score", ascending=True)

        fig = px.bar(
            top10, x="Impact Score", y="company", orientation="h",
            color_discrete_sequence=[COLORS["warning"]],
            text="custom_label"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        apply_plotly_style(fig)
        fig.update_layout(
            height=380, margin=dict(t=10, l=10, r=40, b=10),
            xaxis_title=t("mp.impact_score_axis"),
            yaxis=dict(title="", showticklabels=True),
        )
        fig.update_xaxes(range=[0, 115])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t("mp.no_ghosting_data"))

# company directory table: one row per company with aggregated performance metrics
section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mc.table_company_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mc.table_company_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

# aggregate request metrics per company using the enriched data
company_req = (
    df_tc_enriched
    .groupby(["id_company", "nama_perusahaan", "industri_sektor", "skala_perusahaan", "company_type", "kota"])
    .agg(
        total_permintaan=("jumlah_permintaan", "sum"),
        total_dikirimkan=("jumlah_dikirimkan", "sum"),
        jumlah_request=("id_tracking_company", "count"),
    )
    .reset_index()
)

# placement count per company from tracking_student
placed_per_company = (
    df_ts[df_ts["progress_student"] == "Placement"]
    .groupby("company").size().reset_index(name="total_placement")
)

# ghosting count per company
reference_date_tbl = df_tc["send_date"].max()
df_ghost_tbl = metrics.get_ghosting_flags(
    df_ts, tracking_company=df_tc, today=reference_date_tbl, include_healthy=False
)
ghost_per_company = (
    df_ghost_tbl.groupby("company").size().reset_index(name="total_ghosting")
    if not df_ghost_tbl.empty
    else pd.DataFrame(columns=["company", "total_ghosting"])
)

# merge all into one table
company_tbl = company_req.copy()
company_tbl = company_tbl.merge(
    placed_per_company, left_on="nama_perusahaan", right_on="company", how="left"
).drop(columns=["company"], errors="ignore")
company_tbl = company_tbl.merge(
    ghost_per_company, left_on="nama_perusahaan", right_on="company", how="left"
).drop(columns=["company"], errors="ignore")

company_tbl["total_placement"] = company_tbl["total_placement"].fillna(0).astype(int)
company_tbl["total_ghosting"] = company_tbl["total_ghosting"].fillna(0).astype(int)
company_tbl["fulfillment_pct"] = company_tbl.apply(
    lambda r: round(r["total_placement"] / r["total_dikirimkan"] * 100, 1)
    if r["total_dikirimkan"] > 0 else 0.0,
    axis=1,
)

with filter_bar():
    search_q = st.text_input(
        t("mc.search_company"), "", key="mc_table_search",
        placeholder=t("mc.search_company_placeholder"),
    )

tbl_view = company_tbl.copy()
if search_q:
    q = search_q.lower()
    tbl_view = tbl_view[
        tbl_view["nama_perusahaan"].str.lower().str.contains(q, na=False) |
        tbl_view["industri_sektor"].str.lower().str.contains(q, na=False) |
        tbl_view["kota"].str.lower().str.contains(q, na=False)
    ]

tbl_view = tbl_view.sort_values("total_placement", ascending=False).reset_index(drop=True)

display_cols = [
    "nama_perusahaan", "industri_sektor", "skala_perusahaan", "company_type", "kota",
    "jumlah_request", "total_permintaan", "total_dikirimkan", "total_placement",
    "total_ghosting", "fulfillment_pct",
]

st.caption(t("mc.table_showing").format(shown=len(tbl_view), total=len(company_tbl)))

st.dataframe(
    tbl_view[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "nama_perusahaan":    st.column_config.TextColumn(t("mc.col_company_name"), width="large"),
        "industri_sektor":    st.column_config.TextColumn(t("mc.col_industry")),
        "skala_perusahaan":   st.column_config.TextColumn(t("mc.col_scale")),
        "company_type":       st.column_config.TextColumn(t("mc.col_type")),
        "kota":               st.column_config.TextColumn(t("mc.col_city")),
        "jumlah_request":     st.column_config.NumberColumn(t("mc.col_requests"), format="%d"),
        "total_permintaan":   st.column_config.NumberColumn(t("mc.col_headcount"), format="%d"),
        "total_dikirimkan":   st.column_config.NumberColumn(t("mc.col_sent"), format="%d"),
        "total_placement":    st.column_config.NumberColumn(t("mc.col_placement"), format="%d"),
        "total_ghosting":     st.column_config.NumberColumn(t("mc.col_ghosting"), format="%d"),
        "fulfillment_pct":    st.column_config.NumberColumn(t("mc.col_fulfillment"), format="%.1f%%"),
    },
)

