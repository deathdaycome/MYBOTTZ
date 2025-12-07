#!/usr/bin/env python3
"""
Миграция: Добавление полей is_read и read_by в таблицу task_comments
"""
import sqlite3
import os

# Путь к базе данных
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bot.db')

def migrate():
    """Добавление полей is_read и read_by в таблицу task_comments"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли уже колонка is_read
        cursor.execute("PRAGMA table_info(task_comments)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'is_read' not in columns:
            print("Добавление колонки is_read в таблицу task_comments...")
            cursor.execute("""
                ALTER TABLE task_comments
                ADD COLUMN is_read BOOLEAN DEFAULT 0
            """)
            conn.commit()
            print("✅ Колонка is_read успешно добавлена в task_comments")
        else:
            print("ℹ️  Колонка is_read уже существует в task_comments")

        if 'read_by' not in columns:
            print("Добавление колонки read_by в таблицу task_comments...")
            cursor.execute("""
                ALTER TABLE task_comments
                ADD COLUMN read_by TEXT
            """)
            conn.commit()
            print("✅ Колонка read_by успешно добавлена в task_comments")
        else:
            print("ℹ️  Колонка read_by уже существует в task_comments")

    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
