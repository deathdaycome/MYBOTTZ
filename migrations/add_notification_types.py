"""
Миграция для добавления новых типов уведомлений
Добавляет поля для задач, правок и чатов
"""

import sqlite3
import sys
from pathlib import Path

# Добавляем корневую директорию в path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.logging import get_logger

logger = get_logger(__name__)

def run_migration():
    """Выполнить миграцию"""
    db_path = root_dir / "data" / "bot.db"

    if not db_path.exists():
        logger.error(f"База данных не найдена: {db_path}")
        return False

    logger.info(f"Подключаемся к БД: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        logger.info("Проверяем структуру таблицы employee_notification_settings...")

        # Проверяем существующие столбцы
        cursor.execute("PRAGMA table_info(employee_notification_settings)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        logger.info(f"Найдено существующих столбцов: {len(existing_columns)}")

        # Список новых столбцов для добавления
        new_columns = [
            # Задачи
            ("task_assigned", "BOOLEAN", "1"),
            ("task_status_changed", "BOOLEAN", "1"),
            ("task_deadline_reminder", "BOOLEAN", "1"),
            ("task_comment_added", "BOOLEAN", "1"),

            # Правки
            ("revision_new", "BOOLEAN", "1"),
            ("revision_status_changed", "BOOLEAN", "1"),
            ("revision_message_new", "BOOLEAN", "1"),

            # Чаты
            ("project_chat_new_message", "BOOLEAN", "1"),
        ]

        # Добавляем столбцы, если их еще нет
        added_count = 0
        for column_name, column_type, default_value in new_columns:
            if column_name not in existing_columns:
                logger.info(f"Добавляем столбец: {column_name}")
                cursor.execute(
                    f"ALTER TABLE employee_notification_settings ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                )
                added_count += 1
            else:
                logger.info(f"Столбец {column_name} уже существует, пропускаем")

        conn.commit()
        logger.info(f"✅ Миграция успешно выполнена! Добавлено столбцов: {added_count}")

        # Проверяем обновленную структуру
        cursor.execute("PRAGMA table_info(employee_notification_settings)")
        all_columns = cursor.fetchall()
        logger.info(f"Всего столбцов в таблице после миграции: {len(all_columns)}")

        return True

    except sqlite3.Error as e:
        logger.error(f"Ошибка при выполнении миграции: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("МИГРАЦИЯ: Добавление новых типов уведомлений")
    logger.info("=" * 60)

    success = run_migration()

    if success:
        logger.info("=" * 60)
        logger.info("МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("МИГРАЦИЯ ЗАВЕРШИЛАСЬ С ОШИБКОЙ!")
        logger.error("=" * 60)
        sys.exit(1)
