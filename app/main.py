import logging
import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
    PicklePersistence,
    ContextTypes,
)

from app.config.settings import get_settings
from app.config.logging import get_logger
from app.bot.handlers.start import StartHandler
from app.bot.handlers.admin import AdminHandler, admin_command, stats_command, report_command
from app.bot.handlers.consultant import ConsultantHandler
from app.bot.handlers.projects import ProjectsHandler
from app.bot.handlers.revisions import RevisionsHandler
from app.bot.handlers.tz_creation import TZCreationHandler
from app.bot.handlers.common import CommonHandler
from app.bot.handlers.portfolio import PortfolioHandler
from app.admin.app import admin_router, templates
from app.database.database import get_db, SessionLocal, init_db
from app.utils.helpers import format_datetime, format_currency, time_ago

# Логгер для main
logger = get_logger(__name__)

# Создаем таблицы при запуске
init_db()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Bot Business Card Admin",
    description="Панель управления для Telegram-бота визитки.",
    version="0.1.0"
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"HTTP {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # Логируем время выполнения
    process_time = time.time() - start_time
    logger.info(f"HTTP {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response

# Подключаем роутер админки
app.include_router(admin_router, prefix="/admin")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Telegram Bot Initialization ---
class TelegramBot:
    def __init__(self):
        """Инициализация бота, логгера и других компонентов."""
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        persistence = PicklePersistence(filepath=self.settings.bot_persistence_file)
        self.application = (
            Application.builder()
            .token(self.settings.bot_token)
            .persistence(persistence)
            .build()
        )
        
        self.setup_handlers()
        self.setup_jinja()

    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений."""
        start_handler = StartHandler()
        admin_handler_instance = AdminHandler()
        consultant_handler_instance = ConsultantHandler()
        projects_handler_instance = ProjectsHandler()
        revisions_handler_instance = RevisionsHandler()
        tz_creation_handler_instance = TZCreationHandler()
        common_handler_instance = CommonHandler()
        portfolio_handler_instance = PortfolioHandler()

        # КРИТИЧЕСКИЙ ПРИОРИТЕТ: Специальный перехватчик (САМЫЙ ПЕРВЫЙ!)
        async def settings_interceptor(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Специальный перехватчик для настроек"""
            user_id = update.effective_user.id
            message_text = update.message.text if update.message else ""
            
            # НЕ обрабатываем команды - пусть проходят к CommandHandler
            if message_text.startswith('/'):
                await common_handler_instance.handle_text_input(update, context)
                return
            
            # Проверяем флаги настроек только для обычных сообщений
            if context.user_data.get('waiting_bot_token_settings'):
                await common_handler_instance.save_bot_token_settings(update, context)
                return
                
            if context.user_data.get('waiting_timeweb_settings'):
                await common_handler_instance.save_timeweb_settings(update, context)
                return
                
            # Если не настройки - передаем дальше
            await common_handler_instance.handle_text_input(update, context)
        
        # Основные команды (ДОЛЖНЫ БЫТЬ ПЕРВЫМИ!)
        self.application.add_handler(CommandHandler("start", start_handler.start))
        self.application.add_handler(CommandHandler("help", start_handler.help))
        self.application.add_handler(CommandHandler("menu", start_handler.menu))
        self.application.add_handler(CommandHandler("cancel", start_handler.cancel))
        
        # MessageHandler для настроек (ВРЕМЕННО ОТКЛЮЧЕН для тестирования)
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, settings_interceptor))
        
        # Админские команды
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("stats", stats_command))
        self.application.add_handler(CommandHandler("report", report_command))
        

        # ConversationHandlers
        tz_conv_handler = self.create_tz_conversation_handler(tz_creation_handler_instance, start_handler)
        self.application.add_handler(tz_conv_handler)

        # Отключаем portfolio conversation handler, так как используем прямые обработчики
        # portfolio_conv_handler = self.create_portfolio_conversation_handler(portfolio_handler_instance, start_handler)
        # self.application.add_handler(portfolio_conv_handler)

        # Обработчики колбэков
        self.application.add_handler(CallbackQueryHandler(projects_handler_instance.show_user_projects, pattern="^list_projects"))
        self.application.add_handler(CallbackQueryHandler(projects_handler_instance.show_project_details, pattern="^project_details_"))
        self.application.add_handler(CallbackQueryHandler(consultant_handler_instance.start_consultation, pattern="^consultation"))
        
        # Обработчики основных кнопок меню
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_callback, pattern="^(main_menu|calculator|faq|consultation|contacts|my_projects|consultant|portfolio|settings)$"))
        
        # Обработчики настроек
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_callback, pattern="^(setup_timeweb|setup_bot_token)$"))
        
        # Обработчики портфолио
        self.application.add_handler(CallbackQueryHandler(portfolio_handler_instance.select_category, pattern="^portfolio_(telegram|whatsapp|web|integration|featured|all)$"))
        self.application.add_handler(CallbackQueryHandler(portfolio_handler_instance.select_project, pattern=r"^project_\d+$"))
        self.application.add_handler(CallbackQueryHandler(portfolio_handler_instance.handle_portfolio_navigation, pattern=r"^portfolio_page_\d+$"))
        
        # Обработчики AI консультанта
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_callback, pattern="^(ask_question|example_questions)$"))
        
        # Обработчики правок
        self.application.add_handler(CallbackQueryHandler(revisions_handler_instance.show_project_revisions, pattern="^project_revisions_"))
        self.application.add_handler(CallbackQueryHandler(revisions_handler_instance.list_project_revisions, pattern="^list_revisions_"))
        self.application.add_handler(CallbackQueryHandler(revisions_handler_instance.start_create_revision, pattern="^create_revision_"))
        self.application.add_handler(CallbackQueryHandler(revisions_handler_instance.handle_revision_priority, pattern="^priority_(low|normal|high|urgent)_"))
        self.application.add_handler(CallbackQueryHandler(revisions_handler_instance.confirm_create_revision, pattern="^confirm_revision_"))
        self.application.add_handler(CallbackQueryHandler(revisions_handler_instance.show_revision_details, pattern="^revision_details_"))
        
        # ОТКЛЮЧЕНЫ: Обработчики текстовых сообщений для правок - конфликтуют с настройками
        # self.application.add_handler(MessageHandler(
        #     filters.TEXT & ~filters.COMMAND, 
        #     revisions_handler_instance.handle_revision_title
        # ))
        # self.application.add_handler(MessageHandler(
        #     filters.TEXT & ~filters.COMMAND, 
        #     revisions_handler_instance.handle_revision_description
        # ))
        
        # Обработчики Timeweb (оставляем для совместимости)
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_timeweb_info, pattern="^timeweb_info"))
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_timeweb_registered, pattern="^timeweb_registered"))
        
        # Обработчики создания бота (оставляем для совместимости)
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_bot_creation_help, pattern="^bot_creation_help"))
        self.application.add_handler(CallbackQueryHandler(common_handler_instance.handle_bot_creation_understood, pattern="^bot_creation_understood"))
        
        # MessageHandler для текста (В САМОМ КОНЦЕ - последний приоритет)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, common_handler_instance.handle_text_input))

    def create_tz_conversation_handler(self, tz_handler, start_handler):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(tz_handler.show_tz_creation_menu, pattern="^create_tz$")],
            states={
                tz_handler.TZ_METHOD: [CallbackQueryHandler(tz_handler.select_tz_method, pattern="^tz_(text|voice|step_by_step|upload)$")],
                tz_handler.TZ_TEXT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, tz_handler.handle_text_input)],
                tz_handler.TZ_VOICE_INPUT: [MessageHandler(filters.VOICE, tz_handler.handle_voice_input)],
                tz_handler.TZ_STEP_BY_STEP: [CallbackQueryHandler(tz_handler.handle_step_answer, pattern="^step_")],
                tz_handler.TZ_FILE_UPLOAD: [MessageHandler(filters.Document.ALL, tz_handler.handle_file_upload)],
                tz_handler.TZ_REVIEW: [CallbackQueryHandler(tz_handler.handle_review_action, pattern="^review_")],
            },
            fallbacks=[CommandHandler("cancel", start_handler.cancel)]
        )

    def create_portfolio_conversation_handler(self, portfolio_handler, start_handler):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(portfolio_handler.show_portfolio_page, pattern="^portfolio_")],
            states={
                portfolio_handler.CATEGORY: [CallbackQueryHandler(portfolio_handler.select_category, pattern="^category_")],
                portfolio_handler.PROJECT: [CallbackQueryHandler(portfolio_handler.select_project, pattern="^project_")],
            },
            fallbacks=[CommandHandler("cancel", start_handler.cancel)]
        )

    def setup_jinja(self):
        """Настройка Jinja2 для рендеринга сообщений."""
        templates.env.globals['format_datetime'] = format_datetime
        templates.env.globals['format_currency'] = format_currency
        templates.env.globals['time_ago'] = time_ago

    async def run(self):
        """Запуск бота в режиме polling."""
        self.logger.info("Запуск бота в режиме polling...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self):
        """Остановка бота."""
        self.logger.info("Остановка бота...")
        if self.application.updater and self.application.updater.running:
            await self.application.updater.stop()
        await self.application.stop()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Bot Business Card Admin",
    description="Панель управления для Telegram-бота визитки.",
    version="0.1.0"
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"HTTP {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # Логируем время выполнения
    process_time = time.time() - start_time
    logger.info(f"HTTP {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response

# Подключаем роутер админки
app.include_router(admin_router, prefix="/admin")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Telegram Bot Initialization ---
bot_instance = TelegramBot()

@app.on_event("startup")
async def startup_event():
    """Запуск Telegram-бота при старте FastAPI"""
    bot_instance.logger.info("🚀 Запускаем Telegram-бота в фоновом режиме...")
    asyncio.create_task(bot_instance.run())

@app.on_event("shutdown")
async def shutdown_event():
    """Остановка Telegram-бота при выключении FastAPI"""
    bot_instance.logger.info("🛑 Останавливаем Telegram-бота...")
    await bot_instance.stop()

# --- Webhook (если используется) ---
@app.post("/webhook")
async def webhook(request: Request):
    """Обработка входящих обновлений от Telegram в режиме вебхука."""
    data = await request.json()
    update = Update.de_json(data, bot_instance.application.bot)
    await bot_instance.application.process_update(update)
    return {"status": "ok"}

@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы."""
    return {"message": "Сервер админ-панели работает. Перейдите на /admin для входа."}

@app.get("/test")
async def test():
    """Тестовый эндпоинт для проверки работы."""
    return {"status": "ok", "message": "Сервер работает"}

@app.get("/admin-test")
async def admin_test():
    """Тестовый эндпоинт для проверки админки."""
    return {"status": "ok", "message": "Админка доступна", "routes": "admin routes working"}

@app.get("/admin-debug")
async def admin_debug():
    """Отладочный эндпоинт для проверки админки без аутентификации."""
    from app.config.settings import get_settings
    settings = get_settings()
    return {
        "status": "ok", 
        "message": "Админка работает без аутентификации",
        "admin_username": settings.ADMIN_USERNAME,
        "admin_port": settings.ADMIN_PORT,
        "database_status": "connected"
    }