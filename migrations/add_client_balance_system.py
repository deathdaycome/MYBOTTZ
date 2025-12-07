#!/usr/bin/env python3
"""
Миграция: Добавление системы балансов клиентов для хостинга
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config.settings import get_settings

settings = get_settings()


def run_migration():
    """Добавить систему балансов клиентов"""

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("🔄 Создание таблиц для системы балансов клиентов...")

        try:
            # 1. Создаем таблицу балансов клиентов
            print("\n1. Создание таблицы client_balances...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS client_balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    client_name TEXT NOT NULL,
                    client_telegram_id BIGINT,
                    balance REAL NOT NULL DEFAULT 0,
                    total_monthly_cost REAL NOT NULL DEFAULT 0,
                    days_remaining INTEGER DEFAULT 0,
                    last_charge_date TIMESTAMP,
                    next_charge_date TIMESTAMP,
                    low_balance_notified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(client_id)
                )
            """))
            conn.commit()
            print("   ✅ Таблица client_balances создана")

            # 2. Создаем таблицу транзакций баланса
            print("\n2. Создание таблицы balance_transactions...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS balance_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    client_name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    balance_before REAL NOT NULL,
                    balance_after REAL NOT NULL,
                    description TEXT,
                    server_id INTEGER,
                    server_name TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("   ✅ Таблица balance_transactions создана")

            # 3. Создаем индексы
            print("\n3. Создание индексов...")

            # Индексы для client_balances
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_client_balances_client_id
                ON client_balances(client_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_client_balances_days_remaining
                ON client_balances(days_remaining)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_client_balances_next_charge
                ON client_balances(next_charge_date)
            """))

            # Индексы для balance_transactions
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_balance_transactions_client_id
                ON balance_transactions(client_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_balance_transactions_type
                ON balance_transactions(type)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_balance_transactions_created_at
                ON balance_transactions(created_at)
            """))

            conn.commit()
            print("   ✅ Индексы созданы")

            # 4. Добавляем поле client_id в hosting_servers если его нет
            print("\n4. Проверка поля client_id в hosting_servers...")

            result = conn.execute(text("""
                PRAGMA table_info(hosting_servers)
            """))

            columns = [row[1] for row in result]

            if 'client_id' not in columns:
                print("   ⚠️  Поле client_id не найдено, добавляем...")
                conn.execute(text("""
                    ALTER TABLE hosting_servers
                    ADD COLUMN client_id INTEGER
                """))
                conn.commit()
                print("   ✅ Поле client_id добавлено")
            else:
                print("   ✅ Поле client_id уже существует")

            print("\n✅ Миграция успешно завершена!")
            print("\n📊 Созданные таблицы:")
            print("   • client_balances - балансы клиентов")
            print("   • balance_transactions - история транзакций")
            print("\n💡 Теперь можно:")
            print("   1. Пополнять баланс клиентов")
            print("   2. Автоматически списывать плату за серверы")
            print("   3. Получать уведомления о низком балансе")

        except Exception as e:
            conn.rollback()
            print(f"\n❌ Ошибка миграции: {str(e)}")
            raise


if __name__ == "__main__":
    run_migration()
