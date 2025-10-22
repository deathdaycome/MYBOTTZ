"""
Сервис уведомлений о задачах для сотрудников через Telegram
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from ..config.logging import get_logger
from ..database.models import Task, AdminUser, TaskComment
from ..config.settings import settings
import requests
import json

logger = get_logger(__name__)

class TaskNotificationService:
    """Сервис для отправки уведомлений о задачах сотрудникам"""
    
    def __init__(self):
        self.bot_token = settings.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def send_telegram_message(self, chat_id: int, message: str, parse_mode: str = "HTML") -> bool:
        """Отправить сообщение в Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Уведомление отправлено пользователю {chat_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка отправки уведомления пользователю {chat_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке уведомления: {e}")
            return False

    async def notify_task_assigned(self, db: Session, task: Task) -> bool:
        """Уведомить о назначенной задаче"""
        try:
            if not task.assigned_to or not task.assigned_to.telegram_id:
                logger.warning(f"У исполнителя задачи {task.id} нет Telegram ID")
                return False
            
            # Формируем сообщение
            message = self._format_task_assigned_message(task)
            
            # Отправляем уведомление
            success = await self.send_telegram_message(
                chat_id=task.assigned_to.telegram_id,
                message=message
            )
            
            if success:
                logger.info(f"Уведомление о назначенной задаче {task.id} отправлено пользователю {task.assigned_to.username}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о назначенной задаче {task.id}: {e}")
            return False

    async def notify_task_deadline_reminder(self, db: Session, task: Task) -> bool:
        """Напомнить о приближающемся дедлайне задачи"""
        try:
            if not task.assigned_to or not task.assigned_to.telegram_id:
                return False
                
            if task.status == "completed":
                return False
                
            # Проверяем, что дедлайн действительно приближается
            if not task.deadline:
                return False
                
            time_until_deadline = task.deadline - datetime.utcnow()
            
            # Отправляем напоминание за 24 часа, 4 часа и 1 час до дедлайна
            if time_until_deadline.total_seconds() <= 0:
                # Задача просрочена
                message = self._format_task_overdue_message(task)
            elif time_until_deadline.days == 0 and time_until_deadline.seconds <= 3600:
                # Менее часа до дедлайна
                message = self._format_task_urgent_reminder_message(task, "1 час")
            elif time_until_deadline.days == 0 and time_until_deadline.seconds <= 14400:
                # Менее 4 часов до дедлайна
                message = self._format_task_urgent_reminder_message(task, "4 часа")
            elif time_until_deadline.days <= 1:
                # Менее 24 часов до дедлайна
                message = self._format_task_urgent_reminder_message(task, "24 часа")
            else:
                return False  # Не время для напоминания
            
            # Отправляем уведомление
            success = await self.send_telegram_message(
                chat_id=task.assigned_to.telegram_id,
                message=message
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания о задаче {task.id}: {e}")
            return False

    async def notify_task_status_changed(self, db: Session, task: Task, old_status: str, comment: Optional[str] = None) -> bool:
        """Уведомить о изменении статуса задачи"""
        try:
            # Уведомляем создателя задачи, если статус изменился на completed
            if task.status == "completed" and task.created_by and task.created_by.telegram_id:
                message = self._format_task_completed_message(task)
                
                success = await self.send_telegram_message(
                    chat_id=task.created_by.telegram_id,
                    message=message
                )
                
                if success:
                    logger.info(f"Уведомление о завершении задачи {task.id} отправлено создателю {task.created_by.username}")
                
                return success
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при уведомлении об изменении статуса задачи {task.id}: {e}")
            return False

    async def notify_new_task_comment(self, db: Session, task: Task, comment: TaskComment, current_user: dict = None) -> bool:
        """Уведомить о новом комментарии к задаче

        Логика уведомлений:
        - Если комментарий от сотрудника (исполнителя) -> уведомляем админа (owner)
        - Если комментарий от админа -> уведомляем исполнителя задачи
        """
        try:
            # Определяем, кого уведомлять
            notify_users = []

            # Проверяем роль автора комментария
            is_admin_comment = current_user and current_user.get("role") == "owner"

            if is_admin_comment:
                # Комментарий от админа -> уведомляем исполнителя
                if (task.assigned_to and
                    task.assigned_to.telegram_id and
                    task.assigned_to.id != comment.author_id):
                    notify_users.append(task.assigned_to)
                    logger.info(f"Админ оставил комментарий к задаче {task.id}, уведомляем исполнителя {task.assigned_to.username}")
            else:
                # Комментарий от сотрудника -> уведомляем всех админов (владельцев)
                # Получаем создателя задачи (обычно это админ)
                if (task.created_by and
                    task.created_by.telegram_id and
                    task.created_by.id != comment.author_id and
                    task.created_by.role == "owner"):
                    notify_users.append(task.created_by)
                    logger.info(f"Сотрудник оставил комментарий к задаче {task.id}, уведомляем админа {task.created_by.username}")

                # Дополнительно можно уведомить всех админов из базы
                # Но для начала уведомим только создателя задачи

            if not notify_users:
                logger.warning(f"Нет пользователей для уведомления о комментарии к задаче {task.id}")
                return True

            # Формируем сообщение
            message = self._format_task_comment_message(task, comment)

            # Отправляем уведомления
            success_count = 0
            for user in notify_users:
                success = await self.send_telegram_message(
                    chat_id=user.telegram_id,
                    message=message
                )
                if success:
                    success_count += 1

            logger.info(f"Уведомления о комментарии к задаче {task.id} отправлены {success_count}/{len(notify_users)} пользователям")
            return success_count > 0

        except Exception as e:
            logger.error(f"Ошибка при уведомлении о комментарии к задаче {task.id}: {e}")
            return False

    def _format_task_assigned_message(self, task: Task) -> str:
        """Форматировать сообщение о назначенной задаче"""
        priority_emoji = {
            "low": "🟢",
            "normal": "🟡", 
            "high": "🟠",
            "urgent": "🔴"
        }
        
        emoji = priority_emoji.get(task.priority, "🟡")
        
        message = f"""
{emoji} <b>Новая задача назначена!</b>

📋 <b>Название:</b> {task.title}

📝 <b>Описание:</b>
{task.description or 'Не указано'}

⚡ <b>Приоритет:</b> {task.priority.upper()}

👤 <b>Назначил:</b> {task.created_by.username if task.created_by else 'Неизвестно'}
"""

        if task.deadline:
            deadline_str = task.deadline.strftime("%d.%m.%Y в %H:%M")
            message += f"\n⏰ <b>Дедлайн:</b> {deadline_str}"
            
            # Добавляем информацию о времени до дедлайна
            time_until = task.deadline - datetime.utcnow()
            if time_until.days > 0:
                message += f" ({time_until.days} дн.)"
            elif time_until.seconds > 3600:
                hours = time_until.seconds // 3600
                message += f" ({hours} ч.)"
            else:
                message += " (менее часа!)"

        if task.estimated_hours:
            message += f"\n⏱ <b>Оценка времени:</b> {task.estimated_hours} ч."

        message += f"\n\n🔗 <b>ID задачи:</b> #{task.id}"
        message += "\n\n📱 Для просмотра подробностей перейдите в админ-панель → Планировщик задач"
        
        return message.strip()

    def _format_task_urgent_reminder_message(self, task: Task, time_left: str) -> str:
        """Форматировать сообщение-напоминание о приближающемся дедлайне"""
        message = f"""
⏰ <b>НАПОМИНАНИЕ О ДЕДЛАЙНЕ!</b>

📋 <b>Задача:</b> {task.title}

🚨 <b>До дедлайна осталось:</b> {time_left}

📅 <b>Дедлайн:</b> {task.deadline.strftime("%d.%m.%Y в %H:%M")}

📌 <b>Статус:</b> {task.status.upper()}

🔗 <b>ID задачи:</b> #{task.id}

⚠️ Не забудьте завершить задачу вовремя!
"""
        return message.strip()

    def _format_task_overdue_message(self, task: Task) -> str:
        """Форматировать сообщение о просроченной задаче"""
        overdue_time = datetime.utcnow() - task.deadline
        
        if overdue_time.days > 0:
            overdue_str = f"{overdue_time.days} дн."
        elif overdue_time.seconds > 3600:
            hours = overdue_time.seconds // 3600
            overdue_str = f"{hours} ч."
        else:
            overdue_str = "менее часа"
        
        message = f"""
🔴 <b>ЗАДАЧА ПРОСРОЧЕНА!</b>

📋 <b>Задача:</b> {task.title}

⏰ <b>Просрочена на:</b> {overdue_str}

📅 <b>Дедлайн был:</b> {task.deadline.strftime("%d.%m.%Y в %H:%M")}

📌 <b>Статус:</b> {task.status.upper()}

🔗 <b>ID задачи:</b> #{task.id}

‼️ Пожалуйста, срочно завершите задачу или сообщите о проблемах!
"""
        return message.strip()

    def _format_task_completed_message(self, task: Task) -> str:
        """Форматировать сообщение о завершенной задаче"""
        message = f"""
✅ <b>Задача завершена!</b>

📋 <b>Название:</b> {task.title}

👤 <b>Исполнитель:</b> {task.assigned_to.username if task.assigned_to else 'Неизвестно'}

📅 <b>Завершена:</b> {task.completed_at.strftime("%d.%m.%Y в %H:%M") if task.completed_at else 'Сейчас'}

🔗 <b>ID задачи:</b> #{task.id}
"""

        if task.deadline:
            if task.completed_at and task.completed_at <= task.deadline:
                message += "\n🎯 Задача выполнена в срок!"
            else:
                message += "\n⚠️ Задача выполнена с опозданием"

        return message.strip()

    def _format_task_comment_message(self, task: Task, comment: TaskComment) -> str:
        """Форматировать сообщение о новом комментарии"""
        message = f"""
💬 <b>Новый комментарий к задаче</b>

📋 <b>Задача:</b> {task.title}

👤 <b>Автор:</b> {comment.author.username if comment.author else 'Неизвестно'}

📝 <b>Комментарий:</b>
{comment.comment}
"""

        # Добавляем информацию о прикрепленных файлах
        if comment.attachments and len(comment.attachments) > 0:
            message += f"\n\n📎 <b>Прикреплено файлов:</b> {len(comment.attachments)}"
            for idx, attachment in enumerate(comment.attachments, 1):
                file_type_emoji = "🖼" if attachment.get("type") == "image" else "📄"
                message += f"\n   {file_type_emoji} {attachment.get('original_filename', 'Файл ' + str(idx))}"

        message += f"\n\n🔗 <b>ID задачи:</b> #{task.id}"
        message += "\n\n📱 Посмотреть все комментарии и файлы можно в админ-панели"

        return message.strip()

    async def check_and_send_deadline_reminders(self, db: Session) -> int:
        """Проверить и отправить все необходимые напоминания о дедлайнах"""
        try:
            # Получаем задачи с приближающимися дедлайнами
            now = datetime.utcnow()
            
            # Задачи с дедлайном в ближайшие 25 часов (с запасом)
            upcoming_deadline = now + timedelta(hours=25)
            
            tasks_with_deadlines = db.query(Task).filter(
                Task.status.in_(["pending", "in_progress"]),
                Task.deadline.isnot(None),
                Task.deadline <= upcoming_deadline,
                Task.assigned_to_id.isnot(None)
            ).all()
            
            sent_count = 0
            
            for task in tasks_with_deadlines:
                try:
                    success = await self.notify_task_deadline_reminder(db, task)
                    if success:
                        sent_count += 1
                except Exception as e:
                    logger.error(f"Ошибка при отправке напоминания для задачи {task.id}: {e}")
                    continue
            
            logger.info(f"Отправлено {sent_count} напоминаний о дедлайнах")
            return sent_count
            
        except Exception as e:
            logger.error(f"Ошибка при проверке дедлайнов задач: {e}")
            return 0

# Глобальный экземпляр сервиса
task_notification_service = TaskNotificationService()