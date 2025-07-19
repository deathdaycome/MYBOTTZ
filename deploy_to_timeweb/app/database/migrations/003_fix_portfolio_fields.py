#!/usr/bin/env python3
"""
Миграция для добавления недостающих полей в таблицу portfolio
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Выполнение миграции"""
    # Получаем корневую директорию проекта 
    # Текущий файл: app/database/migrations/003_fix_portfolio_fields.py
    # Корень проекта: на 4 уровня выше от текущего файла
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    
    # База данных должна быть в data/bot.db от корня проекта
    db_path = project_root / "data" / "bot.db"
    
    print(f"🔄 Выполняем миграцию базы данных: {db_path}")
    print(f"📁 Корень проекта: {project_root}")
    print(f"📂 Существует ли папка data: {(project_root / 'data').exists()}")
    print(f"🗄️ Существует ли bot.db: {db_path.exists()}")
    
    if not db_path.exists():
        print("❌ База данных не найдена.")
        # Попробуем найти файл в других местах
        possible_paths = [
            project_root / "bot.db",
            project_root / "app" / "bot.db", 
            project_root / "app" / "data" / "bot.db"
        ]
        
        for path in possible_paths:
            print(f"� Проверяем: {path}")
            if path.exists():
                print(f"✅ Найдена база данных: {path}")
                db_path = path
                break
        else:
            print("❌ База данных не найдена нигде.")
            return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Проверяем, есть ли поле subtitle
        cursor.execute("PRAGMA table_info(portfolio)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'subtitle' not in columns:
            print("➕ Добавляем поле 'subtitle' в таблицу portfolio...")
            cursor.execute("ALTER TABLE portfolio ADD COLUMN subtitle VARCHAR(500)")
            conn.commit()
            print("✅ Поле 'subtitle' добавлено")
        else:
            print("✅ Поле 'subtitle' уже существует")
        
        # Проверяем другие потенциально отсутствующие поля
        missing_fields = []
        required_fields = [
            ('complexity_level', 'INTEGER DEFAULT 5'),
            ('cost_range', 'VARCHAR(100)'),
            ('show_cost', 'BOOLEAN DEFAULT 0'),
            ('external_links', 'TEXT'),
            ('likes_count', 'INTEGER DEFAULT 0'),
            ('client_name', 'VARCHAR(200)'),
            ('project_status', 'VARCHAR(50) DEFAULT "completed"'),
            ('completed_at', 'DATETIME'),
            ('created_by', 'INTEGER')
        ]
        
        for field_name, field_type in required_fields:
            if field_name not in columns:
                missing_fields.append((field_name, field_type))
        
        if missing_fields:
            for field_name, field_type in missing_fields:
                print(f"➕ Добавляем поле '{field_name}'...")
                cursor.execute(f"ALTER TABLE portfolio ADD COLUMN {field_name} {field_type}")
            
            conn.commit()
            print(f"✅ Добавлено {len(missing_fields)} полей")
        
        conn.close()
        print("🎉 Миграция выполнена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        return False

if __name__ == "__main__":
    run_migration()
