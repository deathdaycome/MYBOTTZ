#!/usr/bin/env python3
"""
Миграция: Добавление поддержки вложений в комментарии задач
Дата: 2025-10-09
Описание: Добавляет поле attachments в task_comments для хранения скриншотов/файлов
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
        cursor.execute("PRAGMA table_info(task_comments)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'attachments' not in columns:
            print("📝 Добавляем колонку attachments в task_comments...")
            cursor.execute("""
                ALTER TABLE task_comments
                ADD COLUMN attachments JSON DEFAULT '[]'
            """)
            conn.commit()
            print("✅ Колонка attachments добавлена")
        else:
            print("ℹ️  Колонка attachments уже существует, пропускаем")

        # Проверяем таблицу portfolio
        cursor.execute("PRAGMA table_info(portfolio)")
        portfolio_columns = [column[1] for column in cursor.fetchall()]

        missing_columns = []
        if 'is_published' not in portfolio_columns:
            missing_columns.append(('is_published', 'BOOLEAN DEFAULT 0'))
        if 'telegram_message_id' not in portfolio_columns:
            missing_columns.append(('telegram_message_id', 'INTEGER'))
        if 'published_at' not in portfolio_columns:
            missing_columns.append(('published_at', 'DATETIME'))
        if 'telegram_channel_id' not in portfolio_columns:
            missing_columns.append(('telegram_channel_id', 'VARCHAR(100)'))

        if missing_columns:
            print("📝 Добавляем недостающие колонки в portfolio...")
            for col_name, col_type in missing_columns:
                cursor.execute(f"ALTER TABLE portfolio ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Добавлена колонка {col_name}")
            conn.commit()
        else:
            print("ℹ️  Все колонки portfolio уже существуют")

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
