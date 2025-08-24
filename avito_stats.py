#!/usr/bin/env python3
"""
Быстрая статистика Avito без логов - только цифры
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Полностью отключаем логирование
logging.disable(logging.CRITICAL)
os.environ['PYTHONWARNINGS'] = 'ignore'

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def get_stats():
    """Получаем быструю статистику"""
    try:
        from app.config.settings import settings
        from app.services.avito_service import init_avito_service
        
        user_id = int(settings.AVITO_USER_ID)
        service = init_avito_service(settings.AVITO_CLIENT_ID, settings.AVITO_CLIENT_SECRET, user_id)
        
        chats = await service.get_chats(limit=20)
        
        stats = {
            'chats': len(chats),
            'unread': sum(chat.unread_count for chat in chats),
            'total_messages': 0,
            'new_messages': 0
        }
        
        # Проверяем сообщения в первых 5 чатах
        from datetime import datetime
        yesterday = datetime.now().timestamp() - 86400
        
        for chat in chats[:5]:
            try:
                messages = await service.get_chat_messages(chat.id, limit=30)
                stats['total_messages'] += len(messages)
                
                # Новые сообщения от других пользователей
                new = [msg for msg in messages if msg.created > yesterday and msg.author_id != user_id]
                stats['new_messages'] += len(new)
                
            except:
                continue
        
        return stats
        
    except Exception as e:
        return {'error': str(e)}

def main():
    """Главная функция"""
    result = asyncio.run(get_stats())
    
    if 'error' in result:
        print(f"❌ Ошибка: {result['error']}")
    else:
        print(f"📊 Avito Stats:")
        print(f"   Чатов: {result['chats']}")
        print(f"   Непрочитанных: {result['unread']}")
        print(f"   Сообщений (5 чатов): {result['total_messages']}")
        print(f"   Новых за 24ч: {result['new_messages']}")
        
        if result['new_messages'] > 0:
            print(f"✅ Есть новые сообщения!")
        else:
            print(f"💤 Новых сообщений нет")

if __name__ == "__main__":
    main()