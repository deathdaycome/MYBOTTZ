# Обзор CRM системы

## 📊 Общая информация

**Название**: Enterprise CRM для управления проектами и клиентами
**Технологии**: Python (FastAPI) + React (TypeScript) + SQLite/PostgreSQL
**Сервер**: 147.45.215.199 (Ubuntu, Docker)
**Порты**: 8000 (API + MiniApp), 8001 (Admin Panel)

---

## 🏗️ Архитектура системы

### Локальная версия (разработка)
```
Модульный монолит с полным стеком Enterprise технологий:
├── PostgreSQL 16 (основная СУБД)
├── Redis 7 (кэширование, очереди)
├── Celery + Flower (фоновые задачи)
├── Prometheus + Grafana (мониторинг)
├── Nginx (reverse proxy)
└── Docker Compose (оркестрация)
```

### Серверная версия (production)
```
Упрощённая версия для production:
├── SQLite (база данных)
├── Docker (контейнеризация)
├── FastAPI (Backend API)
├── React Admin Panel
└── Telegram Bot
```

**Путь на сервере**: `/var/www/bot_business_card`
**Docker контейнер**: `bot-business-card`
**База данных**: `/app/data/bot.db` (SQLite)

---

## 📂 Структура Backend (Python/FastAPI)

### Основные модули

```
app/
├── main.py                     # Точка входа приложения
├── admin/                      # Админ панель
│   ├── app.py                 # Главный файл админки (Flask-admin style)
│   ├── navigation.py          # Навигация админки
│   ├── routers/               # API endpoints для админки
│   │   ├── analytics.py       # 📊 Аналитика
│   │   ├── auth.py            # 🔐 Аутентификация
│   │   ├── automation.py      # 🤖 Автоматизация
│   │   ├── avito.py           # 🛒 Интеграция с Avito
│   │   ├── backup.py          # 💾 Бэкапы
│   │   ├── chats.py           # 💬 Чаты
│   │   ├── clients.py         # 👥 Клиенты
│   │   ├── contractors.py     # 🏗️ Подрядчики
│   │   ├── deals.py           # 💼 Сделки
│   │   ├── documents.py       # 📄 Документы
│   │   ├── files.py           # 📁 Управление файлами
│   │   ├── finance.py         # 💰 Финансы
│   │   ├── hosting.py         # 🌐 Хостинг
│   │   ├── leads.py           # 🎯 Лиды
│   │   ├── notifications.py   # 🔔 Уведомления
│   │   ├── permissions_management.py  # 🔒 Управление правами
│   │   ├── portfolio.py       # 🎨 Портфолио
│   │   ├── projects.py        # 📋 Проекты (основной модуль)
│   │   ├── project_statuses.py # ⚡ Статусы проектов
│   │   ├── reports.py         # 📈 Отчёты
│   │   ├── revisions.py       # 🔄 Ревизии
│   │   ├── services.py        # 🛠️ Услуги
│   │   ├── settings.py        # ⚙️ Настройки
│   │   ├── tasks.py           # ✅ Задачи (крупнейший файл - 87KB)
│   │   ├── timlead_regulations.py  # 📜 Регламенты тимлида
│   │   ├── tracking.py        # 📍 Трекинг
│   │   ├── transactions.py    # 💸 Транзакции
│   │   ├── ui_permissions.py  # 🎛️ UI права
│   │   └── users.py           # 👤 Пользователи
│   └── templates/             # HTML шаблоны (старая версия)
├── api/                        # API endpoints
│   ├── miniapp.py             # API для мини-приложения
│   ├── transcription.py       # 🎤 Транскрипция голоса
│   └── voice_assistant.py     # 🗣️ Голосовой ассистент
├── bot/                        # Telegram Bot
│   ├── handlers/              # Обработчики команд
│   ├── keyboards/             # Клавиатуры бота
│   └── main.py                # Запуск бота
├── database/                   # База данных
│   ├── models.py              # Основные модели (79KB)
│   ├── crm_models.py          # CRM модели
│   ├── notification_models.py # Модели уведомлений
│   ├── automation_models.py   # Модели автоматизации
│   ├── audit_models.py        # Модели аудита
│   ├── rbac_models.py         # Role-Based Access Control
│   └── database.py            # Настройка БД
├── services/                   # Бизнес-логика
│   ├── notification_service.py
│   ├── task_notification_service.py
│   ├── task_scheduler.py
│   ├── transcription_service.py
│   └── wialon_service.py
├── integrations/              # Внешние интеграции
│   └── wialon/                # Интеграция с Wialon
├── core/                      # Ядро системы (для Enterprise версии)
│   ├── config.py              # Конфигурация
│   ├── database.py            # Async SQLAlchemy
│   ├── redis.py               # Redis manager
│   ├── celery_app.py          # Celery
│   ├── logging.py             # Логирование
│   └── security.py            # JWT, RBAC
└── static/                    # Статические файлы
```

---

## 🎨 Структура Frontend (React/TypeScript)

### Admin React Panel (admin-react/)

```
admin-react/
├── src/
│   ├── App.tsx                # Главный компонент
│   ├── services/
│   │   └── api.ts             # API клиент (axios)
│   └── pages/                 # Страницы админки
│       ├── Login.tsx          # 🔐 Вход в систему
│       ├── Dashboard.tsx      # 📊 Главная панель
│       ├── DashboardSimple.tsx # 📊 Упрощённая панель
│       ├── Projects.tsx       # 📋 Проекты
│       ├── ProjectFiles.tsx   # 📁 Файлы проекта
│       ├── Tasks.tsx          # ✅ Задачи
│       ├── TasksArchive.tsx   # 🗄️ Архив задач
│       ├── MyTasks.tsx        # 📝 Мои задачи
│       ├── Revisions.tsx      # 🔄 Ревизии
│       ├── Users.tsx          # 👥 Пользователи
│       ├── Clients.tsx        # 👤 Клиенты
│       ├── Contractors.tsx    # 🏗️ Подрядчики
│       ├── Deals.tsx          # 💼 Сделки
│       ├── Finance.tsx        # 💰 Финансы
│       ├── Documents.tsx      # 📄 Документы
│       ├── Portfolio.tsx      # 🎨 Портфолио
│       ├── Services.tsx       # 🛠️ Услуги
│       ├── Analytics.tsx      # 📈 Аналитика
│       ├── Notifications.tsx  # 🔔 Уведомления
│       ├── Avito.tsx          # 🛒 Avito мессенджер
│       ├── Chats.tsx          # 💬 Чаты
│       ├── ChatDetail.tsx     # 💬 Детали чата
│       ├── AICalls.tsx        # 🤖 AI звонки
│       ├── Automation.tsx     # 🤖 Автоматизация
│       ├── Hosting.tsx        # 🌐 Хостинг
│       ├── Transcription.tsx  # 🎤 Транскрипция
│       ├── TimleadRegulations.tsx  # 📜 Регламенты
│       └── Settings.tsx       # ⚙️ Настройки
├── dist/                      # Production build
└── package.json              # Зависимости
```

**Технологии React админки:**
- React 19.1.1
- TypeScript 5.9
- React Router DOM 7.9.5
- Axios (API requests)
- Chart.js + react-chartjs-2 (графики)
- Leaflet + react-leaflet (карты)
- Tailwind CSS (стили)
- Lucide React (иконки)
- GSAP + Motion (анимации)
- Vite 7.1 (сборщик)

### MiniApp (miniapp/)

```
miniapp/
├── src/
│   ├── App.tsx                # Главный компонент
│   ├── api/
│   │   ├── client.ts          # API клиент
│   │   └── chats.ts           # API чатов
│   ├── pages/
│   │   ├── Dashboard.tsx      # Главная
│   │   ├── Projects.tsx       # Проекты
│   │   ├── Chats.tsx          # Чаты
│   │   └── ChatDetail.tsx     # Детали чата
│   └── components/
│       └── Onboarding.tsx     # Онбординг
├── dist/                      # Production build
└── index.html                 # Entry point
```

---

## 💾 База данных

### Основные таблицы (SQLite/PostgreSQL)

**CRM:**
- `clients` - Клиенты
- `leads` - Лиды
- `deals` - Сделки
- `client_tag` - Теги клиентов
- `client_tags` - Связь клиентов и тегов
- `service_catalog` - Каталог услуг
- `deal_services` - Связь сделок и услуг

**Проекты:**
- `projects` - Проекты
- `project_statuses` - Статусы проектов
- `project_files` - Файлы проектов
- `project_chats` - Чаты проектов
- `revisions` - Ревизии проектов
- `tasks` - Задачи
- `task_comments` - Комментарии к задачам

**Финансы:**
- `transactions` - Транзакции
- `finance_categories` - Категории

**Документы:**
- `documents` - Документы
- `document_templates` - Шаблоны документов

**Портфолио:**
- `portfolio` - Элементы портфолио

**Пользователи и права:**
- `users` - Пользователи
- `roles` - Роли
- `permissions` - Права
- `user_roles` - Связь пользователей и ролей
- `role_permissions` - Связь ролей и прав
- `ui_element_permissions` - Права на UI элементы

**Уведомления:**
- `notifications` - Уведомления
- `notification_settings` - Настройки уведомлений
- `notification_types` - Типы уведомлений

**Интеграции:**
- `avito_accounts` - Аккаунты Avito
- `avito_chats` - Чаты Avito
- `avito_messages` - Сообщения Avito

**Автоматизация:**
- `automation_rules` - Правила автоматизации
- `automation_actions` - Действия автоматизации

**Аудит:**
- `audit_log` - Логи действий пользователей

---

## 🔌 API Endpoints

### Backend API структура:

**Аутентификация:**
- `POST /api/login` - Вход
- `POST /api/logout` - Выход
- `GET /api/me` - Текущий пользователь

**Проекты:**
- `GET /api/projects` - Список проектов
- `POST /api/projects` - Создать проект
- `GET /api/projects/{id}` - Детали проекта
- `PUT /api/projects/{id}` - Обновить проект
- `DELETE /api/projects/{id}` - Удалить проект

**Задачи:**
- `GET /api/tasks` - Список задач
- `POST /api/tasks` - Создать задачу
- `GET /api/tasks/{id}` - Детали задачи
- `PUT /api/tasks/{id}` - Обновить задачу
- `DELETE /api/tasks/{id}` - Удалить задачу
- `POST /api/tasks/{id}/comments` - Добавить комментарий

**Клиенты:**
- `GET /api/clients` - Список клиентов
- `POST /api/clients` - Создать клиента
- `GET /api/clients/{id}` - Детали клиента
- `PUT /api/clients/{id}` - Обновить клиента

**Финансы:**
- `GET /api/transactions` - Транзакции
- `POST /api/transactions` - Создать транзакцию
- `GET /api/finance/stats` - Статистика

**Файлы:**
- `POST /api/upload` - Загрузить файл
- `GET /api/files/{id}` - Скачать файл

---

## 🚀 Запуск и развёртывание

### Локальная разработка:

```bash
# Backend
cd /Users/ivan/Desktop/СРМ\ РЕАКТ
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Admin React Panel
cd admin-react
npm install
npm run dev  # http://localhost:5173

# MiniApp
cd miniapp
npm install
npm run dev  # http://localhost:5174
```

### Production (Docker):

```bash
# На сервере
cd /var/www/bot_business_card
docker-compose up -d

# Просмотр логов
docker logs -f bot-business-card

# Рестарт
docker-compose restart

# Пересборка
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔧 Конфигурация

### Переменные окружения (.env):

```env
# Telegram Bot
BOT_TOKEN=your_bot_token
BOT_USERNAME=your_bot_username

# AI Services
OPENROUTER_API_KEY=your_key
OPENAI_API_KEY=your_key

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db

# Admin Panel
ADMIN_SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
ADMIN_PORT=8001

# Security
SECRET_KEY=your_secret
JWT_SECRET_KEY=your_jwt_secret

# Notifications
ADMIN_CHAT_ID=your_telegram_id
NOTIFICATION_CHAT_ID=your_telegram_id

# Avito Integration
AVITO_CLIENT_ID=your_client_id
AVITO_CLIENT_SECRET=your_client_secret
AVITO_USER_ID=your_user_id
```

---

## 📊 Основные функции системы

### 1. Управление проектами 📋
- Создание и отслеживание проектов
- Назначение исполнителей
- Статусы проектов (В работе, Завершён, Отменён)
- Прогресс выполнения
- Файлы и документы проекта

### 2. Система задач ✅
- Kanban доска
- Архив задач
- Комментарии к задачам с файлами
- Уведомления о задачах
- Таймер времени выполнения
- Теги и приоритеты

### 3. CRM 👥
- Клиенты и контакты
- Лиды (потенциальные клиенты)
- Сделки и воронка продаж
- История взаимодействий

### 4. Финансы 💰
- Транзакции (доходы/расходы)
- Категории транзакций
- Финансовая аналитика
- Отчёты по прибыли

### 5. Портфолио 🎨
- Завершённые работы
- Описания и скриншоты
- Публикация в Telegram канал

### 6. Документы 📄
- Шаблоны документов
- Генерация договоров
- Хранилище файлов

### 7. Avito интеграция 🛒
- Чаты с клиентами из Avito
- Автоматические ответы
- История сообщений

### 8. Уведомления 🔔
- Telegram уведомления
- Настройка типов уведомлений
- История уведомлений

### 9. Автоматизация 🤖
- Правила автоматизации
- Триггеры и действия
- Автоответчики

### 10. Аналитика 📈
- Статистика по проектам
- Загрузка сотрудников
- Финансовые отчёты
- Графики и диаграммы

### 11. Права доступа 🔒
- Role-Based Access Control (RBAC)
- Управление ролями
- Детальные права на UI элементы
- Аудит действий пользователей

### 12. Голосовые функции 🎤
- Транскрипция голосовых сообщений
- AI голосовой ассистент
- Обработка звонков

---

## 🔐 Безопасность

- JWT аутентификация
- Хеширование паролей (bcrypt)
- RBAC система прав
- Аудит логирование
- CORS защита
- Rate limiting

---

## 📱 Telegram бот

**Функции:**
- Уведомления о задачах
- Создание задач через бот
- Просмотр проектов
- Голосовой ассистент
- Публикация в портфолио

---

## 🌐 Доступ к системе

**Production сервер:**
- API: http://147.45.215.199:8000
- Admin Panel: http://147.45.215.199:8001
- Документация API: http://147.45.215.199:8000/docs

**Локальная разработка:**
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8001
- React Admin: http://localhost:5173
- MiniApp: http://localhost:5174

---

## 📈 Статус разработки

**Завершённые модули:**
- ✅ Управление проектами
- ✅ Система задач с комментариями
- ✅ CRM (клиенты, лиды, сделки)
- ✅ Финансы и транзакции
- ✅ Портфолио
- ✅ Документы
- ✅ Telegram бот
- ✅ Уведомления
- ✅ Avito интеграция
- ✅ RBAC система прав
- ✅ Аудит логирование
- ✅ Голосовые функции
- ✅ React Admin Panel

**В разработке:**
- 🔄 Миграция на PostgreSQL (для production)
- 🔄 Redis + Celery (фоновые задачи)
- 🔄 Prometheus + Grafana (мониторинг)
- 🔄 Расширенная аналитика

---

## 🛠️ Инструменты разработчика

- **Vite** - сборщик для React
- **TypeScript** - типизация
- **ESLint** - линтер
- **Prettier** - форматирование
- **Docker** - контейнеризация
- **Git** - версионный контроль

---

## 📝 Следующие шаги

1. **Оптимизация:**
   - Миграция на PostgreSQL для production
   - Настройка Redis кэширования
   - Внедрение Celery для тяжёлых операций

2. **Новые функции:**
   - Расширенные отчёты
   - Интеграция с другими платформами
   - Мобильное приложение
   - WebSocket для real-time обновлений

3. **Улучшения UX:**
   - Оптимизация производительности
   - Улучшение дизайна
   - Добавление новых виджетов

---

**Дата создания документа**: 28 ноября 2024
**Версия системы**: 2.0 (Enterprise)
