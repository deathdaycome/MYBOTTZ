"""
Миграция: Добавление таблиц для управления арендой серверов Timeweb

Создаются две таблицы:
- hosting_servers: информация о серверах и клиентах
- hosting_payments: история платежей за серверы

Функционал:
- Учет серверов с конфигурациями
- Финансовый учет (себестоимость, цена клиента, прибыль)
- История платежей с периодами
- Календарь платежей
- Уведомления о платежах в Telegram
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
    print("🔄 Начинаем миграцию: Создание таблиц для Timeweb Хостинга")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # === ТАБЛИЦА: hosting_servers ===
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='hosting_servers'
        """)

        if cursor.fetchone():
            print("⚠️  Таблица hosting_servers уже существует, пропускаем создание")
        else:
            cursor.execute("""
                CREATE TABLE hosting_servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    client_name VARCHAR(255) NOT NULL,
                    client_company VARCHAR(255),
                    client_telegram_id BIGINT,

                    server_name VARCHAR(255) NOT NULL,
                    configuration TEXT,
                    ip_address VARCHAR(50),

                    cost_price REAL NOT NULL DEFAULT 0,
                    client_price REAL NOT NULL,
                    service_fee REAL DEFAULT 0,

                    start_date TIMESTAMP NOT NULL,
                    next_payment_date TIMESTAMP NOT NULL,
                    payment_period VARCHAR(20) DEFAULT 'monthly',

                    status VARCHAR(20) DEFAULT 'active',
                    notes TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL
                )
            """)

            # Индексы для hosting_servers
            cursor.execute("""
                CREATE INDEX idx_hosting_servers_client_id ON hosting_servers(client_id)
            """)
            cursor.execute("""
                CREATE INDEX idx_hosting_servers_status ON hosting_servers(status)
            """)
            cursor.execute("""
                CREATE INDEX idx_hosting_servers_next_payment ON hosting_servers(next_payment_date)
            """)

            print("✅ Таблица hosting_servers создана с индексами")

        # === ТАБЛИЦА: hosting_payments ===
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='hosting_payments'
        """)

        if cursor.fetchone():
            print("⚠️  Таблица hosting_payments уже существует, пропускаем создание")
        else:
            cursor.execute("""
                CREATE TABLE hosting_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,

                    amount REAL NOT NULL,
                    payment_date TIMESTAMP,
                    expected_date TIMESTAMP NOT NULL,

                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,

                    status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    receipt_url VARCHAR(500),

                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (server_id) REFERENCES hosting_servers (id) ON DELETE CASCADE
                )
            """)

            # Индексы для hosting_payments
            cursor.execute("""
                CREATE INDEX idx_hosting_payments_server_id ON hosting_payments(server_id)
            """)
            cursor.execute("""
                CREATE INDEX idx_hosting_payments_status ON hosting_payments(status)
            """)
            cursor.execute("""
                CREATE INDEX idx_hosting_payments_expected_date ON hosting_payments(expected_date)
            """)

            print("✅ Таблица hosting_payments создана с индексами")

        conn.commit()

        # Показываем статистику
        print(f"\n📊 Статистика системы:")

        cursor.execute("SELECT COUNT(*) FROM clients")
        clients_count = cursor.fetchone()[0]
        print(f"   Клиентов в CRM: {clients_count}")

        cursor.execute("SELECT COUNT(*) FROM hosting_servers")
        servers_count = cursor.fetchone()[0]
        print(f"   Серверов в аренде: {servers_count}")

        print("\n✅ Миграция завершена успешно!")
        print("\n💡 Создан раздел Timeweb Хостинг с функционалом:")
        print("   • Учет серверов и клиентов")
        print("   • Расчет прибыли (₽ и %)")
        print("   • История платежей")
        print("   • Календарь платежей")
        print("   • Автоматические уведомления")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def rollback_migration():
    """Откатить миграцию"""
    print("🔄 Откат миграции: Удаление таблиц Timeweb Хостинга")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS hosting_payments")
        cursor.execute("DROP TABLE IF EXISTS hosting_servers")
        conn.commit()
        print("✅ Таблицы hosting_payments и hosting_servers удалены")

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
