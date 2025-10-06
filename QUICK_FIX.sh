#!/bin/bash

# 🚨 СКРИПТ СРОЧНОГО ВОССТАНОВЛЕНИЯ БОТА
# Выполните на сервере: bash QUICK_FIX.sh

echo "🚨 НАЧИНАЕМ ВОССТАНОВЛЕНИЕ БОТА..."

# Переходим в директорию проекта
cd /var/www/bot_business_card

echo "📥 Скачиваем последнюю версию кода из GitHub..."
git fetch origin

echo "🔄 ЖЕСТКИЙ СБРОС - удаляем все левые изменения..."
git reset --hard origin/main

echo "📦 Обновляем зависимости (если нужно)..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "🔄 Перезапускаем бота через PM2..."
pm2 restart bot-business-card

echo "⏳ Ждем 3 секунды..."
sleep 3

echo "📋 Показываем логи (последние 30 строк)..."
pm2 logs bot-business-card --lines 30 --nostream

echo ""
echo "✅ ГОТОВО!"
echo ""
echo "🔍 Проверьте бота в Telegram: отправьте /start"
echo ""
echo "⚠️  ОБЯЗАТЕЛЬНО СМЕНИТЕ ПАРОЛЬ АДМИНКИ!"
echo "   nano /var/www/bot_business_card/.env"
echo "   Найдите ADMIN_PASSWORD и поставьте новый пароль"
