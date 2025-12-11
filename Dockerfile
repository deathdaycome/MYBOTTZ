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
    pip install --no-cache-dir -r requirements.txt || true && \
    pip install --no-cache-dir websockets wsproto uvicorn[standard] requests httpx aiohttp fastapi sqlalchemy python-telegram-bot aiogram openai pydantic pydantic-settings python-jose passlib python-multipart bcrypt aiofiles python-dotenv jinja2 PyPDF2 pdfplumber python-docx openpyxl Pillow nest-asyncio redis alembic SpeechRecognition pydub APScheduler python-dateutil pytz xlsxwriter cryptography marshmallow structlog prometheus-client asyncpg

# Копируем код приложения
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY start_services.sh ./

# Копируем собранный Mini App из первой стадии
COPY --from=miniapp-builder /app/miniapp/dist ./miniapp/dist

# Создаём необходимые директории и делаем скрипт исполняемым
RUN mkdir -p /app/data /app/uploads /app/logs && \
    chmod +x /app/start_services.sh

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

# Запускаем оба сервиса (API + Admin)
CMD ["/app/start_services.sh"]