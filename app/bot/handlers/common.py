"""
Общие функции для всех обработчиков бота
"""
from telegram import Update, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import asyncio
import re
import traceback

from ..keyboards.main import get_main_menu_keyboard, get_back_to_main_keyboard
from ...database.database import get_db_context, get_or_create_user, update_user_state, get_user_by_telegram_id
from ...database.models import User, Settings, Project, ConsultantSession, ProjectRevision, RevisionMessage, RevisionMessageFile
from ...config.logging import get_logger, log_user_action
from ...utils.decorators import standard_handler, handle_errors, typing_action
from ...services.notification_service import NotificationService

logger = get_logger(__name__)

class CommonHandler:
    """Обработчик общих функций и неизвестных команд."""

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик неизвестных команд."""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text if update.message else ""
            
            log_user_action(user_id, "unknown_command", message_text)
            
            # Если это просто текст без команды, не показываем ошибку
            if not message_text.startswith('/'):
                # Просто игнорируем обычный текст, не отвечаем
                return
            
            text = """
❓ Неизвестная команда.

Используйте /help для просмотра доступных команд или выберите действие из меню ниже.
            """
            
            keyboard = get_main_menu_keyboard()
            
            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в unknown: {e}")

    @standard_handler
    async def show_calculator(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать калькулятор стоимости"""
        try:
            text = """
🧮 <b>Калькулятор стоимости разработки</b>

Оценка стоимости разработки зависит от:
• Сложности проекта
• Количества функций
• Интеграций с внешними сервисами
• Дизайна и пользовательского интерфейса
• Сроков разработки

<b>Базовые расценки:</b>
• Простой бот: от 15 000 ₽
• Средний бот: от 35 000 ₽
• Сложный бот: от 75 000 ₽
• Корпоративное решение: от 150 000 ₽

Для точной оценки создайте техническое задание 📋
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Создать ТЗ", callback_data="create_tz")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_calculator: {e}")

    @standard_handler
    async def show_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать часто задаваемые вопросы"""
        try:
            text = """
❓ <b>Часто задаваемые вопросы</b>

<b>🤖 Что такое Telegram-бот?</b>
Это программа, которая автоматизирует общение с пользователями в Telegram. Может принимать заказы, отвечать на вопросы, обрабатывать платежи и многое другое.

<b>⏱ Сколько времени занимает разработка?</b>
• Простой бот: 3-7 дней
• Средний бот: 1-2 недели  
• Сложный бот: 2-4 недели
• Корпоративное решение: 1-3 месяца

<b>💰 Как формируется цена?</b>
Стоимость зависит от функционала, сложности интеграций, дизайна и сроков разработки.

<b>🔧 Что входит в поддержку?</b>
Исправление ошибок, обновления, консультации по использованию, мелкие доработки.

<b>📱 На каких платформах работают боты?</b>
Telegram, WhatsApp, веб-сайты, социальные сети.
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_faq: {e}")

    @standard_handler
    async def show_consultation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о консультации"""
        try:
            text = """
💬 <b>Персональная консультация</b>

Получите профессиональную консультацию по:
• Выбору технологий для проекта
• Архитектуре и структуре решения
• Интеграциям и API
• Оптимизации бизнес-процессов
• Монетизации через ботов

<b>🎯 Форматы консультаций:</b>
• Голосовой звонок (30-60 мин)
• Видеоконференция с демо
• Чат-консультация в Telegram
• Встреча в офисе (Москва)

<b>💰 Стоимость:</b>
• Экспресс-консультация (15 мин): бесплатно
• Стандартная консультация (60 мин): 3 000 ₽
• Техническая консультация (90 мин): 5 000 ₽

Для записи на консультацию напишите в чат или используйте AI-консультанта.
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
                [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_consultation: {e}")

    @standard_handler
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех callback"""
        try:
            callback_data = update.callback_query.data
            user_id = update.effective_user.id
            
            # Подробное логирование
            logger.info(f"🔍 CALLBACK RECEIVED: user_id={user_id}, callback_data='{callback_data}'")
            logger.info(f"🔍 Update type: {type(update)}")
            logger.info(f"🔍 CallbackQuery: {update.callback_query}")
            logger.info(f"🔍 Message: {update.callback_query.message}")
            log_user_action(user_id, "callback", callback_data)
            
            # Подтверждаем получение callback
            logger.info(f"🔍 Отправляем answer() для callback_data='{callback_data}'")
            await update.callback_query.answer()
            logger.info(f"🔍 Answer() отправлен успешно для callback_data='{callback_data}'")
            
            # Обработка различных callback'ов
            if callback_data == "main_menu":
                logger.info(f"📱 Обрабатываем main_menu для пользователя {user_id}")
                from ..handlers.start import StartHandler
                start_handler = StartHandler()
                await start_handler.start(update, context)
                
            elif callback_data == "calculator":
                logger.info(f"🧮 Обрабатываем calculator для пользователя {user_id}")
                await self.show_calculator(update, context)
                
            elif callback_data == "faq":
                logger.info(f"❓ Обрабатываем faq для пользователя {user_id}")
                await self.show_faq(update, context)
                
            elif callback_data == "consultation":
                logger.info(f"💬 Обрабатываем consultation для пользователя {user_id}")
                await self.show_consultation(update, context)
                
            elif callback_data == "contacts":
                logger.info(f"📞 Обрабатываем contacts для пользователя {user_id}")
                await self.show_contacts(update, context)
                
            elif callback_data == "my_projects":
                logger.info(f"📊 Обрабатываем my_projects для пользователя {user_id}")
                await self.show_my_projects(update, context)
                
            elif callback_data == "portfolio":
                logger.info(f"💼 Обрабатываем portfolio для пользователя {user_id}")
                await self.show_portfolio_menu(update, context)
                
            elif callback_data == "portfolio":
                logger.info(f"💼 Обрабатываем portfolio для пользователя {user_id}")
                await self.show_portfolio_categories(update, context)
                
            elif callback_data == "consultant":
                logger.info(f"🤖 Обрабатываем consultant для пользователя {user_id}")
                await self.show_consultant_menu(update, context)
                
            elif callback_data == "create_tz":
                logger.info(f"🚀 Обрабатываем create_tz для пользователя {user_id}")
                from ..handlers.tz_creation import TZCreationHandler
                tz_handler = TZCreationHandler()
                await tz_handler.show_tz_creation_menu(update, context)
                
            elif callback_data == "create_bot_guide":
                logger.info(f"🎯 Обрабатываем create_bot_guide для пользователя {user_id}")
                from ..handlers.bot_creation import BotCreationHandler
                bot_handler = BotCreationHandler()
                await bot_handler.show_bot_creation_guide(update, context)
                
            elif callback_data.startswith("portfolio_"):
                logger.info(f"💼 Обрабатываем {callback_data} для пользователя {user_id}")
                await self.show_portfolio_category(update, context, callback_data)
                
            elif callback_data == "ask_question":
                logger.info(f"💬 Обрабатываем ask_question для пользователя {user_id}")
                await self.show_ask_question(update, context)
                
            elif callback_data == "example_questions":
                logger.info(f"📋 Обрабатываем example_questions для пользователя {user_id}")
                await self.show_example_questions(update, context)
                
            elif callback_data == "settings":
                logger.info(f"⚙️ Обрабатываем settings для пользователя {user_id}")
                await self.show_settings(update, context)
                
            elif callback_data == "setup_timeweb":
                logger.info(f"🌐 Обрабатываем setup_timeweb для пользователя {user_id}")
                await self.setup_timeweb(update, context)
                
            elif callback_data == "setup_bot_token":
                logger.info(f"🤖 Обрабатываем setup_bot_token для пользователя {user_id}")
                await self.setup_bot_token(update, context)
                
            elif callback_data.startswith("project_chat_"):
                logger.info(f"💬 Обрабатываем project_chat для пользователя {user_id}")
                await self.show_project_chat(update, context)
                
            elif callback_data.startswith("project_download_"):
                logger.info(f"📄 Обрабатываем project_download для пользователя {user_id}")
                await self.download_project_tz(update, context)
                
            else:
                logger.warning(f"❌ Неизвестный callback: '{callback_data}' от пользователя {user_id}")
                # Для неизвестных callback показываем главное меню
                text = f"""
❓ Неизвестная команда: {callback_data}

Выберите действие из меню ниже:
                """
                
                keyboard = get_main_menu_keyboard()
                
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            logger.info(f"✅ Callback '{callback_data}' обработан успешно для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_callback: {e}")
            logger.error(f"   Callback data: {callback_data if 'callback_data' in locals() else 'unknown'}")
            logger.error(f"   User ID: {user_id if 'user_id' in locals() else 'unknown'}")
            
            # В случае ошибки показываем главное меню
            try:
                keyboard = get_main_menu_keyboard()
                await update.callback_query.edit_message_text(
                    "❌ Произошла ошибка. Попробуйте снова.",
                    reply_markup=keyboard
                )
            except Exception as e2:
                logger.error(f"❌ Критическая ошибка при показе главного меню: {e2}")

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений с учетом контекста"""
        try:
            # Логируем все входящие сообщения для диагностики
            logger.info(f"🔍 MESSAGE RECEIVED: type={type(update.message)}, has_text={bool(update.message and update.message.text)}, has_photo={bool(update.message and update.message.photo)}, has_document={bool(update.message and update.message.document)}")
            
            # БЫСТРОЕ ИСПРАВЛЕНИЕ: Если это фотография на этапе files - направляем в photo handler
            if update.message and update.message.photo and context.user_data.get('creating_revision_step') == 'files':
                logger.info(f"🔍 PHOTO DETECTED IN TEXT HANDLER - routing to photo handler")
                await self.handle_photo(update, context)
                return
            
            user_id = update.effective_user.id
            message_text = update.message.text if update.message else ""
            
            # Если это команда - очищаем все флаги ожидания
            logger.info(f"🔍 ПРОВЕРКА КОМАНДЫ: message_text='{message_text}', startswith('/')={message_text.startswith('/')}")
            if message_text.startswith('/'):
                logger.info(f"🛑 ЭТО КОМАНДА - ОЧИЩАЕМ ФЛАГИ И ВЫХОДИМ")
                context.user_data.pop('waiting_bot_token_settings', None)
                context.user_data.pop('waiting_timeweb_settings', None)
                context.user_data.pop('waiting_bot_token', None)
                context.user_data.pop('waiting_timeweb_credentials', None)
                # Для команд не делаем ничего - пусть обрабатывается CommandHandler
                return
            
            logger.info(f"💬 ТЕКСТОВОЕ СООБЩЕНИЕ от {user_id}: '{message_text}'")
            logger.info(f"🔍 Состояние context.user_data: {context.user_data}")
            
            log_user_action(user_id, "text_message", message_text[:50])
            
            # Проверяем, ожидаем ли мы данные Timeweb (старый флоу)
            if context.user_data.get('waiting_timeweb_credentials'):
                await self.handle_timeweb_credentials(update, context)
                return
            
            # Проверяем, ожидаем ли мы API токен бота (старый флоу)
            if context.user_data.get('waiting_bot_token'):
                await self.handle_bot_token(update, context)
                return
            
            # Проверяем, ожидаем ли мы данные Timeweb (новый флоу из настроек)
            if context.user_data.get('waiting_timeweb_settings'):
                await self.save_timeweb_settings(update, context)
                return
            
            # Проверяем, ожидаем ли мы API токен бота (новый флоу из настроек)
            logger.info(f"🔍 Проверяем флаг waiting_bot_token_settings: {context.user_data.get('waiting_bot_token_settings')}")
            if context.user_data.get('waiting_bot_token_settings'):
                logger.info(f"🔑 Обрабатываем токен бота для пользователя {user_id}")
                await self.save_bot_token_settings(update, context)
                return
            
            # Проверяем, создает ли пользователь правку
            if context.user_data.get('creating_revision_step') == 'title':
                from .revisions import revisions_handler
                await revisions_handler.handle_revision_title(update, context)
                return
            
            if context.user_data.get('creating_revision_step') == 'description':
                from .revisions import revisions_handler
                await revisions_handler.handle_revision_description(update, context)
                return
            
            # Если сообщение не является командой, показываем главное меню
            if not message_text.startswith('/'):
                keyboard = get_main_menu_keyboard()
                await update.message.reply_text(
                    "Выберите действие из меню:",
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка обработки текстового сообщения: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений (алиас для handle_text_input)"""
        await self.handle_text_input(update, context)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка голосовых сообщений"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "voice_message", "voice")
            
            await update.message.reply_text(
                "🎤 Голосовые сообщения получены! В будущем здесь будет распознавание речи."
            )
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка документов"""
        try:
            user_id = update.effective_user.id
            document = update.message.document
            file_name = document.file_name if document else "unknown"
            
            logger.info(f"📄 DOCUMENT HANDLER CALLED: user_id={user_id}, file_name={file_name}")
            logger.info(f"📄 User data: {context.user_data}")
            logger.info(f"📄 Creating revision step: {context.user_data.get('creating_revision_step')}")
            
            log_user_action(user_id, "document_message", file_name)
            
            # Проверяем, создает ли пользователь правку
            if context.user_data.get('creating_revision_step') == 'files':
                logger.info(f"📄 ROUTING TO REVISION DOCUMENT HANDLER")
                await self.handle_revision_document(update, context)
                return
            
            await update.message.reply_text(
                f"📄 Документ '{file_name}' получен! В будущем здесь будет обработка файлов."
            )
        except Exception as e:
            logger.error(f"❌ Ошибка обработки документа: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка фотографий"""
        try:
            user_id = update.effective_user.id
            
            # Подробное логирование для диагностики
            logger.info(f"📸 PHOTO HANDLER CALLED: user_id={user_id}")
            logger.info(f"📸 Update: {update}")
            logger.info(f"📸 Message: {update.message}")
            logger.info(f"� Photo: {update.message.photo if update.message else None}")
            logger.info(f"📸 User data: {context.user_data}")
            logger.info(f"� Creating revision step: {context.user_data.get('creating_revision_step')}")
            
            log_user_action(user_id, "photo_message")
            
            # Проверяем, создает ли пользователь правку
            if context.user_data.get('creating_revision_step') == 'files':
                logger.info(f"� ROUTING TO REVISION FILES HANDLER")
                await self.handle_revision_photo(update, context)
                return
            
            logger.info(f"� NOT IN REVISION MODE - sending default message")
            await update.message.reply_text(
                "📷 Фотография получена! В будущем здесь будет обработка изображений."
            )
        except Exception as e:
            logger.error(f"❌ Ошибка обработки фотографии: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            # Отправляем сообщение об ошибке пользователю
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке фотографии. Попробуйте еще раз."
                )
            except:
                pass

    async def handle_any_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Универсальный обработчик для диагностики всех сообщений"""
        try:
            user_id = update.effective_user.id
            message = update.message
            
            logger.info(f"🔍 UNIVERSAL HANDLER: user_id={user_id}")
            logger.info(f"🔍 Message type: {type(message)}")
            logger.info(f"🔍 Has text: {bool(message and message.text)}")
            logger.info(f"🔍 Has photo: {bool(message and message.photo)}")
            logger.info(f"🔍 Has document: {bool(message and message.document)}")
            logger.info(f"🔍 Has video: {bool(message and message.video)}")
            logger.info(f"🔍 User data: {context.user_data}")
            
            # Если это фотография и пользователь на этапе files
            if message and message.photo and context.user_data.get('creating_revision_step') == 'files':
                logger.info(f"🔍 PHOTO DETECTED IN FILES STEP - routing to photo handler")
                await self.handle_photo(update, context)
                return
            
            # Для всех остальных случаев - стандартное сообщение
            logger.info(f"🔍 Universal handler: sending default message")
            await update.message.reply_text(
                "🤖 Сообщение получено! Используйте кнопки меню для навигации."
            )
            
        except Exception as e:
            logger.error(f"Ошибка в universal handler: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка видео"""
        try:
            user_id = update.effective_user.id
            
            logger.info(f"🎥 VIDEO HANDLER CALLED: user_id={user_id}")
            logger.info(f"🎥 User data: {context.user_data}")
            logger.info(f"🎥 Creating revision step: {context.user_data.get('creating_revision_step')}")
            
            log_user_action(user_id, "video_message")
            
            # Проверяем, создает ли пользователь правку
            if context.user_data.get('creating_revision_step') == 'files':
                logger.info(f"🎥 ROUTING TO REVISION VIDEO HANDLER")
                await self.handle_revision_video(update, context)
                return
            
            await update.message.reply_text(
                "🎥 Видео получено! В будущем здесь будет обработка видео."
            )
        except Exception as e:
            logger.error(f"❌ Ошибка обработки видео: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

    @standard_handler
    async def handle_timeweb_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о Timeweb"""
        try:
            text = """
🌐 <b>Что такое Timeweb и зачем он нужен?</b>

<b>Timeweb Cloud</b> - это надежный российский хостинг-провайдер, который обеспечит стабильную работу вашего бота 24/7.

<b>🎯 Зачем нужен хостинг для бота:</b>
• Бот должен работать круглосуточно
• Нужен сервер для размещения кода
• Требуется база данных для хранения информации
• Необходимо обеспечить безопасность

<b>💰 Преимущества Timeweb:</b>
• Доступные цены (от 150₽/мес)
• Простая панель управления  
• Техподдержка на русском языке
• Высокая надежность и скорость
• Подходит для любых ботов

<b>🎁 При регистрации по нашей ссылке:</b>
• Бонусы на счет
• Скидки на услуги
• Персональная поддержка

<i>Мы поможем настроить хостинг и разместить ваш бот!</i>
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Зарегистрироваться на Timeweb", url="https://timeweb.cloud/r/xv15146")],
                [
                    InlineKeyboardButton("✅ Уже зарегистрирован", callback_data="timeweb_registered"),
                    InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
                ]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_timeweb_info: {e}")

    @standard_handler 
    async def handle_timeweb_registered(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка уведомления о регистрации на Timeweb"""
        try:
            user_id = update.effective_user.id
            callback_data = update.callback_query.data
            
            # Извлекаем ID проекта из callback_data если есть
            project_id = None
            if "timeweb_registered_" in callback_data:
                project_id = int(callback_data.split("_")[-1])
            
            text = """
✅ <b>Отлично! Теперь нужны данные от аккаунта</b>

Для настройки хостинга мне понадобятся данные от вашего аккаунта Timeweb:

📧 <b>Логин</b> - ваш email, телефон или логин
🔑 <b>Пароль</b> - пароль от аккаунта

<i>⚠️ Данные нужны для первоначальной настройки сервера и размещения бота. Мы рекомендуем после настройки сменить пароль.</i>

<b>Отправьте данные в любом из форматов:</b>

<b>Вариант 1:</b>
<code>Логин: ваш_логин
Пароль: ваш_пароль</code>

<b>Вариант 2 (просто две строки):</b>
<code>ваш_логин
ваш_пароль</code>

<i>💡 Логин может быть email, номером телефона или обычным логином</i>
            """
            
            # Сохраняем ID проекта в context для последующего использования
            if project_id:
                context.user_data['waiting_timeweb_credentials'] = project_id
                logger.info(f"🔍 Set waiting_timeweb_credentials to project_id: {project_id}")
            else:
                context.user_data['waiting_timeweb_credentials'] = True
                logger.info(f"🔍 Set waiting_timeweb_credentials to True")
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отменить", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_timeweb_registered: {e}")

    @standard_handler
    async def handle_timeweb_credentials(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка получения данных от Timeweb"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            
            logger.info(f"🔍 TIMEWEB CREDENTIALS: user_id={user_id}, waiting_flag={context.user_data.get('waiting_timeweb_credentials')}")
            logger.info(f"🔍 Message text: {message_text}")
            
            # Проверяем, ожидаем ли мы данные Timeweb
            if not context.user_data.get('waiting_timeweb_credentials'):
                logger.info("🔍 Not waiting for Timeweb credentials, returning")
                return
            
            # Парсим данные - поддерживаем разные форматы
            login_match = re.search(r'логин:\s*(.+)', message_text, re.IGNORECASE)
            password_match = re.search(r'пароль:\s*(.+)', message_text, re.IGNORECASE)
            
            # Если не найден формат "Логин: ... Пароль: ...", пробуем построчно
            if not login_match or not password_match:
                lines = [line.strip() for line in message_text.strip().split('\n') if line.strip()]
                
                if len(lines) >= 2:
                    # Берем первую строку как логин, вторую как пароль
                    login = lines[0]
                    password = lines[1]
                else:
                    await update.message.reply_text(
                        "❌ Неверный формат данных.\n\n"
                        "Отправьте данные в любом из форматов:\n\n"
                        "<b>Вариант 1:</b>\n"
                        "<code>Логин: ваш_логин\n"
                        "Пароль: ваш_пароль</code>\n\n"
                        "<b>Вариант 2:</b>\n"
                        "<code>ваш_логин\n"
                        "ваш_пароль</code>\n\n"
                        "<i>Логин может быть email, номером или обычным логином</i>",
                        parse_mode='HTML'
                    )
                    return
            else:
                login = login_match.group(1).strip()
                password = password_match.group(1).strip()
            
            # Сохраняем данные в проект
            project_id = context.user_data.get('waiting_timeweb_credentials')
            
            logger.info(f"🔍 SAVING TIMEWEB: project_id={project_id}, type={type(project_id)}")
            
            try:
                with get_db_context() as db:
                    if isinstance(project_id, int):
                        # Обновляем конкретный проект
                        logger.info(f"🔍 Looking for project with ID: {project_id}")
                        project = db.query(Project).filter(Project.id == project_id).first()
                        if project:
                            logger.info(f"🔍 Found project: {project.title}")
                            if not project.project_metadata:
                                project.project_metadata = {}
                            project.project_metadata['timeweb_credentials'] = {
                                'login': login,
                                'password': password,
                                'created_at': datetime.utcnow().isoformat()
                            }
                            db.commit()
                            logger.info(f"✅ Данные Timeweb сохранены для проекта {project_id}")
                        else:
                            logger.error(f"❌ Проект с ID {project_id} не найден")
                    else:
                        # Ищем последний проект пользователя
                        logger.info(f"🔍 Looking for user with telegram_id: {user_id}")
                        user = get_user_by_telegram_id(db, user_id)
                        if user:
                            logger.info(f"🔍 Found user: {user.id}")
                            project = db.query(Project).filter(Project.user_id == user.id).order_by(Project.created_at.desc()).first()
                            if project:
                                logger.info(f"🔍 Found latest project: {project.id} - {project.title}")
                                if not project.project_metadata:
                                    project.project_metadata = {}
                                project.project_metadata['timeweb_credentials'] = {
                                    'login': login,
                                    'password': password,
                                    'created_at': datetime.utcnow().isoformat()
                                }
                                db.commit()
                                logger.info(f"✅ Данные Timeweb сохранены для проекта {project.id}")
                            else:
                                logger.error(f"❌ Не найден проект для пользователя {user.id}")
                        else:
                            logger.error(f"❌ Пользователь с telegram_id {user_id} не найден")
                
            except Exception as db_error:
                logger.error(f"❌ Ошибка при сохранении данных Timeweb: {db_error}")
                await update.message.reply_text(
                    "❌ Ошибка при сохранении данных. Попробуйте еще раз.",
                    reply_markup=get_main_menu_keyboard()
                )
                return
            
            # Очищаем флаг ожидания
            context.user_data.pop('waiting_timeweb_credentials', None)
            
            text = """
✅ <b>Данные Timeweb сохранены!</b>

Теперь нужно создать Telegram бота для вашего проекта:

<b>🤖 Шаг 1: Создание бота</b>
1. Откройте @BotFather в Telegram
2. Отправьте команду /newbot
3. Придумайте имя бота (например: "Мой Магазин Бот")
4. Придумайте username (например: @my_shop_bot)
5. Скопируйте API токен

<b>💡 Пример API токена:</b>
<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>

<b>⚠️ Важно:</b>
• Токен должен содержать двоеточие (:)
• Никому не передавайте токен
• Он нужен для подключения бота к серверу

<b>Отправьте мне API токен вашего бота:</b>
            """
            
            # Сохраняем состояние ожидания токена
            context.user_data['waiting_bot_token'] = project_id if isinstance(project_id, int) else True
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Помощь с созданием", callback_data="bot_creation_help")],
                [InlineKeyboardButton("❌ Отменить", callback_data="main_menu")]
            ])
            
            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_timeweb_credentials: {e}")
    
    @standard_handler
    async def handle_bot_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка получения API токена бота"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text.strip()
            
            # Проверяем, ожидаем ли мы токен
            if not context.user_data.get('waiting_bot_token'):
                return
            
            # Проверяем формат токена
            if not self._validate_bot_token(message_text):
                await update.message.reply_text(
                    "❌ <b>Неверный формат токена</b>\n\n"
                    "<b>Правильный формат:</b>\n"
                    "<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>\n\n"
                    "<b>Токен должен содержать:</b>\n"
                    "• Числа до двоеточия\n"
                    "• Двоеточие (:)\n"
                    "• Буквы и цифры после двоеточия\n\n"
                    "<b>Отправьте корректный токен:</b>",
                    parse_mode='HTML'
                )
                return
            
            # Сохраняем токен в проект
            project_id = context.user_data.get('waiting_bot_token')
            
            try:
                with get_db_context() as db:
                    if isinstance(project_id, int):
                        # Обновляем конкретный проект
                        project = db.query(Project).filter(Project.id == project_id).first()
                        if project:
                            if not project.project_metadata:
                                project.project_metadata = {}
                            project.project_metadata['bot_token'] = message_text
                            db.commit()
                            logger.info(f"API токен бота сохранен для проекта {project_id}")
                    else:
                        # Ищем последний проект пользователя
                        user = get_user_by_telegram_id(db, user_id)
                        if user:
                            project = db.query(Project).filter(Project.user_id == user.id).order_by(Project.created_at.desc()).first()
                            if project:
                                if not project.project_metadata:
                                    project.project_metadata = {}
                                project.project_metadata['bot_token'] = message_text
                                db.commit()
                                logger.info(f"API токен бота сохранен для проекта {project.id}")
                
            except Exception as db_error:
                logger.error(f"Ошибка при сохранении токена: {db_error}")
                await update.message.reply_text(
                    "❌ Ошибка при сохранении токена. Попробуйте еще раз.",
                    reply_markup=get_main_menu_keyboard()
                )
                return
            
            # Очищаем флаг ожидания
            context.user_data.pop('waiting_bot_token', None)
            
            text = """
🎉 <b>Отлично! Все данные получены!</b>

Теперь у нас есть все необходимое для разработки:
✅ Техническое задание
✅ Аккаунт хостинга Timeweb
✅ API токен бота

<b>Что дальше:</b>
• Мы начнем разработку бота
• Настроим сервер на Timeweb
• Развернем и протестируем бота
• Передадим вам готовое решение

<i>Мы свяжемся с вами в ближайшее время для уточнения деталей и начала работы!</i>

<b>💬 Отслеживайте статус проекта в разделе "Мои проекты"</b>
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects"),
                    InlineKeyboardButton("🚀 Создать еще ТЗ", callback_data="create_tz")
                ],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_bot_token: {e}")
    
    def _validate_bot_token(self, token: str) -> bool:
        """Валидация формата токена бота"""
        import re
        # Токен должен быть в формате: числа:буквы-цифры
        pattern = r'^\d+:[A-Za-z0-9_-]+$'
        return bool(re.match(pattern, token)) and len(token) > 20
    
    @standard_handler
    async def handle_bot_creation_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Помощь с созданием бота"""
        try:
            text = """
🤖 <b>Подробная инструкция создания бота</b>

<b>Шаг 1: Открыть @BotFather</b>
• Найдите @BotFather в поиске Telegram
• Нажмите START или напишите /start

<b>Шаг 2: Создать нового бота</b>
• Отправьте команду <code>/newbot</code>
• BotFather попросит ввести имя бота

<b>Шаг 3: Придумать имя</b>
• Напишите имя как хотите (например: "Мой магазин")
• Это имя будет видно в контактах

<b>Шаг 4: Придумать username</b>
• Username должен заканчиваться на "bot"
• Например: <code>my_shop_bot</code>
• Если занято, попробуйте другое

<b>Шаг 5: Скопировать токен</b>
• BotFather пришлет сообщение с токеном
• Скопируйте весь токен полностью
• Отправьте его мне

<b>💡 Пример токена:</b>
<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>

<b>⚠️ Важно:</b>
• Токен содержит цифры, двоеточие и буквы
• Длина примерно 45-50 символов
• Не показывайте токен посторонним
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Открыть @BotFather", url="https://t.me/botfather")],
                [InlineKeyboardButton("✅ Понятно, создаю бота", callback_data="bot_creation_understood")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_bot_creation_help: {e}")
    
    @standard_handler
    async def handle_bot_creation_understood(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка понимания инструкции создания бота"""
        try:
            text = """
🤖 <b>Отлично! Теперь создайте бота и отправьте токен</b>

<b>Что нужно сделать:</b>
1. Откройте @BotFather
2. Создайте бота по инструкции выше
3. Скопируйте полученный токен
4. Отправьте его мне следующим сообщением

<b>💡 Пример правильного токена:</b>
<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>

<b>Жду ваш токен...</b>
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Показать инструкцию снова", callback_data="bot_creation_help")],
                [InlineKeyboardButton("❌ Отменить", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_bot_creation_understood: {e}")

    @standard_handler
    async def show_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать контактную информацию"""
        try:
            text = """
📞 <b>Контакты</b>

<b>👨‍💻 Разработчик:</b> Ivan Petrov
<b>📧 Email:</b> ivan@botdev.ru
<b>📱 Telegram:</b> @botdev_ivan
<b>🌐 Сайт:</b> botdev.ru

<b>💬 Способы связи:</b>
• Telegram: @botdev_ivan
• Email: ivan@botdev.ru
• Телефон: +7 (999) 123-45-67

<b>🕒 Время работы:</b>
Пн-Пт: 10:00 - 19:00 (МСК)
Сб: 11:00 - 16:00 (МСК)
Вс: выходной

<b>💼 Офис:</b>
Москва, ул. Примерная, 1
(работаем удаленно)

Для быстрого ответа пишите в Telegram!
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Консультация", callback_data="consultation")],
                [InlineKeyboardButton("🚀 Создать ТЗ", callback_data="create_tz")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_contacts: {e}")

    @standard_handler
    async def show_my_projects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать проекты пользователя"""
        try:
            # Используем ProjectsHandler для показа проектов
            from .projects import ProjectsHandler
            projects_handler = ProjectsHandler()
            await projects_handler.show_user_projects(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка в show_my_projects: {e}")

    @standard_handler
    async def show_consultant_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню AI консультанта"""
        try:
            text = """
🤖 <b>AI Консультант</b>

Получите мгновенные ответы на ваши вопросы о разработке ботов!

<b>💡 Что может AI консультант:</b>
• Помочь выбрать технологии для проекта
• Объяснить возможности автоматизации
• Рассказать о интеграциях
• Дать советы по архитектуре
• Ответить на технические вопросы

<b>🎯 Как работает:</b>
1. Задайте вопрос обычным сообщением
2. Получите развернутый ответ
3. Задавайте уточняющие вопросы

<b>📝 Примеры вопросов:</b>
• "Как подключить оплату к боту?"
• "Какие API можно интегрировать?"
• "Сколько стоит разработка CRM?"
• "Как сделать бота для интернет-магазина?"

Просто напишите свой вопрос следующим сообщением!
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Задать вопрос", callback_data="ask_question")],
                [InlineKeyboardButton("📋 Примеры вопросов", callback_data="example_questions")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_consultant_menu: {e}")

    @standard_handler
    async def show_portfolio_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню портфолио"""
        try:
            text = """
💼 <b>Портфолио</b>

Посмотрите на готовые решения и примеры наших работ!

<b>🚀 Категории проектов:</b>

🤖 <b>Telegram боты</b>
• Боты для бизнеса и автоматизации
• E-commerce и интернет-магазины
• CRM и управление клиентами
• Образовательные и информационные

📱 <b>WhatsApp боты</b>
• Боты для поддержки клиентов
• Автоматизация продаж
• Уведомления и рассылки

🌐 <b>Веб-чатботы</b>
• Чатботы для сайтов
• Интеграция с веб-сервисами
• AI-ассистенты

🔗 <b>Интеграции</b>
• CRM системы
• Платежные системы
• API и внешние сервисы

Выберите категорию для просмотра примеров работ:
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🤖 Telegram боты", callback_data="portfolio_telegram"),
                    InlineKeyboardButton("📱 WhatsApp боты", callback_data="portfolio_whatsapp")
                ],
                [
                    InlineKeyboardButton("🌐 Веб-чатботы", callback_data="portfolio_web"),
                    InlineKeyboardButton("🔗 Интеграции", callback_data="portfolio_integration")
                ],
                [
                    InlineKeyboardButton("⭐ Рекомендуемые", callback_data="portfolio_featured"),
                    InlineKeyboardButton("📊 Все проекты", callback_data="portfolio_all")
                ],
                [
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_menu: {e}")

    @standard_handler
    async def show_portfolio_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Показать категорию портфолио"""
        try:
            category = callback_data.replace("portfolio_", "")
            
            category_names = {
                "telegram": "🤖 Telegram боты",
                "whatsapp": "📱 WhatsApp боты", 
                "web": "🌐 Веб-чатботы",
                "integrations": "🔗 Интеграции",
                "all": "📊 Все проекты"
            }
            
            category_descriptions = {
                "telegram": """
🤖 <b>Telegram боты</b>

<b>📋 Примеры наших работ:</b>

<b>1. Бот для ресторана</b>
• Прием заказов через меню
• Интеграция с системой доставки
• Оплата онлайн
• Уведомления о статусе заказа

<b>2. CRM-бот для агентства</b>
• Управление клиентами
• Автоматизация воронки продаж
• Интеграция с AmoCRM
• Аналитика и отчеты

<b>3. Бот для интернет-магазина</b>
• Каталог товаров
• Корзина и оформление заказа
• Интеграция с 1С
• Система лояльности

<b>💰 Стоимость:</b> от 25 000 ₽
                """,
                "whatsapp": """
📱 <b>WhatsApp боты</b>

<b>📋 Примеры наших работ:</b>

<b>1. Бот поддержки клиентов</b>
• Автоответчик 24/7
• Обработка частых вопросов
• Передача в службу поддержки
• База знаний и FAQ

<b>2. Бот для записи на услуги</b>
• Календарь свободного времени
• Выбор услуги и мастера
• Подтверждение записи
• Напоминания о встрече

<b>3. Бот для уведомлений</b>
• Рассылка новостей
• Персональные уведомления
• Статистика доставки
• Сегментация аудитории

<b>💰 Стоимость:</b> от 35 000 ₽
                """,
                "web": """
🌐 <b>Веб-чатботы</b>

<b>📋 Примеры наших работ:</b>

<b>1. Консультант для сайта</b>
• AI-помощник для клиентов
• Ответы на вопросы о товарах
• Сбор контактов
• Интеграция с CRM

<b>2. Бот для онлайн-школы</b>
• Помощь в выборе курса
• Демо-уроки и материалы
• Регистрация на курсы
• Поддержка учеников

<b>3. Бот для банка</b>
• Информация о услугах
• Калькулятор кредитов
• Заявки на карты
• Поиск отделений

<b>💰 Стоимость:</b> от 40 000 ₽
                """,
                "integrations": """
🔗 <b>Интеграции</b>

<b>📋 Примеры наших работ:</b>

<b>1. Интеграция с CRM</b>
• AmoCRM, Bitrix24, Salesforce
• Автоматическое создание сделок
• Синхронизация контактов
• Отчеты и аналитика

<b>2. Платежные системы</b>
• Яндекс.Касса, Сбербанк
• Stripe, PayPal
• Автоматические чеки
• Возвраты и отмены

<b>3. Внешние API</b>
• Социальные сети
• Почтовые сервисы
• Системы аналитики
• Сторонние сервисы

<b>💰 Стоимость:</b> от 15 000 ₽
                """,
                "all": """
📊 <b>Все проекты</b>

<b>🎯 Наша статистика:</b>
• 150+ успешных проектов
• 95% довольных клиентов
• 200+ интеграций
• 50+ отраслей бизнеса

<b>🏆 Ключевые достижения:</b>
• Автоматизация продаж на 40%
• Сокращение времени ответа на 80%
• Увеличение конверсии на 25%
• Экономия расходов на 30%

<b>🚀 Технологии:</b>
• Python, Node.js, PHP
• Telegram Bot API, WhatsApp API
• AI и машинное обучение
• Облачные решения

<b>💼 Отрасли:</b>
Ритейл, HoReCa, Образование, Финансы, Медицина, Недвижимость, Авто, IT-услуги

<b>📞 Готовы обсудить ваш проект?</b>
                """
            }
            
            text = category_descriptions.get(category, "Категория не найдена")
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Создать ТЗ", callback_data="create_tz")],
                [InlineKeyboardButton("💬 Консультация", callback_data="consultation")],
                [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_category: {e}")

    @standard_handler
    async def show_ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать форму для вопроса"""
        try:
            text = """
💬 <b>Задать вопрос AI консультанту</b>

Просто напишите свой вопрос следующим сообщением, и AI консультант даст вам развернутый ответ!

<b>📝 Советы для лучшего ответа:</b>
• Опишите вашу задачу подробно
• Укажите отрасль бизнеса
• Добавьте технические требования
• Уточните бюджет (при необходимости)

<b>⚡ Например:</b>
"Нужен бот для доставки еды. Хочу принимать заказы, показывать меню, интегрировать с оплатой. Бюджет до 50 000 рублей."

Ожидаю ваш вопрос! 👇
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Примеры вопросов", callback_data="example_questions")],
                [InlineKeyboardButton("🔙 К консультанту", callback_data="consultant")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_ask_question: {e}")

    @standard_handler
    async def show_example_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать примеры вопросов"""
        try:
            text = """
📋 <b>Примеры вопросов</b>

<b>💼 Для бизнеса:</b>
• "Как автоматизировать прием заказов?"
• "Какой бот нужен для интернет-магазина?"
• "Как интегрировать бота с CRM?"

<b>🏪 Для ритейла:</b>
• "Как сделать каталог товаров в боте?"
• "Можно ли принимать платежи в боте?"
• "Как настроить уведомления о заказах?"

<b>🎓 Для образования:</b>
• "Как создать бота для онлайн-курсов?"
• "Можно ли тестировать учеников через бота?"
• "Как отправлять домашние задания?"

<b>🏥 Для услуг:</b>
• "Как сделать запись на прием через бота?"
• "Можно ли отправлять напоминания клиентам?"
• "Как интегрировать с календарем?"

<b>💰 О стоимости:</b>
• "Сколько стоит простой бот?"
• "Что влияет на цену разработки?"
• "Есть ли помесячная оплата?"

Выберите любой вопрос как пример или задайте свой!
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Задать свой вопрос", callback_data="ask_question")],
                [InlineKeyboardButton("🔙 К консультанту", callback_data="consultant")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_example_questions: {e}")

    @standard_handler
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать настройки пользователя"""
        try:
            user_id = update.effective_user.id
            logger.info(f"🔧 Showing settings for user {user_id}")
            
            # Получаем данные пользователя из базы данных
            with get_db_context() as db:
                user = get_user_by_telegram_id(db, user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                
                # Получаем данные пользователя из метаданных
                timeweb_login = ""
                timeweb_password = ""
                bot_token = ""
                
                if user.preferences:
                    timeweb_creds = user.preferences.get('timeweb_credentials', {})
                    timeweb_login = timeweb_creds.get('login', '')
                    timeweb_password = timeweb_creds.get('password', '')
                    bot_token = user.preferences.get('bot_token', '')
                
                # Если нет данных в профиле, ищем в последнем проекте
                if not timeweb_login and not bot_token:
                    project = db.query(Project).filter(Project.user_id == user.id).order_by(Project.created_at.desc()).first()
                    if project and project.project_metadata:
                        timeweb_creds = project.project_metadata.get('timeweb_credentials', {})
                        timeweb_login = timeweb_creds.get('login', '')
                        timeweb_password = timeweb_creds.get('password', '')
                        bot_token = project.project_metadata.get('bot_token', '')
            
            # Маскируем пароль и токен для безопасности
            masked_password = "*" * len(timeweb_password) if timeweb_password else "не указан"
            masked_token = f"{bot_token[:10]}..." if bot_token and len(bot_token) > 10 else "не указан"
            
            text = f"""
⚙️ <b>Настройки</b>

<b>🌐 Данные Timeweb:</b>
• Логин: {timeweb_login or "не указан"}
• Пароль: {masked_password}

<b>🤖 Данные бота:</b>
• API токен: {masked_token}

<b>💡 Инструкции:</b>
• Нажмите на кнопку ниже для настройки параметров
• Данные автоматически применятся к новым проектам
• Для изменения существующих проектов обратитесь к менеджеру
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌐 Настроить Timeweb", callback_data="setup_timeweb"),
                    InlineKeyboardButton("🤖 Настроить бота", callback_data="setup_bot_token")
                ],
                [
                    InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_settings: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при загрузке настроек. Попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )

    @standard_handler
    async def setup_timeweb(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройка Timeweb"""
        try:
            text = """🌐 <b>Ввод данных Timeweb</b>

Отправьте данные от Timeweb в одном из форматов:

<b>Формат 1:</b>
<code>Логин: ваш_email@example.com
Пароль: ваш_пароль</code>

<b>Формат 2:</b>
<code>ваш_email@example.com
ваш_пароль</code>

<b>💡 Примеры логина:</b>
• email@example.com
• +7 900 123 45 67
• myusername

<b>⚠️ Важно:</b>
• Отправьте данные следующим сообщением
• Данные будут сохранены в зашифрованном виде
• Используются только для настройки хостинга"""
            
            # Устанавливаем флаг ожидания данных Timeweb
            context.user_data['waiting_timeweb_settings'] = True
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Зарегистрироваться", url="https://timeweb.cloud/r/xv15146")],
                [InlineKeyboardButton("❌ Отменить", callback_data="settings")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в setup_timeweb: {e}")
    
    @standard_handler
    async def setup_bot_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройка API токена бота"""
        try:
            text = """🤖 <b>Ввод API токена бота</b>

Отправьте токен от @BotFather:

<b>Формат токена:</b>
<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>

<b>⚠️ Важно:</b>
• Скопируйте токен полностью
• Не добавляйте лишние символы
• Токен сохраняется только в вашем профиле

<b>Как получить токен:</b>
1. Откройте @BotFather в Telegram
2. Отправьте /newbot
3. Следуйте инструкциям
4. Скопируйте токен"""
            
            # Устанавливаем флаг ожидания токена
            context.user_data['waiting_bot_token_settings'] = True
            logger.info(f"🔑 Установлен флаг waiting_bot_token_settings для пользователя {update.effective_user.id}")
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Открыть @BotFather", url="https://t.me/botfather")],
                [InlineKeyboardButton("❌ Отменить", callback_data="settings")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в setup_bot_token: {e}")


    @standard_handler
    async def save_timeweb_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение настроек Timeweb"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            logger.info(f"🌐 Начинаем сохранение данных Timeweb для пользователя {user_id}")
            
            # Проверяем, ожидаем ли мы данные Timeweb
            if not context.user_data.get('waiting_timeweb_settings'):
                logger.info(f"🌐 Флаг waiting_timeweb_settings не установлен для пользователя {user_id}")
                return
            
            # Парсим данные
            login_match = re.search(r'логин:\s*(.+)', message_text, re.IGNORECASE)
            password_match = re.search(r'пароль:\s*(.+)', message_text, re.IGNORECASE)
            
            if login_match and password_match:
                login = login_match.group(1).strip()
                password = password_match.group(1).strip()
            else:
                # Пробуем простой формат (логин и пароль на разных строках)
                lines = message_text.strip().split('\n')
                if len(lines) >= 2:
                    login = lines[0].strip()
                    password = lines[1].strip()
                else:
                    await update.message.reply_text(
                        "❌ Неверный формат данных. Попробуйте еще раз.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
                        ])
                    )
                    return
            
            # Сохраняем в базу данных
            with get_db_context() as db:
                user = get_user_by_telegram_id(db, user_id)
                if user:
                    if not user.preferences:
                        user.preferences = {}
                    
                    user.preferences['timeweb_credentials'] = {
                        'login': login,
                        'password': password,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    db.commit()
                    logger.info(f"🌐 Данные Timeweb сохранены для пользователя {user_id} в preferences")
                else:
                    logger.error(f"🌐 Пользователь {user_id} не найден в базе данных")
            
            # Очищаем флаг ожидания
            context.user_data.pop('waiting_timeweb_settings', None)
            
            await update.message.reply_text(
                "✅ <b>Данные Timeweb сохранены!</b>\n\n"
                "Теперь эти данные будут автоматически применяться к новым проектам и отображаться в расширенной информации о проектах.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚙️ К настройкам", callback_data="settings")]
                ]),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в save_timeweb_settings: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при сохранении данных. Попробуйте еще раз.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
                ])
            )

    @standard_handler
    async def save_bot_token_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение настроек API токена бота"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text.strip()
            logger.info(f"🔑 Начинаем сохранение токена для пользователя {user_id}, токен: {message_text[:10]}...")
            
            # Проверяем, ожидаем ли мы токен
            if not context.user_data.get('waiting_bot_token_settings'):
                logger.info(f"🔑 Флаг waiting_bot_token_settings не установлен для пользователя {user_id}")
                return
            
            # Проверяем формат токена
            if not self._validate_bot_token(message_text):
                logger.warning(f"🔑 Неверный формат токена от пользователя {user_id}: {message_text[:10]}...")
                await update.message.reply_text(
                    "❌ Неверный формат токена. Токен должен иметь вид: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
                    ])
                )
                return
            
            # Сохраняем в базу данных
            with get_db_context() as db:
                user = get_user_by_telegram_id(db, user_id)
                if user:
                    if not user.preferences:
                        user.preferences = {}
                    
                    user.preferences['bot_token'] = message_text
                    user.preferences['bot_token_added_at'] = datetime.utcnow().isoformat()
                    db.commit()
                    logger.info(f"🔑 Токен бота сохранен для пользователя {user_id} в preferences")
                else:
                    logger.error(f"🔑 Пользователь {user_id} не найден в базе данных")
            
            # Очищаем флаг ожидания
            context.user_data.pop('waiting_bot_token_settings', None)
            
            await update.message.reply_text(
                "✅ <b>API токен бота сохранен!</b>\n\n"
                "Теперь этот токен будет автоматически применляться к новым проектам и отображаться в расширенной информации о проектах.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚙️ К настройкам", callback_data="settings")]
                ]),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в save_bot_token_settings: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при сохранении токена. Попробуйте еще раз.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
                ])
            )


    @standard_handler
    async def handle_revision_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка фотографий при создании правки"""
        try:
            user_id = update.effective_user.id
            
            logger.info(f"📸 REVISION PHOTO: user_id={user_id}")
            logger.info(f"📸 Context state: {context.user_data.get('creating_revision_step')}")
            
            # Проверяем, что пользователь действительно на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"📸 User {user_id} sent photo but not in files step")
                await update.message.reply_text(
                    "📷 Фотография получена, но вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Делегируем обработку в revisions handler
            from .revisions import revisions_handler
            await revisions_handler.handle_revision_photo(update, context)
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_photo: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке фотографии. Попробуйте еще раз."
                )
            except:
                pass

    async def handle_revision_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка видео при создании правки"""
        try:
            user_id = update.effective_user.id
            
            logger.info(f"🎥 REVISION VIDEO: user_id={user_id}")
            logger.info(f"🎥 Context state: {context.user_data.get('creating_revision_step')}")
            
            # Проверяем, что пользователь действительно на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"🎥 User {user_id} sent video but not in files step")
                await update.message.reply_text(
                    "🎥 Видео получено, но вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Делегируем обработку в revisions handler
            from .revisions import revisions_handler
            await revisions_handler.handle_revision_video(update, context)
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_video: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке видео. Попробуйте еще раз."
                )
            except:
                pass

    async def handle_revision_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка документов при создании правки"""
        try:
            user_id = update.effective_user.id
            document = update.message.document
            file_name = document.file_name if document else "unknown"
            
            logger.info(f"📄 REVISION DOCUMENT: user_id={user_id}, file_name={file_name}")
            logger.info(f"📄 Context state: {context.user_data.get('creating_revision_step')}")
            
            # Проверяем, что пользователь действительно на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"📄 User {user_id} sent document but not in files step")
                await update.message.reply_text(
                    f"📄 Документ '{file_name}' получен, но вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Делегируем обработку в revisions handler
            from .revisions import revisions_handler
            await revisions_handler.handle_revision_document(update, context)
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_document: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке документа. Попробуйте еще раз."
                )
            except:
                pass

    async def handle_revision_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка файлов при создании правки"""
        try:
            user_id = update.effective_user.id
            
            logger.info(f"📂 REVISION FILES: user_id={user_id}")
            logger.info(f"📂 Context data: {context.user_data}")
            
            # Проверяем, что пользователь действительно на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"📂 User {user_id} is not in files step")
                await update.message.reply_text(
                    "📂 Вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Инициализируем список файлов если его нет
            if 'creating_revision_files' not in context.user_data:
                context.user_data['creating_revision_files'] = []
                logger.info(f"📂 Initialized file list")
            
            # Обрабатываем документы
            if update.message and update.message.document:
                document = update.message.document
                
                # Проверяем, что файл подходит по типу
                if not is_allowed_file_type(document.file_name):
                    await update.message.reply_text(
                        "❌ Неподдерживаемый тип файла. Пожалуйста, отправьте документ в формате PDF, DOCX или TXT.",
                        reply_markup=get_back_to_main_keyboard()
                    )
                    return
                
                file_info = await context.bot.get_file(document.file_id)
                
                # Сохраняем информацию о файле
                context.user_data['creating_revision_files'].append({
                    'file_id': document.file_id,
                    'file_name': document.file_name,
                    'file_size': document.file_size,
                    'mime_type': document.mime_type
                })
                
                log_user_action(user_id, "revision_file_added", document.file_name)
                
                await update.message.reply_text(
                    f"📂 Документ '{document.file_name}' добавлен к правке.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➡️ Далее", callback_data="revision_files_done")]
                    ])
                )
            
            # Обрабатываем фотографии
            elif update.message and update.message.photo:
                # Берем фото наилучшего качества
                photo = update.message.photo[-1]
                file_info = await context.bot.get_file(photo.file_id)
                
                # Сохраняем информацию о файле
                context.user_data['creating_revision_files'].append({
                    'file_id': photo.file_id,
                    'file_name': f"photo_{len(context.user_data['creating_revision_files']) + 1}.jpg",
                    'file_size': photo.file_size,
                    'mime_type': "image/jpeg"
                })
                
                log_user_action(user_id, "revision_photo_added", f"photo_{len(context.user_data['creating_revision_files'])}")
                
                await update.message.reply_text(
                    f"📸 Фотография добавлена к правке.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➡️ Далее", callback_data="revision_files_done")]
                    ])
                )
            
            # Обрабатываем видео
            elif update.message and update.message.video:
                video = update.message.video
                file_info = await context.bot.get_file(video.file_id)
                
                # Сохраняем информацию о файле
                context.user_data['creating_revision_files'].append({
                    'file_id': video.file_id,
                    'file_name': f"video_{len(context.user_data['creating_revision_files']) + 1}.mp4",
                    'file_size': video.file_size,
                    'mime_type': "video/mp4"
                })
                
                log_user_action(user_id, "revision_video_added", f"video_{len(context.user_data['creating_revision_files'])}")
                
                await update.message.reply_text(
                    f"🎥 Видео добавлено к правке.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➡️ Далее", callback_data="revision_files_done")]
                    ])
                )
            
            else:
                await update.message.reply_text(
                    "📂 Пожалуйста, отправьте документ, фотографию или видео для добавления к правке.",
                    reply_markup=get_back_to_main_keyboard()
                )
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_files: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке файлов. Попробуйте еще раз."
                )
            except:
                pass

    @standard_handler
    async def show_project_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать чат проекта"""
        try:
            query = update.callback_query
            project_id = int(query.data.replace('project_chat_', ''))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, update.effective_user.id)
                
                # Получаем проект
                project = db.query(Project).filter(
                    Project.id == project_id,
                    Project.user_id == user.id
                ).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                # Получаем все правки проекта
                revisions = db.query(ProjectRevision).filter(
                    ProjectRevision.project_id == project_id
                ).order_by(ProjectRevision.created_at.desc()).all()
                
                # Формируем сообщение
                text = f"💬 <b>Чат проекта: {project.title}</b>\n\n"
                
                if not revisions:
                    text += "📝 <b>Пока нет правок по этому проекту</b>\n\n"
                    text += "Создайте первую правку, чтобы начать общение с исполнителем!"
                else:
                    # Показываем последние 5 правок
                    text += f"📋 <b>Правки проекта ({len(revisions)}):</b>\n\n"
                    
                    for i, revision in enumerate(revisions[:5]):
                        status_emoji = self._get_revision_status_emoji(revision.status)
                        priority_emoji = self._get_revision_priority_emoji(revision.priority)
                        
                        # Получаем количество сообщений
                        messages_count = db.query(RevisionMessage).filter(
                            RevisionMessage.revision_id == revision.id
                        ).count()
                        
                        text += f"{i+1}. {status_emoji} <b>Правка #{revision.revision_number}</b>\n"
                        text += f"   📝 {revision.title}\n"
                        text += f"   {priority_emoji} {self._get_revision_priority_name(revision.priority)}\n"
                        text += f"   💬 Сообщений: {messages_count}\n"
                        text += f"   📅 {self._format_date(revision.created_at)}\n\n"
                    
                    if len(revisions) > 5:
                        text += f"... и ещё {len(revisions) - 5} правок\n\n"
                
                text += "🔹 Выберите правку для просмотра сообщений или создайте новую"
                
                # Создаем клавиатуру
                keyboard = []
                
                # Кнопки для последних правок
                for revision in revisions[:5]:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"💬 Правка #{revision.revision_number}", 
                            callback_data=f"revision_chat_{revision.id}"
                        )
                    ])
                
                # Кнопки управления
                keyboard.append([
                    InlineKeyboardButton("➕ Создать правку", callback_data=f"create_revision_{project_id}"),
                    InlineKeyboardButton("📋 Все правки", callback_data=f"project_revisions_{project_id}")
                ])
                
                keyboard.append([
                    InlineKeyboardButton("🔙 К проекту", callback_data=f"project_details_{project_id}"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ])
                
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
            
        except Exception as e:
            logger.error(f"Ошибка в show_project_chat: {e}")
            await query.answer("Произошла ошибка при открытии чата")

    def _get_revision_status_emoji(self, status: str) -> str:
        """Получить эмодзи для статуса правки"""
        emojis = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'rejected': '❌'
        }
        return emojis.get(status, '❓')
    
    def _get_revision_status_name(self, status: str) -> str:
        """Получить название статуса правки"""
        names = {
            'pending': 'В ожидании',
            'in_progress': 'В работе',
            'completed': 'Выполнено',
            'rejected': 'Отклонено'
        }
        return names.get(status, status)
    
    def _get_revision_priority_emoji(self, priority: str) -> str:
        """Получить эмодзи для приоритета правки"""
        emojis = {
            'low': '🟢',
            'normal': '🔵',
            'high': '🟡',
            'urgent': '🔴'
        }
        return emojis.get(priority, '⚪')
    
    def _get_revision_priority_name(self, priority: str) -> str:
        """Получить название приоритета правки"""
        names = {
            'low': 'Низкий',
            'normal': 'Обычный',
            'high': 'Высокий',
            'urgent': 'Срочный'
        }
        return names.get(priority, priority)
    
    def _format_date(self, date) -> str:
        """Форматировать дату для отображения"""
        if not date:
            return "Неизвестно"
        try:
            return date.strftime("%d.%m.%Y %H:%M")
        except:
            return "Неизвестно"
    
    async def _send_revision_images(self, query, revision_id: int, messages: list):
        """Отправить изображения из сообщений правки"""
        try:
            from ...database.database import get_db_context
            import os
            from pathlib import Path
            
            with get_db_context() as db:
                # Получаем файлы из последних 5 сообщений
                recent_messages = messages[-5:] if len(messages) > 5 else messages
                
                for message in recent_messages:
                    # Получаем файлы сообщения
                    message_files = db.query(RevisionMessageFile).filter(
                        RevisionMessageFile.message_id == message.id
                    ).all()
                    
                    for file in message_files:
                        if file.file_type == 'image':
                            file_path = Path(file.file_path)
                            
                            # Проверяем существование файла
                            if file_path.exists():
                                try:
                                    # Определяем отправителя
                                    sender_name = "Клиент"
                                    if message.sender_type == "admin" or message.sender_type == "executor":
                                        sender_name = "Исполнитель"
                                    
                                    # Создаем подпись к изображению
                                    caption = f"📸 От: {sender_name}\n"
                                    caption += f"📅 {self._format_date(message.created_at)}\n"
                                    caption += f"📎 {file.original_filename}"
                                    
                                    # Отправляем изображение
                                    with open(file_path, 'rb') as photo:
                                        await query.bot.send_photo(
                                            chat_id=query.message.chat_id,
                                            photo=photo,
                                            caption=caption,
                                            parse_mode='HTML'
                                        )
                                        
                                except Exception as e:
                                    logger.error(f"Ошибка при отправке изображения {file.original_filename}: {e}")
                                    
                                    # Отправляем сообщение об ошибке
                                    await query.bot.send_message(
                                        chat_id=query.message.chat_id,
                                        text=f"❌ Не удалось загрузить изображение: {file.original_filename}",
                                        parse_mode='HTML'
                                    )
                            else:
                                # Файл не найден
                                await query.bot.send_message(
                                    chat_id=query.message.chat_id,
                                    text=f"❌ Файл не найден: {file.original_filename}",
                                    parse_mode='HTML'
                                )
                        
        except Exception as e:
            logger.error(f"Ошибка в _send_revision_images: {e}")

    @standard_handler
    async def show_revision_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать чат конкретной правки"""
        try:
            query = update.callback_query
            revision_id = int(query.data.replace('revision_chat_', ''))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, update.effective_user.id)
                
                # Получаем правку
                revision = db.query(ProjectRevision).filter(
                    ProjectRevision.id == revision_id,
                    ProjectRevision.created_by_id == user.id
                ).first()
                
                if not revision:
                    await query.answer("Правка не найдена")
                    return
                
                # Получаем сообщения правки
                messages = db.query(RevisionMessage).filter(
                    RevisionMessage.revision_id == revision_id
                ).order_by(RevisionMessage.created_at.asc()).all()
                
                # Формируем сообщение
                status_emoji = self._get_revision_status_emoji(revision.status)
                priority_emoji = self._get_revision_priority_emoji(revision.priority)
                
                text = f"💬 <b>Чат правки #{revision.revision_number}</b>\n\n"
                text += f"📝 <b>Заголовок:</b> {revision.title}\n"
                text += f"{status_emoji} <b>Статус:</b> {self._get_revision_status_name(revision.status)}\n"
                text += f"{priority_emoji} <b>Приоритет:</b> {self._get_revision_priority_name(revision.priority)}\n\n"
                
                if not messages:
                    text += "💬 <b>Пока нет сообщений</b>\n\n"
                    text += "Общение с исполнителем будет отображаться здесь"
                else:
                    text += f"💬 <b>Сообщения ({len(messages)}):</b>\n\n"
                    
                    # Показываем последние 5 сообщений
                    for message in messages[-5:]:
                        sender_name = "Клиент"
                        sender_emoji = "👤"
                        
                        if message.sender_type == "admin" or message.sender_type == "executor":
                            sender_name = "Исполнитель"
                            sender_emoji = "👨‍💻"
                        
                        message_text = message.message
                        if len(message_text) > 100:
                            message_text = message_text[:100] + "..."
                        
                        text += f"{sender_emoji} <b>{sender_name}</b>\n"
                        text += f"📅 {self._format_date(message.created_at)}\n"
                        text += f"💬 {message_text}\n"
                        
                        # Обрабатываем файлы сообщения
                        message_files = db.query(RevisionMessageFile).filter(
                            RevisionMessageFile.message_id == message.id
                        ).all()
                        
                        if message_files:
                            text += "📎 <b>Файлы:</b>\n"
                            for file in message_files:
                                if file.file_type == 'image':
                                    text += f"🖼️ {file.original_filename}\n"
                                elif file.file_type == 'video':
                                    text += f"🎥 {file.original_filename}\n"
                                elif file.file_type == 'document':
                                    text += f"📄 {file.original_filename}\n"
                                else:
                                    text += f"📎 {file.original_filename}\n"
                        
                        text += "\n"
                    
                    if len(messages) > 5:
                        text += f"... и ещё {len(messages) - 5} сообщений\n\n"
                
                text += "🔹 Выберите действие:"
                
                # Создаем клавиатуру
                keyboard = [
                    [InlineKeyboardButton("💬 Написать сообщение", callback_data=f"revision_comment_{revision_id}")],
                    [InlineKeyboardButton("📋 Детали правки", callback_data=f"revision_details_{revision_id}")],
                    [InlineKeyboardButton("🔙 К чату проекта", callback_data=f"project_chat_{revision.project_id}")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                
                # Отправляем изображения как отдельные сообщения
                await self._send_revision_images(query, revision_id, messages)
            
        except Exception as e:
            logger.error(f"Ошибка в show_revision_chat: {e}")
            await query.answer("Произошла ошибка при открытии чата правки")

    @standard_handler
    async def start_revision_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать добавление комментария к правке"""
        try:
            query = update.callback_query
            revision_id = int(query.data.replace('revision_comment_', ''))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, update.effective_user.id)
                
                # Получаем правку
                revision = db.query(ProjectRevision).filter(
                    ProjectRevision.id == revision_id,
                    ProjectRevision.created_by_id == user.id
                ).first()
                
                if not revision:
                    await query.answer("Правка не найдена")
                    return
                
                # Сохраняем ID правки в контекст для последующей обработки
                context.user_data['commenting_revision_id'] = revision_id
                
                text = f"""
💬 <b>Добавление комментария к правке #{revision.revision_number}</b>

📝 <b>Заголовок:</b> {revision.title}

📋 <b>Инструкция:</b>
1. Напишите ваш комментарий или вопрос
2. При необходимости прикрепите файлы (фото, документы)
3. Подтвердите отправку

✍️ <b>Напишите ваш комментарий:</b>
                """
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Отмена", callback_data=f"revision_chat_{revision_id}")]
                ])
                
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
        except Exception as e:
            logger.error(f"Ошибка в start_revision_comment: {e}")
            await query.answer("Произошла ошибка при создании комментария")

    @standard_handler
    async def handle_revision_comment_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текста комментария к правке"""
        try:
            if 'commenting_revision_id' not in context.user_data:
                return
            
            revision_id = context.user_data['commenting_revision_id']
            comment_text = update.message.text
            
            # Сохраняем текст комментария
            context.user_data['comment_text'] = comment_text
            context.user_data['comment_files'] = []
            
            text = f"""
💬 <b>Комментарий готов к отправке</b>

📝 <b>Ваш комментарий:</b>
{comment_text}

📎 <b>Файлы:</b> Нет

🔹 Выберите действие:
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📎 Прикрепить файл", callback_data=f"attach_file_{revision_id}")],
                [InlineKeyboardButton("✅ Отправить", callback_data=f"send_comment_{revision_id}")],
                [InlineKeyboardButton("❌ Отмена", callback_data=f"revision_chat_{revision_id}")]
            ])
            
            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_revision_comment_text: {e}")
            await update.message.reply_text("Произошла ошибка при обработке комментария")

    @standard_handler
    async def send_revision_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправить комментарий к правке"""
        try:
            query = update.callback_query
            revision_id = int(query.data.replace('send_comment_', ''))
            
            if ('commenting_revision_id' not in context.user_data or 
                context.user_data['commenting_revision_id'] != revision_id or
                'comment_text' not in context.user_data):
                await query.answer("Ошибка: данные комментария не найдены")
                return
            
            comment_text = context.user_data['comment_text']
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, update.effective_user.id)
                
                # Получаем правку
                revision = db.query(ProjectRevision).filter(
                    ProjectRevision.id == revision_id,
                    ProjectRevision.created_by_id == user.id
                ).first()
                
                if not revision:
                    await query.answer("Правка не найдена")
                    return
                
                # Создаем сообщение
                revision_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message=comment_text,
                    is_internal=False
                )
                
                db.add(revision_message)
                db.commit()
                db.refresh(revision_message)
                
                # Отправляем уведомление админам/исполнителям
                await self._send_comment_notification(revision, revision_message, user)
                
                # Очищаем контекст
                context.user_data.pop('commenting_revision_id', None)
                context.user_data.pop('comment_text', None)
                context.user_data.pop('comment_files', None)
                
                await query.edit_message_text(
                    f"✅ <b>Комментарий отправлен!</b>\n\n"
                    f"Ваш комментарий по правке #{revision.revision_number} отправлен исполнителю.\n"
                    f"Вы получите уведомление о ответе.",
                    parse_mode='HTML'
                )
                
                # Показываем чат правки
                await self.show_revision_chat(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка в send_revision_comment: {e}")
            await query.answer("Произошла ошибка при отправке комментария")

    async def _send_comment_notification(self, revision: ProjectRevision, message: RevisionMessage, user):
        """Отправить уведомление о новом комментарии"""
        try:
            from ...services.notification_service import notification_service
            
            # Отправляем уведомление админам
            await notification_service.send_admin_notification(
                f"💬 <b>Новый комментарий от клиента</b>\n\n"
                f"📋 <b>Проект:</b> {revision.project.title}\n"
                f"🔢 <b>Правка:</b> #{revision.revision_number}\n"
                f"👤 <b>От:</b> {user.first_name or user.username or 'Клиент'}\n\n"
                f"📝 <b>Комментарий:</b>\n{message.message[:300]}{'...' if len(message.message) > 300 else ''}"
            )
            
            logger.info(f"Comment notification sent: revision_id={revision.id}, message_id={message.id}")
            
        except Exception as e:
            logger.error(f"Error sending comment notification: {e}")

    async def download_project_tz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Скачать ТЗ проекта"""
        try:
            query = update.callback_query
            project_id = int(query.data.replace('project_download_', ''))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, update.effective_user.id)
                
                project = db.query(Project).filter(
                    Project.id == project_id,
                    Project.user_id == user.id
                ).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                project_data = {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description,
                    'status': project.status,
                    'estimated_cost': project.estimated_cost,
                    'created_at': project.created_at
                }
            
            text = f"""
📄 <b>Техническое задание</b>

<b>Проект:</b> {project_data['title']}
<b>ID:</b> #{project_data['id']}
<b>Статус:</b> {project_data['status']}
<b>Стоимость:</b> {format_currency(project_data['estimated_cost'])}

<b>Описание:</b>
{project_data['description']}

<b>Дата создания:</b> {format_datetime(project_data['created_at'])}

🚧 <b>Полная версия ТЗ в разработке</b>

В полной версии будет:
• Детальные требования
• Схемы и макеты
• Техническая документация
• Файлы проекта
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📧 Запросить ТЗ на email", callback_data=f"request_tz_{project_id}")],
                [InlineKeyboardButton("🔙 К проекту", callback_data=f"project_details_{project_id}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в download_project_tz: {e}")
            await query.answer("Произошла ошибка при подготовке ТЗ к скачиванию")


# Константы для общих сообщений
ERROR_MESSAGES = {
    'general': "❌ Произошла ошибка. Попробуйте еще раз или обратитесь в поддержку.",
    'permission_denied': "❌ У вас нет прав для выполнения этого действия.",
    'invalid_input': "❌ Некорректный ввод. Попробуйте еще раз.",
    'user_not_found': "❌ Пользователь не найден.",
    'session_expired': "❌ Сессия истекла. Попробуйте начать заново.",
    'rate_limit': "⏳ Слишком много запросов. Подождите немного.",
    'maintenance': "🔧 Ведутся технические работы. Попробуйте позже."
}

SUCCESS_MESSAGES = {
    'saved': "✅ Данные сохранены успешно!",
    'updated': "✅ Информация обновлена!",
    'deleted': "✅ Удалено успешно!",
    'sent': "✅ Сообщение отправлено!",
    'completed': "✅ Операция завершена успешно!"
}

# Общие утилиты для работы с пользователями
async def get_user_context(update: Update) -> Optional[Dict[str, Any]]:
    """Получить контекст пользователя"""
    try:
        if not update.effective_user:
            return None
            
        user_id = update.effective_user.id
        
        with get_db_context() as db:
            db_user = get_user_by_telegram_id(db, user_id)
            if not db_user:
                db_user = get_or_create_user(
                    db=db,
                    telegram_id=user_id,
                    username=update.effective_user.username,
                    first_name=update.effective_user.first_name,
                    last_name=update.effective_user.last_name
                )
            
            # Получаем статистику пользователя
            projects_count = db.query(Project).filter(Project.user_id == db_user.id).count()
            sessions_count = db.query(ConsultantSession).filter(ConsultantSession.user_id == db_user.id).count()
            
            return {
                'db_user': db_user,
                'telegram_user': update.effective_user,
                'projects_count': projects_count,
                'sessions_count': sessions_count,
                'is_new_user': db_user.registration_date is None or 
                              (datetime.utcnow() - db_user.registration_date) < timedelta(hours=24)
            }
    except Exception as e:
        logger.error(f"Ошибка получения контекста пользователя: {e}")
        return None

async def update_user_context(user_id: int, **updates) -> bool:
    """Обновить данные пользователя"""
    try:
        with get_db_context() as db:
            user = get_user_by_telegram_id(db, user_id)
            if user:
                for key, value in updates.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                db.commit()
                return True
        return False
    except Exception as e:
        logger.error(f"Ошибка обновления контекста пользователя: {e}")
        return False

# Общие функции для работы с сообщениями
async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать индикатор печати"""
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
    except Exception as e:
        logger.error(f"Ошибка отправки typing action: {e}")

async def send_safe_message(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: str = 'HTML',
    disable_web_page_preview: bool = True
) -> Optional[Message]:
    """Безопасная отправка сообщения с обработкой ошибок"""
    try:
        # Ограничиваем длину сообщения
        if len(text) > 4000:
            text = text[:3900] + "\n\n... (сообщение сокращено)"
        
        if update.callback_query:
            return await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )
        else:
            return await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        # Пробуем отправить упрощенное сообщение
        try:
            fallback_text = "Произошла ошибка при отправке сообщения."
            if update.callback_query:
                return await update.callback_query.edit_message_text(
                    text=fallback_text,
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                return await update.message.reply_text(
                    text=fallback_text,
                    reply_markup=get_main_menu_keyboard()
                )
        except Exception as fallback_error:
            logger.error(f"Ошибка отправки fallback сообщения: {fallback_error}")
            return None

async def answer_callback_query(
    update: Update,
    text: Optional[str] = None,
    show_alert: bool = False
):
    """Безопасный ответ на callback query"""
    try:
        if update.callback_query:
            await update.callback_query.answer(text=text, show_alert=show_alert)
    except Exception as e:
        logger.error(f"Ошибка ответа на callback query: {e}")

# Функции для работы с состояниями пользователя
async def set_user_state(user_id: int, state: str, context_data: Optional[Dict] = None) -> bool:
    """Установить состояние пользователя"""
    try:
        with get_db_context() as db:
            success = update_user_state(db, user_id, state)
            if success and context_data:
                # Сохраняем дополнительные данные в контексте
                # В реальной реализации можно использовать Redis или другое хранилище
                pass
            return success
    except Exception as e:
        logger.error(f"Ошибка установки состояния пользователя: {e}")
        return False

async def get_user_state(user_id: int) -> Optional[str]:
    """Получить текущее состояние пользователя"""
    try:
        with get_db_context() as db:
            user = get_user_by_telegram_id(db, user_id)
            return user.state if user else None
    except Exception as e:
        logger.error(f"Ошибка получения состояния пользователя: {e}")
        return None

async def clear_user_state(user_id: int) -> bool:
    """Очистить состояние пользователя (вернуть в main_menu)"""
    return await set_user_state(user_id, "main_menu")

# Функции для валидации данных
def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    # Убираем все нецифровые символы кроме +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    # Проверяем длину и формат
    return len(clean_phone) >= 10 and (clean_phone.startswith('+') or clean_phone.startswith('8'))

def validate_text_length(text: str, min_length: int = 10, max_length: int = 2000) -> bool:
    """Валидация длины текста"""
    return min_length <= len(text.strip()) <= max_length

def sanitize_text(text: str) -> str:
    """Очистка текста от потенциально опасного контента"""
    # Удаляем HTML теги
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Ограничиваем длину
    if len(clean_text) > 4000:
        clean_text = clean_text[:3900] + "..."
    return clean_text.strip()

# Функции для работы с настройками
async def get_setting(key: str, default: Any = None) -> Any:
    """Получить значение настройки"""
    try:
        with get_db_context() as db:
            setting = db.query(Settings).filter(Settings.key == key).first()
            if setting:
                # Пытаемся преобразовать в нужный тип
                try:
                    if setting.value.lower() in ['true', 'false']:
                        return setting.value.lower() == 'true'
                    elif setting.value.isdigit():
                        return int(setting.value)
                    elif '.' in setting.value and setting.value.replace('.', '').isdigit():
                        return float(setting.value)
                    else:
                        return setting.value
                except:
                    return setting.value
            return default
    except Exception as e:
        logger.error(f"Ошибка получения настройки {key}: {e}")
        return default

async def set_setting(key: str, value: Any) -> bool:
    """Установить значение настройки"""
    try:
        with get_db_context() as db:
            setting = db.query(Settings).filter(Settings.key == key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = Settings(key=key, value=str(value))
                db.add(setting)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка установки настройки {key}: {e}")
        return False

# Функции для форматирования данных
def format_datetime(dt: datetime, format_type: str = 'full') -> str:
    """Форматирование даты и времени"""
    if not dt:
        return "Не указано"
    
    if format_type == 'date':
        return dt.strftime('%d.%m.%Y')
    elif format_type == 'time':
        return dt.strftime('%H:%M')
    elif format_type == 'short':
        return dt.strftime('%d.%m.%Y %H:%M')
    else:  # full
        return dt.strftime('%d.%m.%Y в %H:%M')

def format_currency(amount: Union[int, float], currency: str = '₽') -> str:
    """Форматирование валюты"""
    if amount is None:
        return "Не указано"
    return f"{amount:,.0f} {currency}".replace(',', ' ')

def format_duration(days: int) -> str:
    """Форматирование продолжительности"""
    if days == 1:
        return "1 день"
    elif days < 5:
        return f"{days} дня"
    else:
        return f"{days} дней"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Обрезание текста с добавлением суффикса"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

# Функции для работы с файлами
def get_file_size_str(size_bytes: int) -> str:
    """Конвертация размера файла в читаемый формат"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def is_allowed_file_type(filename: str, allowed_types: List[str] = None) -> bool:
    """Проверка разрешенного типа файла"""
    if not allowed_types:
        allowed_types = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
    
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in allowed_types)

# Функции для уведомлений
async def send_notification_to_admins(
    context: ContextTypes.DEFAULT_TYPE,
    message: str,
    notification_type: str = "info"
) -> bool:
    """Отправка уведомления администраторам"""
    try:
        notification_service = NotificationService()
        return await notification_service.send_admin_notification(
            message=message,
            notification_type=notification_type,
            context=context
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления админам: {e}")
        return False

async def send_user_notification(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    message: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None
) -> bool:
    """Отправка уведомления пользователю"""
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
        return False

# Функции для логирования
async def log_user_interaction(
    user_id: int,
    action: str,
    details: Optional[str] = None,
    success: bool = True
):
    """Логирование взаимодействия пользователя"""
    try:
        log_user_action(
            user_id=user_id,
            action=action,
            details=details or ""
        )
        
        # Можно добавить дополнительное логирование в БД
        if not success:
            logger.warning(f"Неуспешное действие пользователя {user_id}: {action}")
            
    except Exception as e:
        logger.error(f"Ошибка логирования взаимодействия: {e}")

# Функции для работы с callback данными
def parse_callback_data(callback_data: str) -> Dict[str, str]:
    """Парсинг callback данных"""
    try:
        parts = callback_data.split('_')
        if len(parts) >= 2:
            return {
                'action': parts[0],
                'type': parts[1],
                'id': parts[2] if len(parts) > 2 else None,
                'extra': '_'.join(parts[3:]) if len(parts) > 3 else None
            }
        return {'action': callback_data}
    except Exception as e:
        logger.error(f"Ошибка парсинга callback данных: {e}")
        return {'action': callback_data}

def build_callback_data(action: str, type_: str = None, id_: Union[str, int] = None, extra: str = None) -> str:
    """Построение callback данных"""
    parts = [action]
    if type_:
        parts.append(type_)
    if id_:
        parts.append(str(id_))
    if extra:
        parts.append(extra)
    
    result = '_'.join(parts)
    # Telegram ограничивает callback_data до 64 байт
    if len(result) > 64:
        logger.warning(f"Callback data слишком длинные: {result}")
        result = result[:64]
    
    return result

# Функции для работы с конверсациями
async def start_conversation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    conversation_type: str,
    initial_message: str,
    keyboard: Optional[InlineKeyboardMarkup] = None
) -> bool:
    """Запуск конверсации"""
    try:
        user_id = update.effective_user.id
        
        # Устанавливаем состояние пользователя
        await set_user_state(user_id, conversation_type)
        
        # Отправляем начальное сообщение
        await send_safe_message(
            update=update,
            context=context,
            text=initial_message,
            reply_markup=keyboard
        )
        
        await log_user_interaction(user_id, f"start_conversation_{conversation_type}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка запуска конверсации: {e}")
        return False

async def end_conversation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    success_message: str = None
) -> bool:
    """Завершение конверсации"""
    try:
        user_id = update.effective_user.id
        
        # Очищаем состояние пользователя
        await clear_user_state(user_id)
        
        # Очищаем данные контекста
        context.user_data.clear()
        
        # Отправляем сообщение о завершении
        if success_message:
            await send_safe_message(
                update=update,
                context=context,
                text=success_message,
                reply_markup=get_main_menu_keyboard()
            )
        
        await log_user_interaction(user_id, "end_conversation")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка завершения конверсации: {e}")
        return False

# Декораторы для общих проверок
def require_user_state(required_state: str):
    """Декоратор для проверки состояния пользователя"""
    def decorator(func):
        @standard_handler
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            current_state = await get_user_state(user_id)
            
            if current_state != required_state:
                await send_safe_message(
                    update=update,
                    context=context,
                    text="❌ Неверная последовательность действий. Начните заново.",
                    reply_markup=get_main_menu_keyboard()
                )
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def require_text_input(func):
    """Декоратор для проверки текстового ввода"""
    @standard_handler
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.message or not update.message.text:
            await send_safe_message(
                update=update,
                context=context,
                text="❌ Пожалуйста, отправьте текстовое сообщение.",
                reply_markup=get_back_to_main_keyboard()
            )
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

# Функции для аналитики
async def track_user_action(
    user_id: int,
    action_type: str,
    action_data: Optional[Dict] = None
):
    """Отслеживание действий пользователя для аналитики"""
    try:
        # Здесь можно добавить логику для отправки данных в аналитику
        await log_user_interaction(
            user_id=user_id,
            action=f"analytics_{action_type}",
            details=str(action_data) if action_data else None
        )
    except Exception as e:
        logger.error(f"Ошибка отслеживания действия пользователя: {e}")

# Вспомогательные функции для UI
def create_confirmation_keyboard(
    confirm_callback: str,
    cancel_callback: str = "main_menu",
    confirm_text: str = "✅ Подтвердить",
    cancel_text: str = "❌ Отмена"
) -> InlineKeyboardMarkup:
    """Создание клавиатуры подтверждения"""
    keyboard = [
        [
            InlineKeyboardButton(confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(cancel_text, callback_data=cancel_callback)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_back_keyboard(
    back_callback: str = "main_menu",
    back_text: str = "🏠 Главное меню"
) -> InlineKeyboardMarkup:
    """Создание клавиатуры с кнопкой назад"""
    keyboard = [[InlineKeyboardButton(back_text, callback_data=back_callback)]]
    return InlineKeyboardMarkup(keyboard)

# Функции для работы с медиа
async def handle_media_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    allowed_types: List[str] = None
) -> Optional[Dict[str, Any]]:
    """Обработка медиа сообщений"""
    try:
        message = update.message
        
        if message.photo:
            # Берем фото наилучшего качества
            photo = message.photo[-1]
            file_info = await context.bot.get_file(photo.file_id)
            return {
                'type': 'photo',
                'file_id': photo.file_id,
                'file_size': photo.file_size,
                'file_path': file_info.file_path
            }
        
        elif message.document:
            document = message.document
            if allowed_types and not is_allowed_file_type(document.file_name, allowed_types):
                await send_safe_message(
                    update=update,
                    context=context,
                    text=f"❌ Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_types)}"
                )
                return None
            
            file_info = await context.bot.get_file(document.file_id)
            return {
                'type': 'document',
                'file_id': document.file_id,
                'file_name': document.file_name,
                'file_size': document.file_size,
                'file_path': file_info.file_path,
                'mime_type': document.mime_type
            }
        
        elif message.voice:
            voice = message.voice
            file_info = await context.bot.get_file(voice.file_id)
            return {
                'type': 'voice',
                'file_id': voice.file_id,
                'file_size': voice.file_size,
                'file_path': file_info.file_path,
                'duration': voice.duration
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Ошибка обработки медиа: {e}")
        return None
