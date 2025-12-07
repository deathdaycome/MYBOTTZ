"""
Роутер для управления регламентами тимлида
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ...database.database import get_db
from ...database.models import AdminUser
from ..middleware.auth import get_current_admin_user
from ...config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/timlead-regulations", tags=["timlead-regulations"])


class RegulationResponse(BaseModel):
    id: int
    regulation_number: int
    title: str
    content: Optional[str]
    icon: str
    allowed_roles: List[str] = []
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RegulationUpdateRequest(BaseModel):
    title: str
    content: str
    icon: str
    allowed_roles: List[str] = []


@router.get("/", response_model=List[RegulationResponse])
async def get_all_regulations(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить регламенты доступные для роли пользователя
    """
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role

    try:
        # Получаем все регламенты из БД с allowed_roles
        cursor = db.execute(text("""
            SELECT id, regulation_number, title, content, icon,
                   allowed_roles, created_at, updated_at
            FROM timlead_regulations
            ORDER BY regulation_number
        """))

        regulations = []
        for row in cursor.fetchall():
            allowed_roles_str = row[5] or "[]"

            # Парсим JSON строку allowed_roles
            import json
            try:
                allowed_roles = json.loads(allowed_roles_str)
            except:
                allowed_roles = []

            # Фильтруем: показываем регламент только если роль пользователя в allowed_roles
            # Или если allowed_roles пустой (для обратной совместимости)
            # Или если пользователь - owner (владелец видит все)
            if user_role == "owner" or not allowed_roles or user_role in allowed_roles:
                regulations.append({
                    "id": row[0],
                    "regulation_number": row[1],
                    "title": row[2],
                    "content": row[3] or "",
                    "icon": row[4],
                    "allowed_roles": allowed_roles,
                    "created_at": row[6],
                    "updated_at": row[7]
                })

        return regulations

    except Exception as e:
        logger.error(f"Error fetching regulations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{regulation_id}", response_model=RegulationResponse)
async def get_regulation(
    regulation_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить конкретный регламент
    Доступно для: owner, timlead
    """
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ["owner", "timlead"]:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    try:
        cursor = db.execute(text("""
            SELECT id, regulation_number, title, content, icon,
                   created_at, updated_at
            FROM timlead_regulations
            WHERE id = :regulation_id
        """), {"regulation_id": regulation_id})

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Регламент не найден")

        return {
            "id": row[0],
            "regulation_number": row[1],
            "title": row[2],
            "content": row[3] or "",
            "icon": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching regulation {regulation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{regulation_id}")
async def update_regulation(
    regulation_id: int,
    regulation_data: RegulationUpdateRequest,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Обновить регламент
    Доступно только для: owner
    """
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Только владелец может редактировать регламенты"
        )

    try:
        # Проверяем, существует ли регламент
        cursor = db.execute(text("""
            SELECT id FROM timlead_regulations WHERE id = :regulation_id
        """), {"regulation_id": regulation_id})

        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Регламент не найден")

        # Обновляем регламент
        import json
        allowed_roles_json = json.dumps(regulation_data.allowed_roles)

        db.execute(text("""
            UPDATE timlead_regulations
            SET title = :title,
                content = :content,
                icon = :icon,
                allowed_roles = :allowed_roles,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :regulation_id
        """), {
            "title": regulation_data.title,
            "content": regulation_data.content,
            "icon": regulation_data.icon,
            "allowed_roles": allowed_roles_json,
            "regulation_id": regulation_id
        })

        db.commit()

        username = current_user.get("username") if isinstance(current_user, dict) else current_user.username
        logger.info(f"Regulation {regulation_id} updated by {username}")

        return JSONResponse(
            status_code=200,
            content={"message": "Регламент успешно обновлен"}
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating regulation {regulation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
