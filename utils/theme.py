"""
Shared design tokens for the SSDC dashboard.

Base colors here MUST match [theme] in .streamlit/config.toml.
config.toml handles native Streamlit widget theming automatically;
this file exists only for Plotly category-color mapping, which
config.toml has no mechanism for (it can't map specific string
values like "Ghosting" to specific colors).
"""

import streamlit as st

# Mirrors .streamlit/config.toml [theme] and chartCategoricalColors.
# If you change a color here, change it in config.toml too.
COLORS = {
    "primary": "#3462ED",     # theme.primaryColor
    "secondary": "#4748B0",   # ungu
    "success": "#10B981",     # hijau
    "danger": "#EF4444",      # merah
    "neutral": "#6e7781",     # not in config.toml — kept for muted/inactive states
    "warning": "#d4a72c",     # not in config.toml — kept for FU1-3 states
}

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
    """
    Call once per page for the few things config.toml can't set:
    hiding default chrome, and letting stMetric use theme-aware colors
    instead of Streamlit's flat default (rather than hardcoding white,
    which breaks in [theme.dark]).
    """
    st.markdown(
        """
        <style>
        #MainMenu, footer {visibility: hidden;}
        div[data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border-radius: 12px;
            padding: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )