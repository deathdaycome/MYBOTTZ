#!/usr/bin/env python3
"""
Скрипт для пересчета всех балансов клиентов
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.models import ClientBalance, HostingServer
from app.services.balance_service import balance_service

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("🔄 Пересчет балансов клиентов...")
print("=" * 70)

try:
    balances = db.query(ClientBalance).all()

    for balance in balances:
        print(f"\n📊 Клиент: {balance.client_name} (ID: {balance.client_id})")
        print(f"   Баланс ДО: {balance.balance}₽")
        print(f"   Стоимость ДО: {balance.total_monthly_cost}₽/мес")
        print(f"   Дней ДО: {balance.days_remaining}")

        # Пересчитываем затраты
        balance_service.update_client_costs(db, balance.client_id, balance.client_name)

        # Обновляем объект
        db.refresh(balance)

        print(f"   Баланс ПОСЛЕ: {balance.balance}₽")
        print(f"   Стоимость ПОСЛЕ: {balance.total_monthly_cost}₽/мес")
        print(f"   Дней ПОСЛЕ: {balance.days_remaining}")

        # Проверяем серверы
        servers = db.query(HostingServer).filter(
            HostingServer.client_id == balance.client_id
        ).all()

        print(f"   Серверов: {len(servers)}")
        for server in servers:
            print(f"     • {server.server_name}: {server.client_price}₽/мес (статус: {server.status})")

    print("\n" + "=" * 70)
    print("✅ Пересчет завершен успешно!")

except Exception as e:
    print(f"\n❌ Ошибка: {str(e)}")
    raise
finally:
    db.close()
