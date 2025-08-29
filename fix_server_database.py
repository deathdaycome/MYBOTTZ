#!/usr/bin/env python3
"""
Скрипт для исправления базы данных на сервере - добавление telegram_id в admin_users
"""

import sqlite3
import os
import sys

def fix_server_database():
    """Исправляет базу данных на сервере"""
    
    # Пути к возможным базам данных
    db_paths = [
        "/var/www/bot_business_card/admin_panel.db",
        "/var/www/bot_business_card/database.db", 
        "/var/www/bot_business_card/app.db",
        "admin_panel.db",
        "database.db",
        "app.db"
    ]
    
    print("🔍 Ищем базу данных...")
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✅ Найдена база: {path}")
            break
    
    if not db_path:
        print("❌ База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы admin_users
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Колонки в admin_users: {columns}")
        
        if 'telegram_id' not in columns:
            print("➕ Добавляем колонку telegram_id...")
            cursor.execute("""
                ALTER TABLE admin_users 
                ADD COLUMN telegram_id BIGINT DEFAULT NULL
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_admin_users_telegram_id 
                ON admin_users(telegram_id)
            """)
            
            conn.commit()
            print("✅ Колонка telegram_id добавлена!")
        else:
            print("ℹ️  Колонка telegram_id уже существует")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(admin_users)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Финальные колонки: {final_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Исправление базы данных на сервере")
    success = fix_server_database()
    if success:
        print("✅ Миграция завершена успешно!")
        sys.exit(0)
    else:
        print("❌ Миграция не удалась!")
        sys.exit(1)