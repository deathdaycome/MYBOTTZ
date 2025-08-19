"""
Middleware для управления ролями и доступами
"""

from fastapi import HTTPException, Depends, status
from typing import List, Optional
from .auth import get_current_admin_user

# Определение доступов для каждой роли
ROLE_PERMISSIONS = {
    "owner": [
        # Полный доступ ко всем разделам
        "dashboard.view",
        "projects.*",
        "users.*",
        "clients.*",
        "leads.*",
        "deals.*",
        "finance.*",
        "reports.*",
        "settings.*",
        "executors.*",
        "revisions.*",
        "notifications.*",
        "portfolio.*",
        "services.*",
        "analytics.*",
        "backup.*"
    ],
    
    "admin": [
        # Администратор - почти полный доступ, кроме критических настроек
        "dashboard.view",
        "projects.*",
        "users.view",
        "users.create",
        "users.edit",
        "clients.*",
        "leads.*",
        "deals.*",
        "finance.view",
        "finance.create",
        "reports.*",
        "executors.*",
        "revisions.*",
        "notifications.*",
        "portfolio.*",
        "services.*",
        "analytics.*"
    ],
    
    "sales": [
        # Продажник - работа с лидами и клиентами
        "dashboard.view",
        "leads.*",
        "clients.*",
        "deals.*",
        "tasks.view",
        "tasks.create",
        "tasks.edit.own",
        "projects.view",
        "reports.sales",
        "notifications.view.own"
    ],
    
    "executor": [
        # Исполнитель - только свои проекты и задачи
        "dashboard.view",
        "projects.view.assigned",
        "projects.edit.assigned",
        "tasks.view.assigned",
        "tasks.edit.assigned",
        "revisions.view.assigned",
        "revisions.edit.assigned",
        "notifications.view.own",
        "portfolio.view",
        "portfolio.create"
    ]
}

def check_permission(user: dict, permission: str) -> bool:
    """
    Проверяет, есть ли у пользователя определенное разрешение
    """
    user_role = user.get("role", "executor")
    role_permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    # Проверяем точное совпадение
    if permission in role_permissions:
        return True
    
    # Проверяем wildcard разрешения (например, projects.*)
    for perm in role_permissions:
        if perm.endswith(".*"):
            prefix = perm[:-2]
            if permission.startswith(prefix + "."):
                return True
    
    return False

def require_permission(permission: str):
    """
    Декоратор для проверки разрешений
    """
    def permission_checker(current_user: dict = Depends(get_current_admin_user)):
        if not check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав для выполнения этого действия. Требуется: {permission}"
            )
        return current_user
    return permission_checker

def require_any_permission(permissions: List[str]):
    """
    Проверяет, есть ли у пользователя хотя бы одно из указанных разрешений
    """
    def permission_checker(current_user: dict = Depends(get_current_admin_user)):
        for permission in permissions:
            if check_permission(current_user, permission):
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Недостаточно прав. Требуется одно из: {', '.join(permissions)}"
        )
    return permission_checker

def require_role(roles: List[str]):
    """
    Проверяет, есть ли у пользователя одна из указанных ролей
    """
    def role_checker(current_user: dict = Depends(get_current_admin_user)):
        user_role = current_user.get("role", "executor")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется роль: {', '.join(roles)}"
            )
        return current_user
    return role_checker

def get_allowed_menu_items(user_role: str) -> List[str]:
    """
    Возвращает список разрешенных пунктов меню для роли
    """
    menu_permissions = {
        "owner": [
            "dashboard", "projects", "users", "clients", "leads", "deals",
            "finance", "reports", "executors", "settings", "revisions",
            "portfolio", "services", "analytics", "backup"
        ],
        "admin": [
            "dashboard", "projects", "users", "clients", "leads", "deals",
            "finance", "reports", "executors", "revisions", "portfolio",
            "services", "analytics"
        ],
        "sales": [
            "dashboard", "leads", "clients", "deals", "tasks", "projects", "reports"
        ],
        "executor": [
            "dashboard", "projects", "tasks", "revisions", "portfolio"
        ]
    }
    
    return menu_permissions.get(user_role, ["dashboard"])

def filter_data_by_role(data: list, user: dict, data_type: str) -> list:
    """
    Фильтрует данные в зависимости от роли пользователя
    """
    user_role = user.get("role", "executor")
    user_id = user.get("id")
    
    # Owner и Admin видят все
    if user_role in ["owner", "admin"]:
        return data
    
    # Sales видит все лиды и клиентов
    if user_role == "sales" and data_type in ["leads", "clients", "deals"]:
        return data
    
    # Executor видит только свои назначенные элементы
    if user_role == "executor":
        if data_type == "projects":
            return [item for item in data if item.get("assigned_executor_id") == user_id]
        elif data_type == "tasks":
            return [item for item in data if item.get("assigned_to_id") == user_id]
        elif data_type == "revisions":
            return [item for item in data if item.get("assigned_to_id") == user_id]
    
    return []