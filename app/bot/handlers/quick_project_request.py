# app/bot/handlers/quick_project_request.py
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..keyboards.main import get_main_menu_keyboard
from ...database.database import get_db_context, create_project, get_or_create_user
from ...database.models import User, Project
from ...config.logging import get_logger, log_user_action

logger = get_logger(__name__)

# Состояния для пошагового заполнения
WAITING_PROJECT_NAME = "waiting_project_name"
WAITING_PROJECT_DESCRIPTION = "waiting_project_description"
WAITING_PROJECT_BUDGET = "waiting_project_budget"
WAITING_PROJECT_DEADLINE = "waiting_project_deadline"

class QuickProjectRequestHandler:
    """Обработчик быстрого создания запроса на проект"""

    async def show_quick_request_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню быстрого создания проекта"""
        try:
            logger.info("🔥 show_quick_request_menu ВЫЗВАН!")
            logger.info(f"🔥 update={update}")
            logger.info(f"🔥 callback_query={update.callback_query if update else None}")

            user_id = update.effective_user.id
            logger.info(f"🔥 user_id={user_id}")
            log_user_action(user_id, "show_quick_request_menu")

            text = """
⚡ <b>Быстрое создание проекта</b>

Создайте заявку за 2 минуты!
Ответьте на 4 простых вопроса, и мы свяжемся с вами.

<b>Как это работает:</b>
1️⃣ Выберите тип проекта
2️⃣ Опишите задачу в 2-3 предложениях
3️⃣ Укажите бюджет и сроки
4️⃣ Готово! Мы получим вашу заявку

<b>💡 Что дальше:</b>
• Изучим вашу заявку
• Свяжемся в течение 2 часов
• Обсудим детали и подготовим предложение

<i>Выберите тип проекта:</i>
            """

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🤖 Telegram бот", callback_data="quick_telegram"),
                    InlineKeyboardButton("✨ Telegram Mini App", callback_data="quick_miniapp")
                ],
                [
                    InlineKeyboardButton("💬 WhatsApp бот", callback_data="quick_whatsapp")
                ],
                [
                    InlineKeyboardButton("🤖 Android приложение", callback_data="quick_android"),
                    InlineKeyboardButton("📱 iOS приложение", callback_data="quick_ios")
                ],
                [InlineKeyboardButton("📋 Подробное ТЗ", callback_data="create_tz")],
                [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
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
            logger.error(f"Ошибка в show_quick_request_menu: {e}")
            await self._send_error_message(update, "Ошибка при загрузке меню")

    async def handle_quick_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать быстрый запрос проекта - начало пошагового заполнения"""
        try:
            logger.info("🔥 handle_quick_request ВЫЗВАН!")
            query = update.callback_query
            logger.info(f"🔥 query.data={query.data}")
            user_id = update.effective_user.id
            logger.info(f"🔥 user_id={user_id}")

            project_types = {
                "quick_telegram": {
                    "name": "Telegram бот",
                    "type": "telegram_bot",
                    "emoji": "🤖"
                },
                "quick_miniapp": {
                    "name": "Telegram Mini App",
                    "type": "telegram_miniapp",
                    "emoji": "✨"
                },
                "quick_whatsapp": {
                    "name": "WhatsApp бот",
                    "type": "whatsapp_bot",
                    "emoji": "💬"
                },
                "quick_android": {
                    "name": "Android приложение",
                    "type": "android_app",
                    "emoji": "🤖"
                },
                "quick_ios": {
                    "name": "iOS приложение",
                    "type": "ios_app",
                    "emoji": "📱"
                }
            }

            project_key = query.data
            if project_key not in project_types:
                await query.answer("Неизвестный тип проекта")
                return

            project_info = project_types[project_key]

            log_user_action(user_id, "start_quick_request", project_info['name'])

            # Сохраняем выбранный тип в context
            context.user_data['quick_project_type'] = project_info
            context.user_data['quick_project_state'] = WAITING_PROJECT_NAME

            # Показываем первый вопрос
            await query.answer()

            text = f"""
{project_info['emoji']} <b>{project_info['name']}</b>

<b>Шаг 1 из 4:</b> Название

Как назовем ваш проект?
Придумайте короткое и понятное название.

<i>Примеры:</i>
• "Магазин одежды"
• "Бот для записи на услуги"
• "Мини-игра для Telegram"

Напишите название:
            """

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отменить", callback_data="quick_request")]
            ])

            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_quick_request: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await query.answer("Произошла ошибка при создании запроса")

    async def handle_project_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка названия проекта"""
        try:
            if context.user_data.get('quick_project_state') != WAITING_PROJECT_NAME:
                return

            project_name = update.message.text.strip()

            if len(project_name) < 3:
                await update.message.reply_text(
                    "❌ Название слишком короткое. Минимум 3 символа.\n\nПопробуйте еще раз:"
                )
                return

            # Сохраняем название
            context.user_data['quick_project_name'] = project_name
            context.user_data['quick_project_state'] = WAITING_PROJECT_DESCRIPTION

            project_info = context.user_data.get('quick_project_type', {})

            text = f"""
{project_info.get('emoji', '⚡')} <b>{project_info.get('name', '')}</b>

✅ Название: <i>{project_name}</i>

<b>Шаг 2 из 4:</b> Описание задачи

Опишите что должно делать приложение.
Напишите 2-3 предложения о главных функциях.

<i>Примеры:</i>
• "Бот для продажи товаров с каталогом, корзиной и оплатой"
• "Игра в Telegram с рейтингом игроков и призами"
• "Приложение для доставки еды с картой и трекингом"

Опишите задачу:
            """

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отменить", callback_data="quick_request")]
            ])

            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_project_name: {e}")

    async def handle_project_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка описания проекта"""
        try:
            if context.user_data.get('quick_project_state') != WAITING_PROJECT_DESCRIPTION:
                return

            description = update.message.text.strip()

            if len(description) < 10:
                await update.message.reply_text(
                    "❌ Описание слишком короткое. Минимум 10 символов.\n\nПопробуйте еще раз:"
                )
                return

            # Сохраняем описание
            context.user_data['quick_project_description'] = description
            context.user_data['quick_project_state'] = WAITING_PROJECT_BUDGET

            project_info = context.user_data.get('quick_project_type', {})
            project_name = context.user_data.get('quick_project_name', '')

            text = f"""
{project_info.get('emoji', '⚡')} <b>{project_info.get('name', '')}</b>

✅ Название: <i>{project_name}</i>
✅ Описание: <i>{description[:50]}...</i>

<b>Шаг 3 из 4:</b> Бюджет

Какой бюджет вы планируете?
Выберите примерный диапазон.

Это поможет нам подготовить подходящее предложение.
            """

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("До 50 000 ₽", callback_data="budget_50000"),
                    InlineKeyboardButton("50-100 тыс ₽", callback_data="budget_100000")
                ],
                [
                    InlineKeyboardButton("100-200 тыс ₽", callback_data="budget_200000"),
                    InlineKeyboardButton("200-500 тыс ₽", callback_data="budget_500000")
                ],
                [
                    InlineKeyboardButton("Более 500 тыс ₽", callback_data="budget_500000plus"),
                    InlineKeyboardButton("Не определился", callback_data="budget_unknown")
                ],
                [InlineKeyboardButton("❌ Отменить", callback_data="quick_request")]
            ])

            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_project_description: {e}")

    async def handle_project_budget(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка бюджета проекта"""
        try:
            query = update.callback_query

            if context.user_data.get('quick_project_state') != WAITING_PROJECT_BUDGET:
                # Возможно пользователь написал текстом бюджет
                if update.message and update.message.text:
                    budget_text = update.message.text.strip()
                    context.user_data['quick_project_budget'] = budget_text
                    await self._ask_deadline(update, context)
                return

            await query.answer()

            budget_map = {
                "budget_50000": "До 50 000 ₽",
                "budget_100000": "50 000 - 100 000 ₽",
                "budget_200000": "100 000 - 200 000 ₽",
                "budget_500000": "200 000 - 500 000 ₽",
                "budget_500000plus": "Более 500 000 ₽",
                "budget_unknown": "Не определился"
            }

            budget = budget_map.get(query.data, "Не указан")
            context.user_data['quick_project_budget'] = budget

            await self._ask_deadline(update, context)

        except Exception as e:
            logger.error(f"Ошибка в handle_project_budget: {e}")

    async def _ask_deadline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Спросить о сроках проекта"""
        context.user_data['quick_project_state'] = WAITING_PROJECT_DEADLINE

        project_info = context.user_data.get('quick_project_type', {})
        project_name = context.user_data.get('quick_project_name', '')
        budget = context.user_data.get('quick_project_budget', '')

        text = f"""
{project_info.get('emoji', '⚡')} <b>{project_info.get('name', '')}</b>

✅ Название: <i>{project_name}</i>
✅ Бюджет: <i>{budget}</i>

<b>Шаг 4 из 4:</b> Сроки

Когда нужно завершить проект?
Выберите желаемый срок.
        """

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Как можно быстрее", callback_data="deadline_asap"),
                InlineKeyboardButton("В течение месяца", callback_data="deadline_month")
            ],
            [
                InlineKeyboardButton("1-3 месяца", callback_data="deadline_3months"),
                InlineKeyboardButton("3-6 месяцев", callback_data="deadline_6months")
            ],
            [
                InlineKeyboardButton("Более 6 месяцев", callback_data="deadline_6plus"),
                InlineKeyboardButton("Не критично", callback_data="deadline_flexible")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data="quick_request")]
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

    async def handle_project_deadline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка срока проекта и создание проекта"""
        try:
            query = update.callback_query

            if context.user_data.get('quick_project_state') != WAITING_PROJECT_DEADLINE:
                return

            await query.answer("Создаю проект...")

            deadline_map = {
                "deadline_asap": "Как можно быстрее",
                "deadline_month": "В течение месяца",
                "deadline_3months": "1-3 месяца",
                "deadline_6months": "3-6 месяцев",
                "deadline_6plus": "Более 6 месяцев",
                "deadline_flexible": "Не критично"
            }

            deadline = deadline_map.get(query.data, "Не указан")
            context.user_data['quick_project_deadline'] = deadline

            # Собираем все данные
            user_id = update.effective_user.id
            username = update.effective_user.username or f"user_{user_id}"
            first_name = update.effective_user.first_name or ""
            last_name = update.effective_user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()

            project_info = context.user_data.get('quick_project_type', {})
            project_name = context.user_data.get('quick_project_name', '')
            description = context.user_data.get('quick_project_description', '')
            budget = context.user_data.get('quick_project_budget', '')

            # Создаем проект
            project_id = None
            with get_db_context() as db:
                user = get_or_create_user(db, user_id)

                # Вычисляем planned_end_date на основе выбранного срока
                from datetime import datetime, timedelta
                start_date = datetime.now()

                # Определяем примерную дату окончания на основе выбранного срока
                deadline_days_map = {
                    "Как можно быстрее": 7,
                    "В течение месяца": 30,
                    "1-3 месяца": 60,
                    "3-6 месяцев": 120,
                    "Более 6 месяцев": 180,
                    "Не критично": 90
                }
                days_to_add = deadline_days_map.get(deadline, 30)
                planned_end_date = start_date + timedelta(days=days_to_add)

                # Парсим бюджет в число для estimated_cost
                estimated_cost = 0.0
                if "До 50" in budget:
                    estimated_cost = 50000.0
                elif "50 000 - 100 000" in budget or "50-100" in budget:
                    estimated_cost = 75000.0
                elif "100 000 - 200 000" in budget or "100-200" in budget:
                    estimated_cost = 150000.0
                elif "200 000 - 500 000" in budget or "200-500" in budget:
                    estimated_cost = 350000.0
                elif "Более 500" in budget:
                    estimated_cost = 500000.0
                else:
                    estimated_cost = 0.0

                # Определяем сложность на основе бюджета
                if estimated_cost < 50000:
                    complexity = 'simple'
                elif estimated_cost < 200000:
                    complexity = 'medium'
                elif estimated_cost < 500000:
                    complexity = 'complex'
                else:
                    complexity = 'premium'

                # Формируем полный запрос для original_request
                original_request = f"""Клиент: @{username} ({full_name})
Telegram ID: {user_id}
Тип проекта: {project_info.get('name', '')}
Бюджет: {budget}
Желаемые сроки: {deadline}

Описание:
{description}"""

                project_data = {
                    'title': project_name,
                    'description': description,  # Только описание от клиента
                    'original_request': original_request,  # Полная информация о запросе
                    'project_type': project_info.get('type', 'other'),
                    'status': 'new',
                    'estimated_cost': estimated_cost,
                    'estimated_hours': days_to_add * 8,  # Примерно 8 часов в день
                    'complexity': complexity,
                    'start_date': start_date,
                    'planned_end_date': planned_end_date,
                    'structured_tz': {
                        'quick_request': True,
                        'request_type': project_info.get('name', ''),
                        'created_via': 'quick_request_stepwise',
                        'client_username': username,
                        'client_name': full_name,
                        'client_tg_id': user_id,
                        'budget': budget,
                        'budget_numeric': estimated_cost,
                        'deadline': deadline,
                        'deadline_text': deadline,
                        'raw_description': description
                    }
                }

                project = create_project(db, user.id, project_data)
                db.commit()
                project_id = project.id

            logger.info(f"Создан проект через быстрый запрос: ID={project_id}, User={user_id} (@{username}), Type={project_info.get('name')}")

            # Отправляем уведомление админу
            try:
                from ...services.notification_service import notification_service
                admin_message = f"""
🆕 <b>Новый проект от клиента!</b>

📋 <b>Проект #{project_id}:</b> {project_name}
{project_info.get('emoji', '⚡')} <b>Тип:</b> {project_info.get('name', '')}

👤 <b>Клиент:</b> @{username} ({full_name})
🆔 <b>Telegram ID:</b> <code>{user_id}</code>

💰 <b>Бюджет:</b> {budget}
⏰ <b>Сроки:</b> {deadline}

📝 <b>Описание:</b>
{description}

🔗 <b>Ссылка на проект:</b> /admin (проект #{project_id})
                """
                await notification_service.send_admin_notification(admin_message)
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление админу: {e}")

            # Очищаем состояние
            context.user_data.pop('quick_project_state', None)
            context.user_data.pop('quick_project_type', None)
            context.user_data.pop('quick_project_name', None)
            context.user_data.pop('quick_project_description', None)
            context.user_data.pop('quick_project_budget', None)
            context.user_data.pop('quick_project_deadline', None)

            # Показываем успех
            text = f"""
✅ <b>Проект успешно создан!</b>

📋 <b>Номер проекта:</b> #{project_id}
{project_info.get('emoji', '⚡')} <b>Название:</b> {project_name}
💰 <b>Бюджет:</b> {budget}
⏰ <b>Сроки:</b> {deadline}

<b>📞 Что дальше:</b>
• Наш менеджер изучит вашу заявку
• Свяжемся с вами в ближайшее время (обычно в течение 1-2 часов)
• Подготовим коммерческое предложение
• Ответим на все вопросы

<b>💡 Информация:</b>
• Статус проекта отслеживайте в разделе "���� Мои проекты"
• Вы получите уведомление при изменении статуса
• Консультация и обсуждение — бесплатно
            """

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects"),
                    InlineKeyboardButton("💼 Портфолио", callback_data="portfolio")
                ],
                [
                    InlineKeyboardButton("⚡ Ещё проект", callback_data="quick_request"),
                    InlineKeyboardButton("📝 Подробное ТЗ", callback_data="create_tz")
                ],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])

            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_project_deadline: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await query.answer("Произошла ошибка при создании проекта")

    async def _send_error_message(self, update: Update, message: str):
        """Отправить сообщение об ошибке"""
        keyboard = get_main_menu_keyboard()

        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"❌ {message}",
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                f"❌ {message}",
                reply_markup=keyboard
            )

# Создаем глобальный экземпляр обработчика
quick_project_handler = QuickProjectRequestHandler()
