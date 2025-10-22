"""
Миграция для добавления статуса прочтения комментариев к задачам
"""
import sqlite3
from pathlib import Path
import json

def run_migration():
    """Выполнить миграцию"""
    db_path = Path("data/bot.db")

    if not db_path.exists():
        print(f"❌ База данных {db_path} не найдена")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("🔄 Запуск миграции: добавление полей is_read и read_by в task_comments")

        # Проверяем существование таблицы
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='task_comments'
        """)

        if not cursor.fetchone():
            print("❌ Таблица task_comments не найдена")
            conn.close()
            return False

        # Проверяем существование колонок
        cursor.execute("PRAGMA table_info(task_comments)")
        columns = [col[1] for col in cursor.fetchall()]

        # Добавляем is_read если не существует
        if 'is_read' not in columns:
            print("📝 Добавляем колонку is_read...")
            cursor.execute("""
                ALTER TABLE task_comments
                ADD COLUMN is_read INTEGER DEFAULT 0
            """)
            print("✅ Колонка is_read добавлена")
        else:
            print("ℹ️  Колонка is_read уже существует")

        # Добавляем read_by если не существует
        if 'read_by' not in columns:
            print("📝 Добавляем колонку read_by...")
            cursor.execute("""
                ALTER TABLE task_comments
                ADD COLUMN read_by TEXT DEFAULT '[]'
            """)
            print("✅ Колонка read_by добавлена")
        else:
            print("ℹ️  Колонка read_by уже существует")

        conn.commit()
        conn.close()

        print("✅ Миграция завершена успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    run_migration()
