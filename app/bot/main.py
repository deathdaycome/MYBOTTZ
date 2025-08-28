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
from app.bot.handlers.money_management import money_handler
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
    app.add_handler(CommandHandler("my_id", start_handler.my_id))
    app.add_handler(CommandHandler("admin", admin_command))
    
    logger.info("🔧 Добавляем conversation handlers...")
    # Conversation handlers
    if hasattr(tz_handler, 'conversation_handler'):
        app.add_handler(tz_handler.conversation_handler)
    
    if hasattr(portfolio_handler, 'conversation_handler'):
        app.add_handler(portfolio_handler.conversation_handler)
    
    # Bot creation conversation handler - ОТКЛЮЧЕН, чтобы не мешать настройкам
    # bot_token_conversation = ConversationHandler(
    #     entry_points=[
    #         CallbackQueryHandler(
    #             bot_creation_handler.start_bot_token_entry,
    #             pattern="^bot_enter_token$"
    #         )
    #     ],
    #     states={
    #         1: [  # ENTER_BOT_TOKEN
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, bot_creation_handler.save_bot_token)
    #         ]
    #     },
    #     fallbacks=[
    #         MessageHandler(filters.COMMAND, bot_creation_handler.cancel_bot_token_entry)
    #     ]
    # )
    # app.add_handler(bot_token_conversation)
    
    logger.info("🔧 Добавляем callback query handlers...")
    # Callback query handlers
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.show_portfolio_categories, 
        pattern="^portfolio$"
    ))
    
    app.add_handler(CallbackQueryHandler(
        common_handler.handle_callback, 
        pattern="^(main_menu|back|consultant|projects|about|calculator|faq|consultation|contacts|my_projects|create_tz|create_bot_guide|settings|setup_timeweb|setup_bot_token|send_bot_token|get_telegram_id|get_chat_id|send_chat_id|detailed_chat_instructions|timeweb_registered|admin_console|admin_money|upload_receipt|transaction_.*|my_transactions|view_income|view_expenses|money_analytics|money_categories)$"
    ))
    
    # Revision handlers
    app.add_handler(CallbackQueryHandler(
        revisions_handler.show_project_revisions,
        pattern="^project_revisions_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.list_project_revisions,
        pattern="^list_revisions_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.start_create_revision,
        pattern="^create_revision_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.show_revision_details,
        pattern="^revision_details_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.handle_revision_priority,
        pattern="^priority_(low|normal|high|urgent)_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.confirm_create_revision,
        pattern="^confirm_revision_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.skip_revision_files,
        pattern="^skip_files_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        revisions_handler.files_done,
        pattern="^files_done_"
    ))
    
    # Добавляем обработчики для всех callback кнопок правок
    app.add_handler(CallbackQueryHandler(
        common_handler.handle_callback,
        pattern="^(skip_files_|files_done_|priority_|confirm_revision_|revision_details_|list_revisions_|create_revision_)"
    ))
    
    # Projects handlers
    app.add_handler(CallbackQueryHandler(
        projects_handler.show_project_details,
        pattern="^project_details_"
    ))
    
    # Portfolio handlers
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.show_project_details,
        pattern="^project_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.show_category_portfolio,
        pattern="^portfolio_category_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.show_portfolio_page,
        pattern="^page_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.show_project_gallery,
        pattern="^gallery_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.like_project,
        pattern="^like_"
    ))
    
    app.add_handler(CallbackQueryHandler(
        portfolio_handler.navigate_project,
        pattern="^portfolio_nav_"
    ))
    
    # Дополнительные обработчики для timeweb
    app.add_handler(CallbackQueryHandler(
        common_handler.handle_timeweb_registered,
        pattern="^timeweb_registered"
    ))
    
    app.add_handler(CallbackQueryHandler(
        common_handler.handle_timeweb_info,
        pattern="^timeweb_info$"
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
    # Message handlers - ФОТО ОБРАБОТЧИК СНАЧАЛА
    app.add_handler(MessageHandler(
        filters.PHOTO,
        common_handler.handle_photo
    ))
    
    # Message handlers - ВИДЕО ОБРАБОТЧИК
    app.add_handler(MessageHandler(
        filters.VIDEO,
        common_handler.handle_video
    ))
    
    # Message handlers - ДОКУМЕНТЫ ОБРАБОТЧИК  
    app.add_handler(MessageHandler(
        filters.ATTACHMENT,
        common_handler.handle_document
    ))
    
    # Message handlers - ТЕКСТ ОБРАБОТЧИК (исключаем фото и видео)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.PHOTO & ~filters.VIDEO,
        common_handler.handle_text_input
    ))
    
    # Message handlers - УНИВЕРСАЛЬНЫЙ ОБРАБОТЧИК (ПОСЛЕДНИЙ)
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND & ~filters.PHOTO & ~filters.VIDEO & ~filters.ATTACHMENT,
        common_handler.handle_any_message
    ))
    
    # Убираем универсальный обработчик - он вызывает конфликты
    
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
