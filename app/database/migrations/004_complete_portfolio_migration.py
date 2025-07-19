#!/usr/bin/env python3
"""
Полная миграция для таблицы portfolio - добавление всех недостающих полей
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Выполнение полной миграции таблицы portfolio"""
    # Получаем корневую директорию проекта 
    project_root = Path(__file__).parent.parent.parent.parent
    db_path = project_root / "data" / "bot.db"
    
    print(f"🔄 Выполняем полную миграцию таблицы portfolio: {db_path}")
    
    if not db_path.exists():
        print("❌ База данных не найдена. Сначала запустите приложение.")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Проверяем текущую структуру таблицы
        cursor.execute("PRAGMA table_info(portfolio)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Текущие поля в таблице portfolio: {columns}")
        
        # Полный список всех полей, которые должны быть в таблице
        required_fields = [
            ('subtitle', 'VARCHAR(500)'),
            ('main_image', 'VARCHAR(500)'),
            ('image_paths', 'TEXT'),
            ('complexity_level', 'INTEGER DEFAULT 5'),
            ('cost_range', 'VARCHAR(100)'),
            ('show_cost', 'BOOLEAN DEFAULT 0'),
            ('demo_link', 'VARCHAR(500)'),
            ('repository_link', 'VARCHAR(500)'),
            ('external_links', 'TEXT'),
            ('is_featured', 'BOOLEAN DEFAULT 0'),
            ('is_visible', 'BOOLEAN DEFAULT 1'),
            ('sort_order', 'INTEGER DEFAULT 0'),
            ('views_count', 'INTEGER DEFAULT 0'),
            ('likes_count', 'INTEGER DEFAULT 0'),
            ('tags', 'TEXT'),
            ('client_name', 'VARCHAR(200)'),
            ('project_status', 'VARCHAR(50) DEFAULT "completed"'),
            ('completed_at', 'DATETIME'),
            ('created_by', 'INTEGER')
        ]
        
        missing_fields = []
        for field_name, field_type in required_fields:
            if field_name not in columns:
                missing_fields.append((field_name, field_type))
        
        if missing_fields:
            print(f"➕ Найдено {len(missing_fields)} недостающих полей:")
            for field_name, field_type in missing_fields:
                print(f"   - {field_name}")
                try:
                    cursor.execute(f"ALTER TABLE portfolio ADD COLUMN {field_name} {field_type}")
                    print(f"   ✅ Поле '{field_name}' добавлено")
                except Exception as e:
                    print(f"   ❌ Ошибка при добавлении '{field_name}': {e}")
            
            conn.commit()
        else:
            print("✅ Все поля уже существуют")
        
        # Проверяем итоговую структуру
        cursor.execute("PRAGMA table_info(portfolio)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Итоговые поля в таблице portfolio ({len(final_columns)}): {final_columns}")
        
        conn.close()
        print("🎉 Полная миграция выполнена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        return False

if __name__ == "__main__":
    run_migration()
