#!/usr/bin/env python3
"""
Миграция: Создание таблицы balance_transactions
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.core.database import engine


async def migrate():
    """Создать таблицу balance_transactions"""
    print("🔧 Создание таблицы balance_transactions...")

    try:
        async with engine.begin() as conn:
            # Проверяем существует ли таблица
            check_query = text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='balance_transactions'
            """)
            result = await conn.execute(check_query)
            row = result.fetchone()

            if row:
                print("   ⚠️  Таблица balance_transactions уже существует, пропускаем...")
            else:
                # Создаем таблицу
                await conn.execute(text("""
                    CREATE TABLE balance_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        server_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        transaction_type VARCHAR(50) NOT NULL,
                        balance_before REAL NOT NULL,
                        balance_after REAL NOT NULL,
                        description TEXT,
                        payment_method VARCHAR(50),
                        receipt_url VARCHAR(500),
                        admin_user_id INTEGER,
                        admin_user_name VARCHAR(255),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (server_id) REFERENCES hosting_servers(id) ON DELETE CASCADE
                    )
                """))

                # Создаем индексы
                await conn.execute(text("""
                    CREATE INDEX ix_balance_transactions_server_id
                    ON balance_transactions(server_id)
                """))

                await conn.execute(text("""
                    CREATE INDEX ix_balance_transactions_created_at
                    ON balance_transactions(created_at)
                """))

                print("   ✓ Таблица balance_transactions создана")
                print("   ✓ Индексы созданы")

        print("\n✅ Миграция успешно выполнена!")
        return True

    except Exception as e:
        print(f"\n❌ Ошибка при выполнении миграции: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(migrate())
    sys.exit(0 if success else 1)
