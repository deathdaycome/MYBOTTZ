#!/usr/bin/env python3
"""
Миграция для добавления таблиц CRM и системы ролей в БД
"""

import sqlite3
import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_crm_tables(conn):
    """Создание таблиц CRM"""
    cursor = conn.cursor()
    
    # Таблица клиентов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(300) NOT NULL,
        type VARCHAR(20) DEFAULT 'individual',
        status VARCHAR(20) DEFAULT 'new',
        phone VARCHAR(50),
        email VARCHAR(255),
        telegram VARCHAR(100),
        whatsapp VARCHAR(50),
        website VARCHAR(500),
        address TEXT,
        company_name VARCHAR(500),
        inn VARCHAR(20),
        kpp VARCHAR(20),
        ogrn VARCHAR(20),
        bank_details JSON,
        source VARCHAR(100),
        description TEXT,
        preferences JSON,
        communication_history JSON DEFAULT '[]',
        total_revenue REAL DEFAULT 0.0,
        average_check REAL DEFAULT 0.0,
        payment_terms VARCHAR(200),
        credit_limit REAL,
        rating INTEGER DEFAULT 0,
        segment VARCHAR(50),
        loyalty_level VARCHAR(50),
        manager_id INTEGER,
        telegram_user_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (manager_id) REFERENCES admin_users(id),
        FOREIGN KEY (telegram_user_id) REFERENCES users(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    )
    """)
    
    # Индексы для клиентов
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_inn ON clients(inn)")
    
    # Таблица лидов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        status VARCHAR(30) DEFAULT 'new',
        source VARCHAR(100),
        client_id INTEGER,
        contact_name VARCHAR(300),
        contact_phone VARCHAR(50),
        contact_email VARCHAR(255),
        contact_telegram VARCHAR(100),
        description TEXT,
        requirements TEXT,
        budget REAL,
        probability INTEGER DEFAULT 50,
        expected_close_date DATETIME,
        next_action_date DATETIME,
        interactions JSON DEFAULT '[]',
        notes TEXT,
        lost_reason VARCHAR(500),
        manager_id INTEGER,
        converted_to_deal_id INTEGER,
        converted_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (manager_id) REFERENCES admin_users(id),
        FOREIGN KEY (converted_to_deal_id) REFERENCES deals(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    )
    """)
    
    # Индексы для лидов
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_client ON leads(client_id)")
    
    # Таблица сделок
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        status VARCHAR(30) DEFAULT 'new',
        client_id INTEGER NOT NULL,
        description TEXT,
        technical_requirements JSON,
        amount REAL NOT NULL,
        cost REAL,
        margin REAL,
        discount REAL DEFAULT 0.0,
        prepayment_percent INTEGER DEFAULT 50,
        prepayment_amount REAL DEFAULT 0.0,
        paid_amount REAL DEFAULT 0.0,
        payment_schedule JSON,
        start_date DATETIME,
        end_date DATETIME,
        actual_start_date DATETIME,
        actual_end_date DATETIME,
        contract_number VARCHAR(100),
        contract_date DATETIME,
        contract_signed BOOLEAN DEFAULT 0,
        act_number VARCHAR(100),
        act_date DATETIME,
        project_id INTEGER,
        manager_id INTEGER,
        executor_id INTEGER,
        priority VARCHAR(20) DEFAULT 'normal',
        tags JSON DEFAULT '[]',
        custom_fields JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME,
        created_by_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (manager_id) REFERENCES admin_users(id),
        FOREIGN KEY (executor_id) REFERENCES admin_users(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    )
    """)
    
    # Индексы для сделок
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_client ON deals(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_contract ON deals(contract_number)")
    
    # Таблица документов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type VARCHAR(50) NOT NULL,
        name VARCHAR(500) NOT NULL,
        number VARCHAR(100),
        client_id INTEGER,
        deal_id INTEGER,
        project_id INTEGER,
        file_path VARCHAR(500),
        file_size INTEGER,
        file_type VARCHAR(50),
        template_id INTEGER,
        content JSON,
        generated_html TEXT,
        status VARCHAR(50) DEFAULT 'draft',
        date DATETIME,
        valid_until DATETIME,
        signed_at DATETIME,
        description TEXT,
        tags JSON DEFAULT '[]',
        metadata JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (deal_id) REFERENCES deals(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (template_id) REFERENCES document_templates(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    )
    """)
    
    # Индексы для документов
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_number ON documents(number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_client ON documents(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_deal ON documents(deal_id)")
    
    # Таблица шаблонов документов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(300) NOT NULL,
        type VARCHAR(50) NOT NULL,
        description TEXT,
        template_html TEXT NOT NULL,
        variables JSON NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_default BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    )
    """)
    
    # Таблица тегов клиентов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_tag (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        color VARCHAR(20),
        description TEXT
    )
    """)
    
    # Таблица связи клиентов и тегов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_tags (
        client_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (client_id, tag_id),
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (tag_id) REFERENCES client_tag(id)
    )
    """)
    
    # Таблица каталога услуг
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS service_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(300) NOT NULL,
        category VARCHAR(100) NOT NULL,
        description TEXT,
        base_price REAL NOT NULL,
        min_price REAL,
        max_price REAL,
        estimated_hours INTEGER,
        estimated_days INTEGER,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        tags JSON DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Таблица связи сделок и услуг
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deal_services (
        deal_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        PRIMARY KEY (deal_id, service_id),
        FOREIGN KEY (deal_id) REFERENCES deals(id),
        FOREIGN KEY (service_id) REFERENCES service_catalog(id)
    )
    """)
    
    # Таблица аудит-логов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action VARCHAR(100) NOT NULL,
        entity_type VARCHAR(50) NOT NULL,
        entity_id INTEGER,
        old_data JSON,
        new_data JSON,
        changes JSON,
        description TEXT,
        ip_address VARCHAR(50),
        user_agent VARCHAR(500),
        request_id VARCHAR(100),
        user_id INTEGER,
        user_name VARCHAR(200),
        user_role VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES admin_users(id)
    )
    """)
    
    # Индексы для аудит-логов
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at)")
    
    print("✅ Таблицы CRM созданы успешно")


def create_rbac_tables(conn):
    """Создание таблиц для системы ролей и прав"""
    cursor = conn.cursor()
    
    # Таблица ролей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        display_name VARCHAR(200) NOT NULL,
        description TEXT,
        level INTEGER DEFAULT 0,
        is_system BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        max_projects INTEGER,
        max_clients INTEGER,
        max_deals INTEGER,
        modules_access JSON DEFAULT '{}',
        dashboard_widgets JSON DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Индекс для ролей
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name)")
    
    # Таблица разрешений
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        display_name VARCHAR(200) NOT NULL,
        description TEXT,
        module VARCHAR(50) NOT NULL,
        action VARCHAR(50) NOT NULL,
        conditions JSON,
        is_system BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Индексы для разрешений
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_permissions_module ON permissions(module)")
    
    # Таблица связи ролей и разрешений
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        role_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (role_id, permission_id),
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (permission_id) REFERENCES permissions(id)
    )
    """)
    
    # Таблица связи пользователей и ролей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_roles (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES admin_users(id),
        FOREIGN KEY (role_id) REFERENCES roles(id)
    )
    """)
    
    # Таблица связи пользователей и дополнительных разрешений
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_permissions (
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, permission_id),
        FOREIGN KEY (user_id) REFERENCES admin_users(id),
        FOREIGN KEY (permission_id) REFERENCES permissions(id)
    )
    """)
    
    # Таблица правил доступа к данным
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_access_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id INTEGER,
        user_id INTEGER,
        entity_type VARCHAR(50) NOT NULL,
        access_type VARCHAR(20) NOT NULL,
        conditions JSON,
        specific_ids JSON,
        can_view BOOLEAN DEFAULT 1,
        can_edit BOOLEAN DEFAULT 0,
        can_delete BOOLEAN DEFAULT 0,
        can_export BOOLEAN DEFAULT 0,
        priority INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (user_id) REFERENCES admin_users(id)
    )
    """)
    
    # Таблица команд
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        leader_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (leader_id) REFERENCES admin_users(id)
    )
    """)
    
    # Таблица членства в командах
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        team_role VARCHAR(50) DEFAULT 'member',
        can_see_team_data BOOLEAN DEFAULT 1,
        can_edit_team_data BOOLEAN DEFAULT 0,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES admin_users(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )
    """)
    
    print("✅ Таблицы RBAC созданы успешно")


def add_admin_user_rbac_columns(conn):
    """Добавление новых колонок в таблицу admin_users для RBAC"""
    cursor = conn.cursor()
    
    # Список новых колонок для admin_users
    columns_to_add = [
        ('last_login', 'DATETIME'),
        ('login_count', 'INTEGER DEFAULT 0'),
        ('failed_login_count', 'INTEGER DEFAULT 0'),
        ('last_failed_login', 'DATETIME'),
        ('is_locked', 'BOOLEAN DEFAULT 0'),
        ('locked_until', 'DATETIME'),
        ('password_changed_at', 'DATETIME'),
        ('must_change_password', 'BOOLEAN DEFAULT 0'),
        ('session_token', 'VARCHAR(500)'),
        ('session_expires_at', 'DATETIME'),
        ('preferences', 'JSON DEFAULT \'{}\''),
    ]
    
    # Проверяем и добавляем колонки
    for column_name, column_type in columns_to_add:
        try:
            # Проверяем существование колонки
            cursor.execute(f"SELECT {column_name} FROM admin_users LIMIT 1")
        except sqlite3.OperationalError:
            # Колонка не существует, добавляем
            cursor.execute(f"ALTER TABLE admin_users ADD COLUMN {column_name} {column_type}")
            print(f"  ✅ Добавлена колонка {column_name} в admin_users")


def insert_default_roles_and_permissions(conn):
    """Вставка стандартных ролей и разрешений"""
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже роли
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] > 0:
        print("ℹ️  Роли уже существуют, пропускаем создание стандартных ролей")
        return
    
    # Создаем стандартные роли
    roles = [
        ('owner', 'Владелец', 'Полный доступ ко всем функциям системы', 100, 1, None, None, None),
        ('admin', 'Администратор', 'Административный доступ с ограничениями', 90, 1, None, None, None),
        ('manager', 'Менеджер', 'Управление клиентами и сделками', 50, 1, None, 100, 50),
        ('executor', 'Исполнитель', 'Работа с назначенными проектами', 30, 1, 20, None, None),
        ('accountant', 'Бухгалтер', 'Доступ к финансовым данным', 40, 1, None, None, None),
        ('observer', 'Наблюдатель', 'Только просмотр данных', 10, 1, None, None, None),
    ]
    
    for role_data in roles:
        cursor.execute("""
            INSERT INTO roles (name, display_name, description, level, is_system, max_projects, max_clients, max_deals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, role_data)
    
    print("✅ Стандартные роли созданы")
    
    # Создаем стандартные разрешения
    permissions = [
        # Проекты
        ('projects.view', 'Просмотр проектов', 'Просмотр списка и деталей проектов', 'projects', 'view'),
        ('projects.create', 'Создание проектов', 'Создание новых проектов', 'projects', 'create'),
        ('projects.edit', 'Редактирование проектов', 'Изменение данных проектов', 'projects', 'edit'),
        ('projects.delete', 'Удаление проектов', 'Удаление проектов', 'projects', 'delete'),
        ('projects.export', 'Экспорт проектов', 'Экспорт данных проектов', 'projects', 'export'),
        
        # Клиенты
        ('clients.view', 'Просмотр клиентов', 'Просмотр списка и деталей клиентов', 'clients', 'view'),
        ('clients.create', 'Создание клиентов', 'Создание новых клиентов', 'clients', 'create'),
        ('clients.edit', 'Редактирование клиентов', 'Изменение данных клиентов', 'clients', 'edit'),
        ('clients.delete', 'Удаление клиентов', 'Удаление клиентов', 'clients', 'delete'),
        ('clients.export', 'Экспорт клиентов', 'Экспорт данных клиентов', 'clients', 'export'),
        
        # Лиды
        ('leads.view', 'Просмотр лидов', 'Просмотр списка и деталей лидов', 'leads', 'view'),
        ('leads.create', 'Создание лидов', 'Создание новых лидов', 'leads', 'create'),
        ('leads.edit', 'Редактирование лидов', 'Изменение данных лидов', 'leads', 'edit'),
        ('leads.delete', 'Удаление лидов', 'Удаление лидов', 'leads', 'delete'),
        ('leads.convert', 'Конвертация лидов', 'Конвертация лидов в сделки', 'leads', 'convert'),
        
        # Сделки
        ('deals.view', 'Просмотр сделок', 'Просмотр списка и деталей сделок', 'deals', 'view'),
        ('deals.create', 'Создание сделок', 'Создание новых сделок', 'deals', 'create'),
        ('deals.edit', 'Редактирование сделок', 'Изменение данных сделок', 'deals', 'edit'),
        ('deals.delete', 'Удаление сделок', 'Удаление сделок', 'deals', 'delete'),
        ('deals.export', 'Экспорт сделок', 'Экспорт данных сделок', 'deals', 'export'),
        
        # Финансы
        ('finance.view', 'Просмотр финансов', 'Просмотр финансовых данных', 'finance', 'view'),
        ('finance.create', 'Создание транзакций', 'Создание финансовых транзакций', 'finance', 'create'),
        ('finance.edit', 'Редактирование финансов', 'Изменение финансовых данных', 'finance', 'edit'),
        ('finance.delete', 'Удаление транзакций', 'Удаление финансовых транзакций', 'finance', 'delete'),
        ('finance.export', 'Экспорт финансов', 'Экспорт финансовых отчетов', 'finance', 'export'),
        
        # Документы
        ('documents.view', 'Просмотр документов', 'Просмотр документов', 'documents', 'view'),
        ('documents.create', 'Создание документов', 'Создание новых документов', 'documents', 'create'),
        ('documents.edit', 'Редактирование документов', 'Изменение документов', 'documents', 'edit'),
        ('documents.delete', 'Удаление документов', 'Удаление документов', 'documents', 'delete'),
        ('documents.sign', 'Подписание документов', 'Право подписи документов', 'documents', 'sign'),
        
        # Отчеты
        ('reports.view', 'Просмотр отчетов', 'Просмотр отчетов и аналитики', 'reports', 'view'),
        ('reports.export', 'Экспорт отчетов', 'Экспорт отчетов', 'reports', 'export'),
        
        # Настройки
        ('settings.view', 'Просмотр настроек', 'Просмотр настроек системы', 'settings', 'view'),
        ('settings.edit', 'Изменение настроек', 'Изменение настроек системы', 'settings', 'edit'),
        
        # Пользователи
        ('users.view', 'Просмотр пользователей', 'Просмотр списка пользователей', 'users', 'view'),
        ('users.create', 'Создание пользователей', 'Создание новых пользователей', 'users', 'create'),
        ('users.edit', 'Редактирование пользователей', 'Изменение данных пользователей', 'users', 'edit'),
        ('users.delete', 'Удаление пользователей', 'Удаление пользователей', 'users', 'delete'),
        ('users.roles', 'Управление ролями', 'Назначение ролей пользователям', 'users', 'roles'),
    ]
    
    for perm_data in permissions:
        cursor.execute("""
            INSERT INTO permissions (name, display_name, description, module, action, is_system)
            VALUES (?, ?, ?, ?, ?, 1)
        """, perm_data)
    
    print("✅ Стандартные разрешения созданы")
    
    # Назначаем разрешения ролям
    cursor.execute("SELECT id FROM roles WHERE name = 'owner'")
    owner_role_id = cursor.fetchone()[0]
    
    # Владелец получает все разрешения
    cursor.execute("SELECT id FROM permissions")
    all_permissions = cursor.fetchall()
    for perm_id in all_permissions:
        cursor.execute("""
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (?, ?)
        """, (owner_role_id, perm_id[0]))
    
    print("✅ Разрешения назначены ролям")


def migrate_existing_data(conn):
    """Миграция существующих данных"""
    cursor = conn.cursor()
    
    # Получаем роль owner
    cursor.execute("SELECT id FROM roles WHERE name = 'owner'")
    owner_role = cursor.fetchone()
    if not owner_role:
        print("⚠️  Роль owner не найдена, пропускаем миграцию пользователей")
        return
    
    owner_role_id = owner_role[0]
    
    # Назначаем существующим админам роль в зависимости от их текущей роли
    cursor.execute("SELECT id, role FROM admin_users")
    admin_users = cursor.fetchall()
    
    for user_id, current_role in admin_users:
        # Определяем новую роль на основе старой
        if current_role == 'owner':
            new_role_name = 'owner'
        elif current_role == 'admin':
            new_role_name = 'admin'
        elif current_role == 'executor':
            new_role_name = 'executor'
        else:
            new_role_name = 'manager'
        
        # Получаем ID новой роли
        cursor.execute("SELECT id FROM roles WHERE name = ?", (new_role_name,))
        role = cursor.fetchone()
        if role:
            # Проверяем, не назначена ли уже роль
            cursor.execute("""
                SELECT COUNT(*) FROM user_roles 
                WHERE user_id = ? AND role_id = ?
            """, (user_id, role[0]))
            
            if cursor.fetchone()[0] == 0:
                # Назначаем роль пользователю
                cursor.execute("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (?, ?)
                """, (user_id, role[0]))
                print(f"  ✅ Пользователю {user_id} назначена роль {new_role_name}")
    
    print("✅ Миграция существующих данных завершена")


def main():
    """Основная функция миграции"""
    # Пути к базам данных
    db_paths = [
        'data/bot.db',
        'portfolio.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n📂 Обработка базы данных: {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Создаем таблицы CRM
                create_crm_tables(conn)
                
                # Создаем таблицы RBAC
                create_rbac_tables(conn)
                
                # Добавляем колонки в admin_users
                add_admin_user_rbac_columns(conn)
                
                # Вставляем стандартные роли и разрешения
                insert_default_roles_and_permissions(conn)
                
                # Мигрируем существующие данные
                migrate_existing_data(conn)
                
                conn.commit()
                conn.close()
                
                print(f"✅ База данных {db_path} успешно обновлена")
                
            except Exception as e:
                print(f"❌ Ошибка при обновлении {db_path}: {str(e)}")
                if conn:
                    conn.rollback()
                    conn.close()
        else:
            print(f"⚠️  База данных {db_path} не найдена, пропускаем")
    
    print("\n✅ Миграция завершена!")


if __name__ == "__main__":
    main()