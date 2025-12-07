"""
API для работы с прогрессом выполнения проектов
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3
import os

from app.services.project_progress_service import (
    calculate_project_progress,
    update_project_progress,
    get_project_statistics,
    update_all_projects_progress,
)

router = APIRouter()

# Путь к БД
DB_PATH = os.getenv('DATABASE_PATH', '/app/data/bot.db')
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/bot.db'


@router.get("/api/projects/{project_id}/progress")
async def get_project_progress(project_id: int, request: Request):
    """
    Получить прогресс выполнения проекта

    Returns:
        {
            "success": true,
            "progress": 75,
            "statistics": {
                "total_tasks": 10,
                "completed_tasks": 7,
                "in_progress_tasks": 2,
                "new_tasks": 1,
                "total_revisions": 3,
                "open_revisions": 1
            }
        }
    """
    try:
        # Получаем статистику
        stats = get_project_statistics(DB_PATH, project_id)

        return JSONResponse({
            "success": True,
            "progress": stats['progress'],
            "statistics": {
                "total_tasks": stats['total_tasks'],
                "completed_tasks": stats['completed_tasks'],
                "in_progress_tasks": stats['in_progress_tasks'],
                "new_tasks": stats['new_tasks'],
                "total_revisions": stats['total_revisions'],
                "open_revisions": stats['open_revisions'],
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения прогресса: {str(e)}"
        }, status_code=500)


@router.post("/api/projects/{project_id}/update-progress")
async def refresh_project_progress(project_id: int, request: Request):
    """
    Обновить прогресс проекта (пересчитать на основе задач)

    Returns:
        {
            "success": true,
            "progress": 75,
            "message": "Прогресс обновлён"
        }
    """
    try:
        progress = update_project_progress(DB_PATH, project_id)

        if progress is None:
            return JSONResponse({
                "success": False,
                "message": "Ошибка обновления прогресса"
            }, status_code=500)

        return JSONResponse({
            "success": True,
            "progress": progress,
            "message": "Прогресс обновлён"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка обновления прогресса: {str(e)}"
        }, status_code=500)


@router.post("/api/projects/update-all-progress")
async def refresh_all_projects_progress(request: Request):
    """
    Обновить прогресс всех активных проектов

    Returns:
        {
            "success": true,
            "updated_count": 15,
            "message": "Обновлено проектов: 15"
        }
    """
    try:
        count = update_all_projects_progress(DB_PATH)

        return JSONResponse({
            "success": True,
            "updated_count": count,
            "message": f"Обновлено проектов: {count}"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка обновления прогресса: {str(e)}"
        }, status_code=500)


@router.get("/api/projects/{project_id}/tasks")
async def get_project_tasks(project_id: int, request: Request):
    """
    Получить список задач проекта (только задачи, без правок)

    Returns:
        {
            "success": true,
            "tasks": [
                {
                    "id": 1,
                    "title": "Задача 1",
                    "status": "completed",
                    "priority": "high",
                    ...
                }
            ]
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, description, status, priority, deadline, assigned_to_id, created_at
            FROM tasks
            WHERE project_id = ?
            AND (type = 'TASK' OR type IS NULL)
            ORDER BY created_at DESC
            """,
            (project_id,)
        )

        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "deadline": row[5],
                "assigned_to_id": row[6],
                "created_at": row[7],
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "tasks": tasks
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения задач: {str(e)}"
        }, status_code=500)


@router.get("/api/projects/{project_id}/revisions")
async def get_project_revisions(project_id: int, request: Request):
    """
    Получить список правок проекта (Task с type='REVISION')

    Returns:
        {
            "success": true,
            "revisions": [
                {
                    "id": 1,
                    "title": "Правка 1",
                    "status": "in_progress",
                    ...
                }
            ]
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, description, status, created_at, deadline, completed_at
            FROM tasks
            WHERE project_id = ?
            AND type = 'REVISION'
            ORDER BY created_at DESC
            """,
            (project_id,)
        )

        revisions = []
        for row in cursor.fetchall():
            revisions.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "created_at": row[4],
                "deadline": row[5],
                "completed_at": row[6],
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "revisions": revisions
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения правок: {str(e)}"
        }, status_code=500)
