#!/usr/bin/env python3
"""
Автоматическое исправление БД при запуске
Запускается автоматически из main.py
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

def ensure_db_columns():
    """Убеждаемся что все необходимые колонки существуют"""
    db_path = "admin_panel.db"
    
    if not os.path.exists(db_path):
        logger.warning(f"База данных не найдена: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Список необходимых колонок
        required_columns = {
            'projects': [
                ('source_deal_id', 'INTEGER'),
                ('paid_amount', 'REAL DEFAULT 0.0')
            ],
            'finance_transactions': [
                ('account', "VARCHAR(50) DEFAULT 'card'")
            ],
            'deals': [
                ('converted_to_project_id', 'INTEGER')
            ]
        }
        
        for table_name, columns in required_columns.items():
            # Проверяем существование таблицы
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                logger.info(f"Таблица {table_name} не существует, пропускаем")
                continue
            
            # Получаем существующие колонки
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # Добавляем недостающие колонки
            for col_name, col_type in columns:
                if col_name not in existing_columns:
                    logger.info(f"Добавляем колонку {col_name} в таблицу {table_name}")
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                        logger.info(f"✓ Колонка {col_name} добавлена в {table_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            logger.info(f"Колонка {col_name} уже существует в {table_name}")
                        else:
                            logger.error(f"Ошибка добавления колонки {col_name}: {e}")
        
        conn.commit()
        conn.close()
        logger.info("Проверка структуры БД завершена")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при проверке БД: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ensure_db_columns()