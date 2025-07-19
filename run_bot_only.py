#!/usr/bin/env python3
"""
Скрипт для запуска только Telegram бота без FastAPI
"""
import asyncio
import logging
from app.config.settings import get_settings
from app.bot.main import setup_handlers
from app.database.database import init_db
from telegram.ext import Application

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    try:
        settings = get_settings()
        if not settings.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен")
            return
        
        # Инициализация базы данных
        init_db()
        
        # Создание приложения
        app = Application.builder().token(settings.BOT_TOKEN).build()
        
        # Настройка обработчиков
        setup_handlers(app)
        
        logger.info("🤖 Запуск Telegram бота...")
        
        # Запуск бота
        await app.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query', 'inline_query']
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())