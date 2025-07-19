"""
Миграция для добавления поля cost в таблицу portfolio
"""
import sqlite3
import os

def run_migration():
    """Добавляет поле cost в таблицу portfolio"""
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
        
        # Проверяем, есть ли уже поле cost
        if 'cost' not in column_names:
            print("Добавляем поле cost...")
            cursor.execute("ALTER TABLE portfolio ADD COLUMN cost REAL")
            print("Поле cost добавлено успешно")
        else:
            print("Поле cost уже существует")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(portfolio)")
        final_columns = cursor.fetchall()
        print(f"Финальное количество колонок: {len(final_columns)}")
        
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
        print("Миграция 006 выполнена успешно")
    else:
        print("Ошибка при выполнении миграции 006")
