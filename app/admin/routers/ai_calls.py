"""
API для управления AI-звонками
Привязка к Lead/Deal/Project
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3
import os
import json

router = APIRouter()

# Путь к БД
DB_PATH = os.getenv('DATABASE_PATH', '/app/data/bot.db')
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/bot.db'


@router.get("/api/ai-calls")
async def get_ai_calls(request: Request):
    """
    Получить список AI-звонков с фильтрацией

    Query params:
        lead_id: ID лида
        deal_id: ID сделки
        project_id: ID проекта

    Returns:
        {
            "success": true,
            "ai_calls": [
                {
                    "id": 1,
                    "dialog_text": "...",
                    "ai_tips": {...},
                    "summary": "...",
                    "lead_id": 1,
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

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Базовый запрос
        query = """
            SELECT id, lead_id, deal_id, project_id,
                   dialog_text, ai_tips, summary,
                   created_by, created_at
            FROM ai_calls
            WHERE 1=1
        """
        params = []

        # Добавляем фильтры
        if lead_id:
            query += " AND lead_id = ?"
            params.append(lead_id)

        if deal_id:
            query += " AND deal_id = ?"
            params.append(deal_id)

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)

        ai_calls = []
        for row in cursor.fetchall():
            # Парсим JSON поле ai_tips
            ai_tips = None
            if row[5]:
                try:
                    ai_tips = json.loads(row[5])
                except:
                    ai_tips = row[5]

            ai_calls.append({
                "id": row[0],
                "lead_id": row[1],
                "deal_id": row[2],
                "project_id": row[3],
                "dialog_text": row[4],
                "ai_tips": ai_tips,
                "summary": row[6],
                "created_by": row[7],
                "created_at": row[8]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "ai_calls": ai_calls,
            "total": len(ai_calls)
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения AI-звонков: {str(e)}"
        }, status_code=500)


@router.post("/api/ai-calls")
async def create_ai_call(request: Request):
    """
    Создать запись AI-звонка

    Body:
        {
            "dialog_text": "Диалог с клиентом...",
            "ai_tips": {"tips": ["Совет 1", "Совет 2"]},
            "summary": "Краткое содержание звонка",
            "lead_id": 1,
            "deal_id": null,
            "project_id": null,
            "created_by": 1
        }

    Returns:
        {
            "success": true,
            "ai_call": {"id": 1, ...}
        }
    """
    try:
        body = await request.json()

        dialog_text = body.get('dialog_text', '')
        ai_tips = body.get('ai_tips')
        summary = body.get('summary', '')
        lead_id = body.get('lead_id')
        deal_id = body.get('deal_id')
        project_id = body.get('project_id')
        created_by = body.get('created_by')

        if not dialog_text:
            return JSONResponse({
                "success": False,
                "message": "Текст диалога не может быть пустым"
            }, status_code=400)

        # Конвертируем ai_tips в JSON string
        ai_tips_json = None
        if ai_tips:
            ai_tips_json = json.dumps(ai_tips, ensure_ascii=False)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO ai_calls (
                lead_id, deal_id, project_id,
                dialog_text, ai_tips, summary,
                created_by, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (lead_id, deal_id, project_id, dialog_text, ai_tips_json, summary, created_by)
        )

        ai_call_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "ai_call": {
                "id": ai_call_id,
                "dialog_text": dialog_text,
                "ai_tips": ai_tips,
                "summary": summary,
                "lead_id": lead_id,
                "deal_id": deal_id,
                "project_id": project_id
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка создания AI-звонка: {str(e)}"
        }, status_code=500)


@router.patch("/api/ai-calls/{ai_call_id}")
async def update_ai_call(ai_call_id: int, request: Request):
    """
    Обновить привязку AI-звонка к сущностям

    Body:
        {
            "lead_id": 1,
            "deal_id": 2,
            "project_id": null,
            "summary": "Обновленное резюме"
        }

    Returns:
        {
            "success": true,
            "message": "AI-звонок обновлен"
        }
    """
    try:
        body = await request.json()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        update_fields = []
        params = []

        if 'lead_id' in body:
            update_fields.append("lead_id = ?")
            params.append(body['lead_id'])

        if 'deal_id' in body:
            update_fields.append("deal_id = ?")
            params.append(body['deal_id'])

        if 'project_id' in body:
            update_fields.append("project_id = ?")
            params.append(body['project_id'])

        if 'summary' in body:
            update_fields.append("summary = ?")
            params.append(body['summary'])

        if 'ai_tips' in body:
            ai_tips_json = json.dumps(body['ai_tips'], ensure_ascii=False)
            update_fields.append("ai_tips = ?")
            params.append(ai_tips_json)

        if not update_fields:
            return JSONResponse({
                "success": False,
                "message": "Нет полей для обновления"
            }, status_code=400)

        params.append(ai_call_id)

        cursor.execute(
            f"UPDATE ai_calls SET {', '.join(update_fields)} WHERE id = ?",
            params
        )

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": "AI-звонок обновлен"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка обновления AI-звонка: {str(e)}"
        }, status_code=500)


@router.delete("/api/ai-calls/{ai_call_id}")
async def delete_ai_call(ai_call_id: int, request: Request):
    """
    Удалить AI-звонок

    Returns:
        {
            "success": true,
            "message": "AI-звонок удален"
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM ai_calls WHERE id = ?", (ai_call_id,))

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": "AI-звонок удален"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка удаления AI-звонка: {str(e)}"
        }, status_code=500)


@router.get("/api/leads/{lead_id}/ai-calls")
async def get_lead_ai_calls(lead_id: int, request: Request):
    """
    Получить все AI-звонки лида

    Returns:
        {
            "success": true,
            "ai_calls": [...]
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, dialog_text, ai_tips, summary, created_at
            FROM ai_calls
            WHERE lead_id = ?
            ORDER BY created_at DESC
            """,
            (lead_id,)
        )

        ai_calls = []
        for row in cursor.fetchall():
            ai_tips = None
            if row[2]:
                try:
                    ai_tips = json.loads(row[2])
                except:
                    ai_tips = row[2]

            ai_calls.append({
                "id": row[0],
                "dialog_text": row[1],
                "ai_tips": ai_tips,
                "summary": row[3],
                "created_at": row[4]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "ai_calls": ai_calls
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения AI-звонков: {str(e)}"
        }, status_code=500)


@router.get("/api/deals/{deal_id}/ai-calls")
async def get_deal_ai_calls(deal_id: int, request: Request):
    """
    Получить все AI-звонки сделки
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, dialog_text, ai_tips, summary, created_at
            FROM ai_calls
            WHERE deal_id = ?
            ORDER BY created_at DESC
            """,
            (deal_id,)
        )

        ai_calls = []
        for row in cursor.fetchall():
            ai_tips = None
            if row[2]:
                try:
                    ai_tips = json.loads(row[2])
                except:
                    ai_tips = row[2]

            ai_calls.append({
                "id": row[0],
                "dialog_text": row[1],
                "ai_tips": ai_tips,
                "summary": row[3],
                "created_at": row[4]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "ai_calls": ai_calls
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения AI-звонков: {str(e)}"
        }, status_code=500)


@router.get("/api/projects/{project_id}/ai-calls")
async def get_project_ai_calls(project_id: int, request: Request):
    """
    Получить все AI-звонки проекта
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, dialog_text, ai_tips, summary, created_at
            FROM ai_calls
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,)
        )

        ai_calls = []
        for row in cursor.fetchall():
            ai_tips = None
            if row[2]:
                try:
                    ai_tips = json.loads(row[2])
                except:
                    ai_tips = row[2]

            ai_calls.append({
                "id": row[0],
                "dialog_text": row[1],
                "ai_tips": ai_tips,
                "summary": row[3],
                "created_at": row[4]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "ai_calls": ai_calls
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения AI-звонков: {str(e)}"
        }, status_code=500)
