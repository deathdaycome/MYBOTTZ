from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets

from ...database.database import get_db_context
from ...database.models import AdminUser
from ...config.settings import settings
from ...services.auth_service import AuthService

security = HTTPBasic()

def require_admin_auth(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """Требует аутентификации администратора"""
    # Проверяем основного владельца
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if correct_username and correct_password:
        # Ищем администратора в базе данных
        try:
            with get_db_context() as db:
                admin_user = db.query(AdminUser).filter(
                    AdminUser.username == settings.ADMIN_USERNAME,
                    AdminUser.role == "owner"
                ).first()
                
                if admin_user:
                    # Возвращаем словарь с данными пользователя
                    return {
                        "id": admin_user.id,
                        "username": admin_user.username,
                        "email": admin_user.email,
                        "first_name": admin_user.first_name,
                        "last_name": admin_user.last_name,
                        "role": admin_user.role,
                        "is_active": admin_user.is_active
                    }
                else:
                    # Если не найден в БД, создаем виртуального админа
                    return {
                        "id": 1,
                        "username": settings.ADMIN_USERNAME,
                        "email": "admin@example.com",
                        "first_name": "Администратор",
                        "last_name": "",
                        "role": "owner",
                        "is_active": True
                    }
        except Exception:
            # Fallback - создаем виртуального админа
            return {
                "id": 1,
                "username": settings.ADMIN_USERNAME,
                "email": "admin@example.com",
                "first_name": "Администратор",
                "last_name": "",
                "role": "owner",
                "is_active": True
            }
    
    # Проверяем исполнителей в базе данных
    try:
        with get_db_context() as db:
            admin_user = db.query(AdminUser).filter(
                AdminUser.username == credentials.username,
                AdminUser.is_active == True
            ).first()
            
            if admin_user and AuthService.verify_password(credentials.password, admin_user.password_hash):
                return {
                    "id": admin_user.id,
                    "username": admin_user.username,
                    "email": admin_user.email,
                    "first_name": admin_user.first_name,
                    "last_name": admin_user.last_name,
                    "role": admin_user.role,
                    "is_active": admin_user.is_active
                }
    except Exception:
        pass
    
    # Если ни один способ не сработал
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """Получить текущего администратора (алиас для require_admin_auth)"""
    return require_admin_auth(credentials)
