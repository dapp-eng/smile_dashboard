import streamlit as st
import os

icon_path = os.path.join("assets", "smile-b2.png")
page_icon = icon_path if os.path.exists(icon_path) else None

st.set_page_config(
    page_title="SMILE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=page_icon,
)

from utils.layout import inject_global_css, page_header, render_sidebar_footer
from utils.theme import COLORS

# Inject global CSS once
inject_global_css()


# overview page
def overview_page():
    page_header(
        "Overview",
        "Page ini masih dalam tahap pengembangan"
    )

    st.markdown("""
Gunakan sidebar untuk navigasi:
- **Monitor Student** - eligibility & talent matching (BT-01, BT-06)
- **Monitor Company** - talent request management (BT-03)
- **Monitor Process** - selection progress & ghosting detection (BT-02, BT-05)
- **Reporting** - success rate & periodic recap (BT-04, BT-07)
- **Data Quality** - data sync anomaly checks (BT-08)
""")


# w3 = wide logo for expanded sidebar, w2 = icon for collapsed
logo_path = os.path.join("assets", "smile-w3.png")
icon_path = os.path.join("assets", "smile-w2.png")
if os.path.exists(logo_path) and os.path.exists(icon_path):
    st.logo(logo_path, size="large", icon_image=icon_path)

# navigation
pg = st.navigation([
    st.Page(overview_page, title="Overview", icon=":material/dashboard:", default=True),
    st.Page("pages/1_monitor_student.py", title="Monitor Student", icon=":material/school:"),
    st.Page("pages/2_monitor_company.py", title="Monitor Company", icon=":material/business:"),
    st.Page("pages/3_monitor_process.py", title="Monitor Process", icon=":material/sync:"),
    st.Page("pages/4_reporting.py", title="Reporting", icon=":material/assessment:"),
    st.Page("pages/5_data_quality.py", title="Data Synchronization", icon=":material/verified:"),
])

render_sidebar_footer()
pg.run()
