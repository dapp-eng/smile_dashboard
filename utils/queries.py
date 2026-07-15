from utils.data_loader import load_csv_table
from utils.supabase_client import load_supabase_table

def get_eligible_students():
    return load_csv_table("eligible_students") 

def get_tracking_company_summary():
    return load_csv_table("tracking_company_summary")

def get_ghosting_flags():
    return load_csv_table("ghosting_flags")

def get_talent_requests_for_crud():
    return load_supabase_table("talent_request")  