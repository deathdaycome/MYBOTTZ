#!/bin/bash

# Скрипт для обновления AVITO_USER_ID на сервере

echo "Обновление AVITO_USER_ID на сервере..."

# SSH команда для обновления переменной окружения
ssh root@147.45.215.199 << 'EOF'
    # Переходим в директорию проекта
    cd /root/bot_business_card
    
    # Обновляем AVITO_USER_ID в .env файле
    if grep -q "AVITO_USER_ID=" .env; then
        # Заменяем существующее значение
        sed -i 's/AVITO_USER_ID=.*/AVITO_USER_ID=216012096/' .env
        echo "✓ AVITO_USER_ID обновлен на 216012096"
    else
        # Добавляем новую переменную
        echo "AVITO_USER_ID=216012096" >> .env
        echo "✓ AVITO_USER_ID добавлен: 216012096"
    fi
    
    # Показываем текущее значение для проверки
    echo "Текущее значение:"
    grep "AVITO_USER_ID=" .env
    
    # Перезапускаем приложение через PM2
    echo "Перезапуск приложения..."
    pm2 restart bot-business-card
    pm2 logs bot-business-card --lines 5
EOF

echo "Готово!"