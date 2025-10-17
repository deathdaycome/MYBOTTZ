#!/usr/bin/env python3
"""
Тест подключения бота к Telegram API
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError

async def test_bot():
    token = "7881909419:AAF_9TD2tZFOsQi2FThkyJt6ICjrWPny3JA"

    print("=" * 80)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К TELEGRAM API")
    print("=" * 80)

    # Создаём бота
    bot = Bot(token)

    try:
        print("\n1. Попытка получить информацию о боте...")
        me = await bot.get_me()
        print(f"✅ Успешно! Бот: @{me.username} ({me.first_name})")
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

    try:
        print("\n2. Попытка получить updates...")
        updates = await bot.get_updates(limit=1, timeout=5)
        print(f"✅ Успешно! Получено {len(updates)} updates")
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    asyncio.run(test_bot())
