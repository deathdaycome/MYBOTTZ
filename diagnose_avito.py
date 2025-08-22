#!/usr/bin/env python3
"""
Диагностика проблем с Avito API
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test_token():
    """Проверка получения токена и его содержимого"""
    
    client_id = os.getenv("AVITO_CLIENT_ID")
    client_secret = os.getenv("AVITO_CLIENT_SECRET")
    user_id = os.getenv("AVITO_USER_ID")
    
    print("=" * 60)
    print("ДИАГНОСТИКА AVITO API")
    print("=" * 60)
    print(f"\nClient ID: {client_id}")
    print(f"User ID: {user_id}")
    print(f"Client Secret: {'***' + client_secret[-4:] if client_secret else 'НЕ УСТАНОВЛЕН'}")
    
    # Получаем токен
    print("\n" + "=" * 60)
    print("1. ПОЛУЧЕНИЕ ТОКЕНА")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print(f"Отправка запроса на https://api.avito.ru/token")
        print(f"Grant type: client_credentials")
        
        async with session.post("https://api.avito.ru/token", data=data, headers=headers) as response:
            result = await response.json()
            
            print(f"\nСтатус ответа: {response.status}")
            
            if response.status == 200:
                access_token = result.get("access_token")
                scope = result.get("scope", "Не указан")
                expires_in = result.get("expires_in", "Не указан")
                
                print(f"✅ Токен получен успешно")
                print(f"   Scope: {scope}")
                print(f"   Expires in: {expires_in} секунд")
                print(f"   Token (первые 30 символов): {access_token[:30]}...")
                
                # Пробуем декодировать токен (если это JWT)
                try:
                    import base64
                    # JWT состоит из трех частей, разделенных точками
                    parts = access_token.split('.')
                    if len(parts) == 3:
                        # Декодируем payload (вторая часть)
                        payload = parts[1]
                        # Добавляем padding если нужно
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.b64decode(payload)
                        payload_data = json.loads(decoded)
                        print(f"\n   Информация из токена:")
                        for key, value in payload_data.items():
                            if key not in ['exp', 'iat', 'jti']:
                                print(f"     {key}: {value}")
                except:
                    print("\n   (Токен не является JWT или не может быть декодирован)")
                
                return access_token
            else:
                print(f"❌ Ошибка получения токена:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return None
    
    print("\n" + "=" * 60)
    
async def test_api_with_token(token):
    """Тестирование различных endpoint'ов API"""
    
    if not token:
        print("\n❌ Токен не получен, тестирование API невозможно")
        return
    
    user_id = os.getenv("AVITO_USER_ID")
    
    print("\n" + "=" * 60)
    print("2. ТЕСТИРОВАНИЕ API ENDPOINTS")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    # Список endpoint'ов для тестирования
    endpoints = [
        {
            "name": "Получение чатов (v2)",
            "method": "GET",
            "url": f"https://api.avito.ru/messenger/v2/accounts/{user_id}/chats",
            "params": {"limit": 1}
        },
        {
            "name": "Получение чатов (v1)",
            "method": "GET", 
            "url": f"https://api.avito.ru/messenger/v1/accounts/{user_id}/chats",
            "params": {"limit": 1}
        },
        {
            "name": "Получение подписок",
            "method": "POST",
            "url": "https://api.avito.ru/messenger/v1/subscriptions",
            "json": {}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            print(f"\nТестирование: {endpoint['name']}")
            print(f"  URL: {endpoint['url']}")
            
            kwargs = {"headers": headers}
            if "params" in endpoint:
                kwargs["params"] = endpoint["params"]
            if "json" in endpoint:
                kwargs["json"] = endpoint["json"]
            
            try:
                async with session.request(
                    endpoint["method"], 
                    endpoint["url"], 
                    **kwargs
                ) as response:
                    
                    response_text = await response.text()
                    print(f"  Статус: {response.status}")
                    
                    if response.status == 200:
                        print(f"  ✅ Успешно")
                        try:
                            data = json.loads(response_text)
                            if "chats" in data:
                                print(f"  Количество чатов: {len(data.get('chats', []))}")
                            else:
                                print(f"  Ответ: {response_text[:100]}...")
                        except:
                            print(f"  Ответ: {response_text[:100]}...")
                    else:
                        print(f"  ❌ Ошибка: {response_text}")
                        
            except Exception as e:
                print(f"  ❌ Исключение: {e}")

async def main():
    token = await test_token()
    await test_api_with_token(token)
    
    print("\n" + "=" * 60)
    print("РЕКОМЕНДАЦИИ")
    print("=" * 60)
    print("""
Если вы получаете ошибку 403 "permission denied":

1. Убедитесь, что User ID соответствует владельцу приложения
   - User ID должен быть ID аккаунта, который создал приложение в Avito

2. Проверьте настройки приложения в личном кабинете Avito:
   - Перейдите в раздел API на Avito
   - Убедитесь, что приложение активно
   - Проверьте, что у приложения есть доступ к messenger API

3. Возможно, нужно использовать authorization_code flow вместо client_credentials:
   - Это требует авторизации через браузер
   - Пользователь должен дать разрешение приложению

4. Проверьте корректность User ID:
   - Это должен быть числовой ID вашего аккаунта Avito
   - Его можно найти в личном кабинете или в URL профиля
""")

if __name__ == "__main__":
    asyncio.run(main())