#!/usr/bin/env python3
"""
Скрипт для миграции базы данных - добавляет недостающие колонки
"""

import sqlite3
import os
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

def add_column_if_not_exists(cursor, table_name, column_name, column_type):
    """Добавляет колонку в таблицу, если она еще не существует"""
    # Проверяем существование колонки
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    
    if column_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            print(f"✅ Добавлена колонка {column_name} в таблицу {table_name}")
            return True
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"ℹ️ Колонка {column_name} уже существует в таблице {table_name}")
            else:
                print(f"❌ Ошибка при добавлении колонки {column_name}: {e}")
            return False
    else:
        print(f"ℹ️ Колонка {column_name} уже существует в таблице {table_name}")
        return False

def migrate_database(db_path):
    """Выполняет миграцию базы данных"""
    print(f"🔄 Начинаем миграцию базы данных: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем существование таблицы projects
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            print("❌ Таблица projects не найдена")
            return False
        
        # Добавляем колонку color в таблицу projects
        add_column_if_not_exists(cursor, "projects", "color", "VARCHAR(20) DEFAULT 'default'")
        
        # Добавляем другие недостающие колонки если нужно
        # add_column_if_not_exists(cursor, "admin_users", "password_hash", "VARCHAR(255)")
        
        conn.commit()
        print("✅ Миграция завершена успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    # Определяем путь к базе данных
    db_paths = [
        "business_card_bot.db",
        "../business_card_bot.db",
        "data/bot.db",
        "../data/bot.db"
    ]
    
    db_found = False
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"📁 Найдена база данных: {db_path}")
            if migrate_database(db_path):
                db_found = True
                break
    
    if not db_found:
        print("❌ База данных не найдена ни в одном из стандартных путей")
        print("Проверенные пути:", db_paths)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())