"""
Миграция: Объединение Revisions и Tasks в одну таблицу
Дата: 2025-12-07
Описание: Переносит данные из project_revisions в tasks с type='REVISION'
"""

import sqlite3
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate(db_path='/app/data/bot.db'):
    """Применить миграцию для объединения revisions и tasks"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Начинаем миграцию: объединение Revisions и Tasks...")

        # Получаем все правки из project_revisions
        cursor.execute("SELECT COUNT(*) FROM project_revisions")
        total_revisions = cursor.fetchone()[0]
        print(f"  📊 Найдено правок в project_revisions: {total_revisions}")

        if total_revisions == 0:
            print("  ℹ️  Нет правок для переноса")
            conn.commit()
            return

        # Переносим данные из project_revisions в tasks
        cursor.execute("""
            INSERT INTO tasks (
                title,
                description,
                status,
                priority,
                assigned_to_id,
                created_by_id,
                deadline,
                estimated_hours,
                actual_hours,
                created_at,
                updated_at,
                completed_at,
                progress,
                time_spent_seconds,
                timer_started_at,
                type,
                project_id
            )
            SELECT
                title,
                description,
                COALESCE(status, 'pending') as status,
                COALESCE(priority, 'normal') as priority,
                COALESCE(assigned_to_id, created_by_id) as assigned_to_id,
                created_by_id,
                NULL as deadline,
                COALESCE(estimated_time, 0) as estimated_hours,
                COALESCE(actual_time, 0) as actual_hours,
                COALESCE(created_at, CURRENT_TIMESTAMP) as created_at,
                COALESCE(updated_at, CURRENT_TIMESTAMP) as updated_at,
                completed_at,
                COALESCE(progress, 0) as progress,
                COALESCE(time_spent_seconds, 0) as time_spent_seconds,
                timer_started_at,
                'REVISION' as type,
                project_id
            FROM project_revisions
            WHERE id NOT IN (
                SELECT id FROM tasks WHERE type = 'REVISION'
            )
        """)

        migrated_count = cursor.rowcount
        print(f"  ✅ Перенесено правок: {migrated_count}")

        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE type = 'REVISION'")
        revisions_in_tasks = cursor.fetchone()[0]
        print(f"  📊 Всего правок в tasks (type='REVISION'): {revisions_in_tasks}")

        conn.commit()
        print("✅ Миграция успешно применена!")

        print("\n📝 Информация:")
        print(f"  • Таблица project_revisions сохранена для обратной совместимости")
        print(f"  • Теперь используйте tasks с type='REVISION' для работы с правками")
        print(f"  • Все новые правки создавайте в tasks с type='REVISION'")

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
