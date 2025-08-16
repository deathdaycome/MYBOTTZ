#!/usr/bin/env python3
"""
Запуск только Telegram бота без FastAPI для тестирования
"""
import asyncio
import logging
from app.config.settings import get_settings
from app.config.logging import get_logger
from app.main import TelegramBot

async def main():
    """Запуск только бота"""
    logger = get_logger(__name__)
    logger.info("🚀 Запуск Telegram бота...")
    
    try:
        bot = TelegramBot()
        logger.info("✅ Бот инициализирован")
        
        await bot.run()
        logger.info("✅ Бот запущен в режиме polling")
        
        # Ждем бесконечно
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка бота...")
        await bot.stop()
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())