# design tokens - colors match [theme] in .streamlit/config.toml

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

# sequential blue-derived palette - red/green/yellow reserved for status only
CHART_PALETTE = [
    "#3462ED",  # primary blue
    "#4748B0",  # purple
    "#5B7FFF",  # soft blue
    "#1E3A8A",  # dark blue
    "#7C93ED",  # periwinkle
    "#2D3B87",  # deep navy
    "#818CF8",  # lavender
    "#6366F1",  # indigo
    "#93A8FF",  # light periwinkle
    "#4F46E5",  # violet
]

# status colors - alerts and thresholds only
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
    "Finish": COLORS["neutral"],
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

# pipeline stage colors for tracking_company
PIPELINE_COLORS = {
    "Draft": CHART_PALETTE[4],
    "Submitted": CHART_PALETTE[6],
    "On Review": CHART_PALETTE[0],
    "Shortlisted": CHART_PALETTE[3],
    "Closed": COLORS["neutral"],
}

# plotly layout base - do not set paper_bgcolor/plot_bgcolor/font.color here
# streamlit theme handles those for light/dark mode compat
PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=12),
    margin=dict(t=40, b=40, l=40, r=20),
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
    fig.update_layout(**PLOTLY_LAYOUT)
    # cliponaxis only for cartesian traces - invalid on pie/donut
    for trace in fig.data:
        if trace.type not in ("pie", "sunburst", "funnel", "waterfall"):
            trace.update(cliponaxis=False)
    return fig


def apply_style():
    # backward compat
    from utils.layout import inject_global_css
    inject_global_css()