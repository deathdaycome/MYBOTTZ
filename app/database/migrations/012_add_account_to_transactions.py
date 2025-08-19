"""
Миграция для добавления поля account в таблицу finance_transactions
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from ...database.database import engine
from ...config.logging import get_logger

logger = get_logger(__name__)

def upgrade():
    """Добавляем поле account в таблицу finance_transactions"""
    
    with engine.connect() as conn:
        try:
            # Проверяем, существует ли уже колонка
            result = conn.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('finance_transactions') 
                WHERE name='account'
            """))
            
            if result.scalar() == 0:
                # Добавляем колонку account
                conn.execute(text("""
                    ALTER TABLE finance_transactions 
                    ADD COLUMN account VARCHAR(50) DEFAULT 'card'
                """))
                conn.commit()
                logger.info("✅ Добавлено поле account в таблицу finance_transactions")
            else:
                logger.info("ℹ️ Поле account уже существует в таблице finance_transactions")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении поля account: {e}")
            raise

def downgrade():
    """Удаляем поле account из таблицы finance_transactions"""
    
    with engine.connect() as conn:
        try:
            # SQLite не поддерживает DROP COLUMN напрямую
            # Нужно пересоздать таблицу без этого поля
            logger.warning("⚠️ Откат миграции для SQLite требует пересоздания таблицы")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при откате миграции: {e}")
            raise

if __name__ == "__main__":
    upgrade()