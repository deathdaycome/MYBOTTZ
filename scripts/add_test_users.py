#!/usr/bin/env python3
"""
Скрипт для добавления тестовых пользователей в базу данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auth_service import AuthService
from app.database.models import AdminUser
from app.database.database import get_db_connection

def add_test_users():
    """Добавление тестовых пользователей"""
    
    # Проверяем, есть ли уже пользователи
    db = next(get_db_connection())
    existing_users = db.query(AdminUser).all()
    
    if existing_users:
        print(f"В базе данных уже есть {len(existing_users)} пользователей:")
        for user in existing_users:
            print(f"  - {user.username} ({user.role})")
    
    # Список тестовых пользователей для добавления
    test_users = [
        {
            "username": "admin",
            "password": "qwerty123",
            "role": "owner",
            "first_name": "Администратор",
            "email": "admin@example.com"
        },
        {
            "username": "executor1",
            "password": "executor123",
            "role": "executor",
            "first_name": "Иван",
            "last_name": "Исполнитель",
            "email": "executor1@example.com"
        },
        {
            "username": "executor2",
            "password": "executor123",
            "role": "executor",
            "first_name": "Петр",
            "last_name": "Разработчик",
            "email": "executor2@example.com"
        }
    ]
    
    # Добавляем пользователей
    for user_data in test_users:
        existing = db.query(AdminUser).filter(AdminUser.username == user_data["username"]).first()
        if existing:
            print(f"Пользователь {user_data['username']} уже существует")
            continue
            
        user = AuthService.create_user(
            username=user_data["username"],
            password=user_data["password"],
            role=user_data["role"],
            email=user_data.get("email"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        
        if user:
            print(f"✅ Создан пользователь: {user.username} ({user.role})")
        else:
            print(f"❌ Не удалось создать пользователя: {user_data['username']}")
    
    # Показываем итоговый список
    print("\nИтоговый список пользователей:")
    all_users = db.query(AdminUser).all()
    for user in all_users:
        print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}, Name: {user.first_name or 'Не указано'}")
    
    db.close()

if __name__ == "__main__":
    print("Добавление тестовых пользователей...")
    add_test_users()
    print("Готово!")