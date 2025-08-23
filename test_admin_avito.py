#!/usr/bin/env python3
"""
Тестирование роутера админки для Avito
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Настройки
BASE_URL = "http://localhost:8001"  # Порт админки
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD", "qwerty123")

def test_avito_chats():
    """Тест получения чатов через админку"""
    
    # Создаем сессию для сохранения cookies
    session = requests.Session()
    
    # Авторизуемся
    print("🔐 Авторизация в админке...")
    auth = (USERNAME, PASSWORD)
    
    # Запрашиваем чаты
    print("📋 Запрос чатов...")
    url = f"{BASE_URL}/avito/chats"
    
    response = session.get(url, auth=auth)
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Успешно получены данные:")
        print(f"Total chats: {data.get('total', 0)}")
        
        chats = data.get('chats', [])
        if chats:
            print(f"\nПервые 3 чата:")
            for i, chat in enumerate(chats[:3], 1):
                print(f"{i}. ID: {chat.get('id')}")
                users = chat.get('users', [])
                print(f"   Users: {[u.get('name') for u in users]}")
        else:
            print("⚠️ Список чатов пуст")
            print(f"Полный ответ: {data}")
    else:
        print(f"❌ Ошибка: {response.text}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 Тест роутера админки Avito")
    print("=" * 50)
    
    test_avito_chats()
    
    print("\n" + "=" * 50)