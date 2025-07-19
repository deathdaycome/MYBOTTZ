#!/usr/bin/env python3
"""
Простой бот для тестирования
"""
import asyncio
import logging
from telegram.ext import Application, CommandHandler
from app.config.settings import get_settings

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я работаю!")

async def main():
    try:
        settings = get_settings()
        if not settings.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен")
            return
        
        # Создание приложения
        app = Application.builder().token(settings.BOT_TOKEN).build()
        
        # Добавление обработчиков
        app.add_handler(CommandHandler("start", start_command))
        
        logger.info("🤖 Запуск простого бота...")
        
        # Запуск бота
        await app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())