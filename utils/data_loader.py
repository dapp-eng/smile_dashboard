import streamlit as st
import pandas as pd
import gdown
import os
import shutil
from supabase import create_client, Client

DATA_DIR = "data"


@st.cache_resource
def download_csvs():
    has_csvs = (
        os.path.exists(DATA_DIR)
        and any(f.endswith(".csv") for f in os.listdir(DATA_DIR))
    )
    if not has_csvs:
        gdown.download_folder(
            id=st.secrets["gdrive_file_id"],
            output=DATA_DIR,
            quiet=False,
            use_cookies=False,
        )
        for entry in os.listdir(DATA_DIR):
            sub = os.path.join(DATA_DIR, entry)
            if os.path.isdir(sub):
                for f in os.listdir(sub):
                    shutil.move(os.path.join(sub, f), os.path.join(DATA_DIR, f))
                os.rmdir(sub)
    return DATA_DIR


@st.cache_data
def load_csv_table(table_name: str) -> pd.DataFrame:
    csv_dir = download_csvs()
    path = os.path.join(csv_dir, f"{table_name}.csv")
    # sniff delimiter - status_student uses ';', others use ','
    with open(path, "r", encoding="utf-8-sig") as f:
        sample = f.read(2048)
    import csv
    dialect = csv.Sniffer().sniff(sample)
    return pd.read_csv(path, sep=dialect.delimiter, encoding="utf-8-sig")


# supabase - live, powers CRUD
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