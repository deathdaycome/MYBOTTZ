#!/usr/bin/env python3
"""
Тест системы уведомлений о правках
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import get_db_context
from app.database.models import Project, User, ProjectRevision
from app.services.notification_service import notification_service
from app.config.logging import get_logger

logger = get_logger(__name__)

async def test_revision_notifications():
    """Тест уведомлений о правках"""
    try:
        with get_db_context() as db:
            # Создаем тестового пользователя
            test_user = User(
                telegram_id=12345,
                first_name="Тест",
                username="test_user",
                phone="+79123456789",
                email="test@example.com"
            )
            db.add(test_user)
            db.flush()
            
            # Создаем тестовый проект
            test_project = Project(
                title="Тестовый проект для правок",
                description="Описание тестового проекта",
                user_id=test_user.id,
                status="in_progress",
                estimated_cost=50000,
                estimated_hours=40,
                complexity="medium"
            )
            db.add(test_project)
            db.flush()
            
            # Создаем тестовую правку
            test_revision = ProjectRevision(
                project_id=test_project.id,
                revision_number=1,
                title="Тестовая правка",
                description="Тестовая правка для проверки уведомлений",
                priority="medium",
                status="open",
                created_by_id=test_user.id
            )
            db.add(test_revision)
            db.flush()
            
            print("✅ Тестовые данные созданы")
            print(f"📋 Проект ID: {test_project.id}")
            print(f"📝 Правка ID: {test_revision.id}")
            print(f"👤 Пользователь ID: {test_user.id}")
            
            # Тестируем уведомление о новой правке
            print("\n🔔 Тестируем уведомление о новой правке...")
            await notification_service.notify_new_revision(test_revision, test_project, test_user)
            print("✅ Уведомление о новой правке отправлено")
            
            # Тестируем уведомление об изменении статуса
            print("\n🔔 Тестируем уведомление об изменении статуса...")
            old_status = test_revision.status
            test_revision.status = "completed"
            await notification_service.notify_revision_status_changed(
                test_revision, test_project, test_user, old_status
            )
            print("✅ Уведомление об изменении статуса отправлено")
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Ошибка тестирования уведомлений: {e}")
        print(f"❌ Ошибка: {e}")

async def main():
    """Главная функция"""
    print("🚀 Запуск теста уведомлений о правках...")
    
    # Настраиваем notification_service
    # В реальном приложении бот будет установлен автоматически
    from telegram import Bot
    from app.config.settings import get_settings
    
    settings = get_settings()
    if settings.BOT_TOKEN:
        bot = Bot(token=settings.BOT_TOKEN)
        notification_service.set_bot(bot)
        print("✅ Бот инициализирован")
    else:
        print("⚠️ BOT_TOKEN не найден, уведомления будут только логироваться")
    
    await test_revision_notifications()
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    asyncio.run(main())
