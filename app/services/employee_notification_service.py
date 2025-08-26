"""
Сервис уведомлений для сотрудников
"""

import asyncio
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import pytz

from ..database.database import get_db_context
from ..database.models import AdminUser, Project
from ..database.crm_models import Lead, Deal, Client
from ..database.notification_models import (
    EmployeeNotificationSettings, 
    NotificationQueue, 
    NotificationLog
)
from ..services.notification_service import notification_service
from ..config.logging import get_logger
from ..config.settings import settings

logger = get_logger(__name__)

class EmployeeNotificationService:
    """Сервис управления уведомлениями для сотрудников"""
    
    def __init__(self):
        self.timezone = pytz.timezone('Europe/Moscow')  # Московское время
        
    # === Управление настройками уведомлений ===
    
    def get_employee_settings(self, db: Session, admin_user_id: int) -> Optional[EmployeeNotificationSettings]:
        """Получить настройки уведомлений сотрудника"""
        return db.query(EmployeeNotificationSettings).filter(
            EmployeeNotificationSettings.admin_user_id == admin_user_id
        ).first()
    
    def create_employee_settings(self, db: Session, admin_user_id: int, 
                                telegram_user_id: str, **kwargs) -> EmployeeNotificationSettings:
        """Создать настройки уведомлений для сотрудника"""
        
        # Проверяем, не существуют ли уже настройки
        existing = self.get_employee_settings(db, admin_user_id)
        if existing:
            return self.update_employee_settings(db, admin_user_id, 
                                               telegram_user_id=telegram_user_id, **kwargs)
        
        settings = EmployeeNotificationSettings(
            admin_user_id=admin_user_id,
            telegram_user_id=str(telegram_user_id),
            **kwargs
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Созданы настройки уведомлений для пользователя {admin_user_id} (TG: {telegram_user_id})")
        return settings
    
    def update_employee_settings(self, db: Session, admin_user_id: int, **kwargs) -> EmployeeNotificationSettings:
        """Обновить настройки уведомлений сотрудника"""
        settings = self.get_employee_settings(db, admin_user_id)
        if not settings:
            raise ValueError(f"Настройки для пользователя {admin_user_id} не найдены")
        
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.updated_at = datetime.utcnow()
        db.commit()
        
        return settings
    
    def get_all_employee_settings(self, db: Session) -> List[EmployeeNotificationSettings]:
        """Получить настройки всех сотрудников"""
        return db.query(EmployeeNotificationSettings).filter(
            EmployeeNotificationSettings.notifications_enabled == True
        ).all()
    
    # === Проверка рабочего времени ===
    
    def is_work_time(self, settings: EmployeeNotificationSettings, 
                     priority: str = 'normal') -> bool:
        """Проверить, рабочее ли время для отправки уведомлений"""
        
        # Срочные уведомления отправляем всегда если настроено
        if priority in ['urgent', 'high'] and settings.urgent_notifications_always:
            return True
        
        now = datetime.now(self.timezone)
        
        # Проверяем выходные
        if now.weekday() >= 5 and not settings.weekend_notifications:  # 5=суббота, 6=воскресенье
            return False
        
        # Проверяем рабочие часы
        try:
            work_start = datetime.strptime(settings.work_hours_start, '%H:%M').time()
            work_end = datetime.strptime(settings.work_hours_end, '%H:%M').time()
            current_time = now.time()
            
            return work_start <= current_time <= work_end
        except:
            return True  # Если ошибка в парсинге времени, отправляем
    
    # === Создание уведомлений ===
    
    async def create_notification(self, db: Session, telegram_user_id: str,
                                notification_type: str, title: str, message: str,
                                priority: str = 'normal', entity_type: str = None,
                                entity_id: str = None, action_url: str = None,
                                metadata: Dict = None, group_key: str = None,
                                admin_user_id: int = None, delay_minutes: int = 0):
        """Создать уведомление в очереди"""
        
        # Планируем отправку
        scheduled_at = datetime.utcnow()
        if delay_minutes > 0:
            scheduled_at += timedelta(minutes=delay_minutes)
        
        notification = NotificationQueue(
            telegram_user_id=str(telegram_user_id),
            admin_user_id=admin_user_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            action_url=action_url,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            metadata=metadata or {},
            group_key=group_key,
            scheduled_at=scheduled_at
        )
        
        db.add(notification)
        db.commit()
        
        logger.info(f"Создано уведомление {notification_type} для {telegram_user_id}")
        return notification
    
    # === Уведомления для исполнителей (проекты) ===
    
    async def notify_project_assigned(self, db: Session, project_id: int, executor_id: int):
        """Уведомление о назначении на проект"""
        
        # Получаем настройки исполнителя
        settings = self.get_employee_settings(db, executor_id)
        if not settings or not settings.project_assigned:
            return
        
        # Получаем проект
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return
        
        title = "🎯 Новый проект назначен"
        message = f"""
📋 **{project.title}**

💰 Стоимость: {project.estimated_cost:,}₽
⏱ Время: {project.estimated_hours} часов
📅 Дедлайн: {project.deadline.strftime('%d.%m.%Y') if project.deadline else 'не указан'}

🔧 **Сложность:** {project.complexity}

📝 **Описание:**
{project.description[:200]}{'...' if len(project.description) > 200 else ''}

👆 Откройте админку для работы с проектом
        """
        
        action_url = f"http://147.45.215.199:8001/admin/projects/{project_id}"
        
        await self.create_notification(
            db=db,
            telegram_user_id=settings.telegram_user_id,
            admin_user_id=executor_id,
            notification_type='project_assigned',
            title=title,
            message=message.strip(),
            priority='high',
            entity_type='project',
            entity_id=str(project_id),
            action_url=action_url,
            metadata={
                'project_title': project.title,
                'project_cost': project.estimated_cost,
                'project_hours': project.estimated_hours
            }
        )
    
    async def notify_project_status_changed(self, db: Session, project_id: int, old_status: str, new_status: str):
        """Уведомление об изменении статуса проекта"""
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.assigned_executor_id:
            return
        
        # Получаем настройки исполнителя
        settings = self.get_employee_settings(db, project.assigned_executor_id)
        if not settings or not settings.project_status_changed:
            return
        
        status_names = {
            'new': '🆕 Новый',
            'review': '👀 На рассмотрении',
            'accepted': '✅ Принят',
            'in_progress': '🔄 В работе',
            'testing': '🧪 Тестирование',
            'completed': '🎉 Завершен',
            'cancelled': '❌ Отменен'
        }
        
        title = "📊 Статус проекта изменен"
        message = f"""
📋 **{project.title}**

🔄 **Статус:** {status_names.get(old_status, old_status)} → {status_names.get(new_status, new_status)}

{self._get_status_action_message(new_status)}
        """
        
        priority = 'high' if new_status in ['accepted', 'in_progress'] else 'normal'
        
        await self.create_notification(
            db=db,
            telegram_user_id=settings.telegram_user_id,
            admin_user_id=project.assigned_executor_id,
            notification_type='project_status_changed',
            title=title,
            message=message.strip(),
            priority=priority,
            entity_type='project',
            entity_id=str(project_id),
            action_url=f"http://147.45.215.199:8001/admin/projects/{project_id}",
            metadata={
                'project_title': project.title,
                'old_status': old_status,
                'new_status': new_status
            }
        )
    
    def _get_status_action_message(self, status: str) -> str:
        """Получить сообщение с действием для статуса"""
        messages = {
            'accepted': '🚀 Проект принят! Можете начинать работу.',
            'in_progress': '⚡ Проект в работе. Не забывайте обновлять статус.',
            'testing': '🧪 Проект на тестировании. Исправьте найденные ошибки.',
            'completed': '🎉 Проект завершен! Отличная работа!',
            'cancelled': '😔 Проект отменен. Свяжитесь с менеджером.',
        }
        return messages.get(status, '')
    
    # === Уведомления для продажников (Avito) ===
    
    async def notify_avito_new_message(self, db: Session, chat_id: str, client_name: str, 
                                     message_text: str, is_urgent: bool = False):
        """Уведомление о новом сообщении с Avito"""
        
        # Находим всех продажников с настройками Avito
        salespeople = db.query(EmployeeNotificationSettings).join(AdminUser).filter(
            and_(
                AdminUser.role == 'salesperson',
                EmployeeNotificationSettings.notifications_enabled == True,
                EmployeeNotificationSettings.avito_new_message == True
            )
        ).all()
        
        # Добавляем владельца (всегда получает уведомления)
        owner_settings = db.query(EmployeeNotificationSettings).join(AdminUser).filter(
            AdminUser.role == 'owner'
        ).first()
        
        if owner_settings:
            salespeople.append(owner_settings)
        
        if not salespeople:
            logger.warning("Нет продажников для уведомлений Avito")
            return
        
        # Обрезаем длинный текст
        preview_text = message_text[:100] + "..." if len(message_text) > 100 else message_text
        
        title = "🔔 Новое сообщение Avito"
        if is_urgent:
            title = "🚨 СРОЧНО! Сообщение Avito"
        
        message = f"""
👤 **Клиент:** {client_name}
💬 **Сообщение:** {preview_text}

📱 **Чат:** `{chat_id}`
🕐 **Время:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

👆 Откройте админку для ответа
        """
        
        priority = 'urgent' if is_urgent else 'high'
        action_url = f"http://147.45.215.199:8001/admin/avito"
        
        # Отправляем всем продажникам
        for settings in salespeople:
            # Проверяем настройки срочных сообщений
            if is_urgent and not settings.avito_urgent_message:
                continue
            
            await self.create_notification(
                db=db,
                telegram_user_id=settings.telegram_user_id,
                admin_user_id=settings.admin_user_id,
                notification_type='avito_new_message',
                title=title,
                message=message.strip(),
                priority=priority,
                entity_type='avito_chat',
                entity_id=chat_id,
                action_url=action_url,
                group_key=f"avito_chat_{chat_id}",
                metadata={
                    'chat_id': chat_id,
                    'client_name': client_name,
                    'message_preview': preview_text,
                    'is_urgent': is_urgent
                }
            )
    
    async def notify_avito_unread_reminder(self, db: Session, chat_id: str, client_name: str, 
                                         unread_count: int, last_message_time: datetime):
        """Напоминание о непрочитанных сообщениях Avito"""
        
        # Находим продажников с включенными напоминаниями
        salespeople = db.query(EmployeeNotificationSettings).join(AdminUser).filter(
            and_(
                AdminUser.role.in_(['owner', 'salesperson']),
                EmployeeNotificationSettings.notifications_enabled == True,
                EmployeeNotificationSettings.avito_unread_reminder == True
            )
        ).all()
        
        if not salespeople:
            return
        
        # Считаем время с последнего сообщения
        time_diff = datetime.utcnow() - last_message_time
        hours_passed = int(time_diff.total_seconds() // 3600)
        
        title = "⏰ Напоминание: непрочитанные Avito"
        message = f"""
👤 **Клиент:** {client_name}
📬 **Непрочитанных:** {unread_count}
⏱ **Не отвечаем:** {hours_passed} час(ов)

🔥 **ВАЖНО:** Клиент ждет ответа!

👆 Срочно откройте админку и ответьте
        """
        
        # Определяем приоритет по времени
        if hours_passed >= 2:
            priority = 'urgent'
            title = "🚨 КРИТИЧНО: " + title
        elif hours_passed >= 1:
            priority = 'high'
        else:
            priority = 'normal'
        
        action_url = f"http://147.45.215.199:8001/admin/avito"
        
        for settings in salespeople:
            await self.create_notification(
                db=db,
                telegram_user_id=settings.telegram_user_id,
                admin_user_id=settings.admin_user_id,
                notification_type='avito_unread_reminder',
                title=title,
                message=message.strip(),
                priority=priority,
                entity_type='avito_chat',
                entity_id=chat_id,
                action_url=action_url,
                group_key=f"avito_reminder_{chat_id}",
                metadata={
                    'chat_id': chat_id,
                    'client_name': client_name,
                    'unread_count': unread_count,
                    'hours_passed': hours_passed
                }
            )
    
    # === Отправка уведомлений ===
    
    async def process_notification_queue(self, db: Session):
        """Обработать очередь уведомлений"""
        
        # Получаем уведомления для отправки
        now = datetime.utcnow()
        notifications = db.query(NotificationQueue).filter(
            and_(
                NotificationQueue.status == 'pending',
                NotificationQueue.scheduled_at <= now,
                NotificationQueue.retry_count < NotificationQueue.max_retries
            )
        ).order_by(
            NotificationQueue.priority.desc(),
            NotificationQueue.scheduled_at
        ).limit(50).all()
        
        for notification in notifications:
            try:
                await self._send_notification(db, notification)
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления {notification.id}: {str(e)}")
                await self._handle_failed_notification(db, notification, str(e))
    
    async def _send_notification(self, db: Session, notification: NotificationQueue):
        """Отправить уведомление"""
        
        # Проверяем настройки получателя
        settings = db.query(EmployeeNotificationSettings).filter(
            EmployeeNotificationSettings.telegram_user_id == notification.telegram_user_id
        ).first()
        
        if settings and not self.is_work_time(settings, notification.priority):
            # Переносим на следующий рабочий час
            next_work_time = self._get_next_work_time(settings)
            notification.scheduled_at = next_work_time
            db.commit()
            return
        
        # Формируем сообщение
        full_message = f"**{notification.title}**\n\n{notification.message}"
        
        if notification.action_url:
            full_message += f"\n\n[🔗 Открыть в админке]({notification.action_url})"
        
        # Отправляем через notification_service
        success = await notification_service.send_user_notification(
            int(notification.telegram_user_id),
            full_message,
            parse_mode='Markdown'
        )
        
        if success:
            # Помечаем как отправленное
            notification.status = 'sent'
            notification.sent_at = datetime.utcnow()
            
            # Записываем в лог
            log_entry = NotificationLog(
                telegram_user_id=notification.telegram_user_id,
                admin_user_id=notification.admin_user_id,
                notification_type=notification.notification_type,
                title=notification.title,
                message=notification.message,
                status='sent',
                entity_type=notification.entity_type,
                entity_id=notification.entity_id
            )
            db.add(log_entry)
            
            # Удаляем дублирующие уведомления в группе
            if notification.group_key:
                db.query(NotificationQueue).filter(
                    and_(
                        NotificationQueue.group_key == notification.group_key,
                        NotificationQueue.id != notification.id,
                        NotificationQueue.status == 'pending'
                    )
                ).update({'status': 'cancelled'})
            
            logger.info(f"Уведомление {notification.id} отправлено пользователю {notification.telegram_user_id}")
            
        else:
            raise Exception("Не удалось отправить уведомление через Telegram")
        
        db.commit()
    
    async def _handle_failed_notification(self, db: Session, notification: NotificationQueue, error: str):
        """Обработать неудачную отправку"""
        
        notification.retry_count += 1
        
        if notification.retry_count >= notification.max_retries:
            notification.status = 'failed'
            
            # Записываем в лог
            log_entry = NotificationLog(
                telegram_user_id=notification.telegram_user_id,
                admin_user_id=notification.admin_user_id,
                notification_type=notification.notification_type,
                title=notification.title,
                message=notification.message,
                status='failed',
                error_message=error,
                entity_type=notification.entity_type,
                entity_id=notification.entity_id
            )
            db.add(log_entry)
            
        else:
            # Планируем повторную отправку через 5 минут
            notification.scheduled_at = datetime.utcnow() + timedelta(minutes=5)
        
        db.commit()
    
    def _get_next_work_time(self, settings: EmployeeNotificationSettings) -> datetime:
        """Получить следующее рабочее время"""
        now = datetime.now(self.timezone)
        
        try:
            work_start = datetime.strptime(settings.work_hours_start, '%H:%M').time()
            
            # Если сегодня еще рабочий день и время не прошло
            if now.weekday() < 5:  # Понедельник-пятница
                today_start = datetime.combine(now.date(), work_start)
                if now < today_start:
                    return today_start.replace(tzinfo=None)
            
            # Иначе следующий рабочий день
            days_ahead = 1
            if now.weekday() >= 4:  # Пятница или выходные
                days_ahead = 7 - now.weekday()  # До понедельника
            
            next_work_day = now + timedelta(days=days_ahead)
            return datetime.combine(next_work_day.date(), work_start).replace(tzinfo=None)
            
        except:
            # Если ошибка, отправляем через час
            return datetime.utcnow() + timedelta(hours=1)
    
    async def notify_project_deadline_reminder(
        self,
        db: Session,
        project_id: int,
        executor_id: int,
        project_title: str,
        deadline: datetime,
        is_overdue: bool = False
    ):
        """Напоминание исполнителю о дедлайне проекта"""
        
        settings = self.get_employee_settings(db, executor_id)
        if not settings or not settings.notifications_enabled:
            return
        
        if is_overdue and not settings.project_overdue:
            return
        elif not is_overdue and not settings.project_deadline_reminder:
            return
        
        # Просроченные проекты - всегда срочные
        is_urgent = is_overdue or settings.urgent_notifications_always
        
        # Проверяем рабочее время (кроме срочных)
        if not is_urgent and not self.is_work_time(settings):
            return
        
        if is_overdue:
            title = f"🔴 Проект просрочен!"
            time_info = f"Дедлайн был: {deadline.strftime('%d.%m.%Y %H:%M')}"
            priority = 'high'
        else:
            title = f"⏰ Приближается дедлайн проекта"
            time_info = f"Дедлайн: {deadline.strftime('%d.%m.%Y %H:%M')}"
            priority = 'normal'
        
        message = f"""**{project_title}**

{time_info}

🔗 Открыть проект: http://147.45.215.199:8001/admin/projects/"""
        
        await self.create_notification(
            db=db,
            telegram_user_id=settings.telegram_user_id,
            admin_user_id=executor_id,
            notification_type='project_deadline_reminder' if not is_overdue else 'project_overdue',
            title=title,
            message=message,
            entity_type='project',
            entity_id=str(project_id),
            priority=priority,
            action_url=f"http://147.45.215.199:8001/admin/projects/{project_id}"
        )
    
    async def notify_avito_unread_reminder(
        self,
        db: Session,
        chat_id: str,
        sender_name: str,
        message_text: str,
        time_ago: str,
        chat_url: str
    ):
        """Напоминание продажникам о неотвеченном сообщении Avito"""
        
        # Находим всех продажников с включенными напоминаниями Avito
        salespeople = db.query(AdminUser).filter(
            AdminUser.role.in_(['salesperson', 'sales'])
        ).all()
        
        for salesperson in salespeople:
            settings = self.get_employee_settings(db, salesperson.id)
            if not settings or not settings.notifications_enabled or not settings.avito_unread_reminder:
                continue
            
            # Проверяем рабочее время
            if not self.is_work_time(settings) and not settings.urgent_notifications_always:
                continue
            
            title = f"⏰ Неотвеченное сообщение Avito"
            message = f"""У вас есть неотвеченное сообщение от **{sender_name}**

💬 **Сообщение:** {message_text}  
🕒 **Получено:** {time_ago}

❗️ Пожалуйста, ответьте клиенту как можно скорее!"""
            
            await self.create_notification(
                db=db,
                telegram_user_id=settings.telegram_user_id,
                admin_user_id=salesperson.id,
                notification_type='avito_unread_reminder',
                title=title,
                message=message,
                entity_type='avito_chat',
                entity_id=chat_id,
                priority='high',  # Напоминания всегда высокий приоритет
                group_key=f"avito_reminder_{chat_id}",  # Группируем по чату
                action_url=chat_url
            )


# Создаем глобальный экземпляр сервиса
employee_notification_service = EmployeeNotificationService()