# ROLE: 
- SINH VIÊN AN NINH MẠNG: ĐANG HỌC MÔN BẢO MẬT ỨNG DỤNG WEB (MỤC TIÊU NGHỀ NHIỆP: PENTEST WEB)

# CONTEXT: 
- ĐỒ ÁN MÔN HỌC BẢO MẬT ỨNG DỤNG WEB
## Đề tài 7. Broken Access Control (IDOR & Privilege Escalation)
- Lý thuyết: Tham chiếu đối tượng không an toàn (IDOR) và leo thang đặc quyền (ngang/dọc).
- Sản phẩm: Xây dựng hệ thống quản lý sinh viên. Demo: Sinh viên A xem được điểm của sinh viên B (IDOR) và Sinh viên tự nâng quyền lên thành Giảng viên (Privilege Escalation).

# CONSTRAINTS:
## AUTHORIZATION
- Sinh viên: Xem điểm và thông tin cua mình
- Giảng viên: Xem điểm và thông tin của sinh viên, cập nhật điểm của sinh viên
- Admin: Quản lý hệ thống: tài khoản, api (tạo một /api/docs chứa toàn bộ đường dẫn api của hệ thống cho admin xem được)

## VULNERABILITY
- IDOR: Sinh viên A xem được điểm của sinh viên B
- Privilege Escalation: Sinh viên tự nâng quyền lên thành Giảng viên

## DATABASE
- PostgreSQL: database.sql

## WEB 
- flask cơ bản - cho người mới bắt đầu, mới học về flask
- Mô hình MVC
- Xây dựng các chức năng cơ bản: đăng nhập, đăng xuất, quản lý sinh viên, quản lý tài khoản
- Xây dựng API cơ bản.
- Chưa cần xây dựng giao diện, chỉ cần hiện thông tin đúng yêu cầu lên trang web 
- Dùng Cookie + Session
- Sử dụng các hàm có sẵn của flask ở mức cơ bản đủ dùng, đủ làm đồ án không cần các hàm thủ tục khó nâng cao, đơn giản nhất mức có thể 

## API
```
AUTH
  POST   /api/auth/login          -- đăng nhập, trả về session/token
  POST   /api/auth/logout         -- đăng xuất

SINH VIÊN (student)
  GET    /api/grades              -- xem điểm  ← ĐIỂM IDOR ở đây
  GET    /api/profile             -- xem hồ sơ bản thân

GIẢNG VIÊN (teacher)
  GET    /api/courses/:id/grades  -- xem điểm toàn bộ SV trong môn
  PUT    /api/grades/:id          -- nhập / sửa điểm

ADMIN
  GET    /api/users               -- danh sách tài khoản
  POST   /api/users               -- tạo tài khoản mới
  DELETE /api/users/:id           -- xóa tài khoản
  PUT    /api/users/:id/role      -- thay đổi role  ← đây là endpoint HỢP LỆ để sửa role
  GET    /api/docs                -- danh sách api

PROFILE (dùng chung — lỗ hổng nằm ở đây)
  PUT    /api/profile             -- cập nhật hồ sơ  ← ĐIỂM Privilege Escalation ở đây
```

## Cookie + Session
```
# Đăng nhập — lưu thông tin vào session (cookie mã hoá phía client)
@app.route('/api/auth/login', methods=['POST'])
def login():
    user = db.query("SELECT * FROM users WHERE username = %s", [username])
    if user and user['password_hash'] == sha256(password):
        session['user_id'] = user['id']
        session['role']    = user['role']   # ← lưu role vào session
        return jsonify({'message': 'OK'})

# Middleware kiểm tra quyền
def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') not in roles:
                return jsonify({'error': 'Forbidden'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Dùng trên route
@app.route('/api/grades')
@require_role('student', 'teacher', 'admin')
def get_grades():
    ...
```

```
# ❌ VULNERABLE — nhận role từ body và ghi vào session
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    session['role'] = data.get('role', session['role'])  # ← lỗ hổng
    db.execute("UPDATE users SET role = %s WHERE id = %s",
               [data['role'], session['user_id']])


# ✅ FIXED — không bao giờ nhận role từ client
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    allowed = ['full_name', 'email', 'phone']          # whitelist fields
    update  = {k: data[k] for k in allowed if k in data}
    # role không có trong whitelist → không bao giờ bị sửa
```