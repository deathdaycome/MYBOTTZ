"""
CRM модели для системы BotDev Admin
Включает: Клиентов, Лиды, Сделки, Документы, Аудит-логи
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from .models import Base

# Таблица для связи многие-ко-многим между клиентами и тегами
client_tags = Table('client_tags', Base.metadata,
    Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('client_tag.id'), primary_key=True)
)

# Таблица для связи многие-ко-многим между сделками и услугами
deal_services = Table('deal_services', Base.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('service_id', Integer, ForeignKey('service_catalog.id'), primary_key=True)
)


class ClientType(enum.Enum):
    """Типы клиентов"""
    INDIVIDUAL = "individual"  # Физическое лицо
    COMPANY = "company"  # Компания
    IP = "ip"  # ИП
    SELF_EMPLOYED = "self_employed"  # Самозанятый


class ClientStatus(enum.Enum):
    """Статусы клиентов"""
    NEW = "new"  # Новый
    ACTIVE = "active"  # Активный
    INACTIVE = "inactive"  # Неактивный
    VIP = "vip"  # VIP клиент
    BLACKLIST = "blacklist"  # Черный список


class AvitoClientStatus(enum.Enum):
    """Специальные статусы для клиентов Avito"""
    HOT_LEAD = "hot_lead"  # Горячий лид 🔥
    WARM_CONTACT = "warm_contact"  # Теплый контакт 🟡
    COLD_CONTACT = "cold_contact"  # Холодный контакт 🔵
    DEAL_CLOSED = "deal_closed"  # Завершенная сделка ✅
    REJECTED = "rejected"  # Отклонен ❌


class LeadStatus(enum.Enum):
    """Статусы лидов"""
    NEW = "new"  # Новый
    CONTACT_MADE = "contact_made"  # Установлен контакт
    QUALIFICATION = "qualification"  # Квалификация
    PROPOSAL_SENT = "proposal_sent"  # Отправлено предложение
    NEGOTIATION = "negotiation"  # Переговоры
    WON = "won"  # Выиграно (конвертировано в сделку)
    LOST = "lost"  # Проиграно
    POSTPONED = "postponed"  # Отложено


class DealStatus(enum.Enum):
    """Статусы сделок"""
    NEW = "new"  # Новая
    DISCUSSION = "discussion"  # Обсуждение
    CONTRACT_PREP = "contract_prep"  # Подготовка договора
    CONTRACT_SIGNED = "contract_signed"  # Договор подписан
    PREPAYMENT = "prepayment"  # Ожидание предоплаты
    IN_WORK = "in_work"  # В работе
    TESTING = "testing"  # Тестирование
    ACCEPTANCE = "acceptance"  # Приемка
    PAYMENT = "payment"  # Ожидание оплаты
    COMPLETED = "completed"  # Завершена
    CANCELLED = "cancelled"  # Отменена


class Client(Base):
    """Модель клиента CRM"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(300), nullable=False, index=True)  # ФИО или название компании
    type = Column(Enum(ClientType), default=ClientType.INDIVIDUAL, nullable=False)
    status = Column(Enum(ClientStatus), default=ClientStatus.NEW, nullable=False)
    
    # Контактная информация
    phone = Column(String(50), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    telegram = Column(String(100), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    
    # Реквизиты для юр.лиц
    company_name = Column(String(500), nullable=True)  # Полное название компании
    inn = Column(String(20), nullable=True, index=True)  # ИНН
    kpp = Column(String(20), nullable=True)  # КПП
    ogrn = Column(String(20), nullable=True)  # ОГРН/ОГРНИП
    bank_details = Column(JSON, nullable=True)  # Банковские реквизиты
    
    # Дополнительная информация
    source = Column(String(100), nullable=True)  # Источник привлечения
    description = Column(Text, nullable=True)  # Описание/примечания
    preferences = Column(JSON, nullable=True)  # Предпочтения клиента
    communication_history = Column(JSON, default=list)  # История коммуникаций
    
    # Финансовая информация
    total_revenue = Column(Float, default=0.0)  # Общий доход от клиента
    average_check = Column(Float, default=0.0)  # Средний чек
    payment_terms = Column(String(200), nullable=True)  # Условия оплаты
    credit_limit = Column(Float, nullable=True)  # Кредитный лимит
    
    # Рейтинг и сегментация
    rating = Column(Integer, default=0)  # Рейтинг клиента (0-10)
    segment = Column(String(50), nullable=True)  # Сегмент (A, B, C, D)
    loyalty_level = Column(String(50), nullable=True)  # Уровень лояльности
    
    # Ответственные
    manager_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Avito-специфичные поля
    avito_chat_id = Column(String(100), nullable=True, index=True)  # ID чата в Avito
    avito_user_id = Column(String(100), nullable=True, index=True)  # ID пользователя в Avito
    avito_status = Column(Enum(AvitoClientStatus), nullable=True)  # Статус в Avito
    avito_dialog_history = Column(JSON, default=list)  # История диалога в Avito
    avito_notes = Column(Text, nullable=True)  # Заметки по Avito клиенту
    avito_follow_up = Column(DateTime, nullable=True)  # Напоминание о следующем контакте
    
    # Связь с пользователем телеграм (если есть)
    telegram_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    manager = relationship("AdminUser", foreign_keys=[manager_id], backref="managed_clients")
    telegram_user = relationship("User", backref="crm_client")
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    leads = relationship("Lead", back_populates="client", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="client")
    tags = relationship("ClientTag", secondary=client_tags, back_populates="clients")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "phone": self.phone,
            "email": self.email,
            "telegram": self.telegram,
            "whatsapp": self.whatsapp,
            "website": self.website,
            "address": self.address,
            "company_name": self.company_name,
            "inn": self.inn,
            "kpp": self.kpp,
            "ogrn": self.ogrn,
            "bank_details": self.bank_details,
            "source": self.source,
            "description": self.description,
            "preferences": self.preferences,
            "total_revenue": self.total_revenue,
            "average_check": self.average_check,
            "payment_terms": self.payment_terms,
            "credit_limit": self.credit_limit,
            "rating": self.rating,
            "segment": self.segment,
            "loyalty_level": self.loyalty_level,
            "manager_id": self.manager_id,
            "telegram_user_id": self.telegram_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id
        }


class Lead(Base):
    """Модель лида (потенциальной сделки)"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    title = Column(String(500), nullable=False)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    source = Column(String(100), nullable=True)  # Источник лида
    source_type = Column(String(50), nullable=True)  # hot/cold - горячий/холодный
    
    # Информация о компании (для холодных лидов)
    company_name = Column(String(500), nullable=True)
    company_sphere = Column(String(200), nullable=True)  # Сфера деятельности
    company_website = Column(String(500), nullable=True)
    company_address = Column(Text, nullable=True)
    company_size = Column(String(50), nullable=True)  # 1-10, 10-50, 50-100, 100+
    
    # Клиент
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    
    # Контактная информация (если клиент еще не создан)
    contact_name = Column(String(300), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_telegram = Column(String(100), nullable=True)
    
    # Детали лида
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)  # Требования/потребности
    budget = Column(Float, nullable=True)  # Бюджет
    probability = Column(Integer, default=50)  # Вероятность успеха (0-100%)
    
    # Сроки
    expected_close_date = Column(DateTime, nullable=True)  # Ожидаемая дата закрытия
    next_action_date = Column(DateTime, nullable=True)  # Дата следующего действия
    
    # История взаимодействий
    interactions = Column(JSON, default=list)  # История взаимодействий
    call_history = Column(JSON, default=list)  # История звонков
    email_history = Column(JSON, default=list)  # История писем
    tags = Column(JSON, default=list)  # Теги (#холодный #2гис #ресторан)
    notes = Column(Text, nullable=True)  # Примечания
    
    # Причина отказа/отложения
    lost_reason = Column(String(500), nullable=True)
    
    # Ответственный
    manager_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Конвертация в сделку
    converted_to_deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    converted_at = Column(DateTime, nullable=True)
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    client = relationship("Client", back_populates="leads")
    manager = relationship("AdminUser", foreign_keys=[manager_id], backref="managed_leads")
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    converted_deal = relationship("Deal", foreign_keys=[converted_to_deal_id], backref="source_lead")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value if self.status else None,
            "source": self.source,
            "client_id": self.client_id,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "contact_telegram": self.contact_telegram,
            "description": self.description,
            "requirements": self.requirements,
            "budget": self.budget,
            "probability": self.probability,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "next_action_date": self.next_action_date.isoformat() if self.next_action_date else None,
            "interactions": self.interactions,
            "notes": self.notes,
            "lost_reason": self.lost_reason,
            "manager_id": self.manager_id,
            "converted_to_deal_id": self.converted_to_deal_id,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id
        }


class Deal(Base):
    """Модель сделки"""
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    title = Column(String(500), nullable=False)
    status = Column(Enum(DealStatus), default=DealStatus.NEW, nullable=False, index=True)
    
    # Клиент
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Детали сделки
    description = Column(Text, nullable=True)
    technical_requirements = Column(JSON, nullable=True)  # ТЗ в структурированном виде
    
    # Финансы
    amount = Column(Float, nullable=False)  # Сумма сделки
    cost = Column(Float, nullable=True)  # Себестоимость
    margin = Column(Float, nullable=True)  # Маржа
    discount = Column(Float, default=0.0)  # Скидка
    
    # Платежи
    prepayment_percent = Column(Integer, default=50)  # Процент предоплаты
    prepayment_amount = Column(Float, default=0.0)  # Сумма предоплаты
    paid_amount = Column(Float, default=0.0)  # Оплачено клиентом
    payment_schedule = Column(JSON, nullable=True)  # График платежей
    
    # Сроки
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    # Документы
    contract_number = Column(String(100), nullable=True, index=True)
    contract_date = Column(DateTime, nullable=True)
    contract_signed = Column(Boolean, default=False)
    act_number = Column(String(100), nullable=True)
    act_date = Column(DateTime, nullable=True)
    
    # Связь с проектом
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    converted_to_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # ID проекта, созданного из сделки
    
    # Ответственные
    manager_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    executor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Дополнительные поля
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    tags = Column(JSON, default=list)  # Теги сделки
    custom_fields = Column(JSON, nullable=True)  # Кастомные поля
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    client = relationship("Client", back_populates="deals")
    project = relationship("Project", foreign_keys=[project_id], backref="deal_original")
    converted_project = relationship("Project", foreign_keys=[converted_to_project_id], backref="source_deal")
    manager = relationship("AdminUser", foreign_keys=[manager_id], backref="managed_deals")
    executor = relationship("AdminUser", foreign_keys=[executor_id], backref="executed_deals")
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    documents = relationship("Document", back_populates="deal")
    services = relationship("ServiceCatalog", secondary=deal_services, back_populates="deals")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value if self.status else None,
            "client_id": self.client_id,
            "description": self.description,
            "technical_requirements": self.technical_requirements,
            "amount": self.amount,
            "cost": self.cost,
            "margin": self.margin,
            "discount": self.discount,
            "prepayment_percent": self.prepayment_percent,
            "prepayment_amount": self.prepayment_amount,
            "paid_amount": self.paid_amount,
            "payment_schedule": self.payment_schedule,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "actual_start_date": self.actual_start_date.isoformat() if self.actual_start_date else None,
            "actual_end_date": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "contract_number": self.contract_number,
            "contract_date": self.contract_date.isoformat() if self.contract_date else None,
            "contract_signed": self.contract_signed,
            "act_number": self.act_number,
            "act_date": self.act_date.isoformat() if self.act_date else None,
            "project_id": self.project_id,
            "converted_to_project_id": self.converted_to_project_id,
            "manager_id": self.manager_id,
            "executor_id": self.executor_id,
            "priority": self.priority,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "created_by_id": self.created_by_id
        }


class Document(Base):
    """Модель документа"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Тип и название
    type = Column(String(50), nullable=False)  # contract, act, invoice, kp, specification, other
    name = Column(String(500), nullable=False)
    number = Column(String(100), nullable=True, index=True)
    
    # Связи
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Файл
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # Размер в байтах
    file_type = Column(String(50), nullable=True)  # MIME type
    
    # Контент (для генерируемых документов)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=True)
    content = Column(JSON, nullable=True)  # Данные для заполнения шаблона
    generated_html = Column(Text, nullable=True)  # Сгенерированный HTML
    
    # Статус и даты
    status = Column(String(50), default="draft")  # draft, sent, signed, archived
    date = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    
    # Дополнительно
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    extra_data = Column(JSON, nullable=True)  # Переименовано из metadata
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    client = relationship("Client", back_populates="documents")
    deal = relationship("Deal", back_populates="documents")
    project = relationship("Project", backref="documents")
    template = relationship("DocumentTemplate", backref="documents")
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "number": self.number,
            "client_id": self.client_id,
            "deal_id": self.deal_id,
            "project_id": self.project_id,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "template_id": self.template_id,
            "status": self.status,
            "date": self.date.isoformat() if self.date else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "signed_at": self.signed_at.isoformat() if self.signed_at else None,
            "description": self.description,
            "tags": self.tags,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id
        }


class DocumentTemplate(Base):
    """Модель шаблона документа"""
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(300), nullable=False)
    type = Column(String(50), nullable=False)  # contract, act, invoice, kp, specification
    description = Column(Text, nullable=True)
    
    # Шаблон
    template_html = Column(Text, nullable=False)  # HTML шаблон с переменными
    variables = Column(JSON, nullable=False)  # Список переменных и их описаний
    
    # Настройки
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Шаблон по умолчанию для типа
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "template_html": self.template_html,
            "variables": self.variables,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id
        }


# Модель AuditLog перенесена в audit_models.py

class ClientTag(Base):
    """Модель тега для клиентов"""
    __tablename__ = "client_tag"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(20), nullable=True)  # HEX цвет
    description = Column(Text, nullable=True)
    
    # Связи
    clients = relationship("Client", secondary=client_tags, back_populates="tags")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description
        }


class ServiceCatalog(Base):
    """Каталог услуг"""
    __tablename__ = "service_catalog"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(300), nullable=False)
    category = Column(String(100), nullable=False)  # Категория услуги
    description = Column(Text, nullable=True)
    
    # Цены
    base_price = Column(Float, nullable=False)  # Базовая цена
    min_price = Column(Float, nullable=True)  # Минимальная цена
    max_price = Column(Float, nullable=True)  # Максимальная цена
    
    # Сроки
    estimated_hours = Column(Integer, nullable=True)  # Оценка в часах
    estimated_days = Column(Integer, nullable=True)  # Оценка в днях
    
    # Дополнительно
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    deals = relationship("Deal", secondary=deal_services, back_populates="services")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "base_price": self.base_price,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "estimated_hours": self.estimated_hours,
            "estimated_days": self.estimated_days,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }