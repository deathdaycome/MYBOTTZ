from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Settings, AdminUser
from app.admin.middleware.auth import get_current_admin_user
from app.config.settings import settings
from datetime import datetime
from typing import Dict, Any

router = APIRouter(tags=["admin_settings"])
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user: dict = Depends(get_current_admin_user)):
    """Страница настроек"""
    # Получаем элементы навигации
    from app.admin.app import get_navigation_items
    navigation_items = get_navigation_items(user['role'])
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": user,
        "username": user['username'],
        "user_role": user['role'],
        "navigation_items": navigation_items
    })

@router.get("/api/settings", response_class=JSONResponse)
async def get_settings(db: Session = Depends(get_db), user: dict = Depends(get_current_admin_user)):
    """Получить все настройки"""
    try:
        settings_data = db.query(Settings).all()
        
        # Группируем настройки по категориям
        categorized_settings = {}
        for setting in settings_data:
            if setting.category not in categorized_settings:
                categorized_settings[setting.category] = []
            categorized_settings[setting.category].append(setting.to_dict())
        
        # Добавляем системные настройки
        system_settings = {
            "ai": {
                "openai_api_key": settings.OPENAI_API_KEY[:10] + "..." if settings.OPENAI_API_KEY else "Не установлен",
                "openai_model": getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                "bot_token": settings.BOT_TOKEN[:10] + "..." if settings.BOT_TOKEN else "Не установлен",
            }
        }
        
        return JSONResponse({
            "success": True,
            "data": categorized_settings,
            "system": system_settings
        })
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.post("/api/settings", response_class=JSONResponse)
async def update_settings(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Обновить настройки"""
    try:
        data = await request.json()
        
        for key, value in data.items():
            setting = db.query(Settings).filter(Settings.setting_key == key).first()
            if setting:
                setting.setting_value = str(value)
                setting.updated_at = datetime.utcnow()
                setting.updated_by_id = user["id"]
        
        db.commit()
        
        return JSONResponse({
            "success": True,
            "message": "Настройки обновлены"
        })
    
    except Exception as e:
        db.rollback()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)
