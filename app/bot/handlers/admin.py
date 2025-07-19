from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any

from ...config.settings import settings
from ...config.logging import get_logger, log_user_action
from ...database.database import get_db_context
from ...database.models import User, Project, ConsultantSession
from ...services.analytics_service import analytics_service
from ...services.notification_service import notification_service
from ...utils.decorators import admin_only, standard_handler
from ...utils.helpers import format_currency, format_datetime


logger = get_logger(__name__)

class AdminHandler:
    """Обработчик админских команд"""
    
    def __init__(self):
        self.admin_ids = getattr(settings, 'ADMIN_IDS', [])
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка прав администратора"""
        return user_id in self.admin_ids or str(user_id) == settings.NOTIFICATION_CHAT_ID
    
    @standard_handler
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать админское меню"""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ У вас нет прав администратора")
                return
            
            log_user_action(user_id, "admin_menu")
            
            # Получаем краткую статистику
            with get_db_context() as db:
                total_users = db.query(User).count()
                total_projects = db.query(Project).count()
                active_projects = db.query(Project).filter(
                    Project.status.in_(['new', 'review', 'accepted', 'in_progress', 'testing'])
                ).count()
                total_sessions = db.query(ConsultantSession).count()
            
            text = f"""
👨‍💼 <b>Панель администратора</b>

📊 <b>Быстрая статистика:</b>
• Пользователей: {total_users}
• Проектов: {total_projects}
• Активных проектов: {active_projects}
• Консультаций: {total_sessions}

Выберите действие:
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Подробная статистика", callback_data="admin_stats"),
                    InlineKeyboardButton("📋 Управление проектами", callback_data="admin_projects")
                ],
                [
                    InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
                    InlineKeyboardButton("🤖 Консультации", callback_data="admin_consultations")
                ],
                [
                    InlineKeyboardButton("📤 Рассылка", callback_data="admin_broadcast"),
                    InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")
                ],
                [
                    InlineKeyboardButton("📈 Отчеты", callback_data="admin_reports"),
                    InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_refresh")
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
            logger.error(f"Ошибка в admin_menu: {e}")
    
    @standard_handler
    async def show_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать подробную статистику"""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.callback_query.answer("❌ Нет прав доступа")
                return
            
            # Получаем статистику за неделю
            stats = analytics_service.get_dashboard_data(7)
            
            user_stats = stats.get('user_stats', {})
            project_stats = stats.get('project_stats', {})
            consultant_stats = stats.get('consultant_stats', {})
            financial_stats = stats.get('financial_stats', {})
            
            text = f"""
📊 <b>Подробная статистика (7 дней)</b>

👥 <b>Пользователи:</b>
• Всего: {user_stats.get('total_users', 0)}
• Новых: {user_stats.get('new_users', 0)}
• Активных: {user_stats.get('active_users', 0)}
• Конверсия: {user_stats.get('conversion_rate', 0):.1f}%

📋 <b>Проекты:</b>
• Всего: {project_stats.get('total_projects', 0)}
• Новых: {project_stats.get('new_projects', 0)}
• Завершено: {project_stats.get('completed_projects', 0)}
• Процент завершения: {project_stats.get('completion_rate', 0):.1f}%

🤖 <b>Консультации:</b>
• Сессий: {consultant_stats.get('total_sessions', 0)}
• Новых сессий: {consultant_stats.get('new_sessions', 0)}
• Запросов: {consultant_stats.get('total_queries', 0)}
• Средняя оценка: {consultant_stats.get('avg_rating', 0):.1f}/5

💰 <b>Финансы:</b>
• Доход: {format_currency(financial_stats.get('total_revenue', 0))}
• Потенциальный доход: {format_currency(financial_stats.get('potential_revenue', 0))}
• Средний чек: {format_currency(financial_stats.get('avg_check', 0))}
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📈 Месячный отчет", callback_data="admin_monthly_report"),
                    InlineKeyboardButton("📊 Воронка", callback_data="admin_funnel")
                ],
                [
                    InlineKeyboardButton("🔄 Обновить", callback_data="admin_stats"),
                    InlineKeyboardButton("👨‍💼 Админ меню", callback_data="admin_menu")
                ]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_admin_stats: {e}")
    
    @standard_handler
    async def show_recent_projects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать последние проекты"""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.callback_query.answer("❌ Нет прав доступа")
                return
            
            with get_db_context() as db:
                recent_projects = db.query(Project).order_by(
                    Project.created_at.desc()
                ).limit(10).all()
            
            if not recent_projects:
                text = "📭 Нет проектов"
            else:
                text = "📋 <b>Последние проекты:</b>\n\n"
                
                for i, project in enumerate(recent_projects, 1):
                    status_emoji = self._get_status_emoji(project.status)
                    created_date = format_datetime(project.created_at, 'short') if project.created_at else 'неизвестно'
                    
                    text += f"<b>{i}. {project.title[:30]}{'...' if len(project.title) > 30 else ''}</b>\n"
                    text += f"{status_emoji} {project.status} | {format_currency(project.estimated_cost)} | {created_date}\n\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Обновить", callback_data="admin_projects")],
                [InlineKeyboardButton("👨‍💼 Админ меню", callback_data="admin_menu")]
            ])
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_recent_projects: {e}")
    
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
    
    @standard_handler
    async def send_daily_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправить ежедневный отчет"""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ У вас нет прав администратора")
                return
            
            success = await notification_service.send_daily_report()
            
            if success:
                await update.message.reply_text("✅ Ежедневный отчет отправлен")
            else:
                await update.message.reply_text("❌ Ошибка при отправке отчета")
                
        except Exception as e:
            logger.error(f"Ошибка в send_daily_report: {e}")
    
    @standard_handler
    async def clear_analytics_cache(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить кэш аналитики"""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ У вас нет прав администратора")
                return
            
            analytics_service.clear_cache()
            await update.message.reply_text("✅ Кэш аналитики очищен")
            
        except Exception as e:
            logger.error(f"Ошибка в clear_analytics_cache: {e}")

# Создаем глобальный экземпляр обработчика
admin_handler = AdminHandler()

# Команды для регистрации
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin"""
    await admin_handler.admin_menu(update, context)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats"""
    await admin_handler.show_admin_stats(update, context)

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /report"""
    await admin_handler.send_daily_report(update, context)