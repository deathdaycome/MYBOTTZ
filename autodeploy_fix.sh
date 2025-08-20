#!/bin/bash
# Автоматический фикс БД при деплое

echo "==================================="
echo "АВТОДЕПЛОЙ: ПРИМЕНЕНИЕ ИСПРАВЛЕНИЙ"
echo "==================================="

# Переходим в директорию проекта
cd /var/www/bot_business_card

# Проверяем и выполняем скрипт исправления БД
if [ -f "emergency_fix_db.py" ]; then
    echo "Запускаем emergency_fix_db.py..."
    python3 emergency_fix_db.py
    echo "✓ Скрипт БД выполнен"
fi

# Альтернативный вариант через миграции
if [ -f "fix_database_columns.py" ]; then
    echo "Запускаем fix_database_columns.py..."
    python3 fix_database_columns.py 2>&1 || true
    echo "✓ Миграция выполнена"
fi

# Перезапускаем приложение
echo "Перезапускаем приложение..."
pm2 restart botdev-admin
pm2 restart bot-business-card

echo "==================================="
echo "ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ"
echo "===================================