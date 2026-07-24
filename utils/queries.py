# query layer - bridges data_loader/supabase with metrics

from utils.data_loader import load_csv_table
from utils.supabase_client import load_supabase_table
from utils import metrics


def get_eligible_students():
    # bt-06 (legacy): returns active students only
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_eligible_students(student_all, status_student)


def get_student_eligibility(**criteria):
    # bt-06: full-rule eligibility over the csv layer
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_student_eligibility(student_all, status_student, **criteria)


def get_student_supply_summary():
    # page-level kpis for monitor student hero row (filter-independent)
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_student_supply_summary(student_all, status_student)


def get_student_profiling_data():
    # returns a merged dataframe of student_all and status_student for demographic/skill profiling
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    import pandas as pd
    
    # Keep only relevant columns to avoid memory bloat
    s_all = student_all[["NIM", "bidang_minat", "jenis_penempatan_diminati"]].copy()
    s_status = status_student[["NIM", "semester", "program_studi", "IPK", "domisili", "tools"]].copy()
    
    # Convert NIM to string to ensure safe merge
    s_all["NIM"] = s_all["NIM"].astype(str)
    s_status["NIM"] = s_status["NIM"].astype(str)
    
    df = pd.merge(s_all, s_status, on="NIM", how="inner")
    
    # Ensure numeric columns are actually numeric
    df["IPK"] = pd.to_numeric(df["IPK"], errors="coerce")
    df["semester"] = pd.to_numeric(df["semester"], errors="coerce")
    
    return df


def get_talent_requests():
    # read-only talent requests from the csv layer (matching source for bt-01)
    return load_csv_table("talent_request")


def get_program_studi_options():
    # sorted unique program_studi from student_all for filter widgets
    df = load_csv_table("student_all")
    return sorted(df["program_studi"].dropna().astype(str).unique().tolist())


def get_tracking_company_summary():
    # bt-04: tracking company with acceptance and fulfillment rates
    tracking_company = load_csv_table("tracking_company")
    tracking_student = load_csv_table("tracking_student")
    return metrics.get_tracking_company_summary(tracking_company, tracking_student)


def get_ghosting_flags():
    # bt-05: ghosting detection on active candidates
    tracking_student = load_csv_table("tracking_student")
    return metrics.get_ghosting_flags(tracking_student)


def get_talent_requests_live():
    # for crud pages - pulls live from supabase, not csv
    return load_supabase_table("talent_request")


def get_data_quality_master():
    # bt-08: staleness and consistency checks master table
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_quality_master_data(student_all, status_student)


def get_all_table_counts():
    # row counts for every csv table - used by data quality overview
    tables = [
        "student_all", "status_student", "tracking_student",
        "tracking_company", "company", "talent_request",
    ]
    return {t: len(load_csv_table(t)) for t in tables}


def get_company_monitoring_data():
    # loads all tables needed for the company monitoring page
    return {
        "company": load_csv_table("company"),
        "tracking_company": load_csv_table("tracking_company"),
        "talent_request": load_csv_table("talent_request"),
        "tracking_student": load_csv_table("tracking_student"),
        "student_all": load_csv_table("student_all"),
    }