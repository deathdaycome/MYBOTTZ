#!/bin/bash

# Скрипт автоматического деплоя с PM2
# Запускается через webhook или вручную

echo "🚀 Начинаем деплой..."

# Переходим в директорию проекта
cd /root/bot_business_card || exit 1

# Обновляем код из репозитория
echo "📥 Получаем последние изменения..."
git fetch origin
git reset --hard origin/main

# ВАЖНО: Очищаем Python кеш
echo "🧹 Очищаем кеш Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

# Очищаем кеш pip
pip cache purge 2>/dev/null || true

# Обновляем зависимости
echo "📦 Обновляем зависимости..."
source venv/bin/activate
pip install -r requirements.txt --no-cache-dir

# Применяем миграции БД если нужно
echo "🗄️ Проверяем базу данных..."
python3 -c "from app.database.database import init_database; init_database(); print('✅ База данных готова')" || true

# Перезапускаем приложение через PM2
echo "🔄 Перезапускаем приложение..."
pm2 stop bot-business-card
pm2 delete bot-business-card
pm2 start ecosystem.config.js
pm2 save

# Ждем запуска
sleep 5

# Проверяем статус
pm2 status bot-business-card

echo "✅ Деплой завершен!"
echo "📊 Логи: pm2 logs bot-business-card"