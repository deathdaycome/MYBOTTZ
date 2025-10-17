# ============================================
# Стадия 1: Сборка Mini App (Frontend)
# ============================================
FROM node:18-alpine AS miniapp-builder

WORKDIR /app/miniapp

# Копируем package файлы для кеширования слоёв
COPY miniapp/package*.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходники
COPY miniapp/ ./

# Собираем production версию
RUN npm run build

# ============================================
# Стадия 2: Основной образ (Backend + Bot)
# ============================================
FROM python:3.10-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем requirements для кеширования слоёв
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/
COPY migrations/ ./migrations/

# Копируем собранный Mini App из первой стадии
COPY --from=miniapp-builder /app/miniapp/dist ./miniapp/dist

# Создаём необходимые директории
RUN mkdir -p /app/data /app/uploads /app/logs

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:////app/data/bot.db \
    UPLOAD_PATH=/app/uploads \
    LOG_FILE=/app/logs/bot.log

# Открываем порты (8000 - API, 8001 - Admin)
EXPOSE 8000 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Запускаем приложение
CMD ["sh", "-c", "\
    python3 migrations/add_revision_progress_timer.py 2>/dev/null || true && \
    python3 migrations/add_task_attachments.py 2>/dev/null || true && \
    python3 migrations/create_crm_tables.py 2>/dev/null || true && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 \
"]