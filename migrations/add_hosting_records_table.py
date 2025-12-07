"""
Миграция: Создание таблицы hosting_records
Дата: 2025-12-07
Описание: Добавляет таблицу для учета хостинга проектов
"""

import sqlite3
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def migrate(db_path='/app/data/bot.db'):
    """Создать таблицу hosting_records"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Начинаем миграцию: создание таблицы hosting_records...")

        # Проверяем существует ли таблица
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='hosting_records'"
        )

        if cursor.fetchone():
            print("  ℹ️  Таблица hosting_records уже существует")
            conn.close()
            return

        # Создаем таблицу hosting_records
        cursor.execute("""
            CREATE TABLE hosting_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                project_id INTEGER,
                client_id INTEGER,
                domain TEXT,
                subdomain TEXT,
                ftp_login TEXT,
                ftp_password TEXT,
                ftp_host TEXT,
                ftp_port INTEGER DEFAULT 21,
                db_name TEXT,
                db_user TEXT,
                db_password TEXT,
                db_host TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (server_id) REFERENCES hosting_servers(id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (client_id) REFERENCES users(id)
            )
        """)
        print("  ✅ Создана таблица hosting_records")

        # Создаем индексы для быстрого поиска
        cursor.execute(
            "CREATE INDEX idx_hosting_records_project ON hosting_records(project_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_hosting_records_client ON hosting_records(client_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_hosting_records_server ON hosting_records(server_id)"
        )
        print("  ✅ Созданы индексы")

        conn.commit()
        print("✅ Миграция успешно применена!")

        # Вывод статистики
        cursor.execute("SELECT COUNT(*) FROM hosting_records")
        count = cursor.fetchone()[0]
        print(f"\n📊 Статистика:")
        print(f"  • Записей в hosting_records: {count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Определяем путь к БД в зависимости от окружения
    if os.path.exists('/app/data/bot.db'):
        db_path = '/app/data/bot.db'
    elif os.path.exists('data/bot.db'):
        db_path = 'data/bot.db'
    else:
        db_path = '/app/data/bot.db'

    migrate(db_path)
