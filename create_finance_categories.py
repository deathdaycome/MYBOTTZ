#!/usr/bin/env python3
"""
Скрипт для создания базовых категорий финансов
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.database import SessionLocal
from app.database.models import FinanceCategory, AdminUser
from datetime import datetime

def create_default_finance_categories():
    """Создание базовых категорий финансов"""
    
    # Получаем или создаем администратора
    db = SessionLocal()
    
    try:
        admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin_user:
            print("Администратор не найден! Сначала создайте администратора.")
            return
        
        # Проверяем, есть ли уже категории
        existing_categories = db.query(FinanceCategory).count()
        if existing_categories > 0:
            print(f"Найдено {existing_categories} существующих категорий. Пропускаем создание.")
            return
        
        # Категории доходов
        income_categories = [
            {
                "name": "Проекты - Разработка ботов",
                "description": "Доходы от разработки Telegram-ботов",
                "color": "#28a745",
                "icon": "fas fa-robot"
            },
            {
                "name": "Проекты - Веб-разработка",
                "description": "Доходы от веб-разработки",
                "color": "#17a2b8",
                "icon": "fas fa-globe"
            },
            {
                "name": "Консультации",
                "description": "Доходы от консультаций",
                "color": "#20c997",
                "icon": "fas fa-handshake"
            },
            {
                "name": "Дополнительные услуги",
                "description": "Настройка серверов, домены и прочее",
                "color": "#6f42c1",
                "icon": "fas fa-tools"
            },
            {
                "name": "Бонусы и премии",
                "description": "Бонусные выплаты от клиентов",
                "color": "#fd7e14",
                "icon": "fas fa-gift"
            }
        ]
        
        # Категории расходов
        expense_categories = [
            {
                "name": "Выплаты исполнителям",
                "description": "Оплата работы исполнителей",
                "color": "#dc3545",
                "icon": "fas fa-user-tie"
            },
            {
                "name": "Нейросети и API",
                "description": "Расходы на OpenAI, Claude и другие AI-сервисы",
                "color": "#e83e8c",
                "icon": "fas fa-brain"
            },
            {
                "name": "Хостинг и серверы",
                "description": "Оплата хостинга, VPS, доменов",
                "color": "#6c757d",
                "icon": "fas fa-server"
            },
            {
                "name": "Лицензии и подписки",
                "description": "Софт, инструменты разработки",
                "color": "#007bff",
                "icon": "fas fa-key"
            },
            {
                "name": "Реклама и маркетинг",
                "description": "Расходы на продвижение",
                "color": "#ffc107",
                "icon": "fas fa-bullhorn"
            },
            {
                "name": "Офисные расходы",
                "description": "Интернет, электричество, прочие расходы",
                "color": "#6f42c1",
                "icon": "fas fa-building"
            },
            {
                "name": "Налоги и сборы",
                "description": "Налоги, комиссии банков",
                "color": "#dc3545",
                "icon": "fas fa-receipt"
            },
            {
                "name": "Обучение и развитие",
                "description": "Курсы, книги, конференции",
                "color": "#17a2b8",
                "icon": "fas fa-graduation-cap"
            }
        ]
        
        # Создаем категории доходов
        for category_data in income_categories:
            category = FinanceCategory(
                name=category_data["name"],
                type="income",
                description=category_data["description"],
                color=category_data["color"],
                icon=category_data["icon"],
                created_by_id=admin_user.id,
                created_at=datetime.utcnow()
            )
            db.add(category)
        
        # Создаем категории расходов
        for category_data in expense_categories:
            category = FinanceCategory(
                name=category_data["name"],
                type="expense",
                description=category_data["description"],
                color=category_data["color"],
                icon=category_data["icon"],
                created_by_id=admin_user.id,
                created_at=datetime.utcnow()
            )
            db.add(category)
        
        db.commit()
        
        total_income = len(income_categories)
        total_expense = len(expense_categories)
        total_categories = total_income + total_expense
        
        print(f"✅ Создано {total_categories} базовых категорий финансов:")
        print(f"   📈 Доходы: {total_income} категорий")
        print(f"   📉 Расходы: {total_expense} категорий")
        print("\n📋 Категории доходов:")
        for cat in income_categories:
            print(f"   • {cat['name']}")
        print("\n📋 Категории расходов:")
        for cat in expense_categories:
            print(f"   • {cat['name']}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании категорий: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🏗️  Создание базовых категорий финансов...")
    create_default_finance_categories()
    print("✅ Готово!")
