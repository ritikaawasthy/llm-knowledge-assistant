FROM python:3.11-slim

# Prevents Python from writing pyc files and buffers logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install -y \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# app requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the proj
COPY . .

# collect all static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "knowledge_api.wsgi:application"]

