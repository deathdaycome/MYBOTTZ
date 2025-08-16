#!/usr/bin/env python3
"""
Миграция для добавления недостающих колонок start_date и planned_end_date в таблицу projects
"""

import sys
import os
import sqlite3
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def upgrade():
    """Добавляем недостающие колонки к таблице projects"""
    print("🔄 Добавляем недостающие колонки в таблицу projects...")
    
    # Подключаемся к базе данных (на сервере путь другой)
    db_paths = ["business_card_bot.db", "data/bot.db", "./data/bot.db"]
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ База данных не найдена в путях: {db_paths}")
        return
    
    print(f"📁 Используем БД: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем текущую структуру таблицы
        cursor.execute("PRAGMA table_info(projects)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print(f"📋 Найдено колонок в таблице projects: {len(existing_columns)}")
        
        # Добавляем start_date если её нет
        if 'start_date' not in existing_columns:
            print("➕ Добавляем колонку start_date...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN start_date DATETIME DEFAULT (datetime('now'))
            """)
            print("✅ Колонка start_date добавлена")
        else:
            print("ℹ️ Колонка start_date уже существует")
            
        # Добавляем planned_end_date если её нет
        if 'planned_end_date' not in existing_columns:
            print("➕ Добавляем колонку planned_end_date...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN planned_end_date DATETIME DEFAULT (datetime('now', '+7 days'))
            """)
            print("✅ Колонка planned_end_date добавлена")
        else:
            print("ℹ️ Колонка planned_end_date уже существует")
            
        # Добавляем actual_end_date если её нет
        if 'actual_end_date' not in existing_columns:
            print("➕ Добавляем колонку actual_end_date...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN actual_end_date DATETIME
            """)
            print("✅ Колонка actual_end_date добавлена")
        else:
            print("ℹ️ Колонка actual_end_date уже существует")
            
        # Проверяем и добавляем другие возможно отсутствующие колонки
        required_columns = {
            'prepayment_amount': 'REAL DEFAULT 0.0',
            'client_paid_total': 'REAL DEFAULT 0.0', 
            'executor_paid_total': 'REAL DEFAULT 0.0',
            'responsible_manager_id': 'INTEGER',
            'assigned_executor_id': 'INTEGER',
            'assigned_at': 'DATETIME'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                print(f"➕ Добавляем колонку {col_name}...")
                cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
                print(f"✅ Колонка {col_name} добавлена")
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

def downgrade():
    """Откат миграции (для SQLite сложно реализовать)"""
    print("⚠️ Откат миграции для SQLite не поддерживается")
    print("Для отката создайте резервную копию базы данных перед миграцией")

if __name__ == "__main__":
    upgrade()