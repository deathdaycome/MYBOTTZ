"""
Миграция: Добавление системы ролей и пользователей админ-панели
"""

from sqlalchemy import text

def upgrade(engine):
    """Применить миграцию"""
    with engine.connect() as conn:
        # Создание таблицы admin_users
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                role VARCHAR(50) NOT NULL DEFAULT 'executor',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """))
        
        # Создание таблицы project_files
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_files (
                id INTEGER PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                file_type VARCHAR(100) NOT NULL,
                description TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                project_id INTEGER NOT NULL,
                uploaded_by_id INTEGER NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (uploaded_by_id) REFERENCES admin_users (id)
            )
        """))
        
        # Добавление новых полей в таблицу projects
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN executor_cost REAL"))
        except:
            pass  # Поле уже существует
            
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN assigned_executor_id INTEGER"))
        except:
            pass  # Поле уже существует
            
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN assigned_at TIMESTAMP"))
        except:
            pass  # Поле уже существует
        
        # Создание пользователя-владельца по умолчанию
        conn.execute(text("""
            INSERT OR IGNORE INTO admin_users (username, password_hash, role, first_name, is_active)
            VALUES ('admin', 'cb872de2c8e7435bad0db5ce42b95b6e0ee8d27a8b1e0b9e10f5c1d9c8c4c8b6', 'owner', 'Администратор', 1)
        """))
        
        conn.commit()

def downgrade(engine):
    """Откатить миграцию"""
    with engine.connect() as conn:
        # Удаление новых полей из projects
        try:
            conn.execute(text("ALTER TABLE projects DROP COLUMN executor_cost"))
            conn.execute(text("ALTER TABLE projects DROP COLUMN assigned_executor_id"))
            conn.execute(text("ALTER TABLE projects DROP COLUMN assigned_at"))
        except:
            pass
        
        # Удаление таблиц
        conn.execute(text("DROP TABLE IF EXISTS project_files"))
        conn.execute(text("DROP TABLE IF EXISTS admin_users"))
        
        conn.commit()
