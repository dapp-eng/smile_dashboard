import streamlit as st

from utils.theme import apply_style, JENIS_PENEMPATAN_COLORS
from utils.data_loader import load_csv_table


st.set_page_config(page_title="Monitor Company", layout="wide")
apply_style()

st.title("Monitor Company")
st.caption("Talent Request Management — BT-03 — Owner: Person A")


df_company = load_csv_table("company")
df_tracking = load_csv_table("tracking_company")

# TODO(Person A): request prioritization by request_date / headcount / jenis_penempatan
# TODO(Person A): company profile view (industry_sector, skala_perusahaan, kota)
