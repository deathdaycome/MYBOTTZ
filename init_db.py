#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def init_database():
    """Инициализация базы данных"""
    print("🔧 Инициализация базы данных...")
    
    try:
        from app.database.database import init_db
        from app.database.models import Base, Portfolio
        from sqlalchemy import create_engine, inspect
        from app.config.settings import settings
        
        # Инициализируем базу
        init_db()
        print("✅ База данных инициализирована")
        
        # Проверяем таблицу portfolio
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        
        if 'portfolio' in inspector.get_table_names():
            print("✅ Таблица portfolio существует")
            
            # Проверяем колонки
            columns = [col['name'] for col in inspector.get_columns('portfolio')]
            print(f"📊 Колонки в таблице portfolio: {len(columns)}")
            
            required_columns = [
                'id', 'title', 'description', 'category', 'main_image', 
                'technologies', 'is_featured', 'is_visible', 'created_at'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                print(f"⚠️ Отсутствующие колонки: {missing_columns}")
            else:
                print("✅ Все основные колонки присутствуют")
        else:
            print("❌ Таблица portfolio не найдена, создаем...")
            Base.metadata.create_all(engine)
            print("✅ Таблица portfolio создана")
            
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if init_database():
        print("🚀 База данных готова к работе!")
    else:
        print("💥 Ошибка инициализации базы данных")
        sys.exit(1)
