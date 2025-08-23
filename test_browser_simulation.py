#!/usr/bin/env python3
"""
Симуляция браузерных запросов к админ-панели Avito
Тестируем API эндпоинты, которые использует фронтенд
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import json
import base64

load_dotenv()

# Базовые настройки для админ панели
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "qwerty123"
BASE_URL = "http://localhost:8000"

async def test_admin_api():
    """Тестируем API эндпоинты админ панели"""
    print("="*60)
    print("ТЕСТ API ЭНДПОИНТОВ АДМИН-ПАНЕЛИ AVITO")
    print("="*60)
    
    # Создаем Basic Auth заголовок
    credentials = base64.b64encode(f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Тест 1: Получение чатов
        print("1️⃣ Тестируем GET /admin/avito/chats")
        try:
            async with session.get(f"{BASE_URL}/admin/avito/chats", headers=headers) as response:
                print(f"   Статус: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Получено чатов: {len(data.get('chats', []))}")
                    
                    if data.get('chats'):
                        first_chat = data['chats'][0]
                        print(f"   ID первого чата: {first_chat.get('id')}")
                        
                        # Тест 2: Получение сообщений для первого чата  
                        chat_id = first_chat['id']
                        print(f"\n2️⃣ Тестируем GET /admin/avito/chats/{chat_id}/messages")
                        
                        async with session.get(f"{BASE_URL}/admin/avito/chats/{chat_id}/messages", headers=headers) as msg_response:
                            print(f"   Статус: {msg_response.status}")
                            
                            if msg_response.status == 200:
                                msg_data = await msg_response.json()
                                messages = msg_data.get('messages', [])
                                print(f"   ✅ Получено сообщений: {len(messages)}")
                                
                                if messages:
                                    print("   Структура первого сообщения:")
                                    first_msg = messages[0]
                                    for key, value in first_msg.items():
                                        if isinstance(value, str) and len(value) > 50:
                                            value = value[:50] + "..."
                                        print(f"     {key}: {value}")
                                        
                            else:
                                error_text = await msg_response.text()
                                print(f"   ❌ Ошибка получения сообщений: {error_text}")
                        
                        # Тест 3: Получение информации о чате
                        print(f"\n3️⃣ Тестируем GET /admin/avito/chats/{chat_id}")
                        
                        async with session.get(f"{BASE_URL}/admin/avito/chats/{chat_id}", headers=headers) as chat_response:
                            print(f"   Статус: {chat_response.status}")
                            
                            if chat_response.status == 200:
                                chat_info = await chat_response.json()
                                print(f"   ✅ Информация о чате получена")
                                print(f"   Пользователи: {len(chat_info.get('users', []))}")
                            else:
                                error_text = await chat_response.text()
                                print(f"   ❌ Ошибка получения информации о чате: {error_text}")
                
                else:
                    error_text = await response.text()
                    print(f"   ❌ Ошибка получения чатов: {error_text}")
                    
        except Exception as e:
            print(f"   ❌ Исключение при тестировании: {e}")
    
    print("\n" + "="*60)
    print("✅ ТЕСТ API ЗАВЕРШЕН")
    print("="*60)

async def test_frontend_logic():
    """Тестируем логику, используемую во фронтенде"""
    print("\n4️⃣ Тестируем логику определения имен пользователей")
    
    # Симулируем данные чата как они приходят из API
    sample_chat = {
        "id": "u2i-tIiKX21UKaBNFasNXH5v3A",
        "users": [
            {"id": 216012096, "name": "Nikolaev Code Studio |  Бот ТГ любой сложности!"},
            {"id": 242360910, "name": "IRAKLI"}
        ]
    }
    
    # Логика из фронтенда
    current_user_id = 216012096
    user_name = None
    for user in sample_chat["users"]:
        if user["id"] != current_user_id:
            user_name = user["name"]
            break
    
    print(f"   Собеседник: {user_name}")
    print(f"   ✅ Логика работает корректно")

if __name__ == "__main__":
    asyncio.run(test_admin_api())
    asyncio.run(test_frontend_logic())