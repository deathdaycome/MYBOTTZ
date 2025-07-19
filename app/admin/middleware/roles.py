# app/admin/middleware/roles.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBasicCredentials
from ...services.auth_service import AuthService
from ...config.settings import settings
import secrets
import base64

class RoleMiddleware:
    """Middleware для проверки ролей и доступа"""
    
    @staticmethod
    def get_current_user_from_request(request: Request) -> dict:
        """Получить текущего пользователя из запроса"""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Basic "):
            return None
            
        try:
            # Декодируем Basic Auth
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            # Сначала проверяем старую систему (владелец)
            correct_username = secrets.compare_digest(username, settings.ADMIN_USERNAME)
            correct_password = secrets.compare_digest(password, settings.ADMIN_PASSWORD)
            
            if correct_username and correct_password:
                return {
                    "id": 1,
                    "username": username,
                    "role": "owner",
                    "is_active": True
                }
            
            # Проверяем новую систему (исполнители)
            user = AuthService.authenticate_user(username, password)
            if user and user.is_active:
                return {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "is_active": user.is_active
                }
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def check_access(user: dict, required_role: str = None) -> bool:
        """Проверить права доступа пользователя"""
        if not user:
            return False
            
        if not required_role:
            return True  # Любая роль подходит
            
        # Владелец имеет доступ ко всему
        if user["role"] == "owner":
            return True
            
        # Проверяем конкретную роль
        return user["role"] == required_role
    
    @staticmethod
    def require_role(required_role: str = None):
        """Декоратор для проверки роли"""
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                user = RoleMiddleware.get_current_user_from_request(request)
                
                if not user:
                    raise HTTPException(status_code=401, detail="Требуется аутентификация")
                
                if not RoleMiddleware.check_access(user, required_role):
                    raise HTTPException(status_code=403, detail="Недостаточно прав доступа")
                
                # Добавляем пользователя в kwargs
                kwargs['current_user'] = user
                return await func(request, *args, **kwargs)
            
            return wrapper
        return decorator
