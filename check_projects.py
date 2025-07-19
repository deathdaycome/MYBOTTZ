#!/usr/bin/env python3
"""
Проверка проектов и пользователей для уведомлений
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import get_db_context
from app.database.models import User, Project

def check_projects_for_notifications():
    """Проверяем какие проекты есть и кому отправятся уведомления"""
    print("📋 Проверка проектов для уведомлений")
    print("="*60)
    
    YOUR_TELEGRAM_ID = 501613334
    
    with get_db_context() as db:
        # Находим пользователя с вашим ID
        your_user = db.query(User).filter(User.telegram_id == YOUR_TELEGRAM_ID).first()
        
        if your_user:
            print(f"✅ Найден ваш пользователь:")
            print(f"   ID: {your_user.id}")
            print(f"   Имя: {your_user.first_name}")
            print(f"   Username: @{your_user.username}")
            print(f"   Telegram ID: {your_user.telegram_id}")
            
            # Ищем проекты этого пользователя
            your_projects = db.query(Project).filter(Project.user_id == your_user.id).all()
            
            if your_projects:
                print(f"\n🎯 ВАШИ ПРОЕКТЫ (вы получите уведомления):")
                print("-" * 50)
                for project in your_projects:
                    print(f"📋 ID: {project.id}")
                    print(f"   Название: {project.title}")
                    print(f"   Статус: {project.status}")
                    print(f"   Описание: {project.description[:100]}...")
                    print()
                
                print("🔔 При изменении статуса ЭТИХ проектов вы получите уведомление!")
            else:
                print(f"\n⚠️  У пользователя с ID {YOUR_TELEGRAM_ID} нет проектов")
                print("   Нужно создать проект для этого пользователя")
        else:
            print(f"❌ Пользователь с Telegram ID {YOUR_TELEGRAM_ID} не найден в базе")
        
        # Показываем все проекты и их владельцев
        print(f"\n📊 ВСЕ ПРОЕКТЫ В СИСТЕМЕ:")
        print("-" * 50)
        
        all_projects = db.query(Project).all()
        
        for project in all_projects:
            user = db.query(User).filter(User.id == project.user_id).first()
            
            will_notify = "🔔 ВЫ получите уведомление" if user and user.telegram_id == YOUR_TELEGRAM_ID else "📱 Уведомление получит другой пользователь"
            
            print(f"📋 Проект ID: {project.id}")
            print(f"   Название: {project.title}")
            print(f"   Статус: {project.status}")
            print(f"   Клиент: {user.first_name if user else 'Неизвестно'} (@{user.username if user else 'нет'})")
            print(f"   Telegram ID клиента: {user.telegram_id if user else 'Н/Д'}")
            print(f"   {will_notify}")
            print()
        
        # Рекомендации
        print("="*60)
        print("🎯 РЕКОМЕНДАЦИИ:")
        print("="*60)
        
        if your_user and your_projects:
            target_project = your_projects[0]
            print(f"✅ Меняйте статус проекта ID: {target_project.id}")
            print(f"   Название: {target_project.title}")
            print(f"   Текущий статус: {target_project.status}")
            print(f"   👤 Вы получите уведомление как клиент этого проекта!")
        else:
            # Ищем первый проект
            first_project = db.query(Project).first()
            if first_project:
                owner = db.query(User).filter(User.id == first_project.user_id).first()
                print(f"📋 Можете попробовать проект ID: {first_project.id}")
                print(f"   Название: {first_project.title}")
                print(f"   Клиент: {owner.first_name if owner else 'Неизвестно'}")
                print(f"   ⚠️  Уведомление получит {owner.first_name if owner else 'другой пользователь'}")
                print(f"       (Telegram ID: {owner.telegram_id if owner else 'Н/Д'})")
            
            print(f"\n💡 Чтобы получать уведомления на ваш Telegram:")
            print(f"   1. Создайте проект для пользователя с ID {YOUR_TELEGRAM_ID}")
            print(f"   2. Или измените user_id существующего проекта")

if __name__ == "__main__":
    check_projects_for_notifications()
