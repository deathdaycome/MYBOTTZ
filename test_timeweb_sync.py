#!/usr/bin/env python3
"""
Тестирование автоматической синхронизации серверов с Timeweb Cloud
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# URL сервера
BASE_URL = "http://147.45.215.199:8001"
USERNAME = "admin"
PASSWORD = "qwerty123"

# Создаем объект аутентификации
auth = HTTPBasicAuth(USERNAME, PASSWORD)


def test_sync_all():
    """Тестировать автоматическую синхронизацию всех серверов"""
    print("\n" + "="*60)
    print("🔄 Запуск автоматической синхронизации серверов из Timeweb")
    print("="*60)

    sync_url = f"{BASE_URL}/admin/hosting/api/timeweb/sync-all"

    response = requests.post(
        sync_url,
        auth=auth
    )

    if response.status_code == 200:
        data = response.json()

        print("\n✅ Синхронизация успешно завершена!")
        print(f"\nСообщение: {data.get('message')}")
        print(f"\n📊 Статистика:")
        print(f"  • Создано новых серверов: {data.get('created_count', 0)}")
        print(f"  • Обновлено серверов: {data.get('updated_count', 0)}")
        print(f"  • Ошибок: {data.get('error_count', 0)}")
        print(f"  • Всего обработано: {data.get('total_processed', 0)}")

        if data.get('created'):
            print("\n✨ Созданные серверы:")
            for server in data.get('created', [])[:5]:  # Первые 5
                print(f"  {server.get('name')} (ID: {server.get('crm_id')}, Timeweb ID: {server.get('timeweb_id')})")
            if len(data.get('created', [])) > 5:
                print(f"  ... и ещё {len(data.get('created', [])) - 5} серверов")

        if data.get('updated'):
            print("\n🔄 Обновленные серверы:")
            for server in data.get('updated', [])[:5]:  # Первые 5
                print(f"  {server.get('name')} (ID: {server.get('crm_id')})")
            if len(data.get('updated', [])) > 5:
                print(f"  ... и ещё {len(data.get('updated', [])) - 5} серверов")

        if data.get('errors'):
            print("\n⚠️ Ошибки:")
            for error in data.get('errors', []):
                print(f"  • Сервер {error.get('server_name', 'N/A')} (ID: {error.get('server_id')}): {error.get('error')}")

        return True
    else:
        print(f"\n❌ Ошибка синхронизации: {response.status_code}")
        print(response.text)
        return False


def get_servers_list():
    """Получить список серверов из CRM"""
    print("\n" + "="*60)
    print("📋 Получение списка серверов из CRM")
    print("="*60)

    servers_url = f"{BASE_URL}/admin/hosting/api/servers"

    response = requests.get(
        servers_url,
        auth=auth
    )

    if response.status_code == 200:
        data = response.json()
        servers = data.get('servers', [])

        print(f"\n✅ Найдено серверов в CRM: {len(servers)}")

        if servers:
            print("\n📋 Первые 5 серверов:")
            for server in servers[:5]:
                print(f"\n  {server.get('server_name')}")
                print(f"    • ID: {server.get('id')}")
                print(f"    • Timeweb ID: {server.get('timeweb_id', 'N/A')}")
                print(f"    • Конфигурация: {server.get('configuration', 'N/A')}")
                print(f"    • IP: {server.get('ip_address', 'N/A')}")
                print(f"    • Себестоимость: {server.get('cost_price', 0)} ₽/мес")
                print(f"    • Цена клиента: {server.get('client_price', 0)} ₽/мес")
                print(f"    • Статус: {server.get('status', 'N/A')}")
                print(f"    • Клиент: {server.get('client_name', 'Не указан')}")

        return True
    else:
        print(f"\n❌ Ошибка получения списка: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("✅ Используем Basic Auth аутентификацию")

    # Тестируем синхронизацию
    sync_success = test_sync_all()

    if sync_success:
        # Показываем список серверов
        get_servers_list()

        print("\n" + "="*60)
        print("✅ Тестирование завершено успешно!")
        print("="*60)
        print("\n💡 Что дальше:")
        print("  1. Откройте раздел 'Хостинг' в админ-панели")
        print("  2. Все серверы из Timeweb уже загружены автоматически")
        print("  3. Установите для каждого сервера:")
        print("     • Цену для клиента")
        print("     • Имя клиента")
        print("     • Привязку к проекту")
        print("     • Дату следующего платежа")
        print("\n💰 Ваша наценка рассчитывается автоматически:")
        print("  Маржа = Цена клиента - Себестоимость")
    else:
        print("\n❌ Тестирование завершено с ошибками")
        exit(1)
