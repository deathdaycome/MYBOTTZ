#!/usr/bin/env python3
"""
Скрипт для инициализации категорий доходов и расходов
"""

from app.database.database import get_db_context
from app.database.models import MoneyCategory, AdminUser

def init_money_categories():
    """Инициализация базовых категорий"""
    
    # Категории доходов
    income_categories = [
        {"name": "Разработка ботов", "color": "#28a745", "icon": "fas fa-robot", "sort_order": 1},
        {"name": "Веб-разработка", "color": "#007bff", "icon": "fas fa-code", "sort_order": 2},
        {"name": "Консультации", "color": "#17a2b8", "icon": "fas fa-handshake", "sort_order": 3},
        {"name": "Интеграции", "color": "#6610f2", "icon": "fas fa-plug", "sort_order": 4},
        {"name": "Поддержка", "color": "#fd7e14", "icon": "fas fa-tools", "sort_order": 5},
        {"name": "Обучение", "color": "#20c997", "icon": "fas fa-graduation-cap", "sort_order": 6},
        {"name": "Прочие доходы", "color": "#6c757d", "icon": "fas fa-plus-circle", "sort_order": 99}
    ]
    
    # Категории расходов
    expense_categories = [
        {"name": "Еда", "color": "#dc3545", "icon": "fas fa-utensils", "sort_order": 1},
        {"name": "Транспорт", "color": "#ffc107", "icon": "fas fa-car", "sort_order": 2},
        {"name": "Жилье", "color": "#8B4513", "icon": "fas fa-home", "sort_order": 3},
        {"name": "Коммунальные услуги", "color": "#6f42c1", "icon": "fas fa-bolt", "sort_order": 4},
        {"name": "Интернет", "color": "#0dcaf0", "icon": "fas fa-wifi", "sort_order": 5},
        {"name": "Софт и подписки", "color": "#6610f2", "icon": "fas fa-laptop", "sort_order": 6},
        {"name": "Хостинг", "color": "#198754", "icon": "fas fa-server", "sort_order": 7},
        {"name": "Реклама", "color": "#fd7e14", "icon": "fas fa-bullhorn", "sort_order": 8},
        {"name": "Образование", "color": "#20c997", "icon": "fas fa-book", "sort_order": 9},
        {"name": "Здоровье", "color": "#dc3545", "icon": "fas fa-heartbeat", "sort_order": 10},
        {"name": "Развлечения", "color": "#e83e8c", "icon": "fas fa-gamepad", "sort_order": 11},
        {"name": "Одежда", "color": "#795548", "icon": "fas fa-tshirt", "sort_order": 12},
        {"name": "Налоги", "color": "#343a40", "icon": "fas fa-file-invoice-dollar", "sort_order": 13},
        {"name": "Прочие расходы", "color": "#6c757d", "icon": "fas fa-minus-circle", "sort_order": 99}
    ]
    
    with get_db_context() as db:
        # Получаем или создаем админа
        admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        
        if not admin_user:
            print("Создаем админ пользователя...")
            admin_user = AdminUser(
                username="admin",
                password_hash="dummy_hash",  # Заглушка
                role="owner",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        
        print(f"Используем админа: {admin_user.username} (ID: {admin_user.id})")
        
        # Добавляем категории доходов
        print("Добавляем категории доходов...")
        for cat_data in income_categories:
            existing = db.query(MoneyCategory).filter(
                MoneyCategory.name == cat_data["name"],
                MoneyCategory.type == "income"
            ).first()
            
            if not existing:
                category = MoneyCategory(
                    name=cat_data["name"],
                    type="income",
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                    sort_order=cat_data["sort_order"],
                    created_by_id=admin_user.id
                )
                db.add(category)
                print(f"  ✅ {cat_data['name']}")
            else:
                print(f"  ⏭️ {cat_data['name']} (уже существует)")
        
        # Добавляем категории расходов
        print("Добавляем категории расходов...")
        for cat_data in expense_categories:
            existing = db.query(MoneyCategory).filter(
                MoneyCategory.name == cat_data["name"],
                MoneyCategory.type == "expense"
            ).first()
            
            if not existing:
                category = MoneyCategory(
                    name=cat_data["name"],
                    type="expense",
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                    sort_order=cat_data["sort_order"],
                    created_by_id=admin_user.id
                )
                db.add(category)
                print(f"  ✅ {cat_data['name']}")
            else:
                print(f"  ⏭️ {cat_data['name']} (уже существует)")
        
        db.commit()
        print("✅ Все категории добавлены!")


if __name__ == "__main__":
    print("🚀 Инициализация категорий доходов и расходов...")
    init_money_categories()
    print("🎉 Готово!")