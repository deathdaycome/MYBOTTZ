"""
Модели для системы автоматизаций и уведомлений
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class AutomationType(enum.Enum):
    """Типы автоматизаций"""
    LEAD_FOLLOWUP = "lead_followup"  # Напоминание о лиде
    DEAL_STAGE_CHANGE = "deal_stage_change"  # Смена этапа сделки
    PROJECT_DEADLINE = "project_deadline"  # Дедлайн проекта
    PAYMENT_REMINDER = "payment_reminder"  # Напоминание об оплате
    CLIENT_BIRTHDAY = "client_birthday"  # День рождения клиента
    TASK_ASSIGNMENT = "task_assignment"  # Назначение задачи
    REPORT_GENERATION = "report_generation"  # Генерация отчета
    EMAIL_CAMPAIGN = "email_campaign"  # Email рассылка
    SMS_NOTIFICATION = "sms_notification"  # SMS уведомление
    DOCUMENT_APPROVAL = "document_approval"  # Согласование документа
    CUSTOM = "custom"  # Пользовательская


class TriggerType(enum.Enum):
    """Типы триггеров"""
    TIME_BASED = "time_based"  # По времени
    EVENT_BASED = "event_based"  # По событию
    CONDITION_BASED = "condition_based"  # По условию
    MANUAL = "manual"  # Ручной запуск


class NotificationChannel(enum.Enum):
    """Каналы уведомлений"""
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class AutomationRule(Base):
    """Правила автоматизации"""
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(AutomationType), nullable=False)
    trigger_type = Column(Enum(TriggerType), nullable=False)
    
    # Условия срабатывания
    conditions = Column(JSON, default=dict)  # Условия в формате JSON
    schedule = Column(String(100))  # Cron-выражение для периодических задач
    
    # Действия
    actions = Column(JSON, default=list)  # Список действий
    
    # Настройки
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)  # 1-10, где 10 - максимальный приоритет
    max_executions = Column(Integer)  # Максимальное количество выполнений
    execution_count = Column(Integer, default=0)
    
    # Время
    last_executed_at = Column(DateTime)
    next_execution_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Связи
    creator = relationship("AdminUser", foreign_keys=[created_by])
    executions = relationship("AutomationExecution", back_populates="rule", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value if self.type else None,
            "trigger_type": self.trigger_type.value if self.trigger_type else None,
            "conditions": self.conditions,
            "actions": self.actions,
            "is_active": self.is_active,
            "priority": self.priority,
            "execution_count": self.execution_count,
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None
        }


class AutomationExecution(Base):
    """История выполнения автоматизаций"""
    __tablename__ = "automation_executions"
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id"), nullable=False)
    
    # Статус выполнения
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    error_message = Column(Text)
    
    # Контекст выполнения
    trigger_data = Column(JSON)  # Данные, вызвавшие срабатывание
    execution_data = Column(JSON)  # Данные выполнения
    result_data = Column(JSON)  # Результаты выполнения
    
    # Время выполнения
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)  # Длительность в миллисекундах
    
    # Связи
    rule = relationship("AutomationRule", back_populates="executions")


class NotificationTemplate(Base):
    """Шаблоны уведомлений"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    
    # Содержимое
    subject = Column(String(500))  # Тема (для email)
    content = Column(Text, nullable=False)  # Содержимое с переменными
    variables = Column(JSON, default=list)  # Список доступных переменных
    
    # Настройки
    is_active = Column(Boolean, default=True)
    language = Column(String(10), default='ru')
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Связи
    creator = relationship("AdminUser", foreign_keys=[created_by])
    notifications = relationship("Notification", back_populates="template")


class Notification(Base):
    """Уведомления"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    channel = Column(Enum(NotificationChannel), nullable=False)
    
    # Получатель
    recipient_type = Column(String(50))  # user, client, admin
    recipient_id = Column(Integer)
    recipient_email = Column(String(200))
    recipient_phone = Column(String(50))
    recipient_telegram_id = Column(String(100))
    
    # Содержимое
    subject = Column(String(500))
    content = Column(Text)
    data = Column(JSON)  # Дополнительные данные
    
    # Статус
    status = Column(String(50), default='pending')  # pending, sent, delivered, failed, read
    error_message = Column(Text)
    
    # Приоритет
    priority = Column(Integer, default=5)  # 1-10
    
    # Время
    scheduled_at = Column(DateTime)  # Запланированное время отправки
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    template = relationship("NotificationTemplate", back_populates="notifications")
    
    # Связь с автоматизацией
    automation_execution_id = Column(Integer, ForeignKey("automation_executions.id"))
    automation_execution = relationship("AutomationExecution")


class WorkflowTemplate(Base):
    """Шаблоны рабочих процессов"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # sales, marketing, support, etc.
    
    # Этапы процесса
    stages = Column(JSON, default=list)  # Список этапов с действиями
    
    # Настройки
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Системный шаблон
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Связи
    creator = relationship("AdminUser", foreign_keys=[created_by])
    workflows = relationship("WorkflowInstance", back_populates="template")


class WorkflowInstance(Base):
    """Экземпляры рабочих процессов"""
    __tablename__ = "workflow_instances"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    
    # Связь с сущностью
    entity_type = Column(String(50))  # lead, deal, project, etc.
    entity_id = Column(Integer)
    
    # Состояние
    current_stage = Column(Integer, default=0)
    status = Column(String(50), default='active')  # active, paused, completed, cancelled
    data = Column(JSON, default=dict)  # Данные процесса
    
    # Прогресс
    progress_percent = Column(Float, default=0)
    
    # Время
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)
    
    # Владелец процесса
    owner_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Связи
    template = relationship("WorkflowTemplate", back_populates="workflows")
    owner = relationship("AdminUser", foreign_keys=[owner_id])
    tasks = relationship("WorkflowTask", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowTask(Base):
    """Задачи в рамках рабочего процесса"""
    __tablename__ = "workflow_tasks"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    
    # Описание задачи
    stage_index = Column(Integer)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # manual, automatic, approval
    
    # Исполнитель
    assigned_to = Column(Integer, ForeignKey("admin_users.id"))
    
    # Статус
    status = Column(String(50), default='pending')  # pending, in_progress, completed, skipped
    
    # Результат
    result = Column(JSON)
    
    # Дедлайн
    due_date = Column(DateTime)
    
    # Время
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    workflow = relationship("WorkflowInstance", back_populates="tasks")
    assignee = relationship("AdminUser", foreign_keys=[assigned_to])


class NotificationSubscription(Base):
    """Подписки на уведомления"""
    __tablename__ = "notification_subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Тип подписки
    event_type = Column(String(100), nullable=False)  # Тип события
    entity_type = Column(String(50))  # Тип сущности
    entity_id = Column(Integer)  # ID конкретной сущности
    
    # Каналы
    channels = Column(JSON, default=list)  # Список каналов для уведомлений
    
    # Настройки
    is_active = Column(Boolean, default=True)
    frequency = Column(String(50), default='instant')  # instant, daily, weekly
    
    # Время
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("AdminUser", foreign_keys=[user_id])


class AutomationCondition(Base):
    """Библиотека условий для автоматизаций"""
    __tablename__ = "automation_conditions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Тип условия
    entity_type = Column(String(50))  # lead, deal, client, project
    field_name = Column(String(100))  # Поле для проверки
    operator = Column(String(50))  # equals, contains, greater_than, etc.
    value_type = Column(String(50))  # string, number, date, boolean
    
    # Пример использования
    example = Column(JSON)
    
    # Системное условие
    is_system = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AutomationAction(Base):
    """Библиотека действий для автоматизаций"""
    __tablename__ = "automation_actions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Тип действия
    category = Column(String(100))  # notification, task, update, integration
    action_type = Column(String(100))  # send_email, create_task, update_field, etc.
    
    # Параметры
    parameters = Column(JSON, default=dict)  # Описание параметров
    
    # Пример использования
    example = Column(JSON)
    
    # Системное действие
    is_system = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)