"""
Финальная миграция для добавления всех недостающих полей в таблицу portfolio
"""
import sqlite3
import os

def run_migration():
    """Добавляет все недостающие поля в таблицу portfolio"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'bot.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(portfolio)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("Текущие колонки в таблице portfolio:")
        for col in columns:
            print(f"  {col[1]} - {col[2]}")
        print(f"Всего колонок: {len(columns)}")
        
        # Список всех полей, которые должны быть в таблице
        required_fields = [
            ('updated_at', 'DATETIME'),
            ('technologies', 'TEXT'),  # Изменяем тип с JSON на TEXT для совместимости
        ]
        
        # Добавляем недостающие поля
        for field_name, field_type in required_fields:
            if field_name not in column_names:
                print(f"Добавляем поле {field_name} ({field_type})...")
                cursor.execute(f"ALTER TABLE portfolio ADD COLUMN {field_name} {field_type}")
                print(f"Поле {field_name} добавлено успешно")
            else:
                print(f"Поле {field_name} уже существует")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(portfolio)")
        final_columns = cursor.fetchall()
        print(f"Финальное количество колонок: {len(final_columns)}")
        
        print("\nФинальная структура таблицы:")
        for col in final_columns:
            print(f"  {col[1]} - {col[2]}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Ошибка при выполнении миграции: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("Финальная миграция 007 выполнена успешно")
    else:
        print("Ошибка при выполнении миграции 007")
