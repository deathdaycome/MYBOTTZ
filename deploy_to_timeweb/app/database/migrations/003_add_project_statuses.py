"""
Миграция: Добавление системы статусов для проектов
Дата: 2025-07-08
"""

from sqlalchemy import text
from app.database.database import engine

def run_migration():
    """Выполняет миграцию для добавления системы статусов"""
    
    # SQL для создания таблицы статусов
    create_statuses_table = """
    CREATE TABLE IF NOT EXISTS project_statuses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        color VARCHAR(7) DEFAULT '#6c757d',
        icon VARCHAR(50) DEFAULT 'fas fa-circle',
        is_default BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    )
    """
    
    # SQL для создания таблицы логов статусов
    create_status_logs_table = """
    CREATE TABLE IF NOT EXISTS project_status_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        status_id INTEGER NOT NULL,
        previous_status_id INTEGER,
        comment TEXT,
        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        changed_by_id INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (status_id) REFERENCES project_statuses(id),
        FOREIGN KEY (previous_status_id) REFERENCES project_statuses(id),
        FOREIGN KEY (changed_by_id) REFERENCES admin_users(id)
    )
    """
    
    # SQL для добавления поля current_status_id в таблицу projects
    add_current_status_field = """
    ALTER TABLE projects ADD COLUMN current_status_id INTEGER 
    REFERENCES project_statuses(id)
    """
    
    # Дефолтные статусы
    default_statuses = [
        ("Новый", "Проект только что создан", "#6c757d", "fas fa-plus-circle", 1, 1, 10),
        ("В ожидании", "Ожидает рассмотрения", "#ffc107", "fas fa-clock", 1, 1, 20),
        ("Принят", "Проект принят в работу", "#17a2b8", "fas fa-check-circle", 1, 1, 30),
        ("В разработке", "Идет активная разработка", "#007bff", "fas fa-code", 1, 1, 40),
        ("Тестирование", "Проект в процессе тестирования", "#fd7e14", "fas fa-flask", 1, 1, 50),
        ("Завершен", "Проект успешно завершен", "#28a745", "fas fa-check", 1, 1, 60),
        ("Отменен", "Проект отменен", "#dc3545", "fas fa-times", 1, 1, 70),
        ("Приостановлен", "Работа временно приостановлена", "#6f42c1", "fas fa-pause", 1, 1, 80)
    ]
    
    try:
        with engine.connect() as connection:
            # Создаем таблицы
            connection.execute(text(create_statuses_table))
            print("✅ Таблица project_statuses создана")
            
            connection.execute(text(create_status_logs_table))
            print("✅ Таблица project_status_logs создана")
            
            # Добавляем поле current_status_id в projects
            try:
                connection.execute(text(add_current_status_field))
                print("✅ Поле current_status_id добавлено в таблицу projects")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("⚠️ Поле current_status_id уже существует в таблице projects")
                else:
                    raise
            
            # Добавляем дефолтные статусы
            for name, description, color, icon, is_default, is_active, sort_order in default_statuses:
                insert_status = """
                INSERT OR IGNORE INTO project_statuses 
                (name, description, color, icon, is_default, is_active, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                connection.execute(text(insert_status), (name, description, color, icon, is_default, is_active, sort_order))
            
            print("✅ Дефолтные статусы добавлены")
            
            # Обновляем существующие проекты, устанавливая статус "Новый" для тех, у кого нет статуса
            update_projects = """
            UPDATE projects 
            SET current_status_id = (
                SELECT id FROM project_statuses WHERE name = 'Новый' LIMIT 1
            )
            WHERE current_status_id IS NULL
            """
            connection.execute(text(update_projects))
            print("✅ Существующие проекты обновлены")
            
            connection.commit()
            print("🎉 Миграция успешно выполнена!")
            
    except Exception as e:
        print(f"❌ Ошибка выполнения миграции: {e}")
        raise

if __name__ == "__main__":
    run_migration()
