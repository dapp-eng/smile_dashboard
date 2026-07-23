# pdf report generator for periodic placement reports (bt-07)

import io
import os
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


# pie chart placement distribution by jenis penempatan
def _build_placement_by_type_chart(df_tc, df_ts):
    placed = df_ts[df_ts["progress_student"] == "Placement"] if "progress_student" in df_ts.columns else df_ts
    if "jenis_penempatan" in placed.columns and not placed["jenis_penempatan"].dropna().empty:
        counts = placed["jenis_penempatan"].value_counts()
    elif "id_tracking_company" in placed.columns and "id_tracking_company" in df_tc.columns and "jenis_penempatan" in df_tc.columns:
        merged = placed.merge(df_tc[["id_tracking_company", "jenis_penempatan"]], on="id_tracking_company", how="left")
        counts = merged["jenis_penempatan"].value_counts()
    elif "jenis_penempatan" in df_tc.columns and not df_tc["jenis_penempatan"].dropna().empty:
        counts = df_tc["jenis_penempatan"].value_counts()
    else:
        counts = pd.Series({"Magang": 1, "Full-time": 1, "Part-time": 1})

    fig, ax = plt.subplots(figsize=(4.5, 2.2), dpi=200)
    color_map = {"Magang": "#3462ED", "Full-time": "#42c1b6", "Part-time": "#5B7FFF"}
    colors = [color_map.get(k, "#3462ED") for k in counts.index]

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

    fig, ax = plt.subplots(figsize=(5.5, 2.2), dpi=200)
    ax.plot(x_labels, y_values, marker="o", color="#3462ED", linewidth=2, markersize=4)
    ax.fill_between(x_labels, y_values, color="#3462ED", alpha=0.12)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    plt.xticks(rotation=25, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    return fig


# horizontal bar top companies by placement count
def _build_top_companies_chart(df_tc, df_ts, top_n: int = 10):
    if "progress_student" in df_ts.columns and "company" in df_ts.columns:
        placed = df_ts[df_ts["progress_student"] == "Placement"]
        if not placed.empty:
            counts = placed.groupby("company").size().nlargest(top_n).sort_values(ascending=True)
        else:
            counts = pd.Series({"Data Tidak Tersedia": 0})
    elif "nama_perusahaan" in df_tc.columns:
        counts = df_tc["nama_perusahaan"].value_counts().head(top_n).sort_values(ascending=True)
    else:
        counts = pd.Series({"Data Tidak Tersedia": 0})

    fig, ax = plt.subplots(figsize=(5.5, 2.4), dpi=200)
    bars = ax.barh(counts.index, counts.values, color="#3462ED", height=0.6)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")

    max_val = max(1, counts.max())
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(0.1, max_val * 0.02), bar.get_y() + bar.get_height() / 2, f"{int(w)}",
                va="center", ha="left", fontsize=8, fontweight="bold", color="#1E293B")

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    return fig


# horizontal bar placement count by program studi
def _build_placement_by_prodi_chart(df_ts, df_student_status):
    if "progress_student" in df_ts.columns and "NIM" in df_ts.columns and "program_studi" in df_student_status.columns:
        placed = df_ts[df_ts["progress_student"] == "Placement"]
        merged = placed.merge(
            df_student_status[["NIM", "program_studi"]].drop_duplicates(),
            on="NIM", how="left"
        )
        counts = merged["program_studi"].value_counts().head(10).sort_values(ascending=True)
    else:
        counts = pd.Series({"Data Tidak Tersedia": 0})

    fig, ax = plt.subplots(figsize=(5.5, 2.4), dpi=200)
    bars = ax.barh(counts.index, counts.values, color="#4748B0", height=0.6)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")

    max_val = max(1, counts.max())
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(0.1, max_val * 0.02), bar.get_y() + bar.get_height() / 2, f"{int(w)}",
                va="center", ha="left", fontsize=8, fontweight="bold", color="#1E293B")

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    return fig


# donut eligible vs ineligible students
def _build_eligibility_pie(df_eligibility):
    if "is_eligible" in df_eligibility.columns and not df_eligibility.empty:
        comp = df_eligibility["is_eligible"].map({True: "Eligible", False: "Ineligible"}).value_counts()
    else:
        comp = pd.Series({"Eligible": 0, "Ineligible": 0})

    fig, ax = plt.subplots(figsize=(4.5, 2.2), dpi=200)
    colors = ["#10B981", "#EF4444"]
    labels = comp.index.tolist()
    values = comp.values.tolist()
    if sum(values) == 0:
        values = [1, 0]

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%", startangle=90,
        colors=colors[:len(values)], wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=8, color="#1E293B")
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_weight("bold")
    ax.axis("equal")
    plt.tight_layout()
    return fig


# horizontal bar selection stage distribution
def _build_stage_distribution(df_track):
    if "progress_student" in df_track.columns and not df_track.empty:
        counts = df_track["progress_student"].value_counts().sort_values(ascending=True)
    else:
        counts = pd.Series({"Placement": 0})

    fig, ax = plt.subplots(figsize=(5.5, 2.4), dpi=200)
    bars = ax.barh(counts.index, counts.values, color="#3462ED", height=0.6)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")

    max_val = max(1, counts.max())
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(0.1, max_val * 0.02), bar.get_y() + bar.get_height() / 2, f"{int(w)}",
                va="center", ha="left", fontsize=8, fontweight="bold", color="#1E293B")

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    return fig


# donut ghosting proportion
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


# donut data staleness distribution
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


# generate a comprehensive periodic report pdf returning bytes for download
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

    def add_chart_image(fig, caption: str = "", width_mm: float = 110):
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
            os.unlink(tmp_path)
        except Exception:
            add_body_text(f"[Chart: {caption}]")
            pdf.ln(2)
            if caption:
                pdf.set_font("TNR", "I", 9)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 5, caption, align="C", ln=1)
                pdf.ln(3)
            os.unlink(tmp_path)
        except Exception:
            add_body_text(f"[Chart: {caption}]")

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

    # main summary
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

    if is_id:
        summary = (
            f"Laporan ini mencakup seluruh aktivitas placement mahasiswa yang tercatat dalam sistem SMILE. "
            f"Dari total {total_students:,} mahasiswa yang terdaftar, sebanyak {eligible_count:,} mahasiswa "
            f"({eligible_pct}%) dinyatakan eligible untuk dikirimkan ke perusahaan. "
            f"Sistem mencatat {total_companies:,} perusahaan mitra aktif dengan total {total_requests:,} permintaan talent. "
            f"Sebanyak {total_placement:,} mahasiswa berhasil ditempatkan dari {total_sent:,} kandidat yang dikirimkan, "
            f"menghasilkan tingkat pemenuhan sebesar {fulfillment_rate}%."
        )
    else:
        summary = (
            f"This report covers all student placement activities recorded in the SMILE system. "
            f"Out of {total_students:,} registered students, {eligible_count:,} ({eligible_pct}%) "
            f"are eligible for company placement. "
            f"The system records {total_companies:,} active partner companies with {total_requests:,} talent requests. "
            f"A total of {total_placement:,} students were successfully placed from {total_sent:,} submitted candidates, "
            f"yielding a fulfillment rate of {fulfillment_rate}%."
        )
    add_body_text(summary)

    pdf.set_font("TNR", "B", 11)
    pdf.set_draw_color(0, 0, 0)
    kpi_data = [
        ("Total Mahasiswa" if is_id else "Total Students", f"{total_students:,}"),
        ("Eligible", f"{eligible_count:,} ({eligible_pct}%)"),
        ("Total Perusahaan" if is_id else "Total Companies", f"{total_companies:,}"),
        ("Total Permintaan" if is_id else "Total Requests", f"{total_requests:,}"),
        ("Total Placement", f"{total_placement:,}"),
        ("Tingkat Pemenuhan" if is_id else "Fulfillment Rate", f"{fulfillment_rate}%"),
    ]
    col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / 2
    for label, val in kpi_data:
        pdf.set_font("TNR", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(col_w, 7, f"  {label}", border="TB", ln=0)
        pdf.set_font("TNR", "B", 11)
        pdf.cell(col_w, 7, val, border="TB", align="R", ln=1)
    pdf.ln(6)

    # bt-06 student eligibility analysis
    section_label = "Analisis Kelayakan Mahasiswa (BT-06)" if is_id else "Student Eligibility Analysis (BT-06)"
    add_section_title(section_label)

    if is_id:
        add_body_text(
            f"Analisis kelayakan mahasiswa dilakukan berdasarkan beberapa kriteria utama, meliputi kelengkapan CV, "
            f"portofolio, status keaktifan, ketersediaan, serta pencapaian IPK minimum. "
            f"Dari {total_students:,} mahasiswa yang terevaluasi, {eligible_count:,} mahasiswa memenuhi seluruh persyaratan "
            f"kelayakan yang ditetapkan."
        )
    else:
        add_body_text(
            f"Student eligibility is evaluated based on several key criteria including CV completeness, "
            f"portfolio availability, active status, availability, and minimum GPA achievement. "
            f"Out of {total_students:,} evaluated students, {eligible_count:,} met all eligibility requirements."
        )

    fig_elig = _build_eligibility_pie(df_student_eligibility)
    elig_caption = "Komposisi Kelayakan Mahasiswa" if is_id else "Student Eligibility Composition"
    add_chart_image(fig_elig, elig_caption)

    # bt-03 bt-04 company analysis
    section_label = "Analisis Permintaan Perusahaan (BT-03, BT-04)" if is_id else "Company Request Analysis (BT-03, BT-04)"
    add_section_title(section_label)

    if is_id:
        add_body_text(
            f"Selama periode yang tercatat, terdapat {total_requests:,} permintaan talent dari {total_companies:,} "
            f"perusahaan mitra. Distribusi permintaan menunjukkan variasi yang signifikan berdasarkan jenis penempatan "
            f"maupun sektor industri. Berikut adalah distribusi placement berdasarkan jenis penempatan."
        )
    else:
        add_body_text(
            f"During the recorded period, there were {total_requests:,} talent requests from {total_companies:,} "
            f"partner companies. Request distribution shows significant variation across placement types "
            f"and industry sectors. Below is the placement distribution by placement type."
        )

    fig_type = _build_placement_by_type_chart(df_tc, df_ts)
    type_caption = "Distribusi Placement berdasarkan Jenis Penempatan" if is_id else "Placement Distribution by Type"
    add_chart_image(fig_type, type_caption)

    fig_trend = _build_monthly_request_trend(df_tc)
    trend_caption = "Tren Permintaan Talent Bulanan" if is_id else "Monthly Talent Request Trend"
    add_chart_image(fig_trend, trend_caption)

    if is_id:
        add_body_text(
            "Grafik tren di atas menunjukkan pola permintaan talent dari waktu ke waktu. "
            "Fluktuasi ini dipengaruhi oleh siklus akademik dan kebutuhan industri yang bervariasi setiap bulannya."
        )
    else:
        add_body_text(
            "The trend chart above shows talent request patterns over time. "
            "These fluctuations are influenced by academic cycles and varying monthly industry needs."
        )

    fig_top = _build_top_companies_chart(df_tc, df_ts)
    top_caption = "Perusahaan dengan Placement Tertinggi" if is_id else "Top Companies by Placement"
    add_chart_image(fig_top, top_caption)

    # bt-02 bt-05 process analysis
    section_label = "Analisis Proses Seleksi (BT-02, BT-05)" if is_id else "Selection Process Analysis (BT-02, BT-05)"
    add_section_title(section_label)

    total_tracked = len(df_ts)
    finished = ["Placement", "Rejected", "Finish"]
    active_in_process = len(df_ts[~df_ts["progress_student"].isin(finished)]) if "progress_student" in df_ts.columns else 0
    ghost_total = ghosting_stats.get("total_ghosted", 0)
    fu_total = ghosting_stats.get("total_fu", 0)

    if is_id:
        add_body_text(
            f"Sistem mencatat {total_tracked:,} total proses seleksi kandidat. Dari jumlah tersebut, "
            f"{active_in_process:,} proses masih aktif berjalan, sementara {total_placement:,} mahasiswa berhasil "
            f"ditempatkan. Sistem mendeteksi {ghost_total:,} kasus ghosting dan {fu_total:,} kasus yang memerlukan "
            f"tindakan follow-up dari tim CDC."
        )
    else:
        add_body_text(
            f"The system records {total_tracked:,} total candidate selection processes. Of these, "
            f"{active_in_process:,} processes are still actively running, while {total_placement:,} students were "
            f"successfully placed. The system detected {ghost_total:,} ghosting cases and {fu_total:,} cases "
            f"requiring follow-up action from the CDC team."
        )

    fig_stage = _build_stage_distribution(df_ts)
    stage_caption = "Distribusi Tahapan Seleksi" if is_id else "Selection Stage Distribution"
    add_chart_image(fig_stage, stage_caption)

    fig_ghost = _build_ghosting_pie(active_in_process, fu_total, ghost_total)
    ghost_caption = "Proporsi Ghosting pada Kandidat Aktif" if is_id else "Ghosting Proportion Among Active Candidates"
    add_chart_image(fig_ghost, ghost_caption)

    # bt-08 data quality
    if not df_quality_master.empty:
        section_label = "Analisis Kualitas Data (BT-08)" if is_id else "Data Quality Analysis (BT-08)"
        add_section_title(section_label)

        total_q = len(df_quality_master)
        critical_count = len(df_quality_master[df_quality_master["staleness"] == "Critical"]) if "staleness" in df_quality_master.columns else 0
        critical_pct = round(critical_count / total_q * 100, 1) if total_q > 0 else 0
        mismatch_count = int(df_quality_master["has_mismatch"].sum()) if "has_mismatch" in df_quality_master.columns else 0
        mismatch_pct = round(mismatch_count / total_q * 100, 1) if total_q > 0 else 0

        if is_id:
            add_body_text(
                f"Evaluasi kualitas data dilakukan dengan menganalisis kebaruan sinkronisasi dan konsistensi data "
                f"antara tabel Student All dan Status Student. Dari {total_q:,} record mahasiswa, "
                f"{critical_count:,} ({critical_pct}%) memiliki data dengan status sinkronisasi kritis "
                f"(lebih dari 179 hari tanpa pembaruan), dan {mismatch_count:,} ({mismatch_pct}%) menunjukkan "
                f"ketidakcocokan data antar kedua tabel."
            )
        else:
            add_body_text(
                f"Data quality evaluation analyzes synchronization freshness and data consistency "
                f"between the Student All and Status Student tables. Out of {total_q:,} student records, "
                f"{critical_count:,} ({critical_pct}%) have critical synchronization status "
                f"(over 179 days without updates), and {mismatch_count:,} ({mismatch_pct}%) show "
                f"data mismatches between the two tables."
            )

        fig_stale = _build_staleness_pie(df_quality_master)
        stale_caption = "Distribusi Keusangan Data" if is_id else "Data Staleness Distribution"
        add_chart_image(fig_stale, stale_caption)

    # closing
    pdf.add_page()
    closing_title = "Penutup" if is_id else "Closing"
    add_section_title(closing_title)

    if is_id:
        add_body_text(
            "Laporan ini memberikan gambaran menyeluruh mengenai kinerja sistem placement mahasiswa "
            "pada periode yang tercatat. Beberapa poin penting yang perlu mendapat perhatian antara lain "
            "tingkat kelayakan mahasiswa, efektivitas proses seleksi, serta kualitas sinkronisasi data."
        )
        add_body_text(
            "Tim CDC disarankan untuk terus memantau indikator kinerja utama yang disajikan dalam laporan ini, "
            "khususnya terkait tingkat ghosting dan keusangan data, guna memastikan operasional placement "
            "berjalan dengan optimal."
        )
    else:
        add_body_text(
            "This report provides a comprehensive overview of the student placement system performance "
            "during the recorded period. Key areas that require attention include student eligibility rates, "
            "selection process effectiveness, and data synchronization quality."
        )
        add_body_text(
            "The CDC team is encouraged to continuously monitor the key performance indicators presented in this report, "
            "particularly regarding ghosting rates and data staleness, to ensure optimal placement operations."
        )

    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin1", errors="replace")
    elif isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return bytes(pdf.output())
