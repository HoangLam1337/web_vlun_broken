from app.routes.auth import auth_bp
from app.routes.student import student_bp
from app.routes.teacher import teacher_bp
from app.routes.admin import admin_bp
from app.routes.profile import profile_bp


def Route(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)