#!/usr/bin/env python3
"""
Скрипт для создания тестовых проектов и правок
"""
import sys
import os
from datetime import datetime, timedelta

# Добавляем путь к корню проекта для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_context
from app.database.models import Project, ProjectRevision, User

def create_test_data():
    """Создает тестовые проекты и правки"""

    with get_db_context() as db:
        # Получаем первого пользователя
        user = db.query(User).first()
        if not user:
            print("❌ Пользователь не найден. Сначала запустите бота и зарегистрируйтесь.")
            return

        print(f"✅ Найден пользователь: {user.username} (ID: {user.id})")

        # Тестовые проекты
        test_projects = [
            {
                "title": "Интернет-магазин электроники",
                "description": "Разработка полнофункционального интернет-магазина с каталогом, корзиной и оплатой",
                "project_type": "Интернет-магазин",
                "status": "in_progress",
                "estimated_cost": 250000.0,
                "complexity": "high",
            },
            {
                "title": "Мобильное приложение для доставки еды",
                "description": "iOS и Android приложение для заказа еды из ресторанов с трекингом курьера",
                "project_type": "Мобильное приложение",
                "status": "in_progress",
                "estimated_cost": 450000.0,
                "complexity": "high",
            },
            {
                "title": "CRM система для салона красоты",
                "description": "Веб-приложение для управления записями клиентов, складом и зарплатами",
                "project_type": "Веб-сервис",
                "status": "testing",
                "estimated_cost": 180000.0,
                "complexity": "medium",
            },
        ]

        # Тестовые правки
        test_revisions = [
            {
                "title": "Исправить баг с авторизацией",
                "description": "При входе через Telegram иногда пользователь не авторизуется. Нужно исправить проверку токена.",
                "status": "in_progress",
                "priority": "high",
                "progress": 65,
                "time_spent_seconds": 3600,
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
                "time_spent_seconds": 7200,
                "completed_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "title": "Улучшить дизайн кнопок",
                "description": "Кнопки на главной странице выглядят не очень привлекательно. Нужно добавить градиенты и анимации.",
                "status": "in_progress",
                "priority": "low",
                "progress": 40,
                "time_spent_seconds": 1800,
            },
            {
                "title": "СРОЧНО: Исправить крит. ошибку оплаты",
                "description": "После обновления перестала работать оплата через Stripe. Клиенты жалуются!",
                "status": "in_progress",
                "priority": "urgent",
                "progress": 85,
                "time_spent_seconds": 5400,
            },
        ]

        # Создаем проекты
        projects_created = 0
        existing_projects = db.query(Project).filter(Project.user_id == user.id).all()

        if len(existing_projects) == 0:
            print("\n📂 Создание тестовых проектов...")

            for proj_data in test_projects:
                project = Project(
                    user_id=user.id,
                    title=proj_data["title"],
                    description=proj_data["description"],
                    project_type=proj_data["project_type"],
                    status=proj_data["status"],
                    estimated_cost=proj_data["estimated_cost"],
                    complexity=proj_data["complexity"],
                    start_date=datetime.utcnow(),
                    planned_end_date=datetime.utcnow() + timedelta(days=30),  # Плановое завершение через 30 дней
                )
                db.add(project)
                projects_created += 1
                print(f"  ✅ {proj_data['title']}")

            db.commit()
            print(f"\n✅ Создано {projects_created} проектов!")

            # Обновляем список проектов
            existing_projects = db.query(Project).filter(Project.user_id == user.id).all()
        else:
            print(f"\n✅ Найдено {len(existing_projects)} существующих проектов")

        # Создаем правки для каждого проекта
        revisions_created = 0
        print("\n📝 Создание правок для проектов...")

        for project in existing_projects[:3]:
            print(f"\n📂 Проект: {project.title}")

            # Проверяем, есть ли уже правки
            existing_revisions = db.query(ProjectRevision).filter(
                ProjectRevision.project_id == project.id
            ).count()

            if existing_revisions > 0:
                print(f"  ℹ️  Уже есть {existing_revisions} правок, пропускаем...")
                continue

            # Создаем по 3 правки для каждого проекта
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
                revisions_created += 1

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

        if revisions_created > 0 or projects_created > 0:
            db.commit()
            print(f"\n✅ Успешно создано:")
            print(f"   📂 Проектов: {projects_created}")
            print(f"   📝 Правок: {revisions_created}")
            print("\n🎉 Теперь можете открыть Mini App и увидеть данные:")
            print("   http://localhost:5173/projects - Список проектов")
            print("   http://localhost:5173/revisions - Все правки")
        else:
            print("\n✅ Все тестовые данные уже созданы!")


if __name__ == "__main__":
    print("=" * 70)
    print("🛠️  Создание тестовых данных (проекты + правки)")
    print("=" * 70)

    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
