from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Settings, AdminUser
from app.admin.middleware.auth import require_admin_auth
from app.config.settings import settings
import json
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/admin", tags=["admin_settings"])
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user: AdminUser = Depends(require_admin_auth)):
    """Страница настроек"""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": user
    })

@router.get("/api/settings", response_class=JSONResponse)
async def get_settings(db: Session = Depends(get_db), user: AdminUser = Depends(require_admin_auth)):
    """Получить все настройки"""
    try:
        settings_data = db.query(Settings).all()
        
        # Группируем настройки по категориям
        categorized_settings = {}
        for setting in settings_data:
            if setting.category not in categorized_settings:
                categorized_settings[setting.category] = []
            categorized_settings[setting.category].append(setting.to_dict())
        
        return JSONResponse({
            "success": True,
            "data": categorized_settings
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
    user: AdminUser = Depends(require_admin_auth)
):
    """Обновить настройки"""
    try:
        data = await request.json()
        
        for key, value in data.items():
            setting = db.query(Settings).filter(Settings.setting_key == key).first()
            if setting:
                setting.setting_value = str(value)
                setting.updated_at = datetime.utcnow()
                setting.updated_by_id = user.id
        
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
            "database": {
                "database_url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else "Не установлен",
                "database_type": "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL",
            },
            "notifications": {
                "email_notifications": getattr(settings, 'EMAIL_NOTIFICATIONS', True),
                "telegram_notifications": getattr(settings, 'TELEGRAM_NOTIFICATIONS', True),
                "notification_delay": getattr(settings, 'NOTIFICATION_DELAY', 5),
            },
            "security": {
                "admin_password_hash": "Установлен" if getattr(settings, 'ADMIN_PASSWORD_HASH', None) else "Не установлен",
                "session_timeout": getattr(settings, 'SESSION_TIMEOUT', 3600),
                "max_login_attempts": getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5),
            },
            "pricing": {
                "default_hourly_rate": getattr(settings, 'DEFAULT_HOURLY_RATE', 2000),
                "currency": getattr(settings, 'CURRENCY', 'RUB'),
                "tax_rate": getattr(settings, 'TAX_RATE', 0.13),
                "min_project_cost": getattr(settings, 'MIN_PROJECT_COST', 5000),
            }
        }
        
        return {
            "success": True,
            "settings": categorized_settings,
            "system_settings": system_settings
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении настроек: {str(e)}"
        }

@router.post("/api/settings", response_class=JSONResponse)
async def save_settings(
    request: Request,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Сохранить настройки"""
    try:
        data = await request.json()
        
        for category, settings_group in data.items():
            if category == "system_settings":
                continue  # Системные настройки обрабатываются отдельно
                
            for setting_key, setting_value in settings_group.items():
                # Проверяем, существует ли настройка
                existing_setting = db.query(FinanceSettings).filter_by(setting_key=setting_key).first()
                
                if existing_setting:
                    # Обновляем существующую настройку
                    existing_setting.setting_value = setting_value
                    existing_setting.updated_at = datetime.utcnow()
                    existing_setting.updated_by_id = user.id
                else:
                    # Создаем новую настройку
                    new_setting = FinanceSettings(
                        setting_key=setting_key,
                        setting_value=setting_value,
                        category=category,
                        updated_by_id=user.id
                    )
                    db.add(new_setting)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Настройки успешно сохранены"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при сохранении настроек: {str(e)}"
        }

@router.post("/api/settings/reset", response_class=JSONResponse)
async def reset_settings(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Сбросить настройки к значениям по умолчанию"""
    try:
        # Удаляем все пользовательские настройки (кроме системных)
        db.query(FinanceSettings).filter(FinanceSettings.is_system == False).delete()
        
        # Добавляем настройки по умолчанию
        default_settings = [
            {
                "setting_key": "default_currency",
                "setting_value": "RUB",
                "category": "general",
                "description": "Валюта по умолчанию"
            },
            {
                "setting_key": "tax_rate",
                "setting_value": 0.13,
                "category": "tax",
                "description": "Налоговая ставка"
            },
            {
                "setting_key": "default_hourly_rate",
                "setting_value": 2000,
                "category": "pricing",
                "description": "Базовая ставка за час"
            },
            {
                "setting_key": "auto_notifications",
                "setting_value": True,
                "category": "notifications",
                "description": "Автоматические уведомления"
            },
            {
                "setting_key": "backup_frequency",
                "setting_value": "daily",
                "category": "system",
                "description": "Частота резервного копирования"
            }
        ]
        
        for setting_data in default_settings:
            new_setting = FinanceSettings(
                setting_key=setting_data["setting_key"],
                setting_value=setting_data["setting_value"],
                description=setting_data["description"],
                category=setting_data["category"],
                updated_by_id=user.id
            )
            db.add(new_setting)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Настройки сброшены к значениям по умолчанию"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при сбросе настроек: {str(e)}"
        }

@router.get("/api/settings/export", response_class=JSONResponse)
async def export_settings(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Экспортировать настройки"""
    try:
        settings_data = db.query(FinanceSettings).all()
        
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "exported_by": user.username,
            "settings": [setting.to_dict() for setting in settings_data]
        }
        
        return {
            "success": True,
            "data": export_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при экспорте настроек: {str(e)}"
        }

@router.post("/api/settings/import", response_class=JSONResponse)
async def import_settings(
    request: Request,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Импортировать настройки"""
    try:
        data = await request.json()
        
        if "settings" not in data:
            return {
                "success": False,
                "message": "Неверный формат данных для импорта"
            }
        
        imported_count = 0
        
        for setting_data in data["settings"]:
            if setting_data.get("is_system", False):
                continue  # Пропускаем системные настройки
                
            # Проверяем, существует ли настройка
            existing_setting = db.query(FinanceSettings).filter_by(
                setting_key=setting_data["setting_key"]
            ).first()
            
            if existing_setting:
                # Обновляем существующую настройку
                existing_setting.setting_value = setting_data["setting_value"]
                existing_setting.description = setting_data.get("description")
                existing_setting.category = setting_data.get("category", "general")
                existing_setting.updated_at = datetime.utcnow()
                existing_setting.updated_by_id = user.id
            else:
                # Создаем новую настройку
                new_setting = FinanceSettings(
                    setting_key=setting_data["setting_key"],
                    setting_value=setting_data["setting_value"],
                    description=setting_data.get("description"),
                    category=setting_data.get("category", "general"),
                    updated_by_id=user.id
                )
                db.add(new_setting)
            
            imported_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Импортировано {imported_count} настроек"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при импорте настроек: {str(e)}"
        }

@router.get("/api/settings/validate", response_class=JSONResponse)
async def validate_settings(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Проверить валидность настроек"""
    try:
        validation_results = []
        
        # Проверяем основные настройки
        required_settings = [
            "default_currency",
            "tax_rate",
            "default_hourly_rate"
        ]
        
        for setting_key in required_settings:
            setting = db.query(FinanceSettings).filter_by(setting_key=setting_key).first()
            if not setting:
                validation_results.append({
                    "setting": setting_key,
                    "status": "missing",
                    "message": f"Отсутствует обязательная настройка: {setting_key}"
                })
            else:
                validation_results.append({
                    "setting": setting_key,
                    "status": "ok",
                    "message": "Настройка корректна"
                })
        
        # Проверяем системные настройки
        system_checks = [
            {
                "name": "BOT_TOKEN",
                "value": settings.BOT_TOKEN,
                "required": True
            },
            {
                "name": "OPENAI_API_KEY",
                "value": settings.OPENAI_API_KEY,
                "required": False
            },
            {
                "name": "DATABASE_URL",
                "value": settings.DATABASE_URL,
                "required": True
            }
        ]
        
        for check in system_checks:
            if check["required"] and not check["value"]:
                validation_results.append({
                    "setting": check["name"],
                    "status": "error",
                    "message": f"Отсутствует обязательная системная настройка: {check['name']}"
                })
            elif check["value"]:
                validation_results.append({
                    "setting": check["name"],
                    "status": "ok",
                    "message": "Системная настройка корректна"
                })
        
        # Подсчитываем статистику
        total_checks = len(validation_results)
        ok_checks = len([r for r in validation_results if r["status"] == "ok"])
        error_checks = len([r for r in validation_results if r["status"] == "error"])
        missing_checks = len([r for r in validation_results if r["status"] == "missing"])
        
        return {
            "success": True,
            "validation_results": validation_results,
            "statistics": {
                "total": total_checks,
                "ok": ok_checks,
                "errors": error_checks,
                "missing": missing_checks
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при валидации настроек: {str(e)}"
        }
