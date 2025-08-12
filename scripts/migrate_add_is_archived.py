#!/usr/bin/env python3
"""
Скрипт миграции для добавления поля is_archived в таблицу projects
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import engine
from sqlalchemy import text

def migrate():
    """Добавляет поле is_archived в таблицу projects если его нет"""
    
    with engine.connect() as conn:
        # Проверяем, есть ли уже колонка is_archived
        result = conn.execute(text("PRAGMA table_info(projects)"))
        columns = [row[1] for row in result]
        
        if 'is_archived' not in columns:
            print('Добавляем колонку is_archived в таблицу projects...')
            try:
                conn.execute(text('ALTER TABLE projects ADD COLUMN is_archived BOOLEAN DEFAULT 0'))
                conn.commit()
                print('✅ Колонка is_archived успешно добавлена')
            except Exception as e:
                print(f'❌ Ошибка при добавлении колонки: {e}')
                return False
        else:
            print('ℹ️ Колонка is_archived уже существует')
        
        # Устанавливаем значение по умолчанию для существующих записей
        try:
            conn.execute(text('UPDATE projects SET is_archived = 0 WHERE is_archived IS NULL'))
            conn.commit()
            print('✅ Значения по умолчанию установлены')
        except Exception as e:
            print(f'⚠️ Не удалось обновить значения по умолчанию: {e}')
    
    return True

if __name__ == "__main__":
    print("🔄 Запуск миграции базы данных...")
    if migrate():
        print("✅ Миграция успешно завершена!")
    else:
        print("❌ Миграция завершена с ошибками")
        sys.exit(1)