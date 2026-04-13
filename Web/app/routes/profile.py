from flask import Blueprint, request, session, jsonify, render_template
from app.routes.auth import require_login
from app.models import user_model, student_model

profile_bp = Blueprint('profile', __name__)


# ============================================================
#  API — Cập nhật hồ sơ (LỖ HỔNG PRIVILEGE ESCALATION)
# ============================================================

@profile_bp.route('/api/profile', methods=['PUT'])
@require_login
def api_update_profile():
    """
    API cập nhật hồ sơ cá nhân.

    VULNERABLE (Privilege Escalation):
    - Form frontend chỉ gửi full_name, email, phone (trông bình thường).
    - Nhưng server KHÔNG whitelist các field được phép sửa.
    - Nếu pentester dùng Burp Suite thêm {"role": "teacher"} vào JSON body:
      1. Server thấy key "role" → cập nhật vào bảng users
      2. Cập nhật role trong session
    → Sinh viên tự nâng quyền thành Giảng viên hoặc Admin.
    """
    data = request.get_json()
    user_id = session['user_id']

    # Tách field: field nào thuộc bảng students, field nào thuộc bảng users
    student_fields = ['full_name', 'email', 'phone', 'class_name', 'dob']
    user_fields = ['username']

    # Cập nhật các field thuộc bảng students
    student_updates = {k: v for k, v in data.items() if k in student_fields}
    if student_updates:
        student_model.update_student_by_user_id(user_id, student_updates)

    #VULNERABLE: Nếu client gửi "role" → cập nhật luôn vào bảng users + session
    if 'role' in data:
        user_model.update_role(user_id, data['role'])
        session['role'] = data['role']

    return jsonify({'message': 'Cập nhật hồ sơ thành công'})


# # FIXED: Cập nhật hồ sơ
# @profile_bp.route('/api/profile', methods=['PUT'])
# @require_login
# def api_update_profile():
#     allowed_fields = ['full_name', 'email', 'phone']
#     data = request.get_json()
#     user_id = session['user_id']

#     # Chỉ cho phép sửa các field trong allowed_fields
#     updates = {k: v for k, v in data.items() if k in allowed_fields}
#     if updates:
#         student_model.update_student_by_user_id(user_id, updates)

#     return jsonify({'message': 'Cập nhật hồ sơ thành công'})


# ============================================================
#  TRANG WEB — Giao diện xem/sửa hồ sơ
# ============================================================

@profile_bp.route('/profile')
@require_login
def profile_page():
    """Trang HTML xem hồ sơ cá nhân."""
    return render_template('profile.html',
                           username=session.get('username'),
                           role=session.get('role'))
