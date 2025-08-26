#!/usr/bin/env python3
"""
Создание таблиц системы уведомлений для сотрудников
"""

import sqlite3
import os
import sys
from datetime import datetime

def get_database_path():
    """Найти путь к базе данных"""
    possible_paths = [
        "data/bot.db",
        "business_card_bot.db",
        "app.db",
        "data/app.db", 
        "data/business_card_bot.db",
        "/var/www/bot_business_card/data/bot.db",
        "/var/www/bot_business_card/business_card_bot.db",
        "/var/www/bot_business_card/app.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return "data/bot.db"  # Создаст новую если не найдена

def main():
    """Создать таблицы системы уведомлений"""
    print("📫 Создание системы уведомлений для сотрудников...")
    print("=" * 60)
    
    db_path = get_database_path()
    print(f"📁 База данных: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📊 Создание таблиц уведомлений...")
        
        # Таблица настроек уведомлений сотрудников
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user_id INTEGER NOT NULL UNIQUE,
                telegram_user_id VARCHAR(50) NOT NULL,
                
                -- Основные настройки
                notifications_enabled BOOLEAN DEFAULT 1,
                notification_language VARCHAR(10) DEFAULT 'ru',
                
                -- Настройки для исполнителей (проекты)
                project_assigned BOOLEAN DEFAULT 1,
                project_status_changed BOOLEAN DEFAULT 1,
                project_deadline_reminder BOOLEAN DEFAULT 1,
                project_overdue BOOLEAN DEFAULT 1,
                project_new_task BOOLEAN DEFAULT 1,
                
                -- Настройки для продажников (Avito и CRM)
                avito_new_message BOOLEAN DEFAULT 1,
                avito_unread_reminder BOOLEAN DEFAULT 1,
                avito_urgent_message BOOLEAN DEFAULT 1,
                lead_assigned BOOLEAN DEFAULT 1,
                lead_status_changed BOOLEAN DEFAULT 1,
                deal_assigned BOOLEAN DEFAULT 1,
                deal_status_changed BOOLEAN DEFAULT 1,
                
                -- Настройки времени уведомлений
                work_hours_start VARCHAR(5) DEFAULT '09:00',
                work_hours_end VARCHAR(5) DEFAULT '18:00',
                weekend_notifications BOOLEAN DEFAULT 0,
                urgent_notifications_always BOOLEAN DEFAULT 1,
                
                -- Интервалы напоминаний (в минутах)
                avito_reminder_interval INTEGER DEFAULT 30,
                project_reminder_interval INTEGER DEFAULT 120,
                
                -- Системные поля
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (admin_user_id) REFERENCES admin_users (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица employee_notification_settings создана")
        
        # Таблица очереди уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Получатель
                telegram_user_id VARCHAR(50) NOT NULL,
                admin_user_id INTEGER,
                
                -- Тип и содержание уведомления
                notification_type VARCHAR(50) NOT NULL,
                priority VARCHAR(20) DEFAULT 'normal',
                
                -- Сообщение
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                action_url VARCHAR(500),
                
                -- Метаданные
                entity_type VARCHAR(50),
                entity_id VARCHAR(100),
                metadata TEXT DEFAULT '{}',
                
                -- Статус обработки
                status VARCHAR(20) DEFAULT 'pending',
                scheduled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sent_at DATETIME,
                
                -- Повторные попытки
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                
                -- Группировка (для объединения похожих уведомлений)
                group_key VARCHAR(100),
                
                -- Системные поля
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (admin_user_id) REFERENCES admin_users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица notification_queue создана")
        
        # Таблица лога уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Получатель и отправитель
                telegram_user_id VARCHAR(50) NOT NULL,
                admin_user_id INTEGER,
                sent_by_user_id INTEGER,
                
                -- Уведомление
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                
                -- Результат отправки
                status VARCHAR(20) NOT NULL,
                error_message TEXT,
                telegram_message_id INTEGER,
                
                -- Метаданные
                entity_type VARCHAR(50),
                entity_id VARCHAR(100),
                
                -- Время
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (admin_user_id) REFERENCES admin_users (id) ON DELETE SET NULL,
                FOREIGN KEY (sent_by_user_id) REFERENCES admin_users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица notification_log создана")
        
        # Создаем индексы для производительности
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_queue_telegram_user_id ON notification_queue (telegram_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON notification_queue (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_queue_scheduled_at ON notification_queue (scheduled_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_queue_group_key ON notification_queue (group_key)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_log_telegram_user_id ON notification_log (telegram_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_log_admin_user_id ON notification_log (admin_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_log_sent_at ON notification_log (sent_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_notification_settings_admin_user_id ON employee_notification_settings (admin_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_notification_settings_telegram_user_id ON employee_notification_settings (telegram_user_id)')
        
        print("✅ Индексы созданы")
        
        # Создаем настройки для продажника с TG ID 7472859094
        print("\n🔧 Настройка уведомлений для продажника...")
        
        # Находим продажника (предполагаем что есть пользователь с ролью salesperson)
        cursor.execute("SELECT id FROM admin_users WHERE role = 'salesperson' LIMIT 1")
        salesperson = cursor.fetchone()
        
        if salesperson:
            salesperson_id = salesperson[0]
            
            # Создаем настройки уведомлений для продажника
            cursor.execute('''
                INSERT OR REPLACE INTO employee_notification_settings (
                    admin_user_id, 
                    telegram_user_id,
                    notifications_enabled,
                    avito_new_message,
                    avito_unread_reminder,
                    avito_urgent_message,
                    lead_assigned,
                    lead_status_changed,
                    deal_assigned,
                    deal_status_changed,
                    urgent_notifications_always,
                    avito_reminder_interval
                ) VALUES (?, ?, 1, 1, 1, 1, 1, 1, 1, 1, 1, 30)
            ''', (salesperson_id, '7472859094'))
            
            print(f"✅ Настройки созданы для продажника (TG ID: 7472859094)")
        else:
            print("⚠️ Продажник не найден. Создайте пользователя с ролью 'salesperson' в разделе пользователей")
        
        # Сохраняем изменения
        conn.commit()
        conn.close()
        
        print(f"\n✅ Система уведомлений успешно создана!")
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🚀 Теперь вы можете:")
        print("  1. Зайти в админку -> Уведомления -> Настройки")
        print("  2. Настроить уведомления для сотрудников")
        print("  3. Отправить тестовые уведомления")
        print("  4. Следить за очередью и логами уведомлений")
        
        if salesperson:
            print(f"\n📱 Продажник с TG ID 7472859094 уже настроен:")
            print("  ✅ Уведомления о новых сообщениях Avito включены")
            print("  ✅ Напоминания о неотвеченных сообщениях включены")
            print("  ✅ Уведомления о лидах и сделках включены")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()