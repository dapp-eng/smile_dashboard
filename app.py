import streamlit as st

from utils.theme import apply_style

st.set_page_config(page_title="SSDC Dashboard", layout="wide", page_icon="📊")
apply_style()

st.title("Student Placement System — Overview")
st.caption("CDC Talent Placement Dashboard | SSDC 2026")

st.markdown(
    """
Use the sidebar to navigate:
- **Monitor Student** — eligibility & talent matching (BT-01, BT-06)
- **Monitor Company** — talent request management (BT-03)
- **Monitor Process** — selection progress & ghosting detection (BT-02, BT-05)
- **Reporting** — success rate & periodic recap (BT-04, BT-07)
- **Data Quality** — data sync anomaly checks (BT-08)
"""
)

# TODO(Person A): build this LAST, once the other pages' numbers are stable.
# Pull top-line KPIs here, e.g.:
#   - total active students / eligible students
#   - open talent requests
#   - placement rate this semester
#   - companies with pending requests
