import pandas as pd


def get_eligible_students(student_all: pd.DataFrame, status_student: pd.DataFrame) -> pd.DataFrame:
    """
    BT-06: Eligible students = status is Active.
    Joins student_all with status_student on NIM.
    """
    df = student_all.merge(status_student, on="NIM", how="inner", suffixes=("", "_status"))
    df = df[df["status"] == "Active"]
    return df[[
        "NIM", "nama", "program_studi", "semester",
        "ipk", "status", "domisili", "ketersediaan", "tools"
    ]]


def get_tracking_company_summary(tracking_company: pd.DataFrame, tracking_student: pd.DataFrame) -> pd.DataFrame:
    """
    BT-04: Compare jumlah_permintaan, jumlah_dikirim, accepted, acceptance_rate, fulfillment_rate.
    """
    accepted_counts = (
        tracking_student[tracking_student["progress_student"] == "Placement"]
        .groupby("id_tracking_company")
        .size()
        .reset_index(name="accepted")
    )

    df = tracking_company.merge(accepted_counts, on="id_tracking_company", how="left")
    df["accepted"] = df["accepted"].fillna(0).astype(int)

    df["acceptance_rate"] = (
        df["accepted"] / df["jumlah_dikirim"].replace(0, pd.NA) * 100
    ).round(1)

    df["fulfillment_rate"] = (
        df[["accepted", "jumlah_permintaan"]].min(axis=1)
        / df["jumlah_permintaan"].replace(0, pd.NA) * 100
    ).round(1)

    return df


def get_ghosting_flags(tracking_student: pd.DataFrame, today: pd.Timestamp = None) -> pd.DataFrame:
    """
    BT-05: Flag ghosting cases, both explicitly labeled (FU 1/2/3, Ghosting)
    and overdue-but-unlabeled cases based on last_update.
    """
    if today is None:
        today = pd.Timestamp.today().normalize()

    df = tracking_student.copy()
    df["last_update"] = pd.to_datetime(df["last_update"])
    df["days_since_update"] = (today - df["last_update"]).dt.days

    finished_statuses = ["Placement", "Rejected", "Finish"]
    df = df[~df["progress_student"].isin(finished_statuses)]

    def ghosting_check(row):
        if row["progress_student"] in ["FU 1", "FU 2", "FU 3", "Ghosting"]:
            return "labeled"
        elif row["days_since_update"] > 28:
            return "overdue_unlabeled_ghosting"
        elif row["days_since_update"] > 21:
            return "overdue_unlabeled_fu3"
        elif row["days_since_update"] > 14:
            return "overdue_unlabeled_fu2"
        elif row["days_since_update"] > 7:
            return "overdue_unlabeled_fu1"
        else:
            return "ok"

    df["ghosting_check"] = df.apply(ghosting_check, axis=1)
    return df[df["ghosting_check"] != "ok"]


# ─────────────────────────────────────────────
#  BT-08: Data Quality / Sync Checks
# ─────────────────────────────────────────────

def get_sync_mismatch(student_all: pd.DataFrame, status_student: pd.DataFrame) -> pd.DataFrame:
    """
    BT-08: Detect mismatches between student_all and status_student.
    Returns rows with mismatch_type: missing_in_status_student,
    missing_in_student_all, or name_mismatch.
    """
    df = student_all[["NIM", "nama"]].merge(
        status_student[["NIM", "nama"]],
        on="NIM",
        how="outer",
        suffixes=("_student_all", "_status_student"),
        indicator=True,
    )

    def classify(row):
        if row["_merge"] == "left_only":
            return "missing_in_status_student"
        elif row["_merge"] == "right_only":
            return "missing_in_student_all"
        elif row["nama_student_all"] != row["nama_status_student"]:
            return "name_mismatch"
        return "ok"

    df["mismatch_type"] = df.apply(classify, axis=1)
    df = df[df["mismatch_type"] != "ok"].drop(columns=["_merge"])
    return df


def get_stale_sync(status_student: pd.DataFrame, reference_date: pd.Timestamp = None) -> pd.DataFrame:
    """
    BT-08: Flag status_student records whose sync_date is significantly old.
    Uses the latest sync_date in the dataset as reference (since this is a
    static CSV snapshot, not a live system).

    Thresholds:
        >90 days  = stale
        >180 days = very_stale
        >365 days = critical
    """
    df = status_student.copy()
    df["sync_date"] = pd.to_datetime(df["sync_date"], dayfirst=True)

    if reference_date is None:
        reference_date = df["sync_date"].max()

    df["days_since_sync"] = (reference_date - df["sync_date"]).dt.days

    def classify(days):
        if days > 365:
            return "critical"
        elif days > 180:
            return "very_stale"
        elif days > 90:
            return "stale"
        return "ok"

    df["staleness"] = df["days_since_sync"].apply(classify)
    return df


def get_orphaned_tracking(
    tracking_student: pd.DataFrame, student_all: pd.DataFrame
) -> pd.DataFrame:
    """
    Detect tracking_student rows whose NIM doesn't exist in student_all.
    These are legacy FK violations from before constraint enforcement.
    """
    valid_NIMs = set(student_all["NIM"])
    df = tracking_student.copy()
    df["is_orphan"] = ~df["NIM"].isin(valid_NIMs)
    return df[df["is_orphan"]].drop(columns=["is_orphan"])


def get_denorm_inconsistencies(
    tracking_student: pd.DataFrame,
    student_all: pd.DataFrame,
    tracking_company: pd.DataFrame,
    company: pd.DataFrame,
    talent_request: pd.DataFrame,
) -> pd.DataFrame:
    """
    Detect denormalization mismatches: duplicated columns reachable via FK
    that disagree with their canonical source.

    Checks:
    1. tracking_student.student_name vs student_all.nama (via NIM)
    2. tracking_company.nama_perusahaan vs company.company_name (via id_company)
    3. tracking_company fields vs talent_request fields (via id_talent_req)
    """
    issues = []

    # Check 1: tracking_student.student_name vs student_all.nama
    ts_sa = tracking_student[["id_tracking_student", "NIM", "student_name"]].merge(
        student_all[["NIM", "nama"]], on="NIM", how="inner"
    )
    mask = ts_sa["student_name"] != ts_sa["nama"]
    for _, row in ts_sa[mask].iterrows():
        issues.append({
            "table": "tracking_student",
            "record_id": row["id_tracking_student"],
            "field": "student_name",
            "actual_value": row["student_name"],
            "expected_value": row["nama"],
            "source_table": "student_all",
        })

    # Check 2: tracking_company.nama_perusahaan vs company.company_name
    tc_co = tracking_company[["id_tracking_company", "id_company", "nama_perusahaan"]].merge(
        company[["id_company", "company_name"]], on="id_company", how="inner"
    )
    mask = tc_co["nama_perusahaan"] != tc_co["company_name"]
    for _, row in tc_co[mask].iterrows():
        issues.append({
            "table": "tracking_company",
            "record_id": row["id_tracking_company"],
            "field": "nama_perusahaan",
            "actual_value": row["nama_perusahaan"],
            "expected_value": row["company_name"],
            "source_table": "company",
        })

    # Check 3: tracking_company vs talent_request shared fields
    shared_fields = [
        ("posisi", "nama_posisi"),
        ("jenis_penempatan", "jenis_penempatan"),
        ("bidang_studi_dicari", "bidang_studi_dibutuhkan"),
    ]
    tr_cols = ["id_talent_req"] + [src for _, src in shared_fields]
    tc_cols = ["id_tracking_company", "id_talent_req"] + [tc for tc, _ in shared_fields]
    tc_tr = tracking_company[tc_cols].merge(
        talent_request[tr_cols], on="id_talent_req", how="inner", suffixes=("_tc", "_tr")
    )
    for tc_field, tr_field in shared_fields:
        col_tc = f"{tc_field}_tc" if tc_field == tr_field else tc_field
        col_tr = f"{tr_field}_tr" if tc_field == tr_field else tr_field
        # Handle suffix naming from merge
        if col_tc not in tc_tr.columns:
            col_tc = tc_field
        if col_tr not in tc_tr.columns:
            col_tr = tr_field
        mask = tc_tr[col_tc].fillna("") != tc_tr[col_tr].fillna("")
        for _, row in tc_tr[mask].iterrows():
            issues.append({
                "table": "tracking_company",
                "record_id": row["id_tracking_company"],
                "field": tc_field,
                "actual_value": row[col_tc],
                "expected_value": row[col_tr],
                "source_table": "talent_request",
            })

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=["table", "record_id", "field", "actual_value", "expected_value", "source_table"]
    )