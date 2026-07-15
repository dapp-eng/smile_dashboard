def validate_talent_request(data: dict) -> list[str]:
    errors = []
    if not data.get("nama_posisi"):
        errors.append("Posisi wajib diisi.")
    if not data.get("headcount") or data["headcount"] <= 0:
        errors.append("Headcount harus lebih dari 0.")
    return errors

def nim_exists(nim: str, student_all_df) -> bool:
    return nim in student_all_df["nim"].values