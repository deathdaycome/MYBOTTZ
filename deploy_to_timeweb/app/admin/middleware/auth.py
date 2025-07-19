from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets

from ...database.database import get_db
from ...database.models import AdminUser
from ...config.settings import settings
from ...services.auth_service import AuthService

security = HTTPBasic()

def require_admin_auth(credentials: HTTPBasicCredentials = Depends(security)) -> AdminUser:
    """Требует аутентификации администратора"""
    # Проверяем основного владельца
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if correct_username and correct_password:
        # Возвращаем владельца как AdminUser
        return AdminUser(
            id=0,
            username=settings.ADMIN_USERNAME,
            email="admin@example.com",
            role="owner",
            is_active=True
        )
    
    # Проверяем исполнителей в базе данных
    try:
        admin_user = AuthService.authenticate_user(credentials.username, credentials.password)
        if admin_user:
            return admin_user
    except Exception:
        pass
    
    # Если ни один способ не сработал
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)) -> AdminUser:
    """Получить текущего администратора (алиас для require_admin_auth)"""
    return require_admin_auth(credentials)
