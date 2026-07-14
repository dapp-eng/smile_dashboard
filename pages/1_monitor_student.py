"""
The only page that utilizes the Supabase Database
"""

import streamlit as st
from utils.theme import apply_style, ELIGIBLE_COLORS
from utils.data_loader import load_supabase_table, insert_row, update_row, delete_row

st.title("Monitor Student")
st.caption("Eligibility & Talent Matching — BT-01, BT-06 — Owner: Person B")

df_students = load_supabase_table("student_all")
st.dataframe(df_students)

# Contoh Use Case
selected_nim = st.selectbox("Select a student by NIM", df_students["NIM"])
new_status = st.selectbox(
    "Set new eligibility status",
    options=["eligible", "ineligible"],
    index=0 if df_students.loc[df_students["NIM"] == selected_nim, "eligible"].values[0] else 1,
    format_func=lambda x: "Eligible" if x == "eligible" else "Ineligible")

if st.button("Save changes"):
    update_row("status_student", "NIM", selected_nim, {"eligible": new_status})
    st.rerun()
st.set_page_config(page_title="Monitor Student", layout="wide")
apply_style()


# TODO(Person B): eligibility filters (CV, portofolio, IPK, status, ketersediaan)
# TODO(Person B): matching logic — filter students against a selected
#                 TALENT_REQUEST's bidang_studi_dibutuhkan / minimum_semester / tools
