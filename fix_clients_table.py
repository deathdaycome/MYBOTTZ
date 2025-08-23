#!/usr/bin/env python3
"""
Скрипт для исправления таблицы clients - пересоздание с Avito полями
Решает проблему Internal Server Error на странице /clients
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix_clients_table():
    """Исправляет таблицу clients, добавляя Avito поля через пересоздание"""
    try:
        from app.database.database import engine, Base
        from app.database.crm_models import Client
        from sqlalchemy import inspect, MetaData
        
        print("🔧 Исправление таблицы clients...")
        print("=" * 50)
        
        # Проверяем текущее состояние
        inspector = inspect(engine)
        columns = inspector.get_columns('clients')
        avito_cols_before = [col['name'] for col in columns if 'avito' in col['name'].lower()]
        
        print(f"📊 Текущие Avito поля в таблице: {avito_cols_before}")
        print(f"📊 Всего колонок до исправления: {len(columns)}")
        
        if len(avito_cols_before) >= 6:
            print("✅ Avito поля уже существуют, исправление не требуется")
            return True
        
        print("🔄 Выполняем пересоздание таблицы clients...")
        
        # Создаём метаданные только для таблицы clients
        metadata = MetaData()
        metadata.reflect(bind=engine, only=['clients'])
        
        # Сохраняем данные перед удалением
        print("💾 Сохраняем существующие данные...")
        from app.database.database import get_db
        
        existing_clients = []
        with next(get_db()) as db:
            result = db.execute("SELECT * FROM clients")
            existing_clients = result.fetchall()
            column_names = [col['name'] for col in columns]
        
        print(f"💾 Сохранено {len(existing_clients)} записей клиентов")
        
        # Удаляем таблицу clients
        if 'clients' in metadata.tables:
            clients_table = metadata.tables['clients']
            clients_table.drop(bind=engine)
            print("🗑️  Таблица clients удалена")
        
        # Пересоздаём только таблицу clients с новой структурой
        Client.__table__.create(bind=engine)
        print("🆕 Таблица clients пересоздана с Avito полями")
        
        # Восстанавливаем данные
        if existing_clients:
            print("♻️  Восстанавливаем данные клиентов...")
            with next(get_db()) as db:
                for client_data in existing_clients:
                    # Создаём словарь только с существующими полями
                    client_dict = {}
                    for i, value in enumerate(client_data):
                        if i < len(column_names):
                            field_name = column_names[i]
                            # Пропускаем поля, которых нет в новой модели
                            if hasattr(Client, field_name):
                                client_dict[field_name] = value
                    
                    # Добавляем значения по умолчанию для новых Avito полей
                    client_dict.setdefault('avito_chat_id', None)
                    client_dict.setdefault('avito_user_id', None)
                    client_dict.setdefault('avito_status', None)
                    client_dict.setdefault('avito_dialog_history', [])
                    client_dict.setdefault('avito_notes', None)
                    client_dict.setdefault('avito_follow_up', None)
                    
                    # Создаём новый объект Client
                    new_client = Client(**client_dict)
                    db.add(new_client)
                
                db.commit()
            print(f"✅ Восстановлено {len(existing_clients)} записей клиентов")
        
        # Проверяем результат
        inspector = inspect(engine)
        columns_after = inspector.get_columns('clients')
        avito_cols_after = [col['name'] for col in columns_after if 'avito' in col['name'].lower()]
        
        print("📊 Результат:")
        print(f"   ✅ Avito поля: {avito_cols_after}")
        print(f"   ✅ Всего колонок: {len(columns_after)}")
        
        if len(avito_cols_after) >= 6:
            print("🎉 Исправление выполнено успешно!")
            print("🔗 Теперь страница /clients должна работать корректно")
            return True
        else:
            print("❌ Не все Avito поля были созданы")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка исправления: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Главная функция"""
    print("🔧 Скрипт исправления таблицы clients")
    print("=" * 50)
    
    success = fix_clients_table()
    
    if success:
        print("🎉 Исправление завершено успешно!")
        print("💡 Перезапустите сервер для применения изменений:")
        print("   sudo systemctl restart bot-admin")
    else:
        print("💥 Исправление завершилось с ошибкой!")
        sys.exit(1)

if __name__ == "__main__":
    main()