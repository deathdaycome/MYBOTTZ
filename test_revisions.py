#!/usr/bin/env python3
"""
Скрипт для тестирования функциональности правок
"""
from app.database.database import get_db_context
from app.database.models import Project, User, ProjectRevision

def create_test_revision():
    """Создает тестовую правку"""
    with get_db_context() as db:
        # Находим тестовый проект
        project = db.query(Project).filter(Project.title.like('%Тестовый проект%')).first()
        
        if not project:
            print("❌ Тестовый проект не найден")
            return
        
        # Получаем пользователя проекта
        user = project.user
        
        if not user:
            print("❌ Пользователь проекта не найден")
            return
        
        # Создаем правку
        revision = ProjectRevision(
            project_id=project.id,
            revision_number=1,
            title="Исправить цвет кнопки",
            description="Главная кнопка 'Заказать' слишком яркая. Нужно сделать её более мягкого синего цвета, как на странице контактов.",
            priority="normal",
            status="pending",
            created_by_id=user.id
        )
        
        db.add(revision)
        db.commit()
        db.refresh(revision)
        
        print(f"✅ Тестовая правка создана:")
        print(f"   ID: {revision.id}")
        print(f"   Номер: #{revision.revision_number}")
        print(f"   Заголовок: {revision.title}")
        print(f"   Проект: {project.title}")
        print(f"   Статус: {revision.status}")
        print(f"   Приоритет: {revision.priority}")

def create_second_revision():
    """Создает вторую тестовую правку"""
    with get_db_context() as db:
        # Находим тестовый проект
        project = db.query(Project).filter(Project.title.like('%Тестовый проект%')).first()
        
        if not project:
            print("❌ Тестовый проект не найден")
            return
        
        # Получаем пользователя проекта
        user = project.user
        
        # Создаем вторую правку
        revision = ProjectRevision(
            project_id=project.id,
            revision_number=2,
            title="Добавить функцию поиска",
            description="В каталоге товаров не хватает поиска. Нужно добавить строку поиска сверху с фильтрацией по названию и категории.",
            priority="high",
            status="pending",
            created_by_id=user.id
        )
        
        db.add(revision)
        db.commit()
        db.refresh(revision)
        
        print(f"✅ Вторая тестовая правка создана:")
        print(f"   ID: {revision.id}")
        print(f"   Номер: #{revision.revision_number}")
        print(f"   Заголовок: {revision.title}")
        print(f"   Статус: {revision.status}")
        print(f"   Приоритет: {revision.priority}")

def list_project_revisions():
    """Выводит список всех правок проекта"""
    with get_db_context() as db:
        project = db.query(Project).filter(Project.title.like('%Тестовый проект%')).first()
        
        if not project:
            print("❌ Тестовый проект не найден")
            return
        
        revisions = db.query(ProjectRevision).filter(
            ProjectRevision.project_id == project.id
        ).order_by(ProjectRevision.revision_number).all()
        
        print(f"\n📋 Правки проекта '{project.title}':")
        print("=" * 50)
        
        if not revisions:
            print("❌ Правки не найдены")
            return
        
        for revision in revisions:
            print(f"#{revision.revision_number} - {revision.title}")
            print(f"   Статус: {revision.status}")
            print(f"   Приоритет: {revision.priority}")
            print(f"   Описание: {revision.description[:80]}...")
            print(f"   Создано: {revision.created_at}")
            print("-" * 40)

if __name__ == "__main__":
    print("🚀 Создание тестовых правок...")
    create_test_revision()
    print()
    create_second_revision()
    print()
    list_project_revisions()
