# SMILE - Student Placement Management System

SMILE (Student Placement Management System) adalah platform dashboard analitik berbasis Streamlit yang dirancang untuk Career Development Center (CDC) dalam mengelola, memantau, dan mengoptimalkan seluruh siklus penempatan mahasiswa (magang, part-time, maupun full-time).

---

## 📌 Deskripsi Business Task (BT)

Sistem ini memetakan dan mengimplementasikan seluruh kebutuhan bisnis **BT-01 hingga BT-08** secara menyeluruh:

- **BT-01 (Talent Matching)**: Algoritma scoring untuk mencocokkan mahasiswa eligible dengan permintaan perusahaan berdasarkan prodi, semester, dan requirement tools.
- **BT-02 (Selection Progress Monitoring)**: Pemantauan real-time setiap tahapan seleksi mahasiswa (Screening, Study Case, Interview User, Final Interview, hingga Placement).
- **BT-03 (Talent Request Management)**: Pengelolaan dan pemfilteran permintaan talent dari mitra perusahaan berdasarkan headcount, jenis penempatan, sektor industri, dan timeline.
- **BT-04 (Success Rate & Placement Analysis)**: Mengukur tingkat pemenuhan placement (fulfillment rate) dan tingkat penerimaan kandidat di perusahaan mitra.
- **BT-05 (Ghosting Detection & Follow-up)**: Deteksi otomatis mahasiswa/perusahaan yang tidak aktif merespons (inaktif > 7/14/21/28 hari) untuk memicu tindakan follow-up.
- **BT-06 (Student Eligibility Validation)**: Pengujian kelayakan mahasiswa berdasarkan ketersediaan CV, portofolio, status aktif, status ketersediaan, dan ambang batas IPK minimum.
- **BT-07 (Periodic Reporting & Export PDF)**: Halaman Overview terpadu dengan KPI institusi dan fitur ekspor Laporan Periodik PDF dengan interpretasi analitis bahasa alami.
- **BT-08 (Data Quality)**: Pemantauan kebaruan sinkronisasi data (staleness), reklasifikasi status finish, serta deteksi ketidakcocokan atribut (mismatch) antara master data dan data status.

---

## 🎨 Fitur Utama Aplikasi

1. **Overview & Fitur Download PDF Report (BT-07)**
   - Rangkuman KPI Utama (Total Mahasiswa, Perusahaan, Permintaan, Placement, Ghosting Rate, dan Eligibility Rate).
   - Visualisasi distribusi jenis penempatan, tren bulanan, top perusahaan, dan placement per prodi.
   - Generator Laporan PDF periodik otomatis.

2. **Monitor Student (BT-06 & BT-01)**
   - Filter kriteria kelayakan mahasiswa dinamis (IPK, CV, Portofolio, Status, Ketersediaan).
   - Visualisasi rasio kelayakan per program studi.
   - Fitur Talent Matching interaktif untuk memberi skor kandidat terhadap spesifikasi Talent Request tertentu.

3. **Monitor Company (BT-03 & BT-04)**
   - Monitoring volume permintaan berdasarkan sektor industri, skala bisnis, working arrangement, dan pipeline progres.
   - Analisis keberhasilan penempatan kandidat per perusahaan mitra.

4. **Monitor Process (BT-02 & BT-05)**
   - Rangkuman KPI Utama (Total Aplikasi Terlacak, Aplikasi Aktif, Placement, **Aplikasi Butuh Follow-Up**, dan **Aplikasi Ghosting** murni).
   - Visualisasi distribusi tahapan seleksi, status proses, analisis penolakan per tahapan (rejection rate), dan Waterfall Chart alur pipeline.
   - Sankey Diagram Alur Eskalasi Sistem (transisi status dari Label CDC ke Deteksi Otomatis Sistem).
   - Visualisasi dampak deteksi sistem (Sunburst) dan Top 10 Perusahaan berdasarkan dampak ghosting.
   - Master Table Mahasiswa (Individual Student Tracker) dengan filter interaktif dan drill-down detail histori aplikasi lengkap.

5. **Monitor Request (BT-03 Request Analytics)**
   - Analisis karakteristik permintaan talent (distribusi jenis penempatan, working arrangement, durasi, dan sumber form).
   - Analisis kebutuhan spesifik pasar (demam prodi & tools yang paling banyak diminta).
   - Analisis remunerasi/gaji (kategori paid/non-paid, distribusi nominal gaji, dan rata-rata gaji per prodi/tools).
   - Matriks prioritas penanganan permintaan talent (scoring prioritas berdasarkan umur request, headcount gap, status progress, dan jenis penempatan).

6. **Data Quality (BT-08)**
   - Analisis tingkat keusangan data (*Safe*, *Stale*, *Critical*) berdasarkan tanggal sinkronisasi terakhir.
   - Reklasifikasi status 'Finish' secara otomatis menggunakan kolom `rejection` untuk mengungkap hasil aktual kandidat (Placement, Ghosting, Rejected, Unresolved).
   - Deteksi ketidakcocokan field (Nama, Email, Semester, Phone, Prodi) antara dataset `STUDENT ALL` dan `STATUS STUDENT`.

7. **Pengoperasian Mode Tampilan & Multi-Bahasa**
   - **Switch Mode (Light / Dark)**: Penyesuaian tema visual otomatis.
   - **Multi-Language (ID / EN)**: Dukungan Bahasa Indonesia dan Bahasa Inggris untuk seluruh label, metrik, dan judul section.

---

## 📂 Struktur Direktori Proyek

```text
SSDC_SMILE/
├── .streamlit/
│   └── config.toml          # Konfigurasi Streamlit theme
├── assets/
│   ├── smile-b1.png         # Logo varian Black 1 (Header PDF Cover)
│   ├── smile-b2.png         # Logo varian Black 2 (App Icon & Light Mode Collapsed)
│   ├── smile-w2.png         # Logo varian White 2 (Dark Mode Collapsed)
│   └── smile-w3.png         # Logo varian White 3 (Sidebar Expanded)
├── data/                    # Direktori penyimpanan file CSV lokal / terunduh
├── pages/
│   ├── 1_monitor_student.py # Halaman Monitor Mahasiswa (BT-06 & BT-01)
│   ├── 2_monitor_company.py # Halaman Monitor Perusahaan (BT-03 & BT-04)
│   ├── 3_monitor_process.py # Halaman Monitor Proses (BT-02 & BT-05)
│   ├── 4_data_quality.py    # Halaman Kualitas Data (BT-08)
│   └── 5_monitor_request.py # Halaman Monitor Request (BT-03 Request Analytics)
├── utils/
│   ├── charts.py            # Utility pembentuk chart Plotly
│   ├── data_loader.py       # Pemuat data CSV & integrasi client Supabase
│   ├── i18n.py              # Modul terjemahan multi-bahasa (ID/EN)
│   ├── layout.py            # Injeksi CSS global, theme switcher, & komponen layout
│   ├── metrics.py           # Logika perhitungan metrik bisnis (BT-01 s.d. BT-08)
│   ├── pdf_report.py        # Generator laporan periodik berbasis PDF (fpdf2 & Matplotlib)
│   ├── queries.py           # Interface pembacaan query data
│   ├── supabase_client.py   # Client Supabase untuk operasi live CRUD
│   ├── theme.py             # Palette warna dan styling Plotly
│   └── validator.py         # Utility validasi input data
├── .gitignore
├── app.py                   # Entry point aplikasi & Halaman Overview (BT-07)
├── requirements.txt         # Daftar pustaka dependency Python
└── README.md                # Dokumentasi proyek
```

---

## 🛠️ Panduan Instalasi dan Memulai

### 1. Prasyarat
- Python 3.10 atau versi yang lebih baru.
- Virtual environment (disarankan).

### 2. Kloning & Instalasi Dependency
```bash
# Pindah ke direktori proyek
cd SSDC_SMILE

# Buat virtual environment (opsional)
python -m venv .venv
# Aktivasi pada Windows Command Prompt / PowerShell:
.venv\Scripts\activate

# Install pustaka yang dibutuhkan
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi
```bash
streamlit run app.py
```
Aplikasi akan secara otomatis terbuka di browser pada alamat `http://localhost:8501`.

---

## 🛠️ Tech Stack
- **Framework UI**: [Streamlit](https://streamlit.io/)
- **Visualisasi Data**: [Plotly Express & Graph Objects](https://plotly.com/python/) & [Matplotlib](https://matplotlib.org/)
- **Pengolahan Data**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **PDF Generation**: [fpdf2](https://pyfpdf.github.io/fpdf2/) & [Matplotlib Engine](https://matplotlib.org/)
- **Database & Storage**: CSV Data Layer & [Supabase](https://supabase.com/)
