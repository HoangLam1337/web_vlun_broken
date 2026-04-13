import hashlib
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import user_model

auth_bp = Blueprint('auth', __name__)


# ============================================================
#  MIDDLEWARE — Decorator kiểm tra đăng nhập và quyền
# ============================================================

def require_login(f):
    """Decorator: Kiểm tra user đã đăng nhập chưa (session có user_id không)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            # Nếu là API request → trả JSON lỗi
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Chưa đăng nhập'}), 401
            # Nếu là trang web → redirect về trang login
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return wrapper


def require_role(*roles):
    """Decorator: Kiểm tra role của user có nằm trong danh sách cho phép không."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Không có quyền truy cập'}), 403
                return redirect(url_for('auth.login_page'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

   
# ============================================================
# Tạo decorator kiểm tra ownership (Fix - IDOR)
# ============================================================

# def require_student_ownership(f):
#     @wraps(f)
#     def wrapper(student_id, *args, **kwargs):
#         if session.get('role') == 'student':
#             student = student_model.get_student_by_user_id(session['user_id'])
#             if not student or student['id'] != student_id:
#                 return jsonify({'error': 'Forbidden'}), 403
#         return f(student_id, *args, **kwargs)
#     return wrapper


# ============================================================
#  TRANG WEB — Hiển thị giao diện
# ============================================================

@auth_bp.route('/')
def home():
    """Trang chủ: nếu đã đăng nhập → dashboard, chưa → login."""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/login')
def login_page():
    """Hiển thị trang đăng nhập."""
    return render_template('login.html')


@auth_bp.route('/dashboard')
@require_login
def dashboard():
    """Trang chính sau đăng nhập — hiển thị menu theo role."""
    return render_template('dashboard.html',
                           username=session.get('username'),
                           role=session.get('role'))


# ============================================================
#  API — Xử lý đăng nhập / đăng xuất
# ============================================================

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """
    API đăng nhập.
    Nhận JSON: {"username": "...", "password": "..."}
    Kiểm tra SHA-256(password) với password_hash trong DB.
    Nếu đúng → lưu user_id và role vào session.
    """
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    # Tìm user trong database
    user = user_model.find_by_username(username)
    if not user:
        return jsonify({'error': 'Sai tên đăng nhập hoặc mật khẩu'}), 401

    # Mã hóa password bằng SHA-256 và so sánh
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        return jsonify({'error': 'Sai tên đăng nhập hoặc mật khẩu'}), 401

    # Kiểm tra tài khoản có bị khóa không
    if not user['is_active']:
        return jsonify({'error': 'Tài khoản đã bị khóa'}), 403

    # Lưu thông tin vào session (cookie mã hóa phía client)
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']

    return jsonify({
        'message': 'Đăng nhập thành công',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })


@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API đăng xuất — xóa toàn bộ session."""
    session.clear()
    return jsonify({'message': 'Đã đăng xuất'})