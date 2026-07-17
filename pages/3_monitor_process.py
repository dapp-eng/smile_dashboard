import streamlit as st
from utils.layout import inject_global_css, page_header

inject_global_css()
page_header(
    "Monitor Process",
    "Proses seleksi dan deteksi ghosting"
)

st.info("Halaman ini sedang dalam pengembangan.")
