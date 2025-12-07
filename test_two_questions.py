#!/usr/bin/env python3
"""Test WebSocket with TWO questions to reproduce the issue"""

import asyncio
import websockets
import json
import sys

async def test_two_questions():
    uri = "wss://nikolaevcodev.ru/ws/voice-assistant"

    print(f"🔌 Подключаемся к {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket подключен!\n")

            # Ждем приветственное сообщение
            welcome = await websocket.recv()
            print(f"📨 Приветствие: {welcome}\n")

            # ========================================
            # ПЕРВЫЙ ВОПРОС (должен работать)
            # ========================================
            question1 = {
                'type': 'speech',
                'text': 'Сколько стоит разработка бота для ремонта телефонов?',
                'speaker': 'client',
                'timestamp': '2025-11-21T21:30:00Z'
            }

            print(f"📤 ВОПРОС 1: '{question1['text']}'")
            await websocket.send(json.dumps(question1))

            try:
                response1 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                print(f"✅ ОТВЕТ 1 ПОЛУЧЕН:")
                data1 = json.loads(response1)
                if data1.get('type') == 'suggestion':
                    print(f"   🤖 AI: {data1.get('answer', 'N/A')[:100]}...")
                    print(f"   📊 Категория: {data1.get('category')}")
                else:
                    print(f"   ⚠️  Получен не suggestion: {data1}")
            except asyncio.TimeoutError:
                print(f"❌ ОТВЕТ 1: TIMEOUT (15 секунд)")
                return False

            print("\n" + "="*60 + "\n")

            # Небольшая задержка перед вторым вопросом
            await asyncio.sleep(1)

            # ========================================
            # ВТОРОЙ ВОПРОС (НЕ работает по словам пользователя)
            # ========================================
            question2 = {
                'type': 'speech',
                'text': 'А какие сроки разработки такого бота?',
                'speaker': 'client',
                'timestamp': '2025-11-21T21:31:00Z'
            }

            print(f"📤 ВОПРОС 2: '{question2['text']}'")
            await websocket.send(json.dumps(question2))

            try:
                response2 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                print(f"✅ ОТВЕТ 2 ПОЛУЧЕН:")
                data2 = json.loads(response2)
                if data2.get('type') == 'suggestion':
                    print(f"   🤖 AI: {data2.get('answer', 'N/A')[:100]}...")
                    print(f"   📊 Категория: {data2.get('category')}")
                    print("\n🎉 ОБА ВОПРОСА РАБОТАЮТ!")
                    return True
                else:
                    print(f"   ⚠️  Получен не suggestion: {data2}")
            except asyncio.TimeoutError:
                print(f"❌ ОТВЕТ 2: TIMEOUT (15 секунд)")
                print(f"\n🐛 ПРОБЛЕМА ВОСПРОИЗВЕДЕНА: Второй вопрос не получает ответ!")
                return False

    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("ТЕСТ: Отправка ДВУХ вопросов подряд")
    print("="*60)
    print()

    success = asyncio.run(test_two_questions())

    print("\n" + "="*60)
    if success:
        print("✅ РЕЗУЛЬТАТ: Оба вопроса работают")
        sys.exit(0)
    else:
        print("❌ РЕЗУЛЬТАТ: Второй вопрос не работает")
        sys.exit(1)
