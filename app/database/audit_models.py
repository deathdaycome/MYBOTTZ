"""
Модели для системы аудит-лога
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class AuditActionType(enum.Enum):
    """Типы действий для аудита"""
    # CRUD операции
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # Аутентификация
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    
    # Импорт/Экспорт
    IMPORT = "import"
    EXPORT = "export"
    
    # Системные действия
    SETTING_CHANGE = "setting_change"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"
    ROLE_ASSIGN = "role_assign"
    ROLE_REMOVE = "role_remove"
    
    # Бизнес-операции
    LEAD_CONVERT = "lead_convert"
    DEAL_CREATE = "deal_create"
    DEAL_CLOSE = "deal_close"
    PROJECT_START = "project_start"
    PROJECT_COMPLETE = "project_complete"
    PAYMENT_RECEIVE = "payment_receive"
    DOCUMENT_GENERATE = "document_generate"
    DOCUMENT_SIGN = "document_sign"
    
    # Коммуникации
    EMAIL_SEND = "email_send"
    SMS_SEND = "sms_send"
    NOTIFICATION_SEND = "notification_send"
    
    # Автоматизации
    AUTOMATION_EXECUTE = "automation_execute"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"


class AuditEntityType(enum.Enum):
    """Типы сущностей для аудита"""
    USER = "user"
    CLIENT = "client"
    LEAD = "lead"
    DEAL = "deal"
    PROJECT = "project"
    TASK = "task"
    DOCUMENT = "document"
    INVOICE = "invoice"
    PAYMENT = "payment"
    SETTING = "setting"
    ROLE = "role"
    PERMISSION = "permission"
    AUTOMATION = "automation"
    WORKFLOW = "workflow"
    REPORT = "report"
    FILE = "file"


class AuditLog(Base):
    """Основная таблица аудит-лога"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True)
    
    # Время и действие
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action_type = Column(Enum(AuditActionType), nullable=False, index=True)
    
    # Пользователь
    user_id = Column(Integer, ForeignKey("admin_users.id"), index=True)
    user_email = Column(String(200))  # Сохраняем email на момент действия
    user_role = Column(String(100))  # Роль на момент действия
    
    # IP и сессия
    ip_address = Column(String(45))  # IPv4 или IPv6
    user_agent = Column(Text)
    session_id = Column(String(100))
    
    # Сущность
    entity_type = Column(Enum(AuditEntityType), index=True)
    entity_id = Column(Integer, index=True)
    entity_name = Column(String(500))  # Название/описание сущности
    
    # Детали действия
    description = Column(Text)  # Человекочитаемое описание
    
    # Изменения данных (для UPDATE)
    old_values = Column(JSON)  # Старые значения
    new_values = Column(JSON)  # Новые значения
    changed_fields = Column(JSON)  # Список измененных полей
    
    # Дополнительная информация
    extra_metadata = Column(JSON)  # Любые дополнительные данные
    
    # Результат
    success = Column(String(10), default='success')  # success, failure, partial
    error_message = Column(Text)
    
    # Время выполнения
    duration_ms = Column(Integer)  # Длительность операции в миллисекундах
    
    # Связи
    user = relationship("AdminUser", foreign_keys=[user_id])
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_audit_timestamp_user', 'timestamp', 'user_id'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_action_entity', 'action_type', 'entity_type'),
    )
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action_type": self.action_type.value if self.action_type else None,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_role": self.user_role,
            "ip_address": self.ip_address,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "description": self.description,
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms
        }


class AuditSession(Base):
    """Сессии пользователей для аудита"""
    __tablename__ = "audit_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Информация о сессии
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Информация о подключении
    ip_address = Column(String(45))
    user_agent = Column(Text)
    browser = Column(String(100))
    os = Column(String(100))
    device_type = Column(String(50))  # desktop, mobile, tablet
    
    # Геолокация (опционально)
    country = Column(String(100))
    city = Column(String(100))
    
    # Статистика сессии
    actions_count = Column(Integer, default=0)
    pages_visited = Column(JSON, default=list)
    
    # Статус
    is_active = Column(String(10), default='active')  # active, expired, terminated
    termination_reason = Column(String(100))  # logout, timeout, forced
    
    # Связи
    user = relationship("AdminUser", foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "ip_address": self.ip_address,
            "browser": self.browser,
            "os": self.os,
            "device_type": self.device_type,
            "is_active": self.is_active,
            "actions_count": self.actions_count
        }


class AuditDataChange(Base):
    """Детальная история изменений данных"""
    __tablename__ = "audit_data_changes"
    
    id = Column(Integer, primary_key=True)
    audit_log_id = Column(Integer, ForeignKey("audit_log.id"), nullable=False)
    
    # Поле
    field_name = Column(String(100), nullable=False)
    field_type = Column(String(50))  # string, integer, boolean, json, etc.
    
    # Значения
    old_value = Column(Text)
    new_value = Column(Text)
    
    # Метаданные поля
    field_label = Column(String(200))  # Человекочитаемое название
    is_sensitive = Column(String(10), default='no')  # Чувствительные данные
    
    # Связи
    audit_log = relationship("AuditLog", backref="data_changes")


class AuditAlert(Base):
    """Оповещения о подозрительной активности"""
    __tablename__ = "audit_alerts"
    
    id = Column(Integer, primary_key=True)
    
    # Тип и важность
    alert_type = Column(String(100), nullable=False)  # multiple_failed_logins, unusual_activity, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Описание
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Связанные данные
    user_id = Column(Integer, ForeignKey("admin_users.id"))
    session_id = Column(String(100))
    ip_address = Column(String(45))
    
    # Детали
    details = Column(JSON)
    
    # Время
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Обработка
    is_resolved = Column(String(10), default='no')
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("admin_users.id"))
    resolution_notes = Column(Text)
    
    # Связи
    user = relationship("AdminUser", foreign_keys=[user_id])
    resolver = relationship("AdminUser", foreign_keys=[resolved_by])


class AuditReport(Base):
    """Сохраненные отчеты аудита"""
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True)
    
    # Информация об отчете
    name = Column(String(200), nullable=False)
    description = Column(Text)
    report_type = Column(String(100))  # user_activity, security, compliance, etc.
    
    # Параметры
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    filters = Column(JSON)  # Фильтры для генерации
    
    # Результат
    data = Column(JSON)  # Данные отчета
    summary = Column(JSON)  # Сводка
    
    # Файлы
    file_path = Column(String(500))  # Путь к файлу отчета
    file_format = Column(String(20))  # pdf, excel, csv
    
    # Метаданные
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Расписание (для автоматических отчетов)
    is_scheduled = Column(String(10), default='no')
    schedule = Column(String(100))  # Cron выражение
    recipients = Column(JSON)  # Список email для отправки
    
    # Связи
    generator = relationship("AdminUser", foreign_keys=[generated_by])


class AuditRetention(Base):
    """Политики хранения аудит-логов"""
    __tablename__ = "audit_retention_policies"
    
    id = Column(Integer, primary_key=True)
    
    # Политика
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Условия
    entity_type = Column(Enum(AuditEntityType))
    action_type = Column(Enum(AuditActionType))
    
    # Срок хранения
    retention_days = Column(Integer, nullable=False)  # Дней хранения
    
    # Действие после истечения
    action_after_expiry = Column(String(50))  # delete, archive, anonymize
    
    # Статус
    is_active = Column(String(10), default='yes')
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Связи
    creator = relationship("AdminUser", foreign_keys=[created_by])


class AuditStatistics(Base):
    """Статистика аудита для быстрого доступа"""
    __tablename__ = "audit_statistics"
    
    id = Column(Integer, primary_key=True)
    
    # Период
    date = Column(DateTime, nullable=False, unique=True)  # Дата (день)
    
    # Общая статистика
    total_actions = Column(Integer, default=0)
    total_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    
    # По типам действий
    actions_by_type = Column(JSON, default=dict)
    
    # По сущностям
    actions_by_entity = Column(JSON, default=dict)
    
    # По пользователям
    top_users = Column(JSON, default=list)
    
    # Ошибки
    failed_actions = Column(Integer, default=0)
    error_types = Column(JSON, default=dict)
    
    # Производительность
    avg_duration_ms = Column(Integer)
    max_duration_ms = Column(Integer)
    
    # Безопасность
    security_alerts = Column(Integer, default=0)
    suspicious_activities = Column(JSON, default=list)
    
    # Метаданные
    calculated_at = Column(DateTime, default=datetime.utcnow)