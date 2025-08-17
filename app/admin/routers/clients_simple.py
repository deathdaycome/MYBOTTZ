"""
Простой роутер для клиентов (временное решение)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from ...database.database import get_db
from ...database.models import AdminUser
from ..auth import get_current_admin_user
from ..navigation import get_navigation_items

router = APIRouter(prefix="/clients", tags=["clients"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def clients_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Страница клиентов"""
    try:
        # Пока просто возвращаем базовую страницу
        return templates.TemplateResponse(
            "clients.html",
            {
                "request": request,
                "user": current_user,
                "clients": [],  # Пустой список пока
                "stats": {  # Добавляем статистику
                    "total": 0,
                    "active": 0,
                    "vip": 0,
                    "new_month": 0
                },
                "navigation_items": get_navigation_items("/admin/clients")
            }
        )
    except Exception as e:
        return f"Ошибка загрузки страницы клиентов: {e}"


@router.get("/api/list")
async def get_clients_api(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """API для получения списка клиентов"""
    return {
        "success": True,
        "clients": [],
        "total": 0,
        "message": "Модуль клиентов в разработке"
    }