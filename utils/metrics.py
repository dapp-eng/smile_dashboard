# metrics - business logic for all bt computations

import pandas as pd


def normalize_finish_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reclassify 'Finish' in progress_student using the rejection column.

    The raw data uses 'Finish' as a catch-all close-out status regardless of
    the actual outcome. The rejection column holds the real outcome, so we
    use it to remap:
        Finish + Placement          → Placement
        Finish + Ghosting           → Ghosting
        Finish + Rejection *        → Rejected
        Finish + On Progress / else → Unresolved

    The original value is preserved in '_original_progress' so the
    data-quality page can still surface these records.
    """
    df = df.copy()
    df["_original_progress"] = df["progress_student"]

    mask = df["progress_student"] == "Finish"
    df.loc[mask & (df["rejection"] == "Placement"), "progress_student"] = "Placement"
    df.loc[mask & (df["rejection"] == "Ghosting"), "progress_student"] = "Ghosting"
    df.loc[mask & df["rejection"].str.contains("Reject", na=False), "progress_student"] = "Rejected"
    # Remaining Finish rows (typically rejection == "On Progress")
    df.loc[df["progress_student"] == "Finish", "progress_student"] = "Unresolved"

    return df


def _resolve_col(df: pd.DataFrame, *candidates: str) -> str:
    # return the first candidate column that exists in df (case-insensitive)
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in df.columns:
            return cand
        if cand.lower() in lower:
            return lower[cand.lower()]
    raise KeyError(f"none of {candidates} found in columns {list(df.columns)}")


def get_eligible_students(student_all: pd.DataFrame, status_student: pd.DataFrame) -> pd.DataFrame:
    # bt-06 (legacy/simple): eligible students = status is active
    df = student_all.merge(status_student, on="NIM", how="inner", suffixes=("", "_status"))
    df = df[df["status"] == "Active"]
    keep = [
        "NIM", "nama", "program_studi", "semester",
        "ipk", "status", "domisili", "ketersediaan", "tools",
    ]
    return df[[c for c in keep if c in df.columns]]


def get_student_eligibility(
    student_all: pd.DataFrame,
    status_student: pd.DataFrame,
    *,
    ipk_min: float = 3.0,
    require_cv: bool = True,
    require_portfolio: bool = True,
    require_active: bool = True,
    require_available: bool = True,
) -> pd.DataFrame:
    # bt-06: determine which students are fit to send to companies
    df = student_all.merge(
        status_student, on="NIM", how="inner", suffixes=("", "_status")
    )

    # fill missing indicator values
    df["CV"] = df["CV"].fillna("tidak ada").astype(str).str.strip().str.lower()
    df["portofolio"] = df["portofolio"].fillna("tidak ada").astype(str).str.strip().str.lower()
    df["status"] = df["status"].fillna("Inactive").astype(str).str.strip()
    df["ketersediaan"] = df["ketersediaan"].fillna("Tidak Aktif").astype(str).str.strip()
    df["IPK"] = pd.to_numeric(df["IPK"], errors="coerce").fillna(0.0)

    # evaluate boolean eligibility checks
    cond_ipk = df["IPK"] >= ipk_min
    cond_cv = df["CV"] == "ada" if require_cv else True
    cond_port = df["portofolio"] == "ada" if require_portfolio else True
    cond_active = df["status"].str.lower() == "active" if require_active else True
    cond_avail = df["ketersediaan"].str.lower() == "available" if require_available else True

    df["is_eligible"] = cond_ipk & cond_cv & cond_port & cond_active & cond_avail

    # generate human-readable ineligibility reasons
    reasons = []
    for _, row in df.iterrows():
        r = []
        if not (row["IPK"] >= ipk_min):
            r.append(f"IPK < {ipk_min:.2f} ({row['IPK']:.2f})")
        if require_cv and row["CV"] != "ada":
            r.append("CV belum ada")
        if require_portfolio and row["portofolio"] != "ada":
            r.append("Portofolio belum ada")
        if require_active and row["status"].lower() != "active":
            r.append(f"Status '{row['status']}'")
        if require_available and row["ketersediaan"].lower() != "available":
            r.append(f"Ketersediaan '{row['ketersediaan']}'")
        reasons.append(", ".join(r) if r else "Eligible")

    df["ineligible_reasons"] = reasons
    return df


def get_student_supply_summary(
    student_all: pd.DataFrame, status_student: pd.DataFrame
) -> dict:
    # page-level snapshot for monitor student kpi hero row
    prodi = _resolve_col(student_all, "program_studi")
    total = int(student_all[_resolve_col(student_all, "NIM")].nunique())
    n_prodi = int(student_all[prodi].dropna().nunique())

    def _count_ketersediaan(value: str) -> int:
        try:
            col = _resolve_col(status_student, "ketersediaan")
        except KeyError:
            return 0
        return int(
            (status_student[col].astype(str).str.strip().str.lower() == value).sum()
        )

    available = _count_ketersediaan("available")
    placed = _count_ketersediaan("placed")

    try:
        ipk_col = _resolve_col(status_student, "IPK", "ipk")
        avg_ipk = pd.to_numeric(status_student[ipk_col], errors="coerce").mean()
        avg_ipk = None if pd.isna(avg_ipk) else round(float(avg_ipk), 2)
    except KeyError:
        avg_ipk = None

    return {
        "total": total,
        "available": available,
        "placed": placed,
        "n_prodi": n_prodi,
        "avg_ipk": avg_ipk,
    }


def match_students_to_request(
    eligible: pd.DataFrame,
    request: pd.Series,
    *,
    w_bidang: int = 45,
    w_semester: int = 30,
    w_tools: int = 25,
) -> pd.DataFrame:
    # bt-01: rank eligible students against one talent request
    df = eligible.copy()
    if df.empty:
        df["match_score"] = []
        return df

    def _get(field, default=""):
        val = request.get(field, default) if hasattr(request, "get") else default
        return "" if pd.isna(val) else val

    bidang_req = str(_get("bidang_studi_dibutuhkan")).lower()
    min_sem = pd.to_numeric(pd.Series([_get("minimum_semester", 0)]), errors="coerce").iloc[0]
    min_sem = 0 if pd.isna(min_sem) else min_sem
    requirement_txt = str(_get("deskripsi_requirement")).lower()

    def _bidang_score(prodi):
        prodi = str(prodi).strip().lower()
        if not prodi or not bidang_req:
            return 0.0
        return 1.0 if (prodi in bidang_req or bidang_req in prodi) else 0.0

    def _tools_score(tools):
        toks = [t.strip().lower() for t in str(tools).split(",") if t.strip()]
        if not toks:
            return 0.0
        hits = sum(1 for t in toks if t in requirement_txt)
        return hits / len(toks)

    sem_num = pd.to_numeric(df["semester"], errors="coerce").fillna(0)
    df["match_bidang"] = df["program_studi"].map(_bidang_score)
    df["match_semester"] = (sem_num >= min_sem).astype(float)
    df["match_tools"] = df["tools"].map(_tools_score) if "tools" in df.columns else 0.0

    df["match_score"] = (
        df["match_bidang"] * w_bidang
        + df["match_semester"] * w_semester
        + df["match_tools"] * w_tools
    ).round(1)

    return df.sort_values("match_score", ascending=False).reset_index(drop=True)


def get_tracking_company_summary(
    tracking_company: pd.DataFrame, tracking_student: pd.DataFrame
) -> pd.DataFrame:
    # bt-04: compare requested, sent, accepted, and rates per tracking_company
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


def get_ghosting_flags(
    tracking_student: pd.DataFrame,
    tracking_company: pd.DataFrame = None,
    today: pd.Timestamp = None,
    include_healthy: bool = False,
) -> pd.DataFrame:
    # bt-05: flag candidates by ghosting severity based on days since send_date
    if today is None:
        today = pd.Timestamp.today().normalize()

    if tracking_company is not None:
        df = tracking_student.merge(
            tracking_company[["id_tracking_company", "send_date"]],
            on="id_tracking_company", how="left",
        )
    else:
        df = tracking_student.copy()

    df["send_date"] = pd.to_datetime(df["send_date"], errors="coerce")
    df["days_since_update"] = (today - df["send_date"]).dt.days

    finished_statuses = ["Placement", "Rejected", "Unresolved"]
    df = df[~df["progress_student"].isin(finished_statuses)]

    def ghosting_check(row):
        if row["progress_student"] in ["FU 1", "FU 2", "FU 3", "Ghosting"]:
            return row["progress_student"]
        elif row["progress_student"] == "Selecting Student by Company":
            if row["days_since_update"] > 28:
                return "overdue_unlabeled_ghosting"
            elif row["days_since_update"] > 21:
                return "overdue_unlabeled_fu3"
            elif row["days_since_update"] > 14:
                return "overdue_unlabeled_fu2"
            elif row["days_since_update"] > 7:
                return "overdue_unlabeled_fu1"
        return "Healthy"

    df["ghosting_check"] = df.apply(ghosting_check, axis=1)

    if not include_healthy:
        return df[df["ghosting_check"] != "Healthy"]

    return df


def get_quality_master_data(
    student_all: pd.DataFrame,
    status_student: pd.DataFrame,
    reference_date: pd.Timestamp = None,
) -> pd.DataFrame:
    # bt-08: combines staleness and data consistency checks into one master table
    df = student_all.merge(
        status_student, on="NIM", suffixes=("_all", "_status"), how="inner"
    )

    # staleness calculation
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

    # discrepancy checks with phone normalization
    def norm_phone_all(p):
        p = str(p).strip()
        if p.endswith(".0"):
            p = p[:-2]
        if p.startswith("0"):
            return p[1:]
        return p

    def norm_phone_status(p):
        p = str(p).strip()
        if p.endswith(".0"):
            p = p[:-2]
        if p.startswith("62"):
            return p[2:]
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
