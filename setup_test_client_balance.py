#!/usr/bin/env python3
"""
Скрипт для настройки тестового клиента с балансом
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.models import HostingServer
from app.services.balance_service import balance_service

settings = get_settings()


def setup_test_client():
    """Настройка тестового клиента с балансом"""

    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        print("🔄 Настройка тестового клиента...")

        # 1. Находим сервер CRM (ID 2)
        server = db.query(HostingServer).filter(HostingServer.id == 2).first()

        if not server:
            print("❌ Сервер с ID 2 не найден")
            return

        print(f"\n📦 Найден сервер: {server.server_name}")
        print(f"   Текущий client_id: {server.client_id}")
        print(f"   Текущий client_name: {server.client_name}")
        print(f"   Текущий client_price: {server.client_price}₽/мес")

        # 2. Обновляем информацию о клиенте
        print("\n✏️  Обновляем информацию о клиенте...")
        server.client_id = 1001  # Уникальный ID клиента
        server.client_name = "Иван Тестовый"
        server.client_price = 1500.0  # 1500₽/мес как в примере

        db.commit()
        db.refresh(server)

        print("✅ Сервер обновлен:")
        print(f"   client_id: {server.client_id}")
        print(f"   client_name: {server.client_name}")
        print(f"   client_price: {server.client_price}₽/мес")

        # 3. Создаем/обновляем баланс клиента
        print("\n💰 Создаем баланс клиента...")
        balance_service.update_client_costs(db, server.client_id, server.client_name)

        balance = balance_service.get_or_create_balance(
            db,
            server.client_id,
            server.client_name
        )

        print(f"✅ Баланс создан:")
        print(f"   Текущий баланс: {balance.balance}₽")
        print(f"   Месячная стоимость: {balance.total_monthly_cost}₽")
        print(f"   Осталось дней: {balance.days_remaining}")

        # 4. Пополняем баланс на 4000₽ как в примере
        print("\n💳 Пополняем баланс на 4000₽...")
        balance, transaction = balance_service.add_balance(
            db,
            server.client_id,
            server.client_name,
            4000.0,
            "Начальное пополнение баланса",
            "admin"
        )

        print(f"✅ Баланс пополнен:")
        print(f"   Новый баланс: {balance.balance}₽")
        print(f"   Месячная стоимость: {balance.total_monthly_cost}₽/мес")
        print(f"   Осталось дней: {balance.days_remaining}")
        print(f"   Расчет: {balance.balance}₽ / ({balance.total_monthly_cost}₽/30) = {balance.days_remaining} дней")

        # 5. Проверяем транзакцию
        print(f"\n📝 Создана транзакция:")
        print(f"   ID: {transaction.id}")
        print(f"   Тип: {transaction.type}")
        print(f"   Сумма: {transaction.amount}₽")
        print(f"   Баланс до: {transaction.balance_before}₽")
        print(f"   Баланс после: {transaction.balance_after}₽")
        print(f"   Описание: {transaction.description}")

        print("\n✅ Тестовый клиент настроен!")
        print("\n💡 Теперь:")
        print("   1. Обновите страницу Хостинга в админ-панели")
        print("   2. В строке 'CRM' увидите баланс: 4000₽ и дни: ~80 дн")
        print("   3. Кликните на '+' чтобы пополнить баланс")
        print("   4. Виджет покажет прогноз нового баланса и дней")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_test_client()
