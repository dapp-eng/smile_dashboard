-- VIEW 1: Company tracking summary (BT-04)
CREATE VIEW tracking_company_summary AS
SELECT
    tc.id_tracking_company,
    tc.id_company,
    tc.posisi,
    tc.jumlah_permintaan,
    tc.jumlah_dikirimkan,
    COUNT(CASE WHEN ts.progress_student = 'Placement' THEN 1 END) AS accepted,
    ROUND(
        COUNT(CASE WHEN ts.progress_student = 'Placement' THEN 1 END)::DECIMAL
        / NULLIF(tc.jumlah_dikirimkan, 0) * 100, 1
    ) AS acceptance_rate,
    ROUND(
        LEAST(
            COUNT(CASE WHEN ts.progress_student = 'Placement' THEN 1 END),
            tc.jumlah_permintaan
        )::DECIMAL / NULLIF(tc.jumlah_permintaan, 0) * 100, 1
    ) AS fulfillment_rate
FROM tracking_company tc
LEFT JOIN tracking_student ts ON ts.id_tracking_company = tc.id_tracking_company
GROUP BY tc.id_tracking_company, tc.id_company, tc.posisi, tc.jumlah_permintaan, tc.jumlah_dikirimkan;


-- VIEW 2: Ghosting detection (BT-05)
CREATE VIEW ghosting_flags AS
SELECT
    ts.id_tracking_student,
    ts.nim,
    ts.student_name,
    ts.company,
    ts.progress_student,
    ts.last_update,
    CURRENT_DATE - ts.last_update AS days_since_update,
    CASE
        WHEN ts.progress_student IN ('FU 1','FU 2','FU 3','Ghosting') THEN 'labeled'
        WHEN CURRENT_DATE - ts.last_update > 28 THEN 'overdue_unlabeled_ghosting'
        WHEN CURRENT_DATE - ts.last_update > 21 THEN 'overdue_unlabeled_fu3'
        WHEN CURRENT_DATE - ts.last_update > 14 THEN 'overdue_unlabeled_fu2'
        WHEN CURRENT_DATE - ts.last_update > 7 THEN 'overdue_unlabeled_fu1'
        ELSE 'ok'
    END AS ghosting_check
FROM tracking_student ts
WHERE ts.progress_student NOT IN ('Placement', 'Rejected', 'Finish');


-- VIEW 3: Orphaned tracking_student rows
CREATE VIEW orphaned_tracking_student AS
SELECT ts.*
FROM tracking_student ts
LEFT JOIN student_all sa ON ts.nim = sa.nim
WHERE sa.nim IS NULL;


-- VIEW 4: Sync mismatch between student_all and status_student (BT-08)
CREATE VIEW sync_mismatch AS
SELECT
    sa.nim AS student_all_nim,
    ss.nim AS status_student_nim,
    sa.nama AS student_all_nama,
    ss.nama AS status_student_nama,
    ss.sync_date,
    CASE
        WHEN ss.nim IS NULL THEN 'missing_in_status_student'
        WHEN sa.nim IS NULL THEN 'missing_in_student_all'
        WHEN sa.nama <> ss.nama THEN 'name_mismatch'
        ELSE 'ok'
    END AS mismatch_type
FROM student_all sa
FULL OUTER JOIN status_student ss ON sa.nim = ss.nim
WHERE ss.nim IS NULL 
   OR sa.nim IS NULL 
   OR sa.nama <> ss.nama;


-- VIEW 5: Eligible students (BT-06)
CREATE VIEW eligible_students AS
SELECT
    sa.nim,
    sa.nama,
    sa.program_studi,
    sa.semester,
    ss.ipk,
    ss.status,
    ss.domisili,
    ss.ketersediaan,
    ss.tools
FROM student_all sa
JOIN status_student ss ON sa.nim = ss.nim
WHERE ss.status = 'Active';