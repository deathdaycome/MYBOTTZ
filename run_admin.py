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
    
    # Запускаем Avito polling сервис в фоне
    async def start_avito_polling():
        try:
            from app.services.avito_polling_service import polling_service
            from app.config.settings import settings
            
            print("🔔 Проверяем настройки для Avito polling...")
            
            if not settings.BOT_TOKEN:
                print("⚠️  BOT_TOKEN не установлен - уведомления недоступны")
                return
                
            if not settings.ADMIN_CHAT_ID:
                print("⚠️  ADMIN_CHAT_ID не установлен - уведомления недоступны")
                return
                
            print(f"✅ BOT_TOKEN: {'***' + settings.BOT_TOKEN[-4:] if settings.BOT_TOKEN else 'НЕ ЗАДАН'}")
            print(f"✅ ADMIN_CHAT_ID: {settings.ADMIN_CHAT_ID}")
            
            print("🔔 Запускаем Avito polling сервис для уведомлений...")
            
            # Проверяем что сервис инициализирован правильно
            print(f"📋 Polling активен: {polling_service.polling_active}")
            print(f"🤖 Автоответы: {polling_service.auto_response_enabled}")
            print(f"📞 Notification service: {polling_service.notification_service is not None}")
            
            # Запускаем polling в background task
            task = asyncio.create_task(polling_service.start_polling(interval=30))
            print("✅ Avito polling сервис запущен в фоне")
            
            # Ждем немного, чтобы увидеть первые логи
            await asyncio.sleep(2)
            print("🔍 Первый цикл polling должен начаться через 28 секунд")
            
        except Exception as e:
            print(f"❌ Ошибка запуска Avito polling: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    @app.on_event("startup")
    async def startup_event():
        await start_avito_polling()
    
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
        host="0.0.0.0",  # Внешний доступ
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
