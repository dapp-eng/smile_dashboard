# monitor student - bt-06 eligibility and bt-01 talent matching

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.layout import (
    page_header, filter_bar, metric_strip, chart_panel,
    table_panel, panel, card_grid, section_divider, inject_global_css,
)
from utils.theme import COLORS, apply_plotly_style
from utils.i18n import t
from utils import queries, metrics

ELIGIBILITY_COLORS = {"Eligible": COLORS["success"], "Ineligible": COLORS["danger"]}

inject_global_css()

page_header(
    t("page.monitor_student"),
    bt_caption=t("bt.01_06"),
)

# at-a-glance kpi summary
summary = queries.get_student_supply_summary()
metric_strip([
    {"label": t("ms.summary_total"), "value": f"{summary['total']:,}"},
    {"label": t("ms.summary_available"), "value": f"{summary['available']:,}"},
    {"label": t("ms.summary_placed"), "value": f"{summary['placed']:,}"},
    {"label": t("ms.summary_prodi"), "value": f"{summary['n_prodi']:,}"},
    {
        "label": t("ms.summary_avg_ipk"),
        "value": f"{summary['avg_ipk']:.2f}" if summary["avg_ipk"] is not None else "\u2014",
    },
])

section_divider()

# bt-06: eligibility section
st.markdown(f"### {t('ms.eligibility_title')}")
st.caption(f"{t('ms.eligibility_caption')} (BT-06)")

with filter_bar():
    ipk_min = st.slider(t("ms.min_ipk"), 0.0, 4.0, 3.0, 0.05)
    c1, c2, c3, c4 = st.columns(4, vertical_alignment="center")
    require_cv = c1.checkbox(t("ms.cv_exists"), value=True)
    require_portfolio = c2.checkbox(t("ms.portfolio_exists"), value=True)
    require_active = c3.checkbox(t("ms.status_active"), value=True)
    require_available = c4.checkbox(t("ms.available"), value=True)

df = queries.get_student_eligibility(
    ipk_min=ipk_min,
    require_cv=require_cv,
    require_portfolio=require_portfolio,
    require_active=require_active,
    require_available=require_available,
)

# display filters
with filter_bar():
    f1, f2 = st.columns([2, 1], vertical_alignment="center")
    prodi_opts = sorted(df["program_studi"].dropna().astype(str).unique().tolist())
    prodi_sel = f1.multiselect(
        t("ms.filter_prodi"), prodi_opts, default=[],
        help=t("ms.filter_prodi_help"),
    )
    view = f2.radio(
        t("ms.show"),
        [t("ms.show_eligible"), t("ms.show_all"), t("ms.show_ineligible")],
        horizontal=True,
    )

view_df = df.copy()
if prodi_sel:
    view_df = view_df[view_df["program_studi"].isin(prodi_sel)]
if view == t("ms.show_eligible"):
    view_df = view_df[view_df["is_eligible"]]
elif view == t("ms.show_ineligible"):
    view_df = view_df[~view_df["is_eligible"]]

# metrics for the current program studi scope
scope = df[df["program_studi"].isin(prodi_sel)] if prodi_sel else df
n_total = len(scope)
n_eligible = int(scope["is_eligible"].sum())
elig_pct = round(n_eligible / n_total * 100, 1) if n_total else 0.0
avg_ipk_elig = scope.loc[scope["is_eligible"], "IPK"].mean()

metric_strip([
    {
        "label": t("ms.eligible"),
        "value": f"{n_eligible:,}",
        "delta": f"{elig_pct}%",
        "sentiment": "success" if elig_pct >= 50 else "warning" if elig_pct >= 25 else "danger",
    },
    {"label": t("ms.ineligible"), "value": f"{n_total - n_eligible:,}", "sentiment": "neutral"},
    {
        "label": t("ms.avg_ipk_eligible"),
        "value": f"{avg_ipk_elig:.2f}" if pd.notna(avg_ipk_elig) else "\u2014",
    },
])

section_divider()
left, right = card_grid(2)

with left:
    with chart_panel(t("ms.chart_elig_prodi"), height=430):
        by_prodi = (
            scope.assign(elig=scope["is_eligible"].map({True: "Eligible", False: "Ineligible"}))
            .groupby(["program_studi", "elig"]).size().reset_index(name="jumlah")
        )
        if by_prodi.empty:
            st.info(t("ms.no_data_scope"))
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

with right:
    with chart_panel(t("ms.chart_elig_comp"), height=430):
        comp = (
            scope["is_eligible"].map({True: "Eligible", False: "Ineligible"})
            .value_counts().reset_index()
        )
        comp.columns = ["status", "jumlah"]
        if comp.empty:
            st.info(t("ms.no_data_scope"))
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

with table_panel(t("ms.detail_title"), height=430):
    st.caption(t("ms.showing_students", count=f"{len(view_df):,}"))
    show_cols = [c for c in [
        "NIM", "nama", "program_studi", "semester", "IPK", "CV", "portofolio",
        "status", "ketersediaan", "domisili", "is_eligible", "ineligible_reasons",
    ] if c in view_df.columns]
    st.dataframe(
        view_df[show_cols], use_container_width=True, hide_index=True,
        column_config={
            "is_eligible": st.column_config.CheckboxColumn("Eligible"),
            "IPK": st.column_config.NumberColumn("IPK", format="%.2f"),
            "ineligible_reasons": st.column_config.TextColumn(
                "Alasan tidak eligible" if t("ms.show") == "Tampilkan" else "Ineligibility reasons",
                width="large",
            ),
        },
    )

# bt-01: talent matching section
section_divider()
st.markdown(f"### {t('ms.matching_title')}")
st.caption(f"{t('ms.matching_caption')} (BT-01)")

requests = queries.get_talent_requests()

if requests is None or requests.empty:
    st.info(t("ms.no_requests"))
else:
    def _req_label(row):
        posisi = row.get("nama_posisi", "?")
        perusahaan = row.get("nama_perusahaan", row.get("id_company", ""))
        return f"{row['id_talent_req']} \u00b7 {posisi} @ {perusahaan}"

    labels = {_req_label(r): r["id_talent_req"] for _, r in requests.iterrows()}
    chosen = st.selectbox(t("ms.talent_request"), list(labels.keys()))
    req = requests[requests["id_talent_req"] == labels[chosen]].iloc[0]

    def _f(field, default="\u2014"):
        val = req.get(field, default)
        return default if pd.isna(val) else val

    with panel(t("ms.detail_request")):
        d1, d2, d3, d4 = st.columns(4)
        d1.metric(t("ms.position"), _f("nama_posisi"))
        d2.metric(t("ms.type"), _f("jenis_penempatan"))
        d3.metric(t("ms.headcount"), _f("headcount"))
        d4.metric(t("ms.min_semester"), _f("minimum_semester"))
        st.markdown(f"**{t('ms.field_required')}:** {_f('bidang_studi_dibutuhkan')}")
        if str(_f("deskripsi_requirement")) not in ("\u2014", ""):
            st.markdown(f"**{t('ms.requirement')}:** {_f('deskripsi_requirement')}")

    eligible_only = df[df["is_eligible"]]
    matches = metrics.match_students_to_request(eligible_only, req)

    if matches.empty:
        st.warning(t("ms.no_match"))
    else:
        try:
            headcount = int(float(_f("headcount", 0)))
        except (ValueError, TypeError):
            headcount = 0
        strong = int((matches["match_score"] >= 70).sum())
        perfect = int((matches["match_score"] >= 100).sum())

        metric_strip([
            {"label": t("ms.candidates_eligible"), "value": f"{len(matches):,}"},
            {
                "label": t("ms.strong_match"),
                "value": f"{strong:,}",
                "sentiment": "success" if strong >= headcount and headcount > 0 else "warning",
            },
            {"label": t("ms.perfect_match"), "value": f"{perfect:,}"},
            {
                "label": t("ms.headcount_requested"),
                "value": f"{headcount:,}" if headcount else "\u2014",
            },
        ])

        section_divider()

        with table_panel(t("ms.rank_title"), height=430):
            cols = [c for c in [
                "NIM", "nama", "program_studi", "semester", "IPK", "tools",
                "match_bidang", "match_semester", "match_tools", "match_score",
            ] if c in matches.columns]
            st.dataframe(
                matches[cols], use_container_width=True, hide_index=True,
                column_config={
                    "IPK": st.column_config.NumberColumn("IPK", format="%.2f"),
                    "match_bidang": st.column_config.NumberColumn(
                        "Bidang", format="%.0f", help="1 = program studi cocok",
                    ),
                    "match_semester": st.column_config.NumberColumn(
                        "Semester", format="%.0f", help="1 = memenuhi minimum semester",
                    ),
                    "match_tools": st.column_config.ProgressColumn(
                        "Tools", min_value=0, max_value=1, format="%.0f%%",
                    ),
                    "match_score": st.column_config.ProgressColumn(
                        "Skor", min_value=0, max_value=100, format="%.0f",
                    ),
                },
            )
