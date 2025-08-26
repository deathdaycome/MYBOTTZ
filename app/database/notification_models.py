"""
Модели для системы уведомлений сотрудников
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base

class EmployeeNotificationSettings(Base):
    """Настройки уведомлений для сотрудников"""
    __tablename__ = "employee_notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с пользователем админки
    admin_user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=False, unique=True)
    
    # Telegram ID для отправки уведомлений
    telegram_user_id = Column(String(50), nullable=False, index=True)
    
    # Основные настройки
    notifications_enabled = Column(Boolean, default=True)
    notification_language = Column(String(10), default='ru')
    
    # Настройки для исполнителей (проекты)
    project_assigned = Column(Boolean, default=True)  # Назначение на проект
    project_status_changed = Column(Boolean, default=True)  # Изменение статуса проекта
    project_deadline_reminder = Column(Boolean, default=True)  # Напоминание о дедлайнах
    project_overdue = Column(Boolean, default=True)  # Просрочка проекта
    project_new_task = Column(Boolean, default=True)  # Новая задача в проекте
    
    # Настройки для продажников (Avito и CRM)
    avito_new_message = Column(Boolean, default=True)  # Новое сообщение с Avito
    avito_unread_reminder = Column(Boolean, default=True)  # Напоминание о непрочитанных
    avito_urgent_message = Column(Boolean, default=True)  # Срочные сообщения
    lead_assigned = Column(Boolean, default=True)  # Назначение лида
    lead_status_changed = Column(Boolean, default=True)  # Изменение статуса лида
    deal_assigned = Column(Boolean, default=True)  # Назначение сделки
    deal_status_changed = Column(Boolean, default=True)  # Изменение статуса сделки
    
    # Настройки времени уведомлений
    work_hours_start = Column(String(5), default='09:00')  # Начало рабочего дня
    work_hours_end = Column(String(5), default='18:00')  # Конец рабочего дня
    weekend_notifications = Column(Boolean, default=False)  # Уведомления в выходные
    urgent_notifications_always = Column(Boolean, default=True)  # Срочные всегда
    
    # Интервалы напоминаний (в минутах)
    avito_reminder_interval = Column(Integer, default=30)  # Напоминание о непрочитанных Avito
    project_reminder_interval = Column(Integer, default=120)  # Напоминание о проектах
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    admin_user = relationship("AdminUser", backref="notification_settings")
    
    def to_dict(self):
        return {
            "id": self.id,
            "admin_user_id": self.admin_user_id,
            "telegram_user_id": self.telegram_user_id,
            "notifications_enabled": self.notifications_enabled,
            "notification_language": self.notification_language,
            
            # Проекты
            "project_assigned": self.project_assigned,
            "project_status_changed": self.project_status_changed,
            "project_deadline_reminder": self.project_deadline_reminder,
            "project_overdue": self.project_overdue,
            "project_new_task": self.project_new_task,
            
            # Avito и CRM
            "avito_new_message": self.avito_new_message,
            "avito_unread_reminder": self.avito_unread_reminder,
            "avito_urgent_message": self.avito_urgent_message,
            "lead_assigned": self.lead_assigned,
            "lead_status_changed": self.lead_status_changed,
            "deal_assigned": self.deal_assigned,
            "deal_status_changed": self.deal_status_changed,
            
            # Рабочее время
            "work_hours_start": self.work_hours_start,
            "work_hours_end": self.work_hours_end,
            "weekend_notifications": self.weekend_notifications,
            "urgent_notifications_always": self.urgent_notifications_always,
            
            # Интервалы
            "avito_reminder_interval": self.avito_reminder_interval,
            "project_reminder_interval": self.project_reminder_interval,
            
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class NotificationQueue(Base):
    """Очередь уведомлений"""
    __tablename__ = "notification_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Получатель
    telegram_user_id = Column(String(50), nullable=False, index=True)
    admin_user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
    
    # Тип и содержание уведомления
    notification_type = Column(String(50), nullable=False)  # project_assigned, avito_message, etc.
    priority = Column(String(20), default='normal')  # low, normal, high, urgent
    
    # Сообщение
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String(500), nullable=True)  # Ссылка для действия
    
    # Метаданные
    entity_type = Column(String(50), nullable=True)  # project, lead, deal, avito_chat
    entity_id = Column(String(100), nullable=True)  # ID сущности
    metadata = Column(JSON, nullable=True)  # Дополнительные данные
    
    # Статус обработки
    status = Column(String(20), default='pending')  # pending, sent, failed, cancelled
    scheduled_at = Column(DateTime, default=datetime.utcnow)  # Когда отправить
    sent_at = Column(DateTime, nullable=True)  # Когда отправлено
    
    # Повторные попытки
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Группировка (для объединения похожих уведомлений)
    group_key = Column(String(100), nullable=True, index=True)
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "telegram_user_id": self.telegram_user_id,
            "admin_user_id": self.admin_user_id,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "title": self.title,
            "message": self.message,
            "action_url": self.action_url,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "metadata": self.metadata,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "group_key": self.group_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class NotificationLog(Base):
    """Лог отправленных уведомлений"""
    __tablename__ = "notification_log"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Получатель и отправитель
    telegram_user_id = Column(String(50), nullable=False, index=True)
    admin_user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
    sent_by_user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
    
    # Уведомление
    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Результат отправки
    status = Column(String(20), nullable=False)  # sent, failed
    error_message = Column(Text, nullable=True)
    telegram_message_id = Column(Integer, nullable=True)
    
    # Метаданные
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    
    # Время
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "telegram_user_id": self.telegram_user_id,
            "admin_user_id": self.admin_user_id,
            "sent_by_user_id": self.sent_by_user_id,
            "notification_type": self.notification_type,
            "title": self.title,
            "message": self.message,
            "status": self.status,
            "error_message": self.error_message,
            "telegram_message_id": self.telegram_message_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }