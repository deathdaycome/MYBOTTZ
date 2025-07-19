#!/bin/bash

# Скрипт запуска бота на сервере TimeWeb
# Использование: ./start_bot.sh

echo "🚀 Запуск Telegram-бота на сервере TimeWeb..."

# Проверка наличия виртуальной среды
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуальной среды..."
    python3 -m venv venv
fi

# Активация виртуальной среды
echo "🔧 Активация виртуальной среды..."
source venv/bin/activate

# Установка зависимостей
echo "📋 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "📝 Создайте файл .env на основе .env.example"
    echo "💡 Скопируйте: cp .env.example .env"
    echo "✏️  Затем отредактируйте .env с вашими настройками"
    exit 1
fi

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p logs
mkdir -p uploads/audio
mkdir -p uploads/documents
mkdir -p uploads/images
mkdir -p uploads/portfolio/main
mkdir -p uploads/portfolio/thumbs
mkdir -p uploads/portfolio/additional
mkdir -p uploads/projects
mkdir -p uploads/revisions/bot
mkdir -p uploads/temp

# Инициализация базы данных (если нужно)
if [ ! -f "data/bot.db" ]; then
    echo "🗄️  Инициализация базы данных..."
    python -c "
from app.database.database import init_db
init_db()
print('База данных инициализирована')
"
fi

# Запуск приложения
echo "🌟 Запуск приложения..."
python run.py
