"""
Единая навигация для всей админ панели
"""

def get_navigation_items(role_or_path=None, db=None, user_role=None) -> list:
    """Возвращает список элементов навигации с учетом роли пользователя
    
    Args:
        role_or_path: может быть или ролью пользователя (для обратной совместимости) 
                      или путем текущей страницы (новый формат)
        db: сессия базы данных (для обратной совместимости)
        user_role: роль пользователя для фильтрации меню
    """
    
    # Полный список всех элементов навигации
    all_navigation = [
        {"name": "Дашборд", "url": "/", "icon": "fas fa-chart-line", "roles": ["owner", "admin", "sales", "executor"]},
        {"name": "Клиенты", "url": "/clients", "icon": "fas fa-address-book", "roles": ["owner", "admin", "sales"]},
        {"name": "Лиды", "url": "/leads", "icon": "fas fa-user-check", "roles": ["owner", "admin", "sales"]},
        {"name": "Сделки", "url": "/deals", "icon": "fas fa-handshake", "roles": ["owner", "admin", "sales"]},
        {"name": "Авито", "url": "/admin/avito", "icon": "fas fa-comments", "roles": ["owner", "admin", "sales"]},
        {"name": "Проекты", "url": "/projects", "icon": "fas fa-project-diagram", "roles": ["owner", "admin", "sales", "executor"]},
        {"name": "База проектов", "url": "/project-database", "icon": "fas fa-database", "roles": ["owner", "admin"]},
        {"name": "Портфолио", "url": "/portfolio", "icon": "fas fa-briefcase", "roles": ["owner", "admin", "executor"]},
        {"name": "Правки", "url": "/edits", "icon": "fas fa-edit", "roles": ["owner", "admin", "executor"]},
        {"name": "Планировщик задач", "url": "/task-scheduler", "icon": "fas fa-tasks", "roles": ["owner", "admin"]},
        {"name": "Канбан доска", "url": "/tasks/kanban", "icon": "fas fa-columns", "roles": ["owner"]},
        {"name": "Мои задачи", "url": "/my-tasks", "icon": "fas fa-clipboard-list", "roles": ["owner", "admin", "sales", "executor"]},
        {"name": "Документы", "url": "/documents", "icon": "fas fa-file-alt", "roles": ["owner", "admin"]},
        {"name": "Финансы", "url": "/finance", "icon": "fas fa-chart-bar", "roles": ["owner", "admin"]},
        {"name": "Пользователи", "url": "/users", "icon": "fas fa-users", "roles": ["owner", "admin"]},
        {"name": "Исполнители", "url": "/executors", "icon": "fas fa-user-tie", "roles": ["owner", "admin"]},
        {"name": "Сервисы", "url": "/services", "icon": "fas fa-server", "roles": ["owner", "admin"]},
        {"name": "Аналитика", "url": "/analytics", "icon": "fas fa-chart-area", "roles": ["owner", "admin"]},
        {"name": "Отчеты", "url": "/reports", "icon": "fas fa-file-invoice", "roles": ["owner", "admin", "sales"]},
        {"name": "Автоматизация", "url": "/automation", "icon": "fas fa-robot", "roles": ["owner", "admin"]},
        {"name": "Уведомления", "url": "/notifications", "icon": "fas fa-bell", "roles": ["owner", "admin", "sales", "executor"]},
        {"name": "Настройки", "url": "/settings", "icon": "fas fa-cog", "roles": ["owner", "admin"]},
    ]
    
    # Определяем роль для фильтрации
    filter_role = user_role
    
    # Обратная совместимость: если передана роль как первый параметр
    if role_or_path and isinstance(role_or_path, str) and role_or_path in ["owner", "admin", "sales", "executor"]:
        filter_role = role_or_path
    
    # Фильтруем навигацию по роли
    if filter_role:
        navigation = [item for item in all_navigation if filter_role in item.get("roles", [])]
    else:
        navigation = all_navigation
    
    # Убираем информацию о ролях из результата
    for item in navigation:
        item.pop("roles", None)
    
    # Устанавливаем активный элемент если передан путь страницы
    if role_or_path and isinstance(role_or_path, str) and role_or_path.startswith('/'):
        for item in navigation:
            item["active"] = item["url"] == role_or_path
    
    return navigation