"""
Сервис для автоматического расчёта прогресса выполнения проектов
"""

import sqlite3
from typing import Optional, Dict
from datetime import datetime


def calculate_project_progress(db_path: str, project_id: int) -> int:
    """
    Рассчитать прогресс выполнения проекта на основе задач

    Логика расчёта:
    - Считаем общее количество задач проекта (type = 'TASK' или type IS NULL)
    - Считаем количество завершённых задач (status = 'completed')
    - Прогресс = (завершённые задачи / все задачи) * 100

    Если задач нет, прогресс определяется на основе статуса проекта

    Args:
        db_path: Путь к БД
        project_id: ID проекта

    Returns:
        Прогресс выполнения (0-100)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Получаем статус проекта
        cursor.execute(
            "SELECT status FROM projects WHERE id = ?",
            (project_id,)
        )
        project = cursor.fetchone()

        if not project:
            return 0

        project_status = project[0]

        # Считаем все задачи проекта (исключаем правки - type='REVISION')
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            AND is_archived = 0
            """,
            (project_id,)
        )
        total_tasks = cursor.fetchone()[0]

        # Если задач нет - расчёт на основе статуса проекта
        if total_tasks == 0:
            status_progress = {
                'new': 0,
                'review': 10,
                'accepted': 20,
                'in_progress': 50,
                'testing': 80,
                'completed': 100,
                'cancelled': 0,
                'on_hold': 0,
            }
            return status_progress.get(project_status, 0)

        # Считаем завершённые задачи
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            AND status = 'completed'
            AND is_archived = 0
            """,
            (project_id,)
        )
        completed_tasks = cursor.fetchone()[0]

        # Расчёт прогресса
        progress = int((completed_tasks / total_tasks) * 100)

        # Если все задачи завершены, но проект не completed - максимум 95%
        if progress == 100 and project_status != 'completed':
            progress = 95

        # Если проект completed - всегда 100%
        if project_status == 'completed':
            progress = 100

        return progress

    finally:
        conn.close()


def update_project_progress(db_path: str, project_id: int) -> Optional[int]:
    """
    Обновить прогресс проекта в БД

    Args:
        db_path: Путь к БД
        project_id: ID проекта

    Returns:
        Новое значение прогресса или None при ошибке
    """
    try:
        progress = calculate_project_progress(db_path, project_id)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Проверяем, есть ли колонка progress
            cursor.execute("PRAGMA table_info(projects)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'progress' not in columns:
                # Добавляем колонку progress
                cursor.execute("ALTER TABLE projects ADD COLUMN progress INTEGER DEFAULT 0")
                conn.commit()

            # Обновляем прогресс
            cursor.execute(
                "UPDATE projects SET progress = ?, updated_at = ? WHERE id = ?",
                (progress, datetime.now().isoformat(), project_id)
            )
            conn.commit()

            return progress

        finally:
            conn.close()

    except Exception as e:
        print(f"Ошибка обновления прогресса проекта {project_id}: {e}")
        return None


def get_project_statistics(db_path: str, project_id: int) -> Dict:
    """
    Получить детальную статистику по проекту

    Args:
        db_path: Путь к БД
        project_id: ID проекта

    Returns:
        Словарь со статистикой
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Общее количество задач
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            AND is_archived = 0
            """,
            (project_id,)
        )
        total_tasks = cursor.fetchone()[0]

        # Завершённые задачи
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            AND status = 'completed'
            AND is_archived = 0
            """,
            (project_id,)
        )
        completed_tasks = cursor.fetchone()[0]

        # Задачи в работе
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            AND status = 'in_progress'
            AND is_archived = 0
            """,
            (project_id,)
        )
        in_progress_tasks = cursor.fetchone()[0]

        # Новые задачи
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            AND status = 'new'
            AND is_archived = 0
            """,
            (project_id,)
        )
        new_tasks = cursor.fetchone()[0]

        # Правки
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND type = 'REVISION'
            AND is_archived = 0
            """,
            (project_id,)
        )
        total_revisions = cursor.fetchone()[0]

        # Незавершённые правки
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND type = 'REVISION'
            AND status != 'completed'
            AND is_archived = 0
            """,
            (project_id,)
        )
        open_revisions = cursor.fetchone()[0]

        # Прогресс
        progress = calculate_project_progress(db_path, project_id)

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'new_tasks': new_tasks,
            'total_revisions': total_revisions,
            'open_revisions': open_revisions,
            'progress': progress,
        }

    finally:
        conn.close()


def update_all_projects_progress(db_path: str) -> int:
    """
    Обновить прогресс всех активных проектов

    Args:
        db_path: Путь к БД

    Returns:
        Количество обновлённых проектов
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Получаем все активные проекты
        cursor.execute(
            """
            SELECT id
            FROM projects
            WHERE is_archived = 0
            AND status NOT IN ('cancelled', 'completed')
            """
        )
        projects = cursor.fetchall()

        updated_count = 0
        for project in projects:
            project_id = project[0]
            result = update_project_progress(db_path, project_id)
            if result is not None:
                updated_count += 1

        return updated_count

    finally:
        conn.close()


if __name__ == "__main__":
    # Тестовый запуск
    import os

    db_path = '/app/data/bot.db' if os.path.exists('/app/data/bot.db') else 'data/bot.db'

    print("🔄 Обновление прогресса всех проектов...")
    count = update_all_projects_progress(db_path)
    print(f"✅ Обновлено проектов: {count}")
