# Dockerfile 
```
FROM python:3.11-slim

WORKDIR /app

## Cài dependencies
COPY Web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Copy toàn bộ source
COPY Web/ .

EXPOSE 5000

CMD ["python", "app.py"]
``` 

# Docker Compose
```
version: '3.8'
services:
  db:
    image: postgres:15
    container_name: db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: [PASSWORD]
      POSTGRES_DB: web_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    container_name: web
    ports:
      - "5000:5000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:[PASSWORD]@db:5432/web_db

volumes:
  postgres_data:


# .dockerignore
venv/
__pycache__/
*.pyc
.git/
docker.md
document.md
```

# Create Web/.env.example
DB_HOST=db
DB_PORT=5432
DB_NAME=web_db
DB_USER=postgres
DB_PASSWORD=your_password_here
SECRET_KEY=your_secret_key_here

# Build & Run
cd Broken_Access_Control
docker compose up --build
docker compose ps -a
docker compose log db
docker compose log web
docker compose down (tắt docker compose)
docker compose down -v (tắt docker compose và xóa volume)


# push git 
cd "C:\Users\lamnh\OneDrive\Máy tính\BMWEB\Broken_Access_Control"

## Kiểm tra file nào chưa được track
git status

## Add các file cần thiết
git add Dockerfile
git add docker-compose.yml
git add .dockerignore
git add Web/.env.example
git add .gitignore

## Commit
git commit -m "Add Docker configuration for containerization"

## Push lên GitHub
git push origin main


## 🚀 Chạy với Docker

### Yêu cầu
- Docker Desktop đã cài và đang chạy

### Các bước

1. Clone project
   git clone https://github.com/<username>/Broken_Access_Control
   cd Broken_Access_Control

2. Tạo file .env từ template
   cp Web/.env.example Web/.env
   # Sau đó chỉnh sửa Web/.env với thông tin của bạn

3. Chạy Docker
   docker compose up --build

4. Mở trình duyệt
   http://localhost:5000
 

git add README.md
git commit -m "Add README with Docker setup instructions"
git push origin master


git clone https://github.com/<username>/Broken_Access_Control
cd Broken_Access_Control

# Tạo file .env
cp Web/.env.example Web/.env   # Mac/Linux
copy Web\.env.example Web\.env  # Windows

# Chạy
docker compose up --build