#!/usr/bin/env python3
"""
Простой тест системы правок
"""
import asyncio
from app.bot.keyboards.main import get_project_actions_keyboard, get_project_revisions_keyboard
from app.database.database import get_db_context
from app.database.models import Project, ProjectRevision, User

def test_keyboards():
    """Тест клавиатур"""
    print("🔧 Тестирование клавиатур...")
    
    # Тест клавиатуры действий проекта
    keyboard = get_project_actions_keyboard(3)
    print("⌨️ Клавиатура действий проекта:")
    for row in keyboard.inline_keyboard:
        for button in row:
            print(f"  - {button.text} -> {button.callback_data}")
    
    # Тест клавиатуры правок
    keyboard_revisions = get_project_revisions_keyboard(3, 1)
    print("\n⌨️ Клавиатура правок:")
    for row in keyboard_revisions.inline_keyboard:
        for button in row:
            print(f"  - {button.text} -> {button.callback_data}")

def test_database():
    """Тест данных в базе"""
    print("\n🔧 Тестирование данных в базе...")
    
    with get_db_context() as db:
        # Проверяем пользователя
        user = db.query(User).filter(User.id == 3).first()
        if user:
            print(f"👤 Пользователь найден: {user.username}")
        else:
            print("❌ Пользователь не найден")
        
        # Проверяем проект
        project = db.query(Project).filter(Project.id == 3).first()
        if project:
            print(f"📋 Проект найден: {project.title}")
            print(f"📊 Статус: {project.status}")
        else:
            print("❌ Проект не найден")
        
        # Проверяем правки
        revisions = db.query(ProjectRevision).filter(ProjectRevision.project_id == 3).all()
        print(f"📝 Количество правок: {len(revisions)}")
        for revision in revisions:
            print(f"  - #{revision.revision_number}: {revision.title} ({revision.status})")

def main():
    print("🚀 Простой тест системы правок...")
    test_keyboards()
    test_database()
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    main()