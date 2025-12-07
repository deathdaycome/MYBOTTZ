#!/usr/bin/env python3
"""
Миграция: Автоматическое присвоение client_id всем серверам
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.services.client_id_service import client_id_service

settings = get_settings()


def run_migration():
    """Присвоить client_id всем серверам"""

    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        print("🔄 Присвоение client_id всем серверам...")
        print("=" * 60)

        result = client_id_service.assign_client_ids_to_all_servers(db)

        print("\n✅ Миграция успешно завершена!")
        print("=" * 60)
        print(f"\n📊 Статистика:")
        print(f"   Всего серверов без client_id: {result['total_servers']}")
        print(f"   Обновлено серверов: {result['updated']}")
        print(f"   Уникальных клиентов: {result['unique_clients']}")

        if result['updated'] > 0:
            print("\n💡 Что произошло:")
            print("   1. Серверы с одинаковым именем клиента получили одинаковый client_id")
            print("   2. Для каждого уникального имени клиента создан свой client_id")
            print("   3. Обновлены балансы для всех клиентов")
            print("   4. Теперь можно пополнять баланс для каждого клиента")
            print("\n🎯 Следующие шаги:")
            print("   1. Обновите страницу Хостинга в админ-панели")
            print("   2. Увидите виджеты балансов для всех серверов")
            print("   3. Укажите цены (client_price) для серверов")
            print("   4. Пополните балансы клиентов через кнопку '+'")
        else:
            print("\n💡 Все серверы уже имеют client_id")

    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
