#!/usr/bin/env python3
"""Скрипт для добавления test_link к проекту напрямую в БД"""

from sqlalchemy.orm import Session
from app.database.database import get_db_context
from app.database.models import Project

def add_test_link(project_id: int, test_link: str):
    """Добавить test_link к проекту"""
    with get_db_context() as db:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            print(f"❌ Проект {project_id} не найден")
            return False

        if not project.project_metadata:
            project.project_metadata = {}

        project.project_metadata['test_link'] = test_link
        db.commit()

        print(f"✅ Test link добавлен к проекту {project_id}: {test_link}")
        print(f"📋 Проект: {project.title}")
        print(f"👤 Клиент ID: {project.user_id}")
        return True

if __name__ == "__main__":
    # Добавляем test_link к проекту 10
    add_test_link(10, "https://t.me/test_bot_example")
