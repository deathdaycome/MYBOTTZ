"""
Миграция: Добавление чатов проектов для общения клиента с исполнителем

Создает:
1. Колонка client_telegram_username в projects
2. Таблица project_chats
3. Таблица project_chat_messages

Функционал:
- Один чат на проект
- Сообщения между клиентом и исполнителем
- Анонимность (исполнитель не видит контакты)
- Детект нарушений (попытка поделиться контактами)
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/bot.db"

def run_migration():
    """Применить миграцию"""
    print("🔄 Начинаем миграцию: Создание системы чатов проектов")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # === 1. Добавляем колонку client_telegram_username в projects ===
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]

        if "client_telegram_username" in columns:
            print("⚠️  Колонка client_telegram_username уже существует")
        else:
            cursor.execute("""
                ALTER TABLE projects
                ADD COLUMN client_telegram_username VARCHAR(100)
            """)
            print("✅ Добавлена колонка client_telegram_username в projects")

        # === 2. Создаем таблицу project_chats ===
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='project_chats'
        """)

        if cursor.fetchone():
            print("⚠️  Таблица project_chats уже существует")
        else:
            cursor.execute("""
                CREATE TABLE project_chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL UNIQUE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP,

                    unread_by_executor INTEGER DEFAULT 0,
                    unread_by_client INTEGER DEFAULT 0,

                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE UNIQUE INDEX idx_project_chats_project_id
                ON project_chats(project_id)
            """)

            print("✅ Таблица project_chats создана")

        # === 3. Создаем таблицу project_chat_messages ===
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='project_chat_messages'
        """)

        if cursor.fetchone():
            print("⚠️  Таблица project_chat_messages уже существует")
        else:
            cursor.execute("""
                CREATE TABLE project_chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,

                    sender_type VARCHAR(20) NOT NULL,
                    sender_id INTEGER,

                    message_text TEXT,
                    attachments TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read_by_executor BOOLEAN DEFAULT 0,
                    is_read_by_client BOOLEAN DEFAULT 0,
                    read_at TIMESTAMP,

                    has_contact_violation BOOLEAN DEFAULT 0,
                    violation_details TEXT,

                    related_revision_id INTEGER,

                    FOREIGN KEY (chat_id) REFERENCES project_chats (id) ON DELETE CASCADE,
                    FOREIGN KEY (related_revision_id) REFERENCES project_revisions (id)
                )
            """)

            cursor.execute("""
                CREATE INDEX idx_project_chat_messages_chat_id
                ON project_chat_messages(chat_id)
            """)

            cursor.execute("""
                CREATE INDEX idx_project_chat_messages_created_at
                ON project_chat_messages(created_at)
            """)

            print("✅ Таблица project_chat_messages создана")

        conn.commit()

        # Показываем статистику
        print(f"\n📊 Статистика системы:")

        cursor.execute("SELECT COUNT(*) FROM projects")
        projects_count = cursor.fetchone()[0]
        print(f"   Проектов в системе: {projects_count}")

        cursor.execute("SELECT COUNT(*) FROM project_chats")
        chats_count = cursor.fetchone()[0]
        print(f"   Чатов создано: {chats_count}")

        print("\n✅ Миграция завершена успешно!")
        print("\n💡 Создана система чатов проектов:")
        print("   • Один чат на проект")
        print("   • Сообщения между клиентом и исполнителем")
        print("   • Анонимность исполнителя")
        print("   • Автопривязка через Telegram username")
        print("   • Детект попыток поделиться контактами")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def rollback_migration():
    """Откатить миграцию"""
    print("🔄 Откат миграции: Удаление системы чатов проектов")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS project_chat_messages")
        cursor.execute("DROP TABLE IF EXISTS project_chats")
        # client_telegram_username остается (сложно удалить колонку в SQLite)

        conn.commit()
        print("✅ Таблицы project_chat_messages и project_chats удалены")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при откате миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()
