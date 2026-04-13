import hashlib
from flask import Blueprint, request, session, jsonify, render_template
from app.routes.auth import require_login, require_role
from app.models import user_model

admin_bp = Blueprint('admin', __name__)


# ============================================================
#  API — Quản lý tài khoản
# ============================================================

@admin_bp.route('/api/users')
@require_login
@require_role('admin')
def api_get_users():
    """API lấy danh sách tài khoản (dùng view v_users_safe, không lộ password)."""
    users = user_model.get_all_users()
    return jsonify({'users': [dict(u) for u in users]})


@admin_bp.route('/api/users', methods=['POST'])
@require_login
@require_role('admin')
def api_create_user():
    """
    API tạo tài khoản mới.
    Nhận JSON: {"username": "...", "password": "...", "role": "student|teacher|admin"}
    """
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    role = data.get('role', 'student')

    # Kiểm tra username đã tồn tại chưa
    existing = user_model.find_by_username(username)
    if existing:
        return jsonify({'error': 'Username đã tồn tại'}), 400

    # Kiểm tra role hợp lệ
    if role not in ('student', 'teacher', 'admin'):
        return jsonify({'error': 'Role không hợp lệ'}), 400

    # Mã hóa password bằng SHA-256
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    new_id = user_model.create_user(username, password_hash, role)
    return jsonify({'message': 'Tạo tài khoản thành công', 'user_id': new_id}), 201


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_login
@require_role('admin')
def api_delete_user(user_id):
    """API xóa tài khoản."""
    user_model.delete_user(user_id)
    return jsonify({'message': 'Đã xóa tài khoản'})


@admin_bp.route('/api/users/<int:user_id>/role', methods=['PUT'])
@require_login
@require_role('admin')
def api_update_role(user_id):
    """
    API thay đổi role (endpoint HỢP LỆ chỉ admin dùng).
    Nhận JSON: {"role": "student|teacher|admin"}
    """
    data = request.get_json()
    role = data.get('role', '')
    if role not in ('student', 'teacher', 'admin'):
        return jsonify({'error': 'Role không hợp lệ'}), 400

    user_model.update_role(user_id, role)
    return jsonify({'message': f'Đã cập nhật role thành {role}'})


# ============================================================
#  API — Trang API Documentation
# ============================================================

@admin_bp.route('/api/docs')
@require_login
@require_role('admin')
def api_docs():
    """API trả về danh sách toàn bộ endpoints của hệ thống."""
    docs = [
        {'method': 'POST',   'url': '/api/auth/login',             'desc': 'Đăng nhập, trả về session'},
        {'method': 'POST',   'url': '/api/auth/logout',            'desc': 'Đăng xuất'},
        {'method': 'GET',    'url': '/api/grades/<student_id>',    'desc': 'Xem điểm sinh viên'},
        {'method': 'GET',    'url': '/api/profile',                'desc': 'Xem hồ sơ bản thân'},
        {'method': 'PUT',    'url': '/api/profile',                'desc': 'Cập nhật hồ sơ'},
        {'method': 'GET',    'url': '/api/courses/<id>/grades',    'desc': 'Xem điểm toàn bộ SV trong môn'},
        {'method': 'PUT',    'url': '/api/grades/<id>',            'desc': 'Nhập / sửa điểm'},
        {'method': 'GET',    'url': '/api/users',                  'desc': 'Danh sách tài khoản'},
        {'method': 'POST',   'url': '/api/users',                  'desc': 'Tạo tài khoản mới'},
        {'method': 'DELETE',  'url': '/api/users/<id>',            'desc': 'Xóa tài khoản'},
        {'method': 'PUT',    'url': '/api/users/<id>/role',        'desc': 'Thay đổi role'},
        {'method': 'GET',    'url': '/api/docs',                   'desc': 'Trang API documentation'},
    ]
    return jsonify({'endpoints': docs})


# ============================================================
#  TRANG WEB — Giao diện admin
# ============================================================

@admin_bp.route('/admin/users')
@require_login
@require_role('admin')
def admin_users_page():
    """Trang HTML quản lý tài khoản."""
    return render_template('admin_users.html',
                           username=session.get('username'),
                           role=session.get('role'))


@admin_bp.route('/admin/docs')
@require_login
@require_role('admin')
def admin_docs_page():
    """Trang HTML hiển thị API documentation."""
    return render_template('admin_docs.html',
                           username=session.get('username'),
                           role=session.get('role'))
