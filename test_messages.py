#!/usr/bin/env python3
"""
Тестирование получения сообщений чата из Avito API
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import json

load_dotenv()

AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")
AVITO_USER_ID = os.getenv("AVITO_USER_ID")

async def get_access_token():
    """Получение токена доступа"""
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
            result = await response.json()
            return result["access_token"]

async def test_messages():
    """Тест получения сообщений"""
    token = await get_access_token()
    
    # ID первого чата из предыдущего теста
    chat_id = "u2i-tIiKX21UKaBNFasNXH5v3A"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    params = {
        "limit": 10,
        "offset": 0
    }
    
    url = f"https://api.avito.ru/messenger/v3/accounts/{AVITO_USER_ID}/chats/{chat_id}/messages/"
    
    print(f"Запрос сообщений для чата: {chat_id}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response_text = await response.text()
            print(f"Status: {response.status}")
            
            if response.status == 200:
                try:
                    data = await response.json()
                    print(f"\nСтруктура ответа:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                    
                    # Проверяем тип данных
                    print(f"\nТип data: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Ключи: {list(data.keys())}")
                        if "messages" in data:
                            messages = data["messages"]
                            print(f"Тип messages: {type(messages)}")
                            print(f"Количество сообщений: {len(messages)}")
                            if messages:
                                print(f"Первое сообщение: {messages[0]}")
                    elif isinstance(data, list):
                        print(f"Список с {len(data)} элементами")
                        if data:
                            print(f"Первый элемент: {data[0]}")
                            
                except Exception as e:
                    print(f"Ошибка парсинга JSON: {e}")
                    print(f"Raw response: {response_text[:500]}")
            else:
                print(f"Ошибка API: {response_text}")

asyncio.run(test_messages())