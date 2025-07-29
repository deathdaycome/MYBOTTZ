#!/usr/bin/env python3
"""
Скрипт миграции базы данных для добавления новых полей в проекты
"""
import sqlite3
import sys
import os

def migrate_database():
    """Добавляет новые поля в таблицу projects"""
    db_path = "data/bot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Файл базы данных {db_path} не найден!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем какие поля уже существуют
        cursor.execute("PRAGMA table_info(projects)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Список новых полей для добавления
        new_columns = [
            ("prepayment_amount", "REAL DEFAULT 0.0"),
            ("client_paid_total", "REAL DEFAULT 0.0"),
            ("executor_paid_total", "REAL DEFAULT 0.0")
        ]
        
        added_columns = []
        
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE projects ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    added_columns.append(column_name)
                    print(f"✅ Добавлено поле: {column_name}")
                except sqlite3.Error as e:
                    print(f"❌ Ошибка добавления поля {column_name}: {e}")
                    return False
            else:
                print(f"ℹ️  Поле {column_name} уже exists")
        
        conn.commit()
        conn.close()
        
        if added_columns:
            print(f"\n🎉 Миграция завершена! Добавлено полей: {len(added_columns)}")
        else:
            print("\n✅ Все поля уже существуют, миграция не требуется")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def check_migration():
    """Проверяет успешность миграции"""
    db_path = "data/bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(projects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ["prepayment_amount", "client_paid_total", "executor_paid_total"]
        missing_columns = [col for col in required_columns if col not in columns]
        
        conn.close()
        
        if missing_columns:
            print(f"❌ Отсутствуют поля: {missing_columns}")
            return False
        else:
            print("✅ Все новые поля присутствуют в базе данных")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Запуск миграции базы данных...")
    print("=" * 50)
    
    if migrate_database():
        print("\n🔍 Проверка миграции...")
        if check_migration():
            print("\n🎉 Миграция выполнена успешно!")
            sys.exit(0)
        else:
            print("\n❌ Миграция выполнена с ошибками!")
            sys.exit(1)
    else:
        print("\n❌ Миграция не удалась!")
        sys.exit(1)