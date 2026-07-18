from utils.data_loader import load_csv_table
from utils.supabase_client import load_supabase_table
from utils import metrics


def get_eligible_students():
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_eligible_students(student_all, status_student)


def get_student_eligibility(**criteria):
    """BT-06: full-rule eligibility over the CSV layer. See metrics.get_student_eligibility."""
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_student_eligibility(student_all, status_student, **criteria)


def get_student_supply_summary():
    """Page-level KPIs for Monitor Student's hero row (filter-independent)."""
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_student_supply_summary(student_all, status_student)


def get_talent_requests():
    """Read-only talent requests from the CSV layer (matching source for BT-01)."""
    return load_csv_table("talent_request")


def get_program_studi_options():
    """Sorted unique program_studi from student_all — for filter widgets."""
    df = load_csv_table("student_all")
    return sorted(df["program_studi"].dropna().astype(str).unique().tolist())


def get_tracking_company_summary():
    tracking_company = load_csv_table("tracking_company")
    tracking_student = load_csv_table("tracking_student")
    return metrics.get_tracking_company_summary(tracking_company, tracking_student)


def get_ghosting_flags():
    tracking_student = load_csv_table("tracking_student")
    return metrics.get_ghosting_flags(tracking_student)


def get_talent_requests_live():
    """For CRUD pages — pulls live from Supabase, not CSV."""
    return load_supabase_table("talent_request")


# ─────────────────────────────────────────────
#  BT-08: Data Quality queries
# ─────────────────────────────────────────────

def get_data_quality_master():
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_quality_master_data(student_all, status_student)


def get_all_table_counts():
    """Row counts for every CSV table — used by data quality overview."""
    tables = ["student_all", "status_student", "tracking_student",
              "tracking_company", "company", "talent_request"]
    return {t: len(load_csv_table(t)) for t in tables}


# company monitoring queries
def get_company_monitoring_data():
    return {
        "company": load_csv_table("company"),
        "tracking_company": load_csv_table("tracking_company"),
        "talent_request": load_csv_table("talent_request"),
        "tracking_student": load_csv_table("tracking_student"),
    }