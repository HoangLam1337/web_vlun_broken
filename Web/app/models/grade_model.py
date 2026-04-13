from app.db import get_cursor, get_db


def get_grades_by_course_id(course_id):
    # Lấy toàn bộ điểm sinh viên 1 môn học - role: teacher
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM v_grades_full WHERE course_code = (SELECT course_code FROM courses WHERE id = %s) ORDER BY mssv",
        [course_id]
    )
    grades = cur.fetchall()
    cur.close()
    return grades


def get_grade_by_id(grade_id):
    # Lấy điểm 1 môn của sinh viên theo id môn học - role: teacher
    cur = get_cursor()
    cur.execute("SELECT * FROM grades WHERE id = %s", [grade_id])
    grade = cur.fetchone()
    cur.close()
    return grade


def update_grade(grade_id, score_mid1, score_mid2, score_final, updated_by):
    # Cập nhật điểm môn học - role: teacher
    cur = get_cursor()
    cur.execute("""
        UPDATE grades 
        SET score_mid1 = %s, score_mid2 = %s, score_final = %s, updated_by = %s
        WHERE id = %s
    """, [score_mid1, score_mid2, score_final, updated_by, grade_id])
    get_db().commit()
    cur.close()
