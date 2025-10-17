#!/usr/bin/env python3
"""
Скрипт для создания тестовых правок для проектов
"""
import sys
import os
from datetime import datetime, timedelta

# Добавляем путь к корню проекта для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_context
from app.database.models import Project, ProjectRevision, User

def create_test_revisions():
    """Создает тестовые правки для существующих проектов"""

    with get_db_context() as db:
        # Получаем первого пользователя
        user = db.query(User).first()
        if not user:
            print("❌ Пользователь не найден. Сначала запустите бота и зарегистрируйтесь.")
            return

        print(f"✅ Найден пользователь: {user.username} (ID: {user.id})")

        # Получаем все проекты этого пользователя
        projects = db.query(Project).filter(Project.user_id == user.id).all()

        if not projects:
            print("❌ Проекты не найдены. Создайте проект через бота или Mini App.")
            return

        print(f"✅ Найдено проектов: {len(projects)}")

        # Тестовые данные для правок
        test_revisions = [
            {
                "title": "Исправить баг с авторизацией",
                "description": "При входе через Telegram иногда пользователь не авторизуется. Нужно исправить проверку токена.",
                "status": "in_progress",
                "priority": "high",
                "progress": 65,
                "time_spent_seconds": 3600,  # 1 час
            },
            {
                "title": "Добавить валидацию email",
                "description": "Добавить проверку формата email при регистрации пользователя.",
                "status": "pending",
                "priority": "normal",
                "progress": 0,
                "time_spent_seconds": 0,
            },
            {
                "title": "Оптимизировать запросы к БД",
                "description": "Страница со списком проектов загружается медленно. Нужно оптимизировать запросы и добавить индексы.",
                "status": "completed",
                "priority": "normal",
                "progress": 100,
                "time_spent_seconds": 7200,  # 2 часа
                "completed_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "title": "Улучшить дизайн кнопок",
                "description": "Кнопки на главной странице выглядят не очень привлекательно. Нужно добавить градиенты и анимации.",
                "status": "in_progress",
                "priority": "low",
                "progress": 40,
                "time_spent_seconds": 1800,  # 30 минут
            },
            {
                "title": "СРОЧНО: Исправить крит. ошибку оплаты",
                "description": "После обновления перестала работать оплата через Stripe. Клиенты жалуются!",
                "status": "in_progress",
                "priority": "urgent",
                "progress": 85,
                "time_spent_seconds": 5400,  # 1.5 часа
            },
        ]

        created_count = 0

        for project in projects[:3]:  # Берем первые 3 проекта
            print(f"\n📂 Проект: {project.title}")

            # Проверяем, есть ли уже правки
            existing_revisions = db.query(ProjectRevision).filter(
                ProjectRevision.project_id == project.id
            ).count()

            if existing_revisions > 0:
                print(f"  ℹ️  Уже есть {existing_revisions} правок, пропускаем...")
                continue

            # Создаем по 2-3 правки для каждого проекта
            for i, rev_data in enumerate(test_revisions[:3], 1):
                revision = ProjectRevision(
                    project_id=project.id,
                    revision_number=i,
                    title=rev_data["title"],
                    description=rev_data["description"],
                    status=rev_data["status"],
                    priority=rev_data["priority"],
                    progress=rev_data["progress"],
                    time_spent_seconds=rev_data["time_spent_seconds"],
                    created_by_id=user.id,
                    completed_at=rev_data.get("completed_at"),
                )

                db.add(revision)
                created_count += 1

                status_emoji = {
                    "pending": "⏳",
                    "in_progress": "⚙️",
                    "completed": "✅",
                    "rejected": "❌",
                }

                priority_emoji = {
                    "low": "🔵",
                    "normal": "🟢",
                    "high": "🟡",
                    "urgent": "🔴",
                }

                print(f"  {status_emoji.get(rev_data['status'], '❓')} {priority_emoji.get(rev_data['priority'], '⚪')} #{i}: {rev_data['title']}")

        if created_count > 0:
            db.commit()
            print(f"\n✅ Создано {created_count} тестовых правок!")
            print("\n🎉 Теперь можете открыть Mini App и увидеть правки в проектах:")
            print("   http://localhost:5173/projects")
        else:
            print("\n✅ Все проекты уже имеют правки!")


if __name__ == "__main__":
    print("=" * 70)
    print("🛠️  Создание тестовых правок для проектов")
    print("=" * 70)

    try:
        create_test_revisions()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
