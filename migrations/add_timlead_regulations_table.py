"""
Миграция для создания таблицы timlead_regulations
"""
import sqlite3
from datetime import datetime

def run_migration():
    conn = sqlite3.connect('data/bot.db')
    cursor = conn.cursor()

    try:
        # Создаем таблицу для регламентов тимлида
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timlead_regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regulation_number INTEGER NOT NULL UNIQUE,
                title TEXT NOT NULL,
                content TEXT,
                icon TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Создаем индекс по regulation_number для быстрого поиска
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_regulation_number
            ON timlead_regulations(regulation_number)
        """)

        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM timlead_regulations")
        count = cursor.fetchone()[0]

        # Если таблица пустая, заполняем дефолтными значениями
        if count == 0:
            default_regulations = [
                (1, 'Регламент 1', 'Описание первого регламента. Содержимое будет добавлено позже.', 'Book'),
                (2, 'Регламент 2', 'Описание второго регламента. Содержимое будет добавлено позже.', 'CheckSquare'),
                (3, 'Регламент 3', 'Описание третьего регламента. Содержимое будет добавлено позже.', 'Users'),
                (4, 'Регламент 4', 'Описание четвёртого регламента. Содержимое будет добавлено позже.', 'CalendarCheck'),
                (5, 'Регламент 5', 'Описание пятого регламента. Содержимое будет добавлено позже.', 'TrendingUp'),
                (6, 'Регламент 6', 'Описание шестого регламента. Содержимое будет добавлено позже.', 'FileText'),
                (7, 'Регламент 7', 'Описание седьмого регламента. Содержимое будет добавлено позже.', 'FileText'),
                (8, 'Регламент 8', 'Описание восьмого регламента. Содержимое будет добавлено позже.', 'Settings'),
                (9, 'Регламент 9', 'Описание девятого регламента. Содержимое будет добавлено позже.', 'Shield'),
            ]

            cursor.executemany("""
                INSERT INTO timlead_regulations (regulation_number, title, content, icon)
                VALUES (?, ?, ?, ?)
            """, default_regulations)

            print(f"✅ Добавлено {len(default_regulations)} регламентов по умолчанию")

        conn.commit()
        print("✅ Миграция успешно выполнена: таблица timlead_regulations создана")

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка миграции: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
