"""
Простой роутер для лидов (временное решение)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import AdminUser
from ..auth import get_current_admin_user

router = APIRouter(prefix="/leads", tags=["leads"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def leads_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Страница лидов"""
    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "user": current_user,
            "leads": [],
            "navigation_items": [
                {"name": "Дашборд", "url": "/dashboard", "icon": "fas fa-chart-line"},
                {"name": "Проекты", "url": "/projects", "icon": "fas fa-project-diagram"},
                {"name": "Клиенты", "url": "/clients", "icon": "fas fa-address-book"},
                {"name": "Лиды", "url": "/leads", "icon": "fas fa-user-check", "active": True},
                {"name": "Сделки", "url": "/deals", "icon": "fas fa-handshake"},
                {"name": "Финансы", "url": "/finance", "icon": "fas fa-chart-bar"},
            ]
        }
    )


@router.get("/api/list")
async def get_leads_api(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """API для получения списка лидов"""
    return {
        "success": True,
        "leads": [],
        "total": 0,
        "message": "Модуль лидов в разработке"
    }