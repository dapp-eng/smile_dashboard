import streamlit as st
from utils.layout import inject_global_css, page_header

inject_global_css()
page_header(
    "Reporting",
    "Laporan tingkat keberhasilan dan rekap periodik"
)

st.info("Halaman ini sedang dalam pengembangan.")
