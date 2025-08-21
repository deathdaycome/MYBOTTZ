#!/bin/bash
# Скрипт для поиска и исправления БД на сервере

echo "🔍 Поиск файлов БД..."
echo "----------------------------------------"

# Ищем все .db файлы
find /var/www/bot_business_card -name "*.db" -type f 2>/dev/null | while read -r db_file; do
    echo "Найден: $db_file"
done

find /root -name "*.db" -type f 2>/dev/null | while read -r db_file; do
    echo "Найден: $db_file"
done

echo ""
echo "🔧 Проверка наличия таблицы projects в БД..."
echo "----------------------------------------"

# Проверяем каждую БД
for db_path in /var/www/bot_business_card/*.db /root/*.db /var/www/bot_business_card/data/*.db; do
    if [ -f "$db_path" ]; then
        echo "Проверяем: $db_path"
        # Проверяем есть ли таблица projects
        has_projects=$(sqlite3 "$db_path" "SELECT name FROM sqlite_master WHERE type='table' AND name='projects';" 2>/dev/null)
        if [ "$has_projects" = "projects" ]; then
            echo "  ✓ Найдена таблица projects!"
            echo "  Добавляем недостающие колонки..."
            
            # Добавляем колонки
            sqlite3 "$db_path" "ALTER TABLE projects ADD COLUMN source_deal_id INTEGER;" 2>/dev/null && echo "    + source_deal_id добавлена" || echo "    ℹ source_deal_id уже существует"
            sqlite3 "$db_path" "ALTER TABLE projects ADD COLUMN paid_amount REAL DEFAULT 0.0;" 2>/dev/null && echo "    + paid_amount добавлена" || echo "    ℹ paid_amount уже существует"
            
            # Проверяем другие таблицы
            has_transactions=$(sqlite3 "$db_path" "SELECT name FROM sqlite_master WHERE type='table' AND name='finance_transactions';" 2>/dev/null)
            if [ "$has_transactions" = "finance_transactions" ]; then
                sqlite3 "$db_path" "ALTER TABLE finance_transactions ADD COLUMN account VARCHAR(50) DEFAULT 'card';" 2>/dev/null && echo "    + account добавлена в finance_transactions" || echo "    ℹ account уже существует"
            fi
            
            has_deals=$(sqlite3 "$db_path" "SELECT name FROM sqlite_master WHERE type='table' AND name='deals';" 2>/dev/null)
            if [ "$has_deals" = "deals" ]; then
                sqlite3 "$db_path" "ALTER TABLE deals ADD COLUMN converted_to_project_id INTEGER;" 2>/dev/null && echo "    + converted_to_project_id добавлена в deals" || echo "    ℹ converted_to_project_id уже существует"
            fi
            
            has_leads=$(sqlite3 "$db_path" "SELECT name FROM sqlite_master WHERE type='table' AND name='leads';" 2>/dev/null)
            if [ "$has_leads" = "leads" ]; then
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN source VARCHAR(100);" 2>/dev/null && echo "    + source добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN utm_source VARCHAR(255);" 2>/dev/null && echo "    + utm_source добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN utm_medium VARCHAR(255);" 2>/dev/null && echo "    + utm_medium добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN utm_campaign VARCHAR(255);" 2>/dev/null && echo "    + utm_campaign добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN assigned_to INTEGER;" 2>/dev/null && echo "    + assigned_to добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN last_contact_date DATETIME;" 2>/dev/null && echo "    + last_contact_date добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN conversion_date DATETIME;" 2>/dev/null && echo "    + conversion_date добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN rejection_reason TEXT;" 2>/dev/null && echo "    + rejection_reason добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN budget REAL;" 2>/dev/null && echo "    + budget добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN priority VARCHAR(20) DEFAULT 'normal';" 2>/dev/null && echo "    + priority добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN tags JSON;" 2>/dev/null && echo "    + tags добавлена в leads"
                sqlite3 "$db_path" "ALTER TABLE leads ADD COLUMN notes TEXT;" 2>/dev/null && echo "    + notes добавлена в leads"
            fi
            
            echo "  ✅ БД исправлена: $db_path"
            echo ""
        fi
    fi
done

echo "----------------------------------------"
echo "✅ Проверка завершена!"
echo ""
echo "⚠️  Теперь перезапустите приложение:"
echo "   pm2 restart bot-business-card"