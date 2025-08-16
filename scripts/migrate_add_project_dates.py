#!/usr/bin/env python3
"""
Простая миграция для добавления недостающих колонок в таблицу projects
Используется в GitHub Actions для автоматического обновления базы данных
"""

import sqlite3
import os

def main():
    """Добавляем недостающие колонки к таблице projects"""
    print("🔄 Выполняем миграцию для добавления недостающих колонок...")
    
    # Подключаемся к базе данных
    db_paths = ["business_card_bot.db", "data/bot.db", "./data/bot.db"]
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ База данных не найдена в путях: {db_paths}")
        return
        
    print(f"📁 Используем базу данных: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем текущую структуру таблицы
        cursor.execute("PRAGMA table_info(projects)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print(f"📋 Найдено колонок в таблице projects: {len(existing_columns)}")
        
        # Список колонок для добавления
        columns_to_add = [
            ('start_date', 'DATETIME DEFAULT (datetime(\'now\'))'),
            ('planned_end_date', 'DATETIME DEFAULT (datetime(\'now\', \'+7 days\'))'),
            ('actual_end_date', 'DATETIME'),
            ('prepayment_amount', 'REAL DEFAULT 0.0'),
            ('client_paid_total', 'REAL DEFAULT 0.0'), 
            ('executor_paid_total', 'REAL DEFAULT 0.0'),
            ('responsible_manager_id', 'INTEGER'),
            ('assigned_executor_id', 'INTEGER'),
            ('assigned_at', 'DATETIME')
        ]
        
        # Добавляем каждую колонку если её нет
        for col_name, col_definition in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Добавляем колонку {col_name}...")
                try:
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_definition}")
                    print(f"✅ Колонка {col_name} добавлена")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ Колонка {col_name} уже существует")
                    else:
                        print(f"⚠️ Ошибка добавления колонки {col_name}: {e}")
            else:
                print(f"ℹ️ Колонка {col_name} уже существует")
        
        # Сохраняем изменения
        conn.commit()
        print("✅ Миграция успешно выполнена!")
        
        # Показываем финальную структуру таблицы
        cursor.execute("PRAGMA table_info(projects)")
        final_columns = cursor.fetchall()
        print(f"📋 Итого колонок в таблице projects: {len(final_columns)}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при выполнении миграции: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()