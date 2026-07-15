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

def get_sync_mismatch():
    student_all = load_csv_table("student_all")
    status_student = load_csv_table("status_student")
    return metrics.get_sync_mismatch(student_all, status_student)


def get_orphaned_tracking():
    tracking_student = load_csv_table("tracking_student")
    student_all = load_csv_table("student_all")
    return metrics.get_orphaned_tracking(tracking_student, student_all)


def get_denorm_inconsistencies():
    tracking_student = load_csv_table("tracking_student")
    student_all = load_csv_table("student_all")
    tracking_company = load_csv_table("tracking_company")
    company = load_csv_table("company")
    talent_request = load_csv_table("talent_request")
    return metrics.get_denorm_inconsistencies(
        tracking_student, student_all, tracking_company, company, talent_request
    )


def get_all_table_counts():
    """Row counts for every CSV table — used by data quality overview."""
    tables = ["student_all", "status_student", "tracking_student",
              "tracking_company", "company", "talent_request"]
    return {t: len(load_csv_table(t)) for t in tables}