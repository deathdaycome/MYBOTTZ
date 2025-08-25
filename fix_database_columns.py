#!/usr/bin/env python3
"""
Экстренное исправление: добавление недостающих колонок в базу данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.database.database import get_db_context
from app.config.logging import get_logger

logger = get_logger(__name__)

def fix_database():
    """Добавляем недостающие колонки"""
    logger.info("=== ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ ===")
    
    with get_db_context() as db:
        inspector = inspect(db.bind)
        
        try:
            # 1. ИСПРАВЛЯЕМ ТАБЛИЦУ CLIENTS - добавляем Avito колонки
            if inspector.has_table('clients'):
                logger.info("Проверяем таблицу clients...")
                client_columns = [col['name'] for col in inspector.get_columns('clients')]
                
                avito_client_columns = [
                    ('avito_chat_id', 'TEXT'),
                    ('avito_user_id', 'TEXT'),
                    ('avito_status', 'TEXT'),
                    ('avito_dialog_history', 'TEXT'),
                    ('avito_notes', 'TEXT'),
                    ('avito_follow_up', 'TEXT'),
                    ('telegram_user_id', 'TEXT')
                ]
                
                for col_name, col_type in avito_client_columns:
                    if col_name not in client_columns:
                        logger.info(f"Добавляем {col_name} в clients")
                        db.execute(text(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}"))
                        logger.info(f"✓ {col_name} добавлен")
                    else:
                        logger.info(f"ℹ️ Колонка {col_name} уже существует в clients")
            
            # 2. ИСПРАВЛЯЕМ ТАБЛИЦУ LEADS - добавляем недостающие колонки
            if inspector.has_table('leads'):
                logger.info("Проверяем таблицу leads...")
                lead_columns = [col['name'] for col in inspector.get_columns('leads')]
                
                if 'source_type' not in lead_columns:
                    logger.info("Добавляем source_type в leads")
                    db.execute(text("ALTER TABLE leads ADD COLUMN source_type TEXT"))
                    logger.info("✓ source_type добавлен")
                else:
                    logger.info("ℹ️ Колонка source_type уже существует в leads")
            
            # 3. Проверяем и добавляем колонки в projects
            if inspector.has_table('projects'):
                project_columns = [col['name'] for col in inspector.get_columns('projects')]
                
                if 'source_deal_id' not in project_columns:
                    logger.info("Добавляем source_deal_id в projects")
                    db.execute(text("ALTER TABLE projects ADD COLUMN source_deal_id INTEGER"))
                    logger.info("✓ source_deal_id добавлен")
                
                if 'paid_amount' not in project_columns:
                    logger.info("Добавляем paid_amount в projects")
                    db.execute(text("ALTER TABLE projects ADD COLUMN paid_amount REAL DEFAULT 0.0"))
                    logger.info("✓ paid_amount добавлен")
            
            # 4. Проверяем и добавляем колонки в finance_transactions
            if inspector.has_table('finance_transactions'):
                finance_columns = [col['name'] for col in inspector.get_columns('finance_transactions')]
                
                if 'account' not in finance_columns:
                    logger.info("Добавляем account в finance_transactions")
                    db.execute(text("ALTER TABLE finance_transactions ADD COLUMN account VARCHAR(50) DEFAULT 'card'"))
                    logger.info("✓ account добавлен")
            
            # 5. Проверяем и добавляем колонки в deals
            if inspector.has_table('deals'):
                deal_columns = [col['name'] for col in inspector.get_columns('deals')]
                
                if 'converted_to_project_id' not in deal_columns:
                    logger.info("Добавляем converted_to_project_id в deals")
                    db.execute(text("ALTER TABLE deals ADD COLUMN converted_to_project_id INTEGER"))
                    logger.info("✓ converted_to_project_id добавлен")
            
            db.commit()
            logger.info("=== ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО ===")
            logger.info("🔄 Необходимо перезапустить сервер для применения изменений")
            
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    fix_database()