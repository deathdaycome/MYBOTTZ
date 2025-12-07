#!/usr/bin/env python3
"""
Быстрая миграция из SQLite в PostgreSQL
Создает схему и переносит данные
"""
import os
import sys

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlite3

# Импортируем Base со всеми моделями
from app.database.models import Base as MainBase
from app.database.notification_models import Base as NotificationBase

print("🚀 Быстрая миграция на PostgreSQL")
print("=" * 60)

# Настройки подключений
SQLITE_PATH = "./business_card_bot.db"
# Экранируем специальные символы в пароле
from urllib.parse import quote_plus
password = quote_plus("CRM_SecureP@ssw0rd_2024!")
POSTGRES_URL = f"postgresql://crm_user:{password}@localhost:5432/crm_db"

print(f"📊 SQLite: {SQLITE_PATH}")
print(f"📊 PostgreSQL: localhost:5432/crm_db")
print()

# 1. Создаем схему в PostgreSQL
print("1️⃣  Создание схемы PostgreSQL...")
try:
    pg_engine = create_engine(POSTGRES_URL)

    # Создаем все таблицы из моделей
    MainBase.metadata.create_all(pg_engine)
    print("✅ Основные таблицы созданы")

    NotificationBase.metadata.create_all(pg_engine)
    print("✅ Таблицы уведомлений созданы")

except Exception as e:
    print(f"❌ Ошибка создания схемы: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Проверяем SQLite
print("\n2️⃣  Проверка SQLite...")
if not os.path.exists(SQLITE_PATH):
    print(f"❌ SQLite база не найдена: {SQLITE_PATH}")
    sys.exit(1)

try:
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    cursor = sqlite_conn.cursor()

    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✅ Найдено таблиц в SQLite: {len(tables)}")
    print(f"   Таблицы: {', '.join(tables)}")

except Exception as e:
    print(f"❌ Ошибка чтения SQLite: {e}")
    sys.exit(1)

# 3. Переносим данные
print("\n3️⃣  Перенос данных...")
Session = sessionmaker(bind=pg_engine)
session = Session()

total_migrated = 0

for table_name in tables:
    try:
        # Читаем данные из SQLite
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            print(f"   {table_name}: пусто, пропускаем")
            continue

        # Получаем имена колонок
        columns = [description[0] for description in cursor.description]

        # Вставляем в PostgreSQL
        migrated = 0
        for row in rows:
            row_dict = dict(zip(columns, row))

            # Формируем INSERT запрос
            cols = ', '.join(columns)
            placeholders = ', '.join([f":{col}" for col in columns])
            query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

            try:
                session.execute(query, row_dict)
                migrated += 1
            except Exception as e:
                print(f"   ⚠️  Ошибка вставки в {table_name}: {e}")
                continue

        session.commit()
        total_migrated += migrated
        print(f"   ✅ {table_name}: {migrated} записей")

    except Exception as e:
        print(f"   ❌ Ошибка с таблицей {table_name}: {e}")
        session.rollback()
        continue

sqlite_conn.close()
session.close()

print(f"\n✅ Миграция завершена!")
print(f"📊 Всего перенесено записей: {total_migrated}")
print("=" * 60)
