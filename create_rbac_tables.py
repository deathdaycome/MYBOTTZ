#!/usr/bin/env python3
"""
Создание таблиц RBAC системы и инициализация базовых данных
"""

import sqlite3
import os
import sys
from datetime import datetime
import json

def get_database_path():
    """Найти путь к базе данных"""
    possible_paths = [
        "app.db",
        "data/app.db",
        "business_card_bot.db",
        "data/business_card_bot.db",
        "/var/www/bot_business_card/app.db",
        "/var/www/bot_business_card/business_card_bot.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return "app.db"  # Создаст новую если не найдена

def main():
    """Создать таблицы RBAC и наполнить базовыми данными"""
    print("🔐 Создание системы управления правами доступа (RBAC)...")
    print("=" * 60)
    
    db_path = get_database_path()
    print(f"📁 База данных: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📊 Создание таблиц RBAC...")
        
        # Таблица ролей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(200) NOT NULL,
                description TEXT,
                level INTEGER DEFAULT 0,
                is_system BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                max_projects INTEGER,
                max_clients INTEGER,
                max_deals INTEGER,
                modules_access TEXT DEFAULT '{}',
                dashboard_widgets TEXT DEFAULT '[]',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Таблица roles создана")
        
        # Таблица разрешений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(200) NOT NULL,
                description TEXT,
                module VARCHAR(50) NOT NULL,
                action VARCHAR(50) NOT NULL,
                conditions TEXT,
                is_system BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Таблица permissions создана")
        
        # Таблица связей роли-разрешения
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INTEGER,
                permission_id INTEGER,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица role_permissions создана")
        
        # Таблица связей пользователь-роли
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER,
                role_id INTEGER,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица user_roles создана")
        
        # Таблица дополнительных прав пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                user_id INTEGER,
                permission_id INTEGER,
                PRIMARY KEY (user_id, permission_id),
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица user_permissions создана")
        
        # Таблица правил доступа к данным
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_access_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER,
                user_id INTEGER,
                entity_type VARCHAR(50) NOT NULL,
                access_type VARCHAR(20) NOT NULL,
                conditions TEXT,
                specific_ids TEXT,
                can_view BOOLEAN DEFAULT 1,
                can_edit BOOLEAN DEFAULT 0,
                can_delete BOOLEAN DEFAULT 0,
                can_export BOOLEAN DEFAULT 0,
                priority INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица data_access_rules создана")
        
        # Таблица команд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                leader_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (leader_id) REFERENCES admin_users (id)
            )
        ''')
        print("✅ Таблица teams создана")
        
        # Таблица членства в командах
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_memberships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                team_role VARCHAR(50) DEFAULT 'member',
                can_see_team_data BOOLEAN DEFAULT 1,
                can_edit_team_data BOOLEAN DEFAULT 0,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица team_memberships создана")
        
        print("\n🗃️ Создание базовых данных...")
        
        # Создаем базовые роли
        roles_data = [
            ('owner', 'Владелец', 'Полный доступ ко всем функциям системы', 100, 1, 1),
            ('salesperson', 'Продажник', 'Работа с клиентами, лидами и сделками', 30, 0, 1),
            ('executor', 'Исполнитель', 'Работа с проектами и документами', 20, 0, 1)
        ]
        
        for role_name, display_name, description, level, is_system, is_active in roles_data:
            cursor.execute('''
                INSERT OR IGNORE INTO roles (name, display_name, description, level, is_system, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (role_name, display_name, description, level, is_system, is_active))
            print(f"✅ Роль '{display_name}' создана")
        
        # Создаем базовые разрешения
        permissions_data = [
            # Дашборд
            ('dashboard.view', 'Просмотр дашборда', 'dashboard', 'view'),
            ('dashboard.widgets.manage', 'Управление виджетами', 'dashboard', 'widgets.manage'),
            
            # Проекты
            ('projects.view', 'Просмотр проектов', 'projects', 'view'),
            ('projects.create', 'Создание проектов', 'projects', 'create'),
            ('projects.edit', 'Редактирование проектов', 'projects', 'edit'),
            ('projects.delete', 'Удаление проектов', 'projects', 'delete'),
            ('projects.export', 'Экспорт проектов', 'projects', 'export'),
            ('projects.assign', 'Назначение проектов', 'projects', 'assign'),
            
            # Клиенты
            ('clients.view', 'Просмотр клиентов', 'clients', 'view'),
            ('clients.create', 'Создание клиентов', 'clients', 'create'),
            ('clients.edit', 'Редактирование клиентов', 'clients', 'edit'),
            ('clients.delete', 'Удаление клиентов', 'clients', 'delete'),
            ('clients.export', 'Экспорт клиентов', 'clients', 'export'),
            ('clients.contact', 'Контакт с клиентами', 'clients', 'contact'),
            
            # Лиды
            ('leads.view', 'Просмотр лидов', 'leads', 'view'),
            ('leads.create', 'Создание лидов', 'leads', 'create'),
            ('leads.edit', 'Редактирование лидов', 'leads', 'edit'),
            ('leads.delete', 'Удаление лидов', 'leads', 'delete'),
            ('leads.export', 'Экспорт лидов', 'leads', 'export'),
            ('leads.convert', 'Конвертация лидов', 'leads', 'convert'),
            
            # Сделки
            ('deals.view', 'Просмотр сделок', 'deals', 'view'),
            ('deals.create', 'Создание сделок', 'deals', 'create'),
            ('deals.edit', 'Редактирование сделок', 'deals', 'edit'),
            ('deals.delete', 'Удаление сделок', 'deals', 'delete'),
            ('deals.export', 'Экспорт сделок', 'deals', 'export'),
            ('deals.close', 'Закрытие сделок', 'deals', 'close'),
            
            # Финансы
            ('finance.view', 'Просмотр финансов', 'finance', 'view'),
            ('finance.create', 'Создание транзакций', 'finance', 'create'),
            ('finance.edit', 'Редактирование транзакций', 'finance', 'edit'),
            ('finance.delete', 'Удаление транзакций', 'finance', 'delete'),
            ('finance.export', 'Экспорт финансов', 'finance', 'export'),
            ('finance.reports', 'Финансовые отчеты', 'finance', 'reports'),
            
            # Документы
            ('documents.view', 'Просмотр документов', 'documents', 'view'),
            ('documents.create', 'Создание документов', 'documents', 'create'),
            ('documents.edit', 'Редактирование документов', 'documents', 'edit'),
            ('documents.delete', 'Удаление документов', 'documents', 'delete'),
            ('documents.generate', 'Генерация документов', 'documents', 'generate'),
            ('documents.sign', 'Подпись документов', 'documents', 'sign'),
            
            # Отчеты
            ('reports.view', 'Просмотр отчетов', 'reports', 'view'),
            ('reports.create', 'Создание отчетов', 'reports', 'create'),
            ('reports.export', 'Экспорт отчетов', 'reports', 'export'),
            ('reports.schedule', 'Планирование отчетов', 'reports', 'schedule'),
            
            # Настройки
            ('settings.view', 'Просмотр настроек', 'settings', 'view'),
            ('settings.edit', 'Редактирование настроек', 'settings', 'edit'),
            ('settings.system.manage', 'Системные настройки', 'settings', 'system.manage'),
            
            # Пользователи
            ('users.view', 'Просмотр пользователей', 'users', 'view'),
            ('users.create', 'Создание пользователей', 'users', 'create'),
            ('users.edit', 'Редактирование пользователей', 'users', 'edit'),
            ('users.delete', 'Удаление пользователей', 'users', 'delete'),
            ('users.permissions.manage', 'Управление правами', 'users', 'permissions.manage'),
            
            # Avito
            ('avito.view', 'Просмотр Avito', 'avito', 'view'),
            ('avito.messages.send', 'Отправка сообщений', 'avito', 'messages.send'),
            ('avito.chats.manage', 'Управление чатами', 'avito', 'chats.manage'),
            ('avito.settings.edit', 'Настройки Avito', 'avito', 'settings.edit'),
        ]
        
        for perm_name, display_name, module, action in permissions_data:
            cursor.execute('''
                INSERT OR IGNORE INTO permissions (name, display_name, module, action)
                VALUES (?, ?, ?, ?)
            ''', (perm_name, display_name, module, action))
        
        print(f"✅ Создано {len(permissions_data)} базовых разрешений")
        
        # Назначаем все права владельцу
        cursor.execute('SELECT id FROM roles WHERE name = "owner"')
        owner_role = cursor.fetchone()
        
        if owner_role:
            cursor.execute('SELECT id FROM permissions')
            all_permissions = cursor.fetchall()
            
            for perm in all_permissions:
                cursor.execute('''
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                    VALUES (?, ?)
                ''', (owner_role[0], perm[0]))
            
            print(f"✅ Владельцу назначены все права ({len(all_permissions)} разрешений)")
        
        # Сохраняем изменения
        conn.commit()
        conn.close()
        
        print(f"\n✅ Система RBAC успешно создана!")
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🚀 Теперь вы можете:")
        print("  1. Зайти в админку как владелец")
        print("  2. Перейти в 'Управление правами'")
        print("  3. Настроить права для ваших исполнителей и продажников")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()