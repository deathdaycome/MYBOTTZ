"""
Миграция для обновления полей Portfolio
"""

from sqlalchemy import text
from app.database.database import engine

def upgrade():
    """Обновляем таблицу portfolio"""
    
    with engine.connect() as conn:
        # Проверяем существование полей и добавляем если их нет
        try:
            # Добавляем новые поля если их нет
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS category_id INTEGER;
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS technologies TEXT;
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS client_name VARCHAR(255);
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS project_url TEXT;
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS duration_months INTEGER;
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS budget_range VARCHAR(100);
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'completed';
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS featured BOOLEAN DEFAULT FALSE;
            """))
            
            conn.execute(text("""
                ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
            """))
            
            conn.commit()
            print("✅ Миграция portfolio успешно выполнена")
            
        except Exception as e:
            print(f"⚠️  Ошибка миграции (возможно поля уже существуют): {e}")

def downgrade():
    """Откатываем изменения"""
    pass

if __name__ == "__main__":
    upgrade()
