import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from telegram import Bot
from telegram.error import TelegramError

from ..config.settings import settings
from ..config.logging import get_logger, log_api_call
from ..database.database import get_db_context
from ..database.models import User, Project, AdminUser

logger = get_logger(__name__)

class NotificationService:
    """Сервис для отправки уведомлений"""
    
    def __init__(self, bot: Bot = None):
        self.bot = bot
        self.admin_chat_id = settings.ADMIN_CHAT_ID
        
    def set_bot(self, bot: Bot):
        """Установка бота для отправки уведомлений"""
        self.bot = bot
    
    async def send_admin_notification(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Отправка уведомления администратору"""
        if not self.admin_chat_id or not self.bot:
            logger.warning("Админ чат ID или бот не настроены")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                parse_mode=parse_mode
            )
            
            log_api_call("Telegram", "send_admin_notification", True)
            logger.info("Уведомление администратору отправлено")
            return True
            
        except TelegramError as e:
            log_api_call("Telegram", "send_admin_notification", False)
            logger.error(f"Ошибка отправки уведомления админу: {e}")
            return False
    
    async def send_user_notification(self, user_id: int, message: str, parse_mode: str = 'HTML') -> bool:
        """Отправка уведомления пользователю"""
        if not self.bot:
            logger.warning("Бот не настроен")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=parse_mode
            )
            
            log_api_call("Telegram", "send_user_notification", True)
            logger.info(f"Уведомление пользователю {user_id} отправлено")
            return True
            
        except TelegramError as e:
            log_api_call("Telegram", "send_user_notification", False)
            logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
            return False
    
    async def send_telegram_notification(self, user_id: int, message: str, parse_mode: str = 'HTML') -> bool:
        """Отправка уведомления через Telegram (алиас для send_user_notification)"""
        return await self.send_user_notification(user_id, message, parse_mode)
    
    async def notify_new_project(self, project: Project, user: User) -> bool:
        """Уведомление о новом проекте"""
        message = f"""
🆕 <b>Новый проект!</b>

📋 <b>ID:</b> #{project.id}
📝 <b>Название:</b> {project.title}
👤 <b>Клиент:</b> {user.first_name or 'Неизвестно'} (@{user.username or 'нет'})
💰 <b>Стоимость:</b> {project.estimated_cost:,}₽
🔧 <b>Сложность:</b> {project.complexity}
⏱ <b>Время:</b> {project.estimated_hours} часов

📄 <b>Описание:</b>
{project.description[:200]}{'...' if len(project.description) > 200 else ''}

<b>Контакты клиента:</b>
• Telegram ID: {user.telegram_id}
• Телефон: {user.phone or 'не указан'}
• Email: {user.email or 'не указан'}
        """
        
        return await self.send_admin_notification(message)
    
    async def notify_project_status_changed(self, project: Project, old_status: str, user: User) -> bool:
        """Уведомление об изменении статуса проекта"""
        status_names = {
            'new': 'Новый',
            'review': 'На рассмотрении',
            'accepted': 'Принят',
            'in_progress': 'В работе',
            'testing': 'Тестирование',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        
        status_emojis = {
            'new': '🆕',
            'review': '👀',
            'accepted': '✅',
            'in_progress': '🔄',
            'testing': '🧪',
            'completed': '🎉',
            'cancelled': '❌'
        }
        
        old_status_name = status_names.get(old_status, old_status)
        new_status_name = status_names.get(project.status, project.status)
        new_emoji = status_emojis.get(project.status, '📊')
        
        # Уведомление админу
        admin_message = f"""
📊 <b>Изменение статуса проекта</b>

📋 <b>Проект:</b> #{project.id} - {project.title}
👤 <b>Клиент:</b> {user.first_name or 'Неизвестно'} (@{user.username or 'нет'})
🔄 <b>Статус:</b> {old_status_name} → {new_status_name}
        """
        
        # Уведомление клиенту
        client_message = f"""
{new_emoji} <b>Обновление по вашему проекту</b>

📋 <b>Проект:</b> {project.title}
🔄 <b>Новый статус:</b> {new_status_name}

{self._get_status_description(project.status)}
        """
        
        # Отправляем уведомления
        admin_sent = await self.send_admin_notification(admin_message)
        
        # Проверяем наличие telegram_id у пользователя
        client_sent = False
        if user and user.telegram_id:
            client_sent = await self.send_user_notification(user.telegram_id, client_message)
            
            # Логируем результаты
            if client_sent:
                logger.info(f"Уведомление клиенту {user.telegram_id} о смене статуса отправлено")
            else:
                logger.error(f"Не удалось отправить уведомление клиенту {user.telegram_id}")
        else:
            logger.warning(f"User not found or missing telegram_id for project {project.id}")
            
        if admin_sent:
            logger.info(f"Уведомление админу о смене статуса проекта {project.id} отправлено")
        else:
            logger.warning(f"Не удалось отправить уведомление админу о смене статуса проекта {project.id}")
        
        # Возвращаем успех если хотя бы клиенту отправили
        return client_sent
    
    def _get_status_description(self, status: str) -> str:
        """Получение описания статуса для клиента"""
        descriptions = {
            'new': 'Ваш проект зарегистрирован в системе. Мы скоро свяжемся с вами для уточнения деталей.',
            'review': 'Мы изучаем ваш проект и готовим предложение. Ожидайте звонка в ближайшее время.',
            'accepted': 'Отлично! Ваш проект принят в работу. Мы свяжемся с вами для подписания договора.',
            'in_progress': 'Разработка началась! Мы будем регулярно информировать вас о прогрессе.',
            'testing': 'Проект находится на стадии тестирования. Скоро пришлем вам демо для ознакомления.',
            'completed': 'Поздравляем! Ваш проект готов. Спасибо за доверие!',
            'cancelled': 'К сожалению, проект был отменен. Если у вас есть вопросы, свяжитесь с нами.'
        }
        
        return descriptions.get(status, 'Статус проекта обновлен.')
    
    async def notify_error(self, error_message: str, context: Dict[str, Any] = None) -> bool:
        """Уведомление об ошибке"""
        message = f"""
❌ <b>Ошибка в боте</b>

<b>Сообщение:</b> {error_message}

<b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """
        
        if context:
            message += "\n\n<b>Контекст:</b>\n"
            for key, value in context.items():
                message += f"• {key}: {value}\n"
        
        return await self.send_admin_notification(message)
    
    async def notify_new_user(self, user: User) -> bool:
        """Уведомление о новом пользователе"""
        telegram_id_str = str(user.telegram_id) if user.telegram_id else "не указан"
        
        message = f"""
👤 <b>Новый пользователь</b>

<b>ID:</b> {telegram_id_str}
<b>Имя:</b> {user.first_name or 'не указано'}
<b>Username:</b> @{user.username or 'нет'}
<b>Дата регистрации:</b> {user.registration_date.strftime('%d.%m.%Y %H:%M') if user.registration_date else 'неизвестно'}
        """
        
        return await self.send_admin_notification(message)
    
    async def notify_consultation_request(self, user: User, topic: str, message_text: str = None) -> bool:
        """Уведомление о запросе консультации"""
        telegram_id_str = str(user.telegram_id) if user.telegram_id else "не указан"
        
        message = f"""
💬 <b>Запрос консультации</b>

👤 <b>Клиент:</b> {user.first_name or 'Неизвестно'} (@{user.username or 'нет'})
📱 <b>Telegram ID:</b> {telegram_id_str}
🎯 <b>Тема:</b> {topic}

📞 <b>Контакты:</b>
• Телефон: {user.phone or 'не указан'}
• Email: {user.email or 'не указан'}
        """
        
        if message_text:
            message += f"\n\n📝 <b>Сообщение:</b>\n{message_text}"
        
        return await self.send_admin_notification(message)
    
    async def send_daily_report(self) -> bool:
        """Отправка ежедневного отчета"""
        try:
            with get_db_context() as db:
                # Статистика за сегодня
                today = datetime.now().date()
                
                new_projects_count = db.query(Project).filter(
                    Project.created_at >= today
                ).count()
                
                new_users_count = db.query(User).filter(
                    User.registration_date >= today
                ).count()
                
                # Проекты по статусам
                in_progress_count = db.query(Project).filter(
                    Project.status == 'in_progress'
                ).count()
                
                completed_today_count = db.query(Project).filter(
                    Project.status == 'completed',
                    Project.updated_at >= today
                ).count()
                
                # Общая статистика
                total_projects = db.query(Project).count()
                total_users = db.query(User).count()
            
            message = f"""
📊 <b>Ежедневный отчет</b>

<b>За сегодня ({today.strftime('%d.%m.%Y')}):</b>
• 🆕 Новых проектов: {new_projects_count}
• 👤 Новых пользователей: {new_users_count}
• ✅ Завершено проектов: {completed_today_count}

<b>Текущее состояние:</b>
• 🔄 В работе: {in_progress_count} проектов
• 📊 Всего проектов: {total_projects}
• 👥 Всего пользователей: {total_users}

<b>Время отчета:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            
            return await self.send_admin_notification(message)
            
        except Exception as e:
            logger.error(f"Ошибка при создании ежедневного отчета: {e}")
            return False
    
    async def send_reminder(self, user_id: int, reminder_type: str, data: Dict[str, Any] = None) -> bool:
        """Отправка напоминания пользователю"""
        reminders = {
            'project_feedback': """
📝 <b>Ваше мнение важно!</b>

Ваш проект "{title}" завершен. Мы будем благодарны за отзыв о нашей работе.

Это поможет нам стать лучше и поможет другим клиентам сделать выбор.
            """,
            
            'project_update': """
📊 <b>Обновление по проекту</b>

Ваш проект "{title}" в работе уже {days} дней. 

Текущий статус: {status}
Примерное время до завершения: {estimated_days} дней
            """,
            
            'consultation_followup': """
💬 <b>Как дела с проектом?</b>

Недавно мы консультировали вас по вопросу разработки бота. 

Если у вас появились новые вопросы или вы готовы начать проект - мы всегда рады помочь!
            """
        }
        
        template = reminders.get(reminder_type)
        if not template:
            logger.warning(f"Неизвестный тип напоминания: {reminder_type}")
            return False
        
        try:
            message = template.format(**(data or {}))
            return await self.send_user_notification(user_id, message)
            
        except KeyError as e:
            logger.error(f"Отсутствуют данные для напоминания {reminder_type}: {e}")
            return False
    
    async def broadcast_message(self, user_ids: List[int], message: str, parse_mode: str = 'HTML') -> Dict[str, int]:
        """Массовая рассылка сообщений"""
        if not self.bot:
            logger.warning("Бот не настроен для рассылки")
            return {'sent': 0, 'failed': 0}
        
        sent_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=parse_mode
                )
                sent_count += 1
                
                # Небольшая задержка чтобы не превысить лимиты
                await asyncio.sleep(0.1)
                
            except TelegramError as e:
                logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                failed_count += 1
        
        # Отчет о рассылке
        await self.send_admin_notification(
            f"📤 <b>Результат рассылки</b>\n\n"
            f"✅ Отправлено: {sent_count}\n"
            f"❌ Не доставлено: {failed_count}\n"
            f"📊 Всего: {len(user_ids)}"
        )
        
        return {'sent': sent_count, 'failed': failed_count}
    
    async def notify_high_load(self, metric: str, value: Union[int, float], threshold: Union[int, float]) -> bool:
        """Уведомление о высокой нагрузке"""
        message = f"""
⚠️ <b>Предупреждение о нагрузке</b>

<b>Метрика:</b> {metric}
<b>Значение:</b> {value}
<b>Порог:</b> {threshold}
<b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

Рекомендуется проверить состояние сервера.
        """
        
        return await self.send_admin_notification(message)
    
    async def notify_service_status(self, service: str, status: str, details: str = None) -> bool:
        """Уведомление о статусе сервиса"""
        status_emojis = {
            'up': '✅',
            'down': '❌',
            'warning': '⚠️',
            'maintenance': '🔧'
        }
        
        emoji = status_emojis.get(status, '📊')
        
        message = f"""
{emoji} <b>Статус сервиса: {service}</b>

<b>Состояние:</b> {status.upper()}
<b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """
        
        if details:
            message += f"\n\n<b>Детали:</b> {details}"
        
        return await self.send_admin_notification(message)
    
    async def notify_new_revision(self, revision, project: Project, client_user: User) -> bool:
        """Уведомление о новой правке"""
        priority_emojis = {
            'low': '🟢',
            'normal': '🔵',
            'high': '🟡',
            'urgent': '🔴'
        }
        
        priority_names = {
            'low': 'Низкий',
            'normal': 'Обычный',
            'high': 'Высокий',
            'urgent': 'Срочный'
        }
        
        priority_emoji = priority_emojis.get(revision.priority, '📝')
        priority_name = priority_names.get(revision.priority, revision.priority)
        
        # Уведомление администратору (всегда отправляем)
        admin_message = f"""
📝 <b>Новая правка по проекту</b>

{priority_emoji} <b>Приоритет:</b> {priority_name}
📋 <b>Проект:</b> #{project.id} - {project.title}
👤 <b>Клиент:</b> {client_user.first_name or 'Неизвестно'} (@{client_user.username or 'нет'})
🔢 <b>Правка:</b> #{revision.revision_number}

📄 <b>Описание:</b>
{revision.description[:300]}{'...' if len(revision.description) > 300 else ''}

⏰ <b>Создана:</b> {revision.created_at.strftime('%d.%m.%Y %H:%M')}

{'🔒 <b>Статус:</b> Проект не назначен на исполнителя' if not project.assigned_executor_id else '👤 <b>Исполнитель:</b> Назначен'}
        """
        
        return await self.send_admin_notification(admin_message)
    
    async def notify_revision_status_changed(self, revision, project: Project, client_user: User, old_status: str) -> bool:
        """Уведомление об изменении статуса правки"""
        status_names = {
            'open': 'Открыта',
            'in_progress': 'В работе',
            'completed': 'Выполнена',
            'rejected': 'Отклонена'
        }
        
        status_emojis = {
            'open': '📝',
            'in_progress': '🔄',
            'completed': '✅',
            'rejected': '❌'
        }
        
        old_status_name = status_names.get(old_status, old_status)
        new_status_name = status_names.get(revision.status, revision.status)
        new_emoji = status_emojis.get(revision.status, '📊')
        
        # Уведомление клиенту
        client_message = f"""
{new_emoji} <b>Обновление по правке</b>

📋 <b>Проект:</b> {project.title}
🔢 <b>Правка:</b> #{revision.revision_number}
🔄 <b>Статус:</b> {new_status_name}

📄 <b>Описание правки:</b>
{revision.description[:200]}{'...' if len(revision.description) > 200 else ''}

{self._get_revision_status_description(revision.status)}
        """
        
        # Уведомление админу
        admin_message = f"""
📊 <b>Изменение статуса правки</b>

📋 <b>Проект:</b> #{project.id} - {project.title}
👤 <b>Клиент:</b> {client_user.first_name or 'Неизвестно'} (@{client_user.username or 'нет'})
🔢 <b>Правка:</b> #{revision.revision_number}
🔄 <b>Статус:</b> {old_status_name} → {new_status_name}
        """
        
        # Отправляем уведомления
        admin_sent = await self.send_admin_notification(admin_message)
        
        # Проверяем наличие telegram_id у клиента
        client_sent = False
        if client_user and client_user.telegram_id:
            client_sent = await self.send_user_notification(client_user.telegram_id, client_message)
        else:
            logger.warning(f"Client user not found or missing telegram_id for project {project.id}")
        
        return admin_sent and client_sent
    
    async def notify_revision_message(self, revision, project: Project, message, sender_user: User, recipient_user: User) -> bool:
        """Уведомление о новом сообщении в правке"""
        # Проверяем, что пользователи существуют и имеют telegram_id
        if not recipient_user or not recipient_user.telegram_id:
            logger.warning(f"Recipient user not found or missing telegram_id for revision {revision.id}")
            return False
            
        if not sender_user:
            sender_name = "Команда"
            sender_type = "исполнитель"
        else:
            sender_name = sender_user.first_name or 'Неизвестно'
            if hasattr(sender_user, 'telegram_id') and sender_user.telegram_id:
                sender_type = "клиент" if sender_user.telegram_id == project.user_id else "исполнитель"
            else:
                sender_type = "исполнитель"
        
        message_text = f"""
💬 <b>Новое сообщение по правке</b>

📋 <b>Проект:</b> {project.title}
🔢 <b>Правка:</b> #{revision.revision_number}
👤 <b>От:</b> {sender_name} ({sender_type})

📝 <b>Сообщение:</b>
{message.message[:300]}{'...' if len(message.message) > 300 else ''}

⏰ <b>Время:</b> {message.created_at.strftime('%d.%m.%Y %H:%M')}
        """
        
        # Отправляем текстовое сообщение
        result = await self.send_user_notification(recipient_user.telegram_id, message_text)
        
        # Отправляем изображения если есть
        await self._send_revision_message_images(recipient_user.telegram_id, message, sender_name, sender_type)
        
        return result
    
    def _get_revision_status_description(self, status: str) -> str:
        """Получить описание статуса правки для клиента"""
        descriptions = {
            'open': '📋 Правка принята и будет рассмотрена в ближайшее время.',
            'in_progress': '🔄 Исполнитель работает над исправлением.',
            'completed': '🎉 Правка выполнена! Проверьте результат.',
            'rejected': '❌ Правка отклонена. Проверьте комментарии.'
        }
        return descriptions.get(status, '')
    
    async def _send_revision_message_images(self, user_id: int, message, sender_name: str, sender_type: str):
        """Отправить изображения из сообщения правки"""
        try:
            from ..database.database import get_db_context
            from ..database.models import RevisionMessageFile
            import os
            from pathlib import Path
            
            with get_db_context() as db:
                # Получаем файлы сообщения
                message_files = db.query(RevisionMessageFile).filter(
                    RevisionMessageFile.message_id == message.id
                ).all()
                
                for file in message_files:
                    if file.file_type == 'image':
                        file_path = Path(file.file_path)
                        
                        # Проверяем существование файла
                        if file_path.exists():
                            try:
                                # Создаем подпись к изображению
                                caption = f"📸 От: {sender_name} ({sender_type})\n"
                                caption += f"📅 {message.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                                caption += f"📎 {file.original_filename}"
                                
                                # Отправляем изображение
                                with open(file_path, 'rb') as photo:
                                    await self.bot.send_photo(
                                        chat_id=user_id,
                                        photo=photo,
                                        caption=caption,
                                        parse_mode='HTML'
                                    )
                                    
                                logger.info(f"Image sent to user {user_id}: {file.original_filename}")
                                    
                            except Exception as e:
                                logger.error(f"Ошибка при отправке изображения {file.original_filename} пользователю {user_id}: {e}")
                        else:
                            logger.warning(f"Image file not found: {file.file_path}")
                            
        except Exception as e:
            logger.error(f"Ошибка в _send_revision_message_images: {e}")

# Создаем глобальный экземпляр сервиса
notification_service = NotificationService()

# Функции-обертки для удобства
async def notify_admin(message: str) -> bool:
    """Быстрое уведомление администратора"""
    return await notification_service.send_admin_notification(message)

async def notify_user(user_id: int, message: str) -> bool:
    """Быстрое уведомление пользователя"""
    return await notification_service.send_user_notification(user_id, message)

async def notify_error(error: str, context: Dict[str, Any] = None) -> bool:
    """Быстрое уведомление об ошибке"""
    return await notification_service.notify_error(error, context)