#!/bin/bash
# Скрипт для установки переменных окружения Avito на сервере

echo "🔧 Настройка переменных окружения Avito..."

# Читаем значения из локального .env файла
if [ -f ".env" ]; then
    echo "📄 Читаем .env файл..."
    
    # Извлекаем значения
    CLIENT_ID=$(grep "AVITO_CLIENT_ID=" .env | cut -d'=' -f2)
    CLIENT_SECRET=$(grep "AVITO_CLIENT_SECRET=" .env | cut -d'=' -f2)  
    USER_ID=$(grep "AVITO_USER_ID=" .env | cut -d'=' -f2)
    
    echo "🔑 CLIENT_ID: ${CLIENT_ID:0:10}..."
    echo "🔒 CLIENT_SECRET: ***"
    echo "👤 USER_ID: $USER_ID"
    
    # Добавляем переменные в .env для production (если его нет)
    if [ ! -f "/var/www/bot_business_card/.env" ]; then
        echo "📝 Создаем production .env файл..."
        
        cat > /var/www/bot_business_card/.env << EOF
# Avito API Configuration
AVITO_CLIENT_ID=$CLIENT_ID
AVITO_CLIENT_SECRET=$CLIENT_SECRET
AVITO_USER_ID=$USER_ID
EOF
        
        echo "✅ Переменные окружения установлены в /var/www/bot_business_card/.env"
    else
        echo "⚠️ Файл .env уже существует, проверьте его содержимое"
    fi
    
    # Перезапуск сервиса
    echo "🔄 Перезапуск PM2 процесса..."
    pm2 restart bot-busi || echo "⚠️ Не удалось перезапустить PM2"
    
    echo "🎉 Готово! Проверьте логи: pm2 logs bot-busi"
    
else
    echo "❌ Файл .env не найден в текущей директории"
    echo "Пожалуйста, убедитесь что запускаете скрипт из корня проекта"
fi