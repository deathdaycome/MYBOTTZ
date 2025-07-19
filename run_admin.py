#!/usr/bin/env python3
"""
Скрипт запуска только админ панели
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def run_admin_panel():
    """Запускает только админ панель"""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from app.admin.app import admin_router
    from app.config.settings import settings
    from app.database.database import init_db
    
    # Инициализируем базу данных
    init_db()
    
    # Создаем FastAPI приложение
    app = FastAPI(title="Bot Admin Panel", description="Админ панель для Telegram бота")
    
    # Подключаем статические файлы
    try:
        app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")
    except Exception as e:
        print(f"⚠️  Не удалось подключить статические файлы: {e}")
    
    # Подключаем админ роуты
    app.include_router(admin_router, prefix="/admin")
    
    # Редирект с корня на админку
    @app.get("/")
    async def redirect_to_admin():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/admin/")
    
    # Конфигурация сервера
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",  # Локальный доступ для безопасности
        port=settings.ADMIN_PORT,
        reload=False,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    print(f"🚀 Админ панель запущена на http://127.0.0.1:{settings.ADMIN_PORT}")
    print(f"📊 Перейдите по адресу: http://127.0.0.1:{settings.ADMIN_PORT}/admin/")
    print(f"👤 Логин: {settings.ADMIN_USERNAME}")
    print(f"🔐 Пароль: {settings.ADMIN_PASSWORD}")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    await server.serve()

def main():
    """Главная функция"""
    print("🔧 Запуск админ панели...")
    print("=" * 50)
    
    try:
        asyncio.run(run_admin_panel())
    except KeyboardInterrupt:
        print("\n👋 Админ панель остановлена пользователем.")
    except Exception as e:
        print(f"❌ Ошибка при запуске админ панели: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
