#!/usr/bin/env python3
"""Test WebSocket with fixed detect_question logic"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = "wss://nikolaevcodev.ru/ws/voice-assistant"

    print(f"Подключаемся к {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket подключен!")

            # Ждем приветственное сообщение
            welcome = await websocket.recv()
            print(f"Получено: {welcome}")

            # Отправляем тестовое сообщение (НЕ вопрос)
            test_message = {
                'type': 'speech',
                'text': 'Давай зададим вопрос подскажи сколько будет стоить бот для автосервиса',
                'speaker': 'client',
                'timestamp': '2025-11-21T21:30:00Z'
            }

            print(f"\n📤 Отправляем тест: '{test_message['text']}'")
            await websocket.send(json.dumps(test_message))

            # Ждем ответ (с таймаутом)
            print("⏳ Ждем AI suggestion...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                print(f"\n✅ ПОЛУЧЕН ОТВЕТ:")
                print(f"{response}")

                data = json.parse(response)
                if data.get('type') == 'suggestion':
                    print(f"\n🎯 AI SUGGESTION:")
                    print(f"   Вопрос: {data.get('question')}")
                    print(f"   Ответ: {data.get('answer')}")
                    print(f"   Категория: {data.get('category')}")
                    print(f"   Уверенность: {data.get('confidence')}")
                    return True
            except asyncio.TimeoutError:
                print("❌ TIMEOUT: Ответ не получен за 15 секунд")
                return False

    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    sys.exit(0 if success else 1)
