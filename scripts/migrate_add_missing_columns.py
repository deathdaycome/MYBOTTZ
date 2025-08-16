#!/usr/bin/env python3
"""
Миграция для добавления отсутствующих колонок в таблицу projects на сервере
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Добавляет недостающие колонки в таблицу projects"""
    
    # Пути к базе данных
    db_paths = [
        '/var/www/bot_business_card/data/bot.db',
        '/var/www/bot_business_card/business_card_bot.db',
        './data/bot.db',
        './business_card_bot.db',
        'data/bot.db',
        'business_card_bot.db'
    ]
    
    # Находим существующую базу данных
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ База данных не найдена!")
        return False
    
    print(f"📁 Используем базу данных: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем список существующих колонок
        cursor.execute("PRAGMA table_info(projects)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"📋 Найдено колонок в таблице projects: {len(existing_columns)}")
        
        # Список колонок для добавления с их типами
        columns_to_add = [
            ('start_date', 'DATETIME'),
            ('planned_end_date', 'DATETIME'),
            ('actual_end_date', 'DATETIME'),
            ('prepayment_amount', 'REAL'),
            ('client_paid_total', 'REAL'),
            ('executor_paid_total', 'REAL'),
            ('responsible_manager_id', 'INTEGER'),
            ('assigned_executor_id', 'INTEGER'),
            ('assigned_at', 'DATETIME')
        ]
        
        # Добавляем недостающие колонки
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    query = f"ALTER TABLE projects ADD COLUMN {column_name} {column_type}"
                    cursor.execute(query)
                    print(f"✅ Добавлена колонка {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ Колонка {column_name} уже существует")
                    else:
                        print(f"❌ Ошибка при добавлении колонки {column_name}: {e}")
            else:
                print(f"ℹ️ Колонка {column_name} уже существует")
        
        conn.commit()
        
        # Проверяем итоговое количество колонок
        cursor.execute("PRAGMA table_info(projects)")
        final_columns = cursor.fetchall()
        print(f"📋 Итого колонок в таблице projects: {len(final_columns)}")
        
        conn.close()
        print("✅ Миграция успешно выполнена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        return False

if __name__ == "__main__":
    migrate_database()