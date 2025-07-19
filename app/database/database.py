from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
import os
from contextlib import contextmanager
from typing import Generator

from .models import Base
from ..config.settings import settings
from ..config.logging import get_logger

logger = get_logger(__name__)

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Инициализация базы данных"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("База данных инициализирована успешно")
        
        # Добавляем начальные данные
        seed_initial_data()
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection() -> Generator[Session, None, None]:
    """Альтернативная функция для получения сессии БД (для совместимости)"""
    return get_db()

@contextmanager
def get_db_context():
    """Контекстный менеджер для работы с базой данных"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка в транзакции БД: {e}")
        raise
    finally:
        db.close()

def seed_initial_data():
    """Добавление начальных данных"""
    from .models import Settings, FAQ, Portfolio
    
    try:
        with get_db_context() as db:
            # Проверяем, есть ли уже данные
            if db.query(Settings).first():
                return
            
            # Добавляем базовые настройки
            initial_settings = [
                Settings(
                    key="welcome_message",
                    value="👋 Добро пожаловать! Я бот-визитка разработчика ботов. Помогу создать техническое задание для вашего проекта!",
                    description="Приветственное сообщение",
                    data_type="string"
                ),
                Settings(
                    key="company_name",
                    value="BotDev Studio",
                    description="Название компании",
                    data_type="string"
                ),
                Settings(
                    key="contact_email",
                    value="info@botdev.studio",
                    description="Email для связи",
                    data_type="string"
                ),
                Settings(
                    key="contact_phone",
                    value="+7 (999) 123-45-67",
                    description="Телефон для связи",
                    data_type="string"
                ),
                Settings(
                    key="working_hours",
                    value="Пн-Пт 9:00-18:00 (МСК)",
                    description="Рабочие часы",
                    data_type="string"
                )
            ]
            
            for setting in initial_settings:
                db.add(setting)
            
            # Добавляем базовые FAQ
            initial_faq = [
                FAQ(
                    question="Сколько стоит разработка Telegram-бота?",
                    answer="Стоимость зависит от сложности проекта. Простой бот от 10,000₽, средний от 25,000₽, сложный от 50,000₽. Точную стоимость можно рассчитать с помощью калькулятора или создав ТЗ.",
                    category="pricing",
                    sort_order=1
                ),
                FAQ(
                    question="Сколько времени занимает разработка?",
                    answer="Простой бот - 3-7 дней, средний - 1-2 недели, сложный - 2-4 недели. Сроки зависят от функционала и загруженности.",
                    category="timeline",
                    sort_order=2
                ),
                FAQ(
                    question="Предоставляете ли вы техническую поддержку?",
                    answer="Да, предоставляем техническую поддержку и обслуживание ботов. Первый месяц поддержки бесплатно, далее от 2,000₽/месяц.",
                    category="support",
                    sort_order=3
                ),
                FAQ(
                    question="Можете ли интегрировать бота с CRM или другими системами?",
                    answer="Конечно! Интегрируем с популярными CRM (AmoCRM, Bitrix24), платежными системами, базами данных и API сторонних сервисов.",
                    category="integration",
                    sort_order=4
                ),
                FAQ(
                    question="Разрабатываете ли ботов для других платформ?",
                    answer="Да, разрабатываем ботов для Telegram, WhatsApp, ВКонтакте, веб-чатботов для сайтов и голосовых помощников.",
                    category="platforms",
                    sort_order=5
                )
            ]
            
            for faq in initial_faq:
                db.add(faq)
            
            # Добавляем примеры портфолио
            initial_portfolio = [
                Portfolio(
                    title="Бот для интернет-магазина",
                    description="Многофункциональный бот с каталогом товаров, корзиной, оплатой и уведомлениями о заказах",
                    category="telegram_bot",
                    technologies="Python, Telegram Bot API, SQLite, Stripe API",
                    complexity_level=7,
                    development_time=14,
                    cost_range="35000-45000",
                    is_featured=True,
                    sort_order=1
                ),
                Portfolio(
                    title="CRM-бот для управления клиентами",
                    description="Бот для автоматизации работы с клиентами, ведения базы данных и отправки рассылок",
                    category="telegram_bot",
                    technologies="Python, PostgreSQL, Redis, AmoCRM API",
                    complexity_level=8,
                    development_time=21,
                    cost_range="50000-70000",
                    is_featured=True,
                    sort_order=2
                ),
                Portfolio(
                    title="Бот-опросник с аналитикой",
                    description="Интерактивный бот для проведения опросов с детальной аналитикой и экспортом результатов",
                    category="telegram_bot",
                    technologies="Python, Chart.js, Excel API, Google Sheets",
                    complexity_level=6,
                    development_time=10,
                    cost_range="25000-35000",
                    is_featured=False,
                    sort_order=3
                )
            ]
            
            for portfolio_item in initial_portfolio:
                db.add(portfolio_item)
            
            logger.info("Начальные данные добавлены успешно")
            
    except Exception as e:
        logger.error(f"Ошибка при добавлении начальных данных: {e}")
        raise

# Функции для работы с пользователями
def get_or_create_user(db: Session, telegram_id: int, **kwargs):
    """Получить или создать пользователя"""
    from .models import User
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, **kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Создан новый пользователь: {telegram_id}")
    else:
        # Обновляем время последней активности
        user.last_activity = datetime.utcnow()
        db.commit()
    
    return user

def update_user_state(db: Session, telegram_id: int, state: str):
    """Обновить состояние пользователя"""
    from .models import User
    from datetime import datetime
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.state = state
        user.last_activity = datetime.utcnow()
        db.commit()
        return user
    return None

def get_user_by_telegram_id(db: Session, telegram_id: int):
    """Получить пользователя по Telegram ID"""
    from .models import User
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_project(db: Session, user_id: int, project_data: dict):
    """Создать новый проект"""
    from .models import Project, User
    
    # Получаем пользователя для применения его настроек
    user = db.query(User).filter(User.id == user_id).first()
    
    # Создаем проект
    project = Project(user_id=user_id, **project_data)
    
    # Автоматически применяем данные из профиля пользователя
    if user and user.preferences:
        if not project.project_metadata:
            project.project_metadata = {}
        
        # Применяем данные Timeweb
        if 'timeweb_credentials' in user.preferences:
            project.project_metadata['timeweb_credentials'] = user.preferences['timeweb_credentials']
            logger.info(f"Применены данные Timeweb из профиля пользователя {user_id}")
        
        # Применяем API токен бота
        if 'bot_token' in user.preferences:
            project.project_metadata['bot_token'] = user.preferences['bot_token']
            logger.info(f"Применен API токен бота из профиля пользователя {user_id}")
    
    db.add(project)
    db.commit()
    db.refresh(project)
    logger.info(f"Создан новый проект: {project.id} для пользователя {user_id}")
    return project

def get_user_projects(db: Session, user_id: int):
    """Получить проекты пользователя"""
    from .models import Project
    return db.query(Project).filter(Project.user_id == user_id).order_by(Project.created_at.desc()).all()

# Функции для работы с консультантом
def create_consultant_session(db: Session, user_id: int, session_id: str, topic: str = None):
    """Создать сессию консультанта"""
    from .models import ConsultantSession
    from datetime import datetime, timedelta
    
    session = ConsultantSession(
        user_id=user_id,
        session_id=session_id,
        topic=topic,
        expires_at=datetime.utcnow() + timedelta(hours=2)  # Сессия активна 2 часа
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(f"Создана сессия консультанта: {session_id} для пользователя {user_id}")
    return session

def add_consultant_query(db: Session, session_id: int, user_query: str, ai_response: str, tokens_used: int = 0, response_time: float = 0.0):
    """Добавить запрос к консультанту"""
    from .models import ConsultantQuery
    
    query = ConsultantQuery(
        session_id=session_id,
        user_query=user_query,
        ai_response=ai_response,
        tokens_used=tokens_used,
        response_time=response_time
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query