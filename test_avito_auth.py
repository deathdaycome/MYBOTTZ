#!/usr/bin/env python3
"""
Тестирование авторизации Avito API
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

async def test_avito_auth():
    client_id = os.getenv("AVITO_CLIENT_ID")
    client_secret = os.getenv("AVITO_CLIENT_SECRET")
    user_id = os.getenv("AVITO_USER_ID")
    
    print(f"Client ID: {client_id[:10]}..." if client_id else "Not found")
    print(f"Client Secret: {client_secret[:10]}..." if client_secret else "Not found")
    print(f"User ID: {user_id}")
    
    if not all([client_id, client_secret, user_id]):
        print("ERROR: Missing credentials")
        return
    
    # Тест получения токена
    auth_url = "https://api.avito.ru/token"
    
    async with aiohttp.ClientSession() as session:
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "messenger:read messenger:write"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print("\n1. Testing token endpoint...")
        async with session.post(auth_url, data=data, headers=headers) as response:
            status = response.status
            response_text = await response.text()
            
            print(f"Status: {status}")
            
            if status == 200:
                token_data = json.loads(response_text)
                access_token = token_data.get("access_token")
                print(f"✓ Token received: {access_token[:20]}...")
                print(f"  Expires in: {token_data.get('expires_in')} seconds")
                print(f"  Token type: {token_data.get('token_type')}")
                print(f"  Scope: {token_data.get('scope')}")
                
                # Тест API с токеном
                print("\n2. Testing API with token...")
                api_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
                
                # Пробуем получить чаты
                chats_url = f"https://api.avito.ru/messenger/v2/accounts/{user_id}/chats"
                print(f"   URL: {chats_url}")
                
                async with session.get(chats_url, headers=api_headers) as api_response:
                    api_status = api_response.status
                    api_text = await api_response.text()
                    
                    print(f"   Status: {api_status}")
                    
                    if api_status == 200:
                        chats_data = json.loads(api_text)
                        print(f"   ✓ API works! Chats found: {len(chats_data.get('chats', []))}")
                        if chats_data.get('chats'):
                            print(f"   First chat ID: {chats_data['chats'][0].get('id')}")
                    else:
                        print(f"   ✗ API error: {api_text[:200]}")
                
            else:
                print(f"✗ Auth failed: {response_text[:200]}")
                
                # Детальный разбор ошибки
                try:
                    error_data = json.loads(response_text)
                    print(f"\nError details:")
                    print(f"  Error: {error_data.get('error')}")
                    print(f"  Description: {error_data.get('error_description')}")
                except:
                    print(f"Raw error: {response_text}")

if __name__ == "__main__":
    asyncio.run(test_avito_auth())