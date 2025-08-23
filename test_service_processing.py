#!/usr/bin/env python3
"""
Тест обработки данных в нашем сервисе
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Добавляем путь к app для импорта
sys.path.append(str(Path(__file__).parent / "app"))

from services.avito_service import AvitoService
import os
from dotenv import load_dotenv

load_dotenv()

AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")  
AVITO_USER_ID = int(os.getenv("AVITO_USER_ID", "216012096"))

async def test_service_processing():
    """Тест обработки данных в сервисе"""
    print("="*60)
    print("ТЕСТ ОБРАБОТКИ ДАННЫХ В AVITO SERVICE")
    print("="*60)
    
    service = AvitoService(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_USER_ID)
    
    try:
        print("1️⃣ Тестируем get_chats...")
        
        # Проверяем каждый шаг
        print(f"   User ID установлен: {service.user_id}")
        
        # Получаем токен
        print("   Получаем токен...")
        token = await service._get_access_token()
        print(f"   ✅ Токен получен: {token[:20]}...")
        
        # Делаем запрос напрямую
        print("   Делаем запрос к API...")
        params = {
            "limit": 5,  # Ограничиваем для теста
            "offset": 0,
            "unread_only": "false",
            "chat_types": "u2i,u2u"
        }
        
        result = await service._make_request(
            "GET",
            f"/messenger/v2/accounts/{service.user_id}/chats",
            params=params
        )
        
        print(f"   Тип result: {type(result)}")
        print(f"   Result is None: {result is None}")
        print(f"   Result is dict: {isinstance(result, dict)}")
        
        if result:
            print(f"   Ключи result: {list(result.keys()) if isinstance(result, dict) else 'не dict'}")
            if isinstance(result, dict) and 'chats' in result:
                chats_data = result['chats']
                print(f"   Количество чатов в данных: {len(chats_data)}")
                
                if chats_data:
                    first_chat = chats_data[0]
                    print(f"   Ключи первого чата: {list(first_chat.keys())}")
        
        print("\n2️⃣ Тестируем полный метод get_chats...")
        chats = await service.get_chats(limit=5)
        print(f"   ✅ Получено чатов через get_chats: {len(chats)}")
        
        if chats:
            first_chat = chats[0]
            print(f"   Первый чат:")
            print(f"     ID: {first_chat.id}")
            print(f"     Пользователи: {len(first_chat.users)}")
            print(f"     Последнее сообщение: {first_chat.last_message is not None}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Трассировка:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service_processing())