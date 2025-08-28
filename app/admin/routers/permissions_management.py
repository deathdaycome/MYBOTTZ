"""
Роутер для детального управления правами доступа исполнителей
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from ...database.database import get_db
from ...database.models import AdminUser
from ...database.rbac_models import Role, Permission, DataAccessRule
from ...database.crm_models import Client, Lead, Deal
from ...services.rbac_service import RBACService
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user
from ..navigation import get_navigation_items

logger = get_logger(__name__)
router = APIRouter(tags=["permissions"])
templates = Jinja2Templates(directory="app/admin/templates")

# Определяем все доступные модули и их права
AVAILABLE_MODULES = {
    "dashboard": {
        "name": "Дашборд",
        "permissions": ["view", "widgets.manage"],
        "description": "Главная страница с аналитикой"
    },
    "projects": {
        "name": "Проекты", 
        "permissions": ["view", "create", "edit", "delete", "export", "assign"],
        "description": "Управление проектами и задачами"
    },
    "clients": {
        "name": "Клиенты",
        "permissions": ["view", "create", "edit", "delete", "export", "contact"],
        "description": "База клиентов и контакты"
    },
    "leads": {
        "name": "Лиды",
        "permissions": ["view", "create", "edit", "delete", "export", "convert"],
        "description": "Работа с потенциальными клиентами"
    },
    "deals": {
        "name": "Сделки",
        "permissions": ["view", "create", "edit", "delete", "export", "close"],
        "description": "Управление сделками и продажами"
    },
    "finance": {
        "name": "Финансы",
        "permissions": ["view", "create", "edit", "delete", "export", "reports"],
        "description": "Финансовый учет и отчеты"
    },
    "documents": {
        "name": "Документы",
        "permissions": ["view", "create", "edit", "delete", "generate", "sign"],
        "description": "Управление документами и шаблонами"
    },
    "reports": {
        "name": "Отчеты",
        "permissions": ["view", "create", "export", "schedule"],
        "description": "Аналитические отчеты"
    },
    "settings": {
        "name": "Настройки",
        "permissions": ["view", "edit", "system.manage"],
        "description": "Системные настройки"
    },
    "users": {
        "name": "Пользователи",
        "permissions": ["view", "create", "edit", "delete", "permissions.manage"],
        "description": "Управление пользователями и правами"
    },
    "avito": {
        "name": "Avito интеграция",
        "permissions": ["view", "messages.send", "chats.manage", "settings.edit"],
        "description": "Работа с Avito мессенджером"
    }
}

@router.get("/", response_class=HTMLResponse)
async def permissions_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Главная страница управления правами доступа"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав для управления правами доступа")
    
    # Получаем навигацию
    from ..navigation import get_navigation_items
    navigation_items = get_navigation_items(current_user, db)
    
    # Получаем всех пользователей (кроме владельца)
    users = db.query(AdminUser).filter(AdminUser.role != "owner").all()
    
    # Получаем все роли
    try:
        roles = rbac.get_all_roles()
    except Exception as e:
        logger.error(f"Ошибка получения ролей: {str(e)}")
        roles = []
    
    return templates.TemplateResponse(
        "permissions_management.html",
        {
            "request": request,
            "user": current_user,
            "username": current_user.get("username") if isinstance(current_user, dict) else current_user.username,
            "navigation_items": navigation_items,
            "users": users,
            "roles": roles,
            "available_modules": AVAILABLE_MODULES
        }
    )

@router.get("/user/{user_id}", response_class=JSONResponse)
async def get_user_permissions(
    user_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить детальные права пользователя"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получаем роли пользователя
    try:
        user_roles = rbac.get_user_roles(user_id)
    except Exception as e:
        logger.warning(f"Не удалось получить роли пользователя {user_id}: {str(e)}")
        user_roles = []
    
    # Получаем разрешения пользователя (временно возвращаем пустой список)
    try:
        user_permissions = rbac.get_user_permissions(user_id)
    except Exception as e:
        logger.warning(f"Не удалось получить разрешения пользователя {user_id}: {str(e)}")
        user_permissions = []
    
    # Получаем правила доступа к данным
    data_access_rules = db.query(DataAccessRule).filter(
        DataAccessRule.user_id == user_id,
        DataAccessRule.is_active == True
    ).all()
    
    # Формируем детальные права по модулям
    module_permissions = {}
    for module, config in AVAILABLE_MODULES.items():
        module_permissions[module] = {
            "enabled": False,
            "permissions": {},
            "data_access": {
                "type": "none",  # none, own, team, all
                "can_view": False,
                "can_edit": False, 
                "can_delete": False,
                "can_export": False
            }
        }
        
        # Проверяем каждое разрешение модуля
        for perm in config["permissions"]:
            perm_name = f"{module}.{perm}"
            module_permissions[module]["permissions"][perm] = perm_name in user_permissions
            if perm_name in user_permissions:
                module_permissions[module]["enabled"] = True
        
        # Проверяем правила доступа к данным
        for rule in data_access_rules:
            if rule.entity_type == module:
                module_permissions[module]["data_access"] = {
                    "type": rule.access_type,
                    "can_view": rule.can_view,
                    "can_edit": rule.can_edit,
                    "can_delete": rule.can_delete,
                    "can_export": rule.can_export
                }
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        },
        "roles": [role.to_dict() for role in user_roles],
        "module_permissions": module_permissions,
        "available_modules": AVAILABLE_MODULES
    }

@router.post("/user/{user_id}/update", response_class=JSONResponse)
async def update_user_permissions(
    user_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить права пользователя"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получаем данные из запроса
    data = await request.json()
    module_permissions = data.get("module_permissions", {})
    
    try:
        # Обновляем разрешения и правила доступа
        await _update_user_module_permissions(user_id, module_permissions, rbac, db, current_user)
        
        # Логируем изменения  
        from ...database.audit_models import AuditLog, AuditActionType, AuditEntityType
        
        audit_log = AuditLog(
            action_type=AuditActionType.UPDATE,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            new_values=module_permissions,
            description=f"Обновлены права доступа пользователя: {user.username}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.email if hasattr(current_user, 'email') else current_user.get('email')
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Права пользователя {user.username} обновлены пользователем {current_user.username if hasattr(current_user, 'username') else current_user.get('username', 'Unknown')}")
        
        return {"success": True, "message": "Права пользователя успешно обновлены"}
        
    except Exception as e:
        logger.error(f"Ошибка обновления прав пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления прав: {str(e)}")

@router.get("/role/{role_name}/template", response_class=JSONResponse) 
async def get_role_permissions_template(
    role_name: str,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить шаблон прав для роли"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Предустановленные шаблоны прав для ролей
    role_templates = {
        "salesperson": {
            "name": "Продажник",
            "modules": {
                "dashboard": {
                    "enabled": True,
                    "permissions": {"view": True, "widgets.manage": False},
                    "data_access": {"type": "own", "can_view": True, "can_edit": False, "can_delete": False, "can_export": True}
                },
                "leads": {
                    "enabled": True,
                    "permissions": {"view": True, "create": True, "edit": True, "delete": False, "export": True, "convert": True},
                    "data_access": {"type": "own", "can_view": True, "can_edit": True, "can_delete": False, "can_export": True}
                },
                "clients": {
                    "enabled": True,
                    "permissions": {"view": True, "create": True, "edit": True, "delete": False, "export": True, "contact": True},
                    "data_access": {"type": "own", "can_view": True, "can_edit": True, "can_delete": False, "can_export": True}
                },
                "deals": {
                    "enabled": True,
                    "permissions": {"view": True, "create": True, "edit": True, "delete": False, "export": True, "close": True},
                    "data_access": {"type": "own", "can_view": True, "can_edit": True, "can_delete": False, "can_export": True}
                },
                "projects": {
                    "enabled": False,
                    "permissions": {"view": False, "create": False, "edit": False, "delete": False, "export": False, "assign": False},
                    "data_access": {"type": "none", "can_view": False, "can_edit": False, "can_delete": False, "can_export": False}
                },
                "finance": {
                    "enabled": False,
                    "permissions": {"view": False, "create": False, "edit": False, "delete": False, "export": False, "reports": False},
                    "data_access": {"type": "none", "can_view": False, "can_edit": False, "can_delete": False, "can_export": False}
                },
                "avito": {
                    "enabled": True,
                    "permissions": {"view": True, "messages.send": True, "chats.manage": False, "settings.edit": False},
                    "data_access": {"type": "own", "can_view": True, "can_edit": True, "can_delete": False, "can_export": False}
                }
            }
        },
        "executor": {
            "name": "Исполнитель", 
            "modules": {
                "dashboard": {
                    "enabled": True,
                    "permissions": {"view": True, "widgets.manage": False},
                    "data_access": {"type": "own", "can_view": True, "can_edit": False, "can_delete": False, "can_export": False}
                },
                "projects": {
                    "enabled": True,
                    "permissions": {"view": True, "create": False, "edit": True, "delete": False, "export": False, "assign": False},
                    "data_access": {"type": "own", "can_view": True, "can_edit": True, "can_delete": False, "can_export": False}
                },
                "clients": {
                    "enabled": True,
                    "permissions": {"view": True, "create": False, "edit": False, "delete": False, "export": False, "contact": True},
                    "data_access": {"type": "team", "can_view": True, "can_edit": False, "can_delete": False, "can_export": False}
                },
                "documents": {
                    "enabled": True,
                    "permissions": {"view": True, "create": True, "edit": True, "delete": False, "generate": True, "sign": False},
                    "data_access": {"type": "own", "can_view": True, "can_edit": True, "can_delete": False, "can_export": True}
                },
                "leads": {
                    "enabled": False,
                    "permissions": {"view": False, "create": False, "edit": False, "delete": False, "export": False, "convert": False},
                    "data_access": {"type": "none", "can_view": False, "can_edit": False, "can_delete": False, "can_export": False}
                },
                "deals": {
                    "enabled": False,
                    "permissions": {"view": False, "create": False, "edit": False, "delete": False, "export": False, "close": False},
                    "data_access": {"type": "none", "can_view": False, "can_edit": False, "can_delete": False, "can_export": False}
                },
                "finance": {
                    "enabled": False,
                    "permissions": {"view": False, "create": False, "edit": False, "delete": False, "export": False, "reports": False},
                    "data_access": {"type": "none", "can_view": False, "can_edit": False, "can_delete": False, "can_export": False}
                }
            }
        }
    }
    
    template = role_templates.get(role_name)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон роли не найден")
    
    return template


@router.post("/user/{user_id}/apply-role-template", response_class=JSONResponse)
async def apply_role_template(
    user_id: int,
    role_name: str,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Применить шаблон роли к пользователю"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    try:
        # Получаем шаблон роли
        response = await get_role_permissions_template(role_name, current_user, db)
        if hasattr(response, 'status_code') and response.status_code != 200:
            raise HTTPException(status_code=404, detail="Шаблон роли не найден")
        
        template_data = response if isinstance(response, dict) else response.body
        
        # Применяем шаблон
        await _update_user_module_permissions(user_id, template_data['modules'], rbac, db, current_user)
        
        return {"success": True, "message": f"Шаблон роли '{template_data['name']}' успешно применен"}
        
    except Exception as e:
        logger.error(f"Ошибка применения шаблона роли для пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка применения шаблона: {str(e)}")


@router.get("/statistics", response_class=JSONResponse)
async def get_permissions_statistics(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить статистику по правам доступа"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        # Общая статистика пользователей
        total_users = db.query(AdminUser).filter(AdminUser.role != "owner").count()
        active_users = db.query(AdminUser).filter(
            AdminUser.role != "owner", 
            AdminUser.is_active == True
        ).count()
        
        # Статистика по ролям
        users_by_role = {}
        users_roles_query = db.query(AdminUser.role, db.func.count(AdminUser.id)).filter(
            AdminUser.role != "owner"
        ).group_by(AdminUser.role).all()
        
        for role, count in users_roles_query:
            users_by_role[role] = count
        
        # Статистика по модулям
        module_access_stats = {}
        for module in AVAILABLE_MODULES.keys():
            # Подсчитываем пользователей с доступом к модулю
            users_with_access = db.query(DataAccessRule).filter(
                DataAccessRule.entity_type == module,
                DataAccessRule.is_active == True,
                DataAccessRule.access_type != "none"
            ).count()
            
            module_access_stats[module] = users_with_access
        
        # Статистика по правам
        total_permissions = db.query(Permission).count()
        active_rules = db.query(DataAccessRule).filter(DataAccessRule.is_active == True).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
                "by_role": users_by_role
            },
            "modules": module_access_stats,
            "permissions": {
                "total_permissions": total_permissions,
                "active_rules": active_rules
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики прав: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.post("/user/{user_id}/reset", response_class=JSONResponse)
async def reset_user_permissions(
    user_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Сбросить все права пользователя"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "users.permissions.manage"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    try:
        # Удаляем все разрешения пользователя
        db.execute(user_permissions.delete().where(user_permissions.c.user_id == user_id))
        
        # Удаляем все правила доступа к данным
        db.query(DataAccessRule).filter(DataAccessRule.user_id == user_id).delete()
        
        db.commit()
        
        # Логируем действие
        from ...database.audit_models import AuditLog, AuditActionType, AuditEntityType
        
        audit_log = AuditLog(
            action_type=AuditActionType.DELETE,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            description=f"Сброшены все права пользователя: {user.username}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.email if hasattr(current_user, 'email') else current_user.get('email')
        )
        db.add(audit_log)
        db.commit()
        
        return {"success": True, "message": "Права пользователя успешно сброшены"}
        
    except Exception as e:
        logger.error(f"Ошибка сброса прав пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сброса прав: {str(e)}")


async def _update_user_module_permissions(user_id: int, module_permissions: Dict[str, Any], 
                                        rbac: RBACService, db: Session, current_user: AdminUser):
    """Обновить разрешения пользователя по модулям"""
    
    # Сначала удаляем все существующие прямые разрешения пользователя
    from ...database.rbac_models import user_permissions
    db.execute(user_permissions.delete().where(user_permissions.c.user_id == user_id))
    
    # Удаляем все правила доступа к данным пользователя
    db.query(DataAccessRule).filter(DataAccessRule.user_id == user_id).delete()
    
    # Создаем новые разрешения и правила
    for module, config in module_permissions.items():
        if not config.get("enabled", False):
            continue
            
        # Создаем/получаем разрешения для модуля
        permissions_config = config.get("permissions", {})
        for perm_action, enabled in permissions_config.items():
            if enabled:
                perm_name = f"{module}.{perm_action}"
                
                # Найти или создать разрешение
                permission = db.query(Permission).filter(Permission.name == perm_name).first()
                if not permission:
                    permission = Permission(
                        name=perm_name,
                        display_name=f"{AVAILABLE_MODULES.get(module, {}).get('name', module)} - {perm_action}",
                        module=module,
                        action=perm_action,
                        description=f"Разрешение {perm_action} для модуля {module}"
                    )
                    db.add(permission)
                    db.flush()  # Получаем ID без полного commit
                
                # Добавляем разрешение пользователю
                db.execute(user_permissions.insert().values(
                    user_id=user_id,
                    permission_id=permission.id
                ))
        
        # Создаем правило доступа к данным
        data_access = config.get("data_access", {})
        if data_access.get("type", "none") != "none":
            rule = DataAccessRule(
                user_id=user_id,
                entity_type=module,
                access_type=data_access["type"],
                can_view=data_access.get("can_view", False),
                can_edit=data_access.get("can_edit", False),
                can_delete=data_access.get("can_delete", False),
                can_export=data_access.get("can_export", False),
                priority=10  # Пользовательские правила имеют высокий приоритет
            )
            db.add(rule)
    
    db.commit()