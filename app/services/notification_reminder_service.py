"""
Сервис напоминаний о неотвеченных сообщениях и просроченных задачах
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from ..services.avito_service import get_avito_service
from ..services.employee_notification_service import employee_notification_service
from ..database.database import get_db_context
from ..database.models import Project, AdminUser
from ..database.notification_models import EmployeeNotificationSettings
from ..config.settings import settings

logger = logging.getLogger(__name__)

class NotificationReminderService:
    """Сервис для отправки напоминаний о неотвеченных сообщениях и просроченных задачах"""
    
    def __init__(self):
        self.reminder_active = False
        self.last_avito_check: Dict[str, datetime] = {}  # chat_id -> last_check_time
        self.unread_messages: Dict[str, Dict] = {}  # chat_id -> message_data
        
    async def start_reminder_service(self, check_interval: int = 300):  # 5 минут по умолчанию
        """Запуск сервиса напоминаний"""
        self.reminder_active = True
        logger.info(f"🔔 Запускаем сервис напоминаний с интервалом {check_interval} секунд")
        
        while self.reminder_active:
            try:
                await self.check_avito_unread_reminders()
                await self.check_project_deadlines()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Ошибка в сервисе напоминаний: {e}")
                await asyncio.sleep(30)  # Короткая пауза при ошибке
    
    def stop_reminder_service(self):
        """Остановка сервиса напоминаний"""
        self.reminder_active = False
        logger.info("🔕 Сервис напоминаний остановлен")
    
    async def check_avito_unread_reminders(self):
        """Проверка неотвеченных сообщений Avito и отправка напоминаний"""
        try:
            avito_service = get_avito_service()
            if not avito_service:
                logger.debug("Avito service не инициализирован")
                return
                
            # Получаем список чатов
            chats = await avito_service.get_chats()
            if not chats:
                logger.debug("Чаты Avito не найдены")
                return
                
            logger.debug(f"Проверяем {len(chats)} чатов на неотвеченные сообщения")
            
            for chat in chats:
                await self.check_chat_for_unread_reminders(chat)
                
        except Exception as e:
            logger.error(f"Ошибка при проверке неотвеченных сообщений Avito: {e}")
    
    async def check_chat_for_unread_reminders(self, chat):
        """Проверка конкретного чата на неотвеченные сообщения"""
        chat_id = str(chat.id)
        current_user_id = 216012096  # ID текущего пользователя
        
        try:
            # Получаем сообщения чата
            avito_service = get_avito_service()
            messages = await avito_service.get_chat_messages_no_cache(chat_id)
            
            if not messages:
                return
            
            # Ищем последнее сообщение от клиента (не от нас)
            last_client_message = None
            our_response = None
            
            for message in reversed(messages):  # Идем с конца (самые новые)
                if message.author_id != current_user_id and not last_client_message:
                    last_client_message = message
                elif message.author_id == current_user_id and not our_response:
                    our_response = message
                    break
            
            if not last_client_message:
                return  # Нет сообщений от клиента
            
            # Проверяем, нужно ли отправить напоминание
            should_remind = False
            
            if not our_response:
                # Нет ответа вообще - проверяем время с момента получения сообщения
                message_time = last_client_message.created_at
                if isinstance(message_time, str):
                    message_time = datetime.fromisoformat(message_time.replace('Z', '+00:00'))
                
                time_since_message = datetime.utcnow() - message_time.replace(tzinfo=None)
                should_remind = time_since_message.total_seconds() > 1800  # 30 минут
                
            elif our_response.created_at < last_client_message.created_at:
                # Наш ответ был раньше последнего сообщения клиента
                message_time = last_client_message.created_at
                if isinstance(message_time, str):
                    message_time = datetime.fromisoformat(message_time.replace('Z', '+00:00'))
                
                time_since_message = datetime.utcnow() - message_time.replace(tzinfo=None)
                should_remind = time_since_message.total_seconds() > 1800  # 30 минут
            
            if should_remind:
                # Проверяем, не отправляли ли мы уже напоминание недавно
                last_reminder = self.last_avito_check.get(chat_id)
                if last_reminder:
                    time_since_reminder = datetime.utcnow() - last_reminder
                    if time_since_reminder.total_seconds() < 1800:  # Не чаще чем раз в 30 минут
                        return
                
                await self.send_avito_unread_reminder(chat, last_client_message)
                self.last_avito_check[chat_id] = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Ошибка при проверке чата {chat_id} на неотвеченные сообщения: {e}")
    
    async def send_avito_unread_reminder(self, chat, message):
        """Отправка напоминания о неотвеченном сообщении Avito"""
        try:
            # Получаем имя пользователя
            user_name = "Неизвестный"
            current_user_id = 216012096
            
            for user in chat.users:
                if user['id'] != current_user_id:
                    user_name = user.get('name', 'Неизвестный')
                    break
            
            # Текст сообщения (обрезаем если слишком длинный)
            message_text = message.content.get('text', 'Без текста')
            if len(message_text) > 100:
                message_text = message_text[:100] + "..."
            
            # Время сообщения
            message_time = message.created_at
            if isinstance(message_time, str):
                message_time = datetime.fromisoformat(message_time.replace('Z', '+00:00'))
            
            time_ago = datetime.utcnow() - message_time.replace(tzinfo=None)
            if time_ago.total_seconds() < 3600:
                time_str = f"{int(time_ago.total_seconds() / 60)} мин назад"
            else:
                time_str = f"{int(time_ago.total_seconds() / 3600)} ч назад"
            
            # Отправляем напоминания продажникам
            with get_db_context() as db:
                await employee_notification_service.notify_avito_unread_reminder(
                    db=db,
                    chat_id=str(chat.id),
                    sender_name=user_name,
                    message_text=message_text,
                    time_ago=time_str,
                    chat_url="http://147.45.215.199:8001/admin/avito/"
                )
                logger.info(f"Напоминание о неотвеченном сообщении от {user_name} отправлено продажникам")
                
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания о неотвеченном сообщении: {e}")
    
    async def check_project_deadlines(self):
        """Проверка дедлайнов проектов и отправка напоминаний"""
        try:
            with get_db_context() as db:
                now = datetime.utcnow()
                
                # Находим проекты с приближающимися дедлайнами (в течение 24 часов)
                upcoming_deadline = now + timedelta(hours=24)
                projects_due_soon = db.query(Project).filter(
                    Project.deadline.isnot(None),
                    Project.deadline <= upcoming_deadline,
                    Project.deadline > now,
                    Project.status.notin_(['completed', 'cancelled', 'on_hold']),
                    Project.assigned_executor_id.isnot(None)
                ).all()
                
                # Находим просроченные проекты
                overdue_projects = db.query(Project).filter(
                    Project.deadline.isnot(None),
                    Project.deadline < now,
                    Project.status.notin_(['completed', 'cancelled', 'on_hold']),
                    Project.assigned_executor_id.isnot(None)
                ).all()
                
                # Отправляем напоминания о приближающихся дедлайнах
                for project in projects_due_soon:
                    await employee_notification_service.notify_project_deadline_reminder(
                        db=db,
                        project_id=project.id,
                        executor_id=project.assigned_executor_id,
                        project_title=project.title,
                        deadline=project.deadline,
                        is_overdue=False
                    )
                
                # Отправляем уведомления о просроченных проектах
                for project in overdue_projects:
                    await employee_notification_service.notify_project_deadline_reminder(
                        db=db,
                        project_id=project.id,
                        executor_id=project.assigned_executor_id,
                        project_title=project.title,
                        deadline=project.deadline,
                        is_overdue=True
                    )
                
                if projects_due_soon or overdue_projects:
                    logger.info(f"Отправлено напоминаний о дедлайнах: {len(projects_due_soon)} приближающихся, {len(overdue_projects)} просроченных")
                
        except Exception as e:
            logger.error(f"Ошибка при проверке дедлайнов проектов: {e}")

# Глобальный экземпляр сервиса
notification_reminder_service = NotificationReminderService()