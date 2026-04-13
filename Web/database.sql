-- ============================================================
--  HỆ THỐNG QUẢN LÝ SINH VIÊN
--  Đồ án: Broken Access Control (IDOR & Privilege Escalation)
--  Database: PostgreSQL
-- ============================================================

-- Xóa bảng nếu đã tồn tại (thứ tự quan trọng vì FK)
DROP TABLE IF EXISTS grades    CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses   CASCADE;
DROP TABLE IF EXISTS students  CASCADE;
DROP TABLE IF EXISTS teachers  CASCADE;
DROP TABLE IF EXISTS users     CASCADE;

-- ============================================================
--  BẢNG 1: users — xác thực & phân quyền
-- ============================================================
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,   -- MSSV / mã GV / 'admin'
    password_hash CHAR(64)     NOT NULL,          -- SHA-256 hex (64 ký tự)
    role          VARCHAR(10)  NOT NULL
                  CHECK (role IN ('student', 'teacher', 'admin')),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
--  BẢNG 2: students — hồ sơ sinh viên
-- ============================================================
CREATE TABLE students (
    id         SERIAL PRIMARY KEY,
    user_id    INT         UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name  VARCHAR(100) NOT NULL,
    mssv       VARCHAR(20)  UNIQUE NOT NULL,
    email      VARCHAR(150) UNIQUE,
    class_name VARCHAR(50),
    dob        DATE,
    phone      VARCHAR(15)
);

-- ============================================================
--  BẢNG 3: teachers — hồ sơ giảng viên
-- ============================================================
CREATE TABLE teachers (
    id         SERIAL PRIMARY KEY,
    user_id    INT         UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name  VARCHAR(100) NOT NULL,
    magv       VARCHAR(20)  UNIQUE NOT NULL,
    email      VARCHAR(150) UNIQUE,
    department VARCHAR(100),
    phone      VARCHAR(15)
);

-- ============================================================
--  BẢNG 4: courses — môn học
-- ============================================================
CREATE TABLE courses (
    id          SERIAL PRIMARY KEY,
    teacher_id  INT          NOT NULL REFERENCES teachers(id) ON DELETE RESTRICT,
    course_code VARCHAR(20)  UNIQUE NOT NULL,    -- VD: CS101
    course_name VARCHAR(150) NOT NULL,
    credits     INT          NOT NULL DEFAULT 3  CHECK (credits > 0),
    semester    VARCHAR(20)  NOT NULL,           -- VD: HK1-2024
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
--  BẢNG 5: grades — bảng điểm
--  Mỗi sinh viên có đúng 1 dòng điểm cho mỗi môn học
-- ============================================================
CREATE TABLE grades (
    id          SERIAL PRIMARY KEY,
    student_id  INT   NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id   INT   NOT NULL REFERENCES courses(id)  ON DELETE CASCADE,
    score_mid1  NUMERIC(4,2) CHECK (score_mid1  BETWEEN 0 AND 10),  -- Kiểm tra 1
    score_mid2  NUMERIC(4,2) CHECK (score_mid2  BETWEEN 0 AND 10),  -- Kiểm tra 2
    score_final NUMERIC(4,2) CHECK (score_final BETWEEN 0 AND 10),  -- Tổng kết
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_by  INT REFERENCES users(id),                           -- ai cập nhật lần cuối

    UNIQUE (student_id, course_id)   -- mỗi SV chỉ có 1 dòng điểm / môn
);

-- ============================================================
--  AUTO-UPDATE updated_at khi sửa bảng users & grades
-- ============================================================
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_grades_updated
    BEFORE UPDATE ON grades
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================================
--  INDEX — tăng tốc truy vấn thường dùng
-- ============================================================
CREATE INDEX idx_students_user_id  ON students(user_id);
CREATE INDEX idx_teachers_user_id  ON teachers(user_id);
CREATE INDEX idx_courses_teacher   ON courses(teacher_id);
CREATE INDEX idx_grades_student    ON grades(student_id);
CREATE INDEX idx_grades_course     ON grades(course_id);

-- ============================================================
--  DỮ LIỆU MẪU
--  password cho tất cả tài khoản = "123456"
--  SHA-256("123456") = 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
-- ============================================================

-- --- Tài khoản ---
INSERT INTO users (username, password_hash, role) VALUES
-- Admin
('admin',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin'),
-- Giảng viên
('GV001',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'teacher'),
('GV002',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'teacher'),
-- Sinh viên
('SV001',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student'),
('SV002',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student'),
('SV003',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student'),
('SV004',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student');

-- --- Hồ sơ giảng viên ---
INSERT INTO teachers (user_id, full_name, magv, email, department) VALUES
(2, 'Pham Thi Dung',   'GV001', 'dung.pt@university.edu.vn',  'Cong nghe thong tin'),
(3, 'Nguyen Van Hung',  'GV002', 'hung.nv@university.edu.vn',  'Cong nghe thong tin');

-- --- Hồ sơ sinh viên ---
INSERT INTO students (user_id, full_name, mssv, email, class_name, dob) VALUES
(4, 'Nguyen Van An',   'SV001', 'an.nv@student.edu.vn',   'CNTT-K22A', '2002-03-15'),
(5, 'Tran Thi Binh',   'SV002', 'binh.tt@student.edu.vn', 'CNTT-K22A', '2002-07-22'),
(6, 'Le Van Cuong',    'SV003', 'cuong.lv@student.edu.vn','CNTT-K22B', '2001-11-08'),
(7, 'Pham Thi Dieu',   'SV004', 'dieu.pt@student.edu.vn', 'CNTT-K22B', '2002-01-30');

-- --- Môn học ---
INSERT INTO courses (teacher_id, course_code, course_name, credits, semester) VALUES
(1, 'CS301', 'Bao mat ung dung web',     3, 'HK1-2024'),
(1, 'CS201', 'Mang may tinh',            3, 'HK1-2024'),
(2, 'CS401', 'Lap trinh Python nang cao',3, 'HK1-2024');

-- --- Bảng điểm ---
-- CS301 - Bảo mật ứng dụng web
INSERT INTO grades (student_id, course_id, score_mid1, score_mid2, score_final, updated_by) VALUES
(1, 1, 7.0, 6.5,  7.0, 2),   -- SV001 - An
(2, 1, 9.0, 8.5,  9.0, 2),   -- SV002 - Binh  ← nạn nhân IDOR từ SV001
(3, 1, 5.5, 6.0,  6.0, 2),   -- SV003 - Cuong
(4, 1, 8.0, 8.0,  8.5, 2);   -- SV004 - Dieu

-- CS201 - Mạng máy tính
INSERT INTO grades (student_id, course_id, score_mid1, score_mid2, score_final, updated_by) VALUES
(1, 2, 8.0, 7.5,  8.0, 2),
(2, 2, 7.5, 8.0,  7.5, 2),
(3, 2, 6.0, 5.5,  6.5, 2),
(4, 2, 9.0, 9.5,  9.0, 2);

-- CS401 - Lập trình Python
INSERT INTO grades (student_id, course_id, score_mid1, score_mid2, score_final, updated_by) VALUES
(1, 3, 6.5, 7.0,  7.0, 3),
(2, 3, 8.5, 9.0,  8.5, 3);

-- ============================================================
--  VIEW hữu ích (tùy chọn — giúp query nhanh hơn)
-- ============================================================

-- View: điểm đầy đủ kèm tên sinh viên và tên môn
CREATE OR REPLACE VIEW v_grades_full AS
SELECT
    g.id            AS grade_id,
    s.mssv,
    s.full_name     AS student_name,
    s.class_name,
    c.course_code,
    c.course_name,
    c.semester,
    t.full_name     AS teacher_name,
    g.score_mid1,
    g.score_mid2,
    g.score_final,
    ROUND(
        COALESCE(g.score_mid1, 0) * 0.25 +
        COALESCE(g.score_mid2, 0) * 0.25 +
        COALESCE(g.score_final, 0) * 0.50
    , 2)            AS score_weighted,  -- công thức: 25% + 25% + 50%
    g.updated_at
FROM grades   g
JOIN students s ON g.student_id = s.id
JOIN courses  c ON g.course_id  = c.id
JOIN teachers t ON c.teacher_id = t.id;

-- View: danh sách tài khoản (admin dùng — không lộ password_hash)
CREATE OR REPLACE VIEW v_users_safe AS
SELECT
    u.id,
    u.username,
    u.role,
    u.is_active,
    u.created_at,
    COALESCE(s.full_name, t.full_name) AS full_name,
    COALESCE(s.mssv,      t.magv)      AS code,
    COALESCE(s.email,     t.email)     AS email
FROM users    u
LEFT JOIN students s ON u.id = s.user_id
LEFT JOIN teachers t ON u.id = t.user_id;

-- ============================================================
--  KIỂM TRA NHANH
-- ============================================================

-- Xem toàn bộ điểm (chạy sau khi import xong)
-- SELECT * FROM v_grades_full ORDER BY mssv, course_code;

-- Xem danh sách tài khoản (không có hash)
-- SELECT * FROM v_users_safe;

SELECT * FROM USERS;
SELECT * FROM STUDENTS;
SELECT * FROM TEACHERS;
SELECT * FROM COURSES;
SELECT * FROM GRADES;