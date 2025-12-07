"""
Миграция: Добавление полей для интеграции с Timeweb Cloud API
Добавляет поля для связи серверов с Timeweb Cloud и автосинхронизации
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config.settings import get_settings

settings = get_settings()


def run_migration():
    """Добавить поля интеграции с Timeweb в таблицу hosting_servers"""

    # Подключаемся к базе данных
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("🔄 Добавление полей интеграции с Timeweb Cloud...")

        try:
            # Проверяем, существует ли таблица
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='hosting_servers'"
            ))
            if not result.fetchone():
                print("⚠️  Таблица hosting_servers не существует, пропускаем миграцию")
                return

            # Получаем список существующих колонок
            result = conn.execute(text("PRAGMA table_info(hosting_servers)"))
            existing_columns = {row[1] for row in result.fetchall()}
            print(f"Существующие колонки: {existing_columns}")

            # Список новых колонок для добавления
            new_columns = {
                "timeweb_id": "INTEGER UNIQUE",
                "timeweb_status": "VARCHAR(50)",
                "timeweb_preset_id": "INTEGER",
                "timeweb_data": "TEXT",
                "auto_sync": "BOOLEAN DEFAULT 0",
                "last_sync_at": "DATETIME"
            }

            added_count = 0

            # Добавляем каждую новую колонку
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    try:
                        conn.execute(text(
                            f"ALTER TABLE hosting_servers ADD COLUMN {column_name} {column_type}"
                        ))
                        conn.commit()
                        print(f"  ✓ Добавлена колонка {column_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"  ✗ Ошибка добавления колонки {column_name}: {e}")
                        conn.rollback()
                else:
                    print(f"  - Колонка {column_name} уже существует")

            # Создаем индекс для timeweb_id если колонка была добавлена
            if "timeweb_id" in new_columns and "timeweb_id" not in existing_columns:
                try:
                    conn.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_hosting_servers_timeweb_id ON hosting_servers(timeweb_id)"
                    ))
                    conn.commit()
                    print("  ✓ Создан индекс для timeweb_id")
                except Exception as e:
                    print(f"  ✗ Ошибка создания индекса: {e}")
                    conn.rollback()

            if added_count > 0:
                print(f"✅ Миграция завершена! Добавлено колонок: {added_count}")
            else:
                print("✅ Все колонки уже существуют, миграция не требуется")

        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    run_migration()
