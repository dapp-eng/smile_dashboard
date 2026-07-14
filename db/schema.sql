CREATE TABLE company (
    id_company VARCHAR PRIMARY KEY,
    company_name VARCHAR,
    company_type VARCHAR,
    industry_sector VARCHAR,
    kota VARCHAR,
    skala_perusahaan VARCHAR,
    pic_name VARCHAR,
    pic_phone VARCHAR,
    created_at DATE
);

CREATE TABLE talent_request (
    id_talent_req VARCHAR PRIMARY KEY,
    id_company VARCHAR REFERENCES company(id_company),
    nama_perusahaan VARCHAR,
    alamat_kantor TEXT,
    industri_sektor VARCHAR,
    nama_pic VARCHAR,
    no_whatsapp VARCHAR,
    nama_posisi VARCHAR,
    jenis_penempatan VARCHAR,
    headcount INT,
    bidang_studi_dibutuhkan VARCHAR,
    minimum_semester INT,
    deskripsi_requirement TEXT,
    working_arrangement VARCHAR,
    working_arrangement_detail TEXT,
    durasi VARCHAR,
    renumerasi VARCHAR,
    request_date DATE,
    sumber_baris_form VARCHAR
);

CREATE TABLE student_all (
    nim VARCHAR PRIMARY KEY,
    nama VARCHAR,
    program_studi VARCHAR,
    semester INT,
    hp VARCHAR,
    email_pribadi VARCHAR,
    email_kampus VARCHAR,
    bidang_minat VARCHAR,
    jenis_penempatan_diminati VARCHAR,
    bulan_masuk VARCHAR
);

CREATE TABLE status_student (
    id_status VARCHAR PRIMARY KEY,
    nim VARCHAR UNIQUE REFERENCES student_all(nim),
    email VARCHAR,
    nama VARCHAR,
    semester INT,
    program_studi VARCHAR,
    no_whatsapp VARCHAR,
    cv VARCHAR,
    portofolio VARCHAR,
    ipk DECIMAL,
    status VARCHAR,
    domisili VARCHAR,
    ketersediaan VARCHAR,
    tools TEXT,
    sync_date DATE
);

CREATE TABLE tracking_company (
    id_tracking_company VARCHAR PRIMARY KEY,
    id_talent_req VARCHAR REFERENCES talent_request(id_talent_req),
    id_company VARCHAR REFERENCES company(id_company),
    nama_perusahaan VARCHAR,
    posisi VARCHAR,
    jenis_penempatan VARCHAR,
    bidang_studi_dicari VARCHAR,
    progress VARCHAR,
    request_date DATE,
    send_date DATE,
    jumlah_permintaan INT,
    jumlah_dikirim INT,
    lst_rim TEXT
);

CREATE TABLE tracking_student (
    id_tracking_student VARCHAR PRIMARY KEY,
    nim VARCHAR REFERENCES student_all(nim),
    id_tracking_company VARCHAR REFERENCES tracking_company(id_tracking_company),
    student_name VARCHAR,
    internship_semester INT,
    company VARCHAR,
    position VARCHAR,
    jenis_penempatan VARCHAR,
    progress_student VARCHAR,
    last_update DATE,
    rejection TEXT
);

