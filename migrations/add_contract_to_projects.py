"""
Миграция: Добавление поля contract_document_id в таблицу projects
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/bot.db"

def run_migration():
    """Применить миграцию"""
    print("🔄 Начинаем миграцию: Добавление поля contract_document_id в projects")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли уже колонка
        cursor.execute("PRAGMA table_info(projects)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'contract_document_id' in columns:
            print("⚠️  Колонка contract_document_id уже существует")
        else:
            # Добавляем колонку
            cursor.execute("""
                ALTER TABLE projects
                ADD COLUMN contract_document_id INTEGER
            """)

            conn.commit()
            print("✅ Колонка contract_document_id успешно добавлена")

        print("\n✅ Миграция завершена успешно!")
        print("\n💡 Теперь можно привязывать договоры к проектам")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def rollback_migration():
    """Откатить миграцию"""
    print("⚠️  Откат невозможен - SQLite не поддерживает удаление колонок")
    print("Колонка contract_document_id останется в таблице")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()
