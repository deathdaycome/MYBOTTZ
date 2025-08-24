#!/usr/bin/env python3
"""
Скрипт для тестирования получения сообщений Avito
Полезен для проверки работы на сервере
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_avito_messages():
    """Тестирует получение сообщений Avito"""
    print("🔧 Тест получения сообщений Avito")
    print("=" * 50)
    
    try:
        from app.config.settings import settings
        from app.services.avito_service import get_avito_service, init_avito_service
        
        # Проверяем конфигурацию
        print("📋 Проверка конфигурации:")
        print(f"   CLIENT_ID: {settings.AVITO_CLIENT_ID[:10]}..." if settings.AVITO_CLIENT_ID else "   CLIENT_ID: НЕ ЗАДАН")
        print(f"   CLIENT_SECRET: {'***' if settings.AVITO_CLIENT_SECRET else 'НЕ ЗАДАН'}")
        print(f"   USER_ID: {settings.AVITO_USER_ID}")
        
        if not all([settings.AVITO_CLIENT_ID, settings.AVITO_CLIENT_SECRET, settings.AVITO_USER_ID]):
            print("❌ Не все переменные окружения заданы!")
            return False
        
        # Инициализируем сервис
        print("\n🔄 Инициализация сервиса...")
        try:
            user_id = int(settings.AVITO_USER_ID)
            service = init_avito_service(settings.AVITO_CLIENT_ID, settings.AVITO_CLIENT_SECRET, user_id)
            print(f"✅ Сервис инициализирован с User ID: {user_id}")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
        
        # Тест получения чатов
        print("\n📞 Тест получения чатов...")
        try:
            chats = await service.get_chats(limit=10)
            print(f"✅ Получено {len(chats)} чатов")
            
            if not chats:
                print("⚠️  Нет активных чатов для тестирования сообщений")
                return True
            
        except Exception as e:
            print(f"❌ Ошибка получения чатов: {e}")
            return False
        
        # Тест получения сообщений из первых 3 чатов
        print("\n💬 Тест получения сообщений:")
        total_messages = 0
        new_messages_count = 0
        
        for i, chat in enumerate(chats[:3]):
            print(f"\n🗨️  Чат {i+1}: {chat.id}")
            
            # Получаем пользователей чата
            users = []
            for user in chat.users:
                if user['id'] != user_id:  # Исключаем себя
                    users.append(user.get('name', f"User {user['id']}"))
            
            print(f"   👥 Участники: {', '.join(users) if users else 'Неизвестно'}")
            print(f"   📅 Обновлен: {chat.updated_datetime}")
            print(f"   🔢 Непрочитанных: {chat.unread_count}")
            
            try:
                messages = await service.get_chat_messages(chat.id, limit=20)
                print(f"   📨 Сообщений: {len(messages)}")
                total_messages += len(messages)
                
                # Анализируем последние сообщения
                recent_messages = [msg for msg in messages[-5:] if msg.created > (datetime.now().timestamp() - 86400)]  # За последние 24 часа
                if recent_messages:
                    new_messages_count += len(recent_messages)
                    print(f"   🆕 Новых (24ч): {len(recent_messages)}")
                    
                    # Показываем последние сообщения
                    for msg in recent_messages[-2:]:  # Последние 2
                        direction = "➡️" if msg.direction == "out" else "⬅️"
                        msg_time = datetime.fromtimestamp(msg.created).strftime("%H:%M")
                        text = msg.content.get('text', 'Без текста')[:50]
                        if len(text) == 50:
                            text += "..."
                        print(f"      {direction} {msg_time}: {text}")
                else:
                    print("   📭 Нет новых сообщений за 24ч")
                
            except Exception as e:
                print(f"   ❌ Ошибка получения сообщений: {e}")
        
        # Итоговая статистика
        print(f"\n📊 Итоговая статистика:")
        print(f"   📊 Всего чатов проверено: {min(3, len(chats))}")
        print(f"   💬 Всего сообщений: {total_messages}")
        print(f"   🆕 Новых сообщений (24ч): {new_messages_count}")
        
        # Тест уведомлений (если есть новые сообщения)
        if new_messages_count > 0:
            print(f"\n🔔 Тест уведомлений:")
            try:
                from app.services.notification_service import NotificationService
                notification_service = NotificationService()
                
                # Проверяем настройки уведомлений
                if settings.BOT_TOKEN and settings.ADMIN_CHAT_ID:
                    print(f"   ✅ BOT_TOKEN: ***{settings.BOT_TOKEN[-4:]}")
                    print(f"   ✅ ADMIN_CHAT_ID: {settings.ADMIN_CHAT_ID}")
                    
                    # Отправляем тестовое уведомление
                    test_message = f"🧪 Тест Avito уведомлений\\n\\n📊 Найдено {new_messages_count} новых сообщений в {min(3, len(chats))} чатах"
                    await notification_service.send_admin_notification(test_message)
                    print("   ✅ Тестовое уведомление отправлено")
                else:
                    print("   ⚠️  Настройки уведомлений не заданы")
                    
            except Exception as e:
                print(f"   ❌ Ошибка тестирования уведомлений: {e}")
        
        print(f"\n🎉 Тест завершен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка теста: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

async def test_polling_service():
    """Тестирует работу polling сервиса"""
    print("\n🔄 Тест Avito Polling сервиса:")
    print("-" * 30)
    
    try:
        from app.services.avito_polling_service import polling_service
        
        print(f"📋 Статус polling:")
        print(f"   🔄 Активен: {polling_service.polling_active}")
        print(f"   🤖 Автоответы: {polling_service.auto_response_enabled}")
        print(f"   📱 NotificationService: {polling_service.notification_service is not None}")
        print(f"   💾 Известных чатов: {len(polling_service.known_messages)}")
        
        # Запускаем один цикл проверки
        print(f"\n🔍 Запуск одного цикла проверки сообщений...")
        await polling_service.check_new_messages()
        print(f"✅ Цикл проверки выполнен")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования polling: {e}")

def main():
    """Главная функция"""
    print("🧪 Тестирование Avito сообщений на сервере")
    print("=" * 60)
    
    try:
        # Основной тест
        success = asyncio.run(test_avito_messages())
        
        if success:
            # Дополнительный тест polling сервиса
            asyncio.run(test_polling_service())
            print("\n✅ Все тесты пройдены успешно!")
        else:
            print("\n❌ Тесты завершились с ошибками!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Тест прерван пользователем")
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()