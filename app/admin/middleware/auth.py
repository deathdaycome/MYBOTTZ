from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
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
        # Возвращаем владельца из настроек
        return {
            "id": 1,
            "username": settings.ADMIN_USERNAME,
            "password": credentials.password,  # Добавляем пароль для JavaScript
            "email": "admin@example.com",
            "first_name": "Администратор",
            "last_name": "",
            "role": "owner",
            "is_active": True
        }

    # Если credentials не совпали с владельцем, проверяем хеши для других пользователей
    # Примечание: проверку БД убрали чтобы избежать sync/async конфликта
    # Для полноценной аутентификации исполнителей нужно использовать async auth endpoints

    # Если ни один способ не сработал
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """Получить текущего администратора (алиас для require_admin_auth)"""
    return require_admin_auth(credentials)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Аутентификация пользователя, возвращает имя пользователя"""
    user_data = require_admin_auth(credentials)
    return user_data["username"]
