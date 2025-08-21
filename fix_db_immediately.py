#!/usr/bin/env python3
"""
Скрипт для немедленного исправления БД на сервере
Запускается вручную для исправления проблем с колонками
"""

import sqlite3
import os
import sys

def fix_database():
    """Исправляем БД немедленно"""
    # Проверяем несколько возможных путей к БД
    possible_paths = [
        "admin_panel.db",
        "/var/www/bot_business_card/admin_panel.db",
        "/root/bot_business_card/admin_panel.db",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_panel.db")
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✓ Найдена база данных: {db_path}")
            break
    
    if not db_path:
        print(f"✗ База данных не найдена ни по одному из путей: {possible_paths}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Список необходимых колонок
        required_columns = {
            'projects': [
                ('source_deal_id', 'INTEGER'),
                ('paid_amount', 'REAL DEFAULT 0.0')
            ],
            'finance_transactions': [
                ('account', "VARCHAR(50) DEFAULT 'card'")
            ],
            'deals': [
                ('converted_to_project_id', 'INTEGER')
            ],
            'leads': [
                ('source', "VARCHAR(100)"),
                ('utm_source', "VARCHAR(255)"),
                ('utm_medium', "VARCHAR(255)"),
                ('utm_campaign', "VARCHAR(255)"),
                ('assigned_to', 'INTEGER'),
                ('last_contact_date', 'DATETIME'),
                ('conversion_date', 'DATETIME'),
                ('rejection_reason', 'TEXT'),
                ('budget', 'REAL'),
                ('priority', "VARCHAR(20) DEFAULT 'normal'"),
                ('tags', 'JSON'),
                ('notes', 'TEXT')
            ]
        }
        
        fixes_applied = 0
        
        for table_name, columns in required_columns.items():
            # Проверяем существование таблицы
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"ℹ Таблица {table_name} не существует, пропускаем")
                continue
            
            # Получаем существующие колонки
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # Добавляем недостающие колонки
            for col_name, col_type in columns:
                if col_name not in existing_columns:
                    print(f"+ Добавляем колонку {col_name} в таблицу {table_name}")
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                        print(f"  ✓ Колонка {col_name} добавлена в {table_name}")
                        fixes_applied += 1
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            print(f"  ℹ Колонка {col_name} уже существует в {table_name}")
                        else:
                            print(f"  ✗ Ошибка добавления колонки {col_name}: {e}")
                else:
                    print(f"  ✓ Колонка {col_name} уже существует в {table_name}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Проверка завершена. Применено исправлений: {fixes_applied}")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при проверке БД: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Запуск исправления БД...")
    print("-" * 50)
    success = fix_database()
    print("-" * 50)
    if success:
        print("✅ Исправление завершено успешно!")
        print("\n⚠️  ВАЖНО: Перезапустите приложение командой:")
        print("   pm2 restart bot-business-card")
    else:
        print("✗ Исправление завершено с ошибками")
        sys.exit(1)