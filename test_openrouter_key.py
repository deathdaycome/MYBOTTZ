#!/usr/bin/env python3
"""
Тест нового OpenRouter API ключа
"""

import requests
import json

# Новый ключ
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"

def test_openrouter_key():
    """Тестируем ключ OpenRouter"""
    print("="*60)
    print("ТЕСТ OPENROUTER API КЛЮЧА")
    print("="*60)
    print(f"Ключ: {API_KEY[:20]}...")
    print(f"URL: {BASE_URL}")
    print()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://github.com/your-repo",  # Опционально
        "X-Title": "Avito AI Assistant"  # Опционально
    }
    
    # Тест с бесплатной моделью
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",  # Бесплатная модель
        "messages": [
            {
                "role": "system", 
                "content": "Ты - профессиональный IT-менеджер."
            },
            {
                "role": "user", 
                "content": "Клиент спрашивает: 'Сколько стоит разработка мобильного приложения?' Ответь кратко и профессионально."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    print("🚀 Тестируем БЕСПЛАТНУЮ модель: meta-llama/llama-3.1-8b-instruct:free")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ УСПЕХ!")
            print(f"Модель: {data.get('model', 'не указана')}")
            
            if 'choices' in data and data['choices']:
                ai_response = data['choices'][0]['message']['content']
                print(f"Ответ AI: {ai_response}")
                
                if 'usage' in data:
                    usage = data['usage']
                    print(f"Токены: {usage.get('total_tokens', 'не указано')}")
                    
            print("\n" + "="*60)
            print("🎉 API КЛЮЧ РАБОТАЕТ!")
            print("="*60)
            return True
            
        else:
            print(f"❌ Ошибка {response.status_code}")
            print(f"Ответ: {response.text}")
            
            try:
                error_data = response.json()
                print(f"Детали ошибки: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
    except Exception as e:
        print(f"💥 Исключение: {e}")
        import traceback
        traceback.print_exc()
        
    return False

def test_paid_model():
    """Тестируем платную модель"""
    print("\n💰 Тестируем ПЛАТНУЮ модель: openai/gpt-4o-mini")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Привет! Это тест."}
        ],
        "max_tokens": 20
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            print(f"✅ GPT-4o-mini работает: {ai_response}")
            return True
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        
    return False

if __name__ == "__main__":
    # Тестируем бесплатную модель
    free_works = test_openrouter_key()
    
    # Если бесплатная работает, тестируем платную
    if free_works:
        paid_works = test_paid_model()
        
        if paid_works:
            print("\n🎯 РЕКОМЕНДАЦИЯ: Используйте openai/gpt-4o-mini")
        else:
            print("\n🆓 РЕКОМЕНДАЦИЯ: Используйте meta-llama/llama-3.1-8b-instruct:free")
    else:
        print("\n❌ API ключ не работает!")
        print("Проверьте:")
        print("1. Правильность ключа")
        print("2. Баланс на аккаунте OpenRouter")
        print("3. Активность ключа на https://openrouter.ai/keys")