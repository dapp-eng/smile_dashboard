import streamlit as st
import pandas as pd
import gdown
import os
from supabase import create_client, Client

# Layer 1: Local CSV (read-only, powers dashboard/charts)

DATA_DIR = "data"

@st.cache_resource
def download_csvs():
    if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
        gdown.download_folder(
            id=st.secrets["gdrive_folder_id"],
            output=DATA_DIR,
            quiet=False,
            use_cookies=False,
        )
    return DATA_DIR

@st.cache_data
def load_csv_table(table_name: str) -> pd.DataFrame:
    download_csvs()  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")
    return pd.read_csv(path)


# Layer 2: Supabase (live, mutable, powers CRUD)
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])

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