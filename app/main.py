import logging
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
from app.bot.handlers.revision_chat_handlers import RevisionChatHandlers
from app.bot.handlers.tz_creation import TZCreationHandler
from app.bot.handlers.common import CommonHandler
from app.bot.handlers.portfolio import PortfolioHandler
from app.bot.routing import get_callback_router
from app.admin.app import admin_router, templates
from app.database.database import get_db, SessionLocal, init_db
from app.utils.helpers import format_datetime, format_currency, time_ago
from app.services.avito_polling_service import polling_service

# Логгер для main
logger = get_logger(__name__)

# Создаем таблицы при запуске
# init_db()  # Временно отключено из-за проблем с portfolio

# Проверяем и исправляем структуру БД
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from startup_db_fix import ensure_db_columns
    ensure_db_columns()
    logger.info("Проверка структуры БД выполнена")
except Exception as e:
    logger.warning(f"Не удалось выполнить проверку БД: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("=" * 80)
    print("🚀🚀🚀 LIFESPAN STARTUP НАЧАЛСЯ!!!")
    print("=" * 80)
    logger.info("🚀 Запуск приложения...")

    # Запускаем Telegram-бот НАПРЯМУЮ без create_task
    try:
        print("=" * 80)
        print("📱📱📱 НАЧИНАЕМ ЗАПУСК TELEGRAM-БОТА НАПРЯМУЮ!!!")
        print("=" * 80)
        logger.info("📱 Запускаем Telegram-бот...")

        # Инициализируем бота
        print("🔧 Инициализация бота...")
        await bot_instance.application.initialize()
        print("✅ Бот инициализирован")

        # Запускаем бота
        print("🚀 Запуск бота...")
        await bot_instance.application.start()
        print("✅ Бот запущен")

        # Запускаем polling в фоне с обработкой ошибок
        async def start_polling_with_logging():
            try:
                print("📡📡📡 Запуск UPDATER.start_polling()...")
                await bot_instance.application.updater.start_polling(
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True
                )
                print("✅ Updater запущен, polling работает!")
                print("⏳ Ждём updates от Telegram...")

                # Бесконечный цикл чтобы держать polling alive
                while True:
                    await asyncio.sleep(60)
                    print("💓 Polling жив и работает...")

            except Exception as e:
                print(f"❌❌❌ ОШИБКА В POLLING: {e}")
                import traceback
                traceback.print_exc()

        asyncio.create_task(start_polling_with_logging())
        print("✅✅✅ POLLING TASK СОЗДАН! БОТ ГОТОВ К РАБОТЕ!")

    except Exception as e:
        print("=" * 80)
        print(f"❌❌❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ БОТА: {e}")
        print("=" * 80)
        logger.error(f"❌❌❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ БОТА: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise
    
    # Запускаем планировщик автоматизации
    try:
        from app.services.scheduler import scheduler
        scheduler.start()
        logger.info("✅ Планировщик автоматизации запущен")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска планировщика: {e}")
    
    # Запускаем планировщик уведомлений о задачах
    try:
        from app.services.task_scheduler import task_scheduler
        await task_scheduler.start()
        logger.info("✅ Планировщик уведомлений о задачах запущен")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска планировщика уведомлений: {e}")
    
    # Запускаем Avito polling сервис
    try:
        logger.info("🔄 Запускаем Avito polling service...")
        asyncio.create_task(polling_service.start_polling())
        logger.info("✅ Avito polling service запущен")
    except Exception as e:
        logger.error(f"Ошибка запуска Avito polling: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Остановка приложения...")
    
    # Останавливаем Telegram-бота
    bot_instance.logger.info("🛑 Останавливаем Telegram-бота...")
    await bot_instance.stop()
    
    # Останавливаем планировщик
    try:
        from app.services.scheduler import scheduler
        scheduler.stop()
        logger.info("✅ Планировщик автоматизации остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка остановки планировщика: {e}")
    
    # Останавливаем планировщик уведомлений о задачах
    try:
        from app.services.task_scheduler import task_scheduler
        await task_scheduler.stop()
        logger.info("✅ Планировщик уведомлений о задачах остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка остановки планировщика уведомлений: {e}")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Bot Business Card Admin",
    description="Панель управления для Telegram-бота визитки.",
    version="0.1.0",
    lifespan=lifespan
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nikolaevcodev.ru",
        "http://nikolaevcodev.ru",
        "http://147.45.215.199:8000",
        "https://147.45.215.199:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start_time = time.time()
    
    # Логируем входящий запрос с большей детализацией
    logger.info(f"HTTP {request.method} {request.url.path} - {request.client.host}")
    logger.debug(f"Query params: {request.query_params}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    # Логируем время выполнения и статус
    process_time = time.time() - start_time
    logger.info(f"HTTP {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    if response.status_code == 404:
        logger.warning(f"404 Not Found: {request.url.path}")
    
    return response

# Middleware для добавления templates в request.state
@app.middleware("http")
async def add_templates(request: Request, call_next):
    request.state.templates = templates
    response = await call_next(request)
    return response

# Подключаем роутер админки только с префиксом /admin
app.include_router(admin_router, prefix="/admin")

# Подключаем API для Telegram Mini App
from app.api.miniapp import router as miniapp_router
app.include_router(miniapp_router)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/admin/static", StaticFiles(directory="app/admin/static"), name="admin_static")
# Подключаем uploads для портфолио и файлов
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")
# Подключаем Mini App
app.mount("/", StaticFiles(directory="miniapp/dist", html=True), name="miniapp")

# --- Telegram Bot Initialization ---
class TelegramBot:
    def __init__(self):
        """Инициализация бота, логгера и других компонентов."""
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

        # Настройки для httpx - ФИКС СЕТЕВЫХ ПРОБЛЕМ!
        from telegram.request import HTTPXRequest
        import httpx

        # Создаём request с правильными настройками
        request = HTTPXRequest(
            connection_pool_size=100,
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
            http_version="1.1"
        )

        persistence = PicklePersistence(filepath=self.settings.bot_persistence_file)
        self.application = (
            Application.builder()
            .token(self.settings.bot_token)
            .persistence(persistence)
            .request(request)  # Используем наш настроенный request
            .get_updates_request(request)  # И для get_updates тоже
            .build()
        )
        
        self.setup_handlers()
        self.setup_jinja()

    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений."""

        # ГЛОБАЛЬНЫЙ ЛОГГЕР ВСЕХ UPDATES - САМЫЙ ПЕРВЫЙ!
        async def log_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Логирует ВСЕ updates от Telegram"""
            print("=" * 80)
            print(f"🔔🔔🔔 ПОЛУЧЕН UPDATE ОТ TELEGRAM!")
            print(f"Update ID: {update.update_id}")
            if update.message:
                print(f"📨 Тип: MESSAGE, текст: {update.message.text}")
            if update.callback_query:
                print(f"🔘 Тип: CALLBACK_QUERY, data: {update.callback_query.data}")
            print("=" * 80)

        # Добавляем глобальный обработчик ПЕРВЫМ!
        from telegram.ext import TypeHandler
        self.application.add_handler(TypeHandler(Update, log_all_updates), group=-1)

        start_handler = StartHandler()
        admin_handler_instance = AdminHandler()
        consultant_handler_instance = ConsultantHandler()
        projects_handler_instance = ProjectsHandler()
        revisions_handler_instance = RevisionsHandler()
        revision_chat_handler_instance = RevisionChatHandlers()  # ДОБАВЛЕН!
        tz_creation_handler_instance = TZCreationHandler()
        common_handler_instance = CommonHandler()
        portfolio_handler_instance = PortfolioHandler()

        # Получаем централизованный роутер
        router = get_callback_router()
        
        # Регистрируем все маршруты в роутере только если они еще не зарегистрированы
        if len(router.routes) == 0:
            self.register_callback_routes(router, start_handler, admin_handler_instance,
                                        consultant_handler_instance, projects_handler_instance,
                                        revisions_handler_instance, revision_chat_handler_instance,
                                        tz_creation_handler_instance,
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

        # MessageHandler для быстрого создания проекта
        from app.bot.handlers.quick_project_request import QuickProjectRequestHandler
        quick_project_handler_instance = QuickProjectRequestHandler()

        async def text_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Роутер для текстовых сообщений"""
            try:
                # Проверяем состояние быстрого создания проекта
                quick_state = context.user_data.get('quick_project_state')

                if quick_state == 'waiting_project_name':
                    await quick_project_handler_instance.handle_project_name(update, context)
                    return
                elif quick_state == 'waiting_project_description':
                    await quick_project_handler_instance.handle_project_description(update, context)
                    return
                elif quick_state == 'waiting_project_budget':
                    await quick_project_handler_instance.handle_project_budget(update, context)
                    return

                # Проверяем флаги настроек
                if context.user_data.get('waiting_bot_token_settings'):
                    await common_handler_instance.save_bot_token_settings(update, context)
                    return

                if context.user_data.get('waiting_timeweb_settings'):
                    await common_handler_instance.save_timeweb_settings(update, context)
                    return

                # Остальная обработка текста
                await common_handler_instance.handle_text_input(update, context)

            except Exception as e:
                logger.error(f"Ошибка в text_message_router: {e}")
                await common_handler_instance.handle_text_input(update, context)

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_router))
        
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
        
        self.application.add_handler(MessageHandler(filters.ATTACHMENT & ~filters.VOICE, document_router))
        
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
                elif tz_data.get('method') == 'own':
                    await tz_creation_handler_instance.handle_own_tz_input(update, context)
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
                               projects_handler, revisions_handler, revision_chat_handler, tz_handler, common_handler, portfolio_handler):
        """Регистрирует все callback маршруты в централизованном роутере"""
        
        # ПРИОРИТЕТ 1 (САМЫЙ ВЫСОКИЙ): Специфичные ID-based маршруты
        
        # Проекты - детали и чат (очень специфично)
        router.register(r"^project_details_\d+$", projects_handler.show_project_details, 
                       priority=10, description="Детали проекта по ID")
        router.register(r"^project_chat_\d+$", projects_handler.show_project_chat,
                       priority=10, description="Чат с исполнителем проекта")
        
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

        # ЧАТ ПРАВОК - НОВЫЕ ХЕНДЛЕРЫ!
        router.register(r"^revision_chat_\d+$", revision_chat_handler.show_revision_chat,
                       priority=10, description="Открыть чат правки")
        router.register(r"^revision_write_\d+$", revision_chat_handler.start_write_message,
                       priority=10, description="Начать писать сообщение в чат правки")
        router.register(r"^revision_close_chat_\d+$", revision_chat_handler.close_chat,
                       priority=10, description="Закрыть чат правки")
        router.register(r"^my_revisions$", revision_chat_handler.show_all_my_revisions,
                       priority=10, description="Показать все правки пользователя")
        router.register(r"^revision_approve_\d+$", revision_chat_handler.approve_revision,
                       priority=10, description="Принять правку")
        router.register(r"^revision_reject_\d+$", revision_chat_handler.reject_revision,
                       priority=10, description="Отправить правку на доработку")
        router.register(r"^revision_client_approve_\d+$", revision_chat_handler.client_approve_revision,
                       priority=10, description="Клиент принимает правку")
        router.register(r"^revision_client_reject_\d+$", revision_chat_handler.client_reject_revision,
                       priority=10, description="Клиент отправляет правку на доработку")
        router.register(r"^revision_cancel_reject_\d+$", revision_chat_handler.cancel_reject_revision,
                       priority=10, description="Отменить отправку на доработку")

        # ПРИОРИТЕТ 2: Проекты общие
        router.register(r"^list_projects$", projects_handler.show_user_projects,
                       priority=20, description="Показать проекты пользователя")
        
        # ПРИОРИТЕТ 3: Портфолио - ОТКЛЮЧЕНО (заменено на канал)
        # Категории портфолио (старый формат callback'ов)
        # router.register(r"^portfolio_(telegram|whatsapp|web|integration|featured|all)$", portfolio_handler.select_category,
        #                priority=25, description="Выбор категории портфолио (старый формат)")
        # # Категории портфолио (новый формат callback'ов)
        # router.register(r"^portfolio_(telegram_bots|web_development|mobile_apps|ai_integration|automation|ecommerce|other|featured)$", portfolio_handler.show_category_portfolio,
        #                priority=30, description="Категории портфолио")
        # router.register(r"^project_\d+$", portfolio_handler.show_project_details,
        #                priority=30, description="Детали проекта в портфолио") 
        # router.register(r"^gallery_\d+$", portfolio_handler.show_project_gallery,
        #                priority=30, description="Галерея изображений проекта")
        # router.register(r"^like_\d+$", portfolio_handler.like_project,
        #                priority=30, description="Лайкнуть проект")
        # router.register(r"^portfolio_page_\d+$", portfolio_handler.show_portfolio_page,
        #                priority=30, description="Навигация по страницам портфолио")
        # # Навигация между проектами
        # router.register(r"^portfolio_nav_\d+$", portfolio_handler.navigate_project,
        #                priority=30, description="Навигация между проектами")
        
        # ПРИОРИТЕТ 3.5: Quick Request (ВЫСОКИЙ ПРИОРИТЕТ!)
        from app.bot.handlers.quick_project_request import QuickProjectRequestHandler
        quick_handler = QuickProjectRequestHandler()
        router.register(r"^quick_request$", quick_handler.show_quick_request_menu,
                       priority=35, description="Быстрый запрос проекта")
        router.register(r"^quick_(telegram|miniapp|whatsapp|android|ios)$", quick_handler.handle_quick_request,
                       priority=35, description="Обработка быстрого запроса")
        router.register(r"^budget_(50000|100000|200000|500000|500000plus|unknown)$", quick_handler.handle_project_budget,
                       priority=35, description="Выбор бюджета проекта")
        router.register(r"^deadline_(asap|month|3months|6months|6plus|flexible)$", quick_handler.handle_project_deadline,
                       priority=35, description="Выбор срока проекта")

        # ПРИОРИТЕТ 4: ТЗ Creation (ConversationHandler маршруты)
        router.register(r"^create_tz$", tz_handler.show_tz_creation_menu,
                       priority=40, description="Создать техническое задание")
        router.register(r"^tz_(text|voice|step_by_step|upload|own)$", tz_handler.select_tz_method,
                       priority=40, description="Выбор метода создания ТЗ")
        
        # Пошаговое создание ТЗ - кнопки с ответами
        router.register(r"^step_", tz_handler.handle_step_answer,
                       priority=40, description="Ответы на пошаговые вопросы ТЗ")
        
        # Действия с готовым ТЗ
        router.register(r"^(review_|edit_own_tz|tz_save)", tz_handler.handle_review_action,
                       priority=40, description="Действия с готовым ТЗ")
        
        # ПРИОРИТЕТ 5: Консультации - ОТКЛЮЧЕНО
        # router.register(r"^consultation$", consultant_handler.start_consultation,
        #                priority=50, description="Начать консультацию")
        router.register(r"^(ask_question|example_questions)$", common_handler.handle_callback,
                       priority=50, description="AI консультант - вопросы")
        
        # ПРИОРИТЕТ 6: Настройки и служебное 
        router.register(r"^(setup_timeweb|setup_bot_token|send_bot_token|get_telegram_id|get_chat_id|send_chat_id|detailed_chat_instructions|setup_telegram_id)$", common_handler.handle_callback,
                       priority=60, description="Настройки подключения и конфигурации")
        router.register(r"^(bot_enter_token|bot_guide_steps)$", common_handler.handle_callback,
                       priority=60, description="Функции создания бота")
        router.register(r"^timeweb_info$", common_handler.handle_timeweb_info,
                       priority=60, description="Информация о Timeweb")
        router.register(r"^timeweb_registered$", common_handler.handle_timeweb_registered,
                       priority=60, description="Регистрация на Timeweb")
        router.register(r"^bot_creation_help$", common_handler.handle_bot_creation_help,
                       priority=60, description="Помощь в создании бота")
        router.register(r"^bot_creation_understood$", common_handler.handle_bot_creation_understood,
                       priority=60, description="Понял инструкции по созданию бота")
        
        # ПРИОРИТЕТ 6.5: Админские функции (высокий приоритет)
        router.register(r"^admin_console$", common_handler.handle_callback,
                       priority=65, description="Админ консоль")
        router.register(r"^admin_money$", common_handler.handle_callback,
                       priority=65, description="Управление финансами")
        router.register(r"^upload_receipt$", common_handler.handle_callback,
                       priority=65, description="Загрузка чека")
        router.register(r"^transaction_(income|expense)_\d+$", common_handler.handle_callback,
                       priority=65, description="Обработка типа транзакции")
        router.register(r"^transaction_type_(income|expense)$", common_handler.handle_callback,
                       priority=65, description="Выбор типа транзакции OCR")
        router.register(r"^category_\d+$", common_handler.handle_callback,
                       priority=65, description="Выбор категории транзакции")
        router.register(r"^back_to_transaction_type$", common_handler.handle_callback,
                       priority=65, description="Возврат к выбору типа транзакции")
        router.register(r"^(my_transactions|view_income|view_expenses|money_analytics|money_categories)$", 
                       common_handler.handle_callback, priority=65, description="Финансовые отчеты")
        
        # ПРИОРИТЕТ 7 (САМЫЙ НИЗКИЙ): Основное меню и общие команды
        router.register(r"^main_menu$", start_handler.start,
                       priority=70, description="Главное меню")
        router.register(r"^(calculator|faq|contacts|my_projects|consultant|settings|create_bot_guide)$", 
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
        print("=" * 80)
        print("🤖🤖🤖 МЕТОД RUN() ВЫЗВАН!")
        print("=" * 80)
        self.logger.info("🤖🤖🤖 Запуск бота в режиме polling...")
        try:
            print("🤖 Шаг 1: Инициализация приложения...")
            self.logger.info("🤖 Шаг 1: Инициализация приложения...")
            await self.application.initialize()
            print("✅ Приложение инициализировано")
            self.logger.info("✅ Приложение инициализировано")

            self.logger.info("🤖 Шаг 2: Запуск приложения...")
            await self.application.start()
            self.logger.info("✅ Приложение запущено")

            self.logger.info("🤖 Шаг 3: Запуск polling...")
            await self.application.updater.start_polling()
            self.logger.info("✅✅✅ БОТ УСПЕШНО ЗАПУЩЕН И ПОЛУЧАЕТ UPDATES!")
        except Exception as e:
            self.logger.error(f"❌❌❌ ОШИБКА ПРИ ЗАПУСКЕ БОТА: {e}", exc_info=True)
            raise

    async def stop(self):
        """Остановка бота."""
        self.logger.info("Остановка бота...")
        try:
            if self.application.updater and self.application.updater.running:
                await self.application.updater.stop()
            # Проверяем, что приложение запущено перед остановкой
            if self.application.running:
                await self.application.stop()
        except RuntimeError as e:
            # Игнорируем ошибку "This Application is not running!"
            if "not running" not in str(e).lower():
                raise
            self.logger.warning(f"Бот уже остановлен: {e}")

# --- Telegram Bot Initialization ---
bot_instance = TelegramBot()


# --- Webhook (если используется) ---
@app.post("/webhook")
async def webhook(request: Request):
    """Обработка входящих обновлений от Telegram в режиме вебхука."""
    data = await request.json()
    update = Update.de_json(data, bot_instance.application.bot)
    await bot_instance.application.process_update(update)
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    """Самый простой эндпоинт для проверки."""
    return {"message": "pong"}

# Корневой роут теперь обрабатывается admin_router (дашборд)

@app.get("/test")
async def test():
    """Тестовый эндпоинт для проверки работы."""
    try:
        import sys
        return {
            "status": "ok", 
            "message": "Сервер работает",
            "python_version": sys.version,
            "app_name": app.title
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/admin-test")
async def admin_test():
    """Тестовый эндпоинт для проверки админки."""
    try:
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        return {"status": "ok", "message": "Админка доступна", "routes": routes}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Ошибка в admin-test"}

@app.get("/admin-debug")
async def admin_debug():
    """Отладочный эндпоинт для проверки админки без аутентификации."""
    try:
        routes_info = []
        for route in app.routes:
            if hasattr(route, 'path'):
                route_info = {
                    "path": route.path,
                    "name": route.name if hasattr(route, 'name') else None
                }
                if hasattr(route, 'methods'):
                    route_info["methods"] = list(route.methods) if route.methods else []
                routes_info.append(route_info)
        
        # Сортируем роуты для удобства
        routes_info.sort(key=lambda x: x['path'])
        
        # Фильтруем только админские роуты для быстрого анализа
        admin_routes = [r for r in routes_info if r['path'].startswith('/admin')]
        
        return {
            "status": "ok", 
            "message": "Админка работает без аутентификации",
            "total_routes": len(routes_info),
            "admin_routes_count": len(admin_routes),
            "admin_routes": admin_routes[:20],  # Первые 20 для краткости
            "all_routes": routes_info[:50]  # Первые 50 для краткости
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "Ошибка в admin-debug"
        }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    logger.info(f"🚀 Запуск сервера на {settings.server_host}:{settings.server_port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,  # Отключаем reload для продакшена
        log_level="info"
    )