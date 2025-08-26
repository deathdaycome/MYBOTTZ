#!/bin/bash
# Скрипт для ручного исправления базы данных на сервере

echo "🔧 Исправляем базу данных на сервере..."
echo "=================================="

# Переходим в директорию проекта
cd /var/www/bot_business_card

# Проверяем где находится база данных
echo "🔍 Ищем базы данных..."
find . -name "*.db" -type f 2>/dev/null

# Список возможных файлов базы данных
DB_FILES=(
    "app.db"
    "data/app.db" 
    "business_card_bot.db"
    "data/business_card_bot.db"
    "bot.db"
    "data/bot.db"
)

# Ищем существующую базу данных
DB_PATH=""
for db_file in "${DB_FILES[@]}"; do
    if [ -f "$db_file" ]; then
        DB_PATH="$db_file"
        echo "✅ База данных найдена: $DB_PATH"
        break
    fi
done

if [ -z "$DB_PATH" ]; then
    echo "❌ База данных не найдена!"
    echo "Создаем новую базу данных: app.db"
    DB_PATH="app.db"
fi

echo "📁 Используем базу данных: $DB_PATH"

# Исправляем базу данных с помощью Python
echo "🔧 Добавляем недостающие колонки..."

python3 << EOF
import sqlite3
import sys

def check_column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def check_table_exists(cursor, table_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

try:
    conn = sqlite3.connect('$DB_PATH')
    cursor = conn.cursor()
    
    print("📊 Проверяем структуру базы данных...")
    
    # Проверяем таблицу clients
    if check_table_exists(cursor, 'clients'):
        print("🔧 Обрабатываем таблицу clients...")
        client_columns = [
            'avito_chat_id',
            'avito_user_id', 
            'avito_status',
            'avito_dialog_history',
            'avito_notes',
            'avito_follow_up',
            'telegram_user_id'
        ]
        
        for column in client_columns:
            if not check_column_exists(cursor, 'clients', column):
                print(f"  ➕ Добавляем clients.{column}")
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {column} TEXT")
            else:
                print(f"  ✅ clients.{column} уже существует")
    else:
        print("⚠️ Таблица clients не найдена")
    
    # Проверяем таблицу leads
    if check_table_exists(cursor, 'leads'):
        print("🔧 Обрабатываем таблицу leads...")
        if not check_column_exists(cursor, 'leads', 'source_type'):
            print("  ➕ Добавляем leads.source_type")
            cursor.execute("ALTER TABLE leads ADD COLUMN source_type TEXT")
        else:
            print("  ✅ leads.source_type уже существует")
    else:
        print("⚠️ Таблица leads не найдена")
    
    # Сохраняем изменения
    conn.commit()
    conn.close()
    
    print("✅ База данных успешно обновлена!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
EOF

echo ""
echo "🚀 Перезапускаем приложение..."
pm2 restart bot-business-card || pm2 restart all

echo ""
echo "✅ Готово! Проверяйте страницы лидов и клиентов."