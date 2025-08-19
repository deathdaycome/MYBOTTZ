#!/usr/bin/env python3
"""
Миграция: Добавление полей для интеграции CRM (Deal ↔ Project)
Этап 5: Интеграция разделов между собой
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.database.database import get_db_context
from app.config.logging import get_logger

logger = get_logger(__name__)

def run_migration():
    """Запуск миграции"""
    logger.info("=== НАЧАЛО МИГРАЦИИ: Добавление полей интеграции CRM ===")
    
    with get_db_context() as db:
        inspector = inspect(db.bind)
        
        try:
            # 1. Добавляем поле converted_to_project_id в таблицу deals
            existing_columns = [col['name'] for col in inspector.get_columns('deals')]
            
            if 'converted_to_project_id' not in existing_columns:
                logger.info("Добавляем поле converted_to_project_id в таблицу deals")
                db.execute(text("""
                    ALTER TABLE deals 
                    ADD COLUMN converted_to_project_id INTEGER REFERENCES projects(id)
                """))
                logger.info("✓ Поле converted_to_project_id добавлено в deals")
            else:
                logger.info("Поле converted_to_project_id уже существует в deals")
            
            # 2. Добавляем поля source_deal_id и paid_amount в таблицу projects
            project_columns = [col['name'] for col in inspector.get_columns('projects')]
            
            if 'source_deal_id' not in project_columns:
                logger.info("Добавляем поле source_deal_id в таблицу projects")
                db.execute(text("""
                    ALTER TABLE projects 
                    ADD COLUMN source_deal_id INTEGER
                """))
                logger.info("✓ Поле source_deal_id добавлено в projects")
            else:
                logger.info("Поле source_deal_id уже существует в projects")
            
            if 'paid_amount' not in project_columns:
                logger.info("Добавляем поле paid_amount в таблицу projects")
                db.execute(text("""
                    ALTER TABLE projects 
                    ADD COLUMN paid_amount REAL DEFAULT 0.0
                """))
                logger.info("✓ Поле paid_amount добавлено в projects")
            else:
                logger.info("Поле paid_amount уже существует в projects")
            
            # 3. Создаем индексы для оптимизации
            logger.info("Создаем индексы для полей интеграции")
            
            try:
                db.execute(text("CREATE INDEX IF NOT EXISTS idx_deals_converted_to_project_id ON deals(converted_to_project_id)"))
                logger.info("✓ Индекс для deals.converted_to_project_id создан")
            except Exception as e:
                logger.warning(f"Индекс для deals.converted_to_project_id уже существует: {e}")
            
            try:
                db.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_source_deal_id ON projects(source_deal_id)"))
                logger.info("✓ Индекс для projects.source_deal_id создан")
            except Exception as e:
                logger.warning(f"Индекс для projects.source_deal_id уже существует: {e}")
            
            # 4. Обновляем существующие данные
            logger.info("Обновляем существующие данные...")
            
            # Синхронизируем существующие связи deal.project_id → deal.converted_to_project_id
            result = db.execute(text("""
                UPDATE deals 
                SET converted_to_project_id = project_id 
                WHERE project_id IS NOT NULL 
                AND converted_to_project_id IS NULL
            """))
            updated_deals = result.rowcount
            if updated_deals > 0:
                logger.info(f"✓ Обновлено {updated_deals} записей в deals")
            
            # Синхронизируем обратные связи через project_metadata
            result = db.execute(text("""
                UPDATE projects 
                SET source_deal_id = CAST(JSON_EXTRACT(project_metadata, '$.deal_id') AS INTEGER)
                WHERE JSON_EXTRACT(project_metadata, '$.deal_id') IS NOT NULL 
                AND source_deal_id IS NULL
            """))
            updated_projects = result.rowcount
            if updated_projects > 0:
                logger.info(f"✓ Обновлено {updated_projects} записей в projects")
            
            db.commit()
            logger.info("=== МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО ===")
            
        except Exception as e:
            logger.error(f"Ошибка миграции: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    run_migration()