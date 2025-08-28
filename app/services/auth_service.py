"""
Сервис аутентификации для админ-панели
"""

from sqlalchemy.orm import Session
from app.database.models import AdminUser
from app.database.database import get_db_connection
from datetime import datetime
import hashlib
import base64
from typing import Optional, Tuple

class AuthService:
    """Сервис для управления аутентификацией админ-панели"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Проверка пароля"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[AdminUser]:
        """Аутентификация пользователя"""
        db = next(get_db_connection())
        try:
            user = db.query(AdminUser).filter(
                AdminUser.username == username,
                AdminUser.is_active == True
            ).first()
            
            if user and AuthService.verify_password(password, user.password_hash):
                # Обновляем время последнего входа
                user.last_login = datetime.utcnow()
                db.commit()
                return user
            return None
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod  
    def verify_credentials(credentials) -> bool:
        """Проверка учетных данных для FastAPI HTTPBasicCredentials"""
        from app.config.settings import settings
        import secrets
        
        # Проверка основного админа
        correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
        correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
        
        if correct_username and correct_password:
            return True
            
        # Проверка пользователей из БД
        user = AuthService.authenticate_user(credentials.username, credentials.password)
        return user is not None

    @staticmethod
    def verify_basic_auth(auth_header: str) -> Tuple[Optional[AdminUser], str]:
        """
        Проверка Basic Auth заголовка
        Возвращает (пользователь, роль) или (None, 'unauthorized')
        """
        if not auth_header or not auth_header.startswith('Basic '):
            return None, 'unauthorized'
        
        try:
            # Декодируем Base64
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            user = AuthService.authenticate_user(username, password)
            if user:
                return user, user.role
            return None, 'unauthorized'
        except Exception as e:
            print(f"Ошибка проверки Basic Auth: {e}")
            return None, 'unauthorized'
    
    @staticmethod
    def create_user(username: str, password: str, role: str = 'executor', 
                   email: str = None, first_name: str = None, last_name: str = None) -> Optional[AdminUser]:
        """Создание нового пользователя"""
        db = next(get_db_connection())
        try:
            # Проверяем, что пользователь не существует
            existing_user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if existing_user:
                return None
            
            # Создаем нового пользователя
            user = AdminUser(
                username=username,
                password_hash=AuthService.hash_password(password),
                role=role,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_users() -> list:
        """Получить всех пользователей"""
        db = next(get_db_connection())
        try:
            users = db.query(AdminUser).filter(AdminUser.is_active == True).all()
            return [user.to_dict() for user in users]
        except Exception as e:
            print(f"Ошибка получения пользователей: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_executors() -> list:
        """Получить всех исполнителей и админов"""
        db = next(get_db_connection())
        try:
            # Получаем всех активных пользователей (админы и исполнители могут назначаться на проекты)
            executors = db.query(AdminUser).filter(
                AdminUser.role.in_(['executor', 'admin', 'owner']),
                AdminUser.is_active == True
            ).all()
            return [user.to_dict() for user in executors]
        except Exception as e:
            print(f"Ошибка получения исполнителей: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def change_password(user_id: int, new_password: str) -> bool:
        """Изменение пароля пользователя"""
        db = next(get_db_connection())
        try:
            user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if user:
                user.password_hash = AuthService.hash_password(new_password)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка изменения пароля: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """Деактивация пользователя"""
        db = next(get_db_connection())
        try:
            user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if user:
                user.is_active = False
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка деактивации пользователя: {e}")
            db.rollback()
            return False
        finally:
            db.close()

# Декоратор для проверки прав доступа
def require_auth(required_role: str = None):
    """
    Декоратор для проверки аутентификации и прав доступа
    required_role: 'owner' или 'executor' или None (любая роль)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            auth_header = request.headers.get('Authorization')
            user, role = AuthService.verify_basic_auth(auth_header)
            
            if not user:
                return jsonify({"success": False, "message": "Требуется аутентификация"}), 401
            
            if required_role and role != required_role and role != 'owner':
                return jsonify({"success": False, "message": "Недостаточно прав доступа"}), 403
            
            # Добавляем информацию о пользователе в контекст
            kwargs['current_user'] = user
            kwargs['current_role'] = role
            
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
