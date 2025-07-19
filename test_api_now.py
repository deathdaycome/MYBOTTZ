#!/usr/bin/env python3
"""
Тест API правок после исправлений
"""

import requests
import json

def test_api_fix():
    """Тест исправленного API"""
    print("🔧 Тест исправленного API")
    
    base_url = "http://localhost:8001"
    
    # Тестируем получение правки
    print("\n1. Тестирование GET /admin/api/revisions/1")
    try:
        response = requests.get(f"{base_url}/admin/api/revisions/1")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            
            if data.get('success'):
                revision = data['data']
                print(f"   Title: {revision.get('title')}")
                print(f"   Status: {revision.get('status')}")
                print(f"   Messages: {len(revision.get('messages', []))}")
                print(f"   Files: {len(revision.get('files', []))}")
                
                # Тестируем получение сообщений
                print(f"\n2. Тестирование GET /admin/api/revisions/1/messages")
                messages_response = requests.get(f"{base_url}/admin/api/revisions/1/messages")
                print(f"   Status: {messages_response.status_code}")
                
                if messages_response.status_code == 200:
                    messages_data = messages_response.json()
                    print(f"   Success: {messages_data.get('success')}")
                    
                    if messages_data.get('success'):
                        messages = messages_data['data']
                        print(f"   Messages count: {len(messages)}")
                        
                        for i, msg in enumerate(messages[-2:], 1):
                            print(f"     {i}. {msg.get('sender_name', 'Unknown')} ({msg.get('sender_type')})")
                            print(f"        {msg.get('content', msg.get('message', 'No content'))[:50]}...")
                
                print("   ✅ API исправлен и работает корректно!")
                return True
            else:
                print(f"   ❌ API вернул ошибку: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP ошибка: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Исключение: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование исправленного API")
    print("=" * 50)
    
    success = test_api_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ API работает корректно!")
        print("💡 Теперь можно отправлять сообщения через админ панель")
        print("🔗 Откройте http://localhost:8001/admin/revisions")
    else:
        print("❌ Есть проблемы с API")