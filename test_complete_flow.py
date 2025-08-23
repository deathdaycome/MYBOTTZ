#!/usr/bin/env python3
"""
Полный тест функциональности Avito мессенджера
Проверяет весь флоу от авторизации до загрузки сообщений
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import json
import sys
import traceback
from pathlib import Path

# Добавляем путь к app для импорта
sys.path.append(str(Path(__file__).parent / "app"))

from services.avito_service import AvitoService

load_dotenv()

AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")  
AVITO_USER_ID = int(os.getenv("AVITO_USER_ID", "216012096"))

async def test_full_flow():
    """Полный тест всей функциональности"""
    print("="*60)
    print("ПОЛНЫЙ ТЕСТ ФУНКЦИОНАЛЬНОСТИ AVITO МЕССЕНДЖЕРА")
    print("="*60)
    
    if not all([AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_USER_ID]):
        print("❌ Отсутствуют необходимые переменные окружения")
        return
    
    print(f"🔑 Client ID: {AVITO_CLIENT_ID[:10]}...")
    print(f"👤 User ID: {AVITO_USER_ID}")
    print()
    
    # Инициализируем сервис
    avito_service = AvitoService(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_USER_ID)
    
    try:
        # Тест 1: Получение токена
        print("1️⃣ Тестируем получение токена доступа...")
        token = await avito_service._get_access_token()
        print(f"✅ Токен получен: {token[:20]}...")
        print()
        
        # Тест 2: Получение чатов
        print("2️⃣ Тестируем получение списка чатов...")
        chats = await avito_service.get_chats(limit=5)
        print(f"✅ Получено чатов: {len(chats)}")
        
        if not chats:
            print("ℹ️ Нет доступных чатов для тестирования сообщений")
            return
            
        # Показываем информацию о чатах
        for i, chat in enumerate(chats[:3]):
            print(f"   Чат {i+1}: {chat.id}")
            current_user_name = None
            other_user_name = None
            
            for user in chat.users:
                if user.get('id') == AVITO_USER_ID:
                    current_user_name = user.get('name', 'Неизвестный')
                else:
                    other_user_name = user.get('name', 'Неизвестный')
                    
            print(f"   - Текущий пользователь: {current_user_name}")
            print(f"   - Собеседник: {other_user_name}")
            print(f"   - Непрочитанных: {chat.unread_count}")
            
        print()
        
        # Тест 3: Получение сообщений для первого чата
        first_chat = chats[0]
        print(f"3️⃣ Тестируем получение сообщений для чата: {first_chat.id}")
        
        try:
            messages = await avito_service.get_chat_messages(first_chat.id, limit=10)
            print(f"✅ Получено сообщений: {len(messages)}")
            
            if messages:
                print("   Последние 3 сообщения:")
                for msg in messages[-3:]:
                    direction_icon = "📤" if msg.direction == "out" else "📥"
                    content_preview = ""
                    if msg.type.value == "text":
                        content_preview = msg.content.get("text", "")[:50]
                        if len(msg.content.get("text", "")) > 50:
                            content_preview += "..."
                    elif msg.type.value == "image":
                        content_preview = "[Изображение]"
                    elif msg.type.value == "system":
                        content_preview = "[Системное сообщение]"
                    
                    print(f"   {direction_icon} {msg.type.value}: {content_preview}")
                    
        except Exception as e:
            print(f"❌ Ошибка получения сообщений: {e}")
            print("Трассировка:")
            traceback.print_exc()
            
        print()
        
        # Тест 4: Прямой тест API v3 для сообщений
        print("4️⃣ Прямой тест API v3/messages...")
        await test_direct_api_call(first_chat.id)
        
        print()
        print("="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()

async def test_direct_api_call(chat_id):
    """Прямой вызов API для тестирования формата ответа"""
    
    # Получаем токен
    auth_url = "https://api.avito.ru/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AVITO_CLIENT_ID,
        "client_secret": AVITO_CLIENT_SECRET,
        "scope": "messenger:read messenger:write"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, data=data, headers=headers) as response:
            token_data = await response.json()
            token = token_data["access_token"]
    
    # Тестируем API сообщений
    api_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    params = {
        "limit": 5,
        "offset": 0
    }
    
    url = f"https://api.avito.ru/messenger/v3/accounts/{AVITO_USER_ID}/chats/{chat_id}/messages/"
    
    print(f"   Вызываем: {url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=api_headers, params=params) as response:
            response_text = await response.text()
            print(f"   Статус: {response.status}")
            
            if response.status == 200:
                try:
                    data = json.loads(response_text)
                    print(f"   Тип ответа: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"   ✅ API возвращает массив напрямую (длина: {len(data)})")
                        if data:
                            print(f"   Структура первого сообщения: {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"   ✅ API возвращает объект с ключами: {list(data.keys())}")
                        if "messages" in data:
                            messages = data["messages"]
                            print(f"   Сообщений в поле 'messages': {len(messages)}")
                    
                    # Показываем часть JSON для анализа
                    print(f"   JSON (первые 300 символов):")
                    print(f"   {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка парсинга JSON: {e}")
                    print(f"   Raw ответ: {response_text[:200]}...")
            else:
                print(f"   ❌ Ошибка API: {response_text}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())