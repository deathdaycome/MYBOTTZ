#!/usr/bin/env python3
"""
Тестирование получения чатов из Avito API
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
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
    
    print(f"Getting access token for client_id: {AVITO_CLIENT_ID[:10]}...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, data=data, headers=headers) as response:
            response_text = await response.text()
            print(f"Token response status: {response.status}")
            
            if response.status != 200:
                print(f"Failed to get access token: {response_text}")
                return None
                
            result = await response.json()
            access_token = result["access_token"]
            expires_in = result.get("expires_in", 3600)
            
            print(f"✅ Access token received, expires in {expires_in} seconds")
            return access_token

async def test_get_chats(access_token):
    """Тест получения чатов"""
    base_url = "https://api.avito.ru"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    params = {
        "limit": 10,
        "offset": 0,
        "unread_only": "false",
        "chat_types": "u2i,u2u"
    }
    
    url = f"{base_url}/messenger/v2/accounts/{AVITO_USER_ID}/chats"
    
    print(f"\n📋 Getting chats for user_id: {AVITO_USER_ID}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response_text = await response.text()
            print(f"Response status: {response.status}")
            
            if response.status == 200:
                try:
                    data = await response.json()
                    chats = data.get("chats", [])
                    
                    print(f"\n✅ Successfully received response")
                    print(f"Total chats found: {len(chats)}")
                    
                    if chats:
                        print("\n📬 First 3 chats:")
                        for i, chat in enumerate(chats[:3], 1):
                            print(f"\n{i}. Chat ID: {chat.get('id')}")
                            print(f"   Created: {datetime.fromtimestamp(chat.get('created', 0))}")
                            print(f"   Users: {len(chat.get('users', []))}")
                            
                            # Информация о последнем сообщении
                            last_msg = chat.get('last_message')
                            if last_msg:
                                print(f"   Last message:")
                                print(f"     - Type: {last_msg.get('type')}")
                                print(f"     - Direction: {last_msg.get('direction')}")
                                content = last_msg.get('content', {})
                                if content.get('text'):
                                    text_preview = content['text'][:50] + "..." if len(content['text']) > 50 else content['text']
                                    print(f"     - Text: {text_preview}")
                    else:
                        print("\n⚠️ No chats found. This could mean:")
                        print("   1. The account has no active chats")
                        print("   2. The User ID is incorrect")
                        print("   3. The API permissions are insufficient")
                        
                        # Проверяем структуру ответа
                        print(f"\n📄 Full response structure:")
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                        
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse JSON response")
                    print(f"Response text: {response_text[:500]}")
            else:
                print(f"\n❌ API request failed")
                print(f"Response: {response_text[:500]}")
                
                if response.status == 403:
                    print("\n⚠️ 403 Forbidden - Possible issues:")
                    print("   1. Wrong User ID")
                    print("   2. Insufficient permissions")
                    print("   3. App doesn't have access to this account")
                elif response.status == 401:
                    print("\n⚠️ 401 Unauthorized - Token might be invalid")

async def main():
    print("=" * 50)
    print("🔍 Testing Avito API - Get Chats")
    print("=" * 50)
    
    print(f"\n📝 Configuration:")
    print(f"Client ID: {AVITO_CLIENT_ID[:10]}...")
    print(f"User ID: {AVITO_USER_ID}")
    
    if not all([AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_USER_ID]):
        print("\n❌ Missing required environment variables!")
        print("Please check your .env file")
        return
    
    # Получаем токен
    token = await get_access_token()
    if not token:
        print("\n❌ Failed to get access token")
        return
    
    # Тестируем получение чатов
    await test_get_chats(token)
    
    print("\n" + "=" * 50)
    print("✅ Test completed")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())