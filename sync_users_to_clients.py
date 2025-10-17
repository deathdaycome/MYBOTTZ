#!/usr/bin/env python3
"""
Скрипт синхронизации: создаёт CRM клиентов для пользователей, у которых их ещё нет
Запускается автоматически или вручную
"""

import sys
import os
from datetime import datetime

# Добавляем корневую директорию в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import User
from app.database.crm_models import Client, ClientType, ClientStatus

def sync_users_to_clients():
    """Создаёт клиентов для всех пользователей без клиентов"""

    # Подключаемся к БД
    db_path = os.path.join(os.path.dirname(__file__), "admin_panel.db")
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Находим всех пользователей
        users = session.query(User).all()
        print(f"📊 Всего пользователей: {len(users)}")

        created_count = 0
        skipped_count = 0

        for user in users:
            # Проверяем есть ли уже клиент
            existing_client = session.query(Client).filter(
                Client.telegram_user_id == user.id
            ).first()

            if existing_client:
                skipped_count += 1
                continue

            # Создаём клиента
            client_name = user.first_name or user.username or f"Клиент {user.id}"

            client = Client(
                name=client_name,
                type=ClientType.INDIVIDUAL,
                status=ClientStatus.NEW,
                phone=user.phone,
                telegram=f"@{user.username}" if user.username else None,
                source="auto_sync",
                description="Создан автоматически синхронизацией пользователей",
                telegram_user_id=user.id,
                manager_id=1,
                created_by_id=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            session.add(client)
            created_count += 1
            print(f"  ✅ Создан клиент для user_id={user.id}: {client_name}")

        session.commit()

        print(f"\n✅ Синхронизация завершена:")
        print(f"   Создано клиентов: {created_count}")
        print(f"   Пропущено (уже есть): {skipped_count}")
        print(f"   Всего клиентов в БД: {session.query(Client).count()}")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = sync_users_to_clients()
    sys.exit(0 if success else 1)
