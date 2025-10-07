"""
Миграция: Добавление полей progress, time_spent_seconds и timer_started_at в таблицу tasks
"""
import sqlite3
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import get_settings

settings = get_settings()

def migrate():
    """Добавить новые поля в таблицу tasks"""

    # Извлекаем путь к БД из DATABASE_URL
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')

    print(f"Подключение к БД: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Проверяем существование колонок
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]

        print(f"Текущие колонки в tasks: {columns}")

        # Добавляем progress если его нет
        if 'progress' not in columns:
            print("Добавляем колонку 'progress'...")
            cursor.execute("ALTER TABLE tasks ADD COLUMN progress INTEGER DEFAULT 0")
            print("✅ Колонка 'progress' добавлена")
        else:
            print("ℹ️  Колонка 'progress' уже существует")

        # Добавляем time_spent_seconds если его нет
        if 'time_spent_seconds' not in columns:
            print("Добавляем колонку 'time_spent_seconds'...")
            cursor.execute("ALTER TABLE tasks ADD COLUMN time_spent_seconds INTEGER DEFAULT 0")
            print("✅ Колонка 'time_spent_seconds' добавлена")
        else:
            print("ℹ️  Колонка 'time_spent_seconds' уже существует")

        # Добавляем timer_started_at если его нет
        if 'timer_started_at' not in columns:
            print("Добавляем колонку 'timer_started_at'...")
            cursor.execute("ALTER TABLE tasks ADD COLUMN timer_started_at DATETIME NULL")
            print("✅ Колонка 'timer_started_at' добавлена")
        else:
            print("ℹ️  Колонка 'timer_started_at' уже существует")

        conn.commit()
        print("\n🎉 Миграция успешно выполнена!")

    except Exception as e:
        print(f"\n❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
