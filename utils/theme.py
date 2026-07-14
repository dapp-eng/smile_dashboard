"""
Shared design tokens for the SSDC dashboard.

RULE: import colors from here in every page. Never hardcode hex values
or redefine palettes locally — that's exactly how three people end up
with three different shades of "green" across tabs.
"""

import streamlit as st

COLORS = {
    "primary": "#0969da",
    "secondary": "#c08a5b",
    "success": "#2da44e",
    "danger": "#cf222e",
    "neutral": "#6e7781",
    "warning": "#d4a72c",
}

# Fixed category -> color mappings.
# Use these with `color_discrete_map` (NOT `color_discrete_sequence`) in
# Plotly/Altair so the same category is always the same color no matter
# which tab it shows up in or what order it appears in someone's dataframe.

PROGRESS_COLORS = {
    "Selecting Student by Company": COLORS["neutral"],
    "Study Case": COLORS["secondary"],
    "CDC Briefing Student": COLORS["secondary"],
    "Interview User": COLORS["primary"],
    "Final Interview": COLORS["primary"],
    "Placement": COLORS["success"],
    "FU 1": COLORS["warning"],
    "FU 2": COLORS["warning"],
    "FU 3": COLORS["warning"],
    "Ghosting": COLORS["danger"],
    "Rejected": COLORS["danger"],
    "Finish": COLORS["neutral"],
}

REJECTION_COLORS = {
    "On Progress": COLORS["primary"],
    "Placement": COLORS["success"],
    "Rejection Screening CV": COLORS["danger"],
    "Rejection Interview User": COLORS["danger"],
    "Rejection Study Case": COLORS["danger"],
    "Rejection Final Interview": COLORS["danger"],
    "Ghosting": COLORS["neutral"],
}

JENIS_PENEMPATAN_COLORS = {
    "Magang": COLORS["primary"],
    "Part-time": COLORS["secondary"],
    "Full-time": COLORS["success"],
}

ELIGIBLE_COLORS = {
    "Available": COLORS["success"],
    "Placed": COLORS["primary"],
    "Tidak Aktif": COLORS["neutral"],
}


def apply_style():
    """Call once at the top of every page for consistent card/layout styling."""
    st.markdown(
        """
        <style>
        #MainMenu, footer {visibility: hidden;}
        div[data-testid="stMetric"] {
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
