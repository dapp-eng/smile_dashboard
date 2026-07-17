from utils.data_loader import load_csv_table
from utils.supabase_client import load_supabase_table
from utils import metrics


def get_eligible_students():
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_eligible_students(student_all, status_student)


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