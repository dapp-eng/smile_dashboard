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
#  BT-08: Data Quality Master Table
# ─────────────────────────────────────────────

def get_quality_master_data(student_all: pd.DataFrame, status_student: pd.DataFrame, reference_date: pd.Timestamp = None) -> pd.DataFrame:
    """
    BT-08: Combines staleness and data consistency checks into one master table.
    - Staleness categories: Safe (<=90), Stale (91-180), Critical (>180)
    - Consistency checks: nama, email, semester, and hp vs no_whatsapp
    """
    # 1. Merge the tables
    df = student_all.merge(status_student, on="NIM", suffixes=("_all", "_status"), how="inner")
    
    # 2. Staleness Calculation
    df["sync_date"] = pd.to_datetime(df["sync_date"], dayfirst=True)
    if reference_date is None:
        reference_date = df["sync_date"].max()
    df["days_since_sync"] = (reference_date - df["sync_date"]).dt.days
    
    def classify_staleness(days):
        if days > 179:
            return "Critical"
        elif days > 89:
            return "Stale"
        return "Safe"
        
    df["staleness"] = df["days_since_sync"].apply(classify_staleness)

    # 3. Discrepancy Checks
    def norm_phone_all(p):
        p = str(p).strip()
        if p.endswith(".0"): p = p[:-2]
        if p.startswith("0"): return p[1:]
        return p

    def norm_phone_status(p):
        p = str(p).strip()
        if p.endswith(".0"): p = p[:-2]
        if p.startswith("62"): return p[2:]
        return p
        
    hp_norm = df["hp"].apply(norm_phone_all)
    wa_norm = df["no_whatsapp"].apply(norm_phone_status)
    
    email_all = df["email_kampus"].astype(str).str.lower().str.strip()
    email_status = df["email"].astype(str).str.lower().str.strip()
    
    nama_all = df["nama_all"].astype(str).str.lower().str.strip()
    nama_status = df["nama_status"].astype(str).str.lower().str.strip()
    
    sem_all = pd.to_numeric(df["semester_all"], errors="coerce")
    sem_status = pd.to_numeric(df["semester_status"], errors="coerce")
    
    prog_all = df["program_studi_all"].astype(str).str.lower().str.strip()
    prog_status = df["program_studi_status"].astype(str).str.lower().str.strip()
    
    diff_nama = nama_all != nama_status
    diff_email = email_all != email_status
    diff_semester = sem_all != sem_status
    diff_phone = hp_norm != wa_norm
    diff_prog = prog_all != prog_status
    
    df["has_mismatch"] = diff_nama | diff_email | diff_semester | diff_phone | diff_prog
    
    df["mismatch_types"] = ""
    df.loc[diff_nama, "mismatch_types"] += "Name, "
    df.loc[diff_email, "mismatch_types"] += "Email, "
    df.loc[diff_semester, "mismatch_types"] += "Semester, "
    df.loc[diff_phone, "mismatch_types"] += "Phone, "
    df.loc[diff_prog, "mismatch_types"] += "ProgStudi, "
    df["mismatch_types"] = df["mismatch_types"].str.rstrip(", ")
    
    return df
