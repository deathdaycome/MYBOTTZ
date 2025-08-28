#!/usr/bin/env python3
"""
Скрипт для создания тестовой записи в портфолио
"""

import sys
import os
import sqlite3
from datetime import datetime

# Путь к базе данных
db_path = "admin_panel.db"

def create_test_portfolio_item():
    """Создать тестовую запись в портфолио"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже записи в портфолио
        cursor.execute("SELECT COUNT(*) FROM portfolio")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"В портфолио уже есть {count} записей. Ничего не добавляем.")
            return
        
        # Создаем тестовую запись
        now = datetime.utcnow()
        
        test_data = {
            'title': 'Telegram бот для автоматизации бизнеса',
            'subtitle': 'Умный помощник для управления клиентами',
            'description': 'Полнофункциональный Telegram бот с возможностями CRM, управления проектами, финансовой отчетности и интеграции с различными сервисами. Включает админ-панель для управления.',
            'category': 'telegram_bots',
            'technologies': 'Python, FastAPI, SQLAlchemy, Telegram Bot API, HTML/CSS/JavaScript',
            'complexity': 'complex',
            'complexity_level': 8,
            'development_time': 30,
            'cost': 50000.0,
            'cost_range': '40000-60000',
            'show_cost': True,
            'demo_link': 'https://t.me/YourTestBot',
            'is_featured': True,
            'is_visible': True,
            'sort_order': 1,
            'tags': 'telegram,бот,crm,автоматизация,бизнес',
            'client_name': 'ООО "Пример"',
            'project_status': 'completed',
            'views_count': 0,
            'likes_count': 0,
            'is_published': False,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'created_by': 1
        }
        
        # SQL для вставки
        columns = ', '.join(test_data.keys())
        placeholders = ', '.join(['?' for _ in test_data])
        
        sql = f"INSERT INTO portfolio ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, list(test_data.values()))
        
        conn.commit()
        
        item_id = cursor.lastrowid
        print(f"✅ Создана тестовая запись в портфолио с ID: {item_id}")
        print(f"   Название: {test_data['title']}")
        print(f"   Категория: {test_data['category']}")
        print(f"   Статус: {test_data['project_status']}")
        
    except Exception as e:
        print(f"❌ Ошибка создания тестовой записи: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Создание тестовой записи в портфолио...")
    create_test_portfolio_item()