#!/usr/bin/env python3
"""
Миграция 012: Добавление Avito-специфичных полей в таблицу clients
"""

import sqlite3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.config.logging import get_logger

logger = get_logger(__name__)

def migrate():
    """Добавляет Avito-специфичные поля в таблицу clients"""
    db_path = 'admin_panel.db'
    
    if not os.path.exists(db_path):
        logger.error(f"База данных не найдена: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица clients
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='clients'
        """)
        
        if not cursor.fetchone():
            logger.error("Таблица clients не найдена")
            return False
        
        # Добавляем новые поля для Avito интеграции
        fields_to_add = [
            ("avito_chat_id", "VARCHAR(100)"),
            ("avito_user_id", "VARCHAR(100)"), 
            ("avito_status", "VARCHAR(50)"),
            ("avito_dialog_history", "JSON"),
            ("avito_notes", "TEXT"),
            ("avito_follow_up", "DATETIME")
        ]
        
        for field_name, field_type in fields_to_add:
            try:
                # Проверяем существует ли поле
                cursor.execute(f"PRAGMA table_info(clients)")
                existing_columns = [row[1] for row in cursor.fetchall()]
                
                if field_name not in existing_columns:
                    default_value = "'[]'" if field_type == "JSON" else "NULL"
                    cursor.execute(f"""
                        ALTER TABLE clients 
                        ADD COLUMN {field_name} {field_type} DEFAULT {default_value}
                    """)
                    logger.info(f"Добавлено поле {field_name} в таблицу clients")
                else:
                    logger.info(f"Поле {field_name} уже существует")
                    
            except sqlite3.Error as e:
                logger.error(f"Ошибка при добавлении поля {field_name}: {e}")
                continue
        
        # Создаем индексы для поиска по Avito полям
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_avito_chat_id 
                ON clients(avito_chat_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_avito_user_id 
                ON clients(avito_user_id)
            """)
            logger.info("Созданы индексы для Avito полей")
        except sqlite3.Error as e:
            logger.error(f"Ошибка создания индексов: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Миграция 012 (Avito поля клиентов) выполнена успешно")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка миграции: {e}")
        return False

if __name__ == "__main__":
    success = migrate()
    if success:
        print("✅ Миграция выполнена успешно")
    else:
        print("❌ Ошибка выполнения миграции")
        sys.exit(1)