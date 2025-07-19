#!/usr/bin/env python3
"""
Тестовый сервер только для админки без Telegram бота
"""

import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Инициализируем логирование ПЕРВЫМ
from app.config.logging import setup_logging, get_logger
logger = get_logger(__name__)

from app.admin.app import admin_router
from app.database.database import init_db
from app.utils.helpers import format_datetime, format_currency, time_ago

# Создаем таблицы при запуске
logger.info("Инициализация базы данных...")
init_db()
logger.info("База данных инициализирована")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Bot Business Card Admin",
    description="Панель управления для Telegram-бота визитки.",
    version="0.1.0"
)

# Подключаем роутер админки
app.include_router(admin_router, prefix="/admin")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы."""
    return {"message": "Тестовый сервер админ-панели работает. Перейдите на /admin для входа."}

@app.get("/test")
async def test():
    """Тестовый эндпоинт для проверки работы."""
    return {"status": "ok", "message": "Тестовый сервер работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)