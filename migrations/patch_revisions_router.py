"""
Патч для revisions.py - обновление для использования tasks table
"""

import re

def patch_revisions_router(file_path):
    """Обновить revisions.py для использования Task вместо ProjectRevision"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Обновляем импорты - добавляем Task, удаляем ProjectRevision
    if 'from ...database.models import (' in content:
        # Добавляем Task в импорты если его нет
        if 'Task,' not in content and 'Task ' not in content:
            content = content.replace(
                'from ...database.models import (',
                'from ...database.models import (Task, '
            )
        # Удаляем ProjectRevision из импортов
        content = content.replace('ProjectRevision, ', '')
        content = content.replace(', ProjectRevision', '')

    # 2. Заменяем db.query(ProjectRevision) на Task с фильтром
    content = re.sub(
        r'db\.query\(ProjectRevision\)',
        'db.query(Task).filter(Task.type == "REVISION")',
        content
    )

    # 3. Заменяем ProjectRevision. на Task.
    content = re.sub(
        r'ProjectRevision\.',
        'Task.',
        content
    )

    # 4. Обновляем поля
    content = content.replace('.estimated_time', '.estimated_hours')
    content = content.replace('.actual_time', '.actual_hours')
    content = content.replace('estimated_time=', 'estimated_hours=')
    content = content.replace('actual_time=', 'actual_hours=')

    # 5. Обновляем создание новых записей
    content = content.replace(
        'ProjectRevision(',
        'Task(type="REVISION", '
    )

    # Записываем обновленный файл
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Файл успешно обновлен")
        print(f"   Размер: {len(content)} символов")
        return True
    else:
        print("ℹ️  Изменений не требуется")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/var/www/bot_business_card/app/admin/routers/revisions.py"

    print(f"🔄 Обновление {file_path}...")
    patch_revisions_router(file_path)
