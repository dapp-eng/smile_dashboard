import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.layout import (
    inject_global_css, page_header, metric_strip, chart_panel,
    table_panel, card_grid, section_divider, filter_bar
)
from utils.theme import COLORS, CHART_PALETTE, apply_plotly_style, PROGRESS_COLORS, REJECTION_COLORS
from utils.data_loader import load_csv_table
from utils.metrics import get_ghosting_flags

# Page setup
inject_global_css()
page_header(
    "Monitor Process",
    "BT-05 — Proses seleksi dan deteksi ghosting",
    page_title="Monitor Process | SMILE"
)

# Load Data
df_track = load_csv_table("tracking_student")
df_company = load_csv_table("tracking_company")

# Use max send_date as 'today' so old mock data doesn't falsely flag everyone as ghosted
df_company["send_date"] = pd.to_datetime(df_company["send_date"], dayfirst=True, errors="coerce")
reference_date = df_company["send_date"].max()
df_all_ghosting = get_ghosting_flags(df_track, tracking_company=df_company, today=reference_date, include_healthy=True)
df_ghost = df_all_ghosting[df_all_ghosting["ghosting_check"] != "Healthy"]

# Inject system-detected flags into df_track so all top charts reflect the true system state
mapping = {
    "overdue_unlabeled_ghosting": "Ghosting",
    "overdue_unlabeled_fu3": "FU 3",
    "overdue_unlabeled_fu2": "FU 2",
    "overdue_unlabeled_fu1": "FU 1"
}
sys_updates = df_all_ghosting[df_all_ghosting["ghosting_check"].str.startswith("overdue_unlabeled", na=False)]
if not sys_updates.empty:
    sys_updates = sys_updates.set_index("id_tracking_student")["ghosting_check"].replace(mapping)
    df_track.set_index("id_tracking_student", inplace=True)
    df_track.update(pd.DataFrame({"progress_student": sys_updates}))
    df_track.reset_index(inplace=True)

if df_track.empty:
    st.info("Tidak ada data tracking tersedia.")
    st.stop()

# -------------------------------------------------------------
# Row 1: KPI Metrics
# -------------------------------------------------------------
total_tracked = len(df_track)
finished_statuses = ["Placement", "Rejected", "Unresolved", "Ghosting"]
active_in_process = len(df_track[~df_track["progress_student"].isin(finished_statuses)])
total_placement = len(df_track[df_track["progress_student"] == "Placement"])
total_ghosted = len(df_ghost)

metric_strip([
    {"label": "Total Candidates Tracked", "value": f"{total_tracked:,}"},
    {"label": "Total Active In Process", "value": f"{active_in_process:,}"},
    {"label": "Total Placement", "value": f"{total_placement:,}"},
    {"label": "Total Ghosted", "value": f"{total_ghosted:,}", "sentiment": "danger" if total_ghosted > 0 else "success"}
])

section_divider()

st.markdown('''
    <h3 style='margin-bottom: 0.2rem;'>Candidate Status Overview</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>Where every candidate stands right now</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2], gap="medium")

with c1:
    with chart_panel("Stage Distribution", height=420, subtitle="Drill into any status to see its stage-by-stage breakdown"):
        cat_filter = st.selectbox(
            "Category Filter", 
            ["All", "Active", "Follow-Up", "Finished", "Rejected"],
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
            xaxis_title="Candidates",
            yaxis_title="Stages",
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
    with chart_panel("Process Status", height=420, subtitle="Candidate breakdown by process and stage"):
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

st.caption("**Stage Codes:** S0 (CV Screening), S1 (Selecting Student), S2 (Study Case), S3 (CDC Briefing), S4 (Interview User), S5 (Final Interview). **'R.' prefix in Sunburst** denotes Rejection at that stage.")
section_divider()

# -------------------------------------------------------------
# Row 3: Rejection Metrics
# -------------------------------------------------------------
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

st.markdown('''
    <h3 style='margin-bottom: 0.2rem;'>Rejection & Pipeline Analysis</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>Detailed breakdown of where candidates fall out of the process</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

r1, r2 = st.columns([2, 3], gap="medium")

with r1:
    with chart_panel("Rejection Rate by Stage", height=460, subtitle="Percentage of candidates rejected at each stage"):
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
            xaxis_title="", yaxis_title="Rejection Rate (%)",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-45)
        )
        max_rate = df_rates["rate"].max()
        fig_rej.update_yaxes(range=[0, max_rate * 1.3 if max_rate > 0 else 20])
        fig_rej.update_traces(texttemplate='%{y}%', textposition='outside', cliponaxis=False)
        st.plotly_chart(fig_rej, use_container_width=True)

with r2:
    with chart_panel("Pipeline Flow", height=460, subtitle="Volume of candidates entering and falling out of each stage"):
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
            wf_x = ["Resolved Candidates", "Ghosting"]
            wf_y = [entered_counts[0] + ghost_count, -ghost_count]
            wf_measure = ["absolute", "relative"]
            
            for i in range(5):
                if i == 2:
                    continue  # Skip CDC Briefing Student (Training, no rejections)
                wf_x.append(f"Rejected<br>{stage_names[i]}")
                wf_y.append(-rejected_counts[i])
                wf_measure.append("relative")
                
            wf_x.append("Placement")
            wf_y.append(placement_count)
            wf_measure.append("total")
            
            fig_wf = go.Figure(go.Waterfall(
                name="Pipeline Attrition",
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
                yaxis=dict(title="Candidates", showgrid=True),
                xaxis=dict(tickangle=-45)
            )
            st.plotly_chart(fig_wf, use_container_width=True)
        else:
            st.info("No data available to construct Waterfall chart.")

st.caption("**Stage Codes:** S0 (CV Screening), S1 (Selecting Student), S2 (Study Case), S3 (CDC Briefing), S4 (Interview User), S5 (Final Interview).")

with chart_panel("Top 10 Companies by Rejection Impact", height=420, subtitle="Companies ranked by highest combined rejection volume and rate"):
    company_totals = df_track.groupby("company").size().reset_index(name="Total")
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
            
        top_10_rej_company = rej_by_company.sort_values(["Composite_Score", "Rejection Count"], ascending=[True, False]).head(10)
        top_10_rej_company = top_10_rej_company.sort_values(["Composite_Score", "Rejection Count"], ascending=[False, True])
        
        fig_rej_comp = px.bar(
            top_10_rej_company, x="Impact Score", y="company", orientation="h",
            color_discrete_sequence=[COLORS["danger"]],
            text="custom_label"
        )
        apply_plotly_style(fig_rej_comp)
        fig_rej_comp.update_layout(
            height=340, margin=dict(t=10, l=10, r=20, b=10),
            xaxis_title="Impact Score (0-100)", yaxis_title=""
        )
        fig_rej_comp.update_traces(textposition="outside", cliponaxis=False)
        
        fig_rej_comp.update_xaxes(range=[0, 115])
        
        st.plotly_chart(fig_rej_comp, use_container_width=True)
    else:
        st.info("No rejection data to display.")

section_divider()

# -------------------------------------------------------------
# Row 4: Ghosting Metrics
# -------------------------------------------------------------

st.markdown('''
    <h3 style='margin-bottom: 0.2rem;'>Ghosting & System Detection</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>Impact of automated tracking vs manual labeling</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

g2, g1 = st.columns(2, gap="medium")

with g1:
    with chart_panel("Labeling Lag Analysis", height=400, subtitle="Time difference between System Detection and CDC Label"):
        confirmed_ghost = df_ghost[df_ghost["progress_student"] == "Ghosting"].copy()
        
        if not confirmed_ghost.empty:
            confirmed_ghost["last_update"] = pd.to_datetime(confirmed_ghost["last_update"], errors="coerce")
            confirmed_ghost["send_date"] = pd.to_datetime(confirmed_ghost["send_date"], errors="coerce")
            
            # CDC ghosting label date - (send_date + 28)
            confirmed_ghost["lag_days"] = (confirmed_ghost["last_update"] - (confirmed_ghost["send_date"] + pd.Timedelta(days=28))).dt.days
            
            confirmed_ghost = confirmed_ghost.dropna(subset=["lag_days"])
            
            if not confirmed_ghost.empty:
                std_dev = confirmed_ghost["lag_days"].std()
                median_lag = confirmed_ghost["lag_days"].median()
                
                # Fallback to bar chart if variance is very low
                if pd.isna(std_dev) or std_dev < 1.0 or confirmed_ghost["lag_days"].nunique() <= 2:
                    avg_system_days = 28.0
                    avg_manual_days = (confirmed_ghost["last_update"] - confirmed_ghost["send_date"]).dt.days.mean()
                    
                    df_bar = pd.DataFrame({
                        "Method": ["System Detection", "CDC Manual Label"],
                        "Avg Days": [avg_system_days, avg_manual_days]
                    })
                    
                    fig_gh = px.bar(df_bar, x="Method", y="Avg Days", text_auto=".1f", color="Method",
                                 color_discrete_map={"System Detection": COLORS["danger"], "CDC Manual Label": CHART_PALETTE[0]})
                    apply_plotly_style(fig_gh)
                    fig_gh.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10), showlegend=False)
                    st.plotly_chart(fig_gh, use_container_width=True)
                else:
                    # Explicitly set bin size to ~5
                    min_val = confirmed_ghost["lag_days"].min()
                    max_val = confirmed_ghost["lag_days"].max()
                    
                    fig_gh = px.histogram(
                        confirmed_ghost, x="lag_days", 
                        color_discrete_sequence=[CHART_PALETTE[0]]
                    )
                    fig_gh.update_traces(xbins=dict(start=min_val, end=max_val, size=5))
                    apply_plotly_style(fig_gh)
                    fig_gh.update_layout(
                        height=320, margin=dict(t=10, l=10, r=10, b=10),
                        xaxis_title="Lag in Days",
                        yaxis_title="Case Count",
                        bargap=0.1
                    )
                    st.plotly_chart(fig_gh, use_container_width=True)
            else:
                st.info("No valid date data for confirmed ghosting.")
        else:
            st.info("No confirmed Ghosting cases available.")

with g2:
    with chart_panel("System Detection Impact", height=400, subtitle="Comparison of ghosting flags raised by CDC vs System"):
        if not df_ghost.empty:
            def get_granular_severity(g):
                if g in ["Ghosting", "overdue_unlabeled_ghosting"]: return "Ghosting"
                elif g in ["overdue_unlabeled_fu1", "overdue_unlabeled_fu2", "overdue_unlabeled_fu3"]: return "FU 1-3"
                elif g == "FU 3": return "FU 3"
                elif g == "FU 2": return "FU 2"
                elif g == "FU 1": return "FU 1"
                return "Unknown"
                
            def get_source(g):
                if "overdue_unlabeled" in g:
                    return "System Detected"
                return "CDC Labeled"

            df_ghost["granular_severity"] = df_ghost["ghosting_check"].apply(get_granular_severity)
            df_ghost["source"] = df_ghost["ghosting_check"].apply(get_source)

            sev_counts = df_ghost.groupby(["source", "granular_severity"]).size().reset_index(name="Count")
            
            fig_impact = px.sunburst(
                sev_counts, path=["source", "granular_severity"], values="Count",
                color="source",
                color_discrete_map={"CDC Labeled": CHART_PALETTE[0], "System Detected": COLORS["danger"]},
                height=320
            )
            fig_impact.update_traces(textinfo="label+percent parent")
            apply_plotly_style(fig_impact)
            fig_impact.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_impact, use_container_width=True)
        else:
            st.info("No ghosting data to display.")

with chart_panel("Top 10 Companies by Ghosting Impact", height=420, subtitle="Companies ranked by highest combined ghosting volume and rate"):
    if not df_ghost.empty:
        company_totals = df_track.groupby("company").size().reset_index(name="Total")
        ghost_by_company = df_ghost.groupby("company").size().reset_index(name="Ghosting Count")
        ghost_by_company = ghost_by_company.merge(company_totals, on="company")
        ghost_by_company["Ghosting Rate (%)"] = (ghost_by_company["Ghosting Count"] / ghost_by_company["Total"] * 100).round(1)
        
        ghost_by_company["custom_label"] = ghost_by_company.apply(
            lambda row: f"<b>{int(row['Ghosting Count'])}</b>/{int(row['Total'])} ({row['Ghosting Rate (%)']}%)", axis=1
        )
        
        ghost_by_company["Rank_Vol"] = ghost_by_company["Ghosting Count"].rank(method="min", ascending=False)
        ghost_by_company["Rank_Rate"] = ghost_by_company["Ghosting Rate (%)"].rank(method="min", ascending=False)
        ghost_by_company["Composite_Score"] = ghost_by_company["Rank_Vol"] + ghost_by_company["Rank_Rate"]
        
        c_min = ghost_by_company["Composite_Score"].min()
        c_max = ghost_by_company["Composite_Score"].max()
        if c_max > c_min:
            ghost_by_company["Impact Score"] = 100 * (1 - (ghost_by_company["Composite_Score"] - c_min) / (c_max - c_min))
        else:
            ghost_by_company["Impact Score"] = 100.0
            
        top_10_company = ghost_by_company.sort_values(["Composite_Score", "Ghosting Count"], ascending=[True, False]).head(10)
        top_10_company = top_10_company.sort_values(["Composite_Score", "Ghosting Count"], ascending=[False, True])
        
        fig_comp = px.bar(
            top_10_company, x="Impact Score", y="company", orientation="h",
            color_discrete_sequence=[COLORS["warning"]],
            text="custom_label"
        )
        apply_plotly_style(fig_comp)
        fig_comp.update_layout(
            height=340, margin=dict(t=10, l=10, r=20, b=10),
            xaxis_title="Impact Score (0-100)", yaxis_title=""
        )
        fig_comp.update_traces(textposition="outside", cliponaxis=False)
        
        fig_comp.update_xaxes(range=[0, 115])
        
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("No ghosting data to display.")

section_divider()

# -------------------------------------------------------------
# Row 5: Unified Master Table & Drill Down
# -------------------------------------------------------------

st.markdown('''
    <h3 style='margin-bottom: 0.2rem;'>Individual Student Tracker</h3>
    <p style='font-size: 12px; color: var(--text-color); opacity: 0.65; margin-top: -0.2rem; margin-bottom: 0.5rem;'>Search and filter individual candidate pipelines</p>
    <hr style='width: 80%; margin-left: 0; margin-top: 0; margin-bottom: 1.5rem; border: none; border-bottom: 1px solid var(--border-color, #E2E8F0);'>
''', unsafe_allow_html=True)

with table_panel("", height=None):
    if df_all_ghosting.empty:
        st.success("🎉 Tidak ada data kandidat aktif.")
    else:
        display_cols = [
            "NIM", "student_name", "company", "position",
            "jenis_penempatan", "progress_student", "ghosting_check", "days_since_update"
        ]

        with filter_bar():
            f1, f2, f3 = st.columns(3)
            with f1:
                search_query = st.text_input("Search (Name/NIM)", "")
            with f2:
                companies = sorted(df_all_ghosting["company"].dropna().unique())
                sel_company = st.multiselect("Filter by Company", options=companies)
            with f3:
                severities = sorted(df_all_ghosting["ghosting_check"].dropna().unique())
                sel_severity = st.multiselect("Filter by Severity", options=severities)

        df_ghost_view = df_all_ghosting.copy()

        if search_query:
            query = search_query.lower()
            mask = (
                df_ghost_view["student_name"].str.lower().str.contains(query, na=False) |
                df_ghost_view["NIM"].astype(str).str.contains(query, na=False)
            )
            df_ghost_view = df_ghost_view[mask]

        if sel_company:
            df_ghost_view = df_ghost_view[df_ghost_view["company"].isin(sel_company)]

        if sel_severity:
            df_ghost_view = df_ghost_view[df_ghost_view["ghosting_check"].isin(sel_severity)]

        df_ghost_view = df_ghost_view.sort_values("days_since_update", ascending=False).reset_index(drop=True)

        st.caption("Klik salah satu baris untuk melihat riwayat kandidat selengkapnya.")

        event = st.dataframe(
            df_ghost_view[display_cols],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "days_since_update": st.column_config.NumberColumn("Days Since Activity"),
                "ghosting_check": st.column_config.TextColumn("Severity")
            }
        )

        selected_rows = event.selection.rows
        if selected_rows:
            selected_idx = selected_rows[0]
            selected_nim = str(df_ghost_view.iloc[selected_idx]["NIM"])

            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            section_divider()
            st.subheader("Student Detail Profile")

            if "df_student_context" not in st.session_state:
                df_student = load_csv_table("student_all")
                df_status = load_csv_table("status_student")
                st.session_state["df_student_context"] = df_student.merge(df_status, on="NIM", how="inner", suffixes=("", "_status"))

            df_student_context = st.session_state["df_student_context"]

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
                            <div><strong style="opacity:0.7">Domisili:</strong><br>{student_info.get('domisili', '-')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )

            df_full_history = df_track.merge(df_company[['id_tracking_company', 'send_date']], on='id_tracking_company', how='left')
            if not df_all_ghosting.empty and 'id_tracking_student' in df_all_ghosting.columns:
                df_full_history = df_full_history.merge(df_all_ghosting[['id_tracking_student', 'ghosting_check', 'days_since_update']], on='id_tracking_student', how='left')
            else:
                df_full_history["ghosting_check"] = "-"
                df_full_history["days_since_update"] = 0

            df_full_history["ghosting_check"] = df_full_history["ghosting_check"].fillna("-")
            df_full_history["days_since_update"] = df_full_history["days_since_update"].fillna(0)

            df_history = df_full_history[df_full_history["NIM"].astype(str) == selected_nim].copy()

            if df_history.empty:
                st.info("Kandidat ini belum memiliki riwayat aplikasi.")
            else:
                df_history = df_history.sort_values("last_update", ascending=False)

                html_rows = []
                for _, row in df_history.iterrows():
                    prog = str(row["progress_student"])
                    color = PROGRESS_COLORS.get(prog, COLORS["neutral"])
                    badge_html = f'<span style="background-color: {color}; border-radius: 12px; padding: 4px 10px; color: white; font-size: 12px; font-weight: 600; white-space: nowrap;">{prog}</span>'

                    send_dt = pd.to_datetime(row["send_date"]).strftime("%Y-%m-%d") if pd.notnull(row["send_date"]) else "-"
                    last_dt = pd.to_datetime(row["last_update"], format="mixed", dayfirst=True).strftime("%Y-%m-%d") if pd.notnull(row["last_update"]) else "-"

                    ghost_check = row.get('ghosting_check', '-')

                    html_rows.append(f"""<tr style="border-bottom: 1px solid var(--border-color);">
    <td style="padding: 12px 16px;">{row.get('company', '-')}</td>
    <td style="padding: 12px 16px;">{row.get('position', '-')}</td>
    <td style="padding: 12px 16px;">{row.get('jenis_penempatan', '-')}</td>
    <td style="padding: 12px 16px;">{badge_html}</td>
    <td style="padding: 12px 16px;">{send_dt}</td>
    <td style="padding: 12px 16px;">{last_dt}</td>
    <td style="padding: 12px 16px;">{ghost_check}</td>
</tr>""")

                table_html = f"""<div class="smile-panel" style="padding: 0; overflow-x: auto; margin-bottom: 0;">
    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 14px; text-align: left;">
        <thead>
            <tr style="background-color: rgba(0,0,0,0.02);">
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Company</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Position</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Type</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Progress</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Send Date</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Last Update</th>
                <th style="padding: 14px 16px; border-bottom: 2px solid var(--border-color); color: var(--text-color); opacity: 0.8; font-weight: 600;">Severity</th>
            </tr>
        </thead>
        <tbody>
            {''.join(html_rows)}
        </tbody>
    </table>
</div>"""
                st.markdown(table_html, unsafe_allow_html=True)