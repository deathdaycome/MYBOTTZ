#!/usr/bin/env python3
"""
Миграция: Добавление поля deploy_url в таблицу tasks
Дата: 2025-01-18
Описание: Добавляет поле для хранения ссылки на задеплоенное приложение
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/bot.db")

# Конвертируем async драйверы в синхронные для миграции
if "aiosqlite" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)


def upgrade():
    """Добавить колонку deploy_url в таблицу tasks"""
    print("🔄 Добавление поля deploy_url в таблицу tasks...")

    with engine.connect() as conn:
        try:
            # Check if column already exists
            if "sqlite" in DATABASE_URL:
                result = conn.execute(text("PRAGMA table_info(tasks)"))
                columns = [row[1] for row in result.fetchall()]
            else:  # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'tasks'
                """))
                columns = [row[0] for row in result.fetchall()]

            if 'deploy_url' in columns:
                print("✅ Column 'deploy_url' already exists, skipping...")
                return

            # Add deploy_url column
            if "sqlite" in DATABASE_URL:
                conn.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN deploy_url VARCHAR(1000)
                """))
            else:  # PostgreSQL
                conn.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN IF NOT EXISTS deploy_url VARCHAR(1000)
                """))

            conn.commit()
            print("✅ Поле deploy_url успешно добавлено в таблицу tasks")

        except Exception as e:
            print(f"❌ Ошибка при выполнении миграции: {e}")
            conn.rollback()
            raise


def downgrade():
    """Удалить колонку deploy_url из таблицы tasks"""
    print("🔄 Удаление поля deploy_url из таблицы tasks...")

    with engine.connect() as conn:
        try:
            if "sqlite" in DATABASE_URL:
                print("⚠️  SQLite не поддерживает DROP COLUMN, откат невозможен")
                return
            else:  # PostgreSQL
                conn.execute(text("""
                    ALTER TABLE tasks
                    DROP COLUMN IF EXISTS deploy_url
                """))

            conn.commit()
            print("✅ Поле deploy_url успешно удалено из таблицы tasks")

        except Exception as e:
            print(f"❌ Ошибка при откате миграции: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("МИГРАЦИЯ: Добавление deploy_url в tasks")
    print("=" * 60)

    try:
        upgrade()
        print("\n✅ Миграция выполнена успешно!")
    except Exception as e:
        print(f"\n❌ Ошибка выполнения миграции: {e}")
        sys.exit(1)
