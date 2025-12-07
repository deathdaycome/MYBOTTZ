"""
Миграция: Добавление таблицы для отслеживания уведомлений о дедлайнах задач

Эта таблица позволит контролировать, какие уведомления уже были отправлены,
чтобы не спамить пользователей повторяющимися напоминаниями.

Типы уведомлений:
- 24h_before: за 24 часа до дедлайна
- 4h_before: за 4 часа до дедлайна
- 1h_before: за 1 час до дедлайна
- overdue: при первой просрочке
- daily_overdue: ежедневное напоминание о просроченной задаче
"""

import sqlite3
import sys
import os
from datetime import datetime

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings

DB_PATH = "data/bot.db"

def run_migration():
    """Применить миграцию"""
    print("🔄 Начинаем миграцию: Создание таблицы task_deadline_notifications")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли уже таблица
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='task_deadline_notifications'
        """)

        if cursor.fetchone():
            print("⚠️  Таблица task_deadline_notifications уже существует, пропускаем создание")
        else:
            # Создаём таблицу
            cursor.execute("""
                CREATE TABLE task_deadline_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    notification_type VARCHAR(50) NOT NULL,
                    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deadline_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
                )
            """)

            # Создаём индексы для быстрого поиска
            cursor.execute("""
                CREATE INDEX idx_task_deadline_notifications_task_id
                ON task_deadline_notifications(task_id)
            """)

            cursor.execute("""
                CREATE INDEX idx_task_deadline_notifications_type
                ON task_deadline_notifications(task_id, notification_type)
            """)

            cursor.execute("""
                CREATE INDEX idx_task_deadline_notifications_sent_at
                ON task_deadline_notifications(sent_at)
            """)

            conn.commit()
            print("✅ Таблица task_deadline_notifications успешно создана")
            print("✅ Индексы успешно созданы")

        # Показываем статистику таблицы tasks
        cursor.execute("""
            SELECT
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
                SUM(CASE WHEN deadline IS NOT NULL THEN 1 ELSE 0 END) as tasks_with_deadline
            FROM tasks
        """)

        total, pending, with_deadline = cursor.fetchone()
        print(f"\n📊 Статистика задач:")
        print(f"   Всего задач: {total}")
        print(f"   Задач в статусе pending: {pending}")
        print(f"   Задач с дедлайном: {with_deadline}")

        print("\n✅ Миграция завершена успешно!")
        print("\n💡 Теперь система будет отправлять уведомления:")
        print("   • За 24 часа до дедлайна - 1 раз")
        print("   • За 4 часа до дедлайна - 1 раз")
        print("   • За 1 час до дедлайна - 1 раз")
        print("   • При просрочке - 1 раз")
        print("   • При долгой просрочке - раз в день")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def rollback_migration():
    """Откатить миграцию"""
    print("🔄 Откат миграции: Удаление таблицы task_deadline_notifications")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Удаляем таблицу
        cursor.execute("DROP TABLE IF EXISTS task_deadline_notifications")
        conn.commit()
        print("✅ Таблица task_deadline_notifications удалена")

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
