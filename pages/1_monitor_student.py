# monitor student - bt-06 eligibility and bt-01 talent matching

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.layout import (
    page_header, filter_bar, metric_strip, chart_panel,
    table_panel, panel, card_grid, section_divider, inject_global_css,
)
from utils.theme import COLORS, apply_plotly_style, CHART_PALETTE
from utils.i18n import t
from utils import queries, metrics

ELIGIBILITY_COLORS = {"Eligible": "#3462ED", "Ineligible": "#37A2B9"}

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

# bt-00: student profiling section
st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("ms.profiling_section")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("ms.profiling_caption")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

df_prof = queries.get_student_profiling_data()

# Row 1: Field of Interest (Treemap) | Placement Preference (Donut)
c_prof_1, c_prof_2 = card_grid(2)
with c_prof_1:
    with chart_panel(t("ms.chart_interest"), subtitle=t("ms.chart_interest_sub"), height=420):
        if df_prof.empty:
            st.info("No data")
        else:
            interest_counts = df_prof["bidang_minat"].value_counts().reset_index()
            interest_counts.columns = ["Interest", "Count"]
            interest_counts["Root"] = "Semua Minat"
            fig_interest = px.treemap(
                interest_counts, path=["Root", "Interest"], values="Count",
                color="Interest", color_discrete_sequence=CHART_PALETTE
            )
            apply_plotly_style(fig_interest)
            fig_interest.update_layout(height=360, margin=dict(t=30, l=10, r=10, b=30))
            st.plotly_chart(fig_interest, use_container_width=True)

with c_prof_2:
    with chart_panel(t("ms.chart_placement_pref"), subtitle=t("ms.chart_placement_pref_sub"), height=420):
        if df_prof.empty:
            st.info("No data")
        else:
            pref_counts = df_prof["jenis_penempatan_diminati"].value_counts().reset_index()
            pref_counts.columns = ["Preference", "Count"]
            fig_pref = px.pie(
                pref_counts, names="Preference", values="Count", hole=0.5,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pref.update_traces(textposition="outside", textinfo="label+percent", pull=[0.02]*len(pref_counts))
            apply_plotly_style(fig_pref)
            fig_pref.update_layout(height=360, showlegend=True, margin=dict(t=30, b=30))
            st.plotly_chart(fig_pref, use_container_width=True)

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# Row 2: Study Program Distribution (Bar) | Popular Tools (Bar)
c_prof_3, c_prof_4 = card_grid(2)
with c_prof_3:
    with chart_panel(t("ms.chart_prodi_dist"), subtitle=t("ms.chart_prodi_dist_sub"), height=420):
        if df_prof.empty:
            st.info("No data")
        else:
            prodi_counts = df_prof["program_studi"].value_counts().head(10).reset_index()
            prodi_counts.columns = ["Prodi", "Count"]
            prodi_counts = prodi_counts.sort_values("Count", ascending=True)
            fig_prodi = px.bar(
                prodi_counts, x="Count", y="Prodi", orientation="h",
                text="Count", color="Count", color_continuous_scale="Blues"
            )
            apply_plotly_style(fig_prodi)
            fig_prodi.update_layout(height=360, margin=dict(t=10, l=10, r=20, b=0), xaxis_title="", yaxis_title="")
            fig_prodi.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_prodi, use_container_width=True)

with c_prof_4:
    with chart_panel(t("ms.chart_tools"), subtitle=t("ms.chart_tools_sub"), height=420):
        if df_prof.empty:
            st.info("No data")
        else:
            tools_series = df_prof["tools"].dropna().astype(str)
            all_tools = []
            for tools_list in tools_series:
                all_tools.extend([t.strip() for t in tools_list.split(",") if t.strip()])
            tools_df = pd.Series(all_tools).value_counts().head(10).reset_index()
            tools_df.columns = ["Tool", "Count"]
            tools_df = tools_df.sort_values("Count", ascending=True)
            
            fig_tools = px.bar(
                tools_df, x="Count", y="Tool", orientation="h",
                text="Count", color="Count", color_continuous_scale="Blues"
            )
            apply_plotly_style(fig_tools)
            fig_tools.update_layout(height=360, margin=dict(t=10, l=10, r=20, b=0), xaxis_title="", yaxis_title="")
            fig_tools.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_tools, use_container_width=True)

section_divider()

# bt-06: eligibility section
st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("ms.eligibility_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("ms.eligibility_caption")} (BT-06)</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

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
left, right = st.columns([3, 2], gap="large")

with left:
    with chart_panel(t("ms.chart_elig_prodi"), height=430, subtitle=t("ms.chart_elig_prodi_sub")):
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
    with chart_panel(t("ms.chart_elig_comp"), height=430, subtitle=t("ms.chart_elig_comp_sub")):
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

with table_panel(t("ms.detail_title"), height=430, subtitle=t("ms.detail_title_sub")):
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
st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("ms.matching_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("ms.matching_caption")} (BT-01)</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

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
        def _box(title, val, align="center"):
            return f"""<div style="background:var(--bg-color); border:1px solid var(--border-color); border-radius:12px; padding:16px; text-align:{align}; box-shadow:0 1px 2px rgba(0,0,0,0.02); margin-bottom:16px;">
                <div style="font-size:12px; font-weight:700; color:var(--text-color); opacity:0.7; margin-bottom:8px; text-transform:uppercase; font-family:'Inter',sans-serif;">{title}</div>
                <div style="font-size:16px; font-weight:600; color:var(--text-color); line-height:1.4; font-family:'Montserrat',sans-serif;">{val}</div>
            </div>"""
            
        d1, d2, d3, d4 = st.columns([3, 2, 2, 4])
        d1.markdown(_box(t('ms.position'), _f('nama_posisi')), unsafe_allow_html=True)
        d2.markdown(_box(t('ms.type'), _f('jenis_penempatan')), unsafe_allow_html=True)
        d3.markdown(_box(t('ms.min_semester'), _f('minimum_semester')), unsafe_allow_html=True)
        d4.markdown(_box(t('ms.field_required'), _f('bidang_studi_dibutuhkan')), unsafe_allow_html=True)
        
        if str(_f("deskripsi_requirement")) not in ("\u2014", ""):
            d_full = st.columns(1)[0]
            d_full.markdown(_box(t('ms.requirement'), _f('deskripsi_requirement'), align="left"), unsafe_allow_html=True)

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

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

        st.markdown(f'''
            <div class="smile-panel-title" style="margin-top:-20px; margin-bottom:12px; padding-bottom:4px;">
                {t("ms.matching_kpi_title")}
                <div style='font-family: "Inter", sans-serif; font-size: 12px; color: var(--text-color); opacity: 0.65; margin: 4px 0 0 0; font-weight: 400; text-transform: none; letter-spacing: normal;'>{t("ms.matching_kpi_sub")}</div>
            </div>
        ''', unsafe_allow_html=True)

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

        st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

        with table_panel(t("ms.rank_title"), height=430, subtitle=t("ms.rank_title_sub")):
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
