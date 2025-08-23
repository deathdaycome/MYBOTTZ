#!/usr/bin/env python3
"""
Получение информации о пользователе через Avito API
Используем OAuth токен для доступа
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

async def get_user_info():
    client_id = os.getenv("AVITO_CLIENT_ID")
    client_secret = os.getenv("AVITO_CLIENT_SECRET")
    
    print("=" * 60)
    print("Avito API - Получение информации о пользователе")
    print("=" * 60)
    print(f"Client ID: {client_id[:10]}..." if client_id else "Not found")
    print(f"Client Secret: {client_secret[:10]}..." if client_secret else "Not found")
    
    # Сначала получаем токен
    auth_url = "https://api.avito.ru/token"
    
    async with aiohttp.ClientSession() as session:
        # Получение токена
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "messenger:read messenger:write user:read items:info"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print("\n1. Получение токена...")
        async with session.post(auth_url, data=data, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                print(f"Ошибка получения токена: {text}")
                return
                
            token_data = await response.json()
            access_token = token_data.get("access_token")
            print(f"✓ Токен получен")
            
        # Теперь пробуем получить информацию о пользователе
        api_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        print("\n2. Попытка получить информацию о текущем пользователе...")
        
        # Попробуем разные endpoints
        endpoints = [
            "/core/v1/accounts/self",  # Информация о себе
            "/messenger/v2/accounts",   # Список аккаунтов
            "/core/v1/accounts",        # Список аккаунтов v1
        ]
        
        for endpoint in endpoints:
            url = f"https://api.avito.ru{endpoint}"
            print(f"\n   Пробуем: {endpoint}")
            
            async with session.get(url, headers=api_headers) as response:
                status = response.status
                text = await response.text()
                
                print(f"   Status: {status}")
                
                if status == 200:
                    try:
                        data = json.loads(text)
                        print(f"   ✓ Успешно!")
                        print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                        
                        # Если есть информация об аккаунте
                        if isinstance(data, dict):
                            if data.get('id'):
                                print(f"\n   >>> USER ID: {data.get('id')} <<<")
                            if data.get('email'):
                                print(f"   Email: {data.get('email')}")
                            if data.get('name'):
                                print(f"   Name: {data.get('name')}")
                        elif isinstance(data, list) and data:
                            print("\n   Найдены аккаунты:")
                            for acc in data:
                                print(f"   - ID: {acc.get('id')}, Name: {acc.get('name')}")
                    except:
                        print(f"   Не удалось распарсить JSON: {text[:200]}")
                else:
                    print(f"   ✗ Ошибка: {text[:200]}")
        
        print("\n" + "=" * 60)
        print("ВАЖНО: User ID из API должен совпадать с ID в личном кабинете Avito")
        print("Проверьте ID в настройках приложения на avito.ru")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(get_user_info())