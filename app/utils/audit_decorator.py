"""
Декораторы для автоматического аудита действий
"""

from functools import wraps
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import time
import inspect
import json

from ..database.audit_models import AuditActionType, AuditEntityType
from ..services.audit_service import AuditService
from ..config.logging import get_logger

logger = get_logger(__name__)


def audit_action(action_type: AuditActionType = None,
                entity_type: AuditEntityType = None,
                entity_id_param: str = None,
                entity_name_param: str = None,
                capture_old_values: bool = False,
                capture_result: bool = True,
                description_template: str = None):
    """
    Декоратор для автоматического логирования действий
    
    Args:
        action_type: Тип действия
        entity_type: Тип сущности
        entity_id_param: Имя параметра с ID сущности
        entity_name_param: Имя параметра с названием сущности
        capture_old_values: Захватывать старые значения (для UPDATE)
        capture_result: Захватывать результат выполнения
        description_template: Шаблон описания (может содержать {param_name})
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _execute_with_audit(func, True, action_type, entity_type,
                                            entity_id_param, entity_name_param,
                                            capture_old_values, capture_result,
                                            description_template, args, kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _execute_with_audit(func, False, action_type, entity_type,
                                      entity_id_param, entity_name_param,
                                      capture_old_values, capture_result,
                                      description_template, args, kwargs)
        
        # Определяем, асинхронная ли функция
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _execute_with_audit(func: Callable, is_async: bool,
                       action_type: AuditActionType,
                       entity_type: AuditEntityType,
                       entity_id_param: str,
                       entity_name_param: str,
                       capture_old_values: bool,
                       capture_result: bool,
                       description_template: str,
                       args: tuple, kwargs: dict):
    """Выполнить функцию с аудитом"""
    
    start_time = time.time()
    audit_service = None
    db_session = None
    user_id = None
    session_info = {}
    old_values = None
    
    try:
        # Извлекаем параметры для аудита
        func_params = _extract_function_params(func, args, kwargs)
        
        # Получаем db сессию
        db_session = func_params.get('db') or func_params.get('session')
        
        # Получаем информацию о пользователе
        user_id = func_params.get('user_id') or func_params.get('current_user_id')
        if not user_id and 'request' in func_params:
            request = func_params['request']
            if hasattr(request, 'state') and hasattr(request.state, 'user'):
                user_id = request.state.user.id
            session_info = {
                'ip_address': getattr(request, 'client', {}).get('host'),
                'user_agent': request.headers.get('user-agent'),
                'session_id': request.headers.get('x-session-id')
            }
        
        # Получаем ID и название сущности
        entity_id = func_params.get(entity_id_param) if entity_id_param else None
        entity_name = func_params.get(entity_name_param) if entity_name_param else None
        
        # Захватываем старые значения если нужно
        if capture_old_values and db_session and entity_type and entity_id:
            old_values = _get_entity_values(db_session, entity_type, entity_id)
        
        # Создаем сервис аудита
        if db_session:
            audit_service = AuditService(db_session)
        
        # Выполняем функцию
        if is_async:
            import asyncio
            result = asyncio.run(func(*args, **kwargs))
        else:
            result = func(*args, **kwargs)
        
        # Записываем успешное выполнение
        duration_ms = int((time.time() - start_time) * 1000)
        
        if audit_service:
            # Формируем описание
            description = _format_description(description_template, func_params, func.__name__)
            
            # Получаем новые значения если это UPDATE
            new_values = None
            if capture_old_values and old_values:
                new_values = _get_entity_values(db_session, entity_type, entity_id)
            elif capture_result and isinstance(result, dict):
                new_values = result
            
            # Определяем тип действия если не указан
            if not action_type:
                action_type = _infer_action_type(func.__name__)
            
            # Логируем действие
            audit_service.log_action(
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                description=description,
                old_values=old_values,
                new_values=new_values,
                extra_metadata={
                    'function': func.__name__,
                    'module': func.__module__
                },
                success=True,
                duration_ms=duration_ms,
                user_id=user_id,
                session_info=session_info
            )
        
        return result
        
    except Exception as e:
        # Записываем ошибку
        duration_ms = int((time.time() - start_time) * 1000)
        
        if audit_service:
            description = f"Ошибка при выполнении {func.__name__}: {str(e)}"
            
            audit_service.log_action(
                action_type=action_type or AuditActionType.UPDATE,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                description=description,
                old_values=old_values,
                extra_metadata={
                    'function': func.__name__,
                    'module': func.__module__,
                    'error': str(e)
                },
                success=False,
                error_message=str(e),
                duration_ms=duration_ms,
                user_id=user_id,
                session_info=session_info
            )
        
        # Пробрасываем исключение дальше
        raise


def audit_api_endpoint(entity_type: AuditEntityType = None):
    """
    Декоратор для API эндпоинтов FastAPI
    Автоматически определяет тип действия по HTTP методу
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                # Пытаемся найти request в args
                for arg in args:
                    if hasattr(arg, 'method'):
                        request = arg
                        break
            
            # Определяем action_type по HTTP методу
            action_type = None
            if request:
                method = request.method.upper()
                if method == 'POST':
                    action_type = AuditActionType.CREATE
                elif method == 'PUT' or method == 'PATCH':
                    action_type = AuditActionType.UPDATE
                elif method == 'DELETE':
                    action_type = AuditActionType.DELETE
                elif method == 'GET':
                    action_type = AuditActionType.READ
            
            # Вызываем основной декоратор
            return await audit_action(
                action_type=action_type,
                entity_type=entity_type,
                capture_result=True
            )(func)(*args, **kwargs)
        
        return wrapper
    
    return decorator


def audit_login(success_param: str = 'success'):
    """Декоратор для логирования попыток входа"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Получаем параметры
            func_params = _extract_function_params(func, args, kwargs)
            db_session = func_params.get('db') or func_params.get('session')
            
            if db_session:
                audit_service = AuditService(db_session)
                
                # Определяем успешность
                success = result.get(success_param, False) if isinstance(result, dict) else bool(result)
                
                # Получаем информацию о пользователе
                user_id = None
                if success and isinstance(result, dict):
                    user_id = result.get('user_id') or result.get('user', {}).get('id')
                
                # Получаем информацию о сессии
                session_info = {}
                if 'request' in func_params:
                    request = func_params['request']
                    session_info = {
                        'ip_address': getattr(request, 'client', {}).get('host'),
                        'user_agent': request.headers.get('user-agent')
                    }
                
                # Логируем
                audit_service.log_login(
                    user_id=user_id,
                    success=success,
                    ip_address=session_info.get('ip_address'),
                    user_agent=session_info.get('user_agent')
                )
            
            return result
        
        return wrapper
    
    return decorator


def audit_critical(description: str = None):
    """
    Декоратор для критически важных операций
    Всегда логирует, даже если нет db сессии
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.warning(f"CRITICAL OPERATION: {func.__name__} - {description or 'No description'}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"CRITICAL OPERATION SUCCESS: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"CRITICAL OPERATION FAILED: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    
    return decorator


# === Вспомогательные функции ===

def _extract_function_params(func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Извлечь параметры функции"""
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    return bound.arguments


def _infer_action_type(func_name: str) -> AuditActionType:
    """Определить тип действия по имени функции"""
    func_name_lower = func_name.lower()
    
    if any(word in func_name_lower for word in ['create', 'add', 'insert', 'new']):
        return AuditActionType.CREATE
    elif any(word in func_name_lower for word in ['update', 'edit', 'modify', 'change']):
        return AuditActionType.UPDATE
    elif any(word in func_name_lower for word in ['delete', 'remove', 'destroy']):
        return AuditActionType.DELETE
    elif any(word in func_name_lower for word in ['read', 'get', 'fetch', 'list', 'search']):
        return AuditActionType.READ
    elif 'login' in func_name_lower:
        return AuditActionType.LOGIN
    elif 'logout' in func_name_lower:
        return AuditActionType.LOGOUT
    elif 'export' in func_name_lower:
        return AuditActionType.EXPORT
    elif 'import' in func_name_lower:
        return AuditActionType.IMPORT
    else:
        return AuditActionType.UPDATE  # По умолчанию


def _format_description(template: str, params: Dict[str, Any], func_name: str) -> str:
    """Форматировать описание действия"""
    if not template:
        return f"Выполнена операция {func_name}"
    
    try:
        return template.format(**params)
    except:
        return template


def _get_entity_values(db_session, entity_type: AuditEntityType, entity_id: int) -> Dict:
    """Получить значения сущности из БД"""
    try:
        # Импортируем модели
        from ..database.crm_models import Client, Lead, Deal
        from ..database.models import Project, AdminUser, Task
        
        # Маппинг типов на модели
        model_map = {
            AuditEntityType.CLIENT: Client,
            AuditEntityType.LEAD: Lead,
            AuditEntityType.DEAL: Deal,
            AuditEntityType.PROJECT: Project,
            AuditEntityType.USER: AdminUser,
            AuditEntityType.TASK: Task
        }
        
        model_class = model_map.get(entity_type)
        if not model_class:
            return None
        
        # Получаем сущность
        entity = db_session.query(model_class).filter(
            model_class.id == entity_id
        ).first()
        
        if not entity:
            return None
        
        # Преобразуем в словарь
        if hasattr(entity, 'to_dict'):
            return entity.to_dict()
        else:
            # Простое преобразование
            result = {}
            for column in entity.__table__.columns:
                value = getattr(entity, column.name)
                # Преобразуем сложные типы
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif hasattr(value, 'value'):  # Enum
                    value = value.value
                result[column.name] = value
            return result
    except Exception as e:
        logger.error(f"Error getting entity values: {e}")
        return None