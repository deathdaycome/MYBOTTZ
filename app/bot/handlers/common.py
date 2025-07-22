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
                # ВАЖНО: Полностью сбрасываем состояние при переходе в главное меню
                context.user_data.clear()
                logger.info(f"🔄 Состояние пользователя {user_id} полностью сброшено")
                
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
                
            elif callback_data == "consultant":
                logger.info(f"🤖 Обрабатываем consultant для пользователя {user_id}")
                await self.show_consultant_menu(update, context)
                
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
                
            elif callback_data == "setup_telegram_id":
                logger.info(f"📱 Обрабатываем setup_telegram_id для пользователя {user_id}")
                await self.setup_telegram_id(update, context)
                
            elif callback_data == "bot_enter_token":
                logger.info(f"🔑 Обрабатываем bot_enter_token для пользователя {user_id}")
                await self.show_bot_token_projects(update, context)
                
            elif callback_data == "bot_guide_steps":
                logger.info(f"📖 Обрабатываем bot_guide_steps для пользователя {user_id}")
                await self.show_bot_guide_steps(update, context)
                
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
                context.user_data.pop('waiting_telegram_id', None)
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
                
            # Проверяем, ожидаем ли мы Telegram ID
            if context.user_data.get('waiting_telegram_id'):
                logger.info(f"📱 Обрабатываем Telegram ID для пользователя {user_id}")
                await self.save_telegram_id(update, context)
                return
                
            # Проверяем, ожидаем ли мы вопрос для AI консультанта
            if context.user_data.get('waiting_ai_question'):
                logger.info(f"🤖 Обрабатываем вопрос для AI консультанта от пользователя {user_id}")
                await self.handle_ai_question(update, context)
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


    async def handle_revision_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка документов при создании правки"""
        try:
            user_id = update.effective_user.id
            
            logger.info(f"📄 REVISION DOCUMENT: user_id={user_id}")
            logger.info(f"📄 Context state: {context.user_data.get('creating_revision_step')}")
            
            # Проверяем, что пользователь действительно на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"📄 User {user_id} sent document but not in files step")
                await update.message.reply_text(
                    "📄 Документ получен, но вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Делегируем обработку в revisions handler
            from .revisions import revisions_handler
            await revisions_handler.handle_revision_document(update, context)
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_document: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке документа. Попробуйте еще раз."
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
            
            # Пока что просто сообщение (можно добавить обработку видео в revisions handler позже)
            await update.message.reply_text(
                "🎥 Видео получено! Обработка видео файлов пока не поддерживается. Пожалуйста, прикрепите изображения или документы."
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_video: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке видео. Попробуйте еще раз."
                )
            except:
                pass

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
            # Устанавливаем флаг ожидания вопроса
            context.user_data['waiting_ai_question'] = True
            log_user_action(update.effective_user.id, "show_ask_question", "Handler called")
            
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

    async def handle_ai_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать вопрос для AI консультанта"""
        try:
            user_id = update.effective_user.id
            question = update.message.text
            
            logger.info(f"🤖 AI консультант: получен вопрос от {user_id}: '{question[:100]}...'")
            
            # Убираем флаг ожидания
            context.user_data.pop('waiting_ai_question', None)
            
            # Отправляем уведомление о том, что обрабатываем вопрос
            processing_msg = await update.message.reply_text(
                "🤖 AI консультант обрабатывает ваш вопрос...\n⏳ Пожалуйста, подождите..."
            )
            
            # Импортируем AI сервис
            from ...services.openai_service import ai_service
            
            # Получаем ответ от AI консультанта
            result = await ai_service.consultant_response(question)
            ai_response = result.get('response')
            
            if ai_response:
                # Удаляем сообщение о загрузке
                await processing_msg.delete()
                
                # Формируем финальное сообщение
                final_text = f"🤖 <b>AI Консультант</b>\n\n{ai_response}"
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 Задать еще вопрос", callback_data="ask_question")],
                    [InlineKeyboardButton("🔙 К консультанту", callback_data="consultant")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
                
                await update.message.reply_text(
                    final_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                log_user_action(user_id, "ai_question_answered", question[:50])
            else:
                await processing_msg.edit_text(
                    "❌ Извините, произошла ошибка при обработке вашего вопроса. Попробуйте еще раз."
                )
                
        except Exception as e:
            logger.error(f"Ошибка в handle_ai_question: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке вашего вопроса. Попробуйте позже."
            )

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
                    InlineKeyboardButton("📱 Telegram ID", callback_data="setup_telegram_id")
                ],
                [
                    InlineKeyboardButton("🎯 Создать бота", callback_data="create_bot_guide"),
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
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            try:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке фотографии. Попробуйте еще раз."
                )
            except:
                pass

    @standard_handler
    async def setup_telegram_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройка Telegram ID пользователя"""
        try:
            user_id = update.effective_user.id
            logger.info(f"📱 Настройка Telegram ID для пользователя {user_id}")
            
            # Получаем текущий Telegram ID из базы данных
            with get_db_context() as db:
                user = get_user_by_telegram_id(db, user_id)
                current_telegram_id = ""
                if user and user.preferences:
                    current_telegram_id = user.preferences.get('telegram_id', '')
            
            text = f"""📱 <b>Настройка Telegram ID</b>

<b>Ваш текущий Telegram ID:</b> {current_telegram_id or "не указан"}

<b>📋 Инструкция для получения Telegram ID:</b>

1️⃣ Перейдите к боту @infouserbot
2️⃣ Нажмите кнопку "Start" или отправьте команду /start
3️⃣ Бот автоматически пришлет ваш Telegram ID
4️⃣ Скопируйте полученное число
5️⃣ Отправьте его следующим сообщением

<b>💡 Пример Telegram ID:</b> 123456789

<b>⚡ Зачем нужен Telegram ID:</b>
• Автоматическая привязка к проектам
• Отображение в административной консоли
• Упрощение связи с менеджером

Отправьте ваш Telegram ID следующим сообщением:"""

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 Открыть @infouserbot", url="https://t.me/infouserbot")],
                [InlineKeyboardButton("⚙️ К настройкам", callback_data="settings")]
            ])
            
            # Устанавливаем флаг ожидания Telegram ID
            context.user_data['waiting_telegram_id'] = True
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в setup_telegram_id: {e}")

    async def save_telegram_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение Telegram ID пользователя"""
        try:
            user_id = update.effective_user.id
            telegram_id_input = update.message.text.strip()
            
            # Проверяем, ожидаем ли мы Telegram ID
            if not context.user_data.get('waiting_telegram_id'):
                return
            
            # Проверяем формат Telegram ID (должен быть числом)
            try:
                telegram_id_number = int(telegram_id_input)
                if telegram_id_number <= 0:
                    raise ValueError("ID должен быть положительным числом")
            except ValueError:
                await update.message.reply_text(
                    "❌ Неверный формат Telegram ID. ID должен быть положительным числом.\n\n"
                    "Пример: 123456789\n\n"
                    "Попробуйте еще раз:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🤖 Открыть @infouserbot", url="https://t.me/infouserbot")],
                        [InlineKeyboardButton("⚙️ К настройкам", callback_data="settings")]
                    ])
                )
                return
            
            # Сохраняем в базу данных
            with get_db_context() as db:
                user = get_user_by_telegram_id(db, user_id)
                if user:
                    if not user.preferences:
                        user.preferences = {}
                    
                    user.preferences['telegram_id'] = str(telegram_id_number)
                    user.preferences['telegram_id_added_at'] = datetime.utcnow().isoformat()
                    
                    # Также сохраняем в метаданные всех проектов пользователя
                    projects = db.query(Project).filter(Project.user_id == user.id).all()
                    for project in projects:
                        if not project.project_metadata:
                            project.project_metadata = {}
                        project.project_metadata['user_telegram_id'] = str(telegram_id_number)
                    
                    db.commit()
                    logger.info(f"📱 Telegram ID {telegram_id_number} сохранен для пользователя {user_id}")
            
            # Очищаем флаг ожидания
            context.user_data.pop('waiting_telegram_id', None)
            
            await update.message.reply_text(
                f"✅ <b>Telegram ID успешно сохранен!</b>\n\n"
                f"📱 Ваш ID: <code>{telegram_id_number}</code>\n\n"
                f"✨ ID добавлен во все ваши проекты и будет отображаться в административной консоли.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚙️ К настройкам", callback_data="settings")]
                ]),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в save_telegram_id: {e}")

    @standard_handler  
    async def show_bot_token_projects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать проекты для выбора при вводе API токена"""
        try:
            user_id = update.effective_user.id
            
            # Получаем проекты пользователя
            with get_db_context() as db:
                user = get_user_by_telegram_id(db, user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                
                projects = db.query(Project).filter(Project.user_id == user.id).order_by(Project.created_at.desc()).all()
            
            if not projects:
                # Если нет проектов, создаем новый
                text = """🔑 <b>Ввод API токена бота</b>

У вас пока нет проектов. 
Создадим новый проект для вашего бота!

Отправьте API токен, полученный от @BotFather следующим сообщением:

<b>Пример токена:</b>
<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>"""
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 Открыть BotFather", url="https://t.me/BotFather")],
                    [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
                ])
                
                # Устанавливаем флаг ожидания токена для нового проекта
                context.user_data['waiting_bot_token_for'] = 'new_project'
                
            else:
                # Показываем список проектов для выбора
                text = """🔑 <b>Выбор проекта для API токена</b>

Выберите проект, к которому хотите добавить API токен бота:"""
                
                keyboard_rows = []
                for project in projects[:10]:  # Показываем только первые 10
                    status_emoji = {
                        'new': '🆕', 'review': '👀', 'accepted': '✅', 
                        'in_progress': '🔄', 'testing': '🧪', 
                        'completed': '✨', 'cancelled': '❌'
                    }.get(project.status, '📋')
                    
                    title = project.title[:30] + "..." if len(project.title) > 30 else project.title
                    keyboard_rows.append([
                        InlineKeyboardButton(
                            f"{status_emoji} {title}", 
                            callback_data=f"bot_token_project_{project.id}"
                        )
                    ])
                
                keyboard_rows.extend([
                    [InlineKeyboardButton("➕ Создать новый проект", callback_data="bot_token_new_project")],
                    [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard_rows)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_bot_token_projects: {e}")

    @standard_handler
    async def show_bot_guide_steps(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать пошаговую инструкцию создания бота"""
        try:
            text = """📖 <b>Пошаговая инструкция создания бота</b>

<b>Шаг 1:</b> Откройте @BotFather
👆 Нажмите кнопку ниже или найдите @BotFather в поиске

<b>Шаг 2:</b> Отправьте команду <code>/newbot</code>
📱 BotFather попросит ввести имя бота

<b>Шаг 3:</b> Введите имя вашего бота
💬 Например: "Мой Первый Бот"

<b>Шаг 4:</b> Введите username бота
🔗 Должен заканчиваться на "bot", например: my_first_bot

<b>Шаг 5:</b> Получите API токен
🔑 BotFather пришлет вам токен вида: <code>123456789:ABCdef...</code>

<b>Шаг 6:</b> Скопируйте токен и введите его здесь
💾 Мы сохраним его в информации о вашем проекте

⚠️ <b>Важно:</b> Никому не сообщайте ваш API токен!"""

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 Открыть BotFather", url="https://t.me/BotFather")],
                [InlineKeyboardButton("🔑 Ввести API токен", callback_data="bot_enter_token")],
                [InlineKeyboardButton("🔙 К настройкам", callback_data="settings")]
            ])

            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в show_bot_guide_steps: {e}")