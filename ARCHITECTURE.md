# Enterprise CRM - Архитектура системы

## Обзор

Это Enterprise CRM система, построенная по принципам **Modular Monolith** с фокусом на масштабируемость, производительность и надежность.

## Технологический стек

### Backend
- **FastAPI** - современный async веб-фреймворк
- **PostgreSQL 16** - основная СУБД с async драйвером (asyncpg)
- **Redis 7** - кэширование и очереди задач
- **Celery + Flower** - асинхронные фоновые задачи
- **SQLAlchemy 2** - async ORM
- **Alembic** - миграции базы данных
- **Pydantic v2** - валидация данных

### Monitoring & Observability
- **Prometheus** - сбор метрик
- **Grafana** - визуализация
- **Sentry** - отслеживание ошибок
- **Structlog** - структурированное логирование (JSON)
- **OpenTelemetry** - distributed tracing

### Infrastructure
- **Docker Compose** - оркестрация контейнеров
- **Nginx** - reverse proxy (production)

## Архитектура

### Модульная структура (Modular Monolith)

```
app/
├── core/                    # Ядро системы
│   ├── config.py           # Конфигурация (pydantic-settings)
│   ├── database.py         # Async SQLAlchemy setup
│   ├── redis.py            # Redis manager
│   ├── celery_app.py       # Celery configuration
│   ├── logging.py          # Structured logging
│   ├── security.py         # JWT, passwords, RBAC
│   ├── dependencies.py     # FastAPI dependencies
│   └── audit.py            # Audit trail
│
├── modules/                 # Бизнес-модули
│   ├── users/              # Пользователи и аутентификация
│   ├── vehicles/           # Управление автопарком
│   ├── drivers/            # Управление водителями
│   ├── routes/             # Маршруты и точки
│   ├── trips/              # Рейсы и прибыль
│   ├── fuel/               # Топливные карты
│   ├── boxes/              # Управление коробками
│   ├── deliveries/         # Доставки
│   ├── incidents/          # Инциденты
│   ├── calls/              # Звонки и коммуникации
│   ├── analytics/          # Аналитика и отчеты
│   ├── wb/                 # Wildberries интеграция
│   └── tasks_new/          # Управление задачами
│
├── api/                     # API endpoints
│   └── v1/                 # API v1 (версионированный)
│       ├── users.py
│       ├── vehicles.py
│       └── ...
│
├── bot/                     # Telegram Bot
├── admin/                   # Admin Panel (Flask/FastAPI)
└── main.py                  # Application entry point
```

### Принципы модульной архитектуры

1. **Слабая связанность (Loose Coupling)**
   - Модули общаются через чётко определённые интерфейсы
   - Минимизация прямых зависимостей между модулями

2. **Сильная связность (High Cohesion)**
   - Связанная функциональность группируется в одном модуле
   - Каждый модуль имеет единую ответственность

3. **Изолированные модули**
   - Каждый модуль может быть разработан независимо
   - Отдельные тесты для каждого модуля
   - Возможность извлечения в микросервис при необходимости

## Core компоненты

### 1. Configuration (config.py)
```python
from app.core.config import settings

# Доступ к настройкам
database_url = settings.DATABASE_URL
is_production = settings.is_production
```

**Особенности:**
- Pydantic Settings для валидации
- Загрузка из .env файла
- Type hints для всех настроек
- Безопасный вывод (скрытие секретов)

### 2. Database (database.py)
```python
from app.core.database import get_db, Base

# FastAPI dependency
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

**Особенности:**
- Async SQLAlchemy 2
- Connection pooling с оптимизацией
- Автоматический rollback при ошибках
- Health checks
- Transaction decorator

### 3. Logging (logging.py)
```python
from app.core.logging import logger

logger.info("User logged in", user_id=123, action="login")
logger.error("Database error", error=str(e), exc_info=True)
```

**Особенности:**
- Structured logging с structlog
- JSON формат для production
- Correlation ID для трейсинга
- Автоматическое добавление контекста
- Ротация логов

### 4. Security (security.py)
```python
from app.core.security import create_access_token, verify_password

# Create JWT token
token = create_access_token(user_id=123)

# Verify password
is_valid = verify_password(plain_password, hashed_password)
```

**Особенности:**
- JWT authentication
- Bcrypt для паролей
- RBAC (Role-Based Access Control)
- Permission decorators
- Session management

## Database

### PostgreSQL Configuration

**Оптимизации:**
- **Connection Pool**: 20 connections, max overflow 40
- **Prepared Statements**: Ускорение повторяющихся запросов
- **Indexes**: Автоматическое создание для FK и частых запросов
- **WAL**: Write-Ahead Logging для надёжности

### Миграции (Alembic)

```bash
# Создать миграцию
alembic revision --autogenerate -m "Add users table"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## Redis

### Использование

1. **Кэширование**
   - Redis DB 1
   - TTL для автоматического удаления
   - LRU eviction policy

2. **Celery Broker**
   - Redis DB 2
   - Message queue для задач

3. **Session Storage**
   - Redis DB 0
   - Быстрый доступ к сессиям

## Celery

### Фоновые задачи

```python
from app.core.celery_app import celery_app

@celery_app.task
def send_email(user_id: int, subject: str):
    # Отправка email
    pass

# Вызов задачи
send_email.delay(user_id=123, subject="Welcome")
```

**Workers:**
- **celery-worker**: Выполнение задач
- **celery-beat**: Периодические задачи
- **flower**: Мониторинг (http://localhost:5555)

## Monitoring

### Prometheus Metrics

Доступны на `http://localhost:9090/metrics`:

- **HTTP Requests**: Количество, latency, ошибки
- **Database**: Pool size, active connections, query duration
- **Celery**: Task count, success/failure rate
- **Redis**: Commands, memory usage
- **Custom**: Бизнес-метрики

### Grafana Dashboards

Доступны на `http://localhost:3000`:

- **System Overview**: CPU, memory, disk
- **Application Performance**: Request rate, latency, errors
- **Database Performance**: Queries, connections, slow queries
- **Celery Tasks**: Task queue, execution time, failures

## API Versioning

### URL Structure
```
/api/v1/users          # Version 1
/api/v2/users          # Version 2 (будущее)
```

### Deprecation Process
1. Объявить deprecation в v1
2. Добавить warning в response headers
3. Запустить v2 параллельно
4. Миграция клиентов
5. Отключение v1

## Security

### RBAC (Role-Based Access Control)

**Роли:**
- **ADMIN**: Полный доступ ко всему
- **DISPATCHER**: Управление рейсами, маршрутами
- **DRIVER**: Просмотр своих рейсов
- **VIEWER**: Только чтение

**Permissions:**
```python
@router.get("/admin/users")
@requires_role(Role.ADMIN)
async def list_users():
    pass
```

### Audit Log

Все важные действия логируются:
- **Кто**: user_id
- **Что**: action (create, update, delete)
- **Когда**: timestamp
- **Где**: IP address, user agent
- **Изменения**: Before/after values (JSON)

## Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/users")
@limiter.limit("60/minute")
async def get_users():
    pass
```

## Performance

### Optimization Strategies

1. **Database**
   - Connection pooling
   - Query optimization
   - Proper indexes
   - Materialized views

2. **Caching**
   - Redis для частых запросов
   - Cache-aside pattern
   - Cache invalidation

3. **Async Operations**
   - Non-blocking I/O
   - Concurrent requests
   - Background tasks

4. **Load Balancing**
   - Multiple Uvicorn workers
   - Nginx upstream

## Deployment

### Production Checklist

- [ ] Сменить все пароли и секреты
- [ ] Настроить SSL/TLS certificates
- [ ] Включить HTTPS redirect
- [ ] Настроить firewall
- [ ] Включить rate limiting
- [ ] Настроить backup БД
- [ ] Настроить мониторинг
- [ ] Настроить alerting
- [ ] Провести load testing
- [ ] Настроить log aggregation

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache
```

## Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --port 8001
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_users.py
```

## Roadmap

### Phase 1: Foundation (Completed) ✅
- [x] Requirements.txt
- [x] Docker-compose.yml
- [x] Core модуль (config, database, logging)
- [x] Модульная структура директорий

### Phase 2: Infrastructure (In Progress) 🔄
- [ ] Alembic setup
- [ ] Redis integration
- [ ] Celery setup
- [ ] RBAC implementation
- [ ] Audit log

### Phase 3: Modules (Planned) 📋
- [ ] Users module
- [ ] Vehicles module
- [ ] Drivers module
- [ ] Routes module
- [ ] Trips module
- [ ] Fuel module

### Phase 4: Advanced Features (Future) 🚀
- [ ] Real-time notifications (WebSocket)
- [ ] Advanced analytics (ClickHouse)
- [ ] Machine Learning predictions
- [ ] Mobile app integration
- [ ] Multi-tenancy

## Ресурсы

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Celery Docs**: https://docs.celeryq.dev/
- **Prometheus Docs**: https://prometheus.io/docs/

## Контакты

Для вопросов и предложений по архитектуре обращайтесь к команде разработки.
