"""
Модуль аутентификации для админ-панели
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from ..database.models import AdminUser
from ..database.database import get_db_context
from ..config.settings import settings
from ..config.logging import get_logger

logger = get_logger(__name__)
security = HTTPBasic()


def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """
    Получает текущего аутентифицированного пользователя админ-панели
    """
    logger.info(f"Попытка входа пользователя: {credentials.username}")
    
    # Проверка дефолтных учетных данных
    if credentials.username == "admin" and credentials.password == "qwerty123":
        logger.info("Вход по дефолтным учетным данным")
        return {
            "id": 1,
            "username": "admin",
            "role": "owner",
            "email": "admin@example.com"
        }
    
    # Проверка основного владельца из настроек
    if (credentials.username == settings.ADMIN_USERNAME and 
        credentials.password == settings.ADMIN_PASSWORD):
        logger.info("Вход владельца из настроек")
        return {
            "id": 1,
            "username": credentials.username,
            "role": "owner",
            "email": "admin@example.com"
        }
    
    # Проверка в базе данных
    try:
        with get_db_context() as db:
            user = db.query(AdminUser).filter(
                AdminUser.username == credentials.username
            ).first()
            
            if user and user.check_password(credentials.password):
                logger.info(f"Успешный вход пользователя: {user.username}")
                return {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "email": user.email
                }
    except Exception as e:
        logger.error(f"Ошибка при проверке пользователя в БД: {e}")
    
    # Если аутентификация не удалась
    logger.warning(f"Неудачная попытка входа для пользователя: {credentials.username}")
    raise HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )