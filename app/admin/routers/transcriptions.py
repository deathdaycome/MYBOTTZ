"""
API для управления транскрибациями
Привязка к Lead/Deal/Project
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3
import os

router = APIRouter()

# Путь к БД
DB_PATH = os.getenv('DATABASE_PATH', '/app/data/bot.db')
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/bot.db'


@router.get("/api/transcriptions")
async def get_transcriptions(request: Request):
    """
    Получить список транскрибаций с фильтрацией

    Query params:
        lead_id: ID лида
        deal_id: ID сделки
        project_id: ID проекта
        source_type: Тип источника (audio, video)

    Returns:
        {
            "success": true,
            "transcriptions": [
                {
                    "id": 1,
                    "text": "...",
                    "source_type": "audio",
                    "linked_lead_id": 1,
                    "created_at": "2025-12-07"
                }
            ]
        }
    """
    try:
        # Получаем параметры фильтрации
        lead_id = request.query_params.get('lead_id')
        deal_id = request.query_params.get('deal_id')
        project_id = request.query_params.get('project_id')
        source_type = request.query_params.get('source_type')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Базовый запрос
        query = """
            SELECT id, source_type, file_path, text,
                   linked_lead_id, linked_deal_id, linked_project_id,
                   created_by, created_at
            FROM transcriptions
            WHERE 1=1
        """
        params = []

        # Добавляем фильтры
        if lead_id:
            query += " AND linked_lead_id = ?"
            params.append(lead_id)

        if deal_id:
            query += " AND linked_deal_id = ?"
            params.append(deal_id)

        if project_id:
            query += " AND linked_project_id = ?"
            params.append(project_id)

        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)

        transcriptions = []
        for row in cursor.fetchall():
            transcriptions.append({
                "id": row[0],
                "source_type": row[1],
                "file_path": row[2],
                "text": row[3],
                "linked_lead_id": row[4],
                "linked_deal_id": row[5],
                "linked_project_id": row[6],
                "created_by": row[7],
                "created_at": row[8]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "transcriptions": transcriptions,
            "total": len(transcriptions)
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения транскрибаций: {str(e)}"
        }, status_code=500)


@router.post("/api/transcriptions")
async def create_transcription(request: Request):
    """
    Создать запись транскрибации

    Body:
        {
            "text": "Текст транскрибации",
            "source_type": "audio",
            "file_path": "/path/to/file",
            "linked_lead_id": 1,
            "linked_deal_id": null,
            "linked_project_id": null,
            "created_by": 1
        }

    Returns:
        {
            "success": true,
            "transcription": {"id": 1, ...}
        }
    """
    try:
        body = await request.json()

        text = body.get('text', '')
        source_type = body.get('source_type', 'audio')
        file_path = body.get('file_path', '')
        linked_lead_id = body.get('linked_lead_id')
        linked_deal_id = body.get('linked_deal_id')
        linked_project_id = body.get('linked_project_id')
        created_by = body.get('created_by')

        if not text:
            return JSONResponse({
                "success": False,
                "message": "Текст транскрибации не может быть пустым"
            }, status_code=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO transcriptions (
                source_type, file_path, text,
                linked_lead_id, linked_deal_id, linked_project_id,
                created_by, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (source_type, file_path, text, linked_lead_id, linked_deal_id,
             linked_project_id, created_by)
        )

        transcription_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "transcription": {
                "id": transcription_id,
                "text": text,
                "source_type": source_type,
                "linked_lead_id": linked_lead_id,
                "linked_deal_id": linked_deal_id,
                "linked_project_id": linked_project_id
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка создания транскрибации: {str(e)}"
        }, status_code=500)


@router.patch("/api/transcriptions/{transcription_id}")
async def update_transcription(transcription_id: int, request: Request):
    """
    Обновить привязку транскрибации к сущностям

    Body:
        {
            "linked_lead_id": 1,
            "linked_deal_id": 2,
            "linked_project_id": null
        }

    Returns:
        {
            "success": true,
            "message": "Транскрибация обновлена"
        }
    """
    try:
        body = await request.json()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        update_fields = []
        params = []

        if 'linked_lead_id' in body:
            update_fields.append("linked_lead_id = ?")
            params.append(body['linked_lead_id'])

        if 'linked_deal_id' in body:
            update_fields.append("linked_deal_id = ?")
            params.append(body['linked_deal_id'])

        if 'linked_project_id' in body:
            update_fields.append("linked_project_id = ?")
            params.append(body['linked_project_id'])

        if not update_fields:
            return JSONResponse({
                "success": False,
                "message": "Нет полей для обновления"
            }, status_code=400)

        params.append(transcription_id)

        cursor.execute(
            f"UPDATE transcriptions SET {', '.join(update_fields)} WHERE id = ?",
            params
        )

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": "Транскрибация обновлена"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка обновления транскрибации: {str(e)}"
        }, status_code=500)


@router.delete("/api/transcriptions/{transcription_id}")
async def delete_transcription(transcription_id: int, request: Request):
    """
    Удалить транскрибацию

    Returns:
        {
            "success": true,
            "message": "Транскрибация удалена"
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM transcriptions WHERE id = ?", (transcription_id,))

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": "Транскрибация удалена"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка удаления транскрибации: {str(e)}"
        }, status_code=500)


@router.get("/api/leads/{lead_id}/transcriptions")
async def get_lead_transcriptions(lead_id: int, request: Request):
    """
    Получить все транскрибации лида

    Returns:
        {
            "success": true,
            "transcriptions": [...]
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, source_type, text, file_path, created_at
            FROM transcriptions
            WHERE linked_lead_id = ?
            ORDER BY created_at DESC
            """,
            (lead_id,)
        )

        transcriptions = []
        for row in cursor.fetchall():
            transcriptions.append({
                "id": row[0],
                "source_type": row[1],
                "text": row[2],
                "file_path": row[3],
                "created_at": row[4]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "transcriptions": transcriptions
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения транскрибаций: {str(e)}"
        }, status_code=500)


@router.get("/api/deals/{deal_id}/transcriptions")
async def get_deal_transcriptions(deal_id: int, request: Request):
    """
    Получить все транскрибации сделки
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, source_type, text, file_path, created_at
            FROM transcriptions
            WHERE linked_deal_id = ?
            ORDER BY created_at DESC
            """,
            (deal_id,)
        )

        transcriptions = []
        for row in cursor.fetchall():
            transcriptions.append({
                "id": row[0],
                "source_type": row[1],
                "text": row[2],
                "file_path": row[3],
                "created_at": row[4]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "transcriptions": transcriptions
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения транскрибаций: {str(e)}"
        }, status_code=500)


@router.get("/api/projects/{project_id}/transcriptions")
async def get_project_transcriptions(project_id: int, request: Request):
    """
    Получить все транскрибации проекта
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, source_type, text, file_path, created_at
            FROM transcriptions
            WHERE linked_project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,)
        )

        transcriptions = []
        for row in cursor.fetchall():
            transcriptions.append({
                "id": row[0],
                "source_type": row[1],
                "text": row[2],
                "file_path": row[3],
                "created_at": row[4]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "transcriptions": transcriptions
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения транскрибаций: {str(e)}"
        }, status_code=500)
