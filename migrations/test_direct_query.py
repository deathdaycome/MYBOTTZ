#!/usr/bin/env python3
"""
Тестовый скрипт для проверки создания задачи напрямую через SQLAlchemy
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database.database import SessionLocal, engine
from app.database.models import Task, TaskComment, AdminUser
from sqlalchemy import inspect

def test_task_creation():
    """Тестирование создания задачи"""
    print("🔍 Проверяем структуру таблицы task_comments...")

    inspector = inspect(engine)
    columns = inspector.get_columns('task_comments')

    print("\n📋 Колонки в таблице task_comments:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

    print("\n🧪 Попробуем создать задачу...")

    db = SessionLocal()
    try:
        # Найдём первого админа
        admin = db.query(AdminUser).first()
        if not admin:
            print("❌ Не найден ни один администратор в базе")
            return

        print(f"✅ Найден админ: {admin.username} (ID: {admin.id})")

        # Создаём задачу
        new_task = Task(
            title="Тестовая задача из миграции",
            description="Проверка создания задачи",
            assigned_to_id=admin.id,
            created_by_id=admin.id,
            priority="normal",
            status="pending"
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        print(f"✅ Задача создана! ID: {new_task.id}")

        # Проверяем комментарии
        comments = db.query(TaskComment).filter(TaskComment.task_id == new_task.id).all()
        print(f"📝 Комментариев к задаче: {len(comments)}")

    except Exception as e:
        print(f"❌ Ошибка при создании задачи: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    test_task_creation()
