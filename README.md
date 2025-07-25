# 🤖 Telegram-бот визитка разработчика ботов

Многофункциональный Telegram-бот для автоматизации работы с клиентами, создания технических заданий и управления проектами разработки ботов.

## 🚀 Возможности

### ✨ Основной функционал
- **🤖 AI Консультант** - персональная помощь по вопросам разработки ботов
- **📝 Создание ТЗ** - автоматическое создание технических заданий с помощью ChatGPT
- **💼 Портфолио** - демонстрация готовых работ и проектов
- **📊 Управление проектами** - отслеживание статусов и коммуникация с клиентами
- **🧮 Калькулятор стоимости** - автоматический расчет цены проектов
- **❓ FAQ** - база знаний с ответами на популярные вопросы
- **💬 Консультации** - запись на персональные консультации

### 🧠 AI Консультант
- Персональные ответы на технические вопросы
- Рекомендации по архитектуре и технологиям
- Помощь с ценообразованием и оценкой проектов
- История консультаций с возможностью экспорта
- Оценка качества ответов
- Популярные вопросы с готовыми ответами

### 📋 Создание ТЗ
- Описание проекта текстом
- Голосовые сообщения с распознаванием речи
- Пошаговое создание через вопросы
- Загрузка и анализ документов (PDF, DOC, TXT)
- Структурирование хаотичного описания
- Автоматическая оценка стоимости и сложности

## 🛠 Технологии

- **Python 3.9+** - основной язык разработки
- **python-telegram-bot** - библиотека для работы с Telegram API
- **SQLAlchemy** - ORM для работы с базой данных
- **SQLite** - база данных
- **FastAPI** - веб-фреймворк для админ-панели
- **OpenAI API** - интеграция с ChatGPT через OpenRouter
- **Speech Recognition** - распознавание голосовых сообщений

## 📦 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd bot_business_card
```

### 2. Создание виртуального окружения
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка окружения
Создайте файл `.env` в корне проекта:

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=your_bot_username

# OpenAI/OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3.5-sonnet

# Admin Panel
ADMIN_SECRET_KEY=your_super_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password

# Notifications
NOTIFICATION_CHAT_ID=your_admin_chat_id
```

### 5. Запуск бота
```bash
python run.py
```

## 🏗 Структура проекта

```
bot_business_card/
├── app/
│   ├── bot/                    # Логика бота
│   │   ├── handlers/           # Обработчики команд
│   │   │   ├── start.py        # Стартовые команды
│   │   │   ├── consultant.py   # AI консультант
│   │   │   ├── tz_creation.py  # Создание ТЗ
│   │   │   └── ...
│   │   ├── keyboards/          # Клавиатуры
│   │   └── utils/              # Утилиты бота
│   ├── services/               # Сервисы
│   │   ├── openai_service.py   # Работа с AI
│   │   ├── speech_service.py   # Распознавание речи
│   │   └── ...
│   ├── database/               # База данных
│   │   ├── models.py           # Модели SQLAlchemy
│   │   └── database.py         # Подключение к БД
│   ├── admin/                  # Веб админ-панель
│   └── config/                 # Настройки
├── uploads/                    # Загруженные файлы
├── logs/                       # Логи
├── data/                       # База данных
└── requirements.txt            # Зависимости
```

## 📊 База данных

Основные таблицы:
- **Users** - пользователи бота
- **Projects** - проекты клиентов
- **ConsultantSessions** - сессии AI консультанта
- **ConsultantQueries** - запросы к консультанту
- **Messages** - сообщения и коммуникация
- **Portfolio** - примеры работ
- **FAQ** - часто задаваемые вопросы
- **Settings** - настройки системы

## 🤖 AI Консультант

### Функции консультанта:
- **Технические вопросы** - помощь с архитектурой, выбором технологий
- **Ценообразование** - рекомендации по стоимости проектов
- **Лучшие практики** - советы по разработке и деплою
- **Решение проблем** - помощь с конкретными задачами

### Возможности:
- Сессии с историей разговора
- Оценка качества ответов
- Экспорт консультаций в PDF/TXT
- Популярные вопросы с готовыми ответами
- Персонализированные рекомендации

## 🎯 Использование

### Для клиентов:
1. **Запуск бота** - `/start` для знакомства с возможностями
2. **AI Консультант** - получение персональных рекомендаций
3. **Создание ТЗ** - описание проекта для получения оценки
4. **Просмотр портфолио** - изучение примеров работ
5. **Отслеживание проектов** - контроль статуса заказов

### Для разработчика:
1. **Управление проектами** - изменение статусов, коммуникация
2. **Настройка контента** - обновление портфолио, FAQ
3. **Аналитика** - отчеты по клиентам и проектам
4. **Автоматизация** - AI помощь в создании ТЗ и оценке

## 🔧 Настройка

### Переменные окружения:
- `BOT_TOKEN` - токен Telegram бота от @BotFather
- `OPENROUTER_API_KEY` - ключ для доступа к AI через OpenRouter
- `NOTIFICATION_CHAT_ID` - ID чата для уведомлений админа

### Настройки консультанта:
- `CONSULTANT_SYSTEM_PROMPT` - системный промпт для AI
- `CONSULTANT_MAX_TOKENS` - максимальное количество токенов
- `CONSULTANT_TEMPERATURE` - температура генерации (креативность)

### Ценообразование:
- `BASE_HOURLY_RATE` - базовая стоимость часа работы
- `COMPLEXITY_MULTIPLIERS` - коэффициенты сложности проектов

## 📈 Мониторинг

### Логирование:
- Все действия пользователей
- API вызовы к внешним сервисам
- Ошибки и исключения
- Статистика использования

### Уведомления:
- Новые заявки и проекты
- Ошибки в работе бота
- Статистика активности

## 🚀 Развертывание

### Быстрый старт локально:
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/bot_business_card.git
cd bot_business_card

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование конфигурации
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# Запуск приложения
python -m app.main
```

### Автоматический деплой на Timeweb:

Полное руководство по настройке автоматического деплоя с GitHub Actions смотрите в [DEPLOYMENT.md](DEPLOYMENT.md).

**Кратко:**
1. Настройте сервер: `sudo bash scripts/setup_server.sh`
2. Добавьте GitHub Secrets (SSH ключи, адрес сервера)
3. Push в main ветку - автоматический деплой!

### Docker:
```bash
docker-compose up -d
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения и создайте тесты
4. Отправьте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка

- **Telegram:** @your_username
- **Email:** support@botdev.studio
- **Issues:** GitHub Issues

## 🎉 Благодарности

- Telegram Bot API
- OpenAI/Anthropic за AI модели
- Сообщество разработчиков Python

---

**Создано с ❤️ для автоматизации работы разработчиков ботов**# Production deployment ready
# Fix SSH key
# Auto-deploy test четверг, 24 июля 2025 г. 22:08:58 (MSK)
# Simplified deploy test четверг, 24 июля 2025 г. 22:14:54 (MSK)
# Fix pkill command четверг, 24 июля 2025 г. 22:17:07 (MSK)
# Test new SSH key четверг, 24 июля 2025 г. 22:26:11 (MSK)
# Test ed25519 SSH key четверг, 24 июля 2025 г. 22:39:15 (MSK)
# Test updated SSH key четверг, 24 июля 2025 г. 22:43:30 (MSK)
# Complete deployment script четверг, 24 июля 2025 г. 22:47:20 (MSK)
# Enhanced deployment with fallback четверг, 24 июля 2025 г. 22:51:30 (MSK)
# Final deployment script with run.py четверг, 24 июля 2025 г. 22:54:45 (MSK)
# Switch to webhook deployment четверг, 24 июля 2025 г. 23:02:30 (MSK)
Webhook test via Cloudflare Tunnel пятница, 25 июля 2025 г. 10:39:57 (MSK)
🎉 AUTO-DEPLOY SUCCESS! Webhook working perfectly! пятница, 25 июля 2025 г. 10:43:36 (MSK)
🎉 AUTO-DEPLOY SUCCESS! Webhook working perfectly! пятница, 25 июля 2025 г. 10:44:55 (MSK)
🔄 Deployment trigger test пятница, 25 июля 2025 г. 14:27:15 (MSK)
🛠 Test improved webhook with process management пятница, 25 июля 2025 г. 15:27:30 (MSK)
✅ Test fixed webhook - no self-kill пятница, 25 июля 2025 г. 15:33:00 (MSK)
🔥 Final webhook test - all systems go пятница, 25 июля 2025 г. 15:37:00 (MSK)
🚀 Test improved auto-restart webhook пятница, 25 июля 2025 г. 15:48:00 (MSK)
