"""
Миграция: Добавление прогресс-бара и таймера для правок
Дата: 2025-10-10
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Выполнение миграции"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'admin_panel.db')

    print(f"Подключение к БД: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Проверяем существующие колонки
        cursor.execute("PRAGMA table_info(project_revisions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Существующие колонки: {existing_columns}")

        # Добавляем progress если его нет
        if 'progress' not in existing_columns:
            print("Добавление колонки progress...")
            cursor.execute("""
                ALTER TABLE project_revisions
                ADD COLUMN progress INTEGER DEFAULT 0
            """)
            print("✓ Колонка progress добавлена")
        else:
            print("✓ Колонка progress уже существует")

        # Добавляем time_spent_seconds если его нет
        if 'time_spent_seconds' not in existing_columns:
            print("Добавление колонки time_spent_seconds...")
            cursor.execute("""
                ALTER TABLE project_revisions
                ADD COLUMN time_spent_seconds INTEGER DEFAULT 0
            """)
            print("✓ Колонка time_spent_seconds добавлена")
        else:
            print("✓ Колонка time_spent_seconds уже существует")

        # Добавляем timer_started_at если его нет
        if 'timer_started_at' not in existing_columns:
            print("Добавление колонки timer_started_at...")
            cursor.execute("""
                ALTER TABLE project_revisions
                ADD COLUMN timer_started_at DATETIME
            """)
            print("✓ Колонка timer_started_at добавлена")
        else:
            print("✓ Колонка timer_started_at уже существует")

        conn.commit()
        print("\n✅ Миграция выполнена успешно!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Ошибка при выполнении миграции: {e}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
