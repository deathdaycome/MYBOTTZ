#!/usr/bin/env python3
"""
Скрипт создания администратора
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_admin():
    """Создание администратора"""
    try:
        from app.database.database import get_db_context
        from app.database.models import AdminUser
        
        with get_db_context() as db:
            # Проверяем, есть ли уже администратор
            existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
            if existing_admin:
                print("✅ Администратор 'admin' уже существует")
                return True
            
            # Создаем администратора
            admin = AdminUser(
                username="admin",
                email="admin@example.com",
                first_name="Администратор",
                last_name="Системы",
                role="owner",
                is_active=True
            )
            admin.set_password("qwerty123")
            
            db.add(admin)
            db.commit()
            
            print("✅ Администратор создан:")
            print(f"   Логин: admin")
            print(f"   Пароль: qwerty123")
            print(f"   Роль: owner")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка создания администратора: {e}")
        return False

if __name__ == "__main__":
    if create_admin():
        print("🚀 Готово!")
    else:
        print("💥 Ошибка!")
        sys.exit(1)
