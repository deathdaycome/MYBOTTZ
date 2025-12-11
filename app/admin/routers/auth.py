"""
Роутер для аутентификации пользователей админ-панели
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import hashlib
import secrets

from ...database.models import AdminUser
from ...core.database import get_db

router = APIRouter()
security = HTTPBasic()


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


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя по username и паролю
    """
    try:
        # Поиск пользователя в базе
        user = db.query(AdminUser).filter(
            AdminUser.username == request.username,
            AdminUser.is_active == True
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        # Проверка пароля
        if not user.check_password(request.password):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        # Обновление времени последнего входа
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()

        # Создание токена (Base64 от username:password для совместимости с Basic Auth)
        token = secrets.token_urlsafe(32)

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
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Получение информации о текущем пользователе
    """
    try:
        # Извлекаем username из Basic Auth
        username = credentials.username

        # Поиск пользователя в базе
        user = db.query(AdminUser).filter(
            AdminUser.username == username,
            AdminUser.is_active == True
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")

        # Проверка пароля
        if not user.check_password(credentials.password):
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
        print(f"Get user info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.post("/logout")
async def logout():
    """
    Выход из системы (на клиенте нужно удалить токен из localStorage)
    """
    return {"success": True, "message": "Успешный выход"}


def verify_user(credentials: HTTPBasicCredentials, db: Session) -> Optional[AdminUser]:
    """
    Проверка учетных данных пользователя
    """
    try:
        user = db.query(AdminUser).filter(
            AdminUser.username == credentials.username,
            AdminUser.is_active == True
        ).first()

        if user and user.check_password(credentials.password):
            return user
        return None
    except Exception as e:
        print(f"Verify user error: {str(e)}")
        return None
