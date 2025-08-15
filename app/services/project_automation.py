# app/services/project_automation.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any

from ..database.models import Project, User, AdminUser, Transaction
from ..config.logging import get_logger
from ..config.settings import settings
import asyncio
from telegram import Bot
from telegram.error import TelegramError

logger = get_logger(__name__)


class ProjectAutomationService:
    """Сервис автоматизации проектов"""
    
    def __init__(self, db: Session):
        self.db = db
        self.bot_token = settings.BOT_TOKEN if hasattr(settings, 'BOT_TOKEN') else None
        self.admin_chat_id = settings.ADMIN_CHAT_ID if hasattr(settings, 'ADMIN_CHAT_ID') else None
    
    def check_overdue_projects(self) -> List[Project]:
        """Проверить и обновить просроченные проекты"""
        try:
            # Находим проекты, которые должны быть помечены как просроченные
            now = datetime.utcnow()
            overdue_projects = self.db.query(Project).filter(
                and_(
                    Project.status.in_(['new', 'in_progress', 'testing']),
                    Project.planned_end_date < now,
                    Project.status != 'overdue'
                )
            ).all()
            
            updated_projects = []
            for project in overdue_projects:
                # Обновляем статус на "просрочен"
                old_status = project.status
                project.status = 'overdue'
                project.updated_at = now
                
                # Логируем изменение
                logger.warning(f"Проект #{project.id} '{project.title}' помечен как просроченный. "
                             f"Плановая дата: {project.planned_end_date}, Текущая дата: {now}")
                
                updated_projects.append({
                    'project': project,
                    'old_status': old_status,
                    'message': f"Проект просрочен на {(now - project.planned_end_date).days} дней"
                })
            
            if updated_projects:
                self.db.commit()
                logger.info(f"Обновлено {len(updated_projects)} просроченных проектов")
            
            return updated_projects
            
        except Exception as e:
            logger.error(f"Ошибка при проверке просроченных проектов: {str(e)}")
            self.db.rollback()
            return []
    
    def auto_update_project_status(self, project_id: int) -> bool:
        """Автоматически обновить статус проекта на основе текущего состояния"""
        try:
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            # Правила автоматического обновления статусов
            # 1. Если назначен исполнитель и статус "new" -> "in_progress"
            if project.assigned_executor_id and project.status == 'new':
                project.status = 'in_progress'
                project.updated_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"Проект #{project.id} переведен в статус 'В работе' (назначен исполнитель)")
                return True
            
            # 2. Если все задачи выполнены -> "completed"
            # (здесь нужна проверка задач, если у вас есть система задач)
            
            # 3. Если прошла плановая дата завершения -> "overdue"
            if project.planned_end_date and project.planned_end_date < datetime.utcnow():
                if project.status not in ['completed', 'cancelled', 'overdue']:
                    project.status = 'overdue'
                    project.updated_at = datetime.utcnow()
                    self.db.commit()
                    logger.warning(f"Проект #{project.id} помечен как просроченный")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при автоматическом обновлении статуса проекта {project_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def check_unpaid_projects(self) -> List[Dict[str, Any]]:
        """Проверить проекты с неоплаченными остатками после завершения"""
        try:
            # Находим завершенные проекты с остатками к оплате
            completed_projects = self.db.query(Project).filter(
                Project.status == 'completed'
            ).all()
            
            unpaid_projects = []
            for project in completed_projects:
                # Считаем полученные платежи
                total_income = self.db.query(Transaction).filter(
                    and_(
                        Transaction.project_id == project.id,
                        Transaction.transaction_type == 'income',
                        Transaction.status == 'completed'
                    )
                ).with_entities(
                    self.db.query(Transaction).filter(
                        and_(
                            Transaction.project_id == project.id,
                            Transaction.transaction_type == 'income',
                            Transaction.status == 'completed'
                        )
                    ).with_entities(Transaction.amount).subquery()
                ).scalar() or 0
                
                remaining = (project.estimated_cost or 0) - total_income
                
                if remaining > 0:
                    # Проверяем, прошло ли больше 7 дней с момента завершения
                    if project.actual_end_date:
                        days_passed = (datetime.utcnow() - project.actual_end_date).days
                    else:
                        days_passed = (datetime.utcnow() - project.updated_at).days
                    
                    unpaid_projects.append({
                        'project': project,
                        'remaining': remaining,
                        'days_passed': days_passed,
                        'total_cost': project.estimated_cost,
                        'paid': total_income
                    })
            
            return unpaid_projects
            
        except Exception as e:
            logger.error(f"Ошибка при проверке неоплаченных проектов: {str(e)}")
            return []
    
    def check_unpaid_executors(self) -> List[Dict[str, Any]]:
        """Проверить невыплаченные остатки исполнителям"""
        try:
            # Находим проекты с исполнителями
            projects_with_executors = self.db.query(Project).filter(
                Project.assigned_executor_id.isnot(None)
            ).all()
            
            unpaid_executors = []
            for project in projects_with_executors:
                if project.executor_cost:
                    # Считаем выплаты исполнителю
                    total_paid = self.db.query(Transaction).filter(
                        and_(
                            Transaction.project_id == project.id,
                            Transaction.contractor_id == project.assigned_executor_id,
                            Transaction.transaction_type == 'expense',
                            Transaction.status == 'completed'
                        )
                    ).with_entities(
                        self.db.query(Transaction).filter(
                            and_(
                                Transaction.project_id == project.id,
                                Transaction.contractor_id == project.assigned_executor_id,
                                Transaction.transaction_type == 'expense',
                                Transaction.status == 'completed'
                            )
                        ).with_entities(Transaction.amount).subquery()
                    ).scalar() or 0
                    
                    remaining = (project.executor_cost or 0) - total_paid
                    
                    if remaining > 0 and project.status in ['completed', 'testing']:
                        # Проверяем, прошло ли больше 7 дней
                        days_passed = (datetime.utcnow() - project.updated_at).days
                        
                        if days_passed > 7:
                            unpaid_executors.append({
                                'project': project,
                                'executor_id': project.assigned_executor_id,
                                'executor': project.assigned_executor,
                                'remaining': remaining,
                                'days_passed': days_passed,
                                'total_cost': project.executor_cost,
                                'paid': total_paid
                            })
            
            return unpaid_executors
            
        except Exception as e:
            logger.error(f"Ошибка при проверке невыплаченных остатков исполнителям: {str(e)}")
            return []
    
    async def send_notification(self, message: str, chat_id: str = None):
        """Отправить уведомление в Telegram"""
        if not self.bot_token:
            logger.warning("Токен бота не настроен, уведомление не отправлено")
            return False
        
        if not chat_id:
            chat_id = self.admin_chat_id
        
        if not chat_id:
            logger.warning("Chat ID не настроен, уведомление не отправлено")
            return False
        
        try:
            bot = Bot(token=self.bot_token)
            await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
            return True
        except TelegramError as e:
            logger.error(f"Ошибка отправки уведомления в Telegram: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке уведомления: {str(e)}")
            return False
    
    async def run_daily_checks(self):
        """Запустить ежедневные проверки и отправить уведомления"""
        try:
            logger.info("Запуск ежедневных проверок проектов...")
            
            # Проверяем просроченные проекты
            overdue = self.check_overdue_projects()
            if overdue:
                message = "⚠️ <b>Просроченные проекты:</b>\n\n"
                for item in overdue:
                    project = item['project']
                    message += f"📌 <b>{project.title}</b>\n"
                    message += f"   ID: #{project.id}\n"
                    message += f"   {item['message']}\n\n"
                
                await self.send_notification(message)
            
            # Проверяем неоплаченные проекты
            unpaid = self.check_unpaid_projects()
            if unpaid:
                message = "💰 <b>Проекты с остатками к оплате:</b>\n\n"
                for item in unpaid:
                    if item['days_passed'] > 7:  # Только если прошло больше 7 дней
                        project = item['project']
                        message += f"📌 <b>{project.title}</b>\n"
                        message += f"   ID: #{project.id}\n"
                        message += f"   Остаток: {item['remaining']:,.0f} ₽\n"
                        message += f"   Дней с завершения: {item['days_passed']}\n\n"
                
                if len(message) > 50:  # Если есть что отправлять
                    await self.send_notification(message)
            
            # Проверяем невыплаченные остатки исполнителям
            unpaid_exec = self.check_unpaid_executors()
            if unpaid_exec:
                message = "👷 <b>Невыплаченные остатки исполнителям:</b>\n\n"
                for item in unpaid_exec:
                    project = item['project']
                    executor = item['executor']
                    message += f"📌 <b>{project.title}</b>\n"
                    message += f"   Исполнитель: {executor.username if executor else 'Неизвестный'}\n"
                    message += f"   Остаток к выплате: {item['remaining']:,.0f} ₽\n"
                    message += f"   Дней с завершения: {item['days_passed']}\n\n"
                
                await self.send_notification(message)
            
            logger.info("Ежедневные проверки завершены")
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении ежедневных проверок: {str(e)}")
    
    def get_automation_summary(self) -> Dict[str, Any]:
        """Получить сводку по автоматизации"""
        try:
            # Считаем статистику
            total_projects = self.db.query(Project).count()
            overdue_count = self.db.query(Project).filter(Project.status == 'overdue').count()
            
            unpaid_projects = self.check_unpaid_projects()
            unpaid_executors = self.check_unpaid_executors()
            
            total_unpaid_clients = sum(p['remaining'] for p in unpaid_projects)
            total_unpaid_executors = sum(e['remaining'] for e in unpaid_executors)
            
            return {
                'total_projects': total_projects,
                'overdue_count': overdue_count,
                'unpaid_projects_count': len(unpaid_projects),
                'unpaid_executors_count': len(unpaid_executors),
                'total_unpaid_clients': total_unpaid_clients,
                'total_unpaid_executors': total_unpaid_executors,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении сводки автоматизации: {str(e)}")
            return {}