#!/usr/bin/env python3
"""
Скрипт анализа различий между локальной и серверной базой данных
"""

import sqlite3
import sys
from pathlib import Path

def get_table_schema(db_path, table_name):
    """Получить схему таблицы из БД"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получить информацию о колонках
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        conn.close()
        return columns
    except Exception as e:
        print(f"Ошибка при получении схемы таблицы {table_name}: {e}")
        return []

def compare_table_schemas(local_db, server_db, table_name):
    """Сравнить схемы таблиц между локальной и серверной БД"""
    local_schema = get_table_schema(local_db, table_name)
    server_schema = get_table_schema(server_db, table_name)
    
    print(f"\n=== Таблица {table_name} ===")
    print(f"Локальная БД: {len(local_schema)} колонок")
    print(f"Серверная БД: {len(server_schema)} колонок")
    
    if len(local_schema) != len(server_schema):
        print("⚠️ Различается количество колонок!")
        
        # Найти недостающие колонки
        local_cols = {col[1]: col for col in local_schema}
        server_cols = {col[1]: col for col in server_schema}
        
        missing_in_server = set(local_cols.keys()) - set(server_cols.keys())
        missing_in_local = set(server_cols.keys()) - set(local_cols.keys())
        
        if missing_in_server:
            print("❌ Отсутствуют на сервере:")
            for col_name in missing_in_server:
                col_info = local_cols[col_name]
                print(f"   - {col_name} ({col_info[2]})")
        
        if missing_in_local:
            print("➕ Есть только на сервере:")
            for col_name in missing_in_local:
                col_info = server_cols[col_name]
                print(f"   - {col_name} ({col_info[2]})")
    else:
        print("✅ Количество колонок совпадает")
    
    return local_schema, server_schema

def get_all_tables(db_path):
    """Получить список всех таблиц в БД"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    except Exception as e:
        print(f"Ошибка при получении списка таблиц: {e}")
        return []

def main():
    """Главная функция анализа"""
    local_db = "data/bot.db"
    
    if not Path(local_db).exists():
        print(f"❌ Локальная БД не найдена: {local_db}")
        return
    
    print("🔍 Анализ различий между локальной и серверной БД...")
    print("=" * 60)
    
    # Получить список таблиц
    local_tables = get_all_tables(local_db)
    print(f"📋 Найдено таблиц в локальной БД: {len(local_tables)}")
    
    # Имитация серверной БД (мы знаем что users имеет 13 колонок на сервере)
    critical_tables = ['users', 'portfolio', 'projects', 'finance_transactions']
    
    for table in critical_tables:
        if table in local_tables:
            local_schema = get_table_schema(local_db, table)
            print(f"\n📊 Схема таблицы {table}:")
            for col in local_schema:
                cid, name, col_type, not_null, default, pk = col
                null_str = "NOT NULL" if not_null else "NULL"
                pk_str = " (PK)" if pk else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"   {name}: {col_type} {null_str}{default_str}{pk_str}")
    
    # Проверить данные в критичных таблицах
    print("\n" + "=" * 60)
    print("📈 Количество записей в таблицах:")
    
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    for table in local_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} записей")
        except Exception as e:
            print(f"   {table}: ошибка подсчета - {e}")
    
    conn.close()

if __name__ == "__main__":
    main()