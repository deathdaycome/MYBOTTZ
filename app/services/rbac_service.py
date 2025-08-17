"""
Сервис для управления ролями и правами доступа (RBAC)
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from functools import wraps
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta

from ..database.models import AdminUser
from ..database.rbac_models import (
    Role, Permission, DataAccessRule, Team, TeamMembership,
    role_permissions, user_roles, user_permissions
)
from ..database.crm_models import Client, Lead, Deal
from ..database.audit_models import AuditLog
from ..config.logging import get_logger

logger = get_logger(__name__)


class RBACService:
    """Сервис управления ролями и правами доступа"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === Управление ролями ===
    
    def get_all_roles(self, include_inactive: bool = False) -> List[Role]:
        """Получить все роли"""
        query = self.db.query(Role)
        if not include_inactive:
            query = query.filter(Role.is_active == True)
        return query.order_by(Role.level.desc()).all()
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Получить роль по имени"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def create_role(self, data: Dict[str, Any], created_by: AdminUser) -> Role:
        """Создать новую роль"""
        role = Role(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description'),
            level=data.get('level', 0),
            max_projects=data.get('max_projects'),
            max_clients=data.get('max_clients'),
            max_deals=data.get('max_deals'),
            modules_access=data.get('modules_access', {}),
            dashboard_widgets=data.get('dashboard_widgets', [])
        )
        
        self.db.add(role)
        self.db.commit()
        
        # Логируем действие
        self._log_action(
            action="create",
            entity_type="role",
            entity_id=role.id,
            new_data=role.to_dict(),
            user=created_by,
            description=f"Создана роль: {role.display_name}"
        )
        
        return role
    
    def update_role(self, role_id: int, data: Dict[str, Any], updated_by: AdminUser) -> Role:
        """Обновить роль"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Роль с ID {role_id} не найдена")
        
        if role.is_system:
            # Для системных ролей разрешаем изменять только некоторые поля
            allowed_fields = ['display_name', 'description', 'modules_access', 'dashboard_widgets']
            data = {k: v for k, v in data.items() if k in allowed_fields}
        
        old_data = role.to_dict()
        
        for key, value in data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        role.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Логируем действие
        self._log_action(
            action="update",
            entity_type="role",
            entity_id=role.id,
            old_data=old_data,
            new_data=role.to_dict(),
            user=updated_by,
            description=f"Обновлена роль: {role.display_name}"
        )
        
        return role
    
    def delete_role(self, role_id: int, deleted_by: AdminUser) -> bool:
        """Удалить роль"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Роль с ID {role_id} не найдена")
        
        if role.is_system:
            raise ValueError("Системную роль нельзя удалить")
        
        # Проверяем, есть ли пользователи с этой ролью
        users_with_role = self.db.query(user_roles).filter(
            user_roles.c.role_id == role_id
        ).first()
        
        if users_with_role:
            raise ValueError("Нельзя удалить роль, назначенную пользователям")
        
        old_data = role.to_dict()
        self.db.delete(role)
        self.db.commit()
        
        # Логируем действие
        self._log_action(
            action="delete",
            entity_type="role",
            entity_id=role_id,
            old_data=old_data,
            user=deleted_by,
            description=f"Удалена роль: {old_data['display_name']}"
        )
        
        return True
    
    # === Управление разрешениями ===
    
    def get_all_permissions(self, module: Optional[str] = None) -> List[Permission]:
        """Получить все разрешения"""
        query = self.db.query(Permission)
        if module:
            query = query.filter(Permission.module == module)
        return query.order_by(Permission.module, Permission.action).all()
    
    def assign_permission_to_role(self, role_id: int, permission_id: int, assigned_by: AdminUser) -> bool:
        """Назначить разрешение роли"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not role or not permission:
            raise ValueError("Роль или разрешение не найдены")
        
        # Проверяем, не назначено ли уже
        existing = self.db.query(role_permissions).filter(
            and_(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id == permission_id
            )
        ).first()
        
        if existing:
            return False
        
        # Назначаем
        self.db.execute(
            role_permissions.insert().values(
                role_id=role_id,
                permission_id=permission_id
            )
        )
        self.db.commit()
        
        # Логируем действие
        self._log_action(
            action="assign_permission",
            entity_type="role",
            entity_id=role_id,
            new_data={"permission_id": permission_id, "permission_name": permission.name},
            user=assigned_by,
            description=f"Роли {role.display_name} назначено разрешение {permission.display_name}"
        )
        
        return True
    
    def revoke_permission_from_role(self, role_id: int, permission_id: int, revoked_by: AdminUser) -> bool:
        """Отозвать разрешение у роли"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not role or not permission:
            raise ValueError("Роль или разрешение не найдены")
        
        result = self.db.execute(
            role_permissions.delete().where(
                and_(
                    role_permissions.c.role_id == role_id,
                    role_permissions.c.permission_id == permission_id
                )
            )
        )
        self.db.commit()
        
        if result.rowcount > 0:
            # Логируем действие
            self._log_action(
                action="revoke_permission",
                entity_type="role",
                entity_id=role_id,
                old_data={"permission_id": permission_id, "permission_name": permission.name},
                user=revoked_by,
                description=f"У роли {role.display_name} отозвано разрешение {permission.display_name}"
            )
            return True
        
        return False
    
    # === Управление пользователями ===
    
    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: AdminUser) -> bool:
        """Назначить роль пользователю"""
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            raise ValueError("Пользователь или роль не найдены")
        
        # Проверяем, не назначена ли уже
        existing = self.db.query(user_roles).filter(
            and_(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id
            )
        ).first()
        
        if existing:
            return False
        
        # Назначаем
        self.db.execute(
            user_roles.insert().values(
                user_id=user_id,
                role_id=role_id
            )
        )
        self.db.commit()
        
        # Логируем действие
        self._log_action(
            action="assign_role",
            entity_type="user",
            entity_id=user_id,
            new_data={"role_id": role_id, "role_name": role.name},
            user=assigned_by,
            description=f"Пользователю {user.username} назначена роль {role.display_name}"
        )
        
        return True
    
    def revoke_role_from_user(self, user_id: int, role_id: int, revoked_by: AdminUser) -> bool:
        """Отозвать роль у пользователя"""
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            raise ValueError("Пользователь или роль не найдены")
        
        result = self.db.execute(
            user_roles.delete().where(
                and_(
                    user_roles.c.user_id == user_id,
                    user_roles.c.role_id == role_id
                )
            )
        )
        self.db.commit()
        
        if result.rowcount > 0:
            # Логируем действие
            self._log_action(
                action="revoke_role",
                entity_type="user",
                entity_id=user_id,
                old_data={"role_id": role_id, "role_name": role.name},
                user=revoked_by,
                description=f"У пользователя {user.username} отозвана роль {role.display_name}"
            )
            return True
        
        return False
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """Получить роли пользователя"""
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")
        
        return user.roles
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Получить все разрешения пользователя (через роли и прямые)"""
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")
        
        permissions = set()
        
        # Разрешения через роли
        for role in user.roles:
            if role.is_active:
                for perm in role.permissions:
                    permissions.add(perm.name)
        
        # Прямые разрешения
        for perm in user.additional_permissions:
            permissions.add(perm.name)
        
        return list(permissions)
    
    # === Проверка доступа ===
    
    def check_permission(self, user: AdminUser, permission_name: str) -> bool:
        """Проверить наличие разрешения у пользователя"""
        if not user:
            return False
        
        # Админ с ролью owner имеет все права
        if any(role.name == 'owner' for role in user.roles):
            return True
        
        user_permissions = self.get_user_permissions(user.id)
        return permission_name in user_permissions
    
    def check_data_access(self, user: AdminUser, entity_type: str, entity_id: Optional[int] = None, 
                         action: str = "view") -> bool:
        """Проверить доступ к данным"""
        if not user:
            return False
        
        # Владелец имеет доступ ко всему
        if any(role.name == 'owner' for role in user.roles):
            return True
        
        # Получаем правила доступа для пользователя
        rules = self.db.query(DataAccessRule).filter(
            and_(
                DataAccessRule.is_active == True,
                DataAccessRule.entity_type == entity_type,
                or_(
                    DataAccessRule.user_id == user.id,
                    DataAccessRule.role_id.in_([role.id for role in user.roles])
                )
            )
        ).order_by(DataAccessRule.priority.desc()).all()
        
        for rule in rules:
            # Проверяем тип доступа
            if rule.access_type == "all":
                # Доступ ко всем записям
                return self._check_rule_action(rule, action)
            
            elif rule.access_type == "own" and entity_id:
                # Доступ только к своим записям
                if self._is_own_entity(user, entity_type, entity_id):
                    return self._check_rule_action(rule, action)
            
            elif rule.access_type == "team" and entity_id:
                # Доступ к записям команды
                if self._is_team_entity(user, entity_type, entity_id):
                    return self._check_rule_action(rule, action)
            
            elif rule.access_type == "specific" and entity_id:
                # Доступ к конкретным записям
                if rule.specific_ids and entity_id in rule.specific_ids:
                    return self._check_rule_action(rule, action)
        
        return False
    
    def _check_rule_action(self, rule: DataAccessRule, action: str) -> bool:
        """Проверить разрешенное действие в правиле"""
        action_map = {
            "view": rule.can_view,
            "edit": rule.can_edit,
            "delete": rule.can_delete,
            "export": rule.can_export
        }
        return action_map.get(action, False)
    
    def _is_own_entity(self, user: AdminUser, entity_type: str, entity_id: int) -> bool:
        """Проверить, является ли запись собственной для пользователя"""
        if entity_type == "projects":
            from ..database.models import Project
            entity = self.db.query(Project).filter(Project.id == entity_id).first()
            return entity and (entity.assigned_executor_id == user.id or 
                              entity.responsible_manager_id == user.id)
        
        elif entity_type == "clients":
            entity = self.db.query(Client).filter(Client.id == entity_id).first()
            return entity and entity.manager_id == user.id
        
        elif entity_type == "leads":
            entity = self.db.query(Lead).filter(Lead.id == entity_id).first()
            return entity and entity.manager_id == user.id
        
        elif entity_type == "deals":
            entity = self.db.query(Deal).filter(Deal.id == entity_id).first()
            return entity and (entity.manager_id == user.id or entity.executor_id == user.id)
        
        return False
    
    def _is_team_entity(self, user: AdminUser, entity_type: str, entity_id: int) -> bool:
        """Проверить, является ли запись доступной для команды пользователя"""
        # Получаем команды пользователя
        user_teams = self.db.query(TeamMembership).filter(
            and_(
                TeamMembership.user_id == user.id,
                TeamMembership.is_active == True
            )
        ).all()
        
        if not user_teams:
            return False
        
        team_ids = [tm.team_id for tm in user_teams]
        
        # Получаем членов команд
        team_members = self.db.query(TeamMembership).filter(
            and_(
                TeamMembership.team_id.in_(team_ids),
                TeamMembership.is_active == True
            )
        ).all()
        
        team_user_ids = list(set([tm.user_id for tm in team_members]))
        
        # Проверяем принадлежность записи членам команды
        if entity_type == "projects":
            from ..database.models import Project
            entity = self.db.query(Project).filter(Project.id == entity_id).first()
            return entity and (entity.assigned_executor_id in team_user_ids or 
                              entity.responsible_manager_id in team_user_ids)
        
        elif entity_type == "clients":
            entity = self.db.query(Client).filter(Client.id == entity_id).first()
            return entity and entity.manager_id in team_user_ids
        
        elif entity_type == "leads":
            entity = self.db.query(Lead).filter(Lead.id == entity_id).first()
            return entity and entity.manager_id in team_user_ids
        
        elif entity_type == "deals":
            entity = self.db.query(Deal).filter(Deal.id == entity_id).first()
            return entity and (entity.manager_id in team_user_ids or 
                              entity.executor_id in team_user_ids)
        
        return False
    
    # === Управление командами ===
    
    def create_team(self, data: Dict[str, Any], created_by: AdminUser) -> Team:
        """Создать команду"""
        team = Team(
            name=data['name'],
            description=data.get('description'),
            leader_id=data.get('leader_id')
        )
        
        self.db.add(team)
        self.db.commit()
        
        # Если указан лидер, добавляем его в команду
        if team.leader_id:
            self.add_user_to_team(team.id, team.leader_id, 'leader', created_by)
        
        # Логируем действие
        self._log_action(
            action="create",
            entity_type="team",
            entity_id=team.id,
            new_data=team.to_dict(),
            user=created_by,
            description=f"Создана команда: {team.name}"
        )
        
        return team
    
    def add_user_to_team(self, team_id: int, user_id: int, team_role: str = "member", 
                        added_by: AdminUser = None) -> TeamMembership:
        """Добавить пользователя в команду"""
        # Проверяем существование
        team = self.db.query(Team).filter(Team.id == team_id).first()
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        
        if not team or not user:
            raise ValueError("Команда или пользователь не найдены")
        
        # Проверяем, не является ли уже членом
        existing = self.db.query(TeamMembership).filter(
            and_(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == user_id,
                TeamMembership.is_active == True
            )
        ).first()
        
        if existing:
            # Обновляем роль если нужно
            if existing.team_role != team_role:
                existing.team_role = team_role
                self.db.commit()
            return existing
        
        # Создаем членство
        membership = TeamMembership(
            team_id=team_id,
            user_id=user_id,
            team_role=team_role,
            can_see_team_data=True,
            can_edit_team_data=(team_role == 'leader')
        )
        
        self.db.add(membership)
        self.db.commit()
        
        # Логируем действие
        if added_by:
            self._log_action(
                action="add_to_team",
                entity_type="team",
                entity_id=team_id,
                new_data={"user_id": user_id, "team_role": team_role},
                user=added_by,
                description=f"Пользователь {user.username} добавлен в команду {team.name}"
            )
        
        return membership
    
    # === Аудит ===
    
    def _log_action(self, action: str, entity_type: str, entity_id: Optional[int],
                    user: AdminUser, description: str = None,
                    old_data: Dict = None, new_data: Dict = None) -> None:
        """Записать действие в аудит-лог"""
        try:
            audit_log = AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_data=old_data,
                new_data=new_data,
                description=description,
                user_id=user.id if user else None,
                user_name=user.username if user else None,
                user_role=user.role if user and hasattr(user, 'role') else None
            )
            
            self.db.add(audit_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Ошибка записи в аудит-лог: {str(e)}")


# === Декораторы для проверки прав ===

def require_permission(permission_name: str):
    """Декоратор для проверки разрешения"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем пользователя из kwargs
            user = kwargs.get('current_user') or kwargs.get('user')
            if not user:
                raise HTTPException(status_code=403, detail="Пользователь не авторизован")
            
            # Получаем сессию БД
            db = kwargs.get('db')
            if not db:
                raise HTTPException(status_code=500, detail="База данных недоступна")
            
            # Проверяем разрешение
            rbac = RBACService(db)
            if not rbac.check_permission(user, permission_name):
                raise HTTPException(
                    status_code=403,
                    detail=f"Недостаточно прав. Требуется разрешение: {permission_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str):
    """Декоратор для проверки роли"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем пользователя из kwargs
            user = kwargs.get('current_user') or kwargs.get('user')
            if not user:
                raise HTTPException(status_code=403, detail="Пользователь не авторизован")
            
            # Проверяем роль
            if not any(role.name == role_name for role in user.roles):
                raise HTTPException(
                    status_code=403,
                    detail=f"Недостаточно прав. Требуется роль: {role_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_data_access(entity_type: str, action: str = "view"):
    """Декоратор для проверки доступа к данным"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем пользователя и ID сущности
            user = kwargs.get('current_user') or kwargs.get('user')
            if not user:
                raise HTTPException(status_code=403, detail="Пользователь не авторизован")
            
            # Получаем ID сущности из пути или параметров
            entity_id = kwargs.get(f'{entity_type[:-1]}_id') or kwargs.get('entity_id')
            
            # Получаем сессию БД
            db = kwargs.get('db')
            if not db:
                raise HTTPException(status_code=500, detail="База данных недоступна")
            
            # Проверяем доступ
            rbac = RBACService(db)
            if not rbac.check_data_access(user, entity_type, entity_id, action):
                raise HTTPException(
                    status_code=403,
                    detail=f"Нет доступа к {entity_type} для действия {action}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator