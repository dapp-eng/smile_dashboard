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
        "id": "Rekapitulasi placement per semester, prodi, perusahaan, dan jenis penempatan.",
        "en": "Placement recapitulation by semester, study program, company, and placement type.",
    },
    "bt.06": {
        "id": "Validasi kesiapan dan kelayakan mahasiswa berdasarkan CV, portofolio, IPK, dan status.",
        "en": "Student readiness and eligibility validation based on CV, portfolio, GPA, and status.",
    },
    "bt.01": {
        "id": "Pencocokan mahasiswa dengan kebutuhan perusahaan berdasarkan prodi, semester, dan tools.",
        "en": "Student matching with company needs based on study program, semester, and tools.",
    },
    "bt.01_06": {
        "id": "Evaluasi kelayakan mahasiswa dan pencocokan talent dengan kebutuhan perusahaan.",
        "en": "Student eligibility evaluation and talent matching with company needs.",
    },
    "bt.03": {
        "id": "Pengelolaan permintaan talent berdasarkan tanggal, headcount, dan jenis penempatan.",
        "en": "Talent request management based on date, headcount, and placement type.",
    },
    "bt.04": {
        "id": "Analisis tingkat keberhasilan placement dan identifikasi perusahaan mitra terbaik.",
        "en": "Placement success rate analysis and top company partner identification.",
    },
    "bt.03_04": {
        "id": "Manajemen permintaan talent dan analisis tingkat keberhasilan mitra perusahaan.",
        "en": "Talent request management and partner company success rate analysis.",
    },
    "bt.02": {
        "id": "Pemantauan real-time setiap tahapan progress seleksi mahasiswa.",
        "en": "Real-time selection progress monitoring across all stages.",
    },
    "bt.05": {
        "id": "Deteksi otomatis inaktivitas/ghosting kandidat untuk tindakan follow-up.",
        "en": "Automatic candidate ghosting detection for timely follow-up action.",
    },
    "bt.02_05": {
        "id": "Pemantauan progress tahapan seleksi real-time dan deteksi ghosting kandidat.",
        "en": "Real-time selection progress monitoring and candidate ghosting detection.",
    },
    "bt.08": {
        "id": "Sinkronisasi dan validasi data antara Student All dan Status Student.",
        "en": "Data synchronization and validation between Student All and Status Student.",
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
    "ms.chart_elig_prodi_sub": {"id": "Perbandingan jumlah mahasiswa yang memenuhi syarat per program studi", "en": "Comparison of eligible students per study program"},
    "ms.chart_elig_comp": {"id": "Komposisi Kelayakan", "en": "Eligibility Composition"},
    "ms.chart_elig_comp_sub": {"id": "Persentase keseluruhan mahasiswa yang memenuhi syarat", "en": "Overall percentage of eligible students"},
    "ms.student_count": {"id": "Jumlah mahasiswa", "en": "Number of students"},
    "ms.no_data_scope": {"id": "Tidak ada data untuk scope ini.", "en": "No data for this scope."},
    "ms.detail_title": {"id": "Detail Mahasiswa", "en": "Student Details"},
    "ms.detail_title_sub": {"id": "Daftar lengkap status kelayakan mahasiswa", "en": "Complete list of student eligibility status"},
    "ms.showing_students": {"id": "Menampilkan {count} mahasiswa.", "en": "Showing {count} students."},
    "ms.matching_title": {"id": "Matching Talent", "en": "Talent Matching"},
    "ms.matching_caption": {
        "id": "Pilih talent request untuk meranking mahasiswa eligible terhadap kebutuhan prodi, semester, dan tools yang diminta.",
        "en": "Select a talent request to rank eligible students against its required study program, semester, and tools.",
    },
    "ms.matching_kpi_title": {"id": "Ringkasan Pencocokan", "en": "Matching Overview"},
    "ms.matching_kpi_sub": {"id": "Ringkasan jumlah kandidat eligible terhadap kebutuhan headcount", "en": "Overview of eligible candidates against requested headcount"},
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
    "ms.rank_title_sub": {"id": "Hasil pencocokan mahasiswa berdasarkan kriteria yang dipilih", "en": "Student matching results based on selected criteria"},
    "ms.profiling_section": {"id": "Profil Mahasiswa", "en": "Student Profiling"},
    "ms.profiling_caption": {"id": "Ringkasan demografi dan keahlian seluruh talenta di sistem", "en": "Overview of demographics and skills for all talents in the system"},
    "ms.chart_interest": {"id": "Bidang Minat", "en": "Field of Interest"},
    "ms.chart_interest_sub": {"id": "Minat utama mahasiswa", "en": "Primary student interests"},
    "ms.chart_placement_pref": {"id": "Preferensi Penempatan", "en": "Placement Preference"},
    "ms.chart_placement_pref_sub": {"id": "Jenis penempatan yang diinginkan", "en": "Desired placement types"},
    "ms.chart_prodi_dist": {"id": "Sebaran Program Studi", "en": "Study Program Distribution"},
    "ms.chart_prodi_dist_sub": {"id": "Distribusi mahasiswa berdasarkan program studi", "en": "Student distribution by study program"},
    "ms.chart_semester": {"id": "Sebaran Semester", "en": "Semester Distribution"},
    "ms.chart_semester_sub": {"id": "Distribusi tingkat semester mahasiswa", "en": "Distribution of student semester levels"},
    "ms.chart_tools": {"id": "Keahlian & Tools Terpopuler", "en": "Most Popular Skills & Tools"},
    "ms.chart_tools_sub": {"id": "Tools yang paling banyak dikuasai mahasiswa", "en": "Most commonly mastered tools by students"},

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
    "mc.chart_industry_sub": {"id": "Distribusi permintaan talent berdasarkan sektor industri", "en": "Talent request distribution by industry sector"},
    "mc.chart_type_dist": {"id": "Distribusi Jenis Penempatan", "en": "Placement Type Distribution"},
    "mc.chart_type_dist_sub": {"id": "Komposisi jenis penempatan yang ditawarkan", "en": "Composition of offered placement types"},
    "mc.chart_monthly": {"id": "Tren Permintaan Bulanan", "en": "Monthly Request Trend"},
    "mc.chart_monthly_sub": {"id": "Volume permintaan talent dari waktu ke waktu", "en": "Talent request volume over time"},
    "mc.chart_pipeline": {"id": "Pipeline Progress Permintaan", "en": "Request Progress Pipeline"},
    "mc.chart_pipeline_sub": {"id": "Status penyelesaian seluruh talent request saat ini", "en": "Current completion status of all talent requests"},
    "mc.chart_top_companies": {"id": "Top 10 Perusahaan berdasarkan Volume Permintaan", "en": "Top 10 Companies by Request Volume"},
    "mc.chart_top_companies_sub": {"id": "Perusahaan dengan jumlah permintaan talent terbanyak", "en": "Companies with the highest number of talent requests"},
    "mc.chart_working_arr": {"id": "Distribusi Working Arrangement", "en": "Working Arrangement Distribution"},
    "mc.chart_working_arr_sub": {"id": "Komposisi model kerja (WFO, WFH, Hybrid)", "en": "Working arrangement composition (WFO, WFH, Hybrid)"},
    "mc.chart_company_type": {"id": "Distribusi Jenis Perusahaan", "en": "Company Type Distribution"},
    "mc.chart_company_type_sub": {"id": "Komposisi jenis perusahaan (Startup, Korporasi, dll)", "en": "Composition of company types (Startup, Corporate, etc)"},
    "mc.chart_sumber_form": {"id": "Sumber Form Permintaan", "en": "Request Form Source"},
    "mc.chart_sumber_form_sub": {"id": "Platform asal pengajuan talent request", "en": "Origin platform of talent requests"},
    "mc.chart_prodi_demand": {"id": "Kebutuhan Program Studi", "en": "Study Program Demand"},
    "mc.chart_prodi_demand_sub": {"id": "Program studi yang paling sering diminta oleh perusahaan", "en": "Most frequently requested study programs"},
    "mc.chart_tools_demand": {"id": "Kebutuhan Tools & Keahlian", "en": "Tools & Skills Demand"},
    "mc.chart_tools_demand_sub": {"id": "Tools yang paling sering muncul dalam deskripsi requirement", "en": "Most frequent tools in requirement descriptions"},
    "mc.chart_remuneration": {"id": "Tipe Remunerasi", "en": "Remuneration Type"},
    "mc.chart_remuneration_sub": {"id": "Proporsi permintaan Paid, Uang Transport, dan Non-Paid", "en": "Proportion of Paid, Transport-only, and Non-Paid requests"},
    "mc.chart_salary_dist": {"id": "Distribusi Gaji Ditawarkan", "en": "Offered Salary Distribution"},
    "mc.chart_salary_dist_sub": {"id": "Sebaran nilai nominal remunerasi (Rp)", "en": "Distribution of nominal remuneration values (Rp)"},
    "mc.chart_salary_avg": {"id": "Rata-rata Gaji per Kategori", "en": "Average Salary by Category"},
    "mc.chart_salary_avg_sub": {"id": "Rata-rata gaji tertinggi berdasarkan program studi atau tools", "en": "Highest average salary by study program or tools"},
    "mc.chart_company_scale": {"id": "Distribusi Skala Perusahaan", "en": "Company Scale Distribution"},
    "mc.chart_company_scale_sub": {"id": "Komposisi skala bisnis mitra perusahaan", "en": "Composition of partner company business scale"},
    "mc.chart_duration": {"id": "Distribusi Durasi Program", "en": "Program Duration Distribution"},
    "mc.chart_duration_sub": {"id": "Komposisi durasi penempatan (dalam bulan)", "en": "Composition of placement durations (in months)"},
    "mc.top10_placement": {"id": "10 Perusahaan Teratas Penempatan Terbanyak", "en": "Top 10 Companies with Highest Placement"},
    "mc.top10_placement_sub": {
        "id": "Perusahaan diurutkan berdasarkan volume dan tingkat penempatan (Placement) tertinggi",
        "en": "Companies ranked by highest combined placement volume and rate",
    },
    "mc.top10_rejection": {"id": "10 Perusahaan Teratas Penolakan Terbanyak", "en": "Top 10 Companies with Highest Rejection"},
    "mc.top10_rejection_sub": {
        "id": "Perusahaan diurutkan berdasarkan volume dan tingkat penolakan tertinggi",
        "en": "Companies ranked by highest combined rejection volume and rate",
    },
    "mc.detail_title": {"id": "Detail Talent Request", "en": "Talent Request Details"},
    "mc.detail_title_sub": {"id": "Daftar lengkap seluruh talent request beserta statusnya", "en": "Complete list of all talent requests and their status"},
    "mc.demographics_volume_title": {"id": "Demografi & Volume Perusahaan", "en": "Company Demographics & Volume"},
    "mc.demographics_volume_sub": {"id": "Ringkasan industri, jenis, skala, dan volume permintaan", "en": "Overview of industry, type, scale, and request volume"},
    "mc.trend_ops_title": {"id": "Tren & Ikhtisar Operasional", "en": "Trend & Operations Overview"},
    "mc.trend_ops_sub": {"id": "Analisis waktu permintaan, sumber form, dan progress pipeline", "en": "Analysis of request timing, form sources, and pipeline progress"},
    "mc.characteristics_title": {"id": "Karakteristik & Kebutuhan Talent", "en": "Talent Characteristics & Demand"},
    "mc.characteristics_sub": {"id": "Rincian model kerja, durasi, program studi, dan tools yang dibutuhkan", "en": "Breakdown of working models, duration, study programs, and required tools"},
    "mc.salary_analysis_title": {"id": "Analisis Gaji & Remunerasi", "en": "Salary & Remuneration Analysis"},
    "mc.salary_analysis_sub": {"id": "Sebaran remunerasi, distribusi gaji, dan rata-rata berdasarkan kategori", "en": "Remuneration spread, salary distribution, and averages by category"},
    "mc.performance_leaderboard_title": {"id": "Leaderboard Kinerja Mitra", "en": "Partner Performance Leaderboard"},
    "mc.performance_leaderboard_sub": {"id": "Performa penempatan dan penolakan tertinggi dari mitra perusahaan", "en": "Highest placement and rejection performance from partner companies"},
    "mc.search_placeholder": {"id": "Ketik nama perusahaan atau posisi", "en": "Type company name or position"},
    "mc.search_label": {"id": "Cari perusahaan atau posisi...", "en": "Search company or position..."},
    "mc.no_data_filter": {"id": "Tidak ada data yang sesuai dengan filter yang dipilih.", "en": "No data matches the selected filters."},
    "mc.number_requests": {"id": "Jumlah Permintaan", "en": "Number of Requests"},
    "mc.request_count": {"id": "Jumlah Request", "en": "Request Count"},
    "mc.total_headcount_req": {"id": "Total Headcount Diminta", "en": "Total Headcount Requested"},
    "mc.count": {"id": "Jumlah", "en": "Count"},
    "mc.month": {"id": "Bulan", "en": "Month"},
    "mc.company": {"id": "Perusahaan", "en": "Company"},
    "mc.showing_records": {"id": "Menampilkan {shown} dari {total} record", "en": "Showing {shown} of {total} records"},
    "mc.days": {"id": "hari", "en": "days"},

    # monitor process page
    "mp.caption": {
        "id": "Pemantauan tahapan seleksi dan deteksi ghosting kandidat",
        "en": "Selection stage monitoring and candidate ghosting detection",
    },
    "mp.total_tracked": {"id": "Total Aplikasi Terlacak", "en": "Total Applications Tracked"},
    "mp.active_in_process": {"id": "Aplikasi Aktif (Diproses)", "en": "Active Applications"},
    "mp.total_placement": {"id": "Aplikasi Berhasil (Placement)", "en": "Successful Applications (Placed)"},
    "mp.total_ghosted": {"id": "Aplikasi Ghosting", "en": "Ghosted Applications"},
    "mp.stage_dist": {"id": "Distribusi Tahapan", "en": "Stage Distribution"},
    "mp.process_status": {"id": "Status Proses (Aktif vs Selesai)", "en": "Process Status (Active vs Finished)"},
    "mp.candidates": {"id": "Kandidat", "en": "Candidates"},
    "mp.rej_rate_stage": {"id": "Tingkat Penolakan per Tahapan", "en": "Rejection Rate by Stage"},
    "mp.rej_breakdown": {"id": "Rincian Penolakan", "en": "Rejection Breakdown"},
    "mp.rej_rate_pct": {"id": "Tingkat Penolakan (%)", "en": "Rejection Rate (%)"},
    "mp.ghosting_proportion": {"id": "Proporsi Ghosting", "en": "Ghosting Proportion"},
    "mp.fu_severity": {"id": "Tingkat Keparahan Follow-Up", "en": "Follow-Up Severity"},
    "mp.cases": {"id": "Kasus", "en": "Cases"},
    "mp.unified_table": {"id": "Master Table Mahasiswa", "en": "Student Master Table"},
    "mp.no_active_data": {"id": "Tidak ada data kandidat aktif.", "en": "No active candidate data."},
    "mp.search_nim": {"id": "Cari (Nama/NIM)", "en": "Search (Name/NIM)"},
    "mp.filter_company": {"id": "Filter Perusahaan", "en": "Filter by Company"},
    "mp.filter_severity": {"id": "Filter Keparahan", "en": "Filter by Severity"},
    "mp.filter_prodi": {"id": "Filter Program Studi", "en": "Filter by Program"},
    "mp.filter_has_fu": {"id": "Filter Follow-Up", "en": "Filter by Follow-Up"},
    "mp.col_name": {"id": "Nama", "en": "Name"},
    "mp.col_prodi": {"id": "Program Studi", "en": "Program"},
    "mp.col_semester": {"id": "Semester", "en": "Semester"},
    "mp.col_interest": {"id": "Bidang Minat", "en": "Interest"},
    "mp.col_placement_type": {"id": "Jenis Penempatan", "en": "Placement Type"},
    "mp.col_applications": {"id": "Jumlah Lamaran", "en": "Applications"},
    "mp.col_has_fu": {"id": "Butuh Follow-Up?", "en": "Need Follow-Up?"},
    "mp.click_row": {"id": "Klik salah satu baris untuk melihat riwayat kandidat selengkapnya.", "en": "Click a row to view the candidate's full history."},
    "mp.student_detail": {"id": "Detail Profil Mahasiswa", "en": "Student Detail Profile"},
    "mp.no_history": {"id": "Kandidat ini belum memiliki riwayat aplikasi.", "en": "This candidate has no application history yet."},
    "mp.no_ghosting_data": {"id": "Tidak ada data ghosting untuk ditampilkan.", "en": "No ghosting data to display."},
    "mp.no_sankey_data": {"id": "Tidak cukup data untuk diagram Sankey.", "en": "Not enough data for the Sankey diagram."},
    "mp.no_tracking": {"id": "Tidak ada data tracking tersedia.", "en": "No tracking data available."},
    # --- section headers (new, not in incoming) ---
    "mp.status_overview_title": {"id": "Ringkasan Status Kandidat", "en": "Candidate Status Overview"},
    "mp.status_overview_sub": {
        "id": "Posisi setiap kandidat saat ini",
        "en": "Where every candidate stands right now",
    },
    "mp.rejection_pipeline_title": {"id": "Analisis Penolakan & Pipeline", "en": "Rejection & Pipeline Analysis"},
    "mp.rejection_pipeline_sub": {
        "id": "Rincian di mana kandidat gugur dari proses",
        "en": "Detailed breakdown of where candidates fall out of the process",
    },
    "mp.ghosting_detection_title": {"id": "Ghosting & Deteksi Sistem", "en": "Ghosting & System Detection"},
    "mp.ghosting_detection_sub": {
        "id": "Dampak pelacakan otomatis vs pelabelan manual",
        "en": "Impact of automated tracking vs manual labeling",
    },
    "mp.student_tracker_title": {"id": "Pelacak Mahasiswa Individual", "en": "Individual Student Tracker"},
    "mp.student_tracker_sub": {
        "id": "Cari dan filter pipeline kandidat secara individual",
        "en": "Search and filter individual candidate pipelines",
    },

    # --- subtitles for existing chart_panel titles ---
    "mp.stage_dist_sub": {
        "id": "Telusuri status apa pun untuk melihat rinciannya per tahapan",
        "en": "Drill into any status to see its stage-by-stage breakdown",
    },
    "mp.process_status_sub": {
        "id": "Rincian kandidat berdasarkan proses dan tahapan",
        "en": "Candidate breakdown by process and stage",
    },
    "mp.rej_rate_stage_sub": {
        "id": "Persentase kandidat yang ditolak pada setiap tahapan",
        "en": "Percentage of candidates rejected at each stage",
    },

    # --- new charts (no prior key at all) ---
    "mp.pipeline_flow": {"id": "Alur Pipeline", "en": "Pipeline Flow"},
    "mp.pipeline_flow_sub": {
        "id": "Volume kandidat yang masuk dan gugur di setiap tahapan",
        "en": "Volume of candidates entering and falling out of each stage",
    },

    "mp.sankey_title": {"id": "Alur Eskalasi Sistem", "en": "System Escalation Flow"},
    "mp.sankey_sub": {
        "id": "Perubahan status dari Label CDC menjadi Deteksi Sistem",
        "en": "Status transition from CDC Label to System Detection",
    },
    "mp.system_detection_impact": {"id": "Dampak Deteksi Sistem", "en": "System Detection Impact"},
    "mp.system_detection_impact_sub": {
        "id": "Perbandingan flag ghosting dari CDC vs Sistem",
        "en": "Comparison of ghosting flags raised by CDC vs System",
    },
    "mp.top10_ghosting": {"id": "10 Perusahaan Teratas berdasarkan Dampak Ghosting", "en": "Top 10 Companies by Ghosting Impact"},
    "mp.top10_ghosting_sub": {
        "id": "Perusahaan diurutkan berdasarkan volume dan tingkat ghosting tertinggi",
        "en": "Companies ranked by highest combined ghosting volume and rate",
    },
    "mp.cdc_labeled": {"id": "Label CDC", "en": "CDC Labeled"},
    "mp.system_detected": {"id": "Deteksi Sistem", "en": "System Detected"},
    "mp.system_corrected": {"id": "Koreksi Sistem", "en": "System Corrected"},

    # --- small labels / empty-state messages ---
    "mp.stage_cat_filter": {"id": "Filter Kategori", "en": "Category Filter"},
    "mp.no_waterfall_data": {"id": "Tidak ada data untuk membuat grafik Waterfall.", "en": "No data available to construct Waterfall chart."},
    "mp.no_rejection_data": {"id": "Tidak ada data penolakan untuk ditampilkan.", "en": "No rejection data to display."},
    "mp.no_valid_lag_data": {"id": "Tidak ada data tanggal valid untuk ghosting yang dikonfirmasi.", "en": "No valid date data for confirmed ghosting."},
    "mp.no_confirmed_ghosting": {"id": "Tidak ada kasus Ghosting yang dikonfirmasi.", "en": "No confirmed Ghosting cases available."},

    "mp.stage_codes_caption": {
        "id": (
            "**Kode Tahapan:** S0 (Screening CV), S1 (Seleksi Mahasiswa), S2 (Studi Kasus), "
            "S3 (Briefing CDC), S4 (Interview User), S5 (Interview Final). "
            "**Awalan 'R.' pada Sunburst** menandakan Penolakan pada tahap tersebut."
        ),
        "en": (
            "**Stage Codes:** S0 (CV Screening), S1 (Selecting Student), S2 (Study Case), "
            "S3 (CDC Briefing), S4 (Interview User), S5 (Final Interview). "
            "**'R.' prefix in Sunburst** denotes Rejection at that stage."
        ),
    },
    "mp.stage_codes_caption_short": {
        "id": (
            "**Kode Tahapan:** S0 (Screening CV), S1 (Seleksi Mahasiswa), S2 (Studi Kasus), "
            "S3 (Briefing CDC), S4 (Interview User), S5 (Interview Final)."
        ),
        "en": (
            "**Stage Codes:** S0 (CV Screening), S1 (Selecting Student), S2 (Study Case), "
            "S3 (CDC Briefing), S4 (Interview User), S5 (Final Interview)."
        ),
    },
    "mp.resolved_candidates": {"id": "Kandidat Tuntas", "en": "Resolved Candidates"},
    "mp.wf_ghosting": {"id": "Ghosting", "en": "Ghosting"},
    "mp.wf_rejected": {"id": "Ditolak<br>{stage}", "en": "Rejected<br>{stage}"},
    "mp.wf_placement": {"id": "Penempatan", "en": "Placement"},
    "mp.stage_cat_filter": {"id": "Filter Kategori", "en": "Category Filter"},
    "mp.cat_all": {"id": "Semua", "en": "All"},
    "mp.cat_active": {"id": "Aktif", "en": "Active"},
    "mp.cat_followup": {"id": "Follow-Up", "en": "Follow-Up"},
    "mp.cat_finished": {"id": "Selesai", "en": "Finished"},
    "mp.cat_rejected": {"id": "Ditolak", "en": "Rejected"},
    "mp.stages": {"id": "Tahapan", "en": "Stages"},
    "mp.impact_score_axis": {"id": "Skor Dampak (0-100)", "en": "Impact Score (0-100)"},
    "mp.lag_in_days": {"id": "Selisih Hari", "en": "Lag in Days"},
    "mp.unified_table_sub": {
        "id": "Tabel gabungan seluruh kandidat yang sedang dilacak beserta status ghosting-nya",
        "en": "Combined table of all tracked candidates and their ghosting status",
    },

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
    "ds.chart_sem_staleness": {"id": "Keusangan Data per Semester", "en": "Staleness by Semester"},
    "ds.chart_prodi_staleness": {"id": "Keusangan Data per Program Studi", "en": "Staleness by Study Program"},
    "ds.students": {"id": "Mahasiswa", "en": "Students"},
    "ds.master_table": {"id": "Tabel Utama Kualitas Data", "en": "Master Quality Data"},
    "ds.filter_staleness": {"id": "Filter Keusangan", "en": "Filter by Staleness"},
    "ds.show_mismatch": {"id": "Tampilkan hanya data yang tidak cocok", "en": "Show only records with mismatched data"},
    "ds.showing_records": {"id": "Menampilkan {shown} dari {total} total record", "en": "Showing {shown} of {total} total records"},

    "ds.section1_title": {"id": "Overview Sinkronisasi Data", "en": "Data Synchronization Overview"},
    "ds.section1_sub": {"id": "Status kebaruan dan kualitas data mahasiswa", "en": "Freshness and quality status of student data"},
    "ds.section2_title": {"id": "Reklasifikasi Status Finish", "en": "Finish Status Reclassification"},
    "ds.section2_sub": {"id": "Data mentah menggunakan status 'Finish' secara umum. Kami mereklasifikasi data ini menggunakan kolom 'rejection' untuk menampilkan hasil yang sebenarnya.", "en": "The raw data used 'Finish' as a catch-all close-out status. We reclassify these records using the 'rejection' column to reveal the true outcome."},
    "ds.chart_days_sync_sub": {"id": "Distribusi hari sejak pembaruan terakhir", "en": "Distribution of days since last update"},
    "ds.chart_staleness_sub": {"id": "Proporsi data berdasarkan tingkat kebaruan", "en": "Proportion of data by freshness level"},
    "ds.chart_monthly_sync_sub": {"id": "Volume sinkronisasi data per bulan", "en": "Data synchronization volume per month"},
    "ds.chart_sem_staleness_sub": {"id": "Tingkat kebaruan data per semester", "en": "Data freshness level per semester"},
    "ds.chart_prodi_staleness_sub": {"id": "Tingkat kebaruan data per program studi", "en": "Data freshness level per study program"},
    "ds.master_table_sub": {"id": "Data detail kualitas mahasiswa", "en": "Detailed student quality data"},
    "ds.chart_orig_rej": {"id": "Nilai Rejection Asli", "en": "Original Rejection Values"},
    "ds.chart_orig_rej_sub": {"id": "Nilai asli dari kolom rejection untuk status 'Finish'", "en": "What the rejection column actually said for 'Finish' records"},
    "ds.chart_reclass": {"id": "Alur Reklasifikasi", "en": "Reclassification Flow"},
    "ds.chart_reclass_sub": {"id": "Bagaimana status 'Finish' dipetakan ke hasil sebenarnya", "en": "How 'Finish' records were remapped to their true outcomes"},

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
