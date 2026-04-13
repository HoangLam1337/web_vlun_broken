from app.db import get_cursor, get_db


def get_student_by_user_id(user_id):
    # Lấy thông tin sinh viên theo user_id - role: student

    cur = get_cursor()
    cur.execute("SELECT * FROM students WHERE user_id = %s", [user_id])
    student = cur.fetchone()
    cur.close()
    return student


def get_grades_by_student_id(student_id):
    # Lấy điểm theo student_id (dùng view v_grades_full trong database).
    # VULNERABLE (IDOR): Hàm này nhận bất kỳ student_id nào, controller sẽ KHÔNG kiểm tra student_id có phải của user đang đăng nhập không.

    cur = get_cursor()
    cur.execute(
        "SELECT * FROM v_grades_full WHERE mssv = (SELECT mssv FROM students WHERE id = %s) ORDER BY course_code",
        [student_id]
    )
    grades = cur.fetchall()
    cur.close()
    return grades

# # FIXED: Lấy điểm theo user_id
# def get_grades_by_user_id(user_id):
#     #Lấy điểm theo user_id — Model chỉ làm việc với DB."""
#     cur = get_cursor()
#     cur.execute(
#         "SELECT * FROM v_grades_full WHERE mssv = (SELECT mssv FROM students WHERE user_id = %s) ORDER BY course_code",
#         [user_id]
#     )
#     grades = cur.fetchall()
#     cur.close()
#     return grades



def get_profile_by_user_id(user_id):
    # Lấy thông tin profile đầy đủ (user + student info): role: student

    cur = get_cursor()
    cur.execute("""
        SELECT u.id as user_id, u.username, u.role,
               s.id as student_id, s.full_name, s.mssv, s.email, 
               s.class_name, s.dob, s.phone
        FROM users u
        LEFT JOIN students s ON u.id = s.user_id
        WHERE u.id = %s
    """, [user_id])
    profile = cur.fetchone()
    cur.close()
    return profile


def update_student_by_user_id(user_id, updates):
    # Cập nhật thông tin sinh viên trong bảng students.
    # updates là dict,{'full_name': 'Tên mới', 'email': 'email@new.com'}
    # VULNERABLE (Mass Assignment): Hàm này nhận bất kỳ field nào từ updates và update vào DB mà không validate.

    if not updates:
        return

    # Tạo câu SQL động: SET full_name = %s, email = %s ...

    set_parts = []
    values = []
    for field, value in updates.items():
        set_parts.append(f"{field} = %s")
        values.append(value)

    values.append(user_id)
    sql = f"UPDATE students SET {', '.join(set_parts)} WHERE user_id = %s"

    cur = get_cursor()
    cur.execute(sql, values)
    get_db().commit()
    cur.close()


# def update_student_by_user_id(user_id, updates):
#     # Danh sách các cột thực sự được phép sửa trong bảng students
#     whitelist = {'full_name', 'email', 'phone', 'address'} 
    
#     # Chỉ giữ lại các trường nằm trong whitelist
#     safe_updates = {k: v for k, v in updates.items() if k in whitelist}

#     if not safe_updates:
#         return False # Hoặc raise một Exception

#     set_parts = []
#     values = []
#     for field, value in safe_updates.items():
#         set_parts.append(f"{field} = %s")
#         values.append(value)
    
#    values.append(user_id)
#     sql = f"UPDATE students SET {', '.join(set_parts)} WHERE user_id = %s"

#     cur = get_cursor()
#     cur.execute(sql, values)
#     get_db().commit()
#     cur.close()

