# pdf report generator for periodic placement reports (bt-07 dominant)

import io
import os
import re
import tempfile
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from utils.theme import CHART_PALETTE, COLORS, JENIS_PENEMPATAN_COLORS
from utils.i18n import get_lang

# font path resolution for times new roman
_ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
_FONT_DIR = os.path.join(_ASSETS_DIR, "fonts")


# locate the times new roman ttf file on the system or in assets
def _find_tnr_font(style: str = "regular") -> str:
    candidates = {
        "regular": ["times.ttf", "Times New Roman.ttf", "timesnewroman.ttf"],
        "bold": ["timesbd.ttf", "Times New Roman Bold.ttf", "times.ttf"],
        "italic": ["timesi.ttf", "Times New Roman Italic.ttf", "times.ttf"],
    }
    names = candidates.get(style, candidates["regular"])
    search_dirs = [
        _ASSETS_DIR,
        _FONT_DIR,
        r"C:\Windows\Fonts",
        "/usr/share/fonts/truetype/msttcorefonts",
        "/usr/share/fonts/truetype",
    ]
    for directory in search_dirs:
        if not os.path.isdir(directory):
            continue
        for name in names:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


# convert matplotlib figure to high resolution png bytes for pdf embedding
def _plt_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# shared chart style helper
def _style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.tick_params(labelsize=8)


# BT-07 chart: placement per semester
def _build_bt07_by_semester(df_ts, df_status_student):
    student_info = df_status_student[["NIM", "semester"]].drop_duplicates()
    placed = df_ts[df_ts["progress_student"] == "Placement"].copy()
    merged = placed.merge(student_info, on="NIM", how="left")
    merged["semester"] = merged["semester"].astype(str)
    counts = merged["semester"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(7, 2.8), dpi=200)
    bars = ax.bar(counts.index, counts.values, color="#3462ED", width=0.55, edgecolor="white")
    _style_ax(ax)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.grid(axis="x", visible=False)
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
            f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#1E293B"
        )
    ax.set_xlabel("Semester", fontsize=9)
    ax.set_ylabel("Jumlah Placement", fontsize=9)
    plt.tight_layout()
    return fig


# BT-07 chart: placement per program studi
def _build_bt07_by_prodi(df_ts, df_status_student):
    student_info = df_status_student[["NIM", "program_studi"]].drop_duplicates()
    placed = df_ts[df_ts["progress_student"] == "Placement"].copy()
    merged = placed.merge(student_info, on="NIM", how="left")
    counts = merged["program_studi"].value_counts().head(10).sort_values(ascending=True)

    if counts.empty:
        counts = pd.Series({"Data Tidak Tersedia": 0})

    fig, ax = plt.subplots(figsize=(7, 3.2), dpi=200)
    bars = ax.barh(counts.index, counts.values, color="#3462ED", height=0.6, edgecolor="white")
    _style_ax(ax)
    max_val = max(1, counts.max())
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + max(0.1, max_val * 0.02), bar.get_y() + bar.get_height() / 2,
            f"{int(w)}", va="center", ha="left", fontsize=8, fontweight="bold", color="#1E293B"
        )
    ax.set_xlabel("Jumlah Placement", fontsize=9)
    ax.set_xlim(0, max_val * 1.25)
    plt.tight_layout()
    return fig


# BT-07 chart: placement per perusahaan (top 10)
def _build_bt07_by_company(df_ts, top_n=10):
    placed = df_ts[df_ts["progress_student"] == "Placement"].copy()
    if "company" in placed.columns and not placed["company"].dropna().empty:
        counts = placed.groupby("company").size().nlargest(top_n).sort_values(ascending=True)
    else:
        counts = pd.Series({"Data Tidak Tersedia": 0})

    fig, ax = plt.subplots(figsize=(7, 3.2), dpi=200)
    bars = ax.barh(counts.index, counts.values, color="#4748B0", height=0.6, edgecolor="white")
    _style_ax(ax)
    max_val = max(1, counts.max())
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + max(0.1, max_val * 0.02), bar.get_y() + bar.get_height() / 2,
            f"{int(w)}", va="center", ha="left", fontsize=8, fontweight="bold", color="#1E293B"
        )
    ax.set_xlabel("Jumlah Placement", fontsize=9)
    ax.set_xlim(0, max_val * 1.25)
    plt.tight_layout()
    return fig


# BT-07 chart: placement per jenis penempatan
def _build_bt07_by_type(df_tc, df_ts):
    placed = df_ts[df_ts["progress_student"] == "Placement"].copy()
    if "jenis_penempatan" in placed.columns and not placed["jenis_penempatan"].dropna().empty:
        counts = placed["jenis_penempatan"].value_counts()
    elif "id_tracking_company" in placed.columns and "jenis_penempatan" in df_tc.columns:
        merged = placed.merge(df_tc[["id_tracking_company", "jenis_penempatan"]], on="id_tracking_company", how="left")
        counts = merged["jenis_penempatan"].value_counts()
    elif "jenis_penempatan" in df_tc.columns:
        counts = df_tc["jenis_penempatan"].value_counts()
    else:
        counts = pd.Series({"Magang": 1, "Full-time": 1, "Part-time": 1})

    fig, ax = plt.subplots(figsize=(4.5, 2.2), dpi=200)
    color_map = {"Magang": "#3462ED", "Full-time": "#42c1b6", "Part-time": "#5B7FFF"}
    colors = [color_map.get(k, "#3462ED") for k in counts.index]

    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
        colors=colors, wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=9, color="#1E293B")
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_weight("bold")
        at.set_color("#FFFFFF")
    ax.axis("equal")
    plt.tight_layout()
    return fig, counts


# BT-07: rekap table per jenis penempatan
def _build_bt07_rekap_table(df_tc, df_ts, df_status_student):
    placed = df_ts[df_ts["progress_student"] == "Placement"].copy()
    student_info = df_status_student[["NIM", "program_studi", "semester"]].drop_duplicates()
    merged = placed.merge(student_info, on="NIM", how="left")
    if "jenis_penempatan" not in merged.columns:
        tc_info = df_tc[["id_tracking_company", "jenis_penempatan"]].drop_duplicates()
        merged = merged.merge(tc_info, on="id_tracking_company", how="left")
    return merged


# area chart monthly request volume
def _build_monthly_request_trend(df_tc):
    if "request_date" in df_tc.columns and not df_tc.empty:
        df = df_tc.dropna(subset=["request_date"]).copy()
        df["request_date"] = pd.to_datetime(df["request_date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["request_date"])
        if not df.empty:
            monthly = df.groupby(df["request_date"].dt.to_period("M")).size()
            x_labels = [str(period) for period in monthly.index]
            y_values = monthly.values
        else:
            x_labels = [datetime.now().strftime("%Y-%m")]
            y_values = [0]
    else:
        x_labels = [datetime.now().strftime("%Y-%m")]
        y_values = [0]

    fig, ax = plt.subplots(figsize=(7, 2.2), dpi=200)
    ax.plot(x_labels, y_values, marker="o", color="#3462ED", linewidth=2, markersize=4)
    ax.fill_between(x_labels, y_values, color="#3462ED", alpha=0.12)
    _style_ax(ax)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.grid(axis="x", visible=False)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    return fig


# eligibility donut
def _build_eligibility_pie(df_eligibility):
    if "is_eligible" in df_eligibility.columns and not df_eligibility.empty:
        comp = df_eligibility["is_eligible"].map({True: "Eligible", False: "Ineligible"}).value_counts()
    else:
        comp = pd.Series({"Eligible": 0, "Ineligible": 0})

    fig, ax = plt.subplots(figsize=(4.5, 2.2), dpi=200)
    colors = ["#10B981", "#CBD5E1"]
    values = comp.values.tolist()
    if sum(values) == 0:
        values = [1, 0]

    wedges, texts, autotexts = ax.pie(
        values, labels=comp.index.tolist(), autopct="%1.1f%%", startangle=90,
        colors=colors[:len(values)], wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=8, color="#1E293B")
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_weight("bold")
    ax.axis("equal")
    plt.tight_layout()
    return fig


# stage distribution horizontal bar
def _build_stage_distribution(df_track):
    if "progress_student" in df_track.columns and not df_track.empty:
        counts = df_track["progress_student"].value_counts().sort_values(ascending=True)
    else:
        counts = pd.Series({"Placement": 0})

    fig, ax = plt.subplots(figsize=(7, 2.4), dpi=200)
    bars = ax.barh(counts.index, counts.values, color="#3462ED", height=0.6, edgecolor="white")
    _style_ax(ax)
    max_val = max(1, counts.max())
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + max(0.1, max_val * 0.02), bar.get_y() + bar.get_height() / 2,
            f"{int(w)}", va="center", ha="left", fontsize=8, fontweight="bold", color="#1E293B"
        )
    ax.set_xlim(0, max_val * 1.25)
    plt.tight_layout()
    return fig


# ghosting donut
def _build_ghosting_pie(active_count, fu_count, ghost_count):
    healthy = max(0, active_count - fu_count - ghost_count)
    labels = ["Healthy", "FU 1-3", "Ghosting"]
    values = [healthy, fu_count, ghost_count]
    colors = ["#3462ED", "#D4A72C", "#EF4444"]

    if sum(values) == 0:
        values = [1, 0, 0]

    fig, ax = plt.subplots(figsize=(4.5, 2.2), dpi=200)
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%", startangle=90,
        colors=colors, wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=8, color="#1E293B")
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_weight("bold")
    ax.axis("equal")
    plt.tight_layout()
    return fig


# data staleness donut
def _build_staleness_pie(df_master):
    if "staleness" in df_master.columns and not df_master.empty:
        counts = df_master["staleness"].value_counts()
    else:
        counts = pd.Series({"Safe": 1})

    fig, ax = plt.subplots(figsize=(4.5, 2.2), dpi=200)
    staleness_colors = {"Safe": "#3462ED", "Stale": "#D4A72C", "Critical": "#EF4444"}
    colors = [staleness_colors.get(k, "#3462ED") for k in counts.index]

    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
        colors=colors, wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=8, color="#1E293B")
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_weight("bold")
    ax.axis("equal")
    plt.tight_layout()
    return fig


# generate a comprehensive periodic report pdf with BT-07 as dominant section
def generate_report_pdf(
    df_student_eligibility: pd.DataFrame,
    df_company: pd.DataFrame,
    df_tc: pd.DataFrame,
    df_tr: pd.DataFrame,
    df_ts: pd.DataFrame,
    df_student_status: pd.DataFrame,
    df_quality_master: pd.DataFrame,
    ghosting_stats: dict,
) -> bytes:
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 is required for PDF generation. Install with: pip install fpdf2")

    lang = get_lang()
    is_id = lang == "id"

    class ReportPDF(FPDF):
        def header(self):
            self.set_font("TNR", "B", 10)
            self.set_text_color(0, 0, 0)
            if self.page_no() > 1:
                title = "Laporan Periodik Placement Mahasiswa" if is_id else "Student Placement Periodic Report"
                self.cell(0, 8, title, align="L", ln=0)
                self.cell(0, 8, "SMILE Dashboard | SSDC 2026", align="R", ln=1)
                self.set_draw_color(0, 0, 0)
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                self.ln(4)

        def footer(self):
            self.set_y(-15)
            self.set_font("TNR", "", 9)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, f"{self.page_no()}", align="C", ln=0)

    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)

    # register times new roman
    tnr_regular = _find_tnr_font("regular")
    tnr_bold = _find_tnr_font("bold")
    tnr_italic = _find_tnr_font("italic")

    if tnr_regular:
        pdf.add_font("TNR", "", tnr_regular, uni=True)
    else:
        pdf.add_font("TNR", "", style="")

    if tnr_bold:
        pdf.add_font("TNR", "B", tnr_bold, uni=True)
    else:
        pdf.add_font("TNR", "B", style="B")

    if tnr_italic:
        pdf.add_font("TNR", "I", tnr_italic, uni=True)
    else:
        pdf.add_font("TNR", "I", style="I")

    pdf.set_text_color(0, 0, 0)
    now = datetime.now()
    date_str = now.strftime("%d %B %Y")

    def add_section_title(title: str):
        pdf.set_font("TNR", "B", 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 12, title, ln=1)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.5)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 60, pdf.get_y())
        pdf.ln(6)

    def add_subsection_title(title: str):
        pdf.set_font("TNR", "B", 13)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, title, ln=1)
        pdf.ln(2)

    def add_body_text(text: str):
        pdf.set_font("TNR", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, text)
        pdf.ln(3)

    def add_chart_image(fig, caption: str = "", width_mm: float = 140):
        tmp_path = None
        try:
            img_bytes = _plt_to_bytes(fig)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name

            img_w = width_mm
            x_centered = (pdf.w - img_w) / 2

            if pdf.get_y() + 55 > pdf.h - 20:
                pdf.add_page()

            pdf.image(tmp_path, x=x_centered, w=img_w)
            pdf.ln(2)
            if caption:
                pdf.set_font("TNR", "I", 9)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 5, caption, align="C", ln=1)
                pdf.ln(3)
        except Exception:
            add_body_text(f"[Grafik: {caption}]")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def add_kpi_row(label: str, value: str):
        col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / 2
        pdf.set_font("TNR", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(col_w, 7, f"  {label}", border="TB", ln=0)
        pdf.set_font("TNR", "B", 11)
        pdf.cell(col_w, 7, value, border="TB", align="R", ln=1)

    # cover page
    pdf.add_page()
    pdf.ln(50)
    logo_path = os.path.join("assets", "smile-b1.png")
    if os.path.isfile(logo_path):
        pdf.image(logo_path, x=60, w=90)
        pdf.ln(10)
    pdf.set_font("TNR", "B", 26)
    pdf.set_text_color(0, 0, 0)
    title = "Laporan Periodik\nPlacement Mahasiswa" if is_id else "Student Placement\nPeriodic Report"
    pdf.multi_cell(0, 14, title, align="C")
    pdf.ln(6)
    pdf.set_font("TNR", "", 13)
    pdf.cell(0, 8, "SMILE Dashboard | SSDC 2026", align="C", ln=1)
    pdf.ln(4)
    pdf.set_font("TNR", "I", 11)
    gen_label = "Dibuat pada" if is_id else "Generated on"
    pdf.cell(0, 8, f"{gen_label}: {date_str}", align="C", ln=1)

    # section 1: ringkasan utama
    pdf.add_page()
    section_title = "Ringkasan Utama" if is_id else "Main Summary"
    add_section_title(section_title)

    total_students = len(df_student_eligibility)
    eligible_count = int(df_student_eligibility["is_eligible"].sum()) if "is_eligible" in df_student_eligibility.columns else 0
    eligible_pct = round(eligible_count / total_students * 100, 1) if total_students > 0 else 0
    total_companies = df_company["id_company"].nunique() if "id_company" in df_company.columns else 0
    total_requests = len(df_tc)
    total_placement = len(df_ts[df_ts["progress_student"] == "Placement"]) if "progress_student" in df_ts.columns else 0
    total_sent = int(df_tc["jumlah_dikirimkan"].sum()) if "jumlah_dikirimkan" in df_tc.columns else (int(df_tc["jumlah_dikirim"].sum()) if "jumlah_dikirim" in df_tc.columns else 0)
    fulfillment_rate = round(total_placement / total_sent * 100, 1) if total_sent > 0 else 0

    summary_text = (
        f"Laporan ini menyajikan rekapitulasi menyeluruh aktivitas placement mahasiswa yang tercatat dalam "
        f"sistem SMILE pada periode yang dilaporan. Dari total {total_students:,} mahasiswa terdaftar, "
        f"sebanyak {eligible_count:,} mahasiswa ({eligible_pct}%) memenuhi kriteria kelayakan untuk dikirimkan "
        f"ke perusahaan mitra. Sistem mencatat {total_companies:,} perusahaan aktif dengan {total_requests:,} "
        f"permintaan talent, dari mana {total_sent:,} kandidat telah dikirimkan dan {total_placement:,} mahasiswa "
        f"berhasil ditempatkan, menghasilkan tingkat pemenuhan sebesar {fulfillment_rate}%."
        if is_id else
        f"This report presents a comprehensive recapitulation of student placement activities recorded in the SMILE "
        f"system. Out of {total_students:,} registered students, {eligible_count:,} ({eligible_pct}%) meet the "
        f"eligibility criteria for company submission. The system records {total_companies:,} active companies with "
        f"{total_requests:,} talent requests, of which {total_sent:,} candidates were submitted and "
        f"{total_placement:,} students were successfully placed, yielding a fulfillment rate of {fulfillment_rate}%."
    )
    add_body_text(summary_text)

    kpi_data = [
        ("Total Mahasiswa" if is_id else "Total Students", f"{total_students:,}"),
        ("Mahasiswa Eligible" if is_id else "Eligible Students", f"{eligible_count:,} ({eligible_pct}%)"),
        ("Total Perusahaan Mitra" if is_id else "Partner Companies", f"{total_companies:,}"),
        ("Total Permintaan Talent" if is_id else "Talent Requests", f"{total_requests:,}"),
        ("Total Kandidat Dikirim" if is_id else "Candidates Submitted", f"{total_sent:,}"),
        ("Total Placement" if is_id else "Total Placements", f"{total_placement:,}"),
        ("Tingkat Pemenuhan" if is_id else "Fulfillment Rate", f"{fulfillment_rate}%"),
    ]
    pdf.ln(3)
    for label, val in kpi_data:
        add_kpi_row(label, val)
    pdf.ln(6)

    # section 2: rekapitulasi placement bt-07
    pdf.add_page()
    bt07_title = "Rekapitulasi Placement Mahasiswa (BT-07)" if is_id else "Student Placement Recapitulation (BT-07)"
    add_section_title(bt07_title)

    bt07_intro = (
        "Bagian ini menyajikan rekapitulasi lengkap data penempatan mahasiswa sesuai kebutuhan evaluasi institusi "
        "berdasarkan BT-07, mencakup distribusi placement berdasarkan semester, program studi, perusahaan mitra, "
        "dan jenis penempatan. Data yang disajikan merupakan akumulasi seluruh mahasiswa yang berhasil ditempatkan "
        "selama periode yang tercatat dalam sistem SMILE."
        if is_id else
        "This section presents a complete recapitulation of student placement data per institutional evaluation "
        "requirements under BT-07, covering distribution by semester, study program, partner company, and placement "
        "type. Data represents all students successfully placed during the recorded period in the SMILE system."
    )
    add_body_text(bt07_intro)

    # --- 2.1 Placement per Semester ---
    add_subsection_title("2.1 Placement per Semester" if is_id else "2.1 Placement by Semester")

    student_info = df_student_status[["NIM", "program_studi", "semester"]].drop_duplicates() if "program_studi" in df_student_status.columns else pd.DataFrame()
    placed_df = df_ts[df_ts["progress_student"] == "Placement"].copy() if "progress_student" in df_ts.columns else pd.DataFrame()

    if not placed_df.empty and not student_info.empty:
        placed_sem = placed_df.merge(student_info[["NIM", "semester"]], on="NIM", how="left")
        sem_counts = placed_sem["semester"].value_counts().sort_index()
        sem_total = int(sem_counts.sum())
        sem_median = placed_sem["semester"].astype(str).dropna().apply(lambda x: float(re.sub(r'[^0-9.]', '', x)) if re.sub(r'[^0-9.]', '', x) else 0).median()

        sem_text = (
            f"Berdasarkan data yang tercatat, mahasiswa yang berhasil ditempatkan tersebar pada berbagai semester akademik. "
            f"Dari total {sem_total:,} mahasiswa yang ditempatkan, sebaran per semester menunjukkan pola yang bergantung "
            f"pada siklus akademik dan kesiapan mahasiswa. Semester dengan jumlah placement tertinggi adalah semester "
            f"{sem_counts.idxmax()} dengan {int(sem_counts.max()):,} mahasiswa."
            if is_id else
            f"Based on recorded data, successfully placed students are distributed across various academic semesters. "
            f"Of {sem_total:,} total placements, the distribution reflects academic cycle patterns. "
            f"The semester with the highest placements is semester {sem_counts.idxmax()} with {int(sem_counts.max()):,} students."
        )
        add_body_text(sem_text)

        fig_sem = _build_bt07_by_semester(df_ts, df_student_status)
        add_chart_image(fig_sem, "Gambar 2.1 — Distribusi Placement per Semester" if is_id else "Figure 2.1 — Placement Distribution by Semester")

        # Semester summary table
        pdf.set_font("TNR", "B", 11)
        pdf.cell(0, 8, "Tabel Rekapitulasi per Semester" if is_id else "Semester Summary Table", ln=1)
        pdf.set_font("TNR", "", 10)
        col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / 3
        pdf.set_fill_color(220, 220, 220)
        for header in (["Semester", "Jumlah Placement", "Persentase"] if is_id else ["Semester", "Placements", "Percentage"]):
            pdf.cell(col_w, 7, header, border=1, align="C", fill=True, ln=0)
        pdf.ln()
        for sem, cnt in sem_counts.items():
            pct = round(cnt / sem_total * 100, 1) if sem_total > 0 else 0
            pdf.cell(col_w, 6, str(sem), border=1, align="C", ln=0)
            pdf.cell(col_w, 6, f"{int(cnt):,}", border=1, align="C", ln=0)
            pdf.cell(col_w, 6, f"{pct}%", border=1, align="C", ln=0)
            pdf.ln()
        pdf.ln(4)

    else:
        add_body_text("Data semester tidak tersedia." if is_id else "Semester data not available.")

    # --- 2.2 Placement per Program Studi ---
    add_subsection_title("2.2 Placement per Program Studi" if is_id else "2.2 Placement by Study Program")

    if not placed_df.empty and not student_info.empty:
        placed_prodi = placed_df.merge(student_info[["NIM", "program_studi"]], on="NIM", how="left")
        prodi_counts = placed_prodi["program_studi"].value_counts().head(10)
        prodi_total = int(prodi_counts.sum())

        prodi_text = (
            f"Distribusi placement per program studi menunjukkan pola kebutuhan industri yang bervariasi. "
            f"Program studi yang paling banyak menghasilkan lulusan yang ditempatkan adalah {prodi_counts.idxmax()} "
            f"dengan {int(prodi_counts.max()):,} mahasiswa, mewakili {round(prodi_counts.max() / prodi_total * 100, 1) if prodi_total > 0 else 0}% "
            f"dari total {prodi_total:,} mahasiswa yang berhasil ditempatkan pada 10 program studi teratas."
            if is_id else
            f"Placement distribution by study program reflects varying industry demand patterns. "
            f"The study program with the highest placement count is {prodi_counts.idxmax()} with "
            f"{int(prodi_counts.max()):,} students, representing "
            f"{round(prodi_counts.max() / prodi_total * 100, 1) if prodi_total > 0 else 0}% of {prodi_total:,} "
            f"total placed students in the top 10 study programs."
        )
        add_body_text(prodi_text)

        fig_prodi = _build_bt07_by_prodi(df_ts, df_student_status)
        add_chart_image(fig_prodi, "Gambar 2.2 — Placement per Program Studi (Top 10)" if is_id else "Figure 2.2 — Placement by Study Program (Top 10)")

    else:
        add_body_text("Data program studi tidak tersedia." if is_id else "Study program data not available.")

    # --- 2.3 Placement per Perusahaan (Top 10) ---
    add_subsection_title("2.3 Placement per Perusahaan (Top 10)" if is_id else "2.3 Placement by Company (Top 10)")

    if not placed_df.empty and "company" in placed_df.columns:
        comp_counts = placed_df.groupby("company").size().nlargest(10)
        comp_total_top10 = int(comp_counts.sum())

        comp_text = (
            f"Sepuluh perusahaan teratas berdasarkan jumlah mahasiswa yang berhasil ditempatkan mencakup {comp_total_top10:,} "
            f"mahasiswa dari total {total_placement:,} placement yang tercatat. Perusahaan dengan kontribusi placement terbanyak "
            f"adalah {comp_counts.idxmax()} dengan {int(comp_counts.max()):,} mahasiswa. Data ini mencerminkan kekuatan "
            f"kemitraan institusi dengan sektor industri yang relevan."
            if is_id else
            f"The top 10 companies by placement count account for {comp_total_top10:,} students out of {total_placement:,} "
            f"total recorded placements. The company with the highest contribution is {comp_counts.idxmax()} with "
            f"{int(comp_counts.max()):,} students. This data reflects the strength of institutional partnerships with relevant industry sectors."
        )
        add_body_text(comp_text)

        fig_comp = _build_bt07_by_company(df_ts)
        add_chart_image(fig_comp, "Gambar 2.3 — Top 10 Perusahaan berdasarkan Jumlah Placement" if is_id else "Figure 2.3 — Top 10 Companies by Placement Count")

    else:
        add_body_text("Data perusahaan tidak tersedia." if is_id else "Company data not available.")

    # --- 2.4 Placement per Jenis Penempatan ---
    add_subsection_title("2.4 Placement per Jenis Penempatan" if is_id else "2.4 Placement by Type")

    fig_type, jenis_counts = _build_bt07_by_type(df_tc, df_ts)
    jenis_total = int(jenis_counts.sum())

    jenis_text = (
        f"Distribusi penempatan berdasarkan jenis atau skema program menunjukkan komposisi antara Magang, "
        f"Penempatan Penuh Waktu (Full-time), dan Paruh Waktu (Part-time). "
    )
    for jenis, cnt in jenis_counts.items():
        pct = round(cnt / jenis_total * 100, 1) if jenis_total > 0 else 0
        jenis_text += f"Jenis {jenis} mencakup {int(cnt):,} mahasiswa ({pct}%). "

    if not is_id:
        jenis_text = (
            f"Placement distribution by scheme shows the composition of Internship (Magang), "
            f"Full-time, and Part-time programs. "
        )
        for jenis, cnt in jenis_counts.items():
            pct = round(cnt / jenis_total * 100, 1) if jenis_total > 0 else 0
            jenis_text += f"{jenis} covers {int(cnt):,} students ({pct}%). "

    add_body_text(jenis_text)
    add_chart_image(fig_type, "Gambar 2.4 — Distribusi Placement per Jenis Penempatan" if is_id else "Figure 2.4 — Placement Distribution by Type", width_mm=110)

    # section 3: analisis proses seleksi bt-02 dan bt-05
    pdf.add_page()
    proc_title = "Analisis Proses Seleksi (BT-02, BT-05)" if is_id else "Selection Process Analysis (BT-02, BT-05)"
    add_section_title(proc_title)

    total_tracked = len(df_ts)
    finished = ["Placement", "Rejected", "Finish"]
    active_in_process = len(df_ts[~df_ts["progress_student"].isin(finished)]) if "progress_student" in df_ts.columns else 0
    ghost_total = ghosting_stats.get("total_ghosted", 0)
    fu_total = ghosting_stats.get("total_fu", 0)

    proc_text = (
        f"Sistem mencatat {total_tracked:,} total proses seleksi kandidat yang berjalan. Dari jumlah tersebut, "
        f"{active_in_process:,} proses masih aktif berjalan, sementara {total_placement:,} mahasiswa berhasil "
        f"ditempatkan. Tim CDC perlu memberikan perhatian khusus pada {ghost_total:,} kasus ghosting dan "
        f"{fu_total:,} kasus yang memerlukan tindakan follow-up segera."
        if is_id else
        f"The system records {total_tracked:,} total candidate selection processes. Of these, "
        f"{active_in_process:,} processes are still active, while {total_placement:,} students were successfully placed. "
        f"The CDC team should pay particular attention to {ghost_total:,} ghosting cases and "
        f"{fu_total:,} cases requiring immediate follow-up action."
    )
    add_body_text(proc_text)

    fig_stage = _build_stage_distribution(df_ts)
    stage_caption = "Gambar 3.1 — Distribusi Tahapan Seleksi Aktif" if is_id else "Figure 3.1 — Active Selection Stage Distribution"
    add_chart_image(fig_stage, stage_caption)

    fig_ghost = _build_ghosting_pie(active_in_process, fu_total, ghost_total)
    ghost_caption = "Gambar 3.2 — Proporsi Ghosting pada Kandidat Aktif" if is_id else "Figure 3.2 — Ghosting Proportion Among Active Candidates"
    add_chart_image(fig_ghost, ghost_caption, width_mm=110)

    # section 4: analisis kelayakan mahasiswa bt-06
    pdf.add_page()
    elig_title = "Analisis Kelayakan Mahasiswa (BT-06)" if is_id else "Student Eligibility Analysis (BT-06)"
    add_section_title(elig_title)

    elig_text = (
        f"Analisis kelayakan mahasiswa dilakukan berdasarkan serangkaian kriteria yang mencakup kelengkapan CV, "
        f"ketersediaan portofolio, status keaktifan, ketersediaan untuk ditempatkan, serta pencapaian IPK minimum. "
        f"Dari {total_students:,} mahasiswa yang dievaluasi, {eligible_count:,} mahasiswa ({eligible_pct}%) "
        f"memenuhi seluruh persyaratan kelayakan yang ditetapkan dan siap untuk dikirimkan kepada perusahaan mitra."
        if is_id else
        f"Student eligibility evaluation covers CV completeness, portfolio availability, active enrollment status, "
        f"placement availability, and minimum GPA requirements. Of {total_students:,} evaluated students, "
        f"{eligible_count:,} ({eligible_pct}%) meet all eligibility requirements and are ready for company submission."
    )
    add_body_text(elig_text)

    fig_elig = _build_eligibility_pie(df_student_eligibility)
    elig_caption = "Gambar 4.1 — Komposisi Kelayakan Mahasiswa" if is_id else "Figure 4.1 — Student Eligibility Composition"
    add_chart_image(fig_elig, elig_caption, width_mm=110)

    # ============================================================
    # kualitas data bt-08
    if not df_quality_master.empty:
        pdf.add_page()
        quality_title = "Analisis Kualitas Data (BT-08)" if is_id else "Data Quality Analysis (BT-08)"
        add_section_title(quality_title)

        total_q = len(df_quality_master)
        critical_count = len(df_quality_master[df_quality_master["staleness"] == "Critical"]) if "staleness" in df_quality_master.columns else 0
        critical_pct = round(critical_count / total_q * 100, 1) if total_q > 0 else 0
        mismatch_count = int(df_quality_master["has_mismatch"].sum()) if "has_mismatch" in df_quality_master.columns else 0
        mismatch_pct = round(mismatch_count / total_q * 100, 1) if total_q > 0 else 0

        quality_text = (
            f"Evaluasi kualitas data dilakukan dengan menganalisis kebaruan sinkronisasi dan konsistensi data "
            f"antara tabel Student All dan Status Student. Dari {total_q:,} rekaman mahasiswa yang dianalisis, "
            f"{critical_count:,} rekaman ({critical_pct}%) berada dalam status sinkronisasi kritis (lebih dari "
            f"179 hari tanpa pembaruan), dan {mismatch_count:,} rekaman ({mismatch_pct}%) menunjukkan "
            f"ketidakcocokan data antar tabel yang perlu segera ditindaklanjuti."
            if is_id else
            f"Data quality evaluation analyzes synchronization freshness and consistency between the Student All "
            f"and Status Student tables. Of {total_q:,} student records analyzed, {critical_count:,} ({critical_pct}%) "
            f"have critical synchronization status (over 179 days without updates), and {mismatch_count:,} ({mismatch_pct}%) "
            f"show data mismatches requiring immediate attention."
        )
        add_body_text(quality_text)

        fig_stale = _build_staleness_pie(df_quality_master)
        stale_caption = "Gambar 5.1 — Distribusi Keusangan Data Sinkronisasi" if is_id else "Figure 5.1 — Data Synchronization Staleness Distribution"
        add_chart_image(fig_stale, stale_caption, width_mm=110)

    # closing
    closing_title = "Penutup" if is_id else "Closing"
    add_section_title(closing_title)

    closing_text = (
        "Laporan periodik ini menyajikan gambaran menyeluruh kinerja sistem placement mahasiswa pada periode yang "
        "tercatat dalam SMILE Dashboard. Analisis rekapitulasi placement berdasarkan semester, program studi, "
        "perusahaan, dan jenis penempatan memberikan landasan evaluasi yang komprehensif bagi institusi dalam "
        "menilai efektivitas program placement secara kuantitatif."
        if is_id else
        "This periodic report presents a comprehensive overview of the student placement system performance "
        "recorded in the SMILE Dashboard. The placement recapitulation analysis by semester, study program, "
        "company, and placement type provides a comprehensive evaluation basis for institutional assessment "
        "of placement program effectiveness quantitatively."
    )
    add_body_text(closing_text)

    rec_text = (
        "Tim CDC disarankan untuk: (1) menindaklanjuti kasus ghosting yang teridentifikasi dalam sistem, "
        "(2) memperbarui data sinkronisasi yang berada dalam status kritis, (3) meningkatkan upaya penempatan "
        "pada program studi dengan tingkat placement yang masih rendah, dan (4) memperluas kemitraan dengan "
        "perusahaan di sektor industri yang relevan untuk meningkatkan penyerapan lulusan."
        if is_id else
        "The CDC team is advised to: (1) follow up on identified ghosting cases, (2) update synchronization "
        "data in critical status, (3) intensify placement efforts for study programs with low placement rates, "
        "and (4) expand partnerships with companies in relevant industry sectors to increase graduate absorption."
    )
    add_body_text(rec_text)

    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin1", errors="replace")
    elif isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return bytes(pdf.output())
