"""
API для работы с чатами проектов
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import sqlite3
import os
from datetime import datetime
import json

router = APIRouter()

# Путь к БД
DB_PATH = os.getenv('DATABASE_PATH', '/app/data/bot.db')
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/bot.db'


@router.get("/api/projects/{project_id}/chat")
async def get_or_create_project_chat(project_id: int, request: Request):
    """
    Получить или создать чат проекта

    Returns:
        {
            "success": true,
            "chat": {
                "id": 1,
                "project_id": 1,
                "unread_by_executor": 0,
                "unread_by_client": 2
            }
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем существует ли чат
        cursor.execute(
            "SELECT id, project_id, unread_by_executor, unread_by_client, last_message_at FROM project_chats WHERE project_id = ?",
            (project_id,)
        )

        chat = cursor.fetchone()

        # Если чата нет - создаем
        if not chat:
            cursor.execute(
                """
                INSERT INTO project_chats (project_id, created_at, updated_at, unread_by_executor, unread_by_client)
                VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, 0)
                """,
                (project_id,)
            )
            conn.commit()
            chat_id = cursor.lastrowid

            conn.close()

            return JSONResponse({
                "success": True,
                "chat": {
                    "id": chat_id,
                    "project_id": project_id,
                    "unread_by_executor": 0,
                    "unread_by_client": 0,
                    "last_message_at": None
                }
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "chat": {
                "id": chat[0],
                "project_id": chat[1],
                "unread_by_executor": chat[2],
                "unread_by_client": chat[3],
                "last_message_at": chat[4]
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения чата: {str(e)}"
        }, status_code=500)


@router.get("/api/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: int, request: Request, limit: int = 50, offset: int = 0):
    """
    Получить сообщения чата

    Returns:
        {
            "success": true,
            "messages": [
                {
                    "id": 1,
                    "chat_id": 1,
                    "sender_type": "admin",
                    "sender_id": 1,
                    "author_name": "Админ",
                    "text": "Привет!",
                    "created_at": "2025-12-07 10:00:00",
                    "is_client": false,
                    "attachments": []
                }
            ]
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем сообщения с информацией об авторе
        cursor.execute(
            """
            SELECT
                pcm.id,
                pcm.chat_id,
                pcm.sender_type,
                pcm.sender_id,
                pcm.message_text,
                pcm.created_at,
                pcm.attachments,
                pcm.related_revision_id,
                CASE
                    WHEN pcm.sender_type = 'client' THEN u.first_name || ' ' || COALESCE(u.last_name, '')
                    WHEN pcm.sender_type = 'admin' THEN au.username
                    WHEN pcm.sender_type = 'executor' THEN eu.first_name || ' ' || COALESCE(eu.last_name, '')
                    ELSE 'Система'
                END as author_name
            FROM project_chat_messages pcm
            LEFT JOIN users u ON pcm.sender_type = 'client' AND pcm.sender_id = u.id
            LEFT JOIN admin_users au ON pcm.sender_type = 'admin' AND pcm.sender_id = au.id
            LEFT JOIN users eu ON pcm.sender_type = 'executor' AND pcm.sender_id = eu.id
            WHERE pcm.chat_id = ?
            ORDER BY pcm.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (chat_id, limit, offset)
        )

        messages = []
        for row in cursor.fetchall():
            attachments = []
            if row[6]:  # attachments field
                try:
                    attachments = json.loads(row[6])
                except:
                    pass

            messages.append({
                "id": row[0],
                "chat_id": row[1],
                "sender_type": row[2],
                "sender_id": row[3],
                "text": row[4],
                "created_at": row[5],
                "attachments": attachments,
                "related_revision_id": row[7],
                "author_name": row[8] or "Неизвестный",
                "is_client": row[2] == 'client'
            })

        conn.close()

        # Переворачиваем список чтобы новые сообщения были внизу
        messages.reverse()

        return JSONResponse({
            "success": True,
            "messages": messages
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения сообщений: {str(e)}"
        }, status_code=500)


@router.post("/api/chats/{chat_id}/messages")
async def send_message(chat_id: int, request: Request):
    """
    Отправить сообщение в чат

    Body:
        {
            "text": "Текст сообщения",
            "sender_type": "admin",
            "sender_id": 1,
            "attachments": []
        }

    Returns:
        {
            "success": true,
            "message": {
                "id": 1,
                "chat_id": 1,
                "text": "...",
                "created_at": "..."
            }
        }
    """
    try:
        body = await request.json()
        text = body.get('text', '').strip()
        sender_type = body.get('sender_type', 'admin')
        sender_id = body.get('sender_id', 1)
        attachments = body.get('attachments', [])

        if not text:
            return JSONResponse({
                "success": False,
                "message": "Текст сообщения не может быть пустым"
            }, status_code=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Создаем сообщение
        cursor.execute(
            """
            INSERT INTO project_chat_messages (
                chat_id,
                sender_type,
                sender_id,
                message_text,
                attachments,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (chat_id, sender_type, sender_id, text, json.dumps(attachments))
        )

        message_id = cursor.lastrowid

        # Обновляем время последнего сообщения в чате
        cursor.execute(
            """
            UPDATE project_chats
            SET last_message_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                unread_by_executor = CASE WHEN ? != 'executor' THEN unread_by_executor + 1 ELSE unread_by_executor END,
                unread_by_client = CASE WHEN ? != 'client' THEN unread_by_client + 1 ELSE unread_by_client END
            WHERE id = ?
            """,
            (sender_type, sender_type, chat_id)
        )

        conn.commit()

        # Получаем созданное сообщение
        cursor.execute(
            "SELECT id, chat_id, sender_type, sender_id, message_text, created_at FROM project_chat_messages WHERE id = ?",
            (message_id,)
        )

        msg = cursor.fetchone()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": {
                "id": msg[0],
                "chat_id": msg[1],
                "sender_type": msg[2],
                "sender_id": msg[3],
                "text": msg[4],
                "created_at": msg[5]
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка отправки сообщения: {str(e)}"
        }, status_code=500)


@router.post("/api/chats/{chat_id}/mark-read")
async def mark_messages_read(chat_id: int, request: Request):
    """
    Отметить сообщения чата как прочитанные

    Body:
        {
            "reader_type": "executor"  // "executor" or "client"
        }
    """
    try:
        body = await request.json()
        reader_type = body.get('reader_type', 'executor')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Обнуляем счетчик непрочитанных
        if reader_type == 'executor':
            cursor.execute(
                "UPDATE project_chats SET unread_by_executor = 0 WHERE id = ?",
                (chat_id,)
            )
            cursor.execute(
                "UPDATE project_chat_messages SET is_read_by_executor = 1, read_at = CURRENT_TIMESTAMP WHERE chat_id = ? AND is_read_by_executor = 0",
                (chat_id,)
            )
        else:
            cursor.execute(
                "UPDATE project_chats SET unread_by_client = 0 WHERE id = ?",
                (chat_id,)
            )
            cursor.execute(
                "UPDATE project_chat_messages SET is_read_by_client = 1, read_at = CURRENT_TIMESTAMP WHERE chat_id = ? AND is_read_by_client = 0",
                (chat_id,)
            )

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": "Сообщения отмечены как прочитанные"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка отметки сообщений: {str(e)}"
        }, status_code=500)


@router.post("/api/chats/messages/{message_id}/create-revision")
async def create_revision_from_message(message_id: int, request: Request):
    """
    Создать правку из сообщения чата

    Body:
        {
            "title": "Заголовок правки",
            "priority": "normal"
        }

    Returns:
        {
            "success": true,
            "revision": {
                "id": 1,
                "title": "...",
                "project_id": 1
            }
        }
    """
    try:
        body = await request.json()
        title = body.get('title', '').strip()
        priority = body.get('priority', 'normal')

        if not title:
            return JSONResponse({
                "success": False,
                "message": "Заголовок правки не может быть пустым"
            }, status_code=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем сообщение и информацию о чате
        cursor.execute(
            """
            SELECT pcm.message_text, pcm.chat_id, pc.project_id, pcm.sender_id
            FROM project_chat_messages pcm
            JOIN project_chats pc ON pcm.chat_id = pc.id
            WHERE pcm.id = ?
            """,
            (message_id,)
        )

        msg_data = cursor.fetchone()

        if not msg_data:
            conn.close()
            return JSONResponse({
                "success": False,
                "message": "Сообщение не найдено"
            }, status_code=404)

        message_text, chat_id, project_id, sender_id = msg_data

        # Создаем правку (Task с type='REVISION')
        cursor.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                status,
                priority,
                assigned_to_id,
                created_by_id,
                created_at,
                updated_at,
                type,
                project_id
            )
            VALUES (?, ?, 'pending', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'REVISION', ?)
            """,
            (title, message_text, priority, sender_id, sender_id, project_id)
        )

        revision_id = cursor.lastrowid

        # Связываем сообщение с правкой
        cursor.execute(
            "UPDATE project_chat_messages SET related_revision_id = ? WHERE id = ?",
            (revision_id, message_id)
        )

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "revision": {
                "id": revision_id,
                "title": title,
                "description": message_text,
                "project_id": project_id,
                "message": "Правка успешно создана из сообщения"
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка создания правки: {str(e)}"
        }, status_code=500)
