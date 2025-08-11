from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json
import hashlib

Base = declarative_base()

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    state = Column(String(100), default="main_menu")  # Текущее состояние в боте
    preferences = Column(JSON, default=lambda: {})  # Настройки пользователя
    notes = Column(Text, nullable=True)  # Заметки админа
    is_active = Column(Boolean, default=True)
    
    # Настройки бота и хостинга
    bot_token = Column(String(500), nullable=True)  # API токен бота
    timeweb_login = Column(String(255), nullable=True)  # Логин Timeweb
    timeweb_password = Column(String(255), nullable=True)  # Пароль Timeweb
    user_telegram_id = Column(String(50), nullable=True)  # ID пользователя в Telegram для связи
    chat_id = Column(String(50), nullable=True)  # ID чата для уведомлений
    bot_configured = Column(Boolean, default=False)  # Статус настройки бота
    
    # Связи
    projects = relationship("Project", back_populates="user")
    messages = relationship("Message", back_populates="user")
    consultant_sessions = relationship("ConsultantSession", back_populates="user")
    created_revisions = relationship("ProjectRevision", back_populates="created_by")
    
    def to_dict(self):
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "state": self.state,
            "preferences": self.preferences,
            "notes": self.notes,
            "is_active": self.is_active,
            "bot_token": self.bot_token,
            "timeweb_login": self.timeweb_login,
            "timeweb_password": self.timeweb_password,
            "user_telegram_id": self.user_telegram_id,
            "chat_id": self.chat_id,
            "bot_configured": self.bot_configured
        }

class Project(Base):
    """Модель проекта"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    original_request = Column(Text, nullable=True)  # Оригинальный запрос пользователя
    structured_tz = Column(JSON, default=lambda: {})  # Структурированное ТЗ
    status = Column(String(50), default="new")  # new, review, accepted, in_progress, testing, completed, cancelled
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    project_type = Column(String(50), nullable=True)  # telegram_bot, whatsapp_bot, web_bot, integration
    complexity = Column(String(20), default="medium")  # simple, medium, complex, premium
    color = Column(String(20), default="default")  # default, green, yellow, red
    estimated_cost = Column(Float, default=0.0)  # Полная стоимость проекта (видит только владелец)
    executor_cost = Column(Float, nullable=True)  # Стоимость для исполнителя (видит исполнитель)
    final_cost = Column(Float, nullable=True)
    
    # Финансовые поля
    prepayment_amount = Column(Float, default=0.0)  # Сумма предоплаты от клиента
    client_paid_total = Column(Float, default=0.0)  # Сколько уже заплатил клиент
    executor_paid_total = Column(Float, default=0.0)  # Сколько уже выплачено исполнителю
    
    estimated_hours = Column(Integer, default=0)
    actual_hours = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_metadata = Column(JSON, default=lambda: {})  # Дополнительные данные
    
    # Назначение исполнителя
    assigned_executor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)  # Когда назначен исполнитель
    
    # Связи
    user = relationship("User", back_populates="projects")
    messages = relationship("Message", back_populates="project")
    legacy_files = relationship("File", back_populates="project")  # Старые файлы
    files = relationship("ProjectFile", back_populates="project")  # Новые файлы проектов
    assigned_executor = relationship("AdminUser", back_populates="assigned_projects")
    status_logs = relationship("ProjectStatusLog", back_populates="project")
    revisions = relationship("ProjectRevision", back_populates="project")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "original_request": self.original_request,
            "status": self.status,
            "priority": self.priority,
            "project_type": self.project_type,
            "complexity": self.complexity,
            "color": self.color if hasattr(self, 'color') else 'default',
            "estimated_cost": self.estimated_cost,
            "executor_cost": self.executor_cost,
            "final_cost": self.final_cost,
            "prepayment_amount": self.prepayment_amount,
            "client_paid_total": self.client_paid_total,
            "executor_paid_total": self.executor_paid_total,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "structured_tz": self.structured_tz,
            "project_metadata": self.project_metadata,
            "assigned_executor_id": self.assigned_executor_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "assigned_executor": self.assigned_executor.to_dict() if self.assigned_executor else None
        }

class Message(Base):
    """Модель сообщений"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    message_text = Column(Text, nullable=True)
    message_type = Column(String(50), default="text")  # text, voice, document, image, video
    sender_type = Column(String(20), default="user")  # user, admin, bot
    file_path = Column(String(500), nullable=True)
    is_read = Column(Boolean, default=False)
    thread_id = Column(String(100), nullable=True)  # Для группировки сообщений
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="messages")
    project = relationship("Project", back_populates="messages")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "message_text": self.message_text,
            "message_type": self.message_type,
            "sender_type": self.sender_type,
            "file_path": self.file_path,
            "is_read": self.is_read,
            "thread_id": self.thread_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ConsultantSession(Base):
    """Модель сессий консультанта"""
    __tablename__ = "consultant_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), unique=True, nullable=False)  # Уникальный ID сессии
    topic = Column(String(200), nullable=True)  # Тема консультации
    status = Column(String(20), default="active")  # active, completed, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Время истечения сессии
    
    # Связи
    user = relationship("User", back_populates="consultant_sessions")
    queries = relationship("ConsultantQuery", back_populates="session")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "topic": self.topic,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

class ConsultantQuery(Base):
    """Модель запросов к консультанту"""
    __tablename__ = "consultant_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("consultant_sessions.id"), nullable=False)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    response_time = Column(Float, default=0.0)  # Время ответа в секундах
    created_at = Column(DateTime, default=datetime.utcnow)
    rating = Column(Integer, nullable=True)  # Оценка ответа от 1 до 5
    
    # Связи
    session = relationship("ConsultantSession", back_populates="queries")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_query": self.user_query,
            "ai_response": self.ai_response,
            "tokens_used": self.tokens_used,
            "response_time": self.response_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "rating": self.rating
        }

class Portfolio(Base):
    """Модель портфолио - обновленная версия с полным функционалом"""
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    subtitle = Column(String(500), nullable=True)  # Краткое описание
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # telegram_bots, web_development, mobile_apps, ai_integration, automation, ecommerce, other
    
    # Изображения
    main_image = Column(String(500), nullable=True)  # Главное изображение
    image_paths = Column(JSON, default=lambda: [])  # Дополнительные изображения
    
    # Технические характеристики
    technologies = Column(Text, nullable=True)  # Технологии через запятую
    complexity = Column(String(20), default="medium")  # simple, medium, complex, premium
    complexity_level = Column(Integer, default=5)  # 1-10 для точной оценки
    
    # Временные и финансовые характеристики
    development_time = Column(Integer, nullable=True)  # в днях
    cost = Column(Float, nullable=True)  # Стоимость проекта
    cost_range = Column(String(100), nullable=True)  # например "10000-15000"
    show_cost = Column(Boolean, default=False)  # Показывать стоимость в боте
    
    # Ссылки и демо
    demo_link = Column(String(500), nullable=True)  # Ссылка на демо
    repository_link = Column(String(500), nullable=True)  # Ссылка на репозиторий
    external_links = Column(JSON, default=lambda: [])  # Дополнительные ссылки
    
    # Настройки отображения
    is_featured = Column(Boolean, default=False)  # Рекомендуемые работы
    is_visible = Column(Boolean, default=True)  # Показывать в портфолио
    sort_order = Column(Integer, default=0)  # Порядок сортировки
    
    # Статистика
    views_count = Column(Integer, default=0)  # Количество просмотров
    likes_count = Column(Integer, default=0)  # Количество лайков
    
    # Метаданные
    tags = Column(Text, nullable=True)  # Теги для поиска через запятую
    client_name = Column(String(200), nullable=True)  # Имя клиента (если можно указать)
    project_status = Column(String(50), default="completed")  # completed, in_progress, demo
    completed_at = Column(DateTime, nullable=True)  # Дата завершения проекта
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # ID администратора, создавшего запись
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        # Формируем полные URL для изображений для админ-панели (относительные пути)
        main_image_url = None
        if self.main_image:
            main_image_url = f"/uploads/portfolio/{self.main_image}"
        
        image_paths_urls = []
        if self.image_paths:
            for img_path in self.image_paths:
                image_paths_urls.append(f"/uploads/portfolio/{img_path}")
        
        return {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "category": self.category,
            "main_image": main_image_url,
            "image_paths": image_paths_urls,
            "technologies": self.technologies,
            "complexity": self.complexity,
            "complexity_level": self.complexity_level,
            "development_time": self.development_time,
            "cost": self.cost,
            "cost_range": self.cost_range,
            "show_cost": self.show_cost,
            "demo_link": self.demo_link,
            "repository_link": self.repository_link,
            "external_links": self.external_links,
            "is_featured": self.is_featured,
            "is_visible": self.is_visible,
            "sort_order": self.sort_order,
            "views_count": self.views_count,
            "likes_count": self.likes_count,
            "tags": self.tags,
            "client_name": self.client_name,
            "project_status": self.project_status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by
        }
    
    def to_bot_dict(self):
        """Преобразование для отображения в боте"""
        from ..config.settings import settings
        
        # Формируем полные URL для изображений
        main_image_url = None
        if self.main_image:
            # Убираем лишние слэши
            clean_path = self.main_image.lstrip('/')
            main_image_url = f"http://localhost:{settings.ADMIN_PORT}/uploads/portfolio/{clean_path}"
        
        image_paths_urls = []
        if self.image_paths:
            for img_path in self.image_paths[:3]:  # Максимум 3 изображения для бота
                clean_path = img_path.lstrip('/')
                image_paths_urls.append(f"http://localhost:{settings.ADMIN_PORT}/uploads/portfolio/{clean_path}")
        
        return {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "category": self.category,
            "main_image": main_image_url,
            "image_paths": image_paths_urls,
            "technologies": self.technologies.split(',') if self.technologies else [],
            "complexity": self.complexity,
            "complexity_level": self.complexity_level,
            "development_time": self.development_time,
            "cost_display": self.cost_range if self.show_cost and self.cost_range else None,
            "demo_link": self.demo_link,
            "is_featured": self.is_featured,
            "views_count": self.views_count,
            "likes_count": self.likes_count,
            "tags": self.tags.split(',') if self.tags else []
        }
    
    @property 
    def technology_list(self):
        """Получить список технологий"""
        if not self.technologies:
            return []
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
    
    @property
    def tag_list(self):
        """Получить список тегов"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def increment_views(self):
        """Увеличить счетчик просмотров"""
        self.views_count += 1
    
    def increment_likes(self):
        """Увеличить счетчик лайков"""
        self.likes_count += 1

class Review(Base):
    """Модель отзывов"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(200), nullable=False)
    project_title = Column(String(300), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    review_text = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    is_visible = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "project_title": self.project_title,
            "rating": self.rating,
            "review_text": self.review_text,
            "image_path": self.image_path,
            "is_visible": self.is_visible,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class FAQ(Base):
    """Модель FAQ"""
    __tablename__ = "faq"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    views_count = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "views_count": self.views_count,
            "is_visible": self.is_visible,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Settings(Base):
    """Модель настроек"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    data_type = Column(String(20), default="string")  # string, int, float, bool, json
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "data_type": self.data_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class File(Base):
    """Модель файлов"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # document, image, audio, video
    file_size = Column(Integer, default=0)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_metadata = Column(JSON, default=lambda: {}) # Дополнительные данные о файле
    
    # Связи
    project = relationship("Project", back_populates="legacy_files")
    user = relationship("User")
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_name": self.original_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "file_metadata": self.file_metadata
        }

class AdminUser(Base):
    """Модель пользователя админ-панели"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default='executor')  # 'owner' или 'executor'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Связи
    assigned_projects = relationship("Project", back_populates="assigned_executor")
    uploaded_project_files = relationship("ProjectFile", back_populates="uploaded_by")
    created_statuses = relationship("ProjectStatus", back_populates="created_by")
    status_changes = relationship("ProjectStatusLog", back_populates="changed_by")
    assigned_revisions = relationship("ProjectRevision", back_populates="assigned_to")
    # activity_logs = relationship("AdminActivityLog", back_populates="user")  # TODO: Добавить миграцию
    
    def set_password(self, password):
        """Установить пароль с хешированием"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Проверить пароль"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def is_owner(self):
        """Проверить, является ли пользователь владельцем"""
        return self.role == 'owner'
    
    def is_executor(self):
        """Проверить, является ли пользователь исполнителем"""
        return self.role == 'executor'
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class ProjectFile(Base):
    """Модель файлов проектов"""
    __tablename__ = "project_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)  # 'zip', 'image', 'document', etc.
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    project = relationship("Project", back_populates="files")
    uploaded_by = relationship("AdminUser", back_populates="uploaded_project_files")
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "description": self.description,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "project_id": self.project_id,
            "uploaded_by": self.uploaded_by.to_dict() if self.uploaded_by else None
        }

class ProjectStatus(Base):
    """Модель статусов проекта"""
    __tablename__ = "project_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#6c757d")  # HEX цвет для UI
    icon = Column(String(50), default="fas fa-circle")  # FontAwesome иконка
    is_default = Column(Boolean, default=False)  # Системный статус
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)  # Порядок сортировки
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    project_status_logs = relationship("ProjectStatusLog", back_populates="status", foreign_keys="[ProjectStatusLog.status_id]")
    created_by = relationship("AdminUser", back_populates="created_statuses")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

class ProjectStatusLog(Base):
    """Лог изменений статусов проекта"""
    __tablename__ = "project_status_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("project_statuses.id"), nullable=False)
    previous_status_id = Column(Integer, ForeignKey("project_statuses.id"), nullable=True)
    comment = Column(Text, nullable=True)  # Комментарий к смене статуса
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Связи
    project = relationship("Project", back_populates="status_logs")
    status = relationship("ProjectStatus", back_populates="project_status_logs", foreign_keys=[status_id])
    previous_status = relationship("ProjectStatus", foreign_keys=[previous_status_id])
    changed_by = relationship("AdminUser", back_populates="status_changes")
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "status": self.status.to_dict() if self.status else None,
            "previous_status": self.previous_status.to_dict() if self.previous_status else None,
            "comment": self.comment,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            "changed_by": self.changed_by.to_dict() if self.changed_by else None
        }

class FinanceCategory(Base):
    """Модель категорий финансов"""
    __tablename__ = "finance_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Название категории
    type = Column(String(50), nullable=False)  # income или expense
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#6c757d")  # Цвет для графиков
    icon = Column(String(50), default="fas fa-circle")  # Иконка
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    transactions = relationship("FinanceTransaction", back_populates="category")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

class FinanceTransaction(Base):
    """Модель финансовых транзакций"""
    __tablename__ = "finance_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)  # Сумма
    type = Column(String(50), nullable=False)  # income или expense
    description = Column(Text, nullable=False)  # Описание транзакции
    date = Column(DateTime, nullable=False)  # Дата транзакции
    category_id = Column(Integer, ForeignKey("finance_categories.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Связь с проектом (если есть)
    contractor_name = Column(String(255), nullable=True)  # Имя исполнителя/поставщика
    receipt_url = Column(String(500), nullable=True)  # Ссылка на чек/документ
    notes = Column(Text, nullable=True)  # Дополнительные заметки
    is_recurring = Column(Boolean, default=False)  # Повторяющаяся транзакция
    recurring_period = Column(String(50), nullable=True)  # monthly, yearly, etc.
    parent_transaction_id = Column(Integer, ForeignKey("finance_transactions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Связи
    category = relationship("FinanceCategory", back_populates="transactions")
    project = relationship("Project", foreign_keys=[project_id])
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    parent_transaction = relationship("FinanceTransaction", remote_side=[id])
    child_transactions = relationship("FinanceTransaction", foreign_keys=[parent_transaction_id], overlaps="parent_transaction")
    
    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "category": self.category.to_dict() if self.category else None,
            "project": {"id": self.project.id, "title": self.project.title} if self.project else None,
            "contractor_name": self.contractor_name,
            "receipt_url": self.receipt_url,
            "notes": self.notes,
            "is_recurring": self.is_recurring,
            "recurring_period": self.recurring_period,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

class FinanceBudget(Base):
    """Модель бюджетов"""
    __tablename__ = "finance_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Название бюджета
    category_id = Column(Integer, ForeignKey("finance_categories.id"), nullable=False)
    planned_amount = Column(Float, nullable=False)  # Запланированная сумма
    period_start = Column(DateTime, nullable=False)  # Начало периода
    period_end = Column(DateTime, nullable=False)  # Конец периода
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Связи
    category = relationship("FinanceCategory")
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.to_dict() if self.category else None,
            "planned_amount": self.planned_amount,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

# Модели для расширенной финансовой системы

class Contractor(Base):
    """Модель исполнителя/подрядчика"""
    __tablename__ = "contractors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    contact_info = Column(JSON, default=lambda: {})  # email, phone, telegram, etc.
    skills = Column(JSON, default=lambda: [])  # навыки исполнителя
    hourly_rate = Column(Float, nullable=True)  # ставка за час
    project_rate = Column(Float, nullable=True)  # ставка за проект
    rating = Column(Float, default=0.0)  # рейтинг исполнителя
    status = Column(String(50), default="active")  # active, inactive, blocked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    payments = relationship("ContractorPayment", back_populates="contractor")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "contact_info": self.contact_info,
            "skills": self.skills,
            "hourly_rate": self.hourly_rate,
            "project_rate": self.project_rate,
            "rating": self.rating,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ContractorPayment(Base):
    """Модель выплат исполнителям"""
    __tablename__ = "contractor_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    amount = Column(Float, nullable=False)
    payment_type = Column(String(50), default="project")  # hourly, project, bonus
    description = Column(Text, nullable=True)
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")  # pending, paid, cancelled
    payment_method = Column(String(100), nullable=True)  # card, bank_transfer, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    contractor = relationship("Contractor", back_populates="payments")
    project = relationship("Project")
    created_by = relationship("AdminUser")
    
    def to_dict(self):
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "project_id": self.project_id,
            "amount": self.amount,
            "payment_type": self.payment_type,
            "description": self.description,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "status": self.status,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "contractor": self.contractor.to_dict() if self.contractor else None,
            "project": self.project.to_dict() if self.project else None
        }

class ServiceProvider(Base):
    """Модель поставщика услуг (нейросети, хостинг, etc.)"""
    __tablename__ = "service_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    provider_type = Column(String(100), nullable=False)  # ai, hosting, payment, etc.
    website = Column(String(500), nullable=True)
    contact_info = Column(JSON, default=lambda: {})
    pricing_model = Column(String(100), nullable=True)  # monthly, usage, per_request
    status = Column(String(50), default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    expenses = relationship("ServiceExpense", back_populates="service_provider")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "provider_type": self.provider_type,
            "website": self.website,
            "contact_info": self.contact_info,
            "pricing_model": self.pricing_model,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ServiceExpense(Base):
    """Модель расходов на сервисы"""
    __tablename__ = "service_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    service_provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    amount = Column(Float, nullable=False)
    expense_type = Column(String(100), nullable=False)  # subscription, usage, one_time
    description = Column(Text, nullable=True)
    expense_date = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime, nullable=True)  # для подписок
    period_end = Column(DateTime, nullable=True)    # для подписок
    usage_details = Column(JSON, default=lambda: {})  # детали использования
    invoice_url = Column(String(500), nullable=True)
    status = Column(String(50), default="active")  # active, cancelled
    is_recurring = Column(Boolean, default=False)
    recurring_period = Column(String(50), nullable=True)  # monthly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    service_provider = relationship("ServiceProvider", back_populates="expenses")
    project = relationship("Project")
    created_by = relationship("AdminUser")
    
    def to_dict(self):
        return {
            "id": self.id,
            "service_provider_id": self.service_provider_id,
            "project_id": self.project_id,
            "amount": self.amount,
            "expense_type": self.expense_type,
            "description": self.description,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "usage_details": self.usage_details,
            "invoice_url": self.invoice_url,
            "status": self.status,
            "is_recurring": self.is_recurring,
            "recurring_period": self.recurring_period,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "service_provider": self.service_provider.to_dict() if self.service_provider else None,
            "project": self.project.to_dict() if self.project else None
        }

class FinanceReport(Base):
    """Модель финансовых отчетов"""
    __tablename__ = "finance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)  # monthly, quarterly, yearly, custom
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    data = Column(JSON, default=lambda: {})  # данные отчета
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Связи
    created_by = relationship("AdminUser")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "report_type": self.report_type,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

# Модели для системы правок проектов

class ProjectRevision(Base):
    """Модель правок проекта"""
    __tablename__ = "project_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    revision_number = Column(Integer, nullable=False)  # Номер правки
    title = Column(String(500), nullable=False)  # Заголовок правки
    description = Column(Text, nullable=False)  # Описание проблемы
    status = Column(String(50), default="pending")  # pending, in_progress, completed, rejected
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Кто создал правку (клиент)
    assigned_to_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)  # Исполнитель
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # Когда правка была выполнена
    estimated_time = Column(Integer, nullable=True)  # Оценочное время на исправление (в часах)
    actual_time = Column(Integer, nullable=True)  # Фактическое время
    
    # Связи
    project = relationship("Project", back_populates="revisions")
    created_by = relationship("User", back_populates="created_revisions")
    assigned_to = relationship("AdminUser", back_populates="assigned_revisions")
    messages = relationship("RevisionMessage", back_populates="revision")
    files = relationship("RevisionFile", back_populates="revision")
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "revision_number": self.revision_number,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_by_id": self.created_by_id,
            "assigned_to_id": self.assigned_to_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_time": self.estimated_time,
            "actual_time": self.actual_time,
            "created_by": self.created_by.to_dict() if self.created_by else None,
            "assigned_to": self.assigned_to.to_dict() if self.assigned_to else None,
            "messages_count": len(self.messages) if self.messages else 0,
            "files_count": len(self.files) if self.files else 0
        }

class RevisionMessage(Base):
    """Модель сообщений в правках"""
    __tablename__ = "revision_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    revision_id = Column(Integer, ForeignKey("project_revisions.id"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # client, executor, admin
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Если отправитель - клиент
    sender_admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)  # Если отправитель - админ/исполнитель
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Внутреннее сообщение (только для команды)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    revision = relationship("ProjectRevision", back_populates="messages")
    sender_user = relationship("User")
    sender_admin = relationship("AdminUser")
    files = relationship("RevisionMessageFile", back_populates="message")
    
    def to_dict(self):
        sender_name = "Неизвестно"
        if self.sender_type == "client" and self.sender_user:
            sender_name = self.sender_user.first_name or "Клиент"
        elif self.sender_type in ["executor", "admin"] and self.sender_admin:
            sender_name = self.sender_admin.username or "Команда"
            
        return {
            "id": self.id,
            "revision_id": self.revision_id,
            "sender_type": self.sender_type,
            "sender_name": sender_name,
            "message": self.message,
            "is_internal": self.is_internal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "files": [file.to_dict() for file in self.files] if self.files else []
        }

class RevisionFile(Base):
    """Модель файлов правок (скриншоты, документы)"""
    __tablename__ = "revision_files"
    
    id = Column(Integer, primary_key=True, index=True)
    revision_id = Column(Integer, ForeignKey("project_revisions.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)  # image, document, video
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(1000), nullable=False)
    uploaded_by_type = Column(String(20), nullable=False)  # client, executor, admin
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_by_admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    description = Column(Text, nullable=True)  # Описание файла
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    revision = relationship("ProjectRevision", back_populates="files")
    uploaded_by_user = relationship("User")
    uploaded_by_admin = relationship("AdminUser")
    
    def to_dict(self):
        return {
            "id": self.id,
            "revision_id": self.revision_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_path": self.file_path,
            "uploaded_by_type": self.uploaded_by_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class RevisionMessageFile(Base):
    """Модель файлов в сообщениях правок"""
    __tablename__ = "revision_message_files"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("revision_messages.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    message = relationship("RevisionMessage", back_populates="files")
    
    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Модели для системы планировщика задач

class Task(Base):
    """Модель задач для сотрудников"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)  # Заголовок задачи
    description = Column(Text, nullable=True)  # Описание задачи
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    color = Column(String(20), default="normal")  # normal, red, yellow, green - цвет карточки
    
    # Назначение и создание
    assigned_to_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)  # Исполнитель
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)  # Кто создал
    
    # Временные рамки
    deadline = Column(DateTime, nullable=True)  # Дедлайн
    estimated_hours = Column(Integer, nullable=True)  # Оценочное время в часах
    actual_hours = Column(Integer, nullable=True)  # Фактическое время
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # Время завершения
    
    # Дополнительные данные
    task_metadata = Column(JSON, default=lambda: {})  # Дополнительная информация
    
    # Связи
    assigned_to = relationship("AdminUser", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    created_by = relationship("AdminUser", foreign_keys=[created_by_id], back_populates="created_tasks")
    comments = relationship("TaskComment", back_populates="task")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "color": self.color,
            "assigned_to_id": self.assigned_to_id,
            "created_by_id": self.created_by_id,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "task_metadata": self.task_metadata,
            "assigned_to": self.assigned_to.to_dict() if self.assigned_to else None,
            "created_by": self.created_by.to_dict() if self.created_by else None,
            "comments_count": len(self.comments) if self.comments else 0
        }
    
    @property
    def is_overdue(self):
        """Проверить, просрочена ли задача"""
        if self.status == "completed" or not self.deadline:
            return False
        return datetime.utcnow() > self.deadline
    
    @property
    def days_until_deadline(self):
        """Количество дней до дедлайна"""
        if not self.deadline:
            return None
        delta = self.deadline - datetime.utcnow()
        return delta.days
    
    @property
    def comments_count(self):
        """Количество комментариев к задаче"""
        return len(self.comments) if self.comments else 0

class TaskComment(Base):
    """Модель комментариев к задачам"""
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)  # Автор комментария
    comment = Column(Text, nullable=False)  # Текст комментария
    comment_type = Column(String(50), default="general")  # general, status_change, deadline_change
    is_internal = Column(Boolean, default=False)  # Внутренний комментарий (только для команды)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    task = relationship("Task", back_populates="comments")
    author = relationship("AdminUser", back_populates="task_comments")
    
    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "author_id": self.author_id,
            "comment": self.comment,
            "comment_type": self.comment_type,
            "is_internal": self.is_internal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author": self.author.to_dict() if self.author else None
        }

# Модели для системы учета средств с OCR распознаванием чеков

class MoneyTransaction(Base):
    """Модель финансовых транзакций главного админа"""
    __tablename__ = "money_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)  # Сумма
    type = Column(String(20), nullable=False)  # income или expense
    category = Column(String(100), nullable=False)  # Категория транзакции
    description = Column(Text, nullable=True)  # Описание
    date = Column(DateTime, nullable=False)  # Дата транзакции
    
    # OCR данные
    receipt_file_path = Column(String(500), nullable=True)  # Путь к файлу чека
    ocr_data = Column(JSON, default=lambda: {})  # Данные от OCR (сумма, дата, магазин и т.д.)
    is_ocr_processed = Column(Boolean, default=False)  # Обработан ли OCR
    
    # Метаданные
    notes = Column(Text, nullable=True)  # Дополнительные заметки
    source = Column(String(50), default="manual")  # manual, ocr, api
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Связи
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "receipt_file_path": self.receipt_file_path,
            "ocr_data": self.ocr_data,
            "is_ocr_processed": self.is_ocr_processed,
            "notes": self.notes,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

class MoneyCategory(Base):
    """Модель категорий доходов/расходов"""
    __tablename__ = "money_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Название категории
    type = Column(String(20), nullable=False)  # income или expense
    description = Column(Text, nullable=True)  # Описание
    color = Column(String(7), default="#6c757d")  # Цвет для графиков (HEX)
    icon = Column(String(50), default="fas fa-circle")  # FontAwesome иконка
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)  # Порядок сортировки
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Связи
    created_by = relationship("AdminUser", foreign_keys=[created_by_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.to_dict() if self.created_by else None
        }

class ReceiptFile(Base):
    """Модель файлов чеков для OCR обработки"""
    __tablename__ = "receipt_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)  # Имя файла
    original_filename = Column(String(255), nullable=False)  # Оригинальное имя
    file_path = Column(String(500), nullable=False)  # Путь к файлу
    file_size = Column(Integer, nullable=False)  # Размер файла в байтах
    file_type = Column(String(50), nullable=False)  # jpg, png, pdf и т.д.
    
    # OCR статус
    ocr_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    ocr_result = Column(JSON, default=lambda: {})  # Результат OCR
    ocr_confidence = Column(Float, nullable=True)  # Уверенность OCR (0-1)
    ocr_error = Column(Text, nullable=True)  # Ошибка OCR
    
    # Связь с транзакцией
    transaction_id = Column(Integer, ForeignKey("money_transactions.id"), nullable=True)
    
    # Метаданные
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)  # Когда обработан OCR
    uploaded_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Связи
    uploaded_by = relationship("AdminUser", foreign_keys=[uploaded_by_id])
    transaction = relationship("MoneyTransaction", foreign_keys=[transaction_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "ocr_status": self.ocr_status,
            "ocr_result": self.ocr_result,
            "ocr_confidence": self.ocr_confidence,
            "ocr_error": self.ocr_error,
            "transaction_id": self.transaction_id,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "uploaded_by": self.uploaded_by.to_dict() if self.uploaded_by else None
        }

# Обновляем связи существующих моделей
AdminUser.assigned_projects = relationship("Project", back_populates="assigned_executor")
AdminUser.assigned_tasks = relationship("Task", foreign_keys="[Task.assigned_to_id]", back_populates="assigned_to")
AdminUser.created_tasks = relationship("Task", foreign_keys="[Task.created_by_id]", back_populates="created_by")
AdminUser.task_comments = relationship("TaskComment", back_populates="author")
Project.revisions = relationship("ProjectRevision", back_populates="project")
User.created_revisions = relationship("ProjectRevision", back_populates="created_by")

# TODO: Добавить миграцию для этой таблицы
# class AdminActivityLog(Base):
#     """Модель для логирования активности админов и исполнителей"""
#     __tablename__ = "admin_activity_logs"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
#     action = Column(String(100), nullable=False)  # login, logout, view_project, edit_project, etc.
#     action_type = Column(String(50), nullable=False)  # view, create, update, delete
#     entity_type = Column(String(50), nullable=True)  # project, task, user, etc.
#     entity_id = Column(Integer, nullable=True)  # ID сущности
#     details = Column(JSON, nullable=True)  # Дополнительные детали
#     ip_address = Column(String(50), nullable=True)
#     user_agent = Column(String(500), nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     
#     # Связи
#     # user = relationship("AdminUser", back_populates="activity_logs")
#     
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "action": self.action,
#             "action_type": self.action_type,
#             "entity_type": self.entity_type,
#             "entity_id": self.entity_id,
#             "details": self.details,
#             "ip_address": self.ip_address,
#             "user_agent": self.user_agent,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#         }
AdminUser.assigned_revisions = relationship("ProjectRevision", back_populates="assigned_to")