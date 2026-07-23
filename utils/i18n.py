# multi-language support for the smile dashboard

import streamlit as st

LANGUAGES = {"id": "Bahasa Indonesia", "en": "English"}
DEFAULT_LANG = "id"

# translation dictionary: key -> {lang: text}
_TRANSLATIONS = {
    # page titles
    "page.overview": {"id": "Overview", "en": "Overview"},
    "page.monitor_student": {"id": "Monitor Mahasiswa", "en": "Monitor Student"},
    "page.monitor_company": {"id": "Monitor Perusahaan", "en": "Monitor Company"},
    "page.monitor_process": {"id": "Monitor Proses", "en": "Monitor Process"},
    "page.data_sync": {"id": "Sinkronisasi Data", "en": "Data Synchronization"},

    # sidebar section titles
    "sidebar.switch_mode": {"id": "MODE TAMPILAN", "en": "SWITCH MODE"},
    "sidebar.language": {"id": "BAHASA", "en": "LANGUAGE"},

    # bt descriptions
    "bt.07": {
        "id": "BT-07: Rekapitulasi placement per semester, prodi, perusahaan, dan jenis penempatan.",
        "en": "BT-07: Placement recapitulation by semester, study program, company, and placement type.",
    },
    "bt.06": {
        "id": "BT-06: Validasi kesiapan dan kelayakan mahasiswa berdasarkan CV, portofolio, IPK, dan status.",
        "en": "BT-06: Student readiness and eligibility validation based on CV, portfolio, GPA, and status.",
    },
    "bt.01": {
        "id": "BT-01: Pencocokan mahasiswa dengan kebutuhan perusahaan berdasarkan prodi, semester, dan tools.",
        "en": "BT-01: Student matching with company needs based on study program, semester, and tools.",
    },
    "bt.01_06": {
        "id": "BT-01 & BT-06: Evaluasi kelayakan mahasiswa dan pencocokan talent dengan kebutuhan perusahaan.",
        "en": "BT-01 & BT-06: Student eligibility evaluation and talent matching with company needs.",
    },
    "bt.03": {
        "id": "BT-03: Pengelolaan permintaan talent berdasarkan tanggal, headcount, dan jenis penempatan.",
        "en": "BT-03: Talent request management based on date, headcount, and placement type.",
    },
    "bt.04": {
        "id": "BT-04: Analisis tingkat keberhasilan placement dan identifikasi perusahaan mitra terbaik.",
        "en": "BT-04: Placement success rate analysis and top company partner identification.",
    },
    "bt.03_04": {
        "id": "BT-03 & BT-04: Manajemen permintaan talent dan analisis tingkat keberhasilan mitra perusahaan.",
        "en": "BT-03 & BT-04: Talent request management and partner company success rate analysis.",
    },
    "bt.02": {
        "id": "BT-02: Pemantauan real-time setiap tahapan progress seleksi mahasiswa.",
        "en": "BT-02: Real-time selection progress monitoring across all stages.",
    },
    "bt.05": {
        "id": "BT-05: Deteksi otomatis inaktivitas/ghosting kandidat untuk tindakan follow-up.",
        "en": "BT-05: Automatic candidate ghosting detection for timely follow-up action.",
    },
    "bt.02_05": {
        "id": "BT-02 & BT-05: Pemantauan progress tahapan seleksi real-time dan deteksi ghosting kandidat.",
        "en": "BT-02 & BT-05: Real-time selection progress monitoring and candidate ghosting detection.",
    },
    "bt.08": {
        "id": "BT-08: Sinkronisasi dan validasi data antara Student All dan Status Student.",
        "en": "BT-08: Data synchronization and validation between Student All and Status Student.",
    },

    # overview page
    "overview.caption": {
        "id": "Rangkuman kinerja sistem placement mahasiswa secara keseluruhan",
        "en": "Overall summary of the student placement system performance",
    },
    "overview.total_students": {"id": "Total Mahasiswa", "en": "Total Students"},
    "overview.total_companies": {"id": "Total Perusahaan", "en": "Total Companies"},
    "overview.total_requests": {"id": "Total Permintaan", "en": "Total Requests"},
    "overview.total_placement": {"id": "Total Placement", "en": "Total Placements"},
    "overview.fulfillment_rate": {"id": "Tingkat Pemenuhan", "en": "Fulfillment Rate"},
    "overview.ghosting_rate": {"id": "Tingkat Ghosting", "en": "Ghosting Rate"},
    "overview.eligible_rate": {"id": "Tingkat Kelayakan", "en": "Eligibility Rate"},
    "overview.avg_response": {"id": "Rata-rata Respons", "en": "Avg Response Time"},
    "overview.placement_by_type": {"id": "Placement berdasarkan Jenis Penempatan", "en": "Placement by Type"},
    "overview.monthly_trend": {"id": "Tren Permintaan Bulanan", "en": "Monthly Request Trend"},
    "overview.top_companies": {"id": "Perusahaan dengan Placement Tertinggi", "en": "Top Companies by Placement"},
    "overview.placement_by_prodi": {"id": "Placement berdasarkan Program Studi", "en": "Placement by Study Program"},
    "overview.selection_funnel": {"id": "Distribusi Tahapan Seleksi Mahasiswa", "en": "Student Selection Stage Distribution"},
    "overview.data_health": {"id": "Ringkasan Status Kualitas & Sinkronisasi Data", "en": "Data Quality & Sync Status Summary"},
    "overview.report_desc": {
        "id": "Laporan ini menyajikan rangkuman utama serta analisis komprehensif mengenai penempatan mahasiswa, kinerja kemitraan perusahaan, pemantauan proses seleksi, dan kualitas data operasional.",
        "en": "This report provides a main summary and comprehensive analysis of student placement, company partnership performance, selection process monitoring, and operational data quality.",
    },
    "overview.download_report": {"id": "Unduh Laporan PDF", "en": "Download PDF Report"},
    "overview.placed": {"id": "ditempatkan", "en": "placed"},
    "overview.days": {"id": "hari", "en": "days"},

    # monitor student page
    "ms.caption": {
        "id": "Evaluasi kelayakan dan pencocokan mahasiswa dengan kebutuhan perusahaan",
        "en": "Student eligibility evaluation and talent matching with company needs",
    },
    "ms.summary_total": {"id": "Total Mahasiswa", "en": "Total Students"},
    "ms.summary_available": {"id": "Tersedia", "en": "Available"},
    "ms.summary_placed": {"id": "Sudah Ditempatkan", "en": "Already Placed"},
    "ms.summary_prodi": {"id": "Program Studi", "en": "Study Programs"},
    "ms.summary_avg_ipk": {"id": "Rata-rata IPK", "en": "Average GPA"},
    "ms.eligibility_title": {"id": "Kelayakan Mahasiswa", "en": "Student Eligibility"},
    "ms.eligibility_caption": {
        "id": "Kondisi yang menentukan kelayakan mahasiswa untuk ditempatkan ke perusahaan",
        "en": "Conditions that determine whether a student is eligible for company placement",
    },
    "ms.min_ipk": {"id": "Minimum IPK", "en": "Minimum GPA"},
    "ms.cv_exists": {"id": "CV ada", "en": "CV available"},
    "ms.portfolio_exists": {"id": "Portofolio ada", "en": "Portfolio available"},
    "ms.status_active": {"id": "Status aktif", "en": "Active status"},
    "ms.available": {"id": "Tersedia", "en": "Available"},
    "ms.filter_prodi": {"id": "Filter program studi", "en": "Filter study program"},
    "ms.filter_prodi_help": {
        "id": "Kosongkan untuk menampilkan semua program studi.",
        "en": "Leave empty to include all study programs.",
    },
    "ms.show": {"id": "Tampilkan", "en": "Show"},
    "ms.show_eligible": {"id": "Eligible", "en": "Eligible"},
    "ms.show_all": {"id": "Semua", "en": "All"},
    "ms.show_ineligible": {"id": "Ineligible", "en": "Ineligible"},
    "ms.eligible": {"id": "Eligible", "en": "Eligible"},
    "ms.ineligible": {"id": "Ineligible", "en": "Ineligible"},
    "ms.avg_ipk_eligible": {"id": "Rata-rata IPK (eligible)", "en": "Average GPA (eligible)"},
    "ms.chart_elig_prodi": {"id": "Eligible vs Ineligible per Program Studi", "en": "Eligible vs Ineligible by Study Program"},
    "ms.chart_elig_comp": {"id": "Komposisi Kelayakan", "en": "Eligibility Composition"},
    "ms.student_count": {"id": "Jumlah mahasiswa", "en": "Number of students"},
    "ms.no_data_scope": {"id": "Tidak ada data untuk scope ini.", "en": "No data for this scope."},
    "ms.detail_title": {"id": "Detail Mahasiswa", "en": "Student Details"},
    "ms.showing_students": {"id": "Menampilkan {count} mahasiswa.", "en": "Showing {count} students."},
    "ms.matching_title": {"id": "Matching Talent", "en": "Talent Matching"},
    "ms.matching_caption": {
        "id": "Pilih talent request untuk meranking mahasiswa eligible terhadap kebutuhan prodi, semester, dan tools yang diminta.",
        "en": "Select a talent request to rank eligible students against its required study program, semester, and tools.",
    },
    "ms.no_requests": {"id": "Belum ada talent request pada dataset.", "en": "No talent requests found in the dataset."},
    "ms.talent_request": {"id": "Talent request", "en": "Talent request"},
    "ms.detail_request": {"id": "Detail Permintaan", "en": "Request Details"},
    "ms.position": {"id": "Posisi", "en": "Position"},
    "ms.type": {"id": "Jenis", "en": "Type"},
    "ms.headcount": {"id": "Headcount", "en": "Headcount"},
    "ms.min_semester": {"id": "Min. semester", "en": "Min. semester"},
    "ms.field_required": {"id": "Bidang studi dibutuhkan", "en": "Required study field"},
    "ms.requirement": {"id": "Requirement", "en": "Requirement"},
    "ms.no_match": {
        "id": "Tidak ada mahasiswa eligible untuk dicocokkan (longgarkan rule di atas).",
        "en": "No eligible students to match (try loosening the rules above).",
    },
    "ms.candidates_eligible": {"id": "Kandidat eligible", "en": "Eligible candidates"},
    "ms.strong_match": {"id": "Cocok kuat (≥70)", "en": "Strong match (≥70)"},
    "ms.perfect_match": {"id": "Cocok sempurna (100)", "en": "Perfect match (100)"},
    "ms.headcount_requested": {"id": "Headcount diminta", "en": "Headcount requested"},
    "ms.rank_title": {"id": "Peringkat Kandidat", "en": "Candidate Rankings"},

    # monitor company page
    "mc.caption": {
        "id": "Manajemen talent request dan profil perusahaan mitra",
        "en": "Talent request management and partner company profiles",
    },
    "mc.placement_type": {"id": "Jenis Penempatan", "en": "Placement Type"},
    "mc.industry_sector": {"id": "Sektor Industri", "en": "Industry Sector"},
    "mc.company_scale": {"id": "Skala Perusahaan", "en": "Company Scale"},
    "mc.request_progress": {"id": "Progress Permintaan", "en": "Request Progress"},
    "mc.date_range": {"id": "Rentang Tanggal Permintaan", "en": "Request Date Range"},
    "mc.total_requests": {"id": "Total Permintaan", "en": "Total Requests"},
    "mc.total_headcount": {"id": "Total Headcount", "en": "Total Headcount"},
    "mc.candidates_sent": {"id": "Kandidat Dikirim", "en": "Candidates Sent"},
    "mc.fulfillment_rate": {"id": "Tingkat Pemenuhan", "en": "Fulfillment Rate"},
    "mc.avg_response": {"id": "Rata-rata Waktu Respons", "en": "Avg Response Time"},
    "mc.chart_industry": {"id": "Permintaan berdasarkan Sektor Industri", "en": "Requests by Industry Sector"},
    "mc.chart_type_dist": {"id": "Distribusi Jenis Penempatan", "en": "Placement Type Distribution"},
    "mc.chart_monthly": {"id": "Tren Permintaan Bulanan", "en": "Monthly Request Trend"},
    "mc.chart_pipeline": {"id": "Pipeline Progress Permintaan", "en": "Request Progress Pipeline"},
    "mc.chart_top_companies": {"id": "Top 15 Perusahaan berdasarkan Volume Permintaan", "en": "Top 15 Companies by Request Volume"},
    "mc.chart_working_arr": {"id": "Distribusi Working Arrangement", "en": "Working Arrangement Distribution"},
    "mc.detail_title": {"id": "Detail Talent Request", "en": "Talent Request Details"},
    "mc.search_placeholder": {"id": "Ketik nama perusahaan atau posisi", "en": "Type company name or position"},
    "mc.search_label": {"id": "Cari perusahaan atau posisi...", "en": "Search company or position..."},
    "mc.no_data_filter": {"id": "Tidak ada data yang sesuai dengan filter yang dipilih.", "en": "No data matches the selected filters."},
    "mc.number_requests": {"id": "Jumlah Permintaan", "en": "Number of Requests"},
    "mc.request_count": {"id": "Jumlah Request", "en": "Request Count"},
    "mc.total_headcount_req": {"id": "Total Headcount Diminta", "en": "Total Headcount Requested"},
    "mc.count": {"id": "Jumlah", "en": "Count"},
    "mc.month": {"id": "Bulan", "en": "Month"},
    "mc.showing_records": {"id": "Menampilkan {shown} dari {total} record", "en": "Showing {shown} of {total} records"},
    "mc.days": {"id": "hari", "en": "days"},

    # monitor process page
    "mp.caption": {
        "id": "Pemantauan tahapan seleksi dan deteksi ghosting kandidat",
        "en": "Selection stage monitoring and candidate ghosting detection",
    },
    "mp.total_tracked": {"id": "Total Kandidat Terlacak", "en": "Total Candidates Tracked"},
    "mp.active_in_process": {"id": "Aktif dalam Proses", "en": "Active in Process"},
    "mp.total_placement": {"id": "Total Placement", "en": "Total Placements"},
    "mp.total_ghosted": {"id": "Total Ghosting", "en": "Total Ghosted"},
    "mp.stage_dist": {"id": "Distribusi Tahapan", "en": "Stage Distribution"},
    "mp.process_status": {"id": "Status Proses (Aktif vs Selesai)", "en": "Process Status (Active vs Finished)"},
    "mp.candidates": {"id": "Kandidat", "en": "Candidates"},
    "mp.rej_rate_stage": {"id": "Tingkat Penolakan per Tahapan", "en": "Rejection Rate by Stage"},
    "mp.rej_breakdown": {"id": "Rincian Penolakan", "en": "Rejection Breakdown"},
    "mp.rej_rate_pct": {"id": "Tingkat Penolakan (%)", "en": "Rejection Rate (%)"},
    "mp.ghosting_proportion": {"id": "Proporsi Ghosting", "en": "Ghosting Proportion"},
    "mp.fu_severity": {"id": "Tingkat Keparahan Follow-Up", "en": "Follow-Up Severity"},
    "mp.cases": {"id": "Kasus", "en": "Cases"},
    "mp.unified_table": {"id": "Tabel Utama Kandidat", "en": "Unified Master Table"},
    "mp.no_active_data": {"id": "Tidak ada data kandidat aktif.", "en": "No active candidate data."},
    "mp.search_nim": {"id": "Cari (Nama/NIM)", "en": "Search (Name/NIM)"},
    "mp.filter_company": {"id": "Filter Perusahaan", "en": "Filter by Company"},
    "mp.filter_severity": {"id": "Filter Keparahan", "en": "Filter by Severity"},
    "mp.click_row": {"id": "Klik salah satu baris untuk melihat riwayat kandidat selengkapnya.", "en": "Click a row to view the candidate's full history."},
    "mp.student_detail": {"id": "Detail Profil Mahasiswa", "en": "Student Detail Profile"},
    "mp.no_history": {"id": "Kandidat ini belum memiliki riwayat aplikasi.", "en": "This candidate has no application history yet."},
    "mp.no_ghosting_data": {"id": "Tidak ada data ghosting untuk ditampilkan.", "en": "No ghosting data to display."},
    "mp.no_sankey_data": {"id": "Tidak cukup data untuk diagram Sankey.", "en": "Not enough data for the Sankey diagram."},
    "mp.no_tracking": {"id": "Tidak ada data tracking tersedia.", "en": "No tracking data available."},

    # data sync page
    "ds.caption": {
        "id": "Pemeriksaan sinkronisasi data mahasiswa untuk validasi kelengkapan dan kebaruan",
        "en": "Student data synchronization check for completeness and freshness validation",
    },
    "ds.semester": {"id": "Semester", "en": "Semester"},
    "ds.prodi": {"id": "Program Studi", "en": "Study Program"},
    "ds.sync_date_range": {"id": "Rentang Tanggal Sinkronisasi", "en": "Sync Date Range"},
    "ds.no_data": {"id": "Tidak ada data untuk evaluasi sinkronisasi.", "en": "No data available for sync evaluation."},
    "ds.no_data_filter": {"id": "Tidak ada data yang sesuai dengan filter yang dipilih.", "en": "No data matches the selected filters."},
    "ds.earliest_sync": {"id": "Tanggal Sinkronisasi Paling Awal", "en": "Earliest Sync Date"},
    "ds.latest_sync": {"id": "Tanggal Sinkronisasi Terbaru", "en": "Latest Sync Date"},
    "ds.total_students": {"id": "Total Mahasiswa", "en": "Total Students"},
    "ds.critical_sync": {"id": "Sinkronisasi Kritis (>179 hari)", "en": "Critical Sync (>179d)"},
    "ds.mismatched": {"id": "Data Tidak Cocok", "en": "Mismatched Data"},
    "ds.chart_days_sync": {"id": "Hari Sejak Sinkronisasi Terakhir", "en": "Days Since Last Sync"},
    "ds.chart_staleness": {"id": "Distribusi Keusangan", "en": "Staleness Distribution"},
    "ds.days_since_sync": {"id": "Hari Sejak Sinkronisasi", "en": "Days Since Sync"},
    "ds.count_students": {"id": "Jumlah Mahasiswa", "en": "Count of Students"},
    "ds.staleness_note": {
        "id": (
            "**Keterangan Metrik Sinkronisasi:**  \n"
            "**Safe (<90 hari)**: Data rutin disinkronisasi baru-baru ini.  \n"
            "**Stale (90\u2013179 hari)**: Data sudah mulai usang dan belum disinkronisasi dalam waktu yang cukup lama.  \n"
            "**Critical (>179 hari)**: Data sudah tidak disinkronisasi lebih dari 1 semester dan berisiko kehilangan relevansi."
        ),
        "en": (
            "**Sync Metric Definitions:**  \n"
            "**Safe (<90 days)**: Data was recently synchronized.  \n"
            "**Stale (90\u2013179 days)**: Data is becoming outdated and hasn't been synced for a while.  \n"
            "**Critical (>179 days)**: Data hasn't been synced for over 1 semester and may lose relevance."
        ),
    },
    "ds.chart_monthly_sync": {"id": "Volume Sinkronisasi Bulanan", "en": "Monthly Sync Volume"},
    "ds.syncs": {"id": "Jumlah Sinkronisasi", "en": "Number of Syncs"},
    "ds.chart_sem_staleness": {"id": "Keusangan per Semester", "en": "Staleness by Semester"},
    "ds.chart_prodi_staleness": {"id": "Keusangan per Program Studi", "en": "Staleness by Study Program"},
    "ds.students": {"id": "Mahasiswa", "en": "Students"},
    "ds.master_table": {"id": "Tabel Utama Kualitas Data", "en": "Master Quality Data"},
    "ds.filter_staleness": {"id": "Filter Keusangan", "en": "Filter by Staleness"},
    "ds.show_mismatch": {"id": "Tampilkan hanya data yang tidak cocok", "en": "Show only records with mismatched data"},
    "ds.showing_records": {"id": "Menampilkan {shown} dari {total} total record", "en": "Showing {shown} of {total} total records"},

    # sidebar
    "sidebar.data_source": {"id": "Sumber Data", "en": "Data Source"},
    "sidebar.tables": {"id": "Tabel", "en": "Tables"},
    "sidebar.storage": {"id": "Penyimpanan", "en": "Storage"},
    "sidebar.sync": {"id": "Sinkronisasi", "en": "Sync"},
    "sidebar.auto": {"id": "Otomatis", "en": "Auto"},
    "sidebar.mode_light": {"id": "Light", "en": "Light"},
    "sidebar.mode_dark": {"id": "Dark", "en": "Dark"},

    # pdf report
    "pdf.title": {"id": "Laporan Periodik Placement Mahasiswa", "en": "Student Placement Periodic Report"},
    "pdf.generated": {"id": "Dibuat pada", "en": "Generated on"},
    "pdf.exec_summary": {"id": "Ringkasan Utama", "en": "Main Summary"},
    "pdf.student_analysis": {"id": "Analisis Kelayakan Mahasiswa", "en": "Student Eligibility Analysis"},
    "pdf.company_analysis": {"id": "Analisis Permintaan Perusahaan", "en": "Company Request Analysis"},
    "pdf.process_analysis": {"id": "Analisis Proses Seleksi", "en": "Selection Process Analysis"},
    "pdf.data_quality": {"id": "Analisis Kualitas Data", "en": "Data Quality Analysis"},
    "pdf.closing": {"id": "Penutup", "en": "Closing"},
}


def get_lang() -> str:
    # return the currently active language code from session state
    return st.session_state.get("lang", DEFAULT_LANG)


def set_lang(lang: str):
    # set the active language code in session state
    st.session_state["lang"] = lang


def t(key: str, **kwargs) -> str:
    # translate a key to the current language with optional format kwargs
    lang = get_lang()
    entry = _TRANSLATIONS.get(key, {})
    text = entry.get(lang, entry.get(DEFAULT_LANG, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
