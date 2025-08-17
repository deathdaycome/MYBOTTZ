"""
Простой роутер для сделок (временное решение)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import AdminUser
from ..auth import get_current_admin_user

router = APIRouter(prefix="/deals", tags=["deals"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def deals_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Страница сделок"""
    return templates.TemplateResponse(
        "deals.html",
        {
            "request": request,
            "user": current_user,
            "deals": [],
            "stats": {  # Добавляем статистику
                "total": 0,
                "active": 0,
                "total_amount": 0,
                "payment_progress": 0,
                "new": 0,
                "discussion": 0,
                "contract_signed": 0,
                "in_work": 0,
                "testing": 0,
                "payment": 0,
                "count": 0
            },
            "pipeline": {  # Добавляем данные пайплайна
                "new": [],
                "discussion": [],
                "contract": [],
                "in_work": [],
                "testing": [],
                "payment": []
            },
            "navigation_items": [
                {"name": "Дашборд", "url": "/dashboard", "icon": "fas fa-chart-line"},
                {"name": "Проекты", "url": "/projects", "icon": "fas fa-project-diagram"},
                {"name": "Клиенты", "url": "/clients", "icon": "fas fa-address-book"},
                {"name": "Лиды", "url": "/leads", "icon": "fas fa-user-check"},
                {"name": "Сделки", "url": "/deals", "icon": "fas fa-handshake", "active": True},
                {"name": "Финансы", "url": "/finance", "icon": "fas fa-chart-bar"},
            ]
        }
    )


@router.get("/api/list")
async def get_deals_api(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """API для получения списка сделок"""
    return {
        "success": True,
        "deals": [],
        "total": 0,
        "message": "Модуль сделок в разработке"
    }