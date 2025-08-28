"""
Добавление полей для публикации в Telegram канал к модели Portfolio
"""

def upgrade(connection):
    """Применить миграцию"""
    try:
        # Добавляем поля для Telegram публикации
        connection.execute("""
            ALTER TABLE portfolio 
            ADD COLUMN is_published BOOLEAN DEFAULT FALSE
        """)
        
        connection.execute("""
            ALTER TABLE portfolio 
            ADD COLUMN telegram_message_id INTEGER NULL
        """)
        
        connection.execute("""
            ALTER TABLE portfolio 
            ADD COLUMN published_at DATETIME NULL
        """)
        
        connection.execute("""
            ALTER TABLE portfolio 
            ADD COLUMN telegram_channel_id VARCHAR(100) NULL
        """)
        
        print("✅ Добавлены поля для Telegram публикации в таблицу portfolio")
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        raise

def downgrade(connection):
    """Откатить миграцию"""
    try:
        connection.execute("ALTER TABLE portfolio DROP COLUMN is_published")
        connection.execute("ALTER TABLE portfolio DROP COLUMN telegram_message_id")
        connection.execute("ALTER TABLE portfolio DROP COLUMN published_at")
        connection.execute("ALTER TABLE portfolio DROP COLUMN telegram_channel_id")
        
        print("✅ Поля Telegram публикации удалены из таблицы portfolio")
        
    except Exception as e:
        print(f"❌ Ошибка отката миграции: {e}")
        raise