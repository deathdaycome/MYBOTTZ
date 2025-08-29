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
        "/var/www/bot_business_card/data/bot.db",  # Основная база из конфига
        "/var/www/bot_business_card/admin_panel.db",
        "/var/www/bot_business_card/database.db", 
        "/var/www/bot_business_card/app.db",
        "/var/www/bot_business_card/data/database.db",
        "data/bot.db",
        "admin_panel.db",
        "database.db",
        "app.db"
    ]
    
    print("🔍 Ищем все базы данных...")
    
    # Находим все существующие базы
    existing_dbs = []
    for path in db_paths:
        if os.path.exists(path):
            existing_dbs.append(path)
            print(f"✅ Найдена база: {path}")
    
    if not existing_dbs:
        print("❌ База данных не найдена!")
        return False
    
    # Проверяем каждую базу
    for db_path in existing_dbs:
        print(f"\n🔍 Проверяем базу: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Получаем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"📋 Таблицы в {db_path}: {tables}")
            
            # Если есть таблица admin_users, исправляем её
            if 'admin_users' in tables:
                print(f"🎯 Работаем с таблицей admin_users в {db_path}")
                
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
            
        except Exception as e:
            print(f"❌ Ошибка с базой {db_path}: {e}")
            continue
    
    return True

if __name__ == "__main__":
    print("🚀 Исправление базы данных на сервере")
    success = fix_server_database()
    if success:
        print("✅ Миграция завершена успешно!")
        sys.exit(0)
    else:
        print("❌ Миграция не удалась!")
        sys.exit(1)