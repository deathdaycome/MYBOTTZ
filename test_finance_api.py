#!/usr/bin/env python3
"""
Скрипт для тестирования API финансов - удаление транзакций
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8001/admin/api"
AUTH = ("admin", "qwerty123")

def test_finance_api():
    print("🧪 Тестирование API финансов")
    print("=" * 50)
    
    # 1. Получаем список транзакций
    print("\n1. Получение списка транзакций...")
    response = requests.get(f"{API_BASE}/finance/transactions", auth=AUTH)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("data"):
            transactions = data["data"]
            print(f"✅ Загружено {len(transactions)} транзакций")
            
            # Показываем первые 3 транзакции
            for i, t in enumerate(transactions[:3]):
                print(f"   {i+1}. ID {t['id']}: {t['description']} - {t['amount']}₽ ({t['type']})")
        else:
            print("❌ Нет данных о транзакциях")
            return
    else:
        print(f"❌ Ошибка получения транзакций: {response.status_code}")
        return
    
    # 2. Создаём тестовую транзакцию
    print("\n2. Создание тестовой транзакции...")
    test_transaction = {
        "amount": 999,
        "type": "expense", 
        "description": "Тестовая транзакция для удаления",
        "date": datetime.now().isoformat(),
        "category_id": 11,  # Офисные расходы
        "notes": "Создано автоматически для тестирования удаления"
    }
    
    response = requests.post(
        f"{API_BASE}/finance/transactions",
        json=test_transaction,
        auth=AUTH
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            created_transaction = data["data"]
            transaction_id = created_transaction["id"]
            print(f"✅ Создана транзакция ID {transaction_id}: {created_transaction['description']}")
        else:
            print(f"❌ Ошибка создания: {data}")
            return
    else:
        print(f"❌ Ошибка создания транзакции: {response.status_code}")
        return
    
    # 3. Удаляем созданную транзакцию
    print(f"\n3. Удаление транзакции ID {transaction_id}...")
    response = requests.delete(
        f"{API_BASE}/finance/transactions/{transaction_id}",
        auth=AUTH
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"✅ Транзакция успешно удалена: {data.get('message')}")
        else:
            print(f"❌ Ошибка удаления: {data}")
    else:
        print(f"❌ Ошибка удаления транзакции: {response.status_code}")
        if response.text:
            print(f"   Ответ: {response.text}")
    
    # 4. Проверяем, что транзакция действительно удалена
    print(f"\n4. Проверка удаления транзакции ID {transaction_id}...")
    response = requests.get(f"{API_BASE}/finance/transactions", auth=AUTH)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("data"):
            remaining_transactions = data["data"]
            deleted_found = any(t["id"] == transaction_id for t in remaining_transactions)
            
            if not deleted_found:
                print("✅ Транзакция успешно удалена из базы данных")
            else:
                print("❌ Транзакция всё ещё присутствует в базе данных")
            
            print(f"📊 Текущее количество транзакций: {len(remaining_transactions)}")
        else:
            print("❌ Ошибка проверки списка транзакций")
    else:
        print(f"❌ Ошибка проверки: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено")

if __name__ == "__main__":
    test_finance_api()