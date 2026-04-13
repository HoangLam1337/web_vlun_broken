from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for
from app.routes.auth import require_login, require_role
from app.models import student_model

student_bp = Blueprint('student', __name__)


# ============================================================
#  TRANG WEB — Xem điểm
# ============================================================

# @student_bp.route('/grades')
# @require_login
# @require_role('student', 'teacher', 'admin')
# def grades_redirect():
#     """
#     Khi sinh viên bấm "Xem điểm", tự động redirect về /grades/<student_id>.
#     Đây là hành vi bình thường — nhưng pentester sẽ nhìn thấy student_id trên URL
#     và thử thay đổi nó để xem điểm của sinh viên khác.
#     """
#     student = student_model.get_student_by_user_id(session['user_id'])
#     if not student:
#         return "Không tìm thấy hồ sơ sinh viên", 404
#     # Redirect về URL có chứa student_id → pentester nhìn thấy ID trên thanh địa chỉ
#     return redirect(url_for('student.grades_page', student_id=student['id']))


@student_bp.route('/grades')
@require_login
@require_role('student', 'teacher', 'admin')
def grades_page():
    #FIXED: Lấy student_id từ session, không hiện trên URL
    student = student_model.get_student_by_user_id(session['user_id'])
    if not student:
        return "Không tìm thấy hồ sơ sinh viên", 404

    return render_template('grades.html',
                           student_id=student['id'],
                           username=session.get('username'),
                           role=session.get('role'))


# @student_bp.route('/grades/<int:student_id>')
# @require_login
# @require_role('student', 'teacher', 'admin')
# def grades_page(student_id):
#     """
#     Trang xem điểm — URL dạng /grades/1, /grades/2...
    
#     VULNERABLE (IDOR): Không kiểm tra student_id có phải của user đang đăng nhập không.
#     Pentester chỉ cần đổi số trên thanh URL để xem điểm sinh viên khác.
#     """
#     return render_template('grades.html',
#                            student_id=student_id,
#                            username=session.get('username'),
#                            role=session.get('role'))

# @student_bp.route('/grades/<int:student_id>')
# @require_login
# @require_role('student', 'teacher', 'admin')
# def grades_page(student_id):
#     #FIXED: Kiểm tra ownership — student chỉ được xem điểm của mình
#     if session.get('role') == 'student':
#         student = student_model.get_student_by_user_id(session['user_id'])
#         if not student or student['id'] != student_id:
#             return "Bạn không có quyền xem điểm của sinh viên khác", 403
#     return render_template('grades.html',
#                            student_id=student_id,
#                            username=session.get('username'),
#                            role=session.get('role'))


# ============================================================
#  API — Xem điểm sinh viên
# ============================================================

@student_bp.route('/api/grades/<int:student_id>')
@require_login
@require_role('student', 'teacher', 'admin')
def api_get_grades(student_id):
    """
    API xem điểm — nhận student_id từ URL path.

    VULNERABLE (IDOR):
    - KHÔNG KIỂM TRA student_id có phải của user hiện tại không!
    - Bất kỳ ai đăng nhập đều có thể truyền student_id bất kỳ.
    → Sinh viên A gọi /api/grades/2 để xem điểm Sinh viên B.
    """
    grades = student_model.get_grades_by_student_id(student_id)
    return jsonify({
        'student_id': student_id,
        'grades': [dict(row) for row in grades]
    })


# @student_bp.route('/api/grades/<int:student_id>')
# @require_login
# @require_role('student', 'teacher', 'admin')
# def api_get_grades(student_id):
#     if session.get('role') == 'student':
#         student = student_model.get_student_by_user_id(session['user_id'])
#         if not student or student['id'] != student_id:
#             return jsonify({'error': "Bạn không có quyền xem điểm của sinh viên khác"}), 403                   
#     grades = student_model.get_grades_by_student_id(student_id)
#     return jsonify({
#         'student_id': student_id,
#         'grades': [dict(row) for row in grades]
#     })

# ============================================================
#  API — Xem hồ sơ bản thân
# ============================================================

@student_bp.route('/api/profile')
@require_login
def api_get_profile():
    """API xem hồ sơ bản thân."""
    profile = student_model.get_profile_by_user_id(session['user_id'])
    if not profile:
        return jsonify({'error': 'Không tìm thấy hồ sơ'}), 404
    return jsonify(dict(profile))
