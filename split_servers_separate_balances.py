#!/usr/bin/env python3
"""
Скрипт для разделения серверов на отдельные балансы
Каждый сервер = отдельный клиент = отдельный баланс
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.models import HostingServer, ClientBalance, BalanceTransaction

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("🔄 Разделение серверов на отдельные балансы...")
print("=" * 70)

try:
    # Находим всех клиентов с общим балансом
    balances_to_split = db.query(ClientBalance).all()

    total_split = 0

    for balance in balances_to_split:
        # Находим все серверы этого клиента
        servers = db.query(HostingServer).filter(
            HostingServer.client_id == balance.client_id
        ).all()

        if len(servers) <= 1:
            print(f"\n✓ {balance.client_name} (ID: {balance.client_id}) - только 1 сервер, пропускаем")
            continue

        print(f"\n📦 {balance.client_name} (ID: {balance.client_id})")
        print(f"   Серверов: {len(servers)}")
        print(f"   Текущий баланс: {balance.balance}₽")

        # Сохраняем старый баланс для первого сервера
        old_balance = balance.balance
        old_client_id = balance.client_id

        # Оставляем первый сервер с текущим client_id
        first_server = servers[0]
        print(f"\n   Сервер 1: {first_server.server_name}")
        print(f"     → Остается с client_id: {old_client_id}")
        print(f"     → Баланс: {old_balance}₽")

        # Обновляем баланс первого сервера
        balance.total_monthly_cost = first_server.client_price
        balance.days_remaining = balance.calculate_days_remaining()
        db.commit()

        # Остальные серверы получают новые уникальные client_id
        for idx, server in enumerate(servers[1:], start=2):
            # Генерируем уникальный client_id
            new_client_id = int(time.time() * 1000) + random.randint(1000, 9999)

            # Проверяем уникальность
            while db.query(HostingServer).filter(
                HostingServer.client_id == new_client_id
            ).first() is not None:
                new_client_id += 1

            print(f"\n   Сервер {idx}: {server.server_name}")
            print(f"     → Новый client_id: {new_client_id}")

            # Обновляем сервер
            old_server_client_id = server.client_id
            server.client_id = new_client_id
            db.commit()

            # Создаем новый баланс для этого сервера
            new_balance = ClientBalance(
                client_id=new_client_id,
                client_name=server.client_name,
                client_telegram_id=server.client_telegram_id,
                balance=0.0,  # Начинаем с нуля
                total_monthly_cost=server.client_price,
                days_remaining=0
            )
            db.add(new_balance)
            db.commit()
            db.refresh(new_balance)

            print(f"     → Создан баланс: 0₽")
            print(f"     → Стоимость: {server.client_price}₽/мес")

            total_split += 1

    print("\n" + "=" * 70)
    print(f"✅ Разделение завершено!")
    print(f"   Серверов разделено: {total_split}")
    print("\n💡 Теперь каждый сервер имеет свой отдельный баланс")
    print("   Вы можете пополнять баланс для каждого сервера отдельно")

except Exception as e:
    db.rollback()
    print(f"\n❌ Ошибка: {str(e)}")
    import traceback
    traceback.print_exc()
    raise
finally:
    db.close()
