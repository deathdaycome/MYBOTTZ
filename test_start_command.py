#!/usr/bin/env python3
"""
Тест команды /start
"""
import asyncio
from unittest.mock import MagicMock, AsyncMock
from app.bot.handlers.start import StartHandler
from app.config.settings import get_settings

class MockUser:
    def __init__(self, id, username="test_user", first_name="Test", last_name="User"):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

class MockMessage:
    def __init__(self, user):
        self.reply_text = AsyncMock()
        self.from_user = user

class MockUpdate:
    def __init__(self, user_id=123, username="test_user"):
        self.effective_user = MockUser(user_id, username)
        self.message = MockMessage(self.effective_user)
        self.callback_query = None

async def test_start_command():
    """Тест команды /start"""
    print("🔧 Тестирование команды /start...")
    
    # Проверяем настройки
    settings = get_settings()
    if not settings.BOT_TOKEN:
        print("❌ BOT_TOKEN не установлен")
        return False
    
    print(f"✅ BOT_TOKEN: {settings.BOT_TOKEN[:10]}...")
    
    # Создаем объекты для теста
    start_handler = StartHandler()
    update = MockUpdate()
    context = MagicMock()
    
    try:
        # Вызываем команду /start
        await start_handler.start(update, context)
        
        # Проверяем, что reply_text был вызван
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            text = call_args[0][0] if call_args[0] else ""
            reply_markup = call_args[1]['reply_markup'] if 'reply_markup' in call_args[1] else None
            
            print("✅ Команда /start выполнена успешно")
            print(f"📝 Текст приветствия: {text[:100]}...")
            
            if reply_markup:
                print("⌨️ Клавиатура:")
                for row in reply_markup.inline_keyboard:
                    for button in row:
                        print(f"  - {button.text}")
                return True
            else:
                print("❌ Клавиатура не найдена")
                return False
        else:
            print("❌ reply_text не был вызван")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_help_command():
    """Тест команды /help"""
    print("\n🔧 Тестирование команды /help...")
    
    start_handler = StartHandler()
    update = MockUpdate()
    context = MagicMock()
    
    try:
        await start_handler.help(update, context)
        
        if update.message.reply_text.called:
            print("✅ Команда /help выполнена успешно")
            return True
        else:
            print("❌ reply_text не был вызван для /help")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании /help: {e}")
        return False

async def main():
    print("🚀 Тестирование команд бота...")
    
    start_result = await test_start_command()
    help_result = await test_help_command()
    
    if start_result and help_result:
        print("\n✅ Все тесты прошли успешно!")
        print("\n💡 Если команды не работают в боте, проверьте:")
        print("  1. Запущен ли бот (python run.py)")
        print("  2. Правильность токена бота")
        print("  3. Настройки webhook (если используется)")
        print("  4. Логи бота на наличие ошибок")
    else:
        print("\n❌ Некоторые тесты не прошли")

if __name__ == "__main__":
    asyncio.run(main())