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

inject_global_css()

page_header(
    "Monitor Company",
    "Manajemen talent request dan profil perusahaan mitra"
)

# load data
df_company = load_csv_table("company")
df_tc = load_csv_table("tracking_company")
df_tr = load_csv_table("talent_request")
df_ts = load_csv_table("tracking_student")

# Parse dates
df_tc["request_date"] = pd.to_datetime(
    df_tc["request_date"], dayfirst=True, errors="coerce"
)
df_tc["send_date"] = pd.to_datetime(
    df_tc["send_date"], dayfirst=True, errors="coerce"
)
df_tr["request_date"] = pd.to_datetime(
    df_tr["request_date"], errors="coerce"
)

# Enrich tracking_company with industry sector and company scale for filtering
df_tc_enriched = df_tc.merge(
    df_tr[["id_talent_req", "industri_sektor", "headcount", "working_arrangement"]],
    on="id_talent_req", how="left"
)
df_tc_enriched = df_tc_enriched.merge(
    df_company[["id_company", "skala_perusahaan", "company_type", "kota"]],
    on="id_company", how="left"
)

# filters
with filter_bar():
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        sel_jenis = st.multiselect(
            "Placement Type",
            options=sorted(df_tc_enriched["jenis_penempatan"].dropna().unique()),
            default=[],
            key="mc_jenis",
        )
    with fc2:
        sel_industry = st.multiselect(
            "Industry Sector",
            options=sorted(df_tc_enriched["industri_sektor"].dropna().unique()),
            default=[],
            key="mc_industry",
        )
    with fc3:
        sel_scale = st.multiselect(
            "Company Scale",
            options=sorted(df_tc_enriched["skala_perusahaan"].dropna().unique()),
            default=[],
            key="mc_scale",
        )
    with fc4:
        sel_progress = st.multiselect(
            "Request Progress",
            options=sorted(df_tc_enriched["progress"].dropna().unique()),
            default=[],
            key="mc_progress",
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
            "Request Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
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

# Get linked tracking_student rows
tc_ids = set(filtered["id_tracking_company"])
filtered_ts = df_ts[df_ts["id_tracking_company"].isin(tc_ids)]

# compute KPIs
total_requests = len(filtered)
total_headcount = int(filtered["jumlah_permintaan"].sum())
total_sent = int(filtered["jumlah_dikirimkan"].sum())
placements = len(filtered_ts[filtered_ts["progress_student"] == "Placement"])
fulfillment_pct = round(
    placements / total_headcount * 100, 1
) if total_headcount > 0 else 0.0

valid_resp = filtered.dropna(subset=["request_date", "send_date"])
avg_resp_days = round(
    (valid_resp["send_date"] - valid_resp["request_date"]).dt.days.mean(), 1
) if len(valid_resp) > 0 else 0.0

# KPI strip
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
metric_strip([
    {"label": "Total Requests", "value": f"{total_requests:,}"},
    {"label": "Total Headcount", "value": f"{total_headcount:,}"},
    {"label": "Candidates Sent", "value": f"{total_sent:,}"},
    {
        "label": "Fulfillment Rate",
        "value": f"{fulfillment_pct}%",
        "delta": f"{placements:,} placed",
        "sentiment": "success" if fulfillment_pct >= 50 else "warning" if fulfillment_pct >= 25 else "danger",
    },
    {"label": "Avg Response Time", "value": f"{avg_resp_days} days"},
])

# charts row 1
section_divider()
col_l, col_r = card_grid(2)

with col_l:
    with chart_panel("Requests By Industry Sector", height=460):
        if filtered.empty:
            st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")
        else:
            industry_agg = (
                filtered["industri_sektor"]
                .value_counts()
                .head(12)
                .reset_index()
            )
            industry_agg.columns = ["industry", "count"]
            fig = px.bar(
                industry_agg, x="count", y="industry", orientation="h",
                color_discrete_sequence=[CHART_PALETTE[0]],
                text="count",
            )
            fig.update_traces(textposition="outside")
            apply_plotly_style(fig)
            fig.update_layout(
                yaxis=dict(categoryorder="total ascending", title=""),
                xaxis_title="Number Of Requests",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

with col_r:
    with chart_panel("Placement Type Distribution", height=460):
        if filtered.empty:
            st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")
        else:
            jenis_agg = (
                filtered["jenis_penempatan"]
                .value_counts()
                .reset_index()
            )
            jenis_agg.columns = ["type", "count"]
            fig = px.pie(
                jenis_agg, names="type", values="count", hole=0.5,
                color="type", color_discrete_map=JENIS_PENEMPATAN_COLORS,
            )
            fig.update_traces(
                textinfo="label+percent",
                textposition="outside",
                pull=[0.02] * len(jenis_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

# charts row 2
section_divider()
col_l2, col_r2 = card_grid(2)

with col_l2:
    with chart_panel("Monthly Request Trend", height=460):
        if filtered.empty:
            st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")
        else:
            monthly_data = filtered.dropna(subset=["request_date"]).copy()
            monthly = (
                monthly_data
                .groupby(monthly_data["request_date"].dt.to_period("M"))
                .size()
                .reset_index(name="count")
            )
            monthly["request_date"] = monthly["request_date"].astype(str)
            fig = px.area(
                monthly, x="request_date", y="count",
                color_discrete_sequence=[CHART_PALETTE[0]],
                markers=True,
            )
            apply_plotly_style(fig)
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Request Count",
                height=400,
            )
            fig.update_traces(
                line=dict(width=2.5),
                fillcolor="rgba(52,98,237,0.08)",
            )
            st.plotly_chart(fig, use_container_width=True)

with col_r2:
    with chart_panel("Request Progress Pipeline", height=460):
        if filtered.empty:
            st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")
        else:
            # Ordered pipeline stages
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
                color="stage", color_discrete_map=PIPELINE_COLORS,
                text="count",
            )
            fig.update_traces(textposition="outside", showlegend=False)
            apply_plotly_style(fig)
            fig.update_layout(
                yaxis=dict(
                    categoryorder="array",
                    categoryarray=list(reversed(pipeline_order)),
                    title="",
                ),
                xaxis_title="Count",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

# charts row 3
section_divider()
col_l3, col_r3 = card_grid(2)

with col_l3:
    with chart_panel("Top 15 Companies By Request Volume", height=460):
        if filtered.empty:
            st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")
        else:
            company_vol = (
                filtered
                .groupby("nama_perusahaan")
                .agg(
                    requests=("jumlah_permintaan", "sum"),
                    sent=("jumlah_dikirimkan", "sum"),
                )
                .reset_index()
                .nlargest(15, "requests")
            )
            fig = px.bar(
                company_vol, x="requests", y="nama_perusahaan", orientation="h",
                color_discrete_sequence=[CHART_PALETTE[0]],
                text="requests",
            )
            fig.update_traces(textposition="outside")
            apply_plotly_style(fig)
            fig.update_layout(
                yaxis=dict(categoryorder="total ascending", title=""),
                xaxis_title="Total Headcount Requested",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

with col_r3:
    with chart_panel("Working Arrangement Distribution", height=460):
        if filtered.empty:
            st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")
        else:
            wa_agg = (
                filtered["working_arrangement"]
                .value_counts()
                .reset_index()
            )
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
                textinfo="label+percent",
                textposition="outside",
                pull=[0.02] * len(wa_agg),
            )
            apply_plotly_style(fig)
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

# detail table
section_divider()

with table_panel("Detail Talent Request", height=500):
    search_term = st.text_input(
        "Cari perusahaan atau posisi...",
        key="mc_search",
        placeholder="Ketik nama perusahaan atau posisi",
    )

    display_cols = [
        "nama_perusahaan", "posisi", "jenis_penempatan", "industri_sektor",
        "jumlah_permintaan", "jumlah_dikirimkan", "progress",
        "request_date", "send_date",
    ]
    available_cols = [c for c in display_cols if c in filtered.columns]
    detail_df = filtered[available_cols].copy()

    # Rename columns for display
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
    st.caption(f"Menampilkan {len(detail_df):,} dari {total_requests:,} record")
