#!/usr/bin/env python3
"""
Создание таблицы employee_notification_settings если её не существует
"""
import sqlite3
import sys
from pathlib import Path

def create_notification_settings_table():
    """Создать таблицу employee_notification_settings"""

    db_path = Path(__file__).parent.parent / "business_card_bot.db"

    if not db_path.exists():
        print(f"❌ База данных не найдена: {db_path}")
        return False

    print(f"📊 Подключение к базе данных: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Проверяем существует ли таблица
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='employee_notification_settings'
        """)
        table_exists = cursor.fetchone() is not None

        if table_exists:
            print("ℹ️  Таблица employee_notification_settings уже существует")

            # Проверяем наличие всех необходимых колонок
            cursor.execute("PRAGMA table_info(employee_notification_settings)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            # Колонки которые должны быть
            required_columns = {
                'task_assigned', 'task_status_changed', 'task_deadline_reminder',
                'task_comment_added'
            }

            missing_columns = required_columns - existing_columns

            if missing_columns:
                print(f"⚠️  Отсутствуют колонки: {missing_columns}")
                for column in missing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE employee_notification_settings ADD COLUMN {column} BOOLEAN DEFAULT 1")
                        print(f"✅ Добавлена колонка: {column}")
                    except sqlite3.OperationalError as e:
                        print(f"❌ Ошибка при добавлении {column}: {e}")
                conn.commit()
            else:
                print("✅ Все необходимые колонки присутствуют")
        else:
            print("📝 Создание таблицы employee_notification_settings...")

            # SQL для создания таблицы
            create_table_sql = """
            CREATE TABLE employee_notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user_id INTEGER NOT NULL UNIQUE,
                telegram_user_id VARCHAR(50) NOT NULL,

                -- Основные настройки
                notifications_enabled BOOLEAN DEFAULT 1,
                notification_language VARCHAR(10) DEFAULT 'ru',

                -- Настройки для проектов
                project_assigned BOOLEAN DEFAULT 1,
                project_status_changed BOOLEAN DEFAULT 1,
                project_deadline_reminder BOOLEAN DEFAULT 1,
                project_overdue BOOLEAN DEFAULT 1,
                project_new_task BOOLEAN DEFAULT 1,

                -- Настройки для Avito и CRM
                avito_new_message BOOLEAN DEFAULT 1,
                avito_unread_reminder BOOLEAN DEFAULT 1,
                avito_urgent_message BOOLEAN DEFAULT 1,
                lead_assigned BOOLEAN DEFAULT 1,
                lead_status_changed BOOLEAN DEFAULT 1,
                deal_assigned BOOLEAN DEFAULT 1,
                deal_status_changed BOOLEAN DEFAULT 1,

                -- Настройки для задач
                task_assigned BOOLEAN DEFAULT 1,
                task_status_changed BOOLEAN DEFAULT 1,
                task_deadline_reminder BOOLEAN DEFAULT 1,
                task_comment_added BOOLEAN DEFAULT 1,

                -- Настройки для правок
                revision_new BOOLEAN DEFAULT 1,
                revision_status_changed BOOLEAN DEFAULT 1,
                revision_message_new BOOLEAN DEFAULT 1,

                -- Настройки для чатов
                project_chat_new_message BOOLEAN DEFAULT 1,

                -- Настройки времени
                work_hours_start VARCHAR(5) DEFAULT '09:00',
                work_hours_end VARCHAR(5) DEFAULT '18:00',
                weekend_notifications BOOLEAN DEFAULT 0,
                urgent_notifications_always BOOLEAN DEFAULT 1,

                -- Интервалы напоминаний
                avito_reminder_interval INTEGER DEFAULT 30,
                project_reminder_interval INTEGER DEFAULT 120,

                -- Системные поля
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (admin_user_id) REFERENCES admin_users (id)
            )
            """

            cursor.execute(create_table_sql)

            # Создаем индексы
            cursor.execute("CREATE INDEX idx_notification_settings_admin_user ON employee_notification_settings(admin_user_id)")
            cursor.execute("CREATE INDEX idx_notification_settings_telegram_user ON employee_notification_settings(telegram_user_id)")

            conn.commit()
            print("✅ Таблица employee_notification_settings успешно создана")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_notification_settings_table()
    sys.exit(0 if success else 1)
