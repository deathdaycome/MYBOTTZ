from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..keyboards.main import get_project_actions_keyboard, get_pagination_keyboard
from ...database.database import get_db_context
from ...database.models import User, Project
from ...config.logging import get_logger, log_user_action
from ...utils.decorators import standard_handler
from ...utils.helpers import format_datetime, format_currency, time_ago

logger = get_logger(__name__)

class ProjectsHandler:
    """Обработчик управления проектами"""
    
    def __init__(self):
        self.projects_per_page = 5
    
    @standard_handler
    async def show_user_projects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать проекты пользователя"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "show_user_projects")
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                projects = db.query(Project).filter(
                    Project.user_id == user.id
                ).order_by(Project.created_at.desc()).all()
            
            if not projects:
                await self._show_no_projects(update)
                return
            
            # Статистика по проектам
            stats = self._calculate_project_stats(projects)
            
            text = f"""
📊 <b>Мои проекты</b>

📈 <b>Статистика:</b>
• Всего проектов: {stats['total']}
• В работе: {stats['in_progress']}
• Завершено: {stats['completed']}
• Общая стоимость: {format_currency(stats['total_cost'])}

<b>Ваши проекты:</b>
            """
            
            # Показываем первые 5 проектов
            for i, project in enumerate(projects[:5], 1):
                status_emoji = self._get_status_emoji(project.status)
                created_date = time_ago(project.created_at) if project.created_at else "неизвестно"
                
                text += f"\n<b>{i}. {project.title}</b>\n"
                text += f"{status_emoji} {self._get_status_name(project.status)}\n"
                text += f"💰 {format_currency(project.estimated_cost)}\n"
                text += f"📅 Создан: {created_date}\n"
            
            keyboard = self._create_projects_keyboard(projects)
            
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
            logger.error(f"Ошибка в show_user_projects: {e}")
    
    @standard_handler
    async def show_project_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детали проекта"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('project_details_', ''))
            
            log_user_action(user_id, "show_project_details", str(project_id))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                # Загружаем проект с пользователем
                project = db.query(Project).filter(
                    Project.id == project_id,
                    Project.user_id == user.id
                ).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                # Убеждаемся, что объект user загружен в проект
                project.user = user
            
            # Формируем детальную информацию
            text = f"""
📋 <b>Проект #{project.id}</b>

<b>📝 Название:</b> {project.title}

<b>📄 Описание:</b>
{project.description[:300]}{'...' if len(project.description) > 300 else ''}

<b>📊 Информация:</b>
• Статус: {self._get_status_emoji(project.status)} {self._get_status_name(project.status)}
• Сложность: {project.complexity}
• Тип: {self._get_type_name(project.project_type)}

<b>💰 Финансы:</b>
• Оценочная стоимость: {format_currency(project.estimated_cost)}
{('• Финальная стоимость: ' + format_currency(project.final_cost)) if project.final_cost else ''}

<b>⏱ Время:</b>
• Оценочное время: {project.estimated_hours} часов
{'• Фактическое время: ' + str(project.actual_hours) + ' часов' if project.actual_hours else ''}

<b>📅 Даты:</b>
• Создан: {format_datetime(project.created_at) if project.created_at else 'неизвестно'}
• Обновлен: {format_datetime(project.updated_at) if project.updated_at else 'неизвестно'}
{'• Дедлайн: ' + format_datetime(project.deadline) if project.deadline else ''}

{self._get_project_credentials_info(project)}
            """
            
            keyboard = get_project_actions_keyboard(project.id)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_project_details: {e}")
            await query.answer("Произошла ошибка при загрузке проекта")
    
    @standard_handler
    async def show_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать портфолио проектов"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "show_portfolio")
            
            text = """
💼 <b>Портфолио проектов</b>

🚀 <b>Наши решения:</b>

<b>🤖 Telegram-боты:</b>
• Интернет-магазин с каталогом и корзиной
• CRM для управления клиентами
• Бот-помощник для техподдержки
• Автоматизация записи на услуги
• Система уведомлений и рассылок

<b>💬 WhatsApp-боты:</b>
• Прием заказов в ресторане
• Консультант по недвижимости
• Бот для автосалона
• Система записи к врачу

<b>🌐 Веб-чатботы:</b>
• Помощник на сайте интернет-магазина
• Консультант по подбору товаров
• Система сбора заявок
• FAQ-бот для техподдержки

<b>🔗 Интеграции:</b>
• CRM (amoCRM, Битрикс24)
• Платежные системы
• Внешние API
• Системы аналитики

Хотите увидеть демо или узнать больше о конкретном проекте?
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🤖 Telegram боты", callback_data="portfolio_telegram"),
                    InlineKeyboardButton("💬 WhatsApp боты", callback_data="portfolio_whatsapp")
                ],
                [
                    InlineKeyboardButton("🌐 Веб-боты", callback_data="portfolio_web"),
                    InlineKeyboardButton("🔗 Интеграции", callback_data="portfolio_integrations")
                ],
                [
                    InlineKeyboardButton("🚀 Создать ТЗ", callback_data="create_tz"),
                    InlineKeyboardButton("💬 Консультация", callback_data="consultation")
                ],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
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
            logger.error(f"Ошибка в show_portfolio: {e}")

    def _calculate_project_stats(self, projects: List[Project]) -> Dict[str, Any]:
        """Расчет статистики проектов"""
        stats = {
            'total': len(projects),
            'in_progress': 0,
            'completed': 0,
            'total_cost': 0
        }
        
        for project in projects:
            if project.status in ['in_progress', 'testing']:
                stats['in_progress'] += 1
            elif project.status == 'completed':
                stats['completed'] += 1
            
            stats['total_cost'] += project.final_cost or project.estimated_cost or 0
        
        return stats
    
    def _get_status_emoji(self, status: str) -> str:
        """Получить эмодзи для статуса"""
        emojis = {
            'new': '🆕',
            'review': '👀',
            'accepted': '✅',
            'in_progress': '🔄',
            'testing': '🧪',
            'completed': '🎉',
            'cancelled': '❌'
        }
        return emojis.get(status, '📊')
    
    def _get_status_name(self, status: str) -> str:
        """Получить название статуса"""
        names = {
            'new': 'Новый',
            'review': 'На рассмотрении',
            'accepted': 'Принят',
            'in_progress': 'В работе',
            'testing': 'Тестирование',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        return names.get(status, status)
    
    def _get_type_name(self, project_type: str) -> str:
        """Получить название типа проекта"""
        names = {
            'telegram_bot': 'Telegram бот',
            'whatsapp_bot': 'WhatsApp бот',
            'web_bot': 'Веб-бот',
            'integration': 'Интеграция'
        }
        return names.get(project_type, project_type or 'Не указано')
    
    def _create_projects_keyboard(self, projects: List[Project]) -> InlineKeyboardMarkup:
        """Создание клавиатуры для списка проектов"""
        keyboard = []
        
        # Показываем первые 5 проектов
        for project in projects[:5]:
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 {project.title[:25]}{'...' if len(project.title) > 25 else ''}",
                    callback_data=f"project_details_{project.id}"
                )
            ])
        
        # Если проектов больше 5, добавляем кнопку "Показать все"
        if len(projects) > 5:
            keyboard.append([
                InlineKeyboardButton("📊 Показать все проекты", callback_data="all_projects")
            ])
        
        # Дополнительные действия
        keyboard.append([
            InlineKeyboardButton("📝 Создать новый проект", callback_data="create_tz"),
            InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def _show_no_projects(self, update: Update):
        """Показать сообщение об отсутствии проектов"""
        text = """
📭 <b>У вас пока нет проектов</b>

Начните свой первый проект прямо сейчас!

<b>🚀 Что вы можете сделать:</b>
• Создать техническое задание
• Проконсультироваться с AI
• Посмотреть примеры в портфолио
• Связаться с нами напрямую

<b>💡 Почему стоит начать:</b>
• Бесплатная консультация
• Прозрачное ценообразование  
• Качественная разработка
• Поддержка после запуска
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Создать ТЗ", callback_data="create_tz")],
            [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
            [InlineKeyboardButton("💼 Портфолио", callback_data="portfolio")],
            [InlineKeyboardButton("💬 Консультация", callback_data="consultation")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
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

    def _get_project_credentials_info(self, project: Project) -> str:
        """Получить информацию о реквизитах проекта (Timeweb, Bot Token)"""
        credentials_info = []
        
        # Получаем данные из preferences пользователя
        if project.user and project.user.preferences:
            user_preferences = project.user.preferences
            
            # Информация о Timeweb
            timeweb_creds = user_preferences.get('timeweb_credentials')
            if timeweb_creds:
                credentials_info.append(f"""
<b>🌐 Timeweb хостинг:</b>
• Логин: <code>{timeweb_creds.get('login', 'не указан')}</code>
• Пароль: <code>{timeweb_creds.get('password', 'не указан')}</code>
• Добавлен: {timeweb_creds.get('created_at', 'неизвестно')}""")
            
            # Информация о Bot Token
            bot_token = user_preferences.get('bot_token')
            if bot_token:
                # Скрываем большую часть токена для безопасности
                masked_token = bot_token[:10] + "..." + bot_token[-10:] if len(bot_token) > 20 else bot_token
                token_added = user_preferences.get('bot_token_added_at', 'неизвестно')
                
                credentials_info.append(f"""
<b>🤖 Bot API Token:</b>
• Токен: <code>{masked_token}</code>
• Добавлен: {token_added}""")
        
        # Также проверяем project_metadata (для обратной совместимости)
        if project.project_metadata:
            # Информация о Timeweb из project_metadata
            timeweb_creds = project.project_metadata.get('timeweb_credentials')
            if timeweb_creds and not any('🌐 Timeweb хостинг:' in info for info in credentials_info):
                credentials_info.append(f"""
<b>🌐 Timeweb хостинг (проект):</b>
• Логин: <code>{timeweb_creds.get('login', 'не указан')}</code>
• Пароль: <code>{timeweb_creds.get('password', 'не указан')}</code>""")
            
            # Информация о Bot Token из project_metadata
            bot_token = project.project_metadata.get('bot_token')
            if bot_token and not any('🤖 Bot API Token:' in info for info in credentials_info):
                # Скрываем большую часть токена для безопасности
                masked_token = bot_token[:10] + "..." + bot_token[-10:] if len(bot_token) > 20 else bot_token
                token_added = project.project_metadata.get('bot_token_added_at', 'неизвестно')
                
                credentials_info.append(f"""
<b>🤖 Bot API Token (проект):</b>
• Токен: <code>{masked_token}</code>
• Добавлен: {token_added}""")
        
        return '\n'.join(credentials_info) if credentials_info else ""

# Создаем глобальный экземпляр обработчика
projects_handler = ProjectsHandler()