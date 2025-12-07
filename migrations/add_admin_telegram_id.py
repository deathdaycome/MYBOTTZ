#!/usr/bin/env python3
"""
Миграция: Добавление telegram_id в таблицу admin_users
"""
import sqlite3
import os

# Путь к базе данных
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bot.db')

def migrate():
    """Добавление поля telegram_id в таблицу admin_users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли уже колонка
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'telegram_id' not in columns:
            print("Добавление колонки telegram_id в таблицу admin_users...")
            cursor.execute("""
                ALTER TABLE admin_users
                ADD COLUMN telegram_id INTEGER
            """)
            conn.commit()
            print("✅ Колонка telegram_id успешно добавлена в admin_users")
        else:
            print("ℹ️  Колонка telegram_id уже существует в admin_users")

    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
