#!/usr/bin/env python3
"""
Тест доступных моделей OpenRouter
"""

import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def test_model(model_name, description=""):
    """Тест конкретной модели"""
    print(f"Тестируем: {model_name} {description}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Привет! Скажи 'работаю'"}
        ],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            print(f"✅ РАБОТАЕТ: {ai_response}")
            return True
        else:
            error_data = response.json()
            print(f"❌ {response.status_code}: {error_data.get('error', {}).get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        return False

def main():
    print("="*60)
    print("ТЕСТ ДОСТУПНЫХ МОДЕЛЕЙ")
    print("="*60)
    
    # Модели для тестирования
    models_to_test = [
        ("openai/gpt-4o-mini", "💰 Дешевая и быстрая"),
        ("openai/gpt-3.5-turbo", "💰 Классическая дешевая"),
        ("anthropic/claude-3-haiku", "⚡ Быстрый Claude"),
        ("meta-llama/llama-3.1-8b-instruct", "🦙 Llama без :free"),
        ("microsoft/phi-3-mini-128k-instruct", "🔬 Microsoft Phi"),
        ("google/gemma-2-9b-it", "🔍 Google Gemma"),
        ("mistralai/mistral-7b-instruct", "🌪️ Mistral"),
    ]
    
    working_models = []
    
    for model, description in models_to_test:
        if test_model(model, description):
            working_models.append(model)
        print()
    
    print("="*60)
    print(f"РАБОЧИЕ МОДЕЛИ ({len(working_models)}):")
    for model in working_models:
        print(f"✅ {model}")
    
    if working_models:
        recommended = working_models[0]
        print(f"\n🎯 РЕКОМЕНДУЕМАЯ МОДЕЛЬ: {recommended}")
        
        # Обновим код для использования рабочей модели
        print(f"\n📝 ДОБАВЬТЕ В .env:")
        print(f"DEFAULT_MODEL={recommended}")
    else:
        print("\n❌ НИ ОДНА МОДЕЛЬ НЕ РАБОТАЕТ!")
        print("Проверьте баланс на https://openrouter.ai/")

if __name__ == "__main__":
    main()