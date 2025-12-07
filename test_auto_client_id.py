#!/usr/bin/env python3
"""
Тест автоматического присвоения client_id
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.models import HostingServer, ClientBalance
from app.services.client_id_service import client_id_service

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 70)
print("🧪 ТЕСТ АВТОМАТИЧЕСКОГО ПРИСВОЕНИЯ CLIENT_ID")
print("=" * 70)

# Тест 1: Группировка серверов по имени клиента
print("\n📊 Тест 1: Группировка серверов по имени клиента")
print("-" * 70)

clients = {}
servers = db.query(HostingServer).all()

for server in servers:
    if server.client_name not in clients:
        clients[server.client_name] = {
            'client_id': server.client_id,
            'servers': [],
            'total_price': 0
        }

    clients[server.client_name]['servers'].append(server.server_name)
    clients[server.client_name]['total_price'] += server.client_price

print(f"\nНайдено уникальных клиентов: {len(clients)}")

for client_name, data in clients.items():
    print(f"\n👤 Клиент: {client_name}")
    print(f"   client_id: {data['client_id']}")
    print(f"   Количество серверов: {len(data['servers'])}")
    print(f"   Общая стоимость: {data['total_price']}₽/мес")
    if len(data['servers']) <= 3:
        for server_name in data['servers']:
            print(f"     • {server_name}")
    else:
        for server_name in data['servers'][:3]:
            print(f"     • {server_name}")
        print(f"     ... и еще {len(data['servers']) - 3}")

# Тест 2: Проверка балансов
print("\n" + "=" * 70)
print("💰 Тест 2: Проверка балансов клиентов")
print("-" * 70)

balances = db.query(ClientBalance).all()
print(f"\nНайдено балансов: {len(balances)}")

for balance in balances:
    print(f"\n💳 {balance.client_name} (ID: {balance.client_id})")
    print(f"   Баланс: {balance.balance}₽")
    print(f"   Месячная стоимость: {balance.total_monthly_cost}₽")
    print(f"   Дней осталось: {balance.days_remaining}")

    # Проверяем, что стоимость правильно рассчитана
    servers_count = db.query(HostingServer).filter(
        HostingServer.client_id == balance.client_id
    ).count()
    print(f"   Количество серверов: {servers_count}")

    # Цветовая индикация дней
    if balance.days_remaining == 0:
        status = "🔴 КРИТИЧНО"
    elif balance.days_remaining <= 3:
        status = "🟠 ТРЕБУЕТСЯ ПОПОЛНЕНИЕ"
    elif balance.days_remaining <= 7:
        status = "🟡 НИЗКИЙ БАЛАНС"
    elif balance.days_remaining < 999:
        status = "🟢 В ПОРЯДКЕ"
    else:
        status = "⚪ НЕТ ЗАТРАТ"

    print(f"   Статус: {status}")

# Тест 3: Проверка автоматической генерации client_id
print("\n" + "=" * 70)
print("🔧 Тест 3: Проверка генерации client_id")
print("-" * 70)

test_names = [
    "Тестовый Клиент",
    "тестовый клиент",  # Должен получить тот же ID
    "  Тестовый Клиент  ",  # Должен получить тот же ID
    "Другой Клиент"  # Должен получить другой ID
]

print("\nТестирование нормализации имен:")
generated_ids = {}

for name in test_names:
    client_id = client_id_service.get_or_create_client_id(db, name)
    generated_ids[name] = client_id
    print(f"   '{name}' → client_id: {client_id}")

# Проверка что нормализация работает
ids_set = set([
    generated_ids["Тестовый Клиент"],
    generated_ids["тестовый клиент"],
    generated_ids["  Тестовый Клиент  "]
])

if len(ids_set) == 1:
    print("\n✅ Нормализация работает правильно - одинаковые имена получают одинаковый ID")
else:
    print("\n❌ ОШИБКА: Нормализация не работает!")

if generated_ids["Другой Клиент"] != generated_ids["Тестовый Клиент"]:
    print("✅ Разные имена получают разные ID")
else:
    print("❌ ОШИБКА: Разные имена получили одинаковый ID!")

# Итоговая статистика
print("\n" + "=" * 70)
print("📈 ИТОГОВАЯ СТАТИСТИКА")
print("=" * 70)

total_servers = db.query(HostingServer).count()
total_with_id = db.query(HostingServer).filter(
    HostingServer.client_id.isnot(None)
).count()
total_balances = db.query(ClientBalance).count()

total_balance_amount = sum(b.balance for b in balances)
total_monthly_revenue = sum(b.total_monthly_cost for b in balances)

print(f"""
Серверов всего:               {total_servers}
Серверов с client_id:         {total_with_id}
Уникальных клиентов:          {len(clients)}
Балансов в системе:           {total_balances}

Общий баланс всех клиентов:   {total_balance_amount:.0f}₽
Общий месячный доход:         {total_monthly_revenue:.0f}₽/мес
""")

# Проверка консистентности
print("🔍 Проверка консистентности:")

if total_servers == total_with_id:
    print("✅ Все серверы имеют client_id")
else:
    print(f"⚠️  {total_servers - total_with_id} серверов без client_id")

if len(clients) == total_balances:
    print("✅ Количество балансов соответствует количеству клиентов")
else:
    print(f"⚠️  Расхождение: {len(clients)} клиентов, {total_balances} балансов")

# Проверяем что стоимости в балансах правильные
print("\n🧮 Проверка расчета стоимостей:")
errors = 0

for balance in balances:
    # Считаем стоимость серверов
    servers = db.query(HostingServer).filter(
        HostingServer.client_id == balance.client_id
    ).all()

    actual_cost = sum(s.client_price for s in servers if s.status in ['active', 'overdue'])

    if abs(balance.total_monthly_cost - actual_cost) > 0.01:
        print(f"❌ Ошибка для {balance.client_name}:")
        print(f"   В балансе: {balance.total_monthly_cost}₽")
        print(f"   Фактически: {actual_cost}₽")
        errors += 1

if errors == 0:
    print("✅ Все стоимости рассчитаны правильно")
else:
    print(f"❌ Найдено ошибок: {errors}")

print("\n" + "=" * 70)
print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 70)

db.close()
