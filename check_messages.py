#!/usr/bin/env python3
"""
Быстрая проверка новых сообщений Avito (без Redis логов)
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Отключаем логирование Redis и других шумных модулей
logging.getLogger('aioredis').setLevel(logging.ERROR)
logging.getLogger('redis').setLevel(logging.ERROR)
logging.getLogger('app.services.avito_service').setLevel(logging.ERROR)

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def check_new_messages():
    """Быстрая проверка новых сообщений"""
    print("🔍 Проверка новых сообщений Avito...")
    
    try:
        from app.config.settings import settings
        from app.services.avito_service import init_avito_service
        
        # Инициализация без логов
        user_id = int(settings.AVITO_USER_ID)
        service = init_avito_service(settings.AVITO_CLIENT_ID, settings.AVITO_CLIENT_SECRET, user_id)
        
        # Получаем чаты
        chats = await service.get_chats(limit=10)
        print(f"📊 Проверяем {len(chats)} чатов...")
        
        total_new = 0
        current_time = datetime.now().timestamp()
        last_24h = current_time - 86400  # 24 часа назад
        last_1h = current_time - 3600    # 1 час назад
        
        for i, chat in enumerate(chats[:5], 1):  # Проверяем только первые 5 чатов
            try:
                messages = await service.get_chat_messages(chat.id, limit=50)
                
                # Считаем новые сообщения
                new_24h = [msg for msg in messages if msg.created > last_24h and msg.author_id != user_id]
                new_1h = [msg for msg in messages if msg.created > last_1h and msg.author_id != user_id]
                
                if new_24h:
                    # Получаем имя собеседника
                    user_name = "Неизвестный"
                    for user in chat.users:
                        if user['id'] != user_id:
                            user_name = user.get('name', f"User {user['id']}")
                            break
                    
                    print(f"🗨️  Чат {i}: {user_name}")
                    print(f"   📅 24ч: {len(new_24h)} сообщений")
                    print(f"   ⏰ 1ч: {len(new_1h)} сообщений")
                    
                    # Показываем последние сообщения
                    for msg in new_1h[-2:]:  # Последние 2 за час
                        msg_time = datetime.fromtimestamp(msg.created).strftime("%H:%M")
                        text = msg.content.get('text', 'Без текста')[:60]
                        if len(text) == 60:
                            text += "..."
                        print(f"   ⬅️  {msg_time}: {text}")
                    
                    total_new += len(new_24h)
                    
            except Exception as e:
                print(f"   ❌ Ошибка в чате {i}: {e}")
        
        print(f"\n📊 Итого новых сообщений за 24ч: {total_new}")
        
        if total_new == 0:
            print("✅ Нет новых входящих сообщений за последние 24 часа")
        
        return total_new > 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Главная функция"""
    try:
        result = asyncio.run(check_new_messages())
        if result:
            print("\n🎉 Найдены новые сообщения!")
        else:
            print("\n💤 Новых сообщений нет")
    except KeyboardInterrupt:
        print("\n👋 Проверка прервана")
    except Exception as e:
        print(f"\n💥 Ошибка: {e}")

if __name__ == "__main__":
    main()