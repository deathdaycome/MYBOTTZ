#!/usr/bin/env python3
"""
Тест уведомлений Avito
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_notifications():
    """Тестирует уведомления Avito"""
    
    # Проверяем переменные окружения
    from app.config.settings import settings
    
    print("=== ПРОВЕРКА КОНФИГУРАЦИИ ===")
    print(f"BOT_TOKEN: {'***' + settings.BOT_TOKEN[-4:] if settings.BOT_TOKEN else 'НЕ ЗАДАН'}")
    print(f"ADMIN_CHAT_ID: {settings.ADMIN_CHAT_ID if settings.ADMIN_CHAT_ID else 'НЕ ЗАДАН'}")
    print(f"OPENROUTER_API_KEY: {'***' + settings.OPENROUTER_API_KEY[-4:] if settings.OPENROUTER_API_KEY else 'НЕ ЗАДАН'}")
    
    if not settings.BOT_TOKEN:
        print("❌ BOT_TOKEN не установлен!")
        return
        
    if not settings.ADMIN_CHAT_ID:
        print("❌ ADMIN_CHAT_ID не установлен!")
        return
    
    # Тестируем отправку уведомления
    print("\n=== ТЕСТ УВЕДОМЛЕНИЯ ===")
    try:
        from app.services.notification_service import NotificationService
        from telegram import Bot
        
        # Создаем бота
        bot = Bot(token=settings.BOT_TOKEN)
        
        # Создаем сервис уведомлений
        notification_service = NotificationService()
        notification_service.set_bot(bot)
        
        # Отправляем тестовое уведомление
        test_message = """
🧪 <b>Тест уведомлений Avito</b>

Это тестовое сообщение для проверки работы уведомлений о новых сообщениях в Avito.

🔧 Если вы видите это сообщение - уведомления работают правильно!
        """
        
        result = await notification_service.send_admin_notification(test_message.strip())
        
        if result:
            print("✅ Тестовое уведомление отправлено успешно!")
        else:
            print("❌ Ошибка отправки тестового уведомления")
            
    except Exception as e:
        print(f"❌ Ошибка в тесте уведомлений: {e}")
    
    # Тестируем Avito polling сервис
    print("\n=== ТЕСТ AVITO POLLING ===")
    try:
        from app.services.avito_polling_service import polling_service
        
        print(f"Polling активен: {polling_service.polling_active}")
        print(f"Автоответы включены: {polling_service.auto_response_enabled}")
        print(f"Известных чатов: {len(polling_service.known_messages)}")
        
        # Проверим Avito сервис
        from app.services.avito_service import get_avito_service
        avito_service = await get_avito_service()
        
        if avito_service:
            print("✅ Avito сервис доступен")
            
            # Попробуем получить чаты
            try:
                chats = await avito_service.get_chats()
                print(f"✅ Найдено чатов: {len(chats) if chats else 0}")
            except Exception as e:
                print(f"⚠️ Ошибка получения чатов: {e}")
        else:
            print("❌ Avito сервис недоступен")
            
    except Exception as e:
        print(f"❌ Ошибка в тесте polling: {e}")
    
    print("\n=== КОНЕЦ ТЕСТИРОВАНИЯ ===")

def main():
    print("🧪 Запуск тестирования уведомлений Avito...")
    print("=" * 50)
    
    try:
        asyncio.run(test_notifications())
    except KeyboardInterrupt:
        print("\n👋 Тестирование прервано пользователем.")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

if __name__ == "__main__":
    main()