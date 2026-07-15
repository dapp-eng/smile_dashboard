import pandas as pd


def get_eligible_students(student_all: pd.DataFrame, status_student: pd.DataFrame) -> pd.DataFrame:
    """
    BT-06: Eligible students = status is Active.
    Joins student_all with status_student on nim.
    """
    df = student_all.merge(status_student, on="nim", how="inner", suffixes=("", "_status"))
    df = df[df["status"] == "Active"]
    return df[[
        "nim", "nama", "program_studi", "semester",
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