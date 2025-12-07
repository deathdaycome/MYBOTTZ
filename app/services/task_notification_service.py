"""
Сервис уведомлений о задачах для сотрудников через Telegram
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from ..config.logging import get_logger
from ..database.models import Task, AdminUser, TaskComment, TaskDeadlineNotification
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

    def _determine_notification_type(self, task: Task) -> Optional[str]:
        """Определить тип уведомления на основе времени до дедлайна"""
        if not task.deadline:
            return None

        now = datetime.utcnow()
        time_until_deadline = (task.deadline - now).total_seconds()

        # Задача просрочена
        if time_until_deadline <= 0:
            overdue_seconds = abs(time_until_deadline)
            # Если просрочена больше суток - ежедневное напоминание
            if overdue_seconds > 86400:  # 24 часа
                return "daily_overdue"
            return "overdue"

        # За 1 час (3600 секунд ± 15 минут окно)
        if 2700 <= time_until_deadline <= 4500:  # 45 мин - 1ч 15 мин
            return "1h_before"

        # За 4 часа (14400 секунд ± 30 минут окно)
        if 12600 <= time_until_deadline <= 16200:  # 3ч 30мин - 4ч 30мин
            return "4h_before"

        # За 24 часа (86400 секунд ± 1 час окно)
        if 82800 <= time_until_deadline <= 90000:  # 23ч - 25ч
            return "24h_before"

        return None

    def _was_notification_sent(self, db: Session, task: Task, notification_type: str) -> bool:
        """Проверить, было ли уже отправлено уведомление данного типа"""
        # Для daily_overdue проверяем за последние 24 часа
        if notification_type == "daily_overdue":
            last_24h = datetime.utcnow() - timedelta(hours=24)
            notification = db.query(TaskDeadlineNotification).filter(
                TaskDeadlineNotification.task_id == task.id,
                TaskDeadlineNotification.notification_type == notification_type,
                TaskDeadlineNotification.sent_at >= last_24h
            ).first()
        else:
            # Для остальных типов просто проверяем наличие записи
            notification = db.query(TaskDeadlineNotification).filter(
                TaskDeadlineNotification.task_id == task.id,
                TaskDeadlineNotification.notification_type == notification_type
            ).first()

        return notification is not None

    def _save_notification_sent(self, db: Session, task: Task, notification_type: str):
        """Сохранить информацию об отправленном уведомлении"""
        notification = TaskDeadlineNotification(
            task_id=task.id,
            notification_type=notification_type,
            sent_at=datetime.utcnow(),
            deadline_at=task.deadline
        )
        db.add(notification)
        db.commit()
        logger.info(f"Сохранено уведомление типа '{notification_type}' для задачи {task.id}")

    async def notify_task_deadline_reminder(self, db: Session, task: Task, notification_type: str) -> bool:
        """Напомнить о приближающемся дедлайне задачи

        Args:
            db: Сессия БД
            task: Задача
            notification_type: Тип уведомления (24h_before, 4h_before, 1h_before, overdue, daily_overdue)
        """
        try:
            if not task.assigned_to or not task.assigned_to.telegram_id:
                logger.warning(f"У задачи {task.id} нет исполнителя с Telegram ID")
                return False

            if task.status == "completed":
                logger.info(f"Задача {task.id} уже завершена, уведомление не отправляется")
                return False

            # Проверяем, было ли уже отправлено это уведомление
            if self._was_notification_sent(db, task, notification_type):
                logger.debug(f"Уведомление '{notification_type}' для задачи {task.id} уже было отправлено")
                return False

            # Формируем сообщение в зависимости от типа
            if notification_type == "24h_before":
                message = self._format_task_urgent_reminder_message(task, "24 часа")
            elif notification_type == "4h_before":
                message = self._format_task_urgent_reminder_message(task, "4 часа")
            elif notification_type == "1h_before":
                message = self._format_task_urgent_reminder_message(task, "1 час")
            elif notification_type == "overdue":
                message = self._format_task_overdue_message(task)
            elif notification_type == "daily_overdue":
                message = self._format_task_daily_overdue_message(task)
            else:
                logger.warning(f"Неизвестный тип уведомления: {notification_type}")
                return False

            # Отправляем уведомление
            success = await self.send_telegram_message(
                chat_id=task.assigned_to.telegram_id,
                message=message
            )

            if success:
                # Сохраняем информацию об отправленном уведомлении
                self._save_notification_sent(db, task, notification_type)
                logger.info(f"✅ Отправлено уведомление '{notification_type}' для задачи {task.id} пользователю {task.assigned_to.username}")

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
            # Логируем входные данные для отладки
            logger.info(f"💬 Обработка уведомления о комментарии к задаче {task.id}")
            logger.info(f"   Автор комментария ID: {comment.author_id}, username: {comment.author.username if comment.author else 'N/A'}")
            logger.info(f"   Current user: {current_user}")

            # Определяем, кого уведомлять
            notify_users = []

            # Проверяем роль автора комментария
            is_admin_comment = current_user and current_user.get("role") == "owner"
            logger.info(f"   Это комментарий от админа: {is_admin_comment}")

            if is_admin_comment:
                # Комментарий от админа -> уведомляем исполнителя
                logger.info(f"   Проверяем исполнителя задачи для уведомления...")
                logger.info(f"   assigned_to: {task.assigned_to}")
                if task.assigned_to:
                    logger.info(f"   assigned_to.telegram_id: {task.assigned_to.telegram_id}")
                    logger.info(f"   assigned_to.id: {task.assigned_to.id}, comment.author_id: {comment.author_id}")

                if (task.assigned_to and
                    task.assigned_to.telegram_id and
                    task.assigned_to.id != comment.author_id):
                    notify_users.append(task.assigned_to)
                    logger.info(f"✅ Админ оставил комментарий к задаче {task.id}, уведомляем исполнителя {task.assigned_to.username} (telegram_id: {task.assigned_to.telegram_id})")
                else:
                    logger.warning(f"⚠️ Не удалось добавить исполнителя для уведомления (assigned_to: {task.assigned_to}, telegram_id: {task.assigned_to.telegram_id if task.assigned_to else 'N/A'})")
            else:
                # Комментарий от сотрудника -> уведомляем всех админов (владельцев)
                logger.info(f"   Сотрудник оставил комментарий к задаче {task.id}, ищем админов для уведомления")

                # Получаем всех админов (владельцев) из базы
                from ..database.models import AdminUser
                admins = db.query(AdminUser).filter(
                    AdminUser.role == "owner",
                    AdminUser.telegram_id.isnot(None),
                    AdminUser.id != comment.author_id  # Не уведомляем автора комментария
                ).all()

                logger.info(f"   Найдено админов с telegram_id и role='owner': {len(admins)}")

                for admin in admins:
                    notify_users.append(admin)
                    logger.info(f"   ✅ Добавляем админа {admin.username} (ID: {admin.id}, telegram_id: {admin.telegram_id}) для уведомления о комментарии")

                if not notify_users:
                    # Если не нашли админов через роль, пытаемся через создателя задачи
                    if (task.created_by and
                        task.created_by.telegram_id and
                        task.created_by.id != comment.author_id):
                        notify_users.append(task.created_by)
                        logger.info(f"Уведомляем создателя задачи {task.created_by.username}")

            if not notify_users:
                logger.warning(f"⚠️ Нет пользователей для уведомления о комментарии к задаче {task.id}")
                logger.warning(f"   is_admin_comment: {is_admin_comment}")
                logger.warning(f"   task.assigned_to: {task.assigned_to}")
                logger.warning(f"   task.created_by: {task.created_by}")
                return True

            # Формируем сообщение
            message = self._format_task_comment_message(task, comment)
            logger.info(f"   Сформировано сообщение для {len(notify_users)} получателей")

            # Отправляем уведомления
            success_count = 0
            for user in notify_users:
                logger.info(f"   Отправка уведомления пользователю {user.username} (telegram_id: {user.telegram_id})...")
                success = await self.send_telegram_message(
                    chat_id=user.telegram_id,
                    message=message
                )
                if success:
                    success_count += 1
                    logger.info(f"   ✅ Успешно отправлено")
                else:
                    logger.warning(f"   ❌ Не удалось отправить")

            logger.info(f"📊 Уведомления о комментарии к задаче {task.id} отправлены {success_count}/{len(notify_users)} пользователям")
            return success_count > 0

        except Exception as e:
            logger.error(f"❌ Ошибка при уведомлении о комментарии к задаче {task.id}: {e}")
            import traceback
            traceback.print_exc()
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
        """Форматировать сообщение о просроченной задаче (первое уведомление)"""
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

    def _format_task_daily_overdue_message(self, task: Task) -> str:
        """Форматировать ежедневное напоминание о просроченной задаче"""
        overdue_time = datetime.utcnow() - task.deadline

        if overdue_time.days > 0:
            overdue_str = f"{overdue_time.days} дн."
        else:
            hours = overdue_time.seconds // 3600
            overdue_str = f"{hours} ч."

        message = f"""
🔴 <b>НАПОМИНАНИЕ: ЗАДАЧА ВСЁ ЕЩЁ ПРОСРОЧЕНА</b>

📋 <b>Задача:</b> {task.title}

⏰ <b>Просрочена на:</b> {overdue_str}

📅 <b>Дедлайн был:</b> {task.deadline.strftime("%d.%m.%Y в %H:%M")}

📌 <b>Статус:</b> {task.status.upper()}

🔗 <b>ID задачи:</b> #{task.id}

⚠️ Задача всё ещё не завершена. Пожалуйста, обновите статус или свяжитесь с администратором.
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
        """Проверить и отправить все необходимые напоминания о дедлайнах

        Новая логика уведомлений:
        - За 24 часа: одно уведомление
        - За 4 часа: одно уведомление
        - За 1 час: одно уведомление
        - При просрочке: одно уведомление
        - Если долго просрочено: раз в день

        Returns:
            Количество отправленных уведомлений
        """
        try:
            now = datetime.utcnow()

            # Получаем все задачи с дедлайнами, которые не завершены
            tasks_with_deadlines = db.query(Task).filter(
                Task.status.in_(["pending", "in_progress"]),  # Незавершённые задачи
                Task.deadline.isnot(None),
                Task.assigned_to_id.isnot(None)
            ).all()

            sent_count = 0
            checked_count = 0

            logger.info(f"🔍 Проверка дедлайнов: найдено {len(tasks_with_deadlines)} задач с дедлайнами")

            for task in tasks_with_deadlines:
                try:
                    checked_count += 1

                    # Определяем тип уведомления для этой задачи
                    notification_type = self._determine_notification_type(task)

                    if not notification_type:
                        logger.debug(f"Задача {task.id} ({task.title}): не требует уведомления сейчас")
                        continue

                    time_until = (task.deadline - now).total_seconds()
                    logger.info(f"📋 Задача {task.id} ({task.title}): определён тип уведомления '{notification_type}' (до дедлайна: {time_until/3600:.1f}ч)")

                    # Отправляем уведомление
                    success = await self.notify_task_deadline_reminder(db, task, notification_type)

                    if success:
                        sent_count += 1

                except Exception as e:
                    logger.error(f"Ошибка при обработке задачи {task.id}: {e}")
                    continue

            logger.info(f"✅ Проверка завершена: проверено {checked_count} задач, отправлено {sent_count} уведомлений")
            return sent_count

        except Exception as e:
            logger.error(f"Ошибка при проверке дедлайнов задач: {e}")
            import traceback
            traceback.print_exc()
            return 0

# Глобальный экземпляр сервиса
task_notification_service = TaskNotificationService()