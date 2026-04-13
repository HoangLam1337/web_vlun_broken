from app.db import get_cursor


def get_teacher_by_user_id(user_id):
    # Lấy hồ sơ giảng viên theo user_id - role: teacher
    cur = get_cursor()
    cur.execute("SELECT * FROM teachers WHERE user_id = %s", [user_id])
    teacher = cur.fetchone()
    cur.close()
    return teacher


def get_courses_by_teacher_id(teacher_id):
    # Lấy danh sách môn học mà giảng viên đang dạy - role: teacher
    cur = get_cursor()
    cur.execute("SELECT * FROM courses WHERE teacher_id = %s ORDER BY course_code", [teacher_id])
    courses = cur.fetchall()
    cur.close()
    return courses


# def get_all_courses():
#     # Lấy toàn bộ môn học (dùng khi user có role teacher nhưng không có profile giảng viên).
#     cur = get_cursor()
#     cur.execute("SELECT * FROM courses ORDER BY course_code")
#     courses = cur.fetchall()
#     cur.close()
#     return courses
