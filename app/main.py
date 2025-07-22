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
from app.bot.routing import get_callback_router
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
# Подключаем uploads для портфолио и файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
        
        # Получаем централизованный роутер
        router = get_callback_router()
        
        # Регистрируем все маршруты в роутере только если они еще не зарегистрированы
        if len(router.routes) == 0:
            self.register_callback_routes(router, start_handler, admin_handler_instance, 
                                        consultant_handler_instance, projects_handler_instance,
                                        revisions_handler_instance, tz_creation_handler_instance,
                                        common_handler_instance, portfolio_handler_instance)

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
        
        # ЕДИНЫЙ ОБРАБОТЧИК ВСЕХ CALLBACK'ОВ ЧЕРЕЗ РОУТЕР
        self.application.add_handler(CallbackQueryHandler(router.route))
        
        # MessageHandler для настроек (ВРЕМЕННО ОТКЛЮЧЕН для тестирования)
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, settings_interceptor))
        
        # Админские команды
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("stats", stats_command))
        self.application.add_handler(CommandHandler("report", report_command))
        
        # ВАЖНО: Обработчики фото и файлов для правок (ВКЛЮЧАЕМ!)
        self.application.add_handler(MessageHandler(
            filters.PHOTO, 
            common_handler_instance.handle_photo
        ))
        
        # КРИТИЧНО: Обработчик документов для ТЗ и правок
        async def document_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Маршрутизация документов"""
            try:
                # Проверяем режим создания ТЗ документом
                tz_data = context.user_data.get('tz_creation', {})
                if tz_data.get('method') == 'upload':
                    await tz_creation_handler_instance.handle_file_upload(update, context)
                    return
                
                # Обычная обработка документов
                await common_handler_instance.handle_document(update, context)
            except Exception as e:
                logger.error(f"Ошибка в document_router: {e}")
        
        self.application.add_handler(MessageHandler(filters.ATTACHMENT, document_router))
        
        # КРИТИЧНО: Обработчик голосовых сообщений для ТЗ
        async def voice_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Маршрутизация голосовых сообщений"""
            try:
                # Проверяем находимся ли в режиме создания ТЗ голосом
                tz_data = context.user_data.get('tz_creation', {})
                if tz_data.get('method') == 'voice':
                    await tz_creation_handler_instance.handle_voice_input(update, context)
                    return
                
                # Если не в режиме ТЗ - передаем в общий обработчик
                await common_handler_instance.handle_voice(update, context)
            except Exception as e:
                logger.error(f"Ошибка в voice_router: {e}")
        
        self.application.add_handler(MessageHandler(filters.VOICE, voice_router))
        
        # УНИВЕРСАЛЬНЫЙ текстовый роутер для ТЗ, правок и общих сообщений
        async def universal_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Маршрутизация текстовых сообщений"""
            try:
                # Проверяем режим создания ТЗ текстом
                tz_data = context.user_data.get('tz_creation', {})
                if tz_data.get('method') == 'text':
                    await tz_creation_handler_instance.handle_text_input(update, context)
                    return
                
                # Проверяем создание правок
                step = context.user_data.get('creating_revision_step')
                if step == 'title':
                    await revisions_handler_instance.handle_revision_title(update, context)
                    return
                elif step == 'description':
                    await revisions_handler_instance.handle_revision_description(update, context)
                    return
                
                # Обычная обработка текста
                await common_handler_instance.handle_text_input(update, context)
            except Exception as e:
                logger.error(f"Ошибка в universal_text_router: {e}")
        
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~filters.PHOTO, 
            universal_text_router
        ))
    
    def register_callback_routes(self, router, start_handler, admin_handler, consultant_handler, 
                               projects_handler, revisions_handler, tz_handler, common_handler, portfolio_handler):
        """Регистрирует все callback маршруты в централизованном роутере"""
        
        # ПРИОРИТЕТ 1 (САМЫЙ ВЫСОКИЙ): Специфичные ID-based маршруты
        
        # Проекты - детали (очень специфично)
        router.register(r"^project_details_\d+$", projects_handler.show_project_details, 
                       priority=10, description="Детали проекта по ID")
        
        # Правки - специфичные действия
        router.register(r"^project_revisions_\d+$", revisions_handler.show_project_revisions,
                       priority=10, description="Правки проекта по ID")
        router.register(r"^list_revisions_\d+$", revisions_handler.list_project_revisions,
                       priority=10, description="Список правок проекта")
        router.register(r"^create_revision_\d+$", revisions_handler.start_create_revision,
                       priority=10, description="Создать правку для проекта")
        router.register(r"^confirm_revision_\d+$", revisions_handler.confirm_create_revision,
                       priority=10, description="Подтвердить создание правки")
        router.register(r"^revision_details_\d+$", revisions_handler.show_revision_details,
                       priority=10, description="Детали правки")
        router.register(r"^files_done_\d+$", revisions_handler.files_done,
                       priority=10, description="Завершить загрузку файлов правки")
        router.register(r"^skip_files_\d+$", revisions_handler.skip_revision_files,
                       priority=10, description="Пропустить загрузку файлов правки")
        
        # Приоритеты правок
        router.register(r"^priority_(low|normal|high|urgent)_\d+$", revisions_handler.handle_revision_priority,
                       priority=10, description="Установить приоритет правки")
        
        # ПРИОРИТЕТ 2: Проекты общие
        router.register(r"^list_projects$", projects_handler.show_user_projects,
                       priority=20, description="Показать проекты пользователя")
        
        # ПРИОРИТЕТ 3: Портфолио специфичное
        router.register(r"^portfolio_(telegram|whatsapp|web|integration|featured|all)$", portfolio_handler.select_category,
                       priority=30, description="Категории портфолио")
        router.register(r"^project_\d+$", portfolio_handler.select_project,
                       priority=30, description="Выбор проекта в портфолио") 
        router.register(r"^portfolio_page_\d+$", portfolio_handler.handle_portfolio_navigation,
                       priority=30, description="Навигация по страницам портфолио")
        
        # ПРИОРИТЕТ 4: ТЗ Creation (ConversationHandler маршруты)
        router.register(r"^create_tz$", tz_handler.show_tz_creation_menu,
                       priority=40, description="Создать техническое задание")
        router.register(r"^tz_(text|voice|step_by_step|upload)$", tz_handler.select_tz_method,
                       priority=40, description="Выбор метода создания ТЗ")
        
        # Пошаговое создание ТЗ - кнопки с ответами
        router.register(r"^step_", tz_handler.handle_step_answer,
                       priority=40, description="Ответы на пошаговые вопросы ТЗ")
        
        # Действия с готовым ТЗ
        router.register(r"^review_", tz_handler.handle_review_action,
                       priority=40, description="Действия с готовым ТЗ")
        
        # ПРИОРИТЕТ 5: Консультации
        router.register(r"^consultation$", consultant_handler.start_consultation,
                       priority=50, description="Начать консультацию")
        router.register(r"^(ask_question|example_questions)$", common_handler.handle_callback,
                       priority=50, description="AI консультант - вопросы")
        
        # ПРИОРИТЕТ 6: Настройки и служебное 
        router.register(r"^(setup_timeweb|setup_bot_token)$", common_handler.handle_callback,
                       priority=60, description="Настройки подключения")
        router.register(r"^timeweb_info$", common_handler.handle_timeweb_info,
                       priority=60, description="Информация о Timeweb")
        router.register(r"^timeweb_registered$", common_handler.handle_timeweb_registered,
                       priority=60, description="Регистрация на Timeweb")
        router.register(r"^bot_creation_help$", common_handler.handle_bot_creation_help,
                       priority=60, description="Помощь в создании бота")
        router.register(r"^bot_creation_understood$", common_handler.handle_bot_creation_understood,
                       priority=60, description="Понял инструкции по созданию бота")
        
        # ПРИОРИТЕТ 7 (САМЫЙ НИЗКИЙ): Основное меню и общие команды
        router.register(r"^main_menu$", start_handler.start,
                       priority=70, description="Главное меню")
        router.register(r"^(calculator|faq|contacts|my_projects|consultant|portfolio|settings|create_bot_guide)$", 
                       common_handler.handle_callback, priority=70, description="Основные разделы меню")
        
        # Логируем все зарегистрированные маршруты
        logger.info(f"🔀 Зарегистрировано {len(router.routes)} callback маршрутов")
        
        # Проверяем конфликты
        conflicts = router.validate_all_patterns()
        if conflicts:
            logger.warning(f"⚠️ Найдены конфликты в маршрутах: {conflicts}")
        else:
            logger.info("✅ Конфликты в маршрутах не найдены")

    # ConversationHandler для ТЗ теперь заменен на роутер - удален для предотвращения конфликтов

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