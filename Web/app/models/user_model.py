from app.db import get_cursor, get_db


def find_by_username(username):
    # Tìm user theo username (dùng cho đăng nhập).
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    cur.close()
    return user


def get_all_users():
    # Lấy danh sách tất cả tài khoản (admin dùng, dùng view v_users_safe).
    cur = get_cursor()
    cur.execute("SELECT * FROM v_users_safe ORDER BY id")
    users = cur.fetchall()
    cur.close()
    return users


def create_user(username, password_hash, role):
    # Tạo tài khoản mới
    cur = get_cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id",
        [username, password_hash, role]
    )
    new_id = cur.fetchone()['id']
    get_db().commit()
    cur.close()
    return new_id


def delete_user(user_id):
    # Xóa tài khoản theo id
    cur = get_cursor()
    cur.execute("DELETE FROM users WHERE id = %s", [user_id])
    get_db().commit()
    cur.close()


def update_role(user_id, role):
    # Cập nhật role cho user (admin dùng — endpoint hợp lệ).
    cur = get_cursor()
    cur.execute("UPDATE users SET role = %s WHERE id = %s", [role, user_id])
    get_db().commit()
    cur.close()


def update_user_field(user_id, field, value):
    # Cập nhật một field bất kỳ cho user (dùng cho lỗ hổng privilege escalation).
    cur = get_cursor()
    # VULNERABLE: cho phép cập nhật bất kỳ field nào, kể cả 'role'
    cur.execute(f"UPDATE users SET {field} = %s WHERE id = %s", [value, user_id])
    get_db().commit()
    cur.close()
