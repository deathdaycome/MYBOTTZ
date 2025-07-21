from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime

from ..keyboards.main import get_main_menu_keyboard, get_contacts_keyboard
from ...database.database import get_db_context, get_or_create_user, update_user_state
from ...database.models import Settings
from ...config.logging import get_logger, log_user_action

logger = get_logger(__name__)

class StartHandler:
    """Обработчик основных команд и стартового взаимодействия."""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # ПОЛНЫЙ СБРОС СОСТОЯНИЯ - принудительно завершаем ConversationHandler
            # Это критично для правильной работы кнопки "Создать ТЗ"
            context.user_data.clear()
            
            # Принудительно сигнализируем завершение ConversationHandler
            # Возвращаем ConversationHandler.END для любых активных диалогов
            conversation_ended = True
            
            log_user_action(user_id, "start_command", f"Username: {user.username}")
            
            with get_db_context() as db:
                db_user = get_or_create_user(
                    db=db,
                    telegram_id=user_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                update_user_state(db, user_id, "main_menu")
                
                # Получаем приветственное сообщение из настроек (с обработкой ошибок)
                welcome_text = f"👋 Добро пожаловать в BotDev Studio!"
                company_name = "BotDev Studio"
                
                try:
                    welcome_setting = db.query(Settings).filter(Settings.key == "welcome_message").first()
                    company_name_setting = db.query(Settings).filter(Settings.key == "company_name").first()
                    
                    if welcome_setting and welcome_setting.value:
                        welcome_text = welcome_setting.value
                    if company_name_setting and company_name_setting.value:
                        company_name = company_name_setting.value
                except Exception as e:
                    logger.warning(f"Не удалось получить настройки из БД: {e}")
            
            user_name = user.first_name or user.username or "пользователь"
            
            full_message = f"""
{welcome_text}

Привет, {user_name}! 

🤖 Я - бот-визитка разработчика ботов и автоматизации. Помогу вам:

✅ <b>Создать техническое задание</b> для вашего проекта
✅ <b>Рассчитать стоимость</b> разработки
✅ <b>Ответить на вопросы</b> через AI-консультанта
✅ <b>Показать портфолио</b> готовых решений
✅ <b>Организовать консультацию</b> с экспертом

🚀 <b>Что делаем:</b>
• Telegram и WhatsApp боты
• Веб-чатботы для сайтов
• CRM и автоматизация бизнеса
• Интеграции с внешними сервисами
• AI-решения и аналитика

Выберите нужный раздел в меню ниже! 👇
            """
            
            keyboard = get_main_menu_keyboard()
            
            if update.message:
                await update.message.reply_text(
                    full_message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    full_message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            logger.info(f"Пользователь {user_id} ({user.username}) запустил бота")
            
        except Exception as e:
            logger.error(f"Ошибка в start: {e}")
            if update.message:
                await update.message.reply_text(
                    "Произошла ошибка при запуске. Попробуйте еще раз или обратитесь в поддержку.",
                    reply_markup=get_main_menu_keyboard()
                )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "help_command")
            
            help_text = """
🆘 <b>Справка по боту</b>

<b>Основные команды:</b>
/start - Запуск бота и главное меню
/help - Эта справка
/menu - Показать главное меню
/cancel - Отменить текущее действие

<b>Нужна помощь?</b>
• Напишите в поддержку: @your_support
• Email: support@botdev.studio
            """
            
            keyboard = get_main_menu_keyboard()
            
            await update.message.reply_text(
                help_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в help: {e}")
            await update.message.reply_text(
                "Произошла ошибка при загрузке справки.",
                reply_markup=get_main_menu_keyboard()
            )

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /menu"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "menu_command")
            
            with get_db_context() as db:
                update_user_state(db, user_id, "main_menu")
            
            menu_text = "🏠 <b>Главное меню</b>\n\nВыберите нужный раздел:"
            
            keyboard = get_main_menu_keyboard()
            
            await update.message.reply_text(
                menu_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в menu: {e}")
            await update.message.reply_text(
                "Произошла ошибка при загрузке меню.",
                reply_markup=get_main_menu_keyboard()
            )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /cancel. Завершает любой ConversationHandler."""
        try:
            user = update.effective_user
            log_user_action(user.id, "cancel_command")
            
            with get_db_context() as db:
                update_user_state(db, user.id, "main_menu")
            
            context.user_data.clear()
            
            cancel_text = "Действие отменено. Возвращаю в главное меню."
            keyboard = get_main_menu_keyboard()
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    cancel_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    cancel_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Ошибка в cancel: {e}")
            return ConversationHandler.END

    async def show_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать контактную информацию"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            log_user_action(user_id, "show_contacts")
            
            contacts_text = """
📞 <b>Контактная информация</b>

<b>Свяжитесь с нами любым удобным способом:</b>

• <b>Telegram:</b> @your_telegram_contact
• <b>WhatsApp:</b> +7 (999) 123-45-67
• <b>Email:</b> info@botdev.studio
• <b>Сайт:</b> botdev.studio

Мы на связи с 9:00 до 18:00 (МСК) в будние дни.
            """
            
            keyboard = get_contacts_keyboard()
            
            await query.edit_message_text(
                text=contacts_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_contacts: {e}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на инлайн-кнопки."""
        query = update.callback_query
        await query.answer()

        # Простое сопоставление для основных кнопок
        if query.data == 'main_menu':
            await self.start(update, context)
        elif query.data == 'contacts':
            await self.show_contacts(update, context)
        # Другие обработчики будут вызваны по своим паттернам
        # (например, 'create_tz', 'portfolio' и т.д.)

# Единственный экземпляр класса для использования в других частях приложения
start_handler = StartHandler()