"""
API для динамического меню на основе роли пользователя
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.roles import get_menu_for_role, get_available_sections
from app.core.permissions import get_current_user


router = APIRouter()


@router.get("/api/menu")
async def get_user_menu(request: Request):
    """
    Получить структуру меню для текущего пользователя

    Returns:
        {
            "success": true,
            "menu": [
                {
                    "group": "Работа",
                    "items": [
                        {"key": "dashboard", "title": "Дашборд", "icon": "📊", "path": "/"},
                        ...
                    ]
                },
                ...
            ],
            "sections": ["dashboard", "projects", ...]
        }
    """
    try:
        # Получить текущего пользователя
        current_user = await get_current_user(request)
        user_role = current_user.get('role')

        if not user_role:
            raise HTTPException(status_code=401, detail="Роль пользователя не определена")

        # Получить меню для роли
        menu = get_menu_for_role(user_role)

        # Получить список доступных разделов
        sections = get_available_sections(user_role)
        section_names = [section.value for section in sections]

        return JSONResponse({
            "success": True,
            "menu": menu,
            "sections": section_names,
            "role": user_role
        })

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка получения меню: {str(e)}"
        }, status_code=500)


@router.get("/api/permissions/check")
async def check_user_permissions(request: Request, section: str = None, action: str = None):
    """
    Проверить права пользователя на конкретное действие

    Query params:
        section: Раздел системы (projects, tasks, etc.)
        action: Действие (view, create, edit, delete, etc.)

    Returns:
        {
            "success": true,
            "has_permission": true
        }
    """
    try:
        from app.core.roles import Section, Action, has_permission

        # Получить текущего пользователя
        current_user = await get_current_user(request)
        user_role = current_user.get('role')

        if not user_role:
            raise HTTPException(status_code=401, detail="Роль пользователя не определена")

        # Если не указаны section и action - вернуть все права
        if not section or not action:
            return JSONResponse({
                "success": True,
                "role": user_role,
                "message": "Укажите section и action для проверки"
            })

        # Проверить право
        try:
            section_enum = Section(section)
            action_enum = Action(action)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Неверный section или action: {str(e)}")

        has_perm = has_permission(user_role, section_enum, action_enum)

        return JSONResponse({
            "success": True,
            "has_permission": has_perm,
            "role": user_role,
            "section": section,
            "action": action
        })

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Ошибка проверки прав: {str(e)}"
        }, status_code=500)
