#!/usr/bin/env python3
"""Test WebSocket connection to voice assistant endpoint"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/voice-assistant"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")

            # Wait for welcome message
            welcome = await websocket.recv()
            print(f"Received: {welcome}")

            # Send a test message
            test_message = {
                'type': 'speech',
                'text': 'Привет, сколько стоит разработка бота?',
                'speaker': 'client',
            }

            await websocket.send(json.dumps(test_message))
            print(f"Sent: {test_message}")

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Response: {response}")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed with status code: {e.status_code}")
        print(f"Headers: {e.headers}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
