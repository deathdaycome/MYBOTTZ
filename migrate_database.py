#!/usr/bin/env python3
"""
Скрипт миграции базы данных для синхронизации локальной и серверной БД
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, local_db_path, server_db_path=None):
        self.local_db_path = local_db_path
        self.server_db_path = server_db_path or local_db_path
        self.migration_log = []
        
    def log(self, message):
        """Логирование миграции"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def backup_database(self, db_path):
        """Создание резервной копии БД"""
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            self.log(f"✅ Создана резервная копия: {backup_path}")
            return backup_path
        except Exception as e:
            self.log(f"❌ Ошибка создания резервной копии: {e}")
            return None
    
    def get_server_table_schema(self, conn, table_name):
        """Получить текущую схему таблицы на сервере"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return {row[1]: row for row in cursor.fetchall()}
    
    def alter_users_table(self, conn):
        """Обновить таблицу users до новой схемы"""
        self.log("🔧 Обновляем схему таблицы users...")
        
        cursor = conn.cursor()
        
        # Получить текущие колонки
        current_schema = self.get_server_table_schema(conn, "users")
        
        # Новые колонки для добавления
        new_columns = [
            ("bot_token", "VARCHAR(500)"),
            ("timeweb_login", "VARCHAR(255)"),
            ("timeweb_password", "VARCHAR(255)"),
            ("user_telegram_id", "VARCHAR(50)"),
            ("chat_id", "VARCHAR(50)"),
            ("bot_configured", "BOOLEAN DEFAULT FALSE")
        ]
        
        # Добавить недостающие колонки
        for col_name, col_type in new_columns:
            if col_name not in current_schema:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    self.log(f"   ➕ Добавлена колонка: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        self.log(f"   ⚠️ Колонка {col_name} уже существует")
                    else:
                        self.log(f"   ❌ Ошибка добавления колонки {col_name}: {e}")
        
        conn.commit()
        self.log("✅ Схема таблицы users обновлена")
    
    def sync_data_smart(self, local_conn, server_conn, table_name, unique_field="id"):
        """Умная синхронизация данных без дубликатов"""
        self.log(f"🔄 Синхронизация таблицы {table_name}...")
        
        local_cursor = local_conn.cursor()
        server_cursor = server_conn.cursor()
        
        try:
            # Получить данные из локальной БД
            local_cursor.execute(f"SELECT * FROM {table_name}")
            local_data = local_cursor.fetchall()
            
            if not local_data:
                self.log(f"   ⚠️ Нет данных в локальной таблице {table_name}")
                return
            
            # Получить схему таблицы
            local_cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = local_cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Получить схему серверной таблицы
            server_cursor.execute(f"PRAGMA table_info({table_name})")
            server_columns_info = server_cursor.fetchall()
            server_column_names = [col[1] for col in server_columns_info]
            
            # Найти общие колонки
            common_columns = [col for col in column_names if col in server_column_names]
            
            if not common_columns:
                self.log(f"   ❌ Нет общих колонок в таблице {table_name}")
                return
            
            # Получить существующие записи на сервере
            if unique_field in server_column_names:
                server_cursor.execute(f"SELECT {unique_field} FROM {table_name}")
                existing_ids = {row[0] for row in server_cursor.fetchall()}
            else:
                existing_ids = set()
            
            # Подготовить запрос для вставки
            placeholders = ", ".join(["?" for _ in common_columns])
            columns_str = ", ".join(common_columns)
            insert_query = f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            inserted_count = 0
            skipped_count = 0
            
            for row in local_data:
                # Создать словарь из строки
                row_dict = dict(zip(column_names, row))
                
                # Проверить, существует ли запись
                if unique_field in row_dict and row_dict[unique_field] in existing_ids:
                    skipped_count += 1
                    continue
                
                # Подготовить данные для вставки
                values = [row_dict.get(col) for col in common_columns]
                
                try:
                    server_cursor.execute(insert_query, values)
                    inserted_count += 1
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed" in str(e):
                        skipped_count += 1
                    else:
                        self.log(f"   ⚠️ Ошибка вставки в {table_name}: {e}")
            
            server_conn.commit()
            self.log(f"   ✅ {table_name}: добавлено {inserted_count}, пропущено {skipped_count}")
            
        except Exception as e:
            self.log(f"   ❌ Ошибка синхронизации {table_name}: {e}")
    
    def migrate(self, target_db_path=None):
        """Выполнить миграцию"""
        if target_db_path:
            self.server_db_path = target_db_path
            
        self.log("🚀 Начинаем миграцию базы данных...")
        
        # Проверить наличие файлов
        if not Path(self.local_db_path).exists():
            self.log(f"❌ Локальная БД не найдена: {self.local_db_path}")
            return False
        
        # Создать резервную копию серверной БД
        if Path(self.server_db_path).exists():
            backup_path = self.backup_database(self.server_db_path)
            if not backup_path:
                return False
        
        try:
            # Подключиться к базам
            local_conn = sqlite3.connect(self.local_db_path)
            server_conn = sqlite3.connect(self.server_db_path)
            
            # 1. Обновить схему users
            self.alter_users_table(server_conn)
            
            # 2. Синхронизировать данные критичных таблиц
            critical_tables = [
                ("users", "telegram_id"),
                ("portfolio", "id"),
                ("projects", "id"),
                ("finance_transactions", "id"),
                ("finance_categories", "id"),
                ("admin_users", "username"),
                ("settings", "key"),
                ("faq", "id"),
                ("project_statuses", "id"),
                ("contractors", "id"),
                ("service_providers", "id"),
                ("tasks", "id"),
                ("money_categories", "id"),
                ("money_transactions", "id"),
                ("receipt_files", "id"),
                ("revision_message_files", "id"),
                ("task_comments", "id")
            ]
            
            for table_name, unique_field in critical_tables:
                self.sync_data_smart(local_conn, server_conn, table_name, unique_field)
            
            # Закрыть соединения
            local_conn.close()
            server_conn.close()
            
            self.log("✅ Миграция завершена успешно!")
            
            # Сохранить лог миграции
            log_file = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.migration_log))
            self.log(f"📋 Лог миграции сохранен: {log_file}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Критическая ошибка миграции: {e}")
            return False

def main():
    """Главная функция"""
    local_db = "data/bot.db"
    
    if len(sys.argv) > 1:
        server_db = sys.argv[1]
        print(f"Целевая БД: {server_db}")
    else:
        server_db = "data/bot.db"  # По умолчанию тестируем на той же БД
        print("Тестовый режим - используем локальную БД как целевую")
    
    migrator = DatabaseMigrator(local_db, server_db)
    success = migrator.migrate()
    
    if success:
        print("\n🎉 Миграция выполнена успешно!")
        print("Теперь можно запускать приложение с обновленной БД.")
    else:
        print("\n❌ Миграция не удалась. Проверьте логи.")
        sys.exit(1)

if __name__ == "__main__":
    main()