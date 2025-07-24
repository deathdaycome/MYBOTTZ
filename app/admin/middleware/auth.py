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
        # Ищем администратора в базе данных
        try:
            db = next(get_db())
            admin_user = db.query(AdminUser).filter(
                AdminUser.username == settings.ADMIN_USERNAME,
                AdminUser.role == "owner"
            ).first()
            db.close()
            
            if admin_user:
                return admin_user
            else:
                # Если не найден в БД, создаем виртуального админа с правильным ID
                return AdminUser(
                    id=1,  # Используем правильный ID из БД
                    username=settings.ADMIN_USERNAME,
                    password_hash="",
                    email="admin@example.com",
                    first_name="Администратор",
                    last_name="",
                    role="owner",
                    is_active=True
                )
        except Exception:
            # Fallback - создаем виртуального админа
            return AdminUser(
                id=1,
                username=settings.ADMIN_USERNAME,
                password_hash="",
                email="admin@example.com",
                first_name="Администратор",
                last_name="",
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
