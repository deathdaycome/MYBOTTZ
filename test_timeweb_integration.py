#!/usr/bin/env python3
"""
Тестирование интеграции с Timeweb Cloud API
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.timeweb_service import timeweb_service


async def test_timeweb_integration():
    """Тестирование всех методов Timeweb API"""

    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С TIMEWEB CLOUD API")
    print("=" * 60)
    print()

    # 1. Проверка конфигурации
    print("1️⃣ Проверка конфигурации...")
    is_configured = timeweb_service.is_configured()
    print(f"   {'✅' if is_configured else '❌'} API токен {'настроен' if is_configured else 'не настроен'}")

    if not is_configured:
        print("\n❌ ОШИБКА: TIMEWEB_API_TOKEN не настроен в .env")
        return

    print()

    # 2. Получение списка серверов
    print("2️⃣ Получение списка серверов из Timeweb Cloud...")
    try:
        servers = await timeweb_service.get_servers()
        print(f"   ✅ Получено серверов: {len(servers)}")

        if servers:
            print("\n   📋 Список серверов:")
            for i, server in enumerate(servers, 1):
                name = server.get('name', 'Без названия')
                server_id = server.get('id')
                status = server.get('status', 'unknown')
                config = timeweb_service.parse_server_configuration(server)
                ip = timeweb_service.get_primary_ip(server)

                print(f"\n   {i}. {name} (ID: {server_id})")
                print(f"      • Статус: {status}")
                print(f"      • Конфигурация: {config}")
                print(f"      • IP: {ip or 'не назначен'}")

                # Получаем цену сервера
                price = await timeweb_service.get_server_price(server)
                if price:
                    print(f"      • Стоимость: {price} ₽/мес")
        else:
            print("   ℹ️ Серверы не найдены (аккаунт пустой)")
    except Exception as e:
        print(f"   ❌ Ошибка получения серверов: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # 3. Получение финансов аккаунта
    print("3️⃣ Получение информации о балансе...")
    try:
        finances = await timeweb_service.get_account_finances()
        if finances:
            balance = finances.get('balance', 0)
            print(f"   ✅ Баланс аккаунта: {balance} ₽")
        else:
            print("   ⚠️ Информация о финансах недоступна")
    except Exception as e:
        print(f"   ❌ Ошибка получения финансов: {e}")

    print()

    # 4. Получение доступных конфигураций
    print("4️⃣ Получение доступных конфигураций серверов...")
    try:
        presets = await timeweb_service.get_presets()
        print(f"   ✅ Доступно конфигураций: {len(presets)}")

        if presets:
            print("\n   📋 Популярные конфигурации:")
            for i, preset in enumerate(presets[:5], 1):  # Показываем первые 5
                location = preset.get('location', 'unknown')
                price = preset.get('price', 0)
                cpu = preset.get('cpu', 0)
                ram = preset.get('ram', 0) / 1024  # MB -> GB
                disk = preset.get('disk', 0) / 1024  # MB -> GB

                print(f"   {i}. {cpu} CPU / {ram:.0f}GB RAM / {disk:.0f}GB SSD")
                print(f"      • Локация: {location}")
                print(f"      • Цена: {price} ₽/мес")
    except Exception as e:
        print(f"   ❌ Ошибка получения конфигураций: {e}")

    print()
    print("=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_timeweb_integration())
