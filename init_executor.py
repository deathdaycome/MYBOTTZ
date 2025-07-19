#!/usr/bin/env python3
"""
Скрипт для создания исполнителя в админ-панели

Этот скрипт создает нового пользователя-исполнителя в системе.
Используется для тестирования системы ролей.

Пример использования:
python init_executor.py --username executor1 --password password123 --name "Иван Исполнитель"
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_connection
from app.database.models import AdminUser
from app.services.auth_service import AuthService


def create_executor(username: str, password: str, full_name: str = None):
    """Создать нового исполнителя"""
    
    print(f"🔨 Создание исполнителя '{username}'...")
    
    # Получаем соединение с БД
    db = next(get_db_connection())
    
    try:
        # Проверяем, не существует ли уже такой пользователь
        existing_user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing_user:
            print(f"❌ Пользователь '{username}' уже существует!")
            return False
        
        # Создаем нового исполнителя
        new_executor = AdminUser(
            username=username,
            password_hash=AuthService.hash_password(password),
            first_name=full_name or username,
            role="executor",
            is_active=True,
            created_at=datetime.now()
        )
        
        db.add(new_executor)
        db.commit()
        db.refresh(new_executor)
        
        print(f"✅ Исполнитель '{username}' успешно создан!")
        print(f"   ID: {new_executor.id}")
        print(f"   Имя: {new_executor.first_name}")
        print(f"   Роль: {new_executor.role}")
        print(f"   Активен: {new_executor.is_active}")
        print(f"   Создан: {new_executor.created_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании исполнителя: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_executors():
    """Показать список всех исполнителей"""
    
    print("📋 Список исполнителей:")
    
    db = next(get_db_connection())
    
    try:
        executors = db.query(AdminUser).filter(AdminUser.role == "executor").all()
        
        if not executors:
            print("   Исполнители не найдены")
            return
        
        print(f"   Найдено исполнителей: {len(executors)}")
        print()
        
        for executor in executors:
            status = "🟢 Активен" if executor.is_active else "🔴 Неактивен"
            print(f"   ID: {executor.id}")
            print(f"   Имя пользователя: {executor.username}")
            print(f"   Полное имя: {executor.first_name}")
            print(f"   Статус: {status}")
            print(f"   Создан: {executor.created_at}")
            print(f"   Последний вход: {executor.last_login}")
            print("   " + "-" * 40)
        
    except Exception as e:
        print(f"❌ Ошибка при получении списка: {e}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Управление исполнителями админ-панели")
    parser.add_argument("--username", "-u", help="Имя пользователя исполнителя")
    parser.add_argument("--password", "-p", help="Пароль исполнителя")
    parser.add_argument("--name", "-n", help="Полное имя исполнителя")
    parser.add_argument("--list", "-l", action="store_true", help="Показать список исполнителей")
    
    args = parser.parse_args()
    
    print("🤖 Управление исполнителями BotDev Admin")
    print("=" * 50)
    
    if args.list:
        list_executors()
        return
    
    if not args.username or not args.password:
        print("❌ Необходимо указать имя пользователя и пароль!")
        print("Пример: python init_executor.py -u executor1 -p password123 -n 'Иван Исполнитель'")
        sys.exit(1)
    
    # Создаем исполнителя
    success = create_executor(args.username, args.password, args.name)
    
    if success:
        print()
        print("🎉 Исполнитель готов к работе!")
        print(f"   URL админ-панели: http://localhost:8000/admin/")
        print(f"   Логин: {args.username}")
        print(f"   Пароль: {args.password}")
        print()
        print("💡 Для просмотра всех исполнителей используйте:")
        print("   python init_executor.py --list")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
