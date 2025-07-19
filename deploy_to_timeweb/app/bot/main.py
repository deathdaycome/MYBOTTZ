"""
Основной модуль Telegram бота
"""
import logging
import asyncio
import sys
from pathlib import Path

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
    PicklePersistence,
)

from app.config.settings import get_settings
from app.bot.handlers.start import StartHandler
from app.bot.handlers.admin import AdminHandler, admin_command
from app.bot.handlers.consultant import ConsultantHandler
from app.bot.handlers.projects import ProjectsHandler
from app.bot.handlers.revisions import RevisionsHandler
from app.bot.handlers.tz_creation import TZCreationHandler
from app.bot.handlers.common import CommonHandler
from app.bot.handlers.portfolio import PortfolioHandler
from app.bot.handlers.bot_creation import BotCreationHandler
from app.database.database import init_db

logger = logging.getLogger(__name__)


async def error_handler(update, context):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")


def setup_handlers(app: Application):
    """Настройка обработчиков бота"""
    
    logger.info("🔧 Настройка обработчиков бота...")
    
    # Инициализируем обработчики
    start_handler = StartHandler()
    admin_handler = AdminHandler()
    consultant_handler = ConsultantHandler()
    projects_handler = ProjectsHandler()
    revisions_handler = RevisionsHandler()
    tz_handler = TZCreationHandler()
    common_handler = CommonHandler()
    portfolio_handler = PortfolioHandler()
    bot_creation_handler = BotCreationHandler()
    
    logger.info("🔧 Добавляем команды...")
    # Команды
    app.add_handler(CommandHandler("start", start_handler.start))
    app.add_handler(CommandHandler("help", start_handler.help))
    app.add_handler(CommandHandler("admin", admin_command))
    
    logger.info("🔧 Добавляем conversation handlers...")
    # Conversation handlers
    if hasattr(tz_handler, 'conversation_handler'):
        app.add_handler(tz_handler.conversation_handler)
    
    if hasattr(portfolio_handler, 'conversation_handler'):
        app.add_handler(portfolio_handler.conversation_handler)
    
    # Bot creation conversation handler
    bot_token_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                bot_creation_handler.start_bot_token_entry,
                pattern="^bot_enter_token$"
            )
        ],
        states={
            1: [  # ENTER_BOT_TOKEN
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_creation_handler.save_bot_token)
            ]
        },
        fallbacks=[
            MessageHandler(filters.COMMAND, bot_creation_handler.cancel_bot_token_entry)
        ]
    )
    app.add_handler(bot_token_conversation)
    
    logger.info("🔧 Добавляем callback query handlers...")
    # Callback query handlers
    app.add_handler(CallbackQueryHandler(
        common_handler.handle_callback, 
        pattern="^(main_menu|back|consultant|projects|portfolio|about|calculator|faq|consultation|contacts|my_projects|create_tz|create_bot_guide)$"
    ))
    
    logger.info("🔧 Добавляем bot creation handlers...")
    # Bot creation handlers
    app.add_handler(CallbackQueryHandler(
        bot_creation_handler.show_bot_creation_guide,
        pattern="^create_bot_guide$"
    ))
    
    app.add_handler(CallbackQueryHandler(
        bot_creation_handler.show_bot_creation_steps,
        pattern="^bot_guide_steps$"
    ))
    
    logger.info("🔧 Добавляем message handlers...")
    # Message handlers
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        common_handler.handle_message
    ))
    
    app.add_handler(MessageHandler(
        filters.VOICE,
        common_handler.handle_voice
    ))
    
    app.add_handler(MessageHandler(
        filters.Document.ALL,
        common_handler.handle_document
    ))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("✅ Все обработчики настроены!")


async def main():
    """Главная функция запуска бота"""
    try:
        # Получаем настройки
        settings = get_settings()
        
        if not settings.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен в переменных окружения")
            return
        
        # Инициализируем базу данных
        init_db()
        
        # Создаем persistence для сохранения данных
        persistence_file = Path("data/bot_persistence.pkl")
        persistence_file.parent.mkdir(exist_ok=True)
        
        persistence = PicklePersistence(filepath=str(persistence_file))
        
        # Создаем приложение
        app = Application.builder() \
            .token(settings.BOT_TOKEN) \
            .persistence(persistence) \
            .build()
        
        # Инициализируем notification_service с ботом
        from app.services.notification_service import notification_service
        notification_service.set_bot(app.bot)
        
        # Настраиваем обработчики
        setup_handlers(app)
        
        logger.info("🤖 Запуск Telegram бота...")
        
        # Запускаем бота
        await app.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query', 'inline_query']
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
