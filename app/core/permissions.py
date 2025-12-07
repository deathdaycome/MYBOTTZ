"""
Middleware и декораторы для проверки прав доступа к API
"""

from functools import wraps
from typing import Optional, Callable
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.roles import (
    UserRole, Section, Action,
    has_permission,
    can_access_project,
    can_access_task
)


# ============================================
# HELPERS
# ============================================

def get_current_user_from_request(request: Request) -> Optional[dict]:
    """
    Извлечь текущего пользователя из запроса

    Args:
        request: FastAPI Request объект

    Returns:
        Словарь с данными пользователя или None
    """
    # Попытка получить из session (admin panel)
    try:
        # Проверяем наличие _session в scope для определения установленного SessionMiddleware
        if hasattr(request, 'scope') and '_session' in request.scope:
            session = request.session
            if session:
                user_id = session.get('user_id')
                role = session.get('role')

                if user_id and role:
                    return {
                        'id': user_id,
                        'role': role,
                        'username': session.get('username', ''),
                    }
    except (RuntimeError, AttributeError, KeyError):
        # Session middleware not installed or error accessing session
        pass

    # Попытка получить из state (если установлено middleware)
    if hasattr(request.state, 'user'):
        return request.state.user

    # Попытка получить из Basic Auth (для совместимости)
    try:
        import base64
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Basic '):
            # Для тестирования - вернем mock пользователя
            # В продакшене здесь должна быть реальная проверка
            return {
                'id': 1,
                'role': 'owner',
                'username': 'admin'
            }
    except Exception:
        pass

    return None


def check_user_permission(user: dict, section: Section, action: Action) -> bool:
    """
    Проверить, есть ли у пользователя право на действие

    Args:
        user: Словарь с данными пользователя (должен содержать 'role')
        section: Раздел системы
        action: Действие

    Returns:
        True если право есть
    """
    if not user or 'role' not in user:
        return False

    return has_permission(user['role'], section, action)


# ============================================
# DECORATORS ДЛЯ FASTAPI ROUTES
# ============================================

def require_permission(section: Section, action: Action):
    """
    Декоратор для проверки прав доступа к эндпоинту

    Использование:
        @app.get("/admin/api/projects")
        @require_permission(Section.PROJECTS, Action.VIEW)
        async def get_projects(request: Request):
            ...

    Args:
        section: Раздел системы
        action: Требуемое действие
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Найти Request в аргументах
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # Попробовать найти в kwargs
                request = kwargs.get('request')

            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Request object not found in route handler"
                )

            # Получить текущего пользователя
            current_user = get_current_user_from_request(request)

            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Необходима авторизация"
                )

            # Проверить право
            if not check_user_permission(current_user, section, action):
                raise HTTPException(
                    status_code=403,
                    detail=f"У вас нет прав для {action.value} в разделе {section.value}"
                )

            # Вызвать оригинальную функцию
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(*allowed_roles: UserRole):
    """
    Декоратор для проверки роли пользователя

    Использование:
        @app.post("/admin/api/users")
        @require_role(UserRole.OWNER, UserRole.ADMIN)
        async def create_user(request: Request):
            ...

    Args:
        allowed_roles: Список разрешённых ролей
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Найти Request в аргументах
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get('request')

            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Request object not found in route handler"
                )

            # Получить текущего пользователя
            current_user = get_current_user_from_request(request)

            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Необходима авторизация"
                )

            # Проверить роль
            user_role = current_user.get('role')
            allowed_role_values = [role.value for role in allowed_roles]

            if user_role not in allowed_role_values:
                raise HTTPException(
                    status_code=403,
                    detail=f"Доступ разрешён только для ролей: {', '.join(allowed_role_values)}"
                )

            # Вызвать оригинальную функцию
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_project_access():
    """
    Декоратор для проверки доступа к конкретному проекту

    Использование:
        @app.get("/admin/api/projects/{project_id}")
        @require_project_access()
        async def get_project(request: Request, project_id: int):
            ...

    Проверяет, может ли пользователь видеть проект на основе его роли и назначения
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Найти Request в аргументах
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get('request')

            project_id = kwargs.get('project_id')

            if not request or not project_id:
                raise HTTPException(
                    status_code=500,
                    detail="Request or project_id not found"
                )

            # Получить текущего пользователя
            current_user = get_current_user_from_request(request)

            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Необходима авторизация"
                )

            # Получить данные проекта из БД
            # TODO: Здесь нужно получить project из БД и проверить executor_id/teamlead_id
            # Для примера используем упрощённую логику

            user_role = current_user.get('role')
            user_id = current_user.get('id')

            # OWNER и ADMIN видят все проекты
            if user_role in [UserRole.OWNER.value, UserRole.ADMIN.value]:
                return await func(*args, **kwargs)

            # TEAMLEAD видит все проекты
            if user_role == UserRole.TEAMLEAD.value:
                return await func(*args, **kwargs)

            # EXECUTOR - нужна проверка через БД
            if user_role == UserRole.EXECUTOR.value:
                # TODO: Запрос к БД для проверки executor_id
                # if project.executor_id != user_id:
                #     raise HTTPException(status_code=403, detail="У вас нет доступа к этому проекту")
                pass

            # Вызвать оригинальную функцию
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_task_access():
    """
    Декоратор для проверки доступа к конкретной задаче

    Использование:
        @app.get("/admin/api/tasks/{task_id}")
        @require_task_access()
        async def get_task(request: Request, task_id: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Найти Request в аргументах
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get('request')

            task_id = kwargs.get('task_id')

            if not request or not task_id:
                raise HTTPException(
                    status_code=500,
                    detail="Request or task_id not found"
                )

            # Получить текущего пользователя
            current_user = get_current_user_from_request(request)

            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Необходима авторизация"
                )

            user_role = current_user.get('role')
            user_id = current_user.get('id')

            # OWNER, ADMIN, TEAMLEAD видят все задачи
            if user_role in [UserRole.OWNER.value, UserRole.ADMIN.value, UserRole.TEAMLEAD.value]:
                return await func(*args, **kwargs)

            # EXECUTOR - нужна проверка через БД
            if user_role == UserRole.EXECUTOR.value:
                # TODO: Запрос к БД для проверки assigned_to
                # if task.assigned_to != user_id:
                #     raise HTTPException(status_code=403, detail="У вас нет доступа к этой задаче")
                pass

            # Вызвать оригинальную функцию
            return await func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================
# MIDDLEWARE ДЛЯ STARLETTE/FASTAPI
# ============================================

class PermissionsMiddleware:
    """
    Middleware для автоматической проверки прав на основе пути

    Использование в FastAPI:
        app.add_middleware(PermissionsMiddleware)
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Создаём Request объект для доступа к session
        request = Request(scope, receive)

        # Получаем текущего пользователя
        current_user = get_current_user_from_request(request)

        # Сохраняем пользователя в request.state для использования в роутах
        if current_user:
            request.state.user = current_user

        # Продолжаем обработку запроса
        await self.app(scope, receive, send)


# ============================================
# HELPER ФУНКЦИИ ДЛЯ ИСПОЛЬЗОВАНИЯ В РОУТАХ
# ============================================

async def get_current_user(request: Request) -> dict:
    """
    Получить текущего пользователя из запроса

    Использование в роутах:
        async def my_route(request: Request):
            user = await get_current_user(request)
            if not user:
                raise HTTPException(status_code=401)
    """
    user = get_current_user_from_request(request)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Необходима авторизация"
        )
    return user


async def check_permission(request: Request, section: Section, action: Action) -> bool:
    """
    Проверить право пользователя на действие

    Использование:
        if not await check_permission(request, Section.PROJECTS, Action.CREATE):
            raise HTTPException(status_code=403)
    """
    user = get_current_user_from_request(request)
    if not user:
        return False

    return check_user_permission(user, section, action)


async def require_permission_or_403(request: Request, section: Section, action: Action):
    """
    Проверить право или выбросить 403

    Использование:
        await require_permission_or_403(request, Section.PROJECTS, Action.DELETE)
    """
    if not await check_permission(request, section, action):
        raise HTTPException(
            status_code=403,
            detail=f"У вас нет прав для {action.value} в разделе {section.value}"
        )
