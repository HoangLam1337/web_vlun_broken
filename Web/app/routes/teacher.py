from flask import Blueprint, request, session, jsonify, render_template
from app.routes.auth import require_login, require_role
from app.models import teacher_model, grade_model

teacher_bp = Blueprint('teacher', __name__)


# ============================================================
#  API — Giảng viên xem điểm sinh viên trong môn
# ============================================================

@teacher_bp.route('/api/courses/<int:course_id>/grades')
@require_login
@require_role('teacher', 'admin')
def api_get_course_grades(course_id):
    """API xem toàn bộ điểm sinh viên trong 1 môn học."""
    grades = grade_model.get_grades_by_course_id(course_id)
    return jsonify({
        'course_id': course_id,
        'grades': [dict(row) for row in grades]
    })


# ============================================================
#  API — Giảng viên nhập/sửa điểm
# ============================================================

@teacher_bp.route('/api/grades/<int:grade_id>', methods=['PUT'])
@require_login
@require_role('teacher', 'admin')
def api_update_grade(grade_id):
    """
    API cập nhật điểm.
    Nhận JSON: {"score_mid1": 8.0, "score_mid2": 7.5, "score_final": 8.0}
    """
    data = request.get_json()

    # Kiểm tra bản ghi điểm có tồn tại không
    grade = grade_model.get_grade_by_id(grade_id)
    if not grade:
        return jsonify({'error': 'Không tìm thấy bản ghi điểm'}), 404

    # Cập nhật điểm
    grade_model.update_grade(
        grade_id=grade_id,
        score_mid1=data.get('score_mid1', grade['score_mid1']),
        score_mid2=data.get('score_mid2', grade['score_mid2']),
        score_final=data.get('score_final', grade['score_final']),
        updated_by=session['user_id']
    )

    return jsonify({'message': 'Cập nhật điểm thành công'})


# ============================================================
#  TRANG WEB — Giao diện giảng viên
# ============================================================

@teacher_bp.route('/teacher/grades')
@require_login
@require_role('teacher', 'admin')
def teacher_grades_page():
    """Trang HTML cho giảng viên xem/sửa điểm."""
    # Lấy danh sách môn dạy theo teacher profile
    teacher = teacher_model.get_teacher_by_user_id(session['user_id'])
    if teacher:
        courses = teacher_model.get_courses_by_teacher_id(teacher['id'])
    else:
        # Không có teacher profile → load toàn bộ môn học
        # (trường hợp admin, hoặc user đã leo thang đặc quyền)
        # courses = teacher_model.get_all_courses()
        courses = []
    
    courses = [dict(c) for c in courses]

    return render_template('teacher_grades.html',
                           username=session.get('username'),
                           role=session.get('role'),
                           courses=courses)
