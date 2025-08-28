# app/admin/routers/users.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import AdminUser
from ...config.logging import get_logger
from ...services.auth_service import AuthService
from ..middleware.auth import get_current_admin_user
from ...services.rbac_service import RBACService

logger = get_logger(__name__)

router = APIRouter(tags=["admin_users"])
templates = Jinja2Templates(directory="app/admin/templates")

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

@router.get("", response_class=HTMLResponse)
async def users_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Страница управления пользователями"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.view"):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра пользователей")
    
    # Получаем элементы навигации
    from ..navigation import get_navigation_items
    navigation_items = get_navigation_items(current_user.get("role", "admin") if isinstance(current_user, dict) else current_user.role)
    
    # Получаем список пользователей
    users = db.query(AdminUser).all()
    
    # Статистика
    stats = {
        "total": len(users),
        "owners": len([u for u in users if u.role == "owner"]),
        "admins": len([u for u in users if u.role == "admin"]), 
        "executors": len([u for u in users if u.role == "executor"]),
        "salespeople": len([u for u in users if u.role == "salesperson"])
    }
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "user": current_user,
        "username": current_user.get("username") if isinstance(current_user, dict) else current_user.username,
        "password": current_user.get("password", "") if isinstance(current_user, dict) else current_user.password if hasattr(current_user, 'password') else "",
        "user_role": current_user.get("role", "admin") if isinstance(current_user, dict) else current_user.role,
        "navigation_items": navigation_items,
        "users": users,
        "stats": stats
    })

@router.get("/api")
async def get_admin_users(db: Session = Depends(get_db)):
    """Получить список всех админ-пользователей для API"""
    try:
        # Получаем всех пользователей из базы данных
        users = db.query(AdminUser).all()
        
        # Преобразуем в формат для API
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "notifications": {
                    "new_tasks": True,
                    "deadlines": True,
                    "comments": True,
                    "reports": True
                }
            })
        
        return {
            "success": True,
            "users": users_data
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

@router.put("/api/{user_id}/notifications")
async def update_user_notifications(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновить настройки уведомлений пользователя"""
    try:
        data = await request.json()
        
        # Здесь можно было бы обновлять настройки в базе данных
        # Пока просто возвращаем успех
        logger.info(f"Обновление настроек уведомлений для пользователя {user_id}: {data}")
        
        return {
            "success": True,
            "message": "Настройки уведомлений обновлены"
        }
    except Exception as e:
        logger.error(f"Ошибка обновления настроек уведомлений: {e}")
        return {
            "success": False,
            "message": f"Ошибка обновления настроек: {str(e)}"
        }

@router.post("/api/users/create", response_class=JSONResponse)
async def create_user(
    request: Request,
    current_user: AdminUser = Depends(get_current_user)
):
    """Создать нового пользователя (только для владельца)"""
    try:
        if not current_user.is_owner():
            raise HTTPException(
                status_code=403,
                detail="Только владелец может создавать пользователей"
            )
        
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "executor")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        
        if not username or not password:
            raise HTTPException(
                status_code=400,
                detail="Логин и пароль обязательны"
            )
        
        if role not in ["owner", "admin", "executor", "salesperson"]:
            raise HTTPException(
                status_code=400,
                detail="Недопустимая роль"
            )
        
        user = AuthService.create_user(
            username=username,
            password=password,
            role=role,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        if not user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким логином уже существует"
            )
        
        return {
            "success": True,
            "message": "Пользователь успешно создан",
            "user": user.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания пользователя: {str(e)}"
        )

@router.put("/{user_id}/password")
async def change_user_password(
    user_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_user)
):
    """Изменить пароль пользователя (только для владельца или себя)"""
    try:
        data = await request.json()
        new_password = data.get("password") or data.get("new_password")
        
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

@router.get("/{user_id}/password/view")
async def view_user_password(
    user_id: int,
    current_user: AdminUser = Depends(get_current_user)
):
    """Просмотреть пароль пользователя (только для владельца)"""
    try:
        # Только владелец может просматривать пароли
        if not current_user.is_owner():
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав для просмотра паролей"
            )
        
        # Получаем пользователя из базы
        from ...database.database import get_db_context
        with get_db_context() as db:
            user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="Пользователь не найден"
                )
            
            # Пароли хранятся в хешированном виде и не могут быть показаны
            # Можно только сбросить пароль через изменение
            return {
                "success": True,
                "password": "Пароль зашифрован. Используйте 'Сменить пароль' для установки нового.",
                "message": "Пароли хранятся в зашифрованном виде"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка просмотра пароля пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка просмотра пароля: {str(e)}"
        )

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: AdminUser = Depends(get_current_user)
):
    """Получить информацию о пользователе"""
    try:
        # Пользователь может просматривать только свои данные или владелец все
        if not current_user.is_owner() and current_user.id != user_id:
            return {
                "success": False,
                "message": "Недостаточно прав доступа"
            }
        
        from ...database.database import get_db_context
        with get_db_context() as db:
            user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "message": "Пользователь не найден"
                }
            
            return {
                "success": True,
                "user": user.to_dict()
            }
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {user_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения пользователя: {str(e)}"
        }

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_user)
):
    """Обновить данные пользователя"""
    try:
        # Пользователь может редактировать только свои данные или владелец все
        if not current_user.is_owner() and current_user.id != user_id:
            return {
                "success": False,
                "message": "Недостаточно прав доступа"
            }
        
        data = await request.json()
        
        from ...database.database import get_db_context
        with get_db_context() as db:
            user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "message": "Пользователь не найден"
                }
            
            # Обновляем данные
            if "first_name" in data:
                user.first_name = data["first_name"]
            if "last_name" in data:
                user.last_name = data["last_name"]
            if "email" in data:
                user.email = data["email"]
            if "password" in data and data["password"]:
                user.set_password(data["password"])
            if "is_active" in data and current_user.is_owner():
                user.is_active = data["is_active"]
            
            db.commit()
            
            # Логирование активности временно отключено
            # TODO: Добавить миграцию для таблицы admin_activity_logs
            # from ...database.models import AdminActivityLog
            # log = AdminActivityLog(
            #     user_id=current_user.id,
            #     action="update_user",
            #     action_type="update",
            #     entity_type="user",
            #     entity_id=user_id,
            #     details={"updated_fields": list(data.keys())}
            # )
            # db.add(log)
            # db.commit()
            
            return {
                "success": True,
                "message": "Данные пользователя обновлены",
                "user": user.to_dict()
            }
    except Exception as e:
        logger.error(f"Ошибка обновления пользователя {user_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка обновления данных: {str(e)}"
        }

@router.get("/me")
async def get_current_user_info(current_user: AdminUser = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return {
        "success": True,
        "user": current_user.to_dict()
    }
