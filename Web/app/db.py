import psycopg2
import psycopg2.extras
from flask import g
import os

def get_db():
    # Dùng global kết nối database mỗi request 1 kết nối duy nhất
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    return g.db

def get_cursor():
    # Trả về cursor dạng dict thay vì tupe
    db = get_db()
    return db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def close_db(exception=None):
    # Đóng kết nối database khi request kết thúc
    db = g.pop('db', None)
    if db is not None:
        db.close()
