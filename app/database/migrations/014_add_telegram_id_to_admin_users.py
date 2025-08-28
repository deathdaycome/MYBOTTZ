#!/usr/bin/env python3
"""
Миграция для добавления telegram_id в таблицу admin_users
"""

import sqlite3
import os

def migrate():
    """Добавляет telegram_id в таблицу admin_users"""
    
    # Определяем путь к базе данных
    db_path = "/Users/ivan/Downloads/bot_business_card 2/admin_panel.db"
    
    if not os.path.exists(db_path):
        print(f"База данных не найдена: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже колонка telegram_id
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'telegram_id' not in columns:
            print("Добавляем колонку telegram_id...")
            cursor.execute("""
                ALTER TABLE admin_users 
                ADD COLUMN telegram_id BIGINT DEFAULT NULL
            """)
            
            # Создаем индекс для telegram_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_admin_users_telegram_id 
                ON admin_users(telegram_id)
            """)
            
            conn.commit()
            print("✅ Колонка telegram_id успешно добавлена в admin_users")
        else:
            print("ℹ️  Колонка telegram_id уже существует")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False

if __name__ == "__main__":
    migrate()