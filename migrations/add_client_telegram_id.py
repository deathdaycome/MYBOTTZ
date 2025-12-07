#!/usr/bin/env python3
"""
Миграция: Добавление Telegram ID клиента в проекты
Дата: 2025-10-24
Описание: Добавляет поле client_telegram_id в таблицу projects для доступа клиента к мини-приложению
"""

import sqlite3
import os
import sys

# Добавляем корневую директорию в PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    """Запуск миграции"""
    db_path = os.environ.get("DATABASE_PATH", "data/bot.db")

    print(f"🔄 Запуск миграции для {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверяем, существует ли уже колонка
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'client_telegram_id' not in columns:
            print("📝 Добавляем колонку client_telegram_id в projects...")
            cursor.execute("""
                ALTER TABLE projects
                ADD COLUMN client_telegram_id VARCHAR(100)
            """)
            conn.commit()
            print("✅ Колонка client_telegram_id добавлена")
        else:
            print("ℹ️  Колонка client_telegram_id уже существует, пропускаем")

        conn.close()
        print("✅ Миграция завершена успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
