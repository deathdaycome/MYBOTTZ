"""
API для управления документами, платежами и хостингом проектов
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3
import os
import json

router = APIRouter()

DB_PATH = os.getenv('DATABASE_PATH', '/app/data/bot.db')
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/bot.db'


# ==================== ДОКУМЕНТЫ ====================

@router.get("/api/projects/{project_id}/documents")
async def get_project_documents(project_id: int, request: Request):
    """
    Получить документы проекта

    Returns:
        {
            "success": true,
            "documents": [
                {
                    "id": 1,
                    "type": "contract",
                    "name": "Договор №123",
                    "status": "signed",
                    "date": "2025-12-01"
                }
            ]
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, type, name, number, file_path, file_size, file_type,
                   status, date, signed_at, description, created_at
            FROM documents
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,)
        )

        documents = []
        for row in cursor.fetchall():
            documents.append({
                "id": row[0],
                "type": row[1],
                "name": row[2],
                "number": row[3],
                "file_path": row[4],
                "file_size": row[5],
                "file_type": row[6],
                "status": row[7],
                "date": row[8],
                "signed_at": row[9],
                "description": row[10],
                "created_at": row[11]
            })

        conn.close()

        return JSONResponse({
            "success": True,
            "documents": documents
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения документов: {str(e)}"
        }, status_code=500)


@router.post("/api/projects/{project_id}/documents")
async def create_document(project_id: int, request: Request):
    """
    Создать документ проекта

    Body:
        {
            "type": "contract",
            "name": "Договор №123",
            "description": "Основной договор",
            "client_id": 1,
            "deal_id": 1
        }
    """
    try:
        body = await request.json()
        doc_type = body.get('type', 'other')
        name = body.get('name', '').strip()
        description = body.get('description', '')
        client_id = body.get('client_id')
        deal_id = body.get('deal_id')

        if not name:
            return JSONResponse({
                "success": False,
                "message": "Название документа не может быть пустым"
            }, status_code=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO documents (
                type, name, description, project_id, client_id, deal_id,
                status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'draft', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (doc_type, name, description, project_id, client_id, deal_id)
        )

        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "document": {
                "id": doc_id,
                "type": doc_type,
                "name": name,
                "project_id": project_id
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка создания документа: {str(e)}"
        }, status_code=500)


# ==================== ПЛАТЕЖИ ====================

@router.get("/api/projects/{project_id}/payments")
async def get_project_payments(project_id: int, request: Request):
    """
    Получить платежи проекта

    Returns:
        {
            "success": true,
            "payments": [
                {
                    "id": 1,
                    "type": "PREPAYMENT",
                    "amount": 50000,
                    "status": "PAID",
                    "due_date": "2025-12-10",
                    "paid_at": "2025-12-05"
                }
            ],
            "summary": {
                "total_amount": 100000,
                "paid_amount": 50000,
                "pending_amount": 50000
            }
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем платежи
        cursor.execute(
            """
            SELECT id, type, amount, status, due_date, paid_at, description, created_at
            FROM payments
            WHERE project_id = ?
            ORDER BY created_at ASC
            """,
            (project_id,)
        )

        payments = []
        total_amount = 0
        paid_amount = 0

        for row in cursor.fetchall():
            payment_data = {
                "id": row[0],
                "type": row[1],
                "amount": row[2],
                "status": row[3],
                "due_date": row[4],
                "paid_at": row[5],
                "description": row[6],
                "created_at": row[7]
            }
            payments.append(payment_data)

            total_amount += row[2]  # amount
            if row[3] == 'PAID':  # status
                paid_amount += row[2]

        conn.close()

        return JSONResponse({
            "success": True,
            "payments": payments,
            "summary": {
                "total_amount": total_amount,
                "paid_amount": paid_amount,
                "pending_amount": total_amount - paid_amount
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения платежей: {str(e)}"
        }, status_code=500)


@router.post("/api/projects/{project_id}/payments")
async def create_payment(project_id: int, request: Request):
    """
    Создать платеж проекта

    Body:
        {
            "type": "PREPAYMENT",  // PREPAYMENT, MILESTONE, FINAL, ADDITIONAL
            "amount": 50000,
            "due_date": "2025-12-10",
            "description": "Предоплата 50%",
            "client_id": 1,
            "deal_id": 1
        }
    """
    try:
        body = await request.json()
        payment_type = body.get('type', 'PREPAYMENT')
        amount = body.get('amount', 0)
        due_date = body.get('due_date')
        description = body.get('description', '')
        client_id = body.get('client_id')
        deal_id = body.get('deal_id')

        if amount <= 0:
            return JSONResponse({
                "success": False,
                "message": "Сумма платежа должна быть больше 0"
            }, status_code=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO payments (
                project_id, deal_id, client_id, type, amount, status,
                due_date, description, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, 'PLANNED', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (project_id, deal_id, client_id, payment_type, amount, due_date, description)
        )

        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "payment": {
                "id": payment_id,
                "type": payment_type,
                "amount": amount,
                "status": "PLANNED",
                "project_id": project_id
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка создания платежа: {str(e)}"
        }, status_code=500)


@router.patch("/api/payments/{payment_id}")
async def update_payment(payment_id: int, request: Request):
    """
    Обновить статус платежа

    Body:
        {
            "status": "PAID",
            "paid_at": "2025-12-05"
        }
    """
    try:
        body = await request.json()
        status = body.get('status')
        paid_at = body.get('paid_at')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        update_fields = []
        params = []

        if status:
            update_fields.append("status = ?")
            params.append(status)

        if paid_at:
            update_fields.append("paid_at = ?")
            params.append(paid_at)

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(payment_id)

        # Сначала получаем текущий платеж для проверки
        cursor.execute(
            "SELECT type, status, deal_id, amount, description FROM payments WHERE id = ?",
            (payment_id,)
        )
        payment_data = cursor.fetchone()

        if not payment_data:
            conn.close()
            return JSONResponse({
                "success": False,
                "message": "Платеж не найден"
            }, status_code=404)

        old_status = payment_data[1]
        payment_type = payment_data[0]
        deal_id = payment_data[2]

        # Обновляем платеж
        cursor.execute(
            f"UPDATE payments SET {', '.join(update_fields)} WHERE id = ?",
            params
        )

        # Автоматически создаём проект при получении предоплаты
        if (status == 'PAID' and old_status != 'PAID' and
            payment_type == 'PREPAYMENT' and deal_id):

            # Проверяем, нет ли уже проекта для этой сделки
            cursor.execute(
                "SELECT id FROM projects WHERE deal_id = ?",
                (deal_id,)
            )
            existing_project = cursor.fetchone()

            if not existing_project:
                # Получаем информацию о сделке
                cursor.execute(
                    "SELECT title, description, client_id, amount FROM deals WHERE id = ?",
                    (deal_id,)
                )
                deal_data = cursor.fetchone()

                if deal_data:
                    # Создаём новый проект
                    cursor.execute("""
                        INSERT INTO projects (
                            title, description, client_id, deal_id,
                            budget, status, progress,
                            created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, 'new', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        deal_data[0],  # title
                        f"Автоматически создано из сделки при получении предоплаты. {deal_data[1] or ''}",
                        deal_data[2],  # client_id
                        deal_id,
                        deal_data[3]  # amount as budget
                    ))

                    project_id = cursor.lastrowid
                    print(f"✅ Автоматически создан проект ID={project_id} из сделки ID={deal_id}")

        conn.commit()
        conn.close()

        return JSONResponse({
            "success": True,
            "message": "Платеж обновлен"
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка обновления платежа: {str(e)}"
        }, status_code=500)


# ==================== ХОСТИНГ ====================

@router.get("/api/projects/{project_id}/hosting")
async def get_project_hosting(project_id: int, request: Request):
    """
    Получить информацию о хостинге проекта

    Returns:
        {
            "success": true,
            "hosting": {
                "id": 1,
                "server_id": 1,
                "domain": "example.com",
                "ftp_login": "user123",
                "status": "active"
            }
        }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем есть ли таблица hosting_records
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='hosting_records'"
        )

        if not cursor.fetchone():
            conn.close()
            return JSONResponse({
                "success": True,
                "hosting": None,
                "message": "Таблица хостинга не создана"
            })

        cursor.execute(
            """
            SELECT hr.id, hr.server_id, hr.domain, hr.ftp_login, hr.status,
                   hr.created_at, hr.expires_at,
                   hs.server_name, hs.ip_address
            FROM hosting_records hr
            LEFT JOIN hosting_servers hs ON hr.server_id = hs.id
            WHERE hr.project_id = ?
            """,
            (project_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return JSONResponse({
                "success": True,
                "hosting": None
            })

        return JSONResponse({
            "success": True,
            "hosting": {
                "id": row[0],
                "server_id": row[1],
                "domain": row[2],
                "ftp_login": row[3],
                "status": row[4],
                "created_at": row[5],
                "expires_at": row[6],
                "server_name": row[7],
                "ip_address": row[8]
            }
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения хостинга: {str(e)}"
        }, status_code=500)
