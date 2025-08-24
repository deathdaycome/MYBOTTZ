#!/bin/bash

# Быстрая проверка Avito сообщений - одна команда
echo "🔍 Быстрая проверка Avito сообщений..."

# Определяем директорию проекта
if [ -d "/var/www/bot_business_card" ]; then
    PROJECT_DIR="/var/www/bot_business_card"
elif [ -d "/opt/bot_business_card" ]; then
    PROJECT_DIR="/opt/bot_business_card"
elif [ -d "./app" ]; then
    PROJECT_DIR="."
else
    echo "❌ Не найдена директория проекта!"
    echo "Попробуйте запустить из директории проекта или укажите путь:"
    echo "cd /path/to/project && ./quick_avito_check.sh"
    exit 1
fi

echo "📂 Директория проекта: $PROJECT_DIR"
cd "$PROJECT_DIR"

# Проверяем наличие скрипта
if [ ! -f "avito_stats.py" ]; then
    echo "❌ Файл avito_stats.py не найден!"
    echo "Убедитесь, что вы в правильной директории или обновите код:"
    echo "git pull origin main"
    exit 1
fi

# Запускаем проверку
echo "🚀 Запуск проверки..."
python3 avito_stats.py

echo ""
echo "💡 Для подробной проверки используйте:"
echo "   python3 check_messages.py"
echo "   python3 test_avito_messages.py"