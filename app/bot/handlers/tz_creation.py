import asyncio
import json
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from ..keyboards.main import get_create_tz_methods_keyboard, get_main_menu_keyboard, get_yes_no_keyboard
from ..keyboards.tz import get_tz_actions_keyboard, get_step_by_step_keyboard, get_tz_editing_keyboard
from ...database.database import get_db_context, create_project
from ...database.models import User, Project
from ...services.openai_service import ai_service
from ...services.file_service import process_uploaded_file
from ...services.speech_service import process_voice_message
from ...config.logging import get_logger, log_user_action
from ...utils.helpers import format_currency

logger = get_logger(__name__)

class TZCreationHandler:
    """Обработчик создания технических заданий"""
    
    # Переносим состояния внутрь класса
    TZ_METHOD, TZ_TEXT_INPUT, TZ_VOICE_INPUT, TZ_STEP_BY_STEP, TZ_FILE_UPLOAD, TZ_REVIEW, TZ_EDIT, DESCRIPTION, CONFIRMATION = range(9)
    
    def __init__(self):
        self.step_questions = [
            {
                "question": "📱 Какой тип бота вы хотите создать?",
                "options": ["Telegram бот", "WhatsApp бот", "Веб-чатбот", "Комплексное решение"],
                "key": "bot_type"
            },
            {
                "question": "🎯 Какова основная цель вашего бота?",
                "options": ["Продажи и заказы", "Поддержка клиентов", "Автоматизация бизнеса", "Развлечения", "Другое"],
                "key": "main_goal"
            },
            {
                "question": "👥 Кто ваша целевая аудитория?",
                "options": ["B2B клиенты", "B2C покупатели", "Сотрудники компании", "Широкая аудитория"],
                "key": "target_audience"
            },
            {
                "question": "💰 Планируете ли интеграцию с платежами?",
                "options": ["Да, обязательно", "Возможно в будущем", "Нет, не нужно"],
                "key": "payments"
            },
            {
                "question": "🔗 Нужна ли интеграция с внешними сервисами?",
                "options": ["CRM системы", "Базы данных", "API сервисы", "Социальные сети", "Не нужно"],
                "key": "integrations"
            },
            {
                "question": "📊 Нужна ли админ-панель для управления?",
                "options": ["Да, полноценная", "Простая админка", "Не нужна"],
                "key": "admin_panel"
            },
            {
                "question": "⏱ Какие у вас сроки реализации?",
                "options": ["Срочно (до недели)", "Стандартно (2-4 недели)", "Не торопимся (1-2 месяца)"],
                "key": "timeline"
            },
            {
                "question": "💵 Какой у вас примерный бюджет?",
                "options": ["До 25,000₽", "25,000-50,000₽", "50,000-100,000₽", "Свыше 100,000₽", "Обсудим"],
                "key": "budget"
            }
        ]
    
    async def show_tz_creation_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню создания ТЗ"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "show_tz_creation_menu")
            
            text = """
📝 <b>Создание технического задания</b>

Выберите удобный для вас способ создания ТЗ:

🔹 <b>Текстом</b> - опишите проект в свободной форме
🔹 <b>Голосом</b> - расскажите о проекте голосовым сообщением  
🔹 <b>Пошагово</b> - ответьте на наводящие вопросы
🔹 <b>Документом</b> - загрузите готовое описание

AI автоматически структурирует ваше описание и создаст детальное техническое задание с оценкой стоимости.
            """
            
            keyboard = get_create_tz_methods_keyboard()
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            logger.info(f"🔄 ConversationHandler: переходим в состояние TZ_METHOD для пользователя {user_id}")
            return self.TZ_METHOD
            
        except Exception as e:
            logger.error(f"Ошибка в show_tz_creation_menu: {e}")
            await self._send_error_message(update, "Ошибка при загрузке меню создания ТЗ")
            return ConversationHandler.END
    
    async def select_tz_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор метода создания ТЗ"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            method = query.data.replace('tz_', '')
            
            log_user_action(user_id, "select_tz_method", method)
            
            # Инициализируем данные пользователя в context
            context.user_data['tz_creation'] = {
                "method": method,
                "step": 0,
                "answers": {}
            }
            
            if method == "text":
                return await self.start_text_input(update, context)
                
            elif method == "voice":
                return await self.start_voice_input(update, context)
                
            elif method == "step_by_step":
                return await self.start_step_by_step(update, context)
                
            elif method == "upload":
                return await self.start_file_upload(update, context)
            
            else:
                await query.answer("Метод не поддерживается")
                return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Ошибка в select_tz_method: {e}")
            await self._send_error_message(update, "Ошибка при выборе метода создания ТЗ")
            return ConversationHandler.END
    
    async def start_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать ввод ТЗ текстом"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "start_text_input")
            
            text = """
📝 <b>Описание проекта текстом</b>

Опишите ваш проект в свободной форме. Укажите:

• Тип бота (Telegram/WhatsApp/веб-бот)
• Основные функции и возможности
• Целевая аудитория
• Особые требования к дизайну/интерфейсу
• Нужны ли интеграции с другими сервисами
• Примерные сроки и бюджет

AI проанализирует ваше описание и создаст структурированное ТЗ.

<i>Напишите описание вашего проекта:</i>
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]
            ])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            return self.TZ_TEXT_INPUT
            
        except Exception as e:
            logger.error(f"Ошибка в start_text_input: {e}")
            return ConversationHandler.END
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать текстовый ввод ТЗ"""
        try:
            user_id = update.effective_user.id
            user_text = update.message.text
            
            log_user_action(user_id, "handle_text_input", f"Length: {len(user_text)}")
            
            # Проверяем минимальную длину
            if len(user_text) < 20:
                await update.message.reply_text(
                    "📝 Описание слишком короткое. Пожалуйста, опишите проект более подробно (минимум 20 символов)."
                )
                return self.TZ_TEXT_INPUT
            
            # Показываем, что бот обрабатывает
            processing_message = await update.message.reply_text("🤖 Анализирую ваше описание и создаю ТЗ...")
            
            try:
                # Создаем структурированное ТЗ через AI
                tz_data = await self._generate_tz_from_text(user_text, user_id)
                
                # Удаляем сообщение о обработке
                await processing_message.delete()
                
                if tz_data:
                    # Сохраняем данные для пользователя в context
                    context.user_data['tz_creation'] = tz_data
                    
                    # Показываем предварительное ТЗ
                    await self._show_generated_tz(update, context, tz_data)
                    return self.TZ_REVIEW
                else:
                    await update.message.reply_text(
                        "❌ Не удалось обработать описание. Попробуйте еще раз или выберите другой способ создания ТЗ.",
                        reply_markup=get_main_menu_keyboard()
                    )
                    return ConversationHandler.END
                    
            except Exception as e:
                logger.error(f"Ошибка при генерации ТЗ: {e}")
                await processing_message.delete()
                await update.message.reply_text(
                    "❌ Произошла ошибка при создании ТЗ. Проверьте подключение к AI-сервису.",
                    reply_markup=get_main_menu_keyboard()
                )
                return ConversationHandler.END
                
        except Exception as e:
            logger.error(f"Ошибка в handle_text_input: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке. Попробуйте еще раз.",
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END
    
    async def start_voice_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать ввод ТЗ голосом"""
        try:
            text = """
🎤 <b>Голосовое описание проекта</b>

Запишите голосовое сообщение с описанием вашего проекта.

Расскажите:
• Что за бот вы хотите
• Какие функции должны быть
• Для кого предназначен
• Особые пожелания

<i>Отправьте голосовое сообщение:</i>
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]
            ])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            return self.TZ_VOICE_INPUT
            
        except Exception as e:
            logger.error(f"Ошибка в start_voice_input: {e}")
            return ConversationHandler.END
    
    # В файле app/bot/handlers/tz_creation.py замените метод handle_voice_input на:

    async def handle_voice_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Улучшенный обработчик голосового ввода ТЗ для русского языка"""
        try:
            user_id = update.effective_user.id
            voice = update.message.voice
            
            log_user_action(user_id, "handle_voice_input", f"Duration: {voice.duration}s, Size: {voice.file_size}")
            
            # Проверяем поддержку голосового сообщения
            from ...services.speech_service import speech_service
            if not speech_service.is_voice_supported(voice):
                await update.message.reply_text(
                    "❌ Проблема с голосовым сообщением:\n"
                    "• Длительность: от 1 сек до 5 минут\n"
                    "• Размер: до 50МБ\n"
                    "• Говорите четко и ясно",
                    reply_markup=get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Получаем информацию об аудио
            voice_data = await context.bot.get_file(voice.file_id)
            voice_bytes = await voice_data.download_as_bytearray()
            audio_info = await speech_service.get_audio_info(bytes(voice_bytes))
            
            logger.info(f"Обрабатываем аудио: {audio_info}")
            
            # Показываем детальное сообщение о процессе
            processing_message = await update.message.reply_text(
                f"🎤 Обрабатываю голосовое сообщение...\n"
                f"⏱ Длительность: {voice.duration} сек\n"
                f"🔊 Распознавание русской речи..."
            )
            
            try:
                # Распознаем речь
                recognized_text = await speech_service.process_voice_message(voice, context.bot)
                
                if recognized_text and len(recognized_text.strip()) >= 15:
                    logger.info(f"Речь успешно распознана: '{recognized_text}'")
                    
                    # Обновляем сообщение о процессе
                    await processing_message.edit_text(
                        f"✅ Речь распознана!\n"
                        f"🤖 Создаю техническое задание..."
                    )
                    
                    # Используем распознанный текст для создания ТЗ
                    tz_data = await self._generate_tz_from_text(recognized_text, user_id)
                    
                    # Удаляем сообщение о обработке
                    await processing_message.delete()
                    
                    if tz_data:
                        # Добавляем метаинформацию
                        tz_data['source'] = 'voice'
                        tz_data['recognized_text'] = recognized_text
                        tz_data['voice_duration'] = voice.duration
                        
                        # Сохраняем данные для пользователя в context
                        context.user_data['tz_creation'] = tz_data
                        
                        # Показываем распознанный текст
                        preview_text = (
                            f"🎤 <b>Распознанный текст:</b>\n"
                            f"<i>«{recognized_text}»</i>\n\n"
                            f"📋 <b>Создано техническое задание:</b>"
                        )
                        
                        await update.message.reply_text(preview_text, parse_mode='HTML')
                        
                        # Показываем сгенерированное ТЗ
                        await self._show_generated_tz(update, context, tz_data)
                        return self.TZ_REVIEW
                    else:
                        await update.message.reply_text(
                            f"✅ <b>Речь распознана:</b>\n"
                            f"<i>«{recognized_text}»</i>\n\n"
                            f"❌ Не удалось создать ТЗ. Попробуйте добавить больше деталей о проекте.",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🎤 Записать заново", callback_data="tz_voice")],
                                [InlineKeyboardButton("📝 Ввести текстом", callback_data="tz_text")],
                                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                            ]),
                            parse_mode='HTML'
                        )
                        return ConversationHandler.END
                
                elif recognized_text:
                    await processing_message.delete()
                    await update.message.reply_text(
                        f"🎤 <b>Распознанный текст:</b>\n"
                        f"<i>«{recognized_text}»</i>\n\n"
                        f"📝 Описание получилось коротким. Для создания качественного ТЗ опишите:\n"
                        f"• Тип проекта (бот/сайт/приложение)\n"
                        f"• Основные функции\n"
                        f"• Целевую аудиторию\n"
                        f"• Особые требования",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🎤 Записать подробнее", callback_data="tz_voice")],
                            [InlineKeyboardButton("📝 Дополнить текстом", callback_data="tz_text")],
                            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                        ]),
                        parse_mode='HTML'
                    )
                    return ConversationHandler.END
                
                else:
                    await processing_message.delete()
                    
                    # Даем детальные рекомендации
                    tips_text = (
                        "❌ <b>Не удалось распознать речь</b>\n\n"
                        "🎯 <b>Советы для лучшего распознавания:</b>\n"
                        "• Говорите четко и не спеша\n"
                        "• Записывайте в тихом месте\n"
                        "• Держите телефон близко ко рту\n"
                        "• Избегайте фоновых шумов\n"
                        "• Делайте паузы между предложениями\n\n"
                        "🗣 <b>Пример хорошего описания:</b>\n"
                        "<i>«Мне нужен телеграм бот для ресторана. Бот должен показывать меню, принимать заказы и обрабатывать оплату. Целевая аудитория — посетители ресторана»</i>"
                    )
                    
                    await update.message.reply_text(
                        tips_text,
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🎤 Попробовать еще раз", callback_data="tz_voice")],
                            [InlineKeyboardButton("📝 Написать текстом", callback_data="tz_text")],
                            [InlineKeyboardButton("📋 Пошаговое создание", callback_data="tz_step_by_step")],
                            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                        ]),
                        parse_mode='HTML'
                    )
                    return ConversationHandler.END
                    
            except Exception as e:
                logger.error(f"Ошибка при обработке голоса: {e}")
                await processing_message.delete()
                
                error_text = (
                    f"❌ <b>Ошибка при обработке голосового сообщения</b>\n\n"
                    f"🔧 Возможные причины:\n"
                    f"• Проблемы с интернет-соединением\n"
                    f"• Перегрузка сервиса распознавания\n"
                    f"• Неподдерживаемый формат аудио\n\n"
                    f"💡 Попробуйте:\n"
                    f"• Записать заново через минуту\n"
                    f"• Использовать текстовое описание\n"
                    f"• Обратиться в поддержку"
                )
                
                await update.message.reply_text(
                    error_text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Попробовать снова", callback_data="tz_voice")],
                        [InlineKeyboardButton("📝 Текстовое описание", callback_data="tz_text")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                    ]),
                    parse_mode='HTML'
                )
                return ConversationHandler.END
                
        except Exception as e:
            logger.error(f"Критическая ошибка в handle_voice_input: {e}")
            await update.message.reply_text(
                "❌ Произошла критическая ошибка. Попробуйте использовать текстовое описание или обратитесь в поддержку.",
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END
    
    async def start_step_by_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать пошаговое создание ТЗ"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "start_step_by_step")
            
            # Инициализируем данные пользователя в context
            context.user_data['tz_creation'] = {
                'method': 'step_by_step',
                'step': 0,
                'answers': {}
            }
            
            await self._ask_step_question(update, context, 0)
            return self.TZ_STEP_BY_STEP
            
        except Exception as e:
            logger.error(f"Ошибка в start_step_by_step: {e}")
            return ConversationHandler.END
    
    async def handle_step_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать ответ на вопрос пошагового создания"""
        try:
            user_id = update.effective_user.id
            callback_data = update.callback_query.data
            
            if 'tz_creation' not in context.user_data:
                await update.callback_query.answer("Сессия истекла. Начните заново.")
                return ConversationHandler.END
            
            # Извлекаем ответ
            answer = callback_data.replace("step_", "")
            current_step = context.user_data['tz_creation']['step']
            
            # Сохраняем ответ
            question_key = self.step_questions[current_step]['key']
            context.user_data['tz_creation']['answers'][question_key] = answer
            
            # Переходим к следующему вопросу
            next_step = current_step + 1
            
            if next_step < len(self.step_questions):
                context.user_data['tz_creation']['step'] = next_step
                await self._ask_step_question(update, context, next_step)
                return self.TZ_STEP_BY_STEP
            else:
                # Все вопросы отвечены, генерируем ТЗ
                await update.callback_query.edit_message_text("🤖 Создаю ТЗ на основе ваших ответов...")
                
                try:
                    tz_data = await self._generate_tz_from_steps(context.user_data['tz_creation']['answers'], user_id)
                    
                    if tz_data:
                        context.user_data['tz_creation'].update(tz_data)
                        await self._show_generated_tz(update, context, tz_data)
                        return self.TZ_REVIEW
                    else:
                        await update.callback_query.edit_message_text(
                            "❌ Не удалось создать ТЗ. Попробуйте еще раз.",
                            reply_markup=get_main_menu_keyboard()
                        )
                        return ConversationHandler.END
                        
                except Exception as e:
                    logger.error(f"Ошибка при генерации ТЗ из шагов: {e}")
                    await update.callback_query.edit_message_text(
                        "❌ Ошибка при создании ТЗ. Проверьте подключение к AI-сервису.",
                        reply_markup=get_main_menu_keyboard()
                    )
                    return ConversationHandler.END
                    
        except Exception as e:
            logger.error(f"Ошибка в handle_step_answer: {e}")
            return ConversationHandler.END
    
    async def start_file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать загрузку файла с ТЗ"""
        try:
            text = """
📄 <b>Загрузка документа</b>

Загрузите файл с описанием проекта:
• PDF, DOC, DOCX
• TXT файлы
• Изображения с текстом

<i>Отправьте файл:</i>
            """
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]
            ])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            return self.TZ_FILE_UPLOAD
            
        except Exception as e:
            logger.error(f"Ошибка в start_file_upload: {e}")
            return ConversationHandler.END
    
    async def handle_file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать загрузку файла"""
        try:
            await update.message.reply_text(
                "📄 Обработка файлов временно недоступна. Попробуйте текстовое описание.",
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Ошибка в handle_file_upload: {e}")
            return ConversationHandler.END
    
    async def handle_review_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать действие в режиме просмотра ТЗ"""
        try:
            callback_data = update.callback_query.data
            user_id = update.effective_user.id
            logger.info(f"handle_review_action: пользователь {user_id}, callback_data: {callback_data}")
            
            if callback_data == "review_save":
                logger.info(f"Пользователь {user_id} нажал кнопку сохранения")
                await self._save_tz(update, context)
                return ConversationHandler.END
            elif callback_data == "review_edit":
                await update.callback_query.answer("Редактирование в разработке")
                return self.TZ_REVIEW
            elif callback_data == "review_regenerate":
                await update.callback_query.answer("Повторная генерация в разработке")
                return self.TZ_REVIEW
            else:
                return ConversationHandler.END
                
        except Exception as e:
            logger.error(f"Ошибка в handle_review_action: {e}")
            return ConversationHandler.END

    async def _send_error_message(self, update: Update, message: str):
        """Отправка сообщения об ошибке"""
        try:
            error_text = f"❌ {message}\n\nПопробуйте еще раз или вернитесь в главное меню."
            keyboard = get_main_menu_keyboard()
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    error_text,
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    error_text,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")

    async def _ask_step_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
        """Задать вопрос для пошагового создания"""
        try:
            question_data = self.step_questions[step]
            
            text = f"""
📋 <b>Вопрос {step + 1} из {len(self.step_questions)}</b>

{question_data['question']}
            """
            
            # Создаем кнопки с вариантами ответов
            buttons = []
            for i, option in enumerate(question_data['options']):
                buttons.append([InlineKeyboardButton(option, callback_data=f"step_{option}")])
            
            buttons.append([InlineKeyboardButton("❌ Отмена", callback_data="main_menu")])
            keyboard = InlineKeyboardMarkup(buttons)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка в _ask_step_question: {e}")
    
    async def _generate_tz_from_text(self, text: str, user_id: int) -> Optional[Dict]:
        """Генерировать ТЗ из текстового описания"""
        try:
            # Используем метод create_technical_specification вместо generate_response
            tz_data = await ai_service.create_technical_specification(
                user_request=text,
                additional_context={"user_id": user_id, "method": "text"}
            )
            
            return tz_data
            
        except Exception as e:
            logger.error(f"Ошибка в _generate_tz_from_text: {e}")
            return None
    
    async def _generate_tz_from_steps(self, answers: Dict, user_id: int) -> Optional[Dict]:
        """Генерировать ТЗ из пошаговых ответов"""
        try:
            # Формируем текст из ответов
            answers_text = "\n".join([f"{k}: {v}" for k, v in answers.items()])
            
            # Создаем описание проекта на основе ответов
            project_description = f"""
Проект бота на основе пошагового опроса:

{answers_text}

Пожалуйста, создайте детальное техническое задание на основе этих данных.
            """
            
            # Используем метод create_technical_specification
            tz_data = await ai_service.create_technical_specification(
                user_request=project_description,
                additional_context={"method": "step_by_step", "user_id": user_id, "answers": answers}
            )
            
            return tz_data
            
        except Exception as e:
            logger.error(f"Ошибка в _generate_tz_from_steps: {e}")
            return None
    
    async def _show_generated_tz(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tz_data: Dict):
        """Показать сгенерированное ТЗ"""
        try:
            # Если есть готовый текст ТЗ, показываем его
            if 'tz_text' in tz_data and tz_data['tz_text']:
                tz_text = tz_data['tz_text']
                # Ограничиваем длину для Telegram (до 4096 символов)
                if len(tz_text) > 3800:
                    tz_text = tz_text[:3800] + "\n\n... (полное ТЗ будет в проекте)"
                
                text = f"📋 <b>Сгенерированное техническое задание</b>\n\n{tz_text}"
            else:
                # Fallback для старого формата
                title = tz_data.get('title', 'Новый проект')
                description = tz_data.get('description', 'Описание не указано')
                estimated_cost = tz_data.get('estimated_cost', 0)
                complexity = tz_data.get('complexity', 'medium')
                
                # Безопасно получаем функции
                bot_sections = tz_data.get('bot_sections', [])
                functions = []
                if bot_sections and isinstance(bot_sections, list):
                    for section in bot_sections:
                        if isinstance(section, dict) and 'functions' in section:
                            section_functions = section['functions']
                            if isinstance(section_functions, list):
                                functions.extend(section_functions)
                
                # Если функций нет, берем из detailed_functions
                if not functions:
                    detailed_functions = tz_data.get('detailed_functions', [])
                    if isinstance(detailed_functions, list):
                        for func in detailed_functions:
                            if isinstance(func, dict) and 'function_name' in func:
                                functions.append(func['function_name'])
                            elif isinstance(func, str):
                                functions.append(func)
                
                functions_text = self._format_list(functions) if functions else "• Базовая функциональность"
                
                text = f"""
📋 <b>Сгенерированное техническое задание</b>

<b>📌 Название:</b> {title}

<b>📝 Описание:</b>
{description}

<b>⚙️ Основные функции:</b>
{functions_text}

<b>💰 Примерная стоимость:</b> {format_currency(estimated_cost)}

<b>📊 Сложность:</b> {self._format_complexity(complexity)}
                """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Сохранить проект", callback_data="review_save"),
                    InlineKeyboardButton("✏️ Редактировать", callback_data="review_edit")
                ],
                [
                    InlineKeyboardButton("🔄 Пересоздать", callback_data="review_regenerate"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка в _show_generated_tz: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"tz_data keys: {list(tz_data.keys()) if isinstance(tz_data, dict) else 'not dict'}")
            await self._send_error_message(update, "Ошибка при отображении ТЗ")

    async def _save_tz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранить ТЗ как проект"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Начало сохранения ТЗ для пользователя {user_id}")
            
            if 'tz_creation' not in context.user_data:
                logger.warning(f"Данные для пользователя {user_id} не найдены в context.user_data")
                if update.callback_query:
                    await update.callback_query.answer("Данные не найдены")
                return
            
            logger.info(f"Данные пользователя {user_id} найдены: {list(context.user_data['tz_creation'].keys())}")
            
            tz_data = context.user_data['tz_creation']
            
            # Сохраняем проект в БД
            project = None
            try:
                with get_db_context() as db:
                    from ...database.database import get_or_create_user
                    user = get_or_create_user(db, user_id)
                    
                    project_data = {
                        'title': tz_data.get('title', 'Новый проект'),
                        'description': tz_data.get('description', ''),
                        'estimated_cost': tz_data.get('estimated_cost', 0),
                        'estimated_hours': tz_data.get('estimated_hours', 0),
                        'complexity': tz_data.get('complexity', 'medium'),
                        'status': 'new',
                        'structured_tz': tz_data  # Сохраняем полное ТЗ в structured_tz
                    }
                    
                    # Если есть полный текст ТЗ, добавляем его в описание
                    if 'tz_text' in tz_data and tz_data['tz_text']:
                        project_data['description'] = tz_data['tz_text'][:1000] + "..." if len(tz_data['tz_text']) > 1000 else tz_data['tz_text']
                    
                    project = create_project(db, user.id, project_data)
                    db.commit()  # Сохраняем изменения
                    
                    # Получаем ID проекта перед закрытием сессии
                    project_id = project.id
                    
                    logger.info(f"Проект сохранен: ID={project_id}, User={user_id}")
                    
            except Exception as db_error:
                logger.error(f"Ошибка при сохранении в БД: {db_error}")
                if update.callback_query:
                    await update.callback_query.answer("Ошибка при сохранении в базу данных")
                return
            
            # Очищаем временные данные
            if 'tz_creation' in context.user_data:
                del context.user_data['tz_creation']
            
            title = tz_data.get('title', 'Новый проект')
            estimated_cost = tz_data.get('estimated_cost', 0)
            
            text = f"""
✅ <b>Проект успешно сохранен!</b>

📋 <b>Название:</b> {title}
💰 <b>Стоимость:</b> {format_currency(estimated_cost)}

Проект добавлен в ваш список. Мы свяжемся с вами в ближайшее время для уточнения деталей разработки.

🎯 <b>Что дальше:</b>
• Наш менеджер свяжется с вами для уточнения деталей
• Мы обсудим сроки и процесс разработки
• Вы сможете отслеживать статус проекта в разделе "Мои проекты"

💡 <b>Дополнительно:</b>
• Для настройки хостинга и API токена бота используйте раздел "Настройки" в личном кабинете
• Там вы найдете инструкции по регистрации на Timeweb и созданию бота
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects"),
                    InlineKeyboardButton("🚀 Создать еще ТЗ", callback_data="create_tz")
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
            logger.error(f"Ошибка в _save_tz: {e}")
            try:
                if update.callback_query:
                    await update.callback_query.answer("Ошибка при сохранении")
                    await update.callback_query.edit_message_text(
                        "❌ Произошла ошибка при сохранении проекта. Попробуйте еще раз.",
                        reply_markup=get_main_menu_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        "❌ Произошла ошибка при сохранении проекта.",
                        reply_markup=get_main_menu_keyboard()
                    )
            except Exception as inner_e:
                logger.error(f"Ошибка при обработке ошибки: {inner_e}")
    
    def _format_list(self, items):
        """Форматировать список элементов"""
        if not items:
            return "• Не указано"
        
        if isinstance(items, list):
            formatted_items = []
            for item in items:
                if isinstance(item, dict):
                    # Если это словарь, пытаемся извлечь название
                    if 'function_name' in item:
                        formatted_items.append(f"• {item['function_name']}")
                    elif 'name' in item:
                        formatted_items.append(f"• {item['name']}")
                    elif 'title' in item:
                        formatted_items.append(f"• {item['title']}")
                    else:
                        # Если не можем извлечь название, берем первое значение
                        for key, value in item.items():
                            if isinstance(value, str) and value:
                                formatted_items.append(f"• {value}")
                                break
                elif isinstance(item, str):
                    formatted_items.append(f"• {item}")
                else:
                    formatted_items.append(f"• {str(item)}")
            
            return "\n".join(formatted_items) if formatted_items else "• Не указано"
        elif isinstance(items, str):
            return f"• {items}"
        else:
            return f"• {str(items)}"
    
    def _format_complexity(self, complexity):
        """Форматировать сложность проекта"""
        complexity_map = {
            'simple': '🟢 Простой',
            'medium': '🟡 Средний',
            'complex': '🔴 Сложный',
            'premium': '🟣 Премиум'
        }
        return complexity_map.get(complexity, '🟡 Средний')

    async def handle_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода описания проекта"""
        if not update.message or not update.message.text:
            return
        
        user_id = update.effective_user.id
        description = update.message.text.strip()
        
        # Сохраняем описание
        if 'tz_creation' not in context.user_data:
            context.user_data['tz_creation'] = {}
        
        context.user_data['tz_creation']['description'] = description
        
        # Переходим к подтверждению
        return await self._show_confirmation(update, context)
        
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка подтверждения создания проекта"""
        if not update.callback_query:
            return
            
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_tz":
            # Обрабатываем подтверждение (логика уже существует в других методах)
            return await self.handle_review_action(update, context)
        
        return ConversationHandler.END
        
    async def _show_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ экрана подтверждения"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_tz")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_tz")]
        ])
        
        text = "Подтвердите создание проекта"
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text, reply_markup=keyboard)
            
        return self.CONFIRMATION

# Создаем экземпляр обработчика для использования в других модулях
tz_creation_handler = TZCreationHandler()