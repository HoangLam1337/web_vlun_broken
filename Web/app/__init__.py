from flask import Flask
from dotenv import load_dotenv
import os
from app.db import close_db

# Load biến môi trường từ file .env
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='views', static_folder='static')

    # Cấu hình SECRET_KEY cho session (cookie mã hóa)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')

    # Đăng ký hàm đóng DB sau mỗi request
    app.teardown_appcontext(close_db)

    # Đăng ký tất cả routes (blueprints)
    from app.route import Route
    Route(app)

    return app