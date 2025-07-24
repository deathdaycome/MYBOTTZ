"""
Миграция: Добавление поля цвета для задач
"""

from sqlalchemy import Column, String, text
from app.database.database import engine

def upgrade():
    """Добавить поле color в таблицу tasks"""
    
    # Добавляем поле цвета карточки
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE tasks ADD COLUMN color VARCHAR(20) DEFAULT 'normal'
            """))
            print("✅ Добавлено поле color в таблицу tasks")
        except Exception as e:
            print(f"⚠️  Поле color возможно уже существует: {e}")

def downgrade():
    """Удалить поле color из таблицы tasks"""
    
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE tasks DROP COLUMN color
        """))
        print("❌ Удалено поле color из таблицы tasks")

if __name__ == "__main__":
    upgrade()