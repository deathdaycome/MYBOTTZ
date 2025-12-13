"""
Миграция: Добавление project_id в tasks
Дата: 2025-12-12
Описание: Добавляет связь задач с проектами через project_id
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config.settings import settings
from app.config.logging import get_logger

logger = get_logger(__name__)

def run_migration():
    """Выполнить миграцию"""
    # Создаем синхронный engine
    sync_database_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    sync_database_url = sync_database_url.replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(sync_database_url)

    try:
        with engine.connect() as conn:
            # Проверяем, существует ли уже колонка
            if "sqlite" in sync_database_url:
                result = conn.execute(text("PRAGMA table_info(tasks)"))
                columns = [row[1] for row in result.fetchall()]

                if "project_id" in columns:
                    logger.info("✅ Колонка project_id уже существует в tasks")
                    return

                # SQLite - создаем новую таблицу с project_id и копируем данные
                logger.info("🔄 Добавление project_id в tasks (SQLite)")

                # 1. Создаем временную таблицу
                conn.execute(text("""
                    CREATE TABLE tasks_new (
                        id INTEGER PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        description TEXT,
                        status VARCHAR(50) DEFAULT 'pending',
                        priority VARCHAR(20) DEFAULT 'normal',
                        color VARCHAR(20) DEFAULT 'normal',
                        tags JSON DEFAULT '[]',
                        assigned_to_id INTEGER NOT NULL,
                        created_by_id INTEGER NOT NULL,
                        project_id INTEGER,
                        deadline DATETIME,
                        estimated_hours INTEGER,
                        actual_hours INTEGER,
                        progress INTEGER DEFAULT 0,
                        time_spent_seconds INTEGER DEFAULT 0,
                        timer_started_at DATETIME,
                        deploy_url VARCHAR(1000),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        completed_at DATETIME,
                        task_metadata JSON DEFAULT '{}',
                        FOREIGN KEY(assigned_to_id) REFERENCES admin_users(id),
                        FOREIGN KEY(created_by_id) REFERENCES admin_users(id),
                        FOREIGN KEY(project_id) REFERENCES projects(id)
                    )
                """))

                # 2. Копируем данные из старой таблицы
                conn.execute(text("""
                    INSERT INTO tasks_new (
                        id, title, description, status, priority, color, tags,
                        assigned_to_id, created_by_id, deadline, estimated_hours,
                        actual_hours, progress, time_spent_seconds, timer_started_at,
                        deploy_url, created_at, updated_at, completed_at, task_metadata
                    )
                    SELECT
                        id, title, description, status, priority, color, tags,
                        assigned_to_id, created_by_id, deadline, estimated_hours,
                        actual_hours, progress, time_spent_seconds, timer_started_at,
                        deploy_url, created_at, updated_at, completed_at, task_metadata
                    FROM tasks
                """))

                # 3. Удаляем старую таблицу
                conn.execute(text("DROP TABLE tasks"))

                # 4. Переименовываем новую таблицу
                conn.execute(text("ALTER TABLE tasks_new RENAME TO tasks"))

                conn.commit()
                logger.info("✅ Миграция выполнена успешно (SQLite)")

            else:  # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='tasks' AND column_name='project_id'
                """))

                if result.fetchone():
                    logger.info("✅ Колонка project_id уже существует в tasks")
                    return

                logger.info("🔄 Добавление project_id в tasks (PostgreSQL)")

                # Добавляем колонку
                conn.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN project_id INTEGER
                    REFERENCES projects(id) ON DELETE SET NULL
                """))

                # Создаем индекс для быстрого поиска
                conn.execute(text("""
                    CREATE INDEX idx_tasks_project_id ON tasks(project_id)
                """))

                conn.commit()
                logger.info("✅ Миграция выполнена успешно (PostgreSQL)")

    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении миграции: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    logger.info("🚀 Запуск миграции: add_project_id_to_tasks")
    run_migration()
    logger.info("✅ Миграция завершена")
