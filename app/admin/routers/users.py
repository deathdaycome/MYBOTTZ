# app/admin/routers/users.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import AdminUser
from ...config.logging import get_logger
from ...services.auth_service import AuthService

logger = get_logger(__name__)

router = APIRouter(tags=["admin_users"])

# Базовая аутентификация
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> AdminUser:
    """Получение текущего пользователя с проверкой аутентификации"""
    user = AuthService.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

@router.get("/")
async def get_admin_users():
    """Получить список всех админ-пользователей - временно без аутентификации для отладки"""
    try:
        # Временно возвращаем пустой список пользователей
        return {
            "success": True,
            "users": []
        }
    except Exception as e:
        logger.error(f"Ошибка получения пользователей: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения пользователей: {str(e)}",
            "users": []
        }

@router.get("/executors")
async def get_executors():
    """Получить список исполнителей"""
    try:
        executors = AuthService.get_executors()
        return {
            "success": True,
            "executors": executors
        }
    except Exception as e:
        logger.error(f"Ошибка получения исполнителей: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения исполнителей: {str(e)}",
            "executors": []
        }

@router.post("/")
async def create_user(
    request: Request,
    current_user: AdminUser = Depends(get_current_user)
):
    """Создать нового пользователя (только для владельца)"""
    try:
        if not current_user.is_owner():
            return {
                "success": False,
                "message": "Только владелец может создавать пользователей"
            }
        
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "executor")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        
        if not username or not password:
            return {
                "success": False,
                "message": "Логин и пароль обязательны"
            }
        
        if role not in ["owner", "executor"]:
            return {
                "success": False,
                "message": "Недопустимая роль"
            }
        
        user = AuthService.create_user(
            username=username,
            password=password,
            role=role,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь с таким логином уже существует"
            }
        
        return {
            "success": True,
            "message": "Пользователь успешно создан",
            "user": user.to_dict()
        }
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        return {
            "success": False,
            "message": f"Ошибка создания пользователя: {str(e)}"
        }

@router.put("/{user_id}/password")
async def change_user_password(
    user_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_user)
):
    """Изменить пароль пользователя (только для владельца или себя)"""
    try:
        data = await request.json()
        new_password = data.get("new_password")
        
        if not new_password:
            return {
                "success": False,
                "message": "Новый пароль обязателен"
            }
        
        # Владелец может менять пароль любому, пользователь только себе
        if not current_user.is_owner() and current_user.id != user_id:
            return {
                "success": False,
                "message": "Недостаточно прав доступа"
            }
        
        success = AuthService.change_password(user_id, new_password)
        
        if not success:
            return {
                "success": False,
                "message": "Не удалось изменить пароль"
            }
        
        return {
            "success": True,
            "message": "Пароль успешно изменен"
        }
    except Exception as e:
        logger.error(f"Ошибка изменения пароля пользователя {user_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка изменения пароля: {str(e)}"
        }

@router.delete("/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: AdminUser = Depends(get_current_user)
):
    """Деактивировать пользователя (только для владельца)"""
    try:
        if not current_user.is_owner():
            return {
                "success": False,
                "message": "Только владелец может деактивировать пользователей"
            }
        
        if user_id == current_user.id:
            return {
                "success": False,
                "message": "Нельзя деактивировать самого себя"
            }
        
        success = AuthService.deactivate_user(user_id)
        
        if not success:
            return {
                "success": False,
                "message": "Не удалось деактивировать пользователя"
            }
        
        return {
            "success": True,
            "message": "Пользователь успешно деактивирован"
        }
    except Exception as e:
        logger.error(f"Ошибка деактивации пользователя {user_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка деактивации пользователя: {str(e)}"
        }

@router.get("/me")
async def get_current_user_info(current_user: AdminUser = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return {
        "success": True,
        "user": current_user.to_dict()
    }
