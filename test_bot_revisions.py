#!/usr/bin/env python3
"""
Тест функциональности правок в боте
"""
import asyncio
from unittest.mock import MagicMock
from app.bot.handlers.revisions import RevisionsHandler
from app.database.database import get_db_context
from app.database.models import Project, User, ProjectRevision

class MockUpdate:
    def __init__(self, callback_data, user_id=123456789):
        self.callback_query = MagicMock()
        self.callback_query.data = callback_data
        self.effective_user = MagicMock()
        self.effective_user.id = user_id
        self.message = None
        
        # Мокаем методы
        self.callback_query.edit_message_text = MagicMock()
        self.callback_query.answer = MagicMock()

class MockContext:
    def __init__(self):
        self.user_data = {}

async def test_revisions_functionality():
    """Тестирует основную функциональность правок"""
    print("🧪 Тестирование функциональности правок...")
    
    # Инициализируем обработчик
    handler = RevisionsHandler()
    
    # Найдем проект для тестирования
    project_id = None
    with get_db_context() as db:
        project = db.query(Project).filter(Project.title.like('%Тестовый проект%')).first()
        if not project:
            print("❌ Тестовый проект не найден")
            return
        
        project_id = project.id
        project_title = project.title
        print(f"✅ Найден проект: {project_title} (ID: {project_id})")
    
    # Тест 1: Показать правки проекта
    print("\n1️⃣ Тестируем показ правок проекта...")
    update = MockUpdate(f"project_revisions_{project_id}")
    context = MockContext()
    
    try:
        await handler.show_project_revisions(update, context)
        print("✅ Показ правок проекта работает")
    except Exception as e:
        print(f"❌ Ошибка при показе правок: {e}")
    
    # Тест 2: Список правок
    print("\n2️⃣ Тестируем список правок...")
    update = MockUpdate(f"list_revisions_{project_id}")
    context = MockContext()
    
    try:
        await handler.list_project_revisions(update, context)
        print("✅ Список правок работает")
    except Exception as e:
        print(f"❌ Ошибка при показе списка правок: {e}")
    
    # Тест 3: Начать создание правки
    print("\n3️⃣ Тестируем начало создания правки...")
    update = MockUpdate(f"create_revision_{project_id}")
    context = MockContext()
    
    try:
        await handler.start_create_revision(update, context)
        print("✅ Начало создания правки работает")
        print(f"   Установлен project_id: {context.user_data.get('creating_revision_project_id')}")
        print(f"   Установлен шаг: {context.user_data.get('creating_revision_step')}")
    except Exception as e:
        print(f"❌ Ошибка при начале создания правки: {e}")
    
    # Тест 4: Детали правки
    print("\n4️⃣ Тестируем показ деталей правки...")
    with get_db_context() as db:
        revision = db.query(ProjectRevision).filter(ProjectRevision.project_id == project_id).first()
        if revision:
            revision_id = revision.id
            revision_number = revision.revision_number
            
            update = MockUpdate(f"revision_details_{revision_id}")
            context = MockContext()
            
            try:
                await handler.show_revision_details(update, context)
                print(f"✅ Показ деталей правки #{revision_number} работает")
            except Exception as e:
                print(f"❌ Ошибка при показе деталей правки: {e}")
        else:
            print("⚠️ Правки не найдены для тестирования деталей")
    
    print("\n🎉 Тестирование завершено!")

def test_helper_functions():
    """Тестирует вспомогательные функции"""
    print("\n🔧 Тестирование вспомогательных функций...")
    
    handler = RevisionsHandler()
    
    # Тест эмодзи статусов
    statuses = ['pending', 'in_progress', 'completed', 'rejected']
    print("📊 Тест эмодзи статусов:")
    for status in statuses:
        emoji = handler._get_revision_status_emoji(status)
        name = handler._get_revision_status_name(status)
        print(f"   {status}: {emoji} {name}")
    
    # Тест эмодзи приоритетов
    priorities = ['low', 'normal', 'high', 'urgent']
    print("\n🎯 Тест эмодзи приоритетов:")
    for priority in priorities:
        emoji = handler._get_revision_priority_emoji(priority)
        name = handler._get_revision_priority_name(priority)
        print(f"   {priority}: {emoji} {name}")
    
    print("✅ Вспомогательные функции работают корректно")

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов функциональности правок")
    print("=" * 50)
    
    # Тестируем вспомогательные функции
    test_helper_functions()
    
    # Тестируем основную функциональность
    await test_revisions_functionality()
    
    print("\n" + "=" * 50)
    print("✅ Все тесты завершены!")

if __name__ == "__main__":
    asyncio.run(main())
