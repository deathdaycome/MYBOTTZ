import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from ..keyboards.consultant import (
    get_consultant_main_keyboard,
    get_consultant_topics_keyboard,
    get_consultant_session_keyboard,
    get_popular_questions_keyboard,
    get_consultant_rating_keyboard,
    get_consultant_history_keyboard,
    get_session_actions_keyboard,
    get_quick_questions_keyboard,
    get_consultant_feedback_keyboard
)
from ...database.database import get_db_context, create_consultant_session, add_consultant_query
from ...database.models import User, ConsultantSession, ConsultantQuery
from ...services.openai_service import ai_service
from ...config.logging import get_logger, log_consultant_query

logger = get_logger(__name__)

# Состояния разговора
# CONSULTANT_TOPIC, CONSULTANT_QUESTION, CONSULTANT_RATING = range(3)

class ConsultantHandler:
    """Обработчик AI консультанта"""
    
    # Переносим состояния внутрь класса
    CONSULTANT_TOPIC, CONSULTANT_QUESTION, CONSULTANT_RATING = range(3)
    
    def __init__(self):
        self.active_sessions: Dict[int, str] = {}  # user_id -> session_id
        self.session_topics: Dict[str, str] = {}  # session_id -> topic
        self.conversation_history: Dict[str, List[Dict]] = {}  # session_id -> messages
    
    async def show_consultant_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню консультанта"""
        try:
            text = """
🤖 <b>AI Консультант по разработке ботов</b>

Я помогу вам с вопросами по:
• Техническим аспектам разработки
• Выбору технологий и архитектуры
• Ценообразованию и оценке проектов
• Лучшим практикам и рекомендациям
• Решению конкретных задач

Выберите действие:
            """
            
            keyboard = get_consultant_main_keyboard()
            
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
            logger.error(f"Ошибка в show_consultant_main: {e}")
            await self._send_error_message(update, "Произошла ошибка при загрузке консультанта")
    
    async def start_consultation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать консультацию"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            
            text = """
🤖 <b>Начинаем консультацию</b>

Выберите тему для консультации или задайте свой вопрос:
            """
            
            keyboard = get_consultant_topics_keyboard()
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            return self.CONSULTANT_TOPIC
            
        except Exception as e:
            logger.error(f"Ошибка в start_consultation: {e}")
            return ConversationHandler.END

    async def start_new_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать новую сессию консультации"""
        try:
            user_id = update.effective_user.id
            
            # Создаем новую сессию
            session_id = str(uuid.uuid4())
            self.active_sessions[user_id] = session_id
            self.conversation_history[session_id] = []
            
            text = """
🎯 <b>Выберите тему консультации</b>

Это поможет мне лучше понять ваши потребности и дать более точные рекомендации.
            """
            
            keyboard = get_consultant_topics_keyboard()
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            return ConsultantHandler.CONSULTANT_TOPIC
            
        except Exception as e:
            logger.error(f"Ошибка в start_new_session: {e}")
            await self._send_error_message(update, "Не удалось создать новую сессию")
    
    async def select_topic(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор темы консультации"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            topic_data = query.data.replace('topic_', '')
            
            # Получаем активную сессию
            session_id = self.active_sessions.get(user_id)
            if not session_id:
                await self.start_new_session(update, context)
                return ConsultantHandler.CONSULTANT_TOPIC
            
            # Сохраняем тему
            topic_names = {
                'telegram_bots': 'Telegram боты',
                'whatsapp_bots': 'WhatsApp боты',
                'web_bots': 'Веб-боты и чат-боты',
                'integrations': 'Интеграции с внешними сервисами',
                'architecture': 'Архитектура и проектирование',
                'databases': 'Базы данных',
                'deployment': 'Деплой и хостинг',
                'security': 'Безопасность',
                'pricing': 'Ценообразование',
                'marketing': 'Маркетинг и продвижение',
                'other': 'Другие вопросы'
            }
            
            topic_name = topic_names.get(topic_data, 'Общие вопросы')
            self.session_topics[session_id] = topic_name
            
            # Сохраняем сессию в базу данных
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                create_consultant_session(db, user.id, session_id, topic_name)
            
            text = f"""
✅ <b>Тема выбрана: {topic_name}</b>

Теперь вы можете задать свой вопрос или выбрать один из популярных вопросов по этой теме.

Просто напишите ваш вопрос, и я дам подробный ответ с рекомендациями!
            """
            
            keyboard = get_consultant_session_keyboard(session_id)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            return ConsultantHandler.CONSULTANT_QUESTION
            
        except Exception as e:
            logger.error(f"Ошибка в select_topic: {e}")
            await self._send_error_message(update, "Ошибка при выборе темы")
    
    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка вопроса пользователя"""
        try:
            user_id = update.effective_user.id
            session_id = self.active_sessions.get(user_id)
            
            if not session_id:
                await update.message.reply_text(
                    "Сессия консультации не найдена. Начните новую сессию.",
                    reply_markup=get_consultant_main_keyboard()
                )
                return ConversationHandler.END
            
            user_question = update.message.text
            
            # Показываем индикатор печати
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            
            # Получаем историю разговора
            conversation_history = self.conversation_history.get(session_id, [])
            
            # Получаем ответ от AI
            ai_response_data = await ai_service.consultant_response(
                user_question, 
                conversation_history
            )
            
            ai_response = ai_response_data['response']
            tokens_used = ai_response_data['tokens_used']
            response_time = ai_response_data['response_time']
            
            # Сохраняем в историю разговора
            conversation_history.extend([
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": ai_response}
            ])
            self.conversation_history[session_id] = conversation_history
            
            # Сохраняем в базу данных
            with get_db_context() as db:
                # Находим сессию
                session = db.query(ConsultantSession).filter(
                    ConsultantSession.session_id == session_id
                ).first()
                
                if session:
                    query_record = add_consultant_query(
                        db, session.id, user_question, ai_response, tokens_used, response_time
                    )
                    
                    # Логируем
                    log_consultant_query(user_id, user_question, len(ai_response))
            
            # Отправляем ответ
            await update.message.reply_text(
                f"🤖 <b>Ответ консультанта:</b>\n\n{ai_response}",
                parse_mode='HTML',
                reply_markup=get_consultant_session_keyboard(session_id)
            )
            
            # Предлагаем оценить ответ
            rating_text = "Оцените качество ответа:"
            rating_keyboard = get_consultant_rating_keyboard(session_id, query_record.id if 'query_record' in locals() else 0)
            
            await update.message.reply_text(
                rating_text,
                reply_markup=rating_keyboard
            )
            
            return ConsultantHandler.CONSULTANT_QUESTION
            
        except Exception as e:
            logger.error(f"Ошибка в handle_question: {e}")
            await self._send_error_message(update, "Не удалось получить ответ консультанта")
    
    async def show_popular_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать популярные вопросы"""
        try:
            text = """
📚 <b>Популярные вопросы</b>

Выберите интересующий вас вопрос или вернитесь к консультанту для персонального ответа:
            """
            
            keyboard = get_popular_questions_keyboard()
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_popular_questions: {e}")
    
    async def handle_popular_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка популярного вопроса"""
        try:
            query = update.callback_query
            question_id = query.data.replace('q_', '')
            
            # Предопределенные ответы на популярные вопросы
            answers = {
                'how_to_start': """
🚀 <b>Как начать разрабатывать ботов?</b>

<b>1. Изучите основы:</b>
• Python (основной язык для ботов)
• HTTP/API понятия
• Telegram Bot API

<b>2. Выберите библиотеку:</b>
• python-telegram-bot (рекомендую)
• aiogram (асинхронная)
• telebot (простая)

<b>3. Создайте первого бота:</b>
• Зарегистрируйте бота через @BotFather
• Напишите простой эхо-бот
• Добавьте клавиатуры и команды

<b>4. Изучите дополнительно:</b>
• Базы данных (SQLite, PostgreSQL)
• Деплой (VPS, Heroku, Railway)
• Мониторинг и логирование

<b>Ресурсы для изучения:</b>
• Документация python-telegram-bot
• YouTube каналы по Python
• GitHub примеры ботов
                """,
                
                'bot_cost': """
💰 <b>Сколько стоит разработка бота?</b>

<b>Простой бот (10,000-25,000₽):</b>
• Базовые команды и меню
• Простая логика
• Без интеграций
• 3-7 дней разработки

<b>Средний бот (25,000-50,000₽):</b>
• База данных
• Админ-панель
• 1-2 интеграции
• 1-2 недели разработки

<b>Сложный бот (50,000-100,000₽):</b>
• Сложная логика
• Множество интеграций
• Платежи
• 2-4 недели разработки

<b>Премиум бот (100,000₽+):</b>
• Уникальная архитектура
• AI интеграции
• Высокие нагрузки
• 1+ месяц разработки

<b>Факторы стоимости:</b>
• Сложность логики
• Количество интеграций
• Требования к дизайну
• Сроки выполнения
                """,
                
                'development_time': """
⏱ <b>Сколько времени нужно на разработку?</b>

<b>Простой бот: 3-7 дней</b>
• Базовый функционал
• Стандартные решения
• Минимум тестирования

<b>Средний бот: 1-2 недели</b>
• Кастомная логика
• Интеграции с API
• Тестирование

<b>Сложный бот: 2-4 недели</b>
• Сложная архитектура
• Множественные интеграции
• Полное тестирование

<b>Премиум бот: 1+ месяц</b>
• Уникальные решения
• Высокая производительность
• Подробное тестирование

<b>Что влияет на сроки:</b>
• Четкость требований
• Сложность интеграций
• Количество правок
• Загруженность команды
• Тестирование и отладка
                """,
                
                'technologies': """
🔧 <b>Какие технологии использовать?</b>

<b>Язык программирования:</b>
• Python (рекомендую) - простота и библиотеки
• Node.js - для веб-разработчиков
• Go - для высоких нагрузок
• PHP - для простых проектов

<b>Библиотеки для ботов:</b>
• python-telegram-bot - стабильная
• aiogram - современная асинхронная
• grammy (TS/JS) - для Node.js
• telebot (Python) - простая

<b>Базы данных:</b>
• SQLite - для простых проектов
• PostgreSQL - для серьезных проектов
• Redis - для кэширования
• MongoDB - для гибких схем

<b>Деплой и хостинг:</b>
• VPS (Ubuntu) - полный контроль
• Heroku - простота деплоя
• Railway - современная альтернатива
• Docker - контейнеризация

<b>Дополнительные инструменты:</b>
• nginx - веб-сервер
• systemd - управление процессами
• Prometheus - мониторинг
• Sentry - отслеживание ошибок
                """
            }
            
            answer = answers.get(question_id, "Ответ на этот вопрос в разработке...")
            
            await query.edit_message_text(
                answer,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 Задать свой вопрос", callback_data="consultant_new_session")],
                    [InlineKeyboardButton("📚 Другие вопросы", callback_data="consultant_popular_questions")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_popular_question: {e}")
    
    async def show_consultant_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать историю консультаций"""
        try:
            user_id = update.effective_user.id
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                sessions = db.query(ConsultantSession).filter(
                    ConsultantSession.user_id == user.id
                ).order_by(ConsultantSession.created_at.desc()).all()
            
            if not sessions:
                text = """
📊 <b>История консультаций</b>

У вас пока нет истории консультаций.
Начните новую сессию для получения персональных рекомендаций!
                """
                keyboard = get_consultant_main_keyboard()
            else:
                text = f"""
📊 <b>История консультаций</b>

Всего сессий: {len(sessions)}
Выберите сессию для просмотра:
                """
                sessions_data = [session.to_dict() for session in sessions]
                keyboard = get_consultant_history_keyboard(sessions_data)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_consultant_history: {e}")
    
    async def rate_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Оценка ответа консультанта"""
        try:
            query = update.callback_query
            rating_data = query.data.split('_')
            rating = int(rating_data[1])
            session_id = rating_data[2]
            query_id = int(rating_data[3]) if len(rating_data) > 3 else 0
            
            # Сохраняем оценку в базу данных
            with get_db_context() as db:
                if query_id:
                    query_record = db.query(ConsultantQuery).filter(
                        ConsultantQuery.id == query_id
                    ).first()
                    
                    if query_record:
                        query_record.rating = rating
                        db.commit()
            
            rating_stars = "⭐" * rating
            await query.answer(f"Спасибо за оценку! {rating_stars}")
            
            # Предлагаем продолжить сессию
            keyboard = get_consultant_session_keyboard(session_id)
            await query.edit_message_reply_markup(reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка в rate_response: {e}")
    
    async def end_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершение сессии консультации"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            session_id = query.data.replace('consultant_end_', '')
            
            # Завершаем сессию в базе данных
            with get_db_context() as db:
                session = db.query(ConsultantSession).filter(
                    ConsultantSession.session_id == session_id
                ).first()
                
                if session:
                    session.status = "completed"
                    db.commit()
            
            # Очищаем активную сессию
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
            
            if session_id in self.conversation_history:
                del self.conversation_history[session_id]
            
            text = """
✅ <b>Сессия завершена</b>

Спасибо за использование AI консультанта!
Надеюсь, смог помочь с вашими вопросами.

Вы можете начать новую сессию в любое время.
            """
            
            keyboard = get_consultant_main_keyboard()
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Ошибка в end_session: {e}")
    
    async def continue_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Продолжение существующей сессии"""
        try:
            user_id = update.effective_user.id
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                # Ищем активную сессию
                active_session = db.query(ConsultantSession).filter(
                    ConsultantSession.user_id == user.id,
                    ConsultantSession.status == "active"
                ).order_by(ConsultantSession.created_at.desc()).first()
            
            if not active_session:
                text = """
❌ <b>Активная сессия не найдена</b>

У вас нет активных сессий консультации.
Начните новую сессию для получения помощи.
                """
                keyboard = get_consultant_main_keyboard()
            else:
                # Восстанавливаем сессию
                session_id = active_session.session_id
                self.active_sessions[user_id] = session_id
                
                # Загружаем историю разговора
                with get_db_context() as db:
                    queries = db.query(ConsultantQuery).filter(
                        ConsultantQuery.session_id == active_session.id
                    ).order_by(ConsultantQuery.created_at.asc()).all()
                    
                    conversation_history = []
                    for q in queries:
                        conversation_history.extend([
                            {"role": "user", "content": q.user_query},
                            {"role": "assistant", "content": q.ai_response}
                        ])
                    
                    self.conversation_history[session_id] = conversation_history
                
                text = f"""
🔄 <b>Сессия восстановлена</b>

Тема: {active_session.topic}
Вопросов задано: {len(queries)}

Можете продолжать задавать вопросы!
                """
                keyboard = get_consultant_session_keyboard(session_id)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            if active_session:
                return ConsultantHandler.CONSULTANT_QUESTION
            
        except Exception as e:
            logger.error(f"Ошибка в continue_session: {e}")
    
    async def _send_error_message(self, update: Update, message: str):
        """Отправка сообщения об ошибке"""
        try:
            error_text = f"❌ {message}\n\nПопробуйте еще раз или обратитесь в поддержку."
            keyboard = get_consultant_main_keyboard()
            
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

# Создаем глобальный экземпляр обработчика
consultant_handler = ConsultantHandler()