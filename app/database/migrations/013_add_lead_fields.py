"""
Миграция для добавления новых полей в таблицу leads для улучшенной воронки продаж
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from ...database.database import engine
from ...config.logging import get_logger

logger = get_logger(__name__)

def upgrade():
    """Добавляем новые поля в таблицу leads"""
    
    with engine.connect() as conn:
        try:
            # Добавляем поля для типа источника и информации о компании
            fields_to_add = [
                ("source_type", "VARCHAR(50)"),  # hot/cold
                ("company_name", "VARCHAR(500)"),
                ("company_sphere", "VARCHAR(200)"),
                ("company_website", "VARCHAR(500)"),
                ("company_address", "TEXT"),
                ("company_size", "VARCHAR(50)"),
                ("call_history", "TEXT DEFAULT '[]'"),
                ("email_history", "TEXT DEFAULT '[]'"),
                ("tags", "TEXT DEFAULT '[]'")
            ]
            
            for field_name, field_type in fields_to_add:
                # Проверяем, существует ли уже колонка
                result = conn.execute(text(f"""
                    SELECT COUNT(*) FROM pragma_table_info('leads') 
                    WHERE name='{field_name}'
                """))
                
                if result.scalar() == 0:
                    # Добавляем колонку
                    conn.execute(text(f"""
                        ALTER TABLE leads 
                        ADD COLUMN {field_name} {field_type}
                    """))
                    logger.info(f"✅ Добавлено поле {field_name} в таблицу leads")
                else:
                    logger.info(f"ℹ️ Поле {field_name} уже существует в таблице leads")
            
            conn.commit()
            logger.info("✅ Миграция полей для воронки продаж завершена")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении полей: {e}")
            raise

def downgrade():
    """Откат миграции"""
    logger.warning("⚠️ Откат миграции для SQLite требует пересоздания таблицы")

if __name__ == "__main__":
    upgrade()