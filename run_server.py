#!/usr/bin/env python3
"""
Серверный скрипт запуска для продакшена
Настроен для работы с внешним IP адресом
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Серверные настройки
SERVER_IP = "147.45.215.199"
SERVER_PORT = 8001

async def run_server():
    """Запускает сервер для продакшена"""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from app.admin.app import admin_router
    from app.config.settings import settings
    from app.database.database import init_db
    
    # Инициализируем базу данных
    init_db()
    
    # Создаем FastAPI приложение
    app = FastAPI(
        title="Bot Admin Panel", 
        description="Админ панель для Telegram бота (Продакшен)",
        version="1.0.0"
    )
    
    # Подключаем статические файлы
    try:
        app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    except Exception as e:
        print(f"⚠️  Не удалось подключить статические файлы: {e}")
    
    # Подключаем админ роуты
    app.include_router(admin_router, prefix="/admin")
    
    # Редирект с корня на админку
    @app.get("/")
    async def redirect_to_admin():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/admin/")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "server": SERVER_IP, "port": SERVER_PORT}
    
    # Конфигурация сервера для продакшена
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",  # Слушаем на всех интерфейсах
        port=SERVER_PORT,
        reload=False,
        access_log=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    print("=" * 60)
    print("🚀 ЗАПУСК ПРОДАКШЕН СЕРВЕРА")
    print("=" * 60)
    print(f"🌐 Внешний адрес: http://{SERVER_IP}:{SERVER_PORT}")
    print(f"🔗 Админ панель: http://{SERVER_IP}:{SERVER_PORT}/admin/")
    print(f"🏥 Health check: http://{SERVER_IP}:{SERVER_PORT}/health")
    print(f"👤 Логин: {settings.ADMIN_USERNAME}")
    print(f"🔐 Пароль: {settings.ADMIN_PASSWORD}")
    print("=" * 60)
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    await server.serve()

def main():
    """Главная функция"""
    print("🔧 Запуск продакшен сервера...")
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем.")
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()