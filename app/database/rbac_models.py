"""
Модели для системы ролей и прав доступа (RBAC)
Role-Based Access Control для BotDev Admin
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base

# Таблица для связи многие-ко-многим между ролями и разрешениями
role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Таблица для связи многие-ко-многим между пользователями и ролями
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('admin_users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Таблица для связи многие-ко-многим между пользователями и дополнительными разрешениями
user_permissions = Table('user_permissions', Base.metadata,
    Column('user_id', Integer, ForeignKey('admin_users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class Role(Base):
    """Модель роли"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(100), nullable=False, unique=True, index=True)  # Системное имя
    display_name = Column(String(200), nullable=False)  # Отображаемое имя
    description = Column(Text, nullable=True)
    
    # Уровень доступа (для иерархии)
    level = Column(Integer, default=0)  # 0 - самый низкий, 100 - самый высокий
    
    # Настройки
    is_system = Column(Boolean, default=False)  # Системная роль (нельзя удалить)
    is_active = Column(Boolean, default=True)
    
    # Ограничения
    max_projects = Column(Integer, nullable=True)  # Макс. количество проектов
    max_clients = Column(Integer, nullable=True)  # Макс. количество клиентов
    max_deals = Column(Integer, nullable=True)  # Макс. количество сделок
    
    # Доступ к модулям
    modules_access = Column(JSON, default=dict)  # {"projects": true, "finance": false, ...}
    
    # Дашборд настройки
    dashboard_widgets = Column(JSON, default=list)  # Список доступных виджетов
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("AdminUser", secondary=user_roles, back_populates="roles")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "level": self.level,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "max_projects": self.max_projects,
            "max_clients": self.max_clients,
            "max_deals": self.max_deals,
            "modules_access": self.modules_access,
            "dashboard_widgets": self.dashboard_widgets,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "permissions": [p.name for p in self.permissions] if self.permissions else []
        }


class Permission(Base):
    """Модель разрешения"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(100), nullable=False, unique=True, index=True)  # Например: "projects.create"
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Категория
    module = Column(String(50), nullable=False, index=True)  # projects, clients, finance, etc.
    action = Column(String(50), nullable=False)  # create, read, update, delete, export, etc.
    
    # Дополнительные условия
    conditions = Column(JSON, nullable=True)  # Условия применения разрешения
    
    # Системные поля
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "module": self.module,
            "action": self.action,
            "conditions": self.conditions,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class DataAccessRule(Base):
    """Правила доступа к данным"""
    __tablename__ = "data_access_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Применение правила
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Тип правила
    entity_type = Column(String(50), nullable=False)  # projects, clients, deals, etc.
    access_type = Column(String(20), nullable=False)  # all, own, team, specific
    
    # Условия
    conditions = Column(JSON, nullable=True)  # Дополнительные условия
    specific_ids = Column(JSON, nullable=True)  # Конкретные ID для access_type=specific
    
    # Права
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    
    # Приоритет (для разрешения конфликтов)
    priority = Column(Integer, default=0)
    
    # Системные поля
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    role = relationship("Role", backref="data_access_rules")
    user = relationship("AdminUser", backref="personal_access_rules")
    
    def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "user_id": self.user_id,
            "entity_type": self.entity_type,
            "access_type": self.access_type,
            "conditions": self.conditions,
            "specific_ids": self.specific_ids,
            "can_view": self.can_view,
            "can_edit": self.can_edit,
            "can_delete": self.can_delete,
            "can_export": self.can_export,
            "priority": self.priority,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class TeamMembership(Base):
    """Членство в команде"""
    __tablename__ = "team_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Участники
    user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Роль в команде
    team_role = Column(String(50), default="member")  # leader, member, observer
    
    # Настройки
    can_see_team_data = Column(Boolean, default=True)
    can_edit_team_data = Column(Boolean, default=False)
    
    # Системные поля
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("AdminUser", backref="team_memberships")
    team = relationship("Team", back_populates="members")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "team_role": self.team_role,
            "can_see_team_data": self.can_see_team_data,
            "can_edit_team_data": self.can_edit_team_data,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "is_active": self.is_active
        }


class Team(Base):
    """Модель команды"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Руководитель
    leader_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Настройки
    is_active = Column(Boolean, default=True)
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    leader = relationship("AdminUser", foreign_keys=[leader_id], backref="led_teams")
    members = relationship("TeamMembership", back_populates="team")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "leader_id": self.leader_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "members_count": len(self.members) if self.members else 0
        }


# Расширение модели AdminUser для RBAC
def extend_admin_user():
    """Функция для расширения модели AdminUser новыми полями RBAC"""
    from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
    from .models import AdminUser
    
    # Добавляем новые атрибуты если их еще нет
    if not hasattr(AdminUser, 'roles'):
        AdminUser.roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    if not hasattr(AdminUser, 'additional_permissions'):
        AdminUser.additional_permissions = relationship("Permission", secondary=user_permissions)
    
    if not hasattr(AdminUser, 'last_login'):
        AdminUser.last_login = Column(DateTime, nullable=True)
    
    if not hasattr(AdminUser, 'login_count'):
        AdminUser.login_count = Column(Integer, default=0)
    
    if not hasattr(AdminUser, 'failed_login_count'):
        AdminUser.failed_login_count = Column(Integer, default=0)
    
    if not hasattr(AdminUser, 'last_failed_login'):
        AdminUser.last_failed_login = Column(DateTime, nullable=True)
    
    if not hasattr(AdminUser, 'is_locked'):
        AdminUser.is_locked = Column(Boolean, default=False)
    
    if not hasattr(AdminUser, 'locked_until'):
        AdminUser.locked_until = Column(DateTime, nullable=True)
    
    if not hasattr(AdminUser, 'password_changed_at'):
        AdminUser.password_changed_at = Column(DateTime, nullable=True)
    
    if not hasattr(AdminUser, 'must_change_password'):
        AdminUser.must_change_password = Column(Boolean, default=False)
    
    if not hasattr(AdminUser, 'session_token'):
        AdminUser.session_token = Column(String(500), nullable=True)
    
    if not hasattr(AdminUser, 'session_expires_at'):
        AdminUser.session_expires_at = Column(DateTime, nullable=True)
    
    if not hasattr(AdminUser, 'preferences'):
        AdminUser.preferences = Column(JSON, default=dict)
    
    # Метод для проверки разрешений
    def has_permission(self, permission_name):
        """Проверка наличия разрешения у пользователя"""
        # Проверяем прямые разрешения
        for perm in self.additional_permissions:
            if perm.name == permission_name:
                return True
        
        # Проверяем разрешения через роли
        for role in self.roles:
            for perm in role.permissions:
                if perm.name == permission_name:
                    return True
        
        return False
    
    # Метод для проверки роли
    def has_role(self, role_name):
        """Проверка наличия роли у пользователя"""
        for role in self.roles:
            if role.name == role_name:
                return True
        return False
    
    # Метод для получения уровня доступа
    def get_access_level(self):
        """Получение максимального уровня доступа пользователя"""
        if not self.roles:
            return 0
        return max([role.level for role in self.roles if role.is_active])
    
    # Добавляем методы к классу
    if not hasattr(AdminUser, 'has_permission'):
        AdminUser.has_permission = has_permission
    
    if not hasattr(AdminUser, 'has_role'):
        AdminUser.has_role = has_role
    
    if not hasattr(AdminUser, 'get_access_level'):
        AdminUser.get_access_level = get_access_level