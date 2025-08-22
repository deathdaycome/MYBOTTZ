#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Avito API
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import logging

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, '.')

async def test_avito_api():
    """Тестирование Avito API"""
    
    # Проверяем переменные окружения
    print("=" * 60)
    print("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 60)
    
    client_id = os.getenv("AVITO_CLIENT_ID")
    client_secret = os.getenv("AVITO_CLIENT_SECRET")
    user_id = os.getenv("AVITO_USER_ID")
    
    print(f"AVITO_CLIENT_ID: {client_id[:10]}..." if client_id else "AVITO_CLIENT_ID: НЕ УСТАНОВЛЕН")
    print(f"AVITO_CLIENT_SECRET: {'Установлен' if client_secret else 'НЕ УСТАНОВЛЕН'}")
    print(f"AVITO_USER_ID: {user_id if user_id else 'НЕ УСТАНОВЛЕН'}")
    
    if not all([client_id, client_secret, user_id]):
        print("\n❌ ОШИБКА: Не все переменные окружения установлены!")
        print("Проверьте файл .env")
        return
    
    print("\n✅ Все переменные окружения установлены")
    
    # Импортируем и инициализируем сервис
    print("\n" + "=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ СЕРВИСА")
    print("=" * 60)
    
    try:
        from app.services.avito_service import AvitoService
        
        service = AvitoService(
            client_id=client_id,
            client_secret=client_secret,
            user_id=int(user_id)
        )
        print("✅ Сервис создан")
        
    except Exception as e:
        print(f"❌ Ошибка при создании сервиса: {e}")
        return
    
    # Получаем токен доступа
    print("\n" + "=" * 60)
    print("ПОЛУЧЕНИЕ ТОКЕНА ДОСТУПА")
    print("=" * 60)
    
    try:
        token = await service._get_access_token()
        print(f"✅ Токен получен: {token[:20]}...")
    except Exception as e:
        print(f"❌ Ошибка при получении токена: {e}")
        print(f"Детали: {str(e)}")
        return
    
    # Получаем список чатов
    print("\n" + "=" * 60)
    print("ПОЛУЧЕНИЕ СПИСКА ЧАТОВ")
    print("=" * 60)
    
    try:
        chats = await service.get_chats(limit=10)
        print(f"✅ Получено чатов: {len(chats)}")
        
        if chats:
            print("\nПервые 3 чата:")
            for i, chat in enumerate(chats[:3], 1):
                print(f"\n  Чат #{i}:")
                print(f"    ID: {chat.id}")
                print(f"    Пользователи: {len(chat.users)}")
                
                if chat.last_message:
                    print(f"    Последнее сообщение:")
                    print(f"      Тип: {chat.last_message.type.value}")
                    print(f"      Направление: {chat.last_message.direction}")
                    if chat.last_message.type.value == "text":
                        text = chat.last_message.content.get("text", "")[:50]
                        print(f"      Текст: {text}...")
        else:
            print("⚠️ Чаты не найдены (возможно их действительно нет)")
            
    except Exception as e:
        print(f"❌ Ошибка при получении чатов: {e}")
        print(f"Детали: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_avito_api())