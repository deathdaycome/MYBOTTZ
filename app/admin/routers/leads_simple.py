"""
Простой роутер для лидов (временное решение)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import AdminUser
from ..middleware.auth import get_current_admin_user
from ..navigation import get_navigation_items

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
            "stats": {  # Добавляем статистику
                "new": 0,
                "contact_made": 0,
                "qualification": 0,
                "proposal_sent": 0,
                "negotiation": 0,
                "won_month": 0,
                "lost_month": 0,
                "conversion_rate": 0
            },
            "navigation_items": get_navigation_items("/admin/leads")
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