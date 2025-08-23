#!/usr/bin/env python3
"""
Скрипт автоматического развертывания Avito webhooks
Настраивает webhook для получения уведомлений о новых сообщениях в реальном времени
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.avito_service import get_avito_service, init_avito_service
from app.config.settings import settings
from app.config.logging import get_logger

logger = get_logger(__name__)

async def setup_webhook():
    """Настройка webhook для Avito"""
    
    print("🔧 Настройка Avito Webhook...")
    print("=" * 50)
    
    try:
        # Инициализируем Avito сервис
        if not settings.AVITO_CLIENT_ID or not settings.AVITO_CLIENT_SECRET or not settings.AVITO_USER_ID:
            print("❌ Отсутствуют необходимые переменные окружения для Avito:")
            print(f"   AVITO_CLIENT_ID: {'✅' if settings.AVITO_CLIENT_ID else '❌'}")
            print(f"   AVITO_CLIENT_SECRET: {'✅' if settings.AVITO_CLIENT_SECRET else '❌'}")
            print(f"   AVITO_USER_ID: {'✅' if settings.AVITO_USER_ID else '❌'}")
            return False
        
        print(f"✅ AVITO_CLIENT_ID: {settings.AVITO_CLIENT_ID[:10]}...")
        print(f"✅ AVITO_USER_ID: {settings.AVITO_USER_ID}")
        
        # Инициализируем сервис
        avito_service = init_avito_service(
            settings.AVITO_CLIENT_ID,
            settings.AVITO_CLIENT_SECRET,
            int(settings.AVITO_USER_ID)
        )
        
        # Определяем URL webhook
        webhook_url = f"https://{settings.DOMAIN}/admin/avito/webhook"
        print(f"🔗 Webhook URL: {webhook_url}")
        
        # Проверяем доступность webhook endpoint
        print("🔍 Проверяем доступность webhook endpoint...")
        
        # Регистрируем webhook
        print("📡 Регистрируем webhook в Avito API...")
        
        try:
            success = await avito_service.subscribe_webhook(webhook_url)
            if success:
                print("✅ Webhook успешно зарегистрирован!")
                print("🎉 Теперь сообщения будут обновляться в реальном времени!")
                
                # Сохраняем URL webhook в настройки
                webhook_file = project_root / "WEBHOOK_URL.txt"
                with open(webhook_file, "w") as f:
                    f.write(webhook_url)
                print(f"💾 Webhook URL сохранен в {webhook_file}")
                
                return True
            else:
                print("❌ Не удалось зарегистрировать webhook")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка регистрации webhook: {e}")
            logger.error(f"Webhook registration error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка настройки webhook: {e}")
        logger.error(f"Webhook setup error: {e}")
        return False

async def unsubscribe_webhook():
    """Отписка от webhook (для отладки)"""
    
    print("🔧 Отписка от Avito Webhook...")
    print("=" * 50)
    
    try:
        # Читаем сохраненный URL
        webhook_file = project_root / "WEBHOOK_URL.txt"
        if not webhook_file.exists():
            print("❌ Файл с URL webhook не найден")
            return False
            
        with open(webhook_file, "r") as f:
            webhook_url = f.read().strip()
        
        print(f"🔗 Webhook URL: {webhook_url}")
        
        # Инициализируем сервис
        avito_service = init_avito_service(
            settings.AVITO_CLIENT_ID,
            settings.AVITO_CLIENT_SECRET,
            int(settings.AVITO_USER_ID)
        )
        
        # Отписываемся от webhook
        success = await avito_service.unsubscribe_webhook(webhook_url)
        if success:
            print("✅ Webhook успешно отключен!")
            return True
        else:
            print("❌ Не удалось отключить webhook")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка отписки от webhook: {e}")
        return False

async def test_webhook_connectivity():
    """Тестирование доступности webhook endpoint"""
    
    print("🧪 Тестирование доступности webhook endpoint...")
    
    import aiohttp
    
    webhook_url = f"https://{settings.DOMAIN}/admin/avito/webhook"
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(webhook_url, json={}) as response:
                if response.status == 200:
                    print("✅ Webhook endpoint доступен и отвечает!")
                    return True
                else:
                    print(f"⚠️ Webhook endpoint отвечает с кодом {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Webhook endpoint недоступен: {e}")
        return False

def main():
    """Главная функция"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Управление Avito Webhooks')
    parser.add_argument('action', choices=['setup', 'unsubscribe', 'test'], 
                       help='Действие: setup - настроить, unsubscribe - отключить, test - тестировать')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        success = asyncio.run(setup_webhook())
    elif args.action == 'unsubscribe':
        success = asyncio.run(unsubscribe_webhook())
    elif args.action == 'test':
        success = asyncio.run(test_webhook_connectivity())
    
    if success:
        print("🎉 Операция выполнена успешно!")
        sys.exit(0)
    else:
        print("💥 Операция завершилась с ошибкой!")
        sys.exit(1)

if __name__ == "__main__":
    main()