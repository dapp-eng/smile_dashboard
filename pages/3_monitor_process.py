# monitor process - bt-02 selection progress, bt-05 ghosting detection

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.layout import (
    inject_global_css, page_header, metric_strip, chart_panel,
    table_panel, card_grid, section_divider, filter_bar,
)
from utils.theme import COLORS, CHART_PALETTE, apply_plotly_style, PROGRESS_COLORS, REJECTION_COLORS
from utils.data_loader import load_csv_table
from utils.metrics import get_ghosting_flags
from utils.i18n import t

# page setup
inject_global_css()
page_header(
    t("page.monitor_process"),
    bt_caption=t("bt.02_05"),
)

# load data
df_track = load_csv_table("tracking_student")
df_company = load_csv_table("tracking_company")

# use max send_date as reference to avoid false ghosting flags on old data
df_company["send_date"] = pd.to_datetime(df_company["send_date"], dayfirst=True, errors="coerce")
reference_date = df_company["send_date"].max()
df_all_ghosting = get_ghosting_flags(
    df_track, tracking_company=df_company, today=reference_date, include_healthy=True,
)
fu_ghost_set = ["FU 1", "FU 2", "FU 3", "Ghosting"]
df_ghost = df_all_ghosting[df_all_ghosting["progress_student_system"].isin(fu_ghost_set)]

# inject system detected flags into tracking student data
sys_updates = df_all_ghosting[
    df_all_ghosting["progress_student_system"] != df_all_ghosting["progress_student"]
]
if not sys_updates.empty:
    overrides = sys_updates.set_index("id_tracking_student")["progress_student_system"]
    df_track.set_index("id_tracking_student", inplace=True)
    df_track.update(pd.DataFrame({"progress_student": overrides}))
    df_track.reset_index(inplace=True)

if df_track.empty:
    st.info(t("mp.no_tracking"))
    st.stop()

# kpi metrics
total_tracked = len(df_track)
finished_statuses = ["Placement", "Rejected", "Unresolved", "Ghosting"]
active_in_process = len(df_track[~df_track["progress_student"].isin(finished_statuses)])
total_placement = len(df_track[df_track["progress_student"] == "Placement"])

df_ghost_only = df_all_ghosting[df_all_ghosting["progress_student_system"] == "Ghosting"]
df_followup_only = df_all_ghosting[df_all_ghosting["progress_student_system"].isin(["FU 1", "FU 2", "FU 3"])]

total_ghosted = len(df_ghost_only)
total_followup = len(df_followup_only)

metric_strip([
    {"label": t("mp.total_tracked"), "value": f"{total_tracked:,}"},
    {"label": t("mp.active_in_process"), "value": f"{active_in_process:,}"},
    {"label": t("mp.total_placement"), "value": f"{total_placement:,}"},
    {
        "label": t("mp.total_followup"),
        "value": f"{total_followup:,}",
        "sentiment": "warning" if total_followup > 0 else "success",
    },
    {
        "label": t("mp.total_ghosted"),
        "value": f"{total_ghosted:,}",
        "sentiment": "danger" if total_ghosted > 0 else "success",
    },
])

section_divider()

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mp.status_overview_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mp.status_overview_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2], gap="medium")

with c1:
    with chart_panel(t("mp.stage_dist"), height=420, subtitle=t("mp.stage_dist_sub")):
        # canonical (untranslated) filter values used for logic; labels shown are translated
        category_values = ["All", "Active", "Follow-Up", "Finished", "Rejected"]
        category_labels = {
            "All": t("mp.cat_all"),
            "Active": t("mp.cat_active"),
            "Follow-Up": t("mp.cat_followup"),
            "Finished": t("mp.cat_finished"),
            "Rejected": t("mp.cat_rejected"),
        }
        cat_filter = st.selectbox(
            t("mp.category_filter"),
            category_values,
            format_func=lambda v: category_labels[v],
            label_visibility="collapsed"
        )

        stage_group_map = {
            "Selecting Student by Company": "Active", "Study Case": "Active",
            "CDC Briefing Student": "Active", "Interview User": "Active", "Final Interview": "Active",
            "FU 1": "Follow-Up", "FU 2": "Follow-Up", "FU 3": "Follow-Up",
            "Ghosting": "Finished", "Rejected": "Finished", "Placement": "Finished",
            "Unresolved": "Finished"
        }

        rename_map = {
            "Selecting Student by Company": "S1",
            "Study Case": "S2",
            "CDC Briefing Student": "S3",
            "Interview User": "S4",
            "Final Interview": "S5",
            "Rejection Screening CV": "Rejection S0",
            "Rejection Study Case": "Rejection S2",
            "Rejection Interview User": "Rejection S4",
            "Rejection Final Interview": "Rejection S5",

        }

        df_c1 = df_track.copy()
        df_c1["stage_group"] = df_c1["progress_student"].map(stage_group_map)

        if cat_filter == "All":
            def get_all_display(row):
                if row["stage_group"] == "Finished":
                    return row["progress_student"]
                return row["stage_group"]
            df_c1["display_stage"] = df_c1.apply(get_all_display, axis=1)
        elif cat_filter == "Rejected":
            df_c1 = df_c1[df_c1["progress_student"] == "Rejected"]
            def get_rej_stage(row):
                rej = str(row["rejection"]) if pd.notna(row["rejection"]) else "Rejected (Unknown)"
                return rej if "Reject" in rej else "Rejected (Unknown)"
            df_c1["display_stage"] = df_c1.apply(get_rej_stage, axis=1)
        else:
            df_c1 = df_c1[df_c1["stage_group"] == cat_filter]
            df_c1["display_stage"] = df_c1["progress_student"]

        df_c1["display_stage"] = df_c1["display_stage"].replace(rename_map)

        stage_counts = df_c1["display_stage"].value_counts().reset_index()
        stage_counts.columns = ["stage", "count"]

        chrono_order = [
            "S1", "S2", "S3", "S4", "S5", "Active",
            "Placement",
            "FU 1", "FU 2", "FU 3", "Follow-Up",
            "Ghosting",
            "Rejection S0", "Rejection S2", "Rejection S4", "Rejection S5", "Rejected (Unknown)", "Rejected",
            "Unresolved"
        ]

        # Filter out categories that have no data to prevent visible gaps
        actual_stages = set(stage_counts["stage"].unique())
        chrono_order = [s for s in chrono_order if s in actual_stages]
        chrono_order.reverse()

        fig_stage = px.bar(
            stage_counts, x="count", y="stage", orientation="h",
            color_discrete_sequence=[CHART_PALETTE[0]],
            height=300,
            text="stage"
        )
        fig_stage.update_traces(
            textposition='outside',
            constraintext='none',
            cliponaxis=False
        )

        annotations = []
        for _, row in stage_counts.iterrows():
            if row["count"] > 0:
                annotations.append(dict(
                    x=row["count"],
                    y=row["stage"],
                    text=str(row["count"]),
                    xanchor='right',
                    xshift=-5,
                    yanchor='middle',
                    showarrow=False,
                    font=dict(color="white", size=9)
                ))

        apply_plotly_style(fig_stage)
        fig_stage.update_layout(
            xaxis_title=t("mp.candidates"),
            yaxis_title=t("mp.stages"),
            yaxis=dict(
                showticklabels=False,
                automargin=False,
                categoryorder='array',
                categoryarray=chrono_order
            ),
            annotations=annotations,
            margin=dict(t=10, b=10)
        )
        max_val = stage_counts["count"].max() if not stage_counts.empty else 1
        fig_stage.update_xaxes(range=[0, max_val * 1.6])
        st.plotly_chart(fig_stage, use_container_width=True)

with c2:
    with chart_panel(t("mp.process_status"), height=420, subtitle=t("mp.process_status_sub")):
        def get_sunburst_group(row):
            prog = row["progress_student"]

            rename_map = {
                "Selecting Student by Company": "S1",
                "Study Case": "S2",
                "CDC Briefing Student": "S3",
                "Interview User": "S4",
                "Final Interview": "S5",
                "Rejection Screening CV": "R.S0",
                "Rejection Study Case": "R.S2",
                "Rejection Interview User": "R.S4",
                "Rejection Final Interview": "R.S5",

            }

            if prog in ["Selecting Student by Company", "Study Case", "CDC Briefing Student", "Interview User", "Final Interview"]:
                code = rename_map.get(prog, prog)
                return "In Progress", "Active", code
            elif prog in ["FU 1", "FU 2", "FU 3"]:
                return "In Progress", "Follow-Up", prog
            elif prog == "Ghosting":
                return "Finished", "Ghosting", "Ghosting"
            elif prog == "Placement":
                return "Finished", "Placement", "Placement"
            elif prog == "Rejected":
                rej = str(row["rejection"]) if pd.notna(row["rejection"]) else "Rejected (Unknown)"
                rej_stage = rej if "Reject" in rej else "Rejected (Unknown)"
                code = rename_map.get(rej_stage, rej_stage)
                return "Finished", "Rejected", code
            elif prog == "Unresolved":
                return "Finished", "Unresolved", "Unresolved"
            return "Unknown", "Unknown", prog

        df_track[["broad_status", "granular_status", "stage"]] = df_track.apply(
            lambda x: pd.Series(get_sunburst_group(x)), axis=1
        )

        status_counts = df_track.groupby(["broad_status", "granular_status", "stage"], dropna=False).size().reset_index(name="count")

        status_colors = {
            "In Progress": CHART_PALETTE[0],
            "Finished": COLORS["neutral"],
            "Active": CHART_PALETTE[0],
            "Follow-Up": COLORS["warning"],
            "Placement": COLORS["success"],
            "Rejected": COLORS["danger"],
            "Ghosting": COLORS["danger"],
            "Unresolved": COLORS["neutral"]
        }

        fig_sun = px.sunburst(
            status_counts, path=["broad_status", "granular_status", "stage"], values="count",
            color="granular_status", color_discrete_map=status_colors,
            height=340
        )
        fig_sun.update_traces(textinfo="label+percent parent")
        apply_plotly_style(fig_sun)
        fig_sun.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig_sun, use_container_width=True)

st.caption(t("mp.stage_codes_caption"))
section_divider()

# rejection metrics
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
    }
    return prog_map.get(prog, 0)

df_track['max_stage'] = df_track.apply(get_max_stage, axis=1)

st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mp.rejection_pipeline_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mp.rejection_pipeline_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

r1, r2 = st.columns([2, 3], gap="medium")

with r1:
    with chart_panel(t("mp.rej_rate_stage"), height=460, subtitle=t("mp.rej_rate_stage_sub")):
        stages = [
            (0, "S0", "Rejection Screening CV"),
            (1, "S2", "Rejection Study Case"),
            (3, "S4", "Rejection Interview User"),
            (4, "S5", "Rejection Final Interview")
        ]

        rates = []
        for idx, stage_name, rej_val in stages:
            denom = (df_track['max_stage'] >= idx).sum()
            num = (df_track['rejection'] == rej_val).sum()
            rate = (num / denom * 100).round(1) if denom > 0 else 0
            rates.append({"stage": stage_name, "rate": rate})

        df_rates = pd.DataFrame(rates)

        fig_rej = px.bar(
            df_rates, x="stage", y="rate", orientation="v",
            color_discrete_sequence=[COLORS["danger"]],
            height=380,
            text_auto='.1f'
        )
        apply_plotly_style(fig_rej)
        fig_rej.update_layout(
            xaxis_title="", yaxis_title=t("mp.rej_rate_pct"),
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-45)
        )
        max_rate = df_rates["rate"].max()
        fig_rej.update_yaxes(range=[0, max_rate * 1.3 if max_rate > 0 else 20])
        fig_rej.update_traces(texttemplate='%{y}%', textposition='outside', cliponaxis=False)
        st.plotly_chart(fig_rej, use_container_width=True)

with r2:
    with chart_panel(t("mp.pipeline_flow"), height=460, subtitle=t("mp.pipeline_flow_sub")):
        entered_counts = {i: 0 for i in range(6)}
        rejected_counts = {i: 0 for i in range(6)}
        placement_count = 0
        ghost_count = 0

        for _, row in df_track.iterrows():
            prog = str(row['progress_student'])
            rej = str(row['rejection'])

            if prog == 'Ghosting' or rej == 'Ghosting':
                ghost_count += 1
                continue

            is_terminal = False
            is_placed = False

            if prog == 'Placement' or rej == 'Placement':
                is_terminal = True
                is_placed = True
            elif 'Reject' in rej or prog == 'Rejected':
                is_terminal = True

            if not is_terminal:
                # Skip candidates currently active in the pipeline (On Progress, FU, etc.)
                continue

            m = get_max_stage(row)

            for i in range(m + 1):
                entered_counts[i] += 1

            if is_placed:
                placement_count += 1
            else:
                rejected_counts[m] += 1

        stage_names = [
            "S1",
            "S2",
            "S3",
            "S4",
            "S5"
        ]

        if entered_counts[0] + ghost_count > 0:
            wf_x = [t("mp.resolved_candidates"), t("mp.wf_ghosting")]
            wf_y = [entered_counts[0] + ghost_count, -ghost_count]
            wf_measure = ["absolute", "relative"]

            for i in range(5):
                if i == 2:
                    continue  # Skip CDC Briefing Student (Training, no rejections)
                wf_x.append(t("mp.wf_rejected", stage=stage_names[i]))
                wf_y.append(-rejected_counts[i])
                wf_measure.append("relative")

            wf_x.append(t("mp.wf_placement"))
            wf_y.append(placement_count)
            wf_measure.append("total")

            fig_wf = go.Figure(go.Waterfall(
                name=t("mp.pipeline_attrition"),
                orientation="v",
                measure=wf_measure,
                x=wf_x,
                textposition="outside",
                text=[str(abs(val)) for val in wf_y],
                y=wf_y,
                connector={"line": {"color": "rgba(63, 63, 63, 0.5)", "width": 1, "dash": "dot"}},
                decreasing={"marker": {"color": COLORS["danger"]}},
                increasing={"marker": {"color": COLORS["primary"]}},
                totals={"marker": {"color": COLORS["success"]}},
            ))

            apply_plotly_style(fig_wf)
            fig_wf.update_traces(cliponaxis=False)
            fig_wf.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
                waterfallgap=0.2,
                showlegend=False,
                yaxis=dict(title=t("mp.candidates"), showgrid=True),
                xaxis=dict(tickangle=-45)
            )
            st.plotly_chart(fig_wf, use_container_width=True)
        else:
            st.info(t("mp.no_waterfall_data"))

st.caption(t("mp.stage_codes_caption_short"))


# ghosting metrics
st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mp.ghosting_detection_title")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mp.ghosting_detection_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

g2, g1 = st.columns(2, gap="medium")

with g1:
    with chart_panel(t("mp.sankey_title"), height=400, subtitle=t("mp.sankey_sub")):
        if not df_ghost.empty:
            import plotly.graph_objects as go
            
            df_sankey = df_ghost.copy()
            df_sankey["source_node"] = "CDC: " + df_sankey["progress_student"]
            df_sankey["target_node"] = "Sys: " + df_sankey["progress_student_system"]

            sankey_counts = df_sankey.groupby(["source_node", "target_node"]).size().reset_index(name="Count")
            
            if not sankey_counts.empty:
                all_nodes = list(pd.concat([sankey_counts["source_node"], sankey_counts["target_node"]]).unique())
                node_indices = {node: i for i, node in enumerate(all_nodes)}
                
                node_colors = []
                for node in all_nodes:
                    if "Ghosting" in node:
                        node_colors.append(COLORS["danger"])
                    elif "FU" in node:
                        node_colors.append(COLORS["warning"])
                    else:
                        node_colors.append(CHART_PALETTE[0])

                fig_sankey = go.Figure(data=[go.Sankey(
                    node = dict(
                      pad = 15,
                      thickness = 20,
                      line = dict(color = "rgba(0,0,0,0)", width = 0),
                      label = [n.replace("CDC: ", "").replace("Sys: ", "") for n in all_nodes],
                      color = node_colors
                    ),
                    link = dict(
                      source = [node_indices[src] for src in sankey_counts["source_node"]],
                      target = [node_indices[tgt] for tgt in sankey_counts["target_node"]],
                      value = sankey_counts["Count"],
                      color = "rgba(180, 180, 180, 0.2)"
                    )
                )])
                apply_plotly_style(fig_sankey)
                fig_sankey.update_layout(height=320, margin=dict(t=20, l=20, r=20, b=20), font_family="'Inter', sans-serif")
                st.plotly_chart(fig_sankey, use_container_width=True)
            else:
                st.info(t("mp.no_ghosting_data"))
        else:
            st.info(t("mp.no_ghosting_data"))

with g2:
    with chart_panel(t("mp.system_detection_impact"), height=400, subtitle=t("mp.system_detection_impact_sub")):
        if not df_ghost.empty:
            fu_ghost = {"FU 1", "FU 2", "FU 3", "Ghosting"}

            def get_source(row):
                cdc = row["progress_student"]
                system = row["progress_student_system"]
                if cdc not in fu_ghost:
                    return t("mp.system_detected")     #CDC missed it entirely
                elif cdc != system:
                    return t("mp.system_corrected")    #CDC labeled, but stale
                return t("mp.cdc_labeled")             #CDC got it right

            df_ghost_chart = df_ghost.copy()
            df_ghost_chart["severity"] = df_ghost_chart["progress_student_system"]
            df_ghost_chart["source"] = df_ghost_chart.apply(get_source, axis=1)

            sev_counts = df_ghost_chart.groupby(["source", "severity"]).size().reset_index(name="Count")

            fig_impact = px.sunburst(
                sev_counts, path=["source", "severity"], values="Count",
                color="source",
                color_discrete_map={
                    t("mp.cdc_labeled"): CHART_PALETTE[0],
                    t("mp.system_detected"): COLORS["danger"],
                    t("mp.system_corrected"): CHART_PALETTE[3],
                },
                height=320
            )
            fig_impact.update_traces(textinfo="label+percent parent")
            apply_plotly_style(fig_impact)
            fig_impact.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_impact, use_container_width=True)
        else:
            st.info(t("mp.no_ghosting_data"))


section_divider()


# unified master table and drill down
st.markdown(f'''
    <h3 style='margin-bottom: 0.2rem;'>{t("mp.unified_table")}</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>{t("mp.unified_table_sub")}</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

with table_panel("", height=None):
    # load student_all and enrich with application count and follow-up flag
    df_student_master = load_csv_table("student_all").copy()

    app_counts = df_track.groupby("NIM").size().reset_index(name="applications")
    app_counts["NIM"] = app_counts["NIM"].astype(str)
    df_student_master["NIM"] = df_student_master["NIM"].astype(str)
    df_student_master = df_student_master.merge(app_counts, on="NIM", how="left")
    df_student_master["applications"] = df_student_master["applications"].fillna(0).astype(int)

    fu_labels = {"FU 1", "FU 2", "FU 3"}
    if not df_all_ghosting.empty:
        fu_nims = df_all_ghosting[df_all_ghosting["progress_student_system"].isin(fu_labels)]["NIM"].astype(str).unique()
        df_student_master["has_follow_up"] = df_student_master["NIM"].isin(fu_nims).map({True: "Yes", False: "No"})
    else:
        df_student_master["has_follow_up"] = "No"

    display_cols = [
        "NIM", "nama", "program_studi", "semester",
        "bidang_minat", "jenis_penempatan_diminati", "applications", "has_follow_up"
    ]

    with filter_bar():
        f1, f2, f3 = st.columns(3)
        with f1:
            search_query = st.text_input(t("mp.search_nim"), "")
        with f2:
            prodi_list = sorted(df_student_master["program_studi"].dropna().unique())
            sel_prodi = st.multiselect(t("mp.filter_prodi"), options=prodi_list)
        with f3:
            fu_options = ["Yes", "No"]
            sel_fu = st.multiselect(t("mp.filter_has_fu"), options=fu_options)

    df_master_view = df_student_master.copy()

    if search_query:
        query = search_query.lower()
        mask = (
            df_master_view["nama"].str.lower().str.contains(query, na=False) |
            df_master_view["NIM"].astype(str).str.contains(query, na=False)
        )
        df_master_view = df_master_view[mask]

    if sel_prodi:
        df_master_view = df_master_view[df_master_view["program_studi"].isin(sel_prodi)]

    if sel_fu:
        df_master_view = df_master_view[df_master_view["has_follow_up"].isin(sel_fu)]

    df_master_view = df_master_view.sort_values("applications", ascending=False).reset_index(drop=True)

    st.caption(t("mp.click_row"))

    event = st.dataframe(
        df_master_view[display_cols],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "nama": st.column_config.TextColumn(t("mp.col_name")),
            "program_studi": st.column_config.TextColumn(t("mp.col_prodi")),
            "semester": st.column_config.NumberColumn(t("mp.col_semester")),
            "bidang_minat": st.column_config.TextColumn(t("mp.col_interest")),
            "jenis_penempatan_diminati": st.column_config.TextColumn(t("mp.col_placement_type")),
            "applications": st.column_config.NumberColumn(t("mp.col_applications")),
            "has_follow_up": st.column_config.TextColumn(t("mp.col_has_fu")),
        }
    )

    selected_rows = event.selection.rows
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_nim = str(df_master_view.iloc[selected_idx]["NIM"])

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        section_divider()
        st.subheader(t("mp.student_detail"))

        if "df_student_context" not in st.session_state:
            df_student = load_csv_table("student_all")
            df_status = load_csv_table("status_student")
            st.session_state["df_student_context"] = df_student.merge(df_status, on="NIM", how="inner", suffixes=("", "_status"))

        df_student_context = st.session_state["df_student_context"]

        df_full_history = df_track.merge(df_company[['id_tracking_company', 'send_date']], on='id_tracking_company', how='left')
        if not df_all_ghosting.empty and 'id_tracking_student' in df_all_ghosting.columns:
            df_full_history = df_full_history.merge(df_all_ghosting[['id_tracking_student', 'progress_student_system', 'days_since_update']], on='id_tracking_student', how='left')
        else:
            df_full_history["progress_student_system"] = df_full_history["progress_student"]
            df_full_history["days_since_update"] = 0

        df_full_history["progress_student_system"] = df_full_history["progress_student_system"].fillna(df_full_history["progress_student"])
        df_full_history["days_since_update"] = df_full_history["days_since_update"].fillna(0).astype(int)

        df_history = df_full_history[df_full_history["NIM"].astype(str) == selected_nim].copy()
        
        latest_prog = "-"
        latest_color = COLORS.get("neutral", "#E2E8F0")
        if not df_history.empty:
            df_history = df_history.sort_values("last_update", ascending=False)
            latest_prog = str(df_history.iloc[0].get('progress_student_system', df_history.iloc[0].get("progress_student", "-")))
            latest_color = PROGRESS_COLORS.get(latest_prog, COLORS.get("neutral", "#E2E8F0"))
            
        badge_html_profile = f'<span style="background-color: {latest_color}; border-radius: 12px; padding: 4px 10px; color: white; font-size: 12px; font-weight: 600; white-space: nowrap; display: inline-block; margin-top: 4px;">{latest_prog}</span>'

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
                        <div><strong style="opacity:0.7">Latest Progress:</strong><br>{badge_html_profile}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

        if df_history.empty:
            st.info(t("mp.no_history"))
        else:
            df_history = df_history.sort_values("last_update", ascending=False)

            def format_date_readable(val):
                """Format date to '1 January, 1970' style."""
                try:
                    dt = pd.to_datetime(val, format="mixed", dayfirst=True)
                    if pd.notnull(dt):
                        return dt.strftime("%-d %B, %Y") if hasattr(dt, 'strftime') else str(dt)
                except Exception:
                    pass
                return "-"

            # Windows strftime doesn't support %-d, use %#d instead
            import platform
            def fmt_date(val):
                try:
                    dt = pd.to_datetime(val, format="mixed", dayfirst=True)
                    if pd.notnull(dt):
                        if platform.system() == "Windows":
                            return dt.strftime("%#d %B, %Y")
                        return dt.strftime("%-d %B, %Y")
                except Exception:
                    pass
                return "-"

            html_rows = []
            for _, row in df_history.iterrows():
                prog = str(row.get('progress_student_system', row.get("progress_student", "-")))
                color = PROGRESS_COLORS.get(prog, COLORS["neutral"])
                badge_html = f'<span style="background-color: {color}; border-radius: 12px; padding: 4px 10px; color: white; font-size: 12px; font-weight: 600; white-space: nowrap;">{prog}</span>'

                send_dt = fmt_date(row["send_date"])
                last_dt = fmt_date(row["last_update"])
                days_since = int(row.get("days_since_update", 0))

                html_rows.append(f"""<tr style="border-bottom: 1px solid var(--border-color);">
    <td style="padding: 12px 16px;">{row.get('company', '-')}</td>
    <td style="padding: 12px 16px;">{row.get('position', '-')}</td>
    <td style="padding: 12px 16px;">{row.get('jenis_penempatan', '-')}</td>
    <td style="padding: 12px 16px;">{badge_html}</td>
    <td style="padding: 12px 16px;">{send_dt}</td>
    <td style="padding: 12px 16px;">{last_dt}</td>
    <td style="padding: 12px 16px; text-align: center;">{days_since}</td>
</tr>""")

            th_style = 'padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;'
            table_html = f"""<div class="smile-panel" style="padding: 0; overflow-x: auto; margin-bottom: 0;">
    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 14px; text-align: left;">
        <thead>
            <tr style="background-color: rgba(0,0,0,0.02);">
                <th style="{th_style}">Company</th>
                <th style="{th_style}">Position</th>
                <th style="{th_style}">Type</th>
                <th style="{th_style}">Progress</th>
                <th style="{th_style}">Send Date</th>
                <th style="{th_style}">Last Update</th>
                <th style="{th_style}; text-align: center;">Days Since Activity</th>
            </tr>
        </thead>
        <tbody>
            {''.join(html_rows)}
        </tbody>
    </table>
</div>"""
            st.markdown(table_html, unsafe_allow_html=True)

