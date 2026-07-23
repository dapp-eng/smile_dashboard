# supabase client - live database connection for crud operations

import streamlit as st
from supabase import create_client, Client
import pandas as pd


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def load_supabase_table(table_name: str) -> pd.DataFrame:
    client = get_supabase_client()
    response = client.table(table_name).select("*").execute()
    return pd.DataFrame(response.data)


def insert_row(table_name: str, row: dict):
    client = get_supabase_client()
    return client.table(table_name).insert(row).execute()


def update_row(table_name: str, match_column: str, match_value, updates: dict):
    client = get_supabase_client()
    return client.table(table_name).update(updates).eq(match_column, match_value).execute()


def delete_row(table_name: str, match_column: str, match_value):
    client = get_supabase_client()
    return client.table(table_name).delete().eq(match_column, match_value).execute()