#!/usr/bin/env python3
"""
Скрипт для исправления отсутствующих колонок в базе данных на сервере
Исправляет ошибки: no such column: clients.avito_chat_id и leads.source_type
"""

import sqlite3
import os
import sys
from datetime import datetime

def get_database_path():
    """Найти путь к базе данных"""
    possible_paths = [
        "app.db",
        "data/app.db",
        "/var/www/bot_business_card/app.db",
        "/var/www/bot_business_card/data/app.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return "app.db"  # Создаст новую если не найдена

def check_column_exists(cursor, table_name, column_name):
    """Проверить существование колонки"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def main():
    """Исправить базу данных"""
    print("🔧 Исправляем ошибки базы данных на сервере...")
    print("=" * 60)
    
    db_path = get_database_path()
    print(f"📁 База данных: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        sys.exit(1)
    
    try:
        # Подключение к базе
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Исправления для таблицы clients
        print("\n🔧 Проверяем таблицу clients...")
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
                print(f"➕ Добавляем clients.{column}")
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {column} TEXT")
            else:
                print(f"✅ clients.{column} уже существует")
        
        # Исправления для таблицы leads
        print("\n🔧 Проверяем таблицу leads...")
        if not check_column_exists(cursor, 'leads', 'source_type'):
            print("➕ Добавляем leads.source_type")
            cursor.execute("ALTER TABLE leads ADD COLUMN source_type TEXT")
        else:
            print("✅ leads.source_type уже существует")
        
        # Сохраняем изменения
        conn.commit()
        conn.close()
        
        print(f"\n✅ База данных успешно исправлена!")
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🚀 Теперь страницы лидов и клиентов должны работать!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()