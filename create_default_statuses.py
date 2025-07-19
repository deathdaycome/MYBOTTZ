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

from app.database.database import get_db
from app.database.models import ProjectStatus
from datetime import datetime

def create_default_statuses():
    """Создание базовых статусов проектов"""
    db = next(get_db())
    
    # Проверяем, есть ли уже статусы
    existing_count = db.query(ProjectStatus).count()
    if existing_count > 0:
        print(f"Статусы уже существуют ({existing_count} шт.). Пропускаем создание.")
        return
    
    # Базовые статусы
    default_statuses = [
        {
            "name": "Новый",
            "description": "Проект только что создан и ожидает рассмотрения",
            "color": "#007bff",
            "icon": "fas fa-plus-circle",
            "is_default": True,
            "sort_order": 1
        },
        {
            "name": "На рассмотрении", 
            "description": "Проект рассматривается менеджером",
            "color": "#ffc107",
            "icon": "fas fa-eye",
            "is_default": True,
            "sort_order": 2
        },
        {
            "name": "Согласован",
            "description": "Проект согласован и готов к выполнению",
            "color": "#17a2b8",
            "icon": "fas fa-check-circle",
            "is_default": True,
            "sort_order": 3
        },
        {
            "name": "В работе",
            "description": "Проект находится в разработке",
            "color": "#fd7e14",
            "icon": "fas fa-cogs",
            "is_default": True,
            "sort_order": 4
        },
        {
            "name": "На тестировании",
            "description": "Проект проходит тестирование",
            "color": "#6f42c1",
            "icon": "fas fa-bug",
            "is_default": True,
            "sort_order": 5
        },
        {
            "name": "Завершен",
            "description": "Проект успешно завершен",
            "color": "#28a745",
            "icon": "fas fa-check",
            "is_default": True,
            "sort_order": 6
        },
        {
            "name": "Отменен",
            "description": "Проект отменен",
            "color": "#dc3545",
            "icon": "fas fa-times-circle",
            "is_default": True,
            "sort_order": 7
        }
    ]
    
    try:
        for status_data in default_statuses:
            status = ProjectStatus(
                name=status_data["name"],
                description=status_data["description"],
                color=status_data["color"],
                icon=status_data["icon"],
                is_default=status_data["is_default"],
                is_active=True,
                sort_order=status_data["sort_order"],
                created_at=datetime.utcnow(),
                created_by_id=None  # Системный статус
            )
            db.add(status)
        
        db.commit()
        print(f"✅ Создано {len(default_statuses)} базовых статусов проектов")
        
        # Показываем созданные статусы
        statuses = db.query(ProjectStatus).order_by(ProjectStatus.sort_order).all()
        for status in statuses:
            print(f"  - {status.name} ({status.color})")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания статусов: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_default_statuses()
