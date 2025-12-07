"""
Миграция: Добавление поля progress в таблицу projects
Дата: 2025-12-07
"""

import sqlite3
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate(db_path='/app/data/bot.db'):
    """Применить миграцию для добавления поля progress"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Начинаем миграцию: добавление поля progress...")

        # Проверяем существование колонки
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'progress' not in columns:
            cursor.execute('ALTER TABLE projects ADD COLUMN progress INTEGER DEFAULT 0')
            print("  ✅ Добавлено поле progress")
        else:
            print("  ℹ️  Поле progress уже существует")

        conn.commit()
        print("✅ Миграция успешно применена!")

        # Обновляем прогресс существующих проектов
        print("\n🔄 Расчёт прогресса для существующих проектов...")

        from app.services.project_progress_service import update_all_projects_progress
        count = update_all_projects_progress(db_path)

        print(f"✅ Обновлено проектов: {count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка миграции: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Определяем путь к БД в зависимости от окружения
    if os.path.exists('/app/data/bot.db'):
        db_path = '/app/data/bot.db'
    elif os.path.exists('data/bot.db'):
        db_path = 'data/bot.db'
    else:
        db_path = '/app/data/bot.db'

    migrate(db_path)
