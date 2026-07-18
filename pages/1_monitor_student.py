"""
Monitor Student — the student-supply side. Owner: Person B.

BT-06  Kelayakan Mahasiswa — who is fit to send to companies (eligibility
       derived from CV / portofolio / IPK / status / ketersediaan).
BT-01  Matching Talent — rank eligible students against a talent request.

Read-only against the CSV layer (Layer 1). No Supabase, no writes.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.layout import (
    page_header, filter_bar, metric_strip, chart_panel,
    table_panel, panel, card_grid, section_divider,
)
from utils.theme import COLORS
from utils import queries, metrics

ELIGIBILITY_COLORS = {"Eligible": COLORS["success"], "Ineligible": COLORS["danger"]}

page_header(
    "Monitor Student",
    "BT-06 Eligibility · BT-01 Talent Matching",
)

# ──────────────────────────────────────────────────────────────
#  Ringkasan — at-a-glance KPI hero (filter-independent)
# ──────────────────────────────────────────────────────────────
summary = queries.get_student_supply_summary()
metric_strip([
    {"label": "Total Mahasiswa", "value": f"{summary['total']:,}"},
    {"label": "Available", "value": f"{summary['available']:,}"},
    {"label": "Sudah Ditempatkan", "value": f"{summary['placed']:,}"},
    {"label": "Program Studi", "value": f"{summary['n_prodi']:,}"},
    {"label": "Rata-rata IPK",
     "value": f"{summary['avg_ipk']:.2f}" if summary["avg_ipk"] is not None else "—"},
])

section_divider()

# ──────────────────────────────────────────────────────────────
#  BT-06 — Eligibility
# ──────────────────────────────────────────────────────────────
st.markdown("### Kelayakan Mahasiswa · BT-06")
st.caption("Kondisi apa saja yang membuat mahasiswa eligible untuk ditempatkan ke perusahaan?")

with filter_bar():
    ipk_min = st.slider("Minimum IPK", 0.0, 4.0, 3.0, 0.05)
    c1, c2, c3, c4 = st.columns(4)
    require_cv = c1.checkbox("CV ada", value=True)
    require_portfolio = c2.checkbox("Portofolio ada", value=True)
    require_active = c3.checkbox("Status aktif", value=True)
    require_available = c4.checkbox("Available", value=True)

df = queries.get_student_eligibility(
    ipk_min=ipk_min,
    require_cv=require_cv,
    require_portfolio=require_portfolio,
    require_active=require_active,
    require_available=require_available,
)

# Display filters (do not change eligibility, only what is shown)
with filter_bar():
    f1, f2 = st.columns([2, 1])
    prodi_opts = sorted(df["program_studi"].dropna().astype(str).unique().tolist())
    prodi_sel = f1.multiselect(
        "Filter program studi", prodi_opts, default=[],
        help="Leave empty to include all program studi.",
    )
    view = f2.radio("Tampilkan", ["Eligible", "Semua", "Ineligible"], horizontal=True)

view_df = df.copy()
if prodi_sel:
    view_df = view_df[view_df["program_studi"].isin(prodi_sel)]
if view == "Eligible":
    view_df = view_df[view_df["is_eligible"]]
elif view == "Ineligible":
    view_df = view_df[~view_df["is_eligible"]]

# Metrics reflect the current program-studi scope (not the show-toggle).
scope = df[df["program_studi"].isin(prodi_sel)] if prodi_sel else df
n_total = len(scope)
n_eligible = int(scope["is_eligible"].sum())
elig_pct = round(n_eligible / n_total * 100, 1) if n_total else 0.0
avg_ipk_elig = scope.loc[scope["is_eligible"], "IPK"].mean()

metric_strip([
    {"label": "Eligible", "value": f"{n_eligible:,}",
     "delta": f"{elig_pct}%",
     "sentiment": "success" if elig_pct >= 50 else "warning" if elig_pct >= 25 else "danger"},
    {"label": "Ineligible", "value": f"{n_total - n_eligible:,}",
     "sentiment": "neutral"},
    {"label": "Rata-rata IPK (eligible)",
     "value": f"{avg_ipk_elig:.2f}" if pd.notna(avg_ipk_elig) else "—"},
])

section_divider()
left, right = card_grid(2)

with left:
    with chart_panel("Eligible vs Ineligible per Program Studi", height=430):
        by_prodi = (
            scope.assign(elig=scope["is_eligible"].map({True: "Eligible", False: "Ineligible"}))
            .groupby(["program_studi", "elig"]).size().reset_index(name="jumlah")
        )
        if by_prodi.empty:
            st.info("Tidak ada data untuk scope ini.")
        else:
            fig = px.bar(
                by_prodi, x="program_studi", y="jumlah", color="elig",
                barmode="stack",
                category_orders={"elig": ["Eligible", "Ineligible"]}, height=350,
            )
            fig.update_layout(
                xaxis_title="", yaxis_title="Jumlah mahasiswa",
                xaxis_tickangle=-25, legend_title_text="",
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

with right:
    with chart_panel("Komposisi Kelayakan", height=430):
        comp = (
            scope["is_eligible"].map({True: "Eligible", False: "Ineligible"})
            .value_counts().reset_index()
        )
        comp.columns = ["status", "jumlah"]
        if comp.empty:
            st.info("Tidak ada data untuk scope ini.")
        else:
            fig = px.pie(
                comp, names="status", values="jumlah", hole=0.55, color="status",
                height=350,
            )
            fig.update_traces(textinfo="label+percent")
            fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

with table_panel("Detail Mahasiswa", height=430):
    st.caption(f"Menampilkan {len(view_df):,} mahasiswa.")
    show_cols = [c for c in [
        "NIM", "nama", "program_studi", "semester", "IPK", "CV", "portofolio",
        "status", "ketersediaan", "domisili", "is_eligible", "ineligible_reasons",
    ] if c in view_df.columns]
    st.dataframe(
        view_df[show_cols], use_container_width=True, hide_index=True,
        column_config={
            "is_eligible": st.column_config.CheckboxColumn("Eligible"),
            "IPK": st.column_config.NumberColumn("IPK", format="%.2f"),
            "ineligible_reasons": st.column_config.TextColumn("Alasan tidak eligible", width="large"),
        },
    )

# ──────────────────────────────────────────────────────────────
#  BT-01 — Talent Matching
# ──────────────────────────────────────────────────────────────
section_divider()
st.markdown("### Matching Talent · BT-01")
st.caption(
    "Pick a talent request, then rank the currently-eligible students against "
    "its program studi, minimum semester, and required tools."
)

requests = queries.get_talent_requests()

if requests is None or requests.empty:
    st.info("Belum ada talent request pada dataset.")
else:
    def _req_label(row):
        posisi = row.get("nama_posisi", "?")
        perusahaan = row.get("nama_perusahaan", row.get("id_company", ""))
        return f"{row['id_talent_req']} · {posisi} @ {perusahaan}"

    labels = {_req_label(r): r["id_talent_req"] for _, r in requests.iterrows()}
    chosen = st.selectbox("Talent request", list(labels.keys()))
    req = requests[requests["id_talent_req"] == labels[chosen]].iloc[0]

    def _f(field, default="—"):
        val = req.get(field, default)
        return default if pd.isna(val) else val

    with panel("Detail Permintaan"):
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Posisi", _f("nama_posisi"))
        d2.metric("Jenis", _f("jenis_penempatan"))
        d3.metric("Headcount", _f("headcount"))
        d4.metric("Min. semester", _f("minimum_semester"))
        st.markdown(f"**Bidang studi dibutuhkan:** {_f('bidang_studi_dibutuhkan')}")
        if str(_f("deskripsi_requirement")) not in ("—", ""):
            st.markdown(f"**Requirement:** {_f('deskripsi_requirement')}")

    eligible_only = df[df["is_eligible"]]
    matches = metrics.match_students_to_request(eligible_only, req)

    if matches.empty:
        st.warning("Tidak ada mahasiswa eligible untuk dicocokkan (longgarkan rule di atas).")
    else:
        try:
            headcount = int(float(_f("headcount", 0)))
        except (ValueError, TypeError):
            headcount = 0
        strong = int((matches["match_score"] >= 70).sum())
        perfect = int((matches["match_score"] >= 100).sum())

        metric_strip([
            {"label": "Kandidat eligible", "value": f"{len(matches):,}"},
            {"label": "Cocok kuat (≥70)", "value": f"{strong:,}",
             "sentiment": "success" if strong >= headcount and headcount > 0 else "warning"},
            {"label": "Cocok sempurna (100)", "value": f"{perfect:,}"},
            {"label": "Headcount diminta", "value": f"{headcount:,}" if headcount else "—"},
        ])

        with table_panel("Peringkat Kandidat", height=430):
            cols = [c for c in [
                "NIM", "nama", "program_studi", "semester", "IPK", "tools",
                "match_bidang", "match_semester", "match_tools", "match_score",
            ] if c in matches.columns]
            st.dataframe(
                matches[cols], use_container_width=True, hide_index=True,
                column_config={
                    "IPK": st.column_config.NumberColumn("IPK", format="%.2f"),
                    "match_bidang": st.column_config.NumberColumn("Bidang", format="%.0f",
                        help="1 = program studi cocok"),
                    "match_semester": st.column_config.NumberColumn("Semester", format="%.0f",
                        help="1 = memenuhi minimum semester"),
                    "match_tools": st.column_config.ProgressColumn("Tools", min_value=0, max_value=1,
                        format="%.0f%%"),
                    "match_score": st.column_config.ProgressColumn("Skor", min_value=0, max_value=100,
                        format="%.0f"),
                },
            )
