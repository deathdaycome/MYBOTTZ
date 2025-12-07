"""
Роутер для управления детальными правами доступа к UI элементам
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json
from pathlib import Path

from app.database.database import get_db
from app.database.models import AdminUser, UIElementPermission
from app.admin.auth import get_current_admin_user

# Зависимость для проверки, что текущий пользователь - владелец
def require_owner(current_user: dict = Depends(get_current_admin_user)):
    """Проверяет, что текущий пользователь имеет роль owner"""
    if current_user.get("role") != "owner":
        raise HTTPException(
            status_code=403,
            detail="Только владелец может выполнять эту операцию"
        )
    return current_user

router = APIRouter(prefix="/api/ui-permissions", tags=["ui-permissions"])

# Загружаем структуру UI элементов
UI_ELEMENTS_FILE = Path(__file__).parent.parent.parent / "config" / "ui_elements_structure.json"

def load_ui_elements_structure():
    """Загрузить структуру UI элементов из JSON файла"""
    try:
        with open(UI_ELEMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


@router.get("/structure")
async def get_ui_structure(
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить структуру всех UI элементов системы
    Возвращает полную иерархию модулей и элементов для построения UI редактора прав
    """
    structure = load_ui_elements_structure()

    return {
        "success": True,
        "structure": structure
    }


@router.get("/user/{user_id}")
async def get_user_ui_permissions(
    user_id: int,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить все UI права конкретного пользователя
    Возвращает словарь прав в формате: {module.element_id: is_enabled}
    """
    # Проверяем существование пользователя
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получаем все права пользователя
    permissions = db.query(UIElementPermission).filter(
        UIElementPermission.admin_user_id == user_id
    ).all()

    # Формируем словарь прав
    permissions_dict = {}
    for perm in permissions:
        key = f"{perm.module}.{perm.element_id}"
        permissions_dict[key] = {
            "is_enabled": perm.is_enabled,
            "element_type": perm.element_type,
            "description": perm.description
        }

    return {
        "success": True,
        "user_id": user_id,
        "username": user.username,
        "role": user.role,
        "permissions": permissions_dict
    }


@router.post("/user/{user_id}/update")
async def update_user_ui_permissions(
    user_id: int,
    request: Request,
    current_admin: dict = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Обновить UI права пользователя

    Тело запроса:
    {
        "permissions": {
            "projects.field.title": true,
            "projects.button.edit": false,
            ...
        }
    }
    """
    # Проверяем существование пользователя
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Парсим тело запроса
    try:
        data = await request.json()
        permissions_update = data.get("permissions", {})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}")

    # Загружаем структуру элементов
    ui_structure = load_ui_elements_structure()

    updated_count = 0
    created_count = 0

    # Обрабатываем каждое право
    for full_element_id, is_enabled in permissions_update.items():
        # Разбираем идентификатор: "projects.field.title" -> module="projects", element_id="field.title"
        parts = full_element_id.split(".", 1)
        if len(parts) != 2:
            continue

        module, element_id = parts

        # Проверяем существование элемента в структуре
        if module not in ui_structure:
            continue

        if element_id not in ui_structure[module]["elements"]:
            continue

        element_info = ui_structure[module]["elements"][element_id]
        element_type = element_info.get("type", "field")
        description = element_info.get("name", "")

        # Ищем существующее право
        existing_perm = db.query(UIElementPermission).filter(
            UIElementPermission.admin_user_id == user_id,
            UIElementPermission.module == module,
            UIElementPermission.element_id == element_id
        ).first()

        if existing_perm:
            # Обновляем существующее право
            existing_perm.is_enabled = is_enabled
            updated_count += 1
        else:
            # Создаем новое право
            new_perm = UIElementPermission(
                admin_user_id=user_id,
                module=module,
                element_type=element_type,
                element_id=element_id,
                is_enabled=is_enabled,
                description=description
            )
            db.add(new_perm)
            created_count += 1

    try:
        db.commit()
        return {
            "success": True,
            "message": f"Права обновлены: {updated_count} изменено, {created_count} создано",
            "updated": updated_count,
            "created": created_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения: {str(e)}")


@router.post("/user/{user_id}/reset")
async def reset_user_ui_permissions(
    user_id: int,
    current_admin: dict = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Сбросить все UI права пользователя (удалить все ограничения, дать полный доступ)
    """
    # Проверяем существование пользователя
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удаляем все права пользователя
    deleted_count = db.query(UIElementPermission).filter(
        UIElementPermission.admin_user_id == user_id
    ).delete()

    try:
        db.commit()
        return {
            "success": True,
            "message": f"Удалено {deleted_count} прав доступа. Пользователь получил полный доступ ко всем элементам.",
            "deleted": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сброса прав: {str(e)}")


@router.post("/user/{user_id}/enable-all")
async def enable_all_ui_permissions(
    user_id: int,
    current_admin: dict = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Включить все UI элементы для пользователя
    Создает записи для всех элементов с is_enabled=True
    """
    # Проверяем существование пользователя
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Загружаем структуру элементов
    ui_structure = load_ui_elements_structure()

    created_count = 0
    updated_count = 0

    # Создаем/обновляем права для всех элементов
    for module, module_data in ui_structure.items():
        for element_id, element_info in module_data["elements"].items():
            # Ищем существующее право
            existing_perm = db.query(UIElementPermission).filter(
                UIElementPermission.admin_user_id == user_id,
                UIElementPermission.module == module,
                UIElementPermission.element_id == element_id
            ).first()

            if existing_perm:
                existing_perm.is_enabled = True
                updated_count += 1
            else:
                new_perm = UIElementPermission(
                    admin_user_id=user_id,
                    module=module,
                    element_type=element_info.get("type", "field"),
                    element_id=element_id,
                    is_enabled=True,
                    description=element_info.get("name", "")
                )
                db.add(new_perm)
                created_count += 1

    try:
        db.commit()
        return {
            "success": True,
            "message": f"Все элементы включены: {updated_count} обновлено, {created_count} создано",
            "updated": updated_count,
            "created": created_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.post("/user/{user_id}/copy-from/{source_user_id}")
async def copy_ui_permissions(
    user_id: int,
    source_user_id: int,
    current_admin: dict = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Скопировать UI права от другого пользователя
    """
    # Проверяем существование обоих пользователей
    target_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    source_user = db.query(AdminUser).filter(AdminUser.id == source_user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Целевой пользователь не найден")
    if not source_user:
        raise HTTPException(status_code=404, detail="Исходный пользователь не найден")

    # Получаем права исходного пользователя
    source_permissions = db.query(UIElementPermission).filter(
        UIElementPermission.admin_user_id == source_user_id
    ).all()

    # Удаляем текущие права целевого пользователя
    db.query(UIElementPermission).filter(
        UIElementPermission.admin_user_id == user_id
    ).delete()

    # Копируем права
    created_count = 0
    for source_perm in source_permissions:
        new_perm = UIElementPermission(
            admin_user_id=user_id,
            module=source_perm.module,
            element_type=source_perm.element_type,
            element_id=source_perm.element_id,
            is_enabled=source_perm.is_enabled,
            description=source_perm.description
        )
        db.add(new_perm)
        created_count += 1

    try:
        db.commit()
        return {
            "success": True,
            "message": f"Скопировано {created_count} прав от пользователя {source_user.username}",
            "copied": created_count,
            "source_user": source_user.username
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка копирования: {str(e)}")


@router.get("/module/{module_name}/elements")
async def get_module_elements(
    module_name: str,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить список всех элементов конкретного модуля
    """
    ui_structure = load_ui_elements_structure()

    if module_name not in ui_structure:
        raise HTTPException(status_code=404, detail=f"Модуль '{module_name}' не найден")

    module_data = ui_structure[module_name]

    return {
        "success": True,
        "module": module_name,
        "name": module_data.get("name", module_name),
        "elements": module_data.get("elements", {})
    }


@router.get("/check")
async def check_ui_permission(
    module: str,
    element_id: str,
    user_id: Optional[int] = None,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Проверить доступ к конкретному UI элементу для пользователя
    Если user_id не указан, проверяет для текущего пользователя
    """
    target_user_id = user_id if user_id else current_admin.get("id")

    # Владелец всегда имеет доступ ко всему
    target_user = db.query(AdminUser).filter(AdminUser.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if target_user.role == 'owner':
        return {
            "success": True,
            "has_access": True,
            "reason": "owner_full_access"
        }

    # Ищем конкретное право
    permission = db.query(UIElementPermission).filter(
        UIElementPermission.admin_user_id == target_user_id,
        UIElementPermission.module == module,
        UIElementPermission.element_id == element_id
    ).first()

    # Если право не установлено явно, по умолчанию доступ разрешен
    has_access = permission.is_enabled if permission else True
    reason = "explicit_permission" if permission else "default_allow"

    return {
        "success": True,
        "has_access": has_access,
        "reason": reason,
        "permission": permission.to_dict() if permission else None
    }


@router.get("/statistics")
async def get_ui_permissions_statistics(
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по UI правам
    """
    # Всего пользователей
    total_users = db.query(AdminUser).filter(AdminUser.is_active == True).count()

    # Всего установленных прав
    total_permissions = db.query(UIElementPermission).count()

    # Пользователи с ограничениями
    users_with_restrictions = db.query(UIElementPermission.admin_user_id).distinct().count()

    # Статистика по модулям
    ui_structure = load_ui_elements_structure()
    total_available_elements = sum(len(m["elements"]) for m in ui_structure.values())

    # Самые ограниченные элементы
    from sqlalchemy import func
    most_restricted = db.query(
        UIElementPermission.module,
        UIElementPermission.element_id,
        func.count(UIElementPermission.id).label('restriction_count')
    ).filter(
        UIElementPermission.is_enabled == False
    ).group_by(
        UIElementPermission.module,
        UIElementPermission.element_id
    ).order_by(
        func.count(UIElementPermission.id).desc()
    ).limit(10).all()

    return {
        "success": True,
        "statistics": {
            "total_users": total_users,
            "users_with_custom_permissions": users_with_restrictions,
            "total_permission_records": total_permissions,
            "total_available_elements": total_available_elements,
            "modules_count": len(ui_structure),
            "most_restricted_elements": [
                {
                    "module": r.module,
                    "element_id": r.element_id,
                    "restriction_count": r.restriction_count
                } for r in most_restricted
            ]
        }
    }
