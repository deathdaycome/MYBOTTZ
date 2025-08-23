#!/bin/bash

# Скрипт для принудительного деплоя на сервер
echo "🚀 Принудительно обновляем код на сервере..."

# SSH данные
SERVER_HOST="147.45.215.199"
SERVER_USER="root"
SERVER_PORT="22"

# Подключаемся к серверу и обновляем код
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'EOF'
cd /var/www/bot_business_card

echo "📍 Текущая директория: $(pwd)"

# Останавливаем PM2 процесс
echo "🛑 Останавливаем PM2..."
pm2 stop bot-business-card || true

# Обновляем код из репозитория
echo "📥 Получаем последние изменения из GitHub..."
git fetch origin main
git reset --hard origin/main
git clean -fd

# Показываем последний коммит
echo "📝 Последний коммит:"
git log -1 --oneline

# Перезапускаем PM2
echo "🚀 Перезапускаем PM2..."
pm2 start ecosystem.config.js

# Проверяем статус
echo "📊 Статус PM2:"
pm2 status

# Показываем логи
echo "📋 Последние логи:"
pm2 logs bot-business-card --lines 10 --nostream

echo "✅ Принудительный деплой завершен!"
EOF

echo "🎉 Код принудительно обновлен на сервере!"