#!/usr/bin/env python3
"""
ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ
Запускать на сервере: python3 emergency_fix_db.py
"""

import sqlite3
import os
import sys

# Путь к базе данных
DB_PATH = "db.sqlite"

def fix_database():
    """Добавляем недостающие колонки напрямую через sqlite3"""
    print("="*60)
    print("ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ")
    print("="*60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных не найдена: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Получаем список колонок в таблице projects
        cursor.execute("PRAGMA table_info(projects)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Существующие колонки в projects: {', '.join(column_names)}")
        
        # 1. Добавляем source_deal_id если его нет
        if 'source_deal_id' not in column_names:
            print("➜ Добавляем source_deal_id в projects...")
            cursor.execute("ALTER TABLE projects ADD COLUMN source_deal_id INTEGER")
            print("✅ source_deal_id добавлен")
        else:
            print("✓ source_deal_id уже существует")
        
        # 2. Добавляем paid_amount если его нет
        if 'paid_amount' not in column_names:
            print("➜ Добавляем paid_amount в projects...")
            cursor.execute("ALTER TABLE projects ADD COLUMN paid_amount REAL DEFAULT 0.0")
            print("✅ paid_amount добавлен")
        else:
            print("✓ paid_amount уже существует")
        
        # Проверяем таблицу finance_transactions
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finance_transactions'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(finance_transactions)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"\nСуществующие колонки в finance_transactions: {', '.join(column_names)}")
            
            # 3. Добавляем account если его нет
            if 'account' not in column_names:
                print("➜ Добавляем account в finance_transactions...")
                cursor.execute("ALTER TABLE finance_transactions ADD COLUMN account VARCHAR(50) DEFAULT 'card'")
                print("✅ account добавлен")
            else:
                print("✓ account уже существует")
        else:
            print("⚠️ Таблица finance_transactions не найдена")
        
        # Проверяем таблицу deals
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deals'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(deals)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"\nСуществующие колонки в deals: {', '.join(column_names)}")
            
            # 4. Добавляем converted_to_project_id если его нет
            if 'converted_to_project_id' not in column_names:
                print("➜ Добавляем converted_to_project_id в deals...")
                cursor.execute("ALTER TABLE deals ADD COLUMN converted_to_project_id INTEGER")
                print("✅ converted_to_project_id добавлен")
            else:
                print("✓ converted_to_project_id уже существует")
        else:
            print("⚠️ Таблица deals не найдена")
        
        # Сохраняем изменения
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("="*60)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = fix_database()
    sys.exit(0 if success else 1)