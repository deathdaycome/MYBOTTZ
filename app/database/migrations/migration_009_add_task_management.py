"""
Migration: Add Task Management System
Adds tables for tasks and task comments management
"""

from sqlalchemy import text
from ..database import get_db_context

def migrate():
    """Применить миграцию - добавить таблицы для управления задачами"""
    
    with get_db_context() as db:
        try:
            # Создаем таблицу задач
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
                    assigned_to_id INTEGER NOT NULL,
                    created_by_id INTEGER NOT NULL,
                    deadline DATETIME,
                    estimated_hours INTEGER,
                    actual_hours INTEGER,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    task_metadata JSON DEFAULT '{}',
                    FOREIGN KEY (assigned_to_id) REFERENCES admin_users (id),
                    FOREIGN KEY (created_by_id) REFERENCES admin_users (id)
                )
            """))
            
            # Создаем таблицу комментариев к задачам
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS task_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    comment_type VARCHAR(50) NOT NULL DEFAULT 'general',
                    is_internal BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (author_id) REFERENCES admin_users (id)
                )
            """))
            
            # Создаем индексы для оптимизации запросов
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks (assigned_to_id)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks (created_by_id)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks (deadline)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_task_comments_task ON task_comments (task_id)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_task_comments_author ON task_comments (author_id)"))
            
            db.commit()
            print("✅ Миграция 009: Таблицы задач успешно созданы")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка миграции 009: {e}")
            raise

def rollback():
    """Откатить миграцию - удалить таблицы задач"""
    
    with get_db_context() as db:
        try:
            # Удаляем индексы
            db.execute(text("DROP INDEX IF EXISTS idx_task_comments_author"))
            db.execute(text("DROP INDEX IF EXISTS idx_task_comments_task"))
            db.execute(text("DROP INDEX IF EXISTS idx_tasks_deadline"))
            db.execute(text("DROP INDEX IF EXISTS idx_tasks_priority"))
            db.execute(text("DROP INDEX IF EXISTS idx_tasks_status"))
            db.execute(text("DROP INDEX IF EXISTS idx_tasks_created_by"))
            db.execute(text("DROP INDEX IF EXISTS idx_tasks_assigned_to"))
            
            # Удаляем таблицы
            db.execute(text("DROP TABLE IF EXISTS task_comments"))
            db.execute(text("DROP TABLE IF EXISTS tasks"))
            
            db.commit()
            print("✅ Откат миграции 009: Таблицы задач удалены")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка отката миграции 009: {e}")
            raise

if __name__ == "__main__":
    migrate()