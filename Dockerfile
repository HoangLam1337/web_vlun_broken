FROM python:3.11-slim

WORKDIR /app

# Cài dependencies
COPY Web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source
COPY Web/ .

EXPOSE 5000

CMD ["python", "app.py"]