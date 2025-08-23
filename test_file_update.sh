#!/bin/bash

# Простой тест обновления файлов на сервере
echo "🔍 ТЕСТ: Проверяем обновился ли файл avito_messenger.html на сервере..."

SERVER_HOST="147.45.215.199"
SERVER_USER="root"
SERVER_PORT="22"

ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'EOF'
cd /var/www/bot_business_card

echo "📍 Проверяем файл avito_messenger.html:"
echo "🔍 Ищем debug блок с версией v2.0..."

if grep -q "v2.0" app/admin/templates/avito_messenger.html; then
    echo "✅✅✅ УСПЕХ! Файл обновился - найдена версия v2.0!"
    echo "📝 Строка с версией:"
    grep "v2.0" app/admin/templates/avito_messenger.html
else
    echo "❌❌❌ ОШИБКА! Файл всё ещё не обновился!"
    echo "📝 Показываем первые 15 строк файла:"
    head -15 app/admin/templates/avito_messenger.html
fi

echo ""
echo "📊 Информация о файле:"
echo "Размер: $(wc -c < app/admin/templates/avito_messenger.html) bytes"
echo "Последнее изменение: $(stat -c %y app/admin/templates/avito_messenger.html)"

echo ""
echo "📝 Последний git коммит:"
git log -1 --oneline
EOF