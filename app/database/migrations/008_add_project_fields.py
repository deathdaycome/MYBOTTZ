#!/usr/bin/env python3
"""
Миграция для добавления полей API токена и данных Timeweb в проекты
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from app.database.database import engine, SessionLocal
from app.database.models import Project

Base = declarative_base()

def upgrade():
    """Добавляем новые поля к проекту"""
    print("🔄 Добавляем новые поля к проектам...")
    
    # В SQLAlchemy для SQLite мы не можем добавить колонки напрямую
    # Вместо этого будем использовать project_metadata JSON поле
    
    db = SessionLocal()
    try:
        # Проверяем существующие проекты и добавляем новые поля в metadata
        projects = db.query(Project).all()
        
        for project in projects:
            if not project.project_metadata:
                project.project_metadata = {}
            
            # Добавляем новые поля если их нет
            if 'bot_token' not in project.project_metadata:
                project.project_metadata['bot_token'] = None
                
            if 'timeweb_login' not in project.project_metadata:
                project.project_metadata['timeweb_login'] = None
                
            if 'timeweb_password' not in project.project_metadata:
                project.project_metadata['timeweb_password'] = None
        
        db.commit()
        print("✅ Поля успешно добавлены к проектам")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении полей: {e}")
        raise
    finally:
        db.close()

def downgrade():
    """Удаляем добавленные поля"""
    print("🔄 Удаляем добавленные поля...")
    
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        
        for project in projects:
            if project.project_metadata:
                # Удаляем добавленные поля
                project.project_metadata.pop('bot_token', None)
                project.project_metadata.pop('timeweb_login', None)
                project.project_metadata.pop('timeweb_password', None)
        
        db.commit()
        print("✅ Поля успешно удалены")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при удалении полей: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()