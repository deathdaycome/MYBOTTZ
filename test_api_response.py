#!/usr/bin/env python3
"""
Диагностика ответов от API Avito
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import json

load_dotenv()

AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET") 
AVITO_USER_ID = int(os.getenv("AVITO_USER_ID", "216012096"))

async def diagnose_api():
    """Диагностика всех этапов запроса к API"""
    print("="*60)
    print("ДИАГНОСТИКА API AVITO")
    print("="*60)
    print(f"Client ID: {AVITO_CLIENT_ID[:10]}...")
    print(f"User ID: {AVITO_USER_ID}")
    print()
    
    # Шаг 1: Получение токена
    print("1️⃣ Получение токена...")
    try:
        token = await get_token()
        print(f"✅ Токен получен: {token[:20]}...")
    except Exception as e:
        print(f"❌ Ошибка получения токена: {e}")
        return
    
    # Шаг 2: Тест запроса чатов с детальным анализом
    print("\n2️⃣ Тестирование запроса чатов...")
    await test_chats_request(token)
    
async def get_token():
    """Получение токена"""
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
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Token request failed: {response.status} - {error_text}")
            
            result = await response.json()
            return result["access_token"]

async def test_chats_request(token):
    """Детальный тест запроса чатов"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    params = {
        "limit": 50,
        "offset": 0,
        "unread_only": "false",
        "chat_types": "u2i,u2u"
    }
    
    url = f"https://api.avito.ru/messenger/v2/accounts/{AVITO_USER_ID}/chats"
    
    print(f"URL: {url}")
    print(f"Параметры: {params}")
    print(f"Заголовки: Authorization: Bearer {token[:20]}...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                print(f"\n📡 Статус ответа: {response.status}")
                print(f"📋 Заголовки ответа: {dict(response.headers)}")
                
                # Получаем raw содержимое
                response_bytes = await response.read()
                response_text = response_bytes.decode('utf-8', errors='replace')
                
                print(f"📄 Размер ответа: {len(response_bytes)} байт")
                print(f"🔤 Кодировка: {response.charset or 'не указана'}")
                print(f"📝 Content-Type: {response.content_type}")
                
                print(f"\n🔍 Raw ответ (первые 500 символов):")
                print("─" * 50)
                print(response_text[:500])
                print("─" * 50)
                
                if response.status == 200:
                    try:
                        # Пытаемся парсить JSON
                        data = json.loads(response_text)
                        print(f"\n✅ JSON успешно распарсен")
                        print(f"📊 Тип данных: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"🔑 Ключи: {list(data.keys())}")
                            
                            if 'chats' in data:
                                chats = data['chats']
                                print(f"💬 Найдено чатов: {len(chats)}")
                                
                                if chats:
                                    print(f"📋 Структура первого чата:")
                                    first_chat = chats[0]
                                    for key, value in first_chat.items():
                                        if isinstance(value, (str, int, bool)):
                                            print(f"  {key}: {value}")
                                        else:
                                            print(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                            else:
                                print("⚠️ Ключ 'chats' не найден в ответе")
                                
                        elif isinstance(data, list):
                            print(f"📋 Получен массив с {len(data)} элементами")
                        else:
                            print(f"⚠️ Неожиданный тип данных: {type(data)}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Ошибка парсинга JSON: {e}")
                        print(f"🔍 Проблема в позиции: {e.pos}")
                        
                        # Показываем проблемный участок
                        start = max(0, e.pos - 50)
                        end = min(len(response_text), e.pos + 50)
                        print(f"📍 Контекст ошибки:")
                        print(response_text[start:end])
                        
                else:
                    print(f"❌ API вернул ошибку: {response.status}")
                    print(f"📄 Содержимое ошибки: {response_text}")
                    
        except Exception as e:
            print(f"💥 Исключение при запросе: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_api())