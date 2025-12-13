#!/usr/bin/env python3
"""
Миграция: Добавление полей balance и balance_last_updated в таблицу hosting_servers
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
    """Добавить поля balance и balance_last_updated"""
    print("🔧 Добавление полей balance и balance_last_updated в hosting_servers...")

    try:
        async with engine.begin() as conn:
            # Проверяем существует ли уже колонка balance
            check_query = text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('hosting_servers')
                WHERE name='balance'
            """)
            result = await conn.execute(check_query)
            row = result.fetchone()

            if row and row[0] > 0:
                print("   ⚠️  Поле balance уже существует, пропускаем...")
            else:
                # Добавляем колонку balance
                await conn.execute(text("""
                    ALTER TABLE hosting_servers
                    ADD COLUMN balance REAL DEFAULT 0.0
                """))
                print("   ✓ Поле balance добавлено")

            # Проверяем существует ли уже колонка balance_last_updated
            check_query2 = text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('hosting_servers')
                WHERE name='balance_last_updated'
            """)
            result2 = await conn.execute(check_query2)
            row2 = result2.fetchone()

            if row2 and row2[0] > 0:
                print("   ⚠️  Поле balance_last_updated уже существует, пропускаем...")
            else:
                # Добавляем колонку balance_last_updated
                await conn.execute(text("""
                    ALTER TABLE hosting_servers
                    ADD COLUMN balance_last_updated DATETIME
                """))
                print("   ✓ Поле balance_last_updated добавлено")

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
