# monitor company - bt-03 talent request management, bt-04 success rate

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    t("page.monitor_company"),
    bt_caption=t("bt.03_04"),
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
    df_tr[["id_talent_req", "industri_sektor", "headcount", "working_arrangement"]],
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
            t("mc.placement_type"),
            options=sorted(df_tc_enriched["jenis_penempatan"].dropna().unique()),
            default=[], key="mc_jenis",
        )
    with fc2:
        sel_industry = st.multiselect(
            t("mc.industry_sector"),
            options=sorted(df_tc_enriched["industri_sektor"].dropna().unique()),
            default=[], key="mc_industry",
        )
    with fc3:
        sel_scale = st.multiselect(
            t("mc.company_scale"),
            options=sorted(df_tc_enriched["skala_perusahaan"].dropna().unique()),
            default=[], key="mc_scale",
        )
    with fc4:
        sel_progress = st.multiselect(
            t("mc.request_progress"),
            options=sorted(df_tc_enriched["progress"].dropna().unique()),
            default=[], key="mc_progress",
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
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt = pd.Timestamp(date_range[1])
    mask = filtered["request_date"].notna()
    filtered = filtered[mask & (filtered["request_date"] >= start_dt) & (filtered["request_date"] <= end_dt)]

# linked tracking_student rows
tc_ids = set(filtered["id_tracking_company"])
filtered_ts = df_ts[df_ts["id_tracking_company"].isin(tc_ids)]

# kpi computation
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
    {"label": t("mc.total_requests"), "value": f"{total_requests:,}"},
    {"label": t("mc.total_headcount"), "value": f"{total_headcount:,}"},
    {"label": t("mc.candidates_sent"), "value": f"{total_sent:,}"},
    {
        "label": t("mc.fulfillment_rate"),
        "value": f"{fulfillment_pct}%",
        "delta": f"{placements:,} {t('overview.placed')}",
        "sentiment": "success" if fulfillment_pct >= 50 else "warning" if fulfillment_pct >= 25 else "danger",
    },
    {"label": t("mc.avg_response"), "value": f"{avg_resp_days} {t('mc.days')}"},
])

# charts row 1
section_divider()
col_l, col_r = card_grid(2)

with col_l:
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

with col_r:
    with chart_panel(t("mc.chart_type_dist"), height=460, subtitle=t("mc.chart_type_dist_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
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
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

# charts row 2
section_divider()
col_l2, col_r2 = card_grid(2)

with col_l2:
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

with col_r2:
    with chart_panel(t("mc.chart_pipeline"), height=460, subtitle=t("mc.chart_pipeline_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
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
                xaxis_title=t("mc.count"), height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

# charts row 3
section_divider()
col_l3, col_r3 = card_grid(2)

with col_l3:
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
            fig = px.bar(
                company_vol, x="requests", y="nama_perusahaan", orientation="h",
                color_discrete_sequence=[CHART_PALETTE[0]], text="nama_perusahaan",
            )
            fig.update_traces(
                textposition='outside',
                constraintext='none',
                cliponaxis=False
            )
            
            annotations = []
            for _, row in company_vol.iterrows():
                if row["requests"] > 0:
                    annotations.append(dict(
                        x=row["requests"],
                        y=row["nama_perusahaan"],
                        text=str(row["requests"]),
                        xanchor='right',
                        xshift=-5,
                        yanchor='middle',
                        showarrow=False,
                        font=dict(color="white", size=10)
                    ))

            apply_plotly_style(fig)
            fig.update_layout(
                yaxis=dict(
                    categoryorder="total ascending", 
                    title=dict(text=t("mc.company"), standoff=20),
                    showticklabels=False,
                    automargin=False
                ),
                xaxis_title=t("mc.total_headcount_req"), height=400,
                annotations=annotations,
                margin=dict(l=30)
            )
            max_val = company_vol["requests"].max() if not company_vol.empty else 1
            fig.update_xaxes(range=[0, max_val * 1.6])
            st.plotly_chart(fig, use_container_width=True)

with col_r3:
    with chart_panel(t("mc.chart_working_arr"), height=460, subtitle=t("mc.chart_working_arr_sub")):
        if filtered.empty:
            st.info(t("mc.no_data_filter"))
        else:
            wa_agg = filtered["working_arrangement"].value_counts().reset_index()
            wa_agg.columns = ["arrangement", "count"]
            wa_colors = {
                "WFO": CHART_PALETTE[0],
                "Hybrid": CHART_PALETTE[1],
                "WFH": CHART_PALETTE[2],
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
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
# charts row 4: Top 10 Placements and Rejections
section_divider()

# Prepare df_track for student metrics
df_track = df_ts.copy()

col_place, col_rej = st.columns(2, gap="medium")

with col_place:
    with chart_panel(t("mc.top10_placement"), height=460, subtitle=t("mc.top10_placement_sub")):
        company_totals = df_track.groupby("company").size().reset_index(name="Total")
        placed_candidates = df_track[df_track["progress_student"] == "Placement"]
        
        if not placed_candidates.empty:
            place_by_company = placed_candidates.groupby("company").size().reset_index(name="Placement Count")
            place_by_company = place_by_company.merge(company_totals, on="company")
            place_by_company["Placement Rate (%)"] = (place_by_company["Placement Count"] / place_by_company["Total"] * 100).round(1)

            place_by_company["custom_label"] = place_by_company.apply(
                lambda row: f"<b>{int(row['Placement Count'])}</b>/{int(row['Total'])} ({row['Placement Rate (%)']}%)", axis=1
            )

            place_by_company["Rank_Vol"] = place_by_company["Placement Count"].rank(method="min", ascending=False)
            place_by_company["Rank_Rate"] = place_by_company["Placement Rate (%)"].rank(method="min", ascending=False)
            place_by_company["Composite_Score"] = place_by_company["Rank_Vol"] + place_by_company["Rank_Rate"]

            c_min = place_by_company["Composite_Score"].min()
            c_max = place_by_company["Composite_Score"].max()
            if c_max > c_min:
                place_by_company["Impact Score"] = 100 * (1 - (place_by_company["Composite_Score"] - c_min) / (c_max - c_min))
            else:
                place_by_company["Impact Score"] = 100.0

            top_10_place = place_by_company.sort_values(["Composite_Score", "Placement Count"], ascending=[True, False]).head(10)
            top_10_place = top_10_place.sort_values(["Composite_Score", "Placement Count"], ascending=[False, True])

            fig_place = px.bar(
                top_10_place, x="Impact Score", y="company", orientation="h",
                color="Impact Score", color_continuous_scale=["#37A2B9", "#3462ED"]
            )
            
            annotations = []
            for _, row in top_10_place.iterrows():
                label_text = f"<b>{row['company']}</b>: {int(row['Placement Count'])}/{int(row['Total'])} ({row['Placement Rate (%)']}%)"
                annotations.append(dict(
                    x=81, 
                    y=row["company"],
                    text=label_text,
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(color="white", size=11)
                ))

            apply_plotly_style(fig_place)
            fig_place.update_layout(
                height=380, margin=dict(t=10, l=30, r=10, b=10),
                xaxis_title=t("mp.impact_score_axis"), 
                yaxis=dict(
                    title=dict(text=t("mc.company"), standoff=20),
                    showticklabels=False
                ),
                annotations=annotations,
                coloraxis_showscale=False
            )
            fig_place.update_xaxes(range=[80, 100])

            st.plotly_chart(fig_place, use_container_width=True)
        else:
            st.info("No placement data available.")

with col_rej:
    with chart_panel(t("mc.top10_rejection"), height=460, subtitle=t("mc.top10_rejection_sub")):
        rejected_candidates = df_track[df_track["progress_student"] == "Rejected"]
        if not rejected_candidates.empty:
            rej_by_company = rejected_candidates.groupby("company").size().reset_index(name="Rejection Count")
            rej_by_company = rej_by_company.merge(company_totals, on="company")
            rej_by_company["Rejection Rate (%)"] = (rej_by_company["Rejection Count"] / rej_by_company["Total"] * 100).round(1)

            rej_by_company["custom_label"] = rej_by_company.apply(
                lambda row: f"<b>{int(row['Rejection Count'])}</b>/{int(row['Total'])} ({row['Rejection Rate (%)']}%)", axis=1
            )

            rej_by_company["Rank_Vol"] = rej_by_company["Rejection Count"].rank(method="min", ascending=False)
            rej_by_company["Rank_Rate"] = rej_by_company["Rejection Rate (%)"].rank(method="min", ascending=False)
            rej_by_company["Composite_Score"] = rej_by_company["Rank_Vol"] + rej_by_company["Rank_Rate"]

            c_min = rej_by_company["Composite_Score"].min()
            c_max = rej_by_company["Composite_Score"].max()
            if c_max > c_min:
                rej_by_company["Impact Score"] = 100 * (1 - (rej_by_company["Composite_Score"] - c_min) / (c_max - c_min))
            else:
                rej_by_company["Impact Score"] = 100.0

            top_10_rej = rej_by_company.sort_values(["Composite_Score", "Rejection Count"], ascending=[True, False]).head(10)
            top_10_rej = top_10_rej.sort_values(["Composite_Score", "Rejection Count"], ascending=[False, True])

            fig_rej = px.bar(
                top_10_rej, x="Impact Score", y="company", orientation="h",
                color="Impact Score", color_continuous_scale=["#37A2B9", "#3462ED"]
            )
            
            annotations = []
            for _, row in top_10_rej.iterrows():
                label_text = f"<b>{row['company']}</b>: {int(row['Rejection Count'])}/{int(row['Total'])} ({row['Rejection Rate (%)']}%)"
                annotations.append(dict(
                    x=81, 
                    y=row["company"],
                    text=label_text,
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(color="white", size=11)
                ))

            apply_plotly_style(fig_rej)
            fig_rej.update_layout(
                height=380, margin=dict(t=10, l=30, r=10, b=10),
                xaxis_title=t("mp.impact_score_axis"), 
                yaxis=dict(
                    title=dict(text=t("mc.company"), standoff=20),
                    showticklabels=False
                ),
                annotations=annotations,
                coloraxis_showscale=False
            )
            fig_rej.update_xaxes(range=[80, 100])

            st.plotly_chart(fig_rej, use_container_width=True)
        else:
            st.info("No rejection data available.")

# detail table
section_divider()

with table_panel(t("mc.detail_title"), height=500, subtitle=t("mc.detail_title_sub")):
    search_term = st.text_input(
        t("mc.search_label"), key="mc_search",
        placeholder=t("mc.search_placeholder"),
    )

    display_cols = [
        "nama_perusahaan", "posisi", "jenis_penempatan", "industri_sektor",
        "jumlah_permintaan", "jumlah_dikirimkan", "progress",
        "request_date", "send_date",
    ]
    available_cols = [c for c in display_cols if c in filtered.columns]
    detail_df = filtered[available_cols].copy()

    col_labels = {
        "nama_perusahaan": "Company",
        "posisi": "Position",
        "jenis_penempatan": "Type",
        "industri_sektor": "Industry",
        "jumlah_permintaan": "Requested",
        "jumlah_dikirimkan": "Sent",
        "progress": "Progress",
        "request_date": "Request Date",
        "send_date": "Send Date",
    }
    detail_df = detail_df.rename(columns=col_labels)

    if search_term:
        mask = detail_df.apply(
            lambda row: search_term.lower() in str(row.values).lower(), axis=1
        )
        detail_df = detail_df[mask]

    st.dataframe(detail_df, use_container_width=True, hide_index=True)
    st.caption(t("mc.showing_records", shown=f"{len(detail_df):,}", total=f"{total_requests:,}"))
