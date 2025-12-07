"""
Система ролей и прав доступа CRM
"""

from enum import Enum
from typing import Dict, List, Set

# ============================================
# РОЛИ ПОЛЬЗОВАТЕЛЕЙ
# ============================================

class UserRole(str, Enum):
    """Роли пользователей в системе"""
    OWNER = "owner"           # Владелец - полный доступ
    TEAMLEAD = "timlead"      # Тимлид - управление проектами и командой (используем 'timlead' для совместимости с БД)
    EXECUTOR = "executor"     # Исполнитель - работа только со своими задачами
    CLIENT = "client"         # Клиент - доступ через мини-апп
    ADMIN = "admin"           # Администратор - расширенный доступ

# ============================================
# РАЗДЕЛЫ СИСТЕМЫ
# ============================================

class Section(str, Enum):
    """Разделы системы CRM"""
    # Работа
    DASHBOARD = "dashboard"
    PROJECTS = "projects"
    TASKS = "tasks"
    REVISIONS = "revisions"
    CHATS = "chats"

    # Продажи
    LEADS = "leads"
    DEALS = "deals"
    CLIENTS = "clients"

    # Команда
    EXECUTORS = "executors"

    # Финансы
    FINANCE = "finance"
    SERVICES = "services"
    HOSTING = "hosting"

    # Документы
    DOCUMENTS = "documents"
    REGULATIONS = "regulations"

    # Интеллект
    TRANSCRIPTION = "transcription"
    AI_CALLS = "ai_calls"
    AUTOMATION = "automation"

    # Система
    PERMISSIONS = "permissions"
    USERS = "users"
    SETTINGS = "settings"

# ============================================
# ДЕЙСТВИЯ (CRUD + специальные)
# ============================================

class Action(str, Enum):
    """Возможные действия в системе"""
    VIEW = "view"           # Просмотр
    CREATE = "create"       # Создание
    EDIT = "edit"          # Редактирование
    DELETE = "delete"      # Удаление
    MANAGE = "manage"      # Управление (полный доступ)

    # Специальные действия
    ASSIGN = "assign"      # Назначение исполнителей
    CHANGE_STATUS = "change_status"
    VIEW_FINANCE = "view_finance"
    MANAGE_FINANCE = "manage_finance"
    SEND_MESSAGES = "send_messages"
    TRIGGER_AUTOMATION = "trigger_automation"

# ============================================
# КОНФИГУРАЦИЯ ПРАВ ДОСТУПА
# ============================================

# Полные права для владельца
OWNER_PERMISSIONS = {
    section: {action for action in Action}
    for section in Section
}

# Права для тимлида
TEAMLEAD_PERMISSIONS = {
    # Работа - полный доступ
    Section.DASHBOARD: {Action.VIEW},
    Section.PROJECTS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE, Action.ASSIGN, Action.CHANGE_STATUS},
    Section.TASKS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE, Action.ASSIGN, Action.CHANGE_STATUS},
    Section.REVISIONS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE},
    Section.CHATS: {Action.VIEW, Action.CREATE, Action.SEND_MESSAGES},

    # Продажи - полный доступ
    Section.LEADS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE},
    Section.DEALS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE},
    Section.CLIENTS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE},

    # Команда - только просмотр
    Section.EXECUTORS: {Action.VIEW},

    # Финансы - только по своим проектам
    Section.FINANCE: {Action.VIEW, Action.VIEW_FINANCE},
    Section.SERVICES: {Action.VIEW},
    Section.HOSTING: {Action.VIEW},

    # Документы - загрузка и просмотр
    Section.DOCUMENTS: {Action.VIEW, Action.CREATE, Action.EDIT},
    Section.REGULATIONS: {Action.VIEW},

    # Интеллект - использование
    Section.TRANSCRIPTION: {Action.VIEW, Action.CREATE},
    Section.AI_CALLS: {Action.VIEW, Action.CREATE},
    Section.AUTOMATION: {Action.VIEW, Action.TRIGGER_AUTOMATION},
}

# Права для исполнителя
EXECUTOR_PERMISSIONS = {
    Section.DASHBOARD: {Action.VIEW},
    Section.PROJECTS: {Action.VIEW},  # Только свои проекты
    Section.TASKS: {Action.VIEW, Action.EDIT, Action.CHANGE_STATUS},  # Только свои задачи
    Section.REVISIONS: {Action.VIEW, Action.EDIT, Action.CHANGE_STATUS},  # Только свои правки
    Section.CHATS: {Action.VIEW, Action.CREATE, Action.SEND_MESSAGES},  # Только по своим проектам
    Section.DOCUMENTS: {Action.VIEW},  # Только ТЗ по своим проектам
}

# Права для клиента (мини-апп)
CLIENT_PERMISSIONS = {
    Section.PROJECTS: {Action.VIEW},  # Только свой проект
    Section.REVISIONS: {Action.VIEW, Action.CREATE},  # Создание и просмотр правок
    Section.CHATS: {Action.VIEW, Action.CREATE, Action.SEND_MESSAGES},  # Чат по своему проекту
    Section.DOCUMENTS: {Action.VIEW},  # Договор, акт, счёт
    Section.FINANCE: {Action.VIEW},  # Блок платежей
}

# Права для администратора
ADMIN_PERMISSIONS = {
    **TEAMLEAD_PERMISSIONS,
    Section.USERS: {Action.VIEW, Action.CREATE, Action.EDIT, Action.DELETE},
    Section.SETTINGS: {Action.VIEW, Action.EDIT},
    Section.FINANCE: {Action.VIEW, Action.VIEW_FINANCE, Action.MANAGE_FINANCE},
}

# Общая карта прав
ROLE_PERMISSIONS: Dict[UserRole, Dict[Section, Set[Action]]] = {
    UserRole.OWNER: OWNER_PERMISSIONS,
    UserRole.TEAMLEAD: TEAMLEAD_PERMISSIONS,
    UserRole.EXECUTOR: EXECUTOR_PERMISSIONS,
    UserRole.CLIENT: CLIENT_PERMISSIONS,
    UserRole.ADMIN: ADMIN_PERMISSIONS,
}

# ============================================
# КОНФИГУРАЦИЯ МЕНЮ ПО РОЛЯМ
# ============================================

class MenuItem:
    """Элемент меню"""
    def __init__(self,
                 key: str,
                 title: str,
                 icon: str,
                 path: str,
                 section: Section,
                 children: List['MenuItem'] = None):
        self.key = key
        self.title = title
        self.icon = icon
        self.path = path
        self.section = section
        self.children = children or []

# Структура меню
MENU_STRUCTURE = [
    # Работа
    {
        "group": "Работа",
        "items": [
            MenuItem("dashboard", "Дашборд", "📊", "/", Section.DASHBOARD),
            MenuItem("projects", "Проекты", "📁", "/projects", Section.PROJECTS),
            MenuItem("tasks", "Задачи", "✓", "/tasks", Section.TASKS),
            MenuItem("chats", "Чаты", "💬", "/chats", Section.CHATS),
        ]
    },
    # Продажи
    {
        "group": "Продажи",
        "items": [
            MenuItem("leads", "Лиды", "🎯", "/leads", Section.LEADS),
            MenuItem("deals", "Сделки", "🤝", "/deals", Section.DEALS),
            MenuItem("clients", "Клиенты", "👥", "/clients", Section.CLIENTS),
        ]
    },
    # Команда
    {
        "group": "Команда",
        "items": [
            MenuItem("executors", "Исполнители", "👨‍💻", "/executors", Section.EXECUTORS),
        ]
    },
    # Финансы
    {
        "group": "Финансы",
        "items": [
            MenuItem("finance", "Финансы", "💰", "/finance", Section.FINANCE),
            MenuItem("services", "Сервисы", "🔌", "/services", Section.SERVICES),
            MenuItem("hosting", "Хостинг", "🖥️", "/hosting", Section.HOSTING),
        ]
    },
    # Документы
    {
        "group": "Документы",
        "items": [
            MenuItem("documents", "Документы", "📄", "/documents", Section.DOCUMENTS),
            MenuItem("regulations", "Регламенты", "📋", "/regulations", Section.REGULATIONS),
        ]
    },
    # Интеллект
    {
        "group": "Интеллект",
        "items": [
            MenuItem("transcription", "Транскрибация", "🎙️", "/transcription", Section.TRANSCRIPTION),
            MenuItem("ai_calls", "AI-звонки", "📞", "/ai-calls", Section.AI_CALLS),
            MenuItem("automation", "Автоматизация", "⚙️", "/automation", Section.AUTOMATION),
        ]
    },
    # Система
    {
        "group": "Система",
        "items": [
            MenuItem("permissions", "Права доступа", "🔐", "/permissions", Section.PERMISSIONS),
            MenuItem("users", "Пользователи", "👤", "/users", Section.USERS),
            MenuItem("settings", "Настройки", "⚙️", "/settings", Section.SETTINGS),
        ]
    },
]

# ============================================
# ФУНКЦИИ ПРОВЕРКИ ПРАВ
# ============================================

def has_permission(role: str, section: Section, action: Action) -> bool:
    """
    Проверить, есть ли у роли право на действие в разделе

    Args:
        role: Роль пользователя
        section: Раздел системы
        action: Действие

    Returns:
        True если право есть, False иначе
    """
    try:
        user_role = UserRole(role)
    except ValueError:
        return False

    permissions = ROLE_PERMISSIONS.get(user_role, {})
    section_permissions = permissions.get(section, set())

    return action in section_permissions


def get_available_sections(role: str) -> List[Section]:
    """
    Получить список доступных разделов для роли

    Args:
        role: Роль пользователя

    Returns:
        Список доступных разделов
    """
    try:
        user_role = UserRole(role)
    except ValueError:
        return []

    permissions = ROLE_PERMISSIONS.get(user_role, {})
    return list(permissions.keys())


def get_menu_for_role(role: str) -> List[dict]:
    """
    Получить структуру меню для роли

    Args:
        role: Роль пользователя

    Returns:
        Структура меню с учётом прав доступа
    """
    available_sections = set(get_available_sections(role))

    filtered_menu = []
    for group in MENU_STRUCTURE:
        filtered_items = [
            {
                "key": item.key,
                "title": item.title,
                "icon": item.icon,
                "path": item.path,
            }
            for item in group["items"]
            if item.section in available_sections
        ]

        if filtered_items:
            filtered_menu.append({
                "group": group["group"],
                "items": filtered_items
            })

    return filtered_menu


def can_access_project(role: str, user_id: int, project_executor_id: int = None, project_teamlead_id: int = None) -> bool:
    """
    Проверить, может ли пользователь получить доступ к проекту

    Args:
        role: Роль пользователя
        user_id: ID пользователя
        project_executor_id: ID исполнителя проекта
        project_teamlead_id: ID тимлида проекта

    Returns:
        True если доступ разрешён
    """
    if role in [UserRole.OWNER.value, UserRole.ADMIN.value]:
        return True

    if role == UserRole.TEAMLEAD.value:
        # Тимлид видит все проекты или только свои (если назначен)
        return True

    if role == UserRole.EXECUTOR.value:
        # Исполнитель видит только свои проекты
        return user_id == project_executor_id

    return False


def can_access_task(role: str, user_id: int, task_assigned_to_id: int = None) -> bool:
    """
    Проверить, может ли пользователь получить доступ к задаче

    Args:
        role: Роль пользователя
        user_id: ID пользователя
        task_assigned_to_id: ID исполнителя задачи

    Returns:
        True если доступ разрешён
    """
    if role in [UserRole.OWNER.value, UserRole.ADMIN.value, UserRole.TEAMLEAD.value]:
        return True

    if role == UserRole.EXECUTOR.value:
        # Исполнитель видит только свои задачи
        return user_id == task_assigned_to_id

    return False
