"""
Миграция: Добавление сущностей CRM (Lead, Deal) и доработка связей
Дата: 2025-12-07
"""

import sqlite3
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate(db_path='/app/data/bot.db'):
    """Применить миграцию для добавления CRM сущностей"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Начинаем миграцию CRM сущностей...")

        # ==============================
        # 1. Таблица Leads (Лиды)
        # ==============================
        print("📊 Создаём таблицу leads...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                budget_estimate FLOAT DEFAULT 0.0,
                source VARCHAR(100),
                status VARCHAR(50) DEFAULT 'NEW',
                manager_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (client_id) REFERENCES users (id) ON DELETE SET NULL,
                FOREIGN KEY (manager_id) REFERENCES admin_users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица leads создана")

        # ==============================
        # 2. Таблица Deals (Сделки)
        # ==============================
        print("📊 Создаём таблицу deals...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                client_id INTEGER NOT NULL,
                title VARCHAR(500) NOT NULL,
                product_type VARCHAR(50),
                amount FLOAT DEFAULT 0.0,
                currency VARCHAR(10) DEFAULT 'RUB',
                status VARCHAR(50) DEFAULT 'NEW',
                manager_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE SET NULL,
                FOREIGN KEY (client_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (manager_id) REFERENCES admin_users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица deals создана")

        # ==============================
        # 3. Доработка таблицы Tasks
        # ==============================
        print("📊 Добавляем поля в таблицу tasks...")

        # Проверяем существование колонок перед добавлением
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'type' not in columns:
            cursor.execute('ALTER TABLE tasks ADD COLUMN type VARCHAR(50) DEFAULT "TASK"')
            print("  ✅ Добавлено поле type")

        if 'project_id' not in columns:
            cursor.execute('ALTER TABLE tasks ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE')
            print("  ✅ Добавлено поле project_id")

        if 'executor_id' not in columns:
            cursor.execute('ALTER TABLE tasks ADD COLUMN executor_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL')
            print("  ✅ Добавлено поле executor_id (для совместимости)")

        if 'visible_to_client' not in columns:
            cursor.execute('ALTER TABLE tasks ADD COLUMN visible_to_client BOOLEAN DEFAULT FALSE')
            print("  ✅ Добавлено поле visible_to_client")

        # ==============================
        # 4. Таблица Payments (Платежи)
        # ==============================
        print("📊 Создаём таблицу payments...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                deal_id INTEGER,
                client_id INTEGER NOT NULL,
                type VARCHAR(50) DEFAULT 'PREPAYMENT',
                amount FLOAT NOT NULL DEFAULT 0.0,
                status VARCHAR(50) DEFAULT 'PLANNED',
                due_date DATETIME,
                paid_at DATETIME,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (deal_id) REFERENCES deals (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица payments создана")

        # ==============================
        # 5. Таблица Transcriptions
        # ==============================
        print("📊 Создаём таблицу transcriptions...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type VARCHAR(50) DEFAULT 'MIC_RECORD',
                file_path VARCHAR(1000),
                text TEXT,
                linked_lead_id INTEGER,
                linked_deal_id INTEGER,
                linked_project_id INTEGER,
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (linked_lead_id) REFERENCES leads (id) ON DELETE SET NULL,
                FOREIGN KEY (linked_deal_id) REFERENCES deals (id) ON DELETE SET NULL,
                FOREIGN KEY (linked_project_id) REFERENCES projects (id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES admin_users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица transcriptions создана")

        # ==============================
        # 6. Таблица AI Calls
        # ==============================
        print("📊 Создаём таблицу ai_calls...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                deal_id INTEGER,
                project_id INTEGER,
                dialog_text TEXT,
                ai_tips JSON,
                summary TEXT,
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE SET NULL,
                FOREIGN KEY (deal_id) REFERENCES deals (id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES admin_users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица ai_calls создана")

        # ==============================
        # 7. Доработка таблицы Projects
        # ==============================
        print("📊 Добавляем поля в таблицу projects...")

        cursor.execute("PRAGMA table_info(projects)")
        project_columns = [col[1] for col in cursor.fetchall()]

        if 'deal_id' not in project_columns:
            cursor.execute('ALTER TABLE projects ADD COLUMN deal_id INTEGER REFERENCES deals(id) ON DELETE SET NULL')
            print("  ✅ Добавлено поле deal_id")

        if 'stage' not in project_columns:
            cursor.execute('ALTER TABLE projects ADD COLUMN stage VARCHAR(100) DEFAULT "ТЗ"')
            print("  ✅ Добавлено поле stage")

        if 'teamlead_id' not in project_columns:
            cursor.execute('ALTER TABLE projects ADD COLUMN teamlead_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL')
            print("  ✅ Добавлено поле teamlead_id")

        if 'executor_id' not in project_columns:
            cursor.execute('ALTER TABLE projects ADD COLUMN executor_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL')
            print("  ✅ Добавлено поле executor_id (основной исполнитель)")

        if 'price_total' not in project_columns:
            # Используем estimated_cost как price_total
            cursor.execute('ALTER TABLE projects ADD COLUMN price_total FLOAT DEFAULT 0.0')
            cursor.execute('UPDATE projects SET price_total = estimated_cost WHERE price_total IS NULL')
            print("  ✅ Добавлено поле price_total")

        if 'price_executor' not in project_columns:
            # Используем executor_cost как price_executor
            cursor.execute('ALTER TABLE projects ADD COLUMN price_executor FLOAT DEFAULT 0.0')
            cursor.execute('UPDATE projects SET price_executor = executor_cost WHERE price_executor IS NULL')
            print("  ✅ Добавлено поле price_executor")

        # ==============================
        # 8. Доработка таблицы Messages
        # ==============================
        print("📊 Добавляем поля в таблицу messages...")

        cursor.execute("PRAGMA table_info(messages)")
        message_columns = [col[1] for col in cursor.fetchall()]

        if 'project_id' not in message_columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE')
            print("  ✅ Добавлено поле project_id")

        if 'task_id' not in message_columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE')
            print("  ✅ Добавлено поле task_id")

        if 'author_id' not in message_columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN author_id INTEGER')
            print("  ✅ Добавлено поле author_id")

        if 'visible_to_client' not in message_columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN visible_to_client BOOLEAN DEFAULT TRUE')
            print("  ✅ Добавлено поле visible_to_client")

        if 'attachments' not in message_columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN attachments JSON')
            print("  ✅ Добавлено поле attachments")

        # ==============================
        # 9. Создаём индексы для оптимизации
        # ==============================
        print("📊 Создаём индексы...")

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_client ON leads(client_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deals_client ON deals(client_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deals_lead ON deals(lead_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_project ON payments(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_deal ON payments(deal_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transcriptions_lead ON transcriptions(linked_lead_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transcriptions_deal ON transcriptions(linked_deal_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transcriptions_project ON transcriptions(linked_project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_calls_lead ON ai_calls(lead_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_calls_deal ON ai_calls(deal_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_calls_project ON ai_calls(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_project ON messages(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_task ON messages(task_id)')

        print("✅ Индексы созданы")

        conn.commit()
        print("✅ Миграция успешно применена!")

        # Показываем статистику
        cursor.execute("SELECT COUNT(*) FROM leads")
        leads_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM deals")
        deals_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM projects")
        projects_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks")
        tasks_count = cursor.fetchone()[0]

        print(f"\n📈 Статистика:")
        print(f"  • Лидов: {leads_count}")
        print(f"  • Сделок: {deals_count}")
        print(f"  • Проектов: {projects_count}")
        print(f"  • Задач: {tasks_count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка миграции: {e}")
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
