#!/usr/bin/env python3
"""Обновить test_link для проекта"""

from app.database.database import get_db_context
from app.database.models import Project

project_id = 10
new_test_link = "https://t.me/NIkolaevTelegram_BOT"

with get_db_context() as db:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        print(f"❌ Проект {project_id} не найден")
    else:
        if not project.project_metadata:
            project.project_metadata = {}

        project.project_metadata['test_link'] = new_test_link
        db.commit()

        print(f"✅ Test link обновлен для проекта {project_id}")
        print(f"📋 Проект: {project.title}")
        print(f"🔗 Новая ссылка: {new_test_link}")
