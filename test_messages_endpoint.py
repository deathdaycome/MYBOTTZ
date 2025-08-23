#!/usr/bin/env python3
"""
Тестируем конкретный эндпоинт для сообщений чата
"""

import asyncio
import aiohttp
import base64
import json

# Настройки
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "qwerty123"

async def test_messages_endpoint():
    """Прямой тест эндпоинта для сообщений"""
    print("="*50)
    print("ТЕСТ ЭНДПОИНТА ДЛЯ СООБЩЕНИЙ")
    print("="*50)
    
    # Создаем Basic Auth заголовок
    credentials = base64.b64encode(f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    # ID чата из теста
    chat_id = "u2i-tIiKX21UKaBNFasNXH5v3A"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"1️⃣ Тестируем GET /admin/avito/chats/{chat_id}/messages")
            
            url = f"{BASE_URL}/admin/avito/chats/{chat_id}/messages"
            print(f"URL: {url}")
            
            async with session.get(url, headers=headers) as response:
                status = response.status
                response_text = await response.text()
                
                print(f"Статус: {status}")
                print(f"Заголовки ответа: {dict(response.headers)}")
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        messages = data.get('messages', [])
                        print(f"✅ Получено сообщений: {len(messages)}")
                        
                        if messages:
                            print("Первое сообщение:")
                            first_msg = messages[0]
                            for key, value in first_msg.items():
                                print(f"  {key}: {value}")
                                
                    except json.JSONDecodeError as e:
                        print(f"❌ Ошибка парсинга JSON: {e}")
                        print(f"Raw ответ (первые 500 символов): {response_text[:500]}")
                        
                else:
                    print(f"❌ Ошибка {status}")
                    print(f"Ответ: {response_text}")
                    
                    # Пробуем распарсить как JSON для получения деталей ошибки
                    try:
                        error_data = json.loads(response_text)
                        print(f"Детали ошибки: {error_data}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Исключение: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_messages_endpoint())