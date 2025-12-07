#!/usr/bin/env python3
"""
Скрипт для объединения клиентов и переноса баланса
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.models import ClientBalance, HostingServer, BalanceTransaction

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("🔄 Объединение клиентов и перенос баланса...")
print("=" * 70)

try:
    # Находим оба клиента "Не указан"
    old_client_id = 1826307831  # Старый клиент с балансом 4500₽
    new_client_id = 1826307832  # Новый клиент с сервером "5 ботов"

    old_balance = db.query(ClientBalance).filter(ClientBalance.client_id == old_client_id).first()
    new_balance = db.query(ClientBalance).filter(ClientBalance.client_id == new_client_id).first()

    print(f"\n📊 Старый клиент (ID: {old_client_id}):")
    print(f"   Баланс: {old_balance.balance}₽")
    print(f"   Стоимость: {old_balance.total_monthly_cost}₽/мес")

    print(f"\n📊 Новый клиент (ID: {new_client_id}):")
    print(f"   Баланс: {new_balance.balance}₽")
    print(f"   Стоимость: {new_balance.total_monthly_cost}₽/мес")

    # 1. Переносим сервер с нового клиента на старого
    server = db.query(HostingServer).filter(HostingServer.client_id == new_client_id).first()
    print(f"\n🔧 Переносим сервер '{server.server_name}' на старого клиента...")
    server.client_id = old_client_id
    db.commit()

    # 2. Удаляем нового клиента (он теперь пустой)
    print(f"🗑️  Удаляем пустого нового клиента...")
    db.delete(new_balance)
    db.commit()

    # 3. Пересчитываем затраты старого клиента
    print(f"📊 Пересчитываем затраты старого клиента...")
    from app.services.balance_service import balance_service
    balance_service.update_client_costs(db, old_client_id, "Не указан")

    # 4. Обновляем и показываем результат
    db.refresh(old_balance)

    print(f"\n✅ Результат:")
    print(f"   Клиент ID: {old_balance.client_id}")
    print(f"   Баланс: {old_balance.balance}₽")
    print(f"   Месячная стоимость: {old_balance.total_monthly_cost}₽/мес")
    print(f"   Дней осталось: {old_balance.days_remaining}")

    # Показываем все серверы клиента
    servers = db.query(HostingServer).filter(HostingServer.client_id == old_client_id).all()
    print(f"\n📦 Серверов клиента: {len(servers)}")
    for s in servers:
        if s.client_price > 0:
            print(f"     • {s.server_name}: {s.client_price}₽/мес")

    print("\n" + "=" * 70)
    print("✅ Объединение завершено успешно!")
    print("\n💡 Теперь все серверы 'Не указан' под одним клиентом с общим балансом")

except Exception as e:
    db.rollback()
    print(f"\n❌ Ошибка: {str(e)}")
    raise
finally:
    db.close()
