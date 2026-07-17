# uses supabase - only page with live CRUD

import streamlit as st
from utils.layout import inject_global_css, page_header
from utils.data_loader import load_supabase_table, insert_row, update_row, delete_row

inject_global_css()

page_header(
    "Monitor Student",
    "Eligibility & talent matching",
)

df_students = load_supabase_table("student_all")

# guard column casing - supabase returns lowercase
nim_col = "NIM" if "NIM" in df_students.columns else "nim"

st.dataframe(df_students, use_container_width=True, hide_index=True)

if "eligible" in df_students.columns:
    selected_nim = st.selectbox("Select a student by NIM", df_students[nim_col])
    new_status = st.selectbox(
        "Set new eligibility status",
        options=["eligible", "ineligible"],
        index=0 if df_students.loc[df_students[nim_col] == selected_nim, "eligible"].values[0] else 1,
        format_func=lambda x: "Eligible" if x == "eligible" else "Ineligible",
    )

    if st.button("Save changes"):
        update_row("status_student", "NIM", selected_nim, {"eligible": new_status})
        st.rerun()
else:
    st.info("Fitur eligibility management sedang dalam pengembangan.")

# TODO: eligibility filters (CV, portofolio, IPK, status, ketersediaan)
# TODO: matching logic - filter students by talent_request requirements
