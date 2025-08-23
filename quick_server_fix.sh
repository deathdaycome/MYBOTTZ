#!/bin/bash

# Быстрое исправление Internal Server Error на странице /clients
echo "🔧 Исправление страницы клиентов..."

# 1. Обновляем код
git pull origin main

# 2. Исправляем таблицу 
python3 fix_clients_table.py

# 3. Перезапускаем сервис
if systemctl is-active --quiet bot-admin; then
    sudo systemctl restart bot-admin
    echo "✅ Сервис bot-admin перезапущен"
elif systemctl is-active --quiet nginx; then
    sudo systemctl restart nginx
    echo "✅ Сервис nginx перезапущен"
else
    echo "⚠️  Нужно вручную перезапустить ваш веб-сервис"
fi

echo "🎉 Исправление завершено! Проверьте страницу /clients"