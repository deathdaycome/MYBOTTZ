"""
Простой роутер для финансов (временное решение)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import AdminUser
from ..middleware.auth import get_current_admin_user
from ..navigation import get_navigation_items

router = APIRouter(prefix="/finance", tags=["finance"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def finance_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Страница финансов"""
    return templates.TemplateResponse(
        "finance.html",
        {
            "request": request,
            "user": current_user,
            "transactions": [],
            "stats": {  # Добавляем статистику
                "income": 0,
                "expenses": 0,
                "balance": 0,
                "pending": 0
            },
            "navigation_items": get_navigation_items("/admin/finance")
        }
    )


@router.get("/api/list")
async def get_finance_api(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """API для получения финансовых данных"""
    return {
        "success": True,
        "transactions": [],
        "total": 0,
        "message": "Модуль финансов в разработке"
    }