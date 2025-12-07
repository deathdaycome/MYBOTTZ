#!/usr/bin/env python3
"""
Миграция для добавления отсутствующих колонок в employee_notification_settings
Исправляет ошибку: no such column: employee_notification_settings.task_assigned
"""
import sqlite3
import sys
from pathlib import Path

def add_missing_columns():
    """Добавить отсутствующие колонки в таблицу employee_notification_settings"""

    db_path = Path(__file__).parent.parent / "business_card_bot.db"

    if not db_path.exists():
        print(f"❌ База данных не найдена: {db_path}")
        return False

    print(f"📊 Подключение к базе данных: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Получаем текущие колонки
        cursor.execute("PRAGMA table_info(employee_notification_settings)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"✅ Текущие колонки: {existing_columns}")

        # Список новых колонок которые нужно добавить
        new_columns = {
            'task_assigned': ('BOOLEAN', 1),  # (тип, значение по умолчанию)
            'task_reminder': ('BOOLEAN', 1),
            'task_deadline_today': ('BOOLEAN', 1),
            'task_deadline_tomorrow': ('BOOLEAN', 1),
            'task_overdue': ('BOOLEAN', 1),
        }

        added = 0
        for column_name, (column_type, default_value) in new_columns.items():
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE employee_notification_settings ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                    cursor.execute(sql)
                    print(f"✅ Добавлена колонка: {column_name} {column_type}")
                    added += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Ошибка при добавлении {column_name}: {e}")
            else:
                print(f"ℹ️  Колонка {column_name} уже существует")

        conn.commit()
        conn.close()

        if added > 0:
            print(f"\n✅ Успешно добавлено {added} колонок")
        else:
            print(f"\nℹ️  Все колонки уже существуют")

        return True

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_missing_columns()
    sys.exit(0 if success else 1)
