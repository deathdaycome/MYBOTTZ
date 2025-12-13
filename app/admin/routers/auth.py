"""
Роутер для аутентификации пользователей админ-панели
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import hashlib
import secrets
import logging
from datetime import datetime

from app.core.database import get_db
from ...database.models import AdminUser
from ...config.settings import settings

router = APIRouter()
security = HTTPBasic()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict
    message: Optional[str] = None


class UserInfoResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    telegram_id: Optional[int]


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return hash_password(plain_password) == hashed_password


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Аутентификация пользователя по username и паролю
    """
    try:
        logger.info(f"Login attempt for user: {request.username}")

        # Сначала проверяем владельца из настроек
        if request.username == settings.ADMIN_USERNAME and request.password == settings.ADMIN_PASSWORD:
            logger.info(f"Owner login successful: {request.username}")
            return LoginResponse(
                success=True,
                token=f"Basic {request.username}:{request.password}",
                user={
                    "id": 1,
                    "username": request.username,
                    "email": "admin@example.com",
                    "first_name": "Администратор",
                    "last_name": "",
                    "role": "owner",
                    "telegram_id": None
                },
                message="Успешный вход"
            )

        # Поиск пользователя в базе
        # Используем правильный async паттерн
        stmt = select(AdminUser).where(
            AdminUser.username == request.username,
            AdminUser.is_active == True
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"User not found: {request.username}")
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        # Проверка пароля - используем простую проверку хеша
        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Invalid password for user: {request.username}")
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        # Обновление времени последнего входа
        user.last_login = datetime.utcnow()
        await db.commit()

        logger.info(f"User login successful: {request.username}, role: {user.role}")

        # Создание токена (Base64 от username:password для совместимости с Basic Auth)
        token = f"Basic {user.username}:{request.password}"

        # Возвращаем данные пользователя
        return LoginResponse(
            success=True,
            token=token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "telegram_id": user.telegram_id
            },
            message="Успешный вход"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Получение информации о текущем пользователе
    """
    try:
        # Извлекаем username из Basic Auth
        username = credentials.username

        # Сначала проверяем владельца
        if username == settings.ADMIN_USERNAME and credentials.password == settings.ADMIN_PASSWORD:
            return UserInfoResponse(
                id=1,
                username=username,
                email="admin@example.com",
                first_name="Администратор",
                last_name="",
                role="owner",
                telegram_id=None
            )

        # Поиск пользователя в базе
        async with get_db_context() as db:
            stmt = select(AdminUser).where(
                AdminUser.username == username,
                AdminUser.is_active == True
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=401, detail="Пользователь не найден")

            # Проверка пароля
            if not verify_password(credentials.password, user.password_hash):
                raise HTTPException(status_code=401, detail="Неверные учетные данные")

            return UserInfoResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                telegram_id=user.telegram_id
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.post("/logout")
async def logout():
    """
    Выход из системы (на клиенте нужно удалить токен из localStorage)
    """
    return {"success": True, "message": "Успешный выход"}


async def verify_user(credentials: HTTPBasicCredentials) -> Optional[AdminUser]:
    """
    Проверка учетных данных пользователя (async версия)
    """
    try:
        # Проверяем владельца
        if credentials.username == settings.ADMIN_USERNAME and credentials.password == settings.ADMIN_PASSWORD:
            # Возвращаем виртуального пользователя для владельца
            user = AdminUser()
            user.id = 1
            user.username = settings.ADMIN_USERNAME
            user.role = "owner"
            user.is_active = True
            user.first_name = "Администратор"
            return user

        # Проверяем в базе
        async with get_db_context() as db:
            stmt = select(AdminUser).where(
                AdminUser.username == credentials.username,
                AdminUser.is_active == True
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if user and verify_password(credentials.password, user.password_hash):
                return user
            return None
    except Exception as e:
        logger.error(f"Verify user error: {str(e)}")
        return None


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """
    Синхронная версия для совместимости (возвращает базовую информацию)
    Для полной проверки используйте get_current_user_async
    """
    # Проверяем владельца
    if credentials.username == settings.ADMIN_USERNAME:
        if credentials.password == settings.ADMIN_PASSWORD:
            return {
                "id": 1,
                "username": credentials.username,
                "role": "owner",
                "is_active": True
            }

    # Для других пользователей возвращаем временные данные
    # Реальная проверка должна быть в async endpoints
    return {
        "id": 0,
        "username": credentials.username,
        "role": "unknown",
        "is_active": False,
        "_needs_async_check": True
    }


async def get_current_user_async(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """
    Асинхронная версия получения текущего пользователя
    """
    user = await verify_user(credentials)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "first_name": getattr(user, 'first_name', ''),
        "last_name": getattr(user, 'last_name', '')
    }