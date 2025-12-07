#!/usr/bin/env python3
"""
Миграция: Исправление схемы таблицы task_comments
Проблема: колонки is_read, read_by, attachments были добавлены без правильных запятых
Решение: Пересоздать таблицу с правильной схемой
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bot.db')

def migrate():
    """Пересоздание таблицы task_comments с правильной схемой"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Начинаем исправление схемы таблицы task_comments...")

        # 1. Создаем временную таблицу с правильной схемой
        print("1. Создаем временную таблицу...")
        cursor.execute("""
            CREATE TABLE task_comments_new (
                id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                comment_type VARCHAR(50),
                is_internal BOOLEAN,
                created_at DATETIME,
                is_read BOOLEAN DEFAULT 0,
                read_by TEXT,
                attachments JSON DEFAULT '[]',
                PRIMARY KEY (id),
                FOREIGN KEY(task_id) REFERENCES tasks (id),
                FOREIGN KEY(author_id) REFERENCES admin_users (id)
            )
        """)

        # 2. Копируем данные из старой таблицы
        print("2. Копируем данные...")
        cursor.execute("""
            INSERT INTO task_comments_new (id, task_id, author_id, comment, comment_type, is_internal, created_at)
            SELECT id, task_id, author_id, comment, comment_type, is_internal, created_at
            FROM task_comments
        """)

        # 3. Удаляем старую таблицу
        print("3. Удаляем старую таблицу...")
        cursor.execute("DROP TABLE task_comments")

        # 4. Переименовываем новую таблицу
        print("4. Переименовываем новую таблицу...")
        cursor.execute("ALTER TABLE task_comments_new RENAME TO task_comments")

        # 5. Восстанавливаем индекс
        print("5. Создаем индекс...")
        cursor.execute("CREATE INDEX ix_task_comments_id ON task_comments (id)")

        conn.commit()
        print("✅ Таблица task_comments успешно пересоздана с правильной схемой")

    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
