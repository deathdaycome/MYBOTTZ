PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE roles (
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
            );
INSERT INTO roles VALUES(1,'owner','Владелец','Полный доступ ко всем функциям системы',100,1,1,NULL,NULL,NULL,'{}','[]','2025-10-17 17:11:43','2025-10-17 17:11:43');
INSERT INTO roles VALUES(2,'salesperson','Продажник','Работа с клиентами, лидами и сделками',30,0,1,NULL,NULL,NULL,'{}','[]','2025-10-17 17:11:43','2025-10-17 17:11:43');
INSERT INTO roles VALUES(3,'executor','Исполнитель','Работа с проектами и документами',20,0,1,NULL,NULL,NULL,'{}','[]','2025-10-17 17:11:43','2025-10-17 17:11:43');
CREATE TABLE permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(200) NOT NULL,
                description TEXT,
                module VARCHAR(50) NOT NULL,
                action VARCHAR(50) NOT NULL,
                conditions TEXT,
                is_system BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO permissions VALUES(1,'dashboard.view','Просмотр дашборда',NULL,'dashboard','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(2,'dashboard.widgets.manage','Управление виджетами',NULL,'dashboard','widgets.manage',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(3,'projects.view','Просмотр проектов',NULL,'projects','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(4,'projects.create','Создание проектов',NULL,'projects','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(5,'projects.edit','Редактирование проектов',NULL,'projects','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(6,'projects.delete','Удаление проектов',NULL,'projects','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(7,'projects.export','Экспорт проектов',NULL,'projects','export',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(8,'projects.assign','Назначение проектов',NULL,'projects','assign',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(9,'clients.view','Просмотр клиентов',NULL,'clients','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(10,'clients.create','Создание клиентов',NULL,'clients','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(11,'clients.edit','Редактирование клиентов',NULL,'clients','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(12,'clients.delete','Удаление клиентов',NULL,'clients','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(13,'clients.export','Экспорт клиентов',NULL,'clients','export',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(14,'clients.contact','Контакт с клиентами',NULL,'clients','contact',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(15,'leads.view','Просмотр лидов',NULL,'leads','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(16,'leads.create','Создание лидов',NULL,'leads','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(17,'leads.edit','Редактирование лидов',NULL,'leads','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(18,'leads.delete','Удаление лидов',NULL,'leads','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(19,'leads.export','Экспорт лидов',NULL,'leads','export',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(20,'leads.convert','Конвертация лидов',NULL,'leads','convert',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(21,'deals.view','Просмотр сделок',NULL,'deals','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(22,'deals.create','Создание сделок',NULL,'deals','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(23,'deals.edit','Редактирование сделок',NULL,'deals','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(24,'deals.delete','Удаление сделок',NULL,'deals','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(25,'deals.export','Экспорт сделок',NULL,'deals','export',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(26,'deals.close','Закрытие сделок',NULL,'deals','close',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(27,'finance.view','Просмотр финансов',NULL,'finance','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(28,'finance.create','Создание транзакций',NULL,'finance','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(29,'finance.edit','Редактирование транзакций',NULL,'finance','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(30,'finance.delete','Удаление транзакций',NULL,'finance','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(31,'finance.export','Экспорт финансов',NULL,'finance','export',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(32,'finance.reports','Финансовые отчеты',NULL,'finance','reports',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(33,'documents.view','Просмотр документов',NULL,'documents','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(34,'documents.create','Создание документов',NULL,'documents','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(35,'documents.edit','Редактирование документов',NULL,'documents','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(36,'documents.delete','Удаление документов',NULL,'documents','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(37,'documents.generate','Генерация документов',NULL,'documents','generate',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(38,'documents.sign','Подпись документов',NULL,'documents','sign',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(39,'reports.view','Просмотр отчетов',NULL,'reports','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(40,'reports.create','Создание отчетов',NULL,'reports','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(41,'reports.export','Экспорт отчетов',NULL,'reports','export',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(42,'reports.schedule','Планирование отчетов',NULL,'reports','schedule',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(43,'settings.view','Просмотр настроек',NULL,'settings','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(44,'settings.edit','Редактирование настроек',NULL,'settings','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(45,'settings.system.manage','Системные настройки',NULL,'settings','system.manage',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(46,'users.view','Просмотр пользователей',NULL,'users','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(47,'users.create','Создание пользователей',NULL,'users','create',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(48,'users.edit','Редактирование пользователей',NULL,'users','edit',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(49,'users.delete','Удаление пользователей',NULL,'users','delete',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(50,'users.permissions.manage','Управление правами',NULL,'users','permissions.manage',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(51,'avito.view','Просмотр Avito',NULL,'avito','view',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(52,'avito.messages.send','Отправка сообщений',NULL,'avito','messages.send',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(53,'avito.chats.manage','Управление чатами',NULL,'avito','chats.manage',NULL,0,'2025-10-17 17:11:43');
INSERT INTO permissions VALUES(54,'avito.settings.edit','Настройки Avito',NULL,'avito','settings.edit',NULL,0,'2025-10-17 17:11:43');
CREATE TABLE role_permissions (
                role_id INTEGER,
                permission_id INTEGER,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
            );
INSERT INTO role_permissions VALUES(1,53);
INSERT INTO role_permissions VALUES(1,52);
INSERT INTO role_permissions VALUES(1,54);
INSERT INTO role_permissions VALUES(1,51);
INSERT INTO role_permissions VALUES(1,14);
INSERT INTO role_permissions VALUES(1,10);
INSERT INTO role_permissions VALUES(1,12);
INSERT INTO role_permissions VALUES(1,11);
INSERT INTO role_permissions VALUES(1,13);
INSERT INTO role_permissions VALUES(1,9);
INSERT INTO role_permissions VALUES(1,1);
INSERT INTO role_permissions VALUES(1,2);
INSERT INTO role_permissions VALUES(1,26);
INSERT INTO role_permissions VALUES(1,22);
INSERT INTO role_permissions VALUES(1,24);
INSERT INTO role_permissions VALUES(1,23);
INSERT INTO role_permissions VALUES(1,25);
INSERT INTO role_permissions VALUES(1,21);
INSERT INTO role_permissions VALUES(1,34);
INSERT INTO role_permissions VALUES(1,36);
INSERT INTO role_permissions VALUES(1,35);
INSERT INTO role_permissions VALUES(1,37);
INSERT INTO role_permissions VALUES(1,38);
INSERT INTO role_permissions VALUES(1,33);
INSERT INTO role_permissions VALUES(1,28);
INSERT INTO role_permissions VALUES(1,30);
INSERT INTO role_permissions VALUES(1,29);
INSERT INTO role_permissions VALUES(1,31);
INSERT INTO role_permissions VALUES(1,32);
INSERT INTO role_permissions VALUES(1,27);
INSERT INTO role_permissions VALUES(1,20);
INSERT INTO role_permissions VALUES(1,16);
INSERT INTO role_permissions VALUES(1,18);
INSERT INTO role_permissions VALUES(1,17);
INSERT INTO role_permissions VALUES(1,19);
INSERT INTO role_permissions VALUES(1,15);
INSERT INTO role_permissions VALUES(1,8);
INSERT INTO role_permissions VALUES(1,4);
INSERT INTO role_permissions VALUES(1,6);
INSERT INTO role_permissions VALUES(1,5);
INSERT INTO role_permissions VALUES(1,7);
INSERT INTO role_permissions VALUES(1,3);
INSERT INTO role_permissions VALUES(1,40);
INSERT INTO role_permissions VALUES(1,41);
INSERT INTO role_permissions VALUES(1,42);
INSERT INTO role_permissions VALUES(1,39);
INSERT INTO role_permissions VALUES(1,44);
INSERT INTO role_permissions VALUES(1,45);
INSERT INTO role_permissions VALUES(1,43);
INSERT INTO role_permissions VALUES(1,47);
INSERT INTO role_permissions VALUES(1,49);
INSERT INTO role_permissions VALUES(1,48);
INSERT INTO role_permissions VALUES(1,50);
INSERT INTO role_permissions VALUES(1,46);
CREATE TABLE user_roles (
                user_id INTEGER,
                role_id INTEGER,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
            );
CREATE TABLE user_permissions (
                user_id INTEGER,
                permission_id INTEGER,
                PRIMARY KEY (user_id, permission_id),
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
            );
CREATE TABLE data_access_rules (
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
            );
CREATE TABLE teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                leader_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (leader_id) REFERENCES admin_users (id)
            );
CREATE TABLE team_memberships (
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
            );
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('roles',90);
INSERT INTO sqlite_sequence VALUES('permissions',1620);
COMMIT;
