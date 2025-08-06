#!/usr/bin/env python3
"""
Простой запуск Telegram бота
"""
import logging
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent))

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    PicklePersistence,
)

from app.config.settings import get_settings
from app.bot.handlers.start import StartHandler
from app.bot.handlers.common import CommonHandler
from app.bot.handlers.money_management import money_handler
from app.database.database import init_db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Главная функция запуска бота"""
    try:
        # Получаем настройки
        settings = get_settings()
        
        if not settings.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен в переменных окружения")
            return
        
        logger.info("🔧 Инициализация базы данных...")
        # Инициализируем базу данных
        init_db()
        
        # Создаем persistence для сохранения данных
        logger.info("🔧 Настройка persistence...")
        persistence_file = Path("data/bot_persistence.pkl")
        persistence_file.parent.mkdir(exist_ok=True)
        persistence = PicklePersistence(filepath=str(persistence_file))
        
        # Создаем приложение
        logger.info("🔧 Создание приложения...")
        app = Application.builder() \
            .token(settings.BOT_TOKEN) \
            .persistence(persistence) \
            .build()
        
        # Инициализируем обработчики
        logger.info("🔧 Инициализация обработчиков...")
        start_handler = StartHandler()
        common_handler = CommonHandler()
        
        # Основные команды
        logger.info("🔧 Добавление команд...")
        app.add_handler(CommandHandler("start", start_handler.start))
        app.add_handler(CommandHandler("help", start_handler.help))
        app.add_handler(CommandHandler("menu", start_handler.menu))
        
        # Callback обработчики
        logger.info("🔧 Добавление callback обработчиков...")
        app.add_handler(CallbackQueryHandler(common_handler.handle_callback))
        
        # Обработчики фото и документов для финансовой системы
        logger.info("🔧 Добавление обработчиков файлов...")
        app.add_handler(MessageHandler(filters.PHOTO, money_handler.handle_document_upload))
        app.add_handler(MessageHandler(filters.ATTACHMENT, money_handler.handle_document_upload))
        
        # Текстовые сообщения
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            common_handler.handle_text_input
        ))
        
        # Error handler
        async def error_handler(update, context):
            logger.error(f"Exception while handling an update: {context.error}")
        
        app.add_error_handler(error_handler)
        
        logger.info("🤖 Запуск Telegram бота...")
        logger.info("✅ Все обработчики настроены!")
        
        # Запускаем бота
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    main()