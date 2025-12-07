"""
Миграция: Добавление связи серверов с проектами

Добавляет поле project_id в таблицу hosting_servers
для интеграции TimeWeb хостинга с проектами
"""

import sqlite3
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/bot.db"

def run_migration():
    """Применить миграцию"""
    print("🔄 Начинаем миграцию: Добавление связи серверов с проектами")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Проверяем существует ли колонка project_id
        cursor.execute("PRAGMA table_info(hosting_servers)")
        columns = [col[1] for col in cursor.fetchall()]

        if "project_id" in columns:
            print("⚠️  Колонка project_id уже существует, пропускаем")
        else:
            # Добавляем колонку project_id
            cursor.execute("""
                ALTER TABLE hosting_servers
                ADD COLUMN project_id INTEGER REFERENCES projects(id)
            """)
            print("✅ Добавлена колонка project_id")

            # Создаем индекс для быстрого поиска серверов по проекту
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_hosting_servers_project_id
                ON hosting_servers(project_id)
            """)
            print("✅ Создан индекс для project_id")

        conn.commit()

        # Показываем статистику
        print(f"\n📊 Статистика системы:")

        cursor.execute("SELECT COUNT(*) FROM hosting_servers")
        servers_count = cursor.fetchone()[0]
        print(f"   Серверов в аренде: {servers_count}")

        cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'in_progress'")
        active_projects = cursor.fetchone()[0]
        print(f"   Активных проектов: {active_projects}")

        print("\n✅ Миграция завершена успешно!")
        print("\n💡 Теперь серверы можно привязывать к проектам:")
        print("   • Автоматическое заполнение данных клиента из проекта")
        print("   • Отображение серверов на странице проекта")
        print("   • Связь финансов проекта и хостинга")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def rollback_migration():
    """Откатить миграцию"""
    print("🔄 Откат миграции: Удаление связи серверов с проектами")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # В SQLite нельзя просто удалить колонку через ALTER TABLE DROP COLUMN
        # Нужно создать новую таблицу без этой колонки и скопировать данные
        print("⚠️  Внимание: Откат миграции требует пересоздания таблицы")
        print("⚠️  Данные серверов будут сохранены, но связи с проектами будут удалены")

        # Удаляем индекс
        cursor.execute("DROP INDEX IF EXISTS idx_hosting_servers_project_id")

        # Для полного отката нужно пересоздать таблицу без project_id
        # Но это сложная операция, поэтому просто обнуляем значения
        cursor.execute("UPDATE hosting_servers SET project_id = NULL")

        conn.commit()
        print("✅ Связи с проектами удалены (колонка project_id обнулена)")

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
