# design tokens and plotly styling for the smile dashboard

import streamlit as st

# brand palette
COLORS = {
    "primary": "#3462ED",
    "secondary": "#4748B0",
    "navy": "#121F45",
    "font": "#1E293B",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#D4A72C",
    "neutral": "#6E7781",
    "light_bg": "#F8FAFC",
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
}

# sequential blue palette for charts (red/green/yellow reserved for status)
CHART_PALETTE = [
    "#3462ED",
    "#4748B0",
    "#5B7FFF",
    "#1E3A8A",
    "#7C93ED",
    "#2D3B87",
    "#818CF8",
    "#6366F1",
    "#93A8FF",
    "#4F46E5",
]

# status colors for alerts and thresholds
STATUS_COLORS = {
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "danger": COLORS["danger"],
}

# progress stage colors
PROGRESS_COLORS = {
    "Selecting Student by Company": CHART_PALETTE[4],
    "Study Case": CHART_PALETTE[1],
    "CDC Briefing Student": CHART_PALETTE[6],
    "Interview User": CHART_PALETTE[0],
    "Final Interview": CHART_PALETTE[3],
    "Placement": STATUS_COLORS["success"],
    "FU 1": STATUS_COLORS["warning"],
    "FU 2": STATUS_COLORS["warning"],
    "FU 3": STATUS_COLORS["warning"],
    "Ghosting": STATUS_COLORS["danger"],
    "Rejected": STATUS_COLORS["danger"],
    "Unresolved": COLORS["neutral"],
}

REJECTION_COLORS = {
    "On Progress": CHART_PALETTE[0],
    "Placement": STATUS_COLORS["success"],
    "Rejection Screening CV": STATUS_COLORS["danger"],
    "Rejection Interview User": STATUS_COLORS["danger"],
    "Rejection Study Case": STATUS_COLORS["danger"],
    "Rejection Final Interview": STATUS_COLORS["danger"],
    "Ghosting": COLORS["neutral"],
}

JENIS_PENEMPATAN_COLORS = {
    "Magang": CHART_PALETTE[0],
    "Part-time": CHART_PALETTE[1],
    "Full-time": CHART_PALETTE[2],
}

ELIGIBLE_COLORS = {
    "Available": CHART_PALETTE[0],
    "Placed": CHART_PALETTE[1],
    "Tidak Aktif": COLORS["neutral"],
}

# pipeline stage colors for tracking_company progress
PIPELINE_COLORS = {
    "Draft": CHART_PALETTE[4],
    "Submitted": CHART_PALETTE[6],
    "On Review": CHART_PALETTE[0],
    "Shortlisted": CHART_PALETTE[3],
    "Closed": COLORS["neutral"],
}

# staleness status colors for data synchronization (bt-08)
STALENESS_COLORS = {
    "Safe": CHART_PALETTE[0],
    "Stale": CHART_PALETTE[1],
    "Critical": CHART_PALETTE[2],
}


def _is_dark_mode() -> bool:
    # check whether the app is currently in dark mode
    return st.session_state.get("theme_mode", "light") == "dark"


def get_font_color() -> str:
    # return appropriate text color for the active theme mode
    return "#F1F5F9" if _is_dark_mode() else "#1E293B"


def get_bg_transparent() -> str:
    # return transparent background string for plotly charts
    return "rgba(0,0,0,0)"


# plotly layout base - paper/plot bg transparent so charts follow container
PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=12),
    margin=dict(t=40, b=40, l=40, r=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    hoverlabel=dict(
        bgcolor=COLORS["navy"],
        font_color="#FFFFFF",
        font_size=13,
        font_family="Inter, sans-serif",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=12),
    ),
)


def apply_plotly_style(fig):
    # apply consistent plotly styling with theme-aware font color
    font_color = get_font_color()

    layout_updates = {
        **PLOTLY_LAYOUT,
        "template": "plotly_white",
        "font": dict(family="Inter, sans-serif", size=12, color=font_color),
        "legend": dict(
            font=dict(color=font_color),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    }

    # only update title font if a non-empty title text is already present on the figure
    if fig.layout.title and fig.layout.title.text:
        layout_updates["title"] = dict(
            text=fig.layout.title.text,
            font=dict(family="Montserrat, sans-serif", size=16, color=font_color),
        )

    fig.update_layout(**layout_updates)

    fig.update_xaxes(
        color=font_color,
        title_font=dict(color=font_color),
        tickfont=dict(color=font_color),
        gridcolor="rgba(128,128,128,0.15)",
        zerolinecolor="rgba(128,128,128,0.2)",
    )
    fig.update_yaxes(
        color=font_color,
        title_font=dict(color=font_color),
        tickfont=dict(color=font_color),
        gridcolor="rgba(128,128,128,0.15)",
        zerolinecolor="rgba(128,128,128,0.2)",
    )

    for trace in fig.data:
        if hasattr(trace, "textfont"):
            trace.update(textfont=dict(color=font_color))
        if trace.type == "sankey":
            if hasattr(trace, "node") and isinstance(trace.node, dict):
                trace.node["font"] = dict(color=font_color, family="Inter, sans-serif", size=12)
        elif trace.type not in ("pie", "sunburst", "funnel", "waterfall", "sankey", "treemap"):
            trace.update(cliponaxis=False)

    return fig