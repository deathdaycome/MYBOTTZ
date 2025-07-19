#!/usr/bin/env python3
"""
Скрипт для создания базовых статусов проектов
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from app.database.database import get_db
from app.database.models import ProjectStatus

def create_default_statuses():
    """Создание базовых статусов проектов"""
    
    default_statuses = [
        {
            "name": "Новый",
            "description": "Проект только что создан и ожидает рассмотрения",
            "color": "#6B7280",
            "icon": "fas fa-plus-circle",
            "is_default": True,
            "sort_order": 1
        },
        {
            "name": "На рассмотрении",
            "description": "Проект рассматривается командой",
            "color": "#F59E0B",
            "icon": "fas fa-eye",
            "is_default": True,
            "sort_order": 2
        },
        {
            "name": "Согласован",
            "description": "Проект согласован и готов к работе",
            "color": "#10B981",
            "icon": "fas fa-check-circle",
            "is_default": True,
            "sort_order": 3
        },
        {
            "name": "В работе",
            "description": "Проект находится в разработке",
            "color": "#3B82F6",
            "icon": "fas fa-cogs",
            "is_default": True,
            "sort_order": 4
        },
        {
            "name": "Тестирование",
            "description": "Проект проходит тестирование",
            "color": "#8B5CF6",
            "icon": "fas fa-vial",
            "is_default": True,
            "sort_order": 5
        },
        {
            "name": "Завершен",
            "description": "Проект успешно завершен",
            "color": "#059669",
            "icon": "fas fa-trophy",
            "is_default": True,
            "sort_order": 6
        },
        {
            "name": "Отменен",
            "description": "Проект отменен",
            "color": "#DC2626",
            "icon": "fas fa-times-circle",
            "is_default": True,
            "sort_order": 7
        },
        {
            "name": "Приостановлен",
            "description": "Проект временно приостановлен",
            "color": "#6B7280",
            "icon": "fas fa-pause-circle",
            "is_default": True,
            "sort_order": 8
        }
    ]
    
    try:
        db = next(get_db())
        
        # Проверяем, есть ли уже статусы
        existing_count = db.query(ProjectStatus).count()
        if existing_count > 0:
            print(f"ℹ️  В базе уже есть {existing_count} статусов. Пропускаем создание.")
            return
        
        # Создаем статусы
        created_count = 0
        for status_data in default_statuses:
            # Проверяем, нет ли уже такого статуса
            existing = db.query(ProjectStatus).filter(ProjectStatus.name == status_data["name"]).first()
            if existing:
                print(f"⚠️  Статус '{status_data['name']}' уже существует, пропускаем")
                continue
            
            status = ProjectStatus(
                name=status_data["name"],
                description=status_data["description"],
                color=status_data["color"],
                icon=status_data["icon"],
                is_default=status_data["is_default"],
                sort_order=status_data["sort_order"],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(status)
            created_count += 1
            print(f"✅ Создан статус: {status_data['name']}")
        
        db.commit()
        print(f"\n🎉 Успешно создано {created_count} статусов проектов!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании статусов: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Создание базовых статусов проектов...")
    create_default_statuses()
