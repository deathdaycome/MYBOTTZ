#!/usr/bin/env python3
"""
Скрипт для создания пользователя с ролью продажника (sales)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.database.models import AdminUser
from app.services.auth_service import AuthService
from app.config.logging import get_logger

logger = get_logger(__name__)

def create_sales_user():
    """Создает пользователя с ролью sales"""
    
    db = SessionLocal()
    
    try:
        # Данные для нового продажника
        username = "anna"  # Логин для Анны
        password = "sales2024"  # Пароль
        email = "anna@sales.com"
        first_name = "Анна"
        last_name = "Продажник"
        role = "sales"
        
        # Проверяем, не существует ли уже такой пользователь
        existing_user = db.query(AdminUser).filter(AdminUser.username == username).first()
        
        if existing_user:
            logger.warning(f"❌ Пользователь {username} уже существует")
            
            # Обновляем роль если нужно
            if existing_user.role != role:
                existing_user.role = role
                db.commit()
                logger.info(f"✅ Роль пользователя {username} обновлена на {role}")
            else:
                logger.info(f"ℹ️ Пользователь {username} уже имеет роль {role}")
        else:
            # Создаем нового пользователя
            new_user = AdminUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True
            )
            new_user.set_password(password)  # Используем метод модели для установки пароля
            
            db.add(new_user)
            db.commit()
            
            logger.info(f"✅ Создан пользователь-продажник:")
            logger.info(f"   Логин: {username}")
            logger.info(f"   Пароль: {password}")
            logger.info(f"   Роль: {role}")
            logger.info(f"   Имя: {first_name} {last_name}")
            
            print("\n" + "="*50)
            print("ДАННЫЕ ДЛЯ ВХОДА ПРОДАЖНИКА:")
            print("="*50)
            print(f"Логин: {username}")
            print(f"Пароль: {password}")
            print(f"URL: http://localhost:8000/admin/")
            print("="*50)
            print("\nДоступные разделы для продажника:")
            print("- Дашборд")
            print("- Лиды (полный доступ)")
            print("- Клиенты (полный доступ)")
            print("- Сделки (полный доступ)")
            print("- Проекты (только просмотр)")
            print("- Отчеты (только по продажам)")
            print("="*50 + "\n")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при создании пользователя: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sales_user()