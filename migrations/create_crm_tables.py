#!/usr/bin/env python3
"""
Миграция: Создание таблиц CRM системы
Дата: 2025-10-12
Описание: Создает таблицы clients, leads, deals, documents и связанные с ними для полноценной CRM системы
"""

import os
import sys

# Добавляем корневую директорию в PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.database.crm_models import Base, Client, Lead, Deal, ClientTag, ServiceCatalog, Document, DocumentTemplate
from app.database.models import Base as MainBase

def run_migration():
    """Запуск миграции"""
    # Используем правильную БД (data/bot.db для админки и бота)
    db_path = os.environ.get("DATABASE_PATH")
    if not db_path:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bot.db")

    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False

    print(f"🔄 Запуск миграции для {db_path}")

    try:
        # Создаем движок для работы с БД
        engine = create_engine(f'sqlite:///{db_path}')

        # Создаем все CRM таблицы
        print("📝 Создаем таблицы CRM системы...")
        Base.metadata.create_all(engine)

        print("✅ Таблицы созданы:")
        print("  - clients (Клиенты)")
        print("  - leads (Лиды)")
        print("  - deals (Сделки)")
        print("  - client_tag (Теги клиентов)")
        print("  - client_tags (Связь клиентов и тегов)")
        print("  - service_catalog (Каталог услуг)")
        print("  - deal_services (Связь сделок и услуг)")
        print("  - documents (Документы)")
        print("  - document_templates (Шаблоны документов)")

        print("✅ Миграция завершена успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
